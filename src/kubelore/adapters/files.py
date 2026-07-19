"""JSON bundle reader and a compact kubectl-dump normalizer."""

from __future__ import annotations

import json
from collections.abc import Iterable
from pathlib import Path
from typing import Any

from kubelore.domain.models import ContainerStatus, Event, IncidentBundle, OwnerReference, Resource


class BundleFormatError(ValueError):
    """Raised when a local input is not an accepted KubeLore bundle."""


def _resource_from_kubernetes(item: dict[str, Any]) -> Resource:
    metadata = item.get("metadata", {})
    status = item.get("status", {})
    owners = [OwnerReference(kind=owner["kind"], name=owner["name"]) for owner in metadata.get("ownerReferences", []) if "kind" in owner and "name" in owner]
    containers = [
        ContainerStatus(
            name=container.get("name", "unknown"),
            waiting_reason=container.get("state", {}).get("waiting", {}).get("reason"),
            terminated_reason=container.get("state", {}).get("terminated", {}).get("reason"),
            restart_count=container.get("restartCount", 0),
        )
        for container in status.get("containerStatuses", [])
    ]
    conditions = {entry.get("type", "unknown"): entry.get("reason", "") for entry in status.get("conditions", [])}
    return Resource(kind=item.get("kind", "Unknown"), name=metadata.get("name", "unknown"), namespace=metadata.get("namespace", "default"), owners=owners, containers=containers, conditions=conditions)


def _event_from_kubernetes(item: dict[str, Any]) -> Event | None:
    involved = item.get("involvedObject", {})
    timestamp = item.get("eventTime") or item.get("lastTimestamp") or item.get("firstTimestamp")
    if not timestamp or not involved.get("kind") or not involved.get("name"):
        return None
    return Event(timestamp=timestamp, reason=item.get("reason", "Unknown"), message=item.get("message", ""), involved_kind=involved["kind"], involved_name=involved["name"], event_type=item.get("type", "Warning"))


def _normalize_dump(name: str, items: Iterable[dict[str, Any]]) -> IncidentBundle:
    resources: list[Resource] = []
    events: list[Event] = []
    for item in items:
        if item.get("kind") == "Event":
            event = _event_from_kubernetes(item)
            if event is not None:
                events.append(event)
        else:
            resources.append(_resource_from_kubernetes(item))
    return IncidentBundle(name=name, resources=resources, events=events)


def load_bundle(path: Path) -> IncidentBundle:
    """Load a native KubeLore bundle or a JSON `cluster-info dump` export."""
    if not path.is_file():
        raise FileNotFoundError(f"Bundle file does not exist: {path}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise BundleFormatError(f"Bundle is not valid JSON: {path}") from exc
    if not isinstance(payload, dict):
        raise BundleFormatError("Bundle root must be a JSON object.")
    if {"name", "resources", "events"}.issubset(payload):
        try:
            return IncidentBundle.model_validate(payload)
        except ValueError as exc:
            raise BundleFormatError(f"Bundle schema is invalid: {exc}") from exc
    items = payload.get("items")
    if isinstance(items, list) and all(isinstance(item, dict) for item in items):
        return _normalize_dump(path.stem, items)
    raise BundleFormatError("Expected KubeLore keys (name/resources/events) or a Kubernetes items list.")

