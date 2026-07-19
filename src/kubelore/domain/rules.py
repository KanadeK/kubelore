"""Deterministic diagnosis rules grounded in events and container state."""

from __future__ import annotations

from collections.abc import Callable

from kubelore.domain.graph import resource_path
from kubelore.domain.models import Evidence, Event, FaultChain, IncidentBundle, Resource
from kubelore.domain.redaction import redact

Rule = Callable[[IncidentBundle], FaultChain | None]


def _event_evidence(event: Event) -> Evidence:
    return Evidence(reference=event.reference, detail=redact(f"{event.reason}: {event.message}"), timestamp=event.timestamp)


def _events(bundle: IncidentBundle, predicate: Callable[[Event], bool]) -> list[Event]:
    return [event for event in bundle.events if predicate(event)]


def _chain(
    bundle: IncidentBundle,
    category: str,
    target: str,
    evidence: list[Evidence],
    steps: list[str],
    base_confidence: float,
) -> FaultChain:
    confidence = min(0.99, base_confidence + 0.02 * max(0, len(evidence) - 1))
    return FaultChain(
        category=category,
        confidence=confidence,
        summary=evidence[0].detail,
        evidence=evidence,
        investigation_steps=steps,
        resource_path=resource_path(bundle, target),
    )


def image_pull_failure(bundle: IncidentBundle) -> FaultChain | None:
    matches = _events(bundle, lambda event: event.reason in {"ErrImagePull", "ImagePullBackOff"} or "pull" in event.message.lower())
    if not matches:
        return None
    return _chain(bundle, "ImagePullFailure", matches[0].reference, [_event_evidence(event) for event in matches], ["Confirm the image reference and imagePullSecrets for the owning Deployment.", "Verify registry access from the cluster network."], 0.92)


def probe_failure(bundle: IncidentBundle) -> FaultChain | None:
    matches = _events(bundle, lambda event: event.reason == "Unhealthy" or "probe" in event.message.lower())
    if not matches:
        return None
    return _chain(bundle, "ProbeFailure", matches[0].reference, [_event_evidence(event) for event in matches], ["Compare probe path, port, and timing with the container's actual listener.", "Inspect container startup logs around the first failed probe."], 0.88)


def oom_failure(bundle: IncidentBundle) -> FaultChain | None:
    events = _events(bundle, lambda event: event.reason == "OOMKilled" or "out of memory" in event.message.lower())
    states = [
        (resource, container)
        for resource in bundle.resources
        for container in resource.containers
        if container.terminated_reason == "OOMKilled"
    ]
    if not events and not states:
        return None
    evidence = [_event_evidence(event) for event in events]
    for resource, container in states:
        evidence.append(Evidence(reference=resource.reference, detail=f"container/{container.name} terminated: OOMKilled"))
    target = events[0].reference if events else states[0][0].reference
    return _chain(bundle, "OutOfMemory", target, evidence, ["Compare container memory limit with observed workload demand.", "Inspect allocation patterns before increasing the memory limit."], 0.90)


def configuration_failure(bundle: IncidentBundle) -> FaultChain | None:
    matches = _events(bundle, lambda event: event.reason == "CreateContainerConfigError" or "configmap" in event.message.lower() or "secret" in event.message.lower())
    if not matches:
        return None
    return _chain(bundle, "ConfigurationMissing", matches[0].reference, [_event_evidence(event) for event in matches], ["Confirm the referenced ConfigMap or Secret exists in the Pod namespace.", "Compare the Deployment volume and environment references with the intended names."], 0.90)


def scheduling_failure(bundle: IncidentBundle) -> FaultChain | None:
    matches = _events(bundle, lambda event: event.reason == "FailedScheduling" or "unschedulable" in event.message.lower())
    if not matches:
        return None
    return _chain(bundle, "SchedulingFailure", matches[0].reference, [_event_evidence(event) for event in matches], ["Compare Pod requests with allocatable node capacity.", "Check node selectors, taints, affinity, and persistent-volume constraints."], 0.91)


def unknown_failure(bundle: IncidentBundle) -> FaultChain:
    evidence = [_event_evidence(event) for event in bundle.events]
    if evidence:
        target = evidence[0].reference
        summary = evidence[0].detail
    else:
        target = "bundle/unknown"
        summary = "No warning event or container failure was present in the bundle."
        evidence = [Evidence(reference=target, detail=summary)]
    return FaultChain(category="Unknown", confidence=0.25, summary=summary, evidence=evidence, investigation_steps=["Collect Pod events, container status, and rollout history before drawing a conclusion."], resource_path=resource_path(bundle, target))


RULES: list[Rule] = [image_pull_failure, probe_failure, oom_failure, configuration_failure, scheduling_failure]


def evaluate_rules(bundle: IncidentBundle) -> FaultChain:
    """Return the first matching failure by explicit severity order."""
    for rule in RULES:
        result = rule(bundle)
        if result is not None:
            return result
    return unknown_failure(bundle)

