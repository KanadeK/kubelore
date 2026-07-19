from datetime import UTC, datetime

import pytest

from kubelore.domain.models import ContainerStatus, Event, IncidentBundle, OwnerReference, Resource
from kubelore.domain.rules import evaluate_rules


def bundle_with(event: Event, containers: list[ContainerStatus] | None = None) -> IncidentBundle:
    return IncidentBundle(
        name="case",
        resources=[
            Resource(kind="Deployment", name="web"),
            Resource(kind="ReplicaSet", name="web-rs", owners=[OwnerReference(kind="Deployment", name="web")]),
            Resource(kind="Pod", name="web-pod", owners=[OwnerReference(kind="ReplicaSet", name="web-rs")], containers=containers or []),
        ],
        events=[event],
    )


@pytest.mark.parametrize(
    ("event", "expected"),
    [
        (Event(timestamp=datetime(2026, 1, 1, tzinfo=UTC), reason="ErrImagePull", message="pull denied", involved_kind="Pod", involved_name="web-pod"), "ImagePullFailure"),
        (Event(timestamp=datetime(2026, 1, 1, tzinfo=UTC), reason="Unhealthy", message="Readiness probe failed", involved_kind="Pod", involved_name="web-pod"), "ProbeFailure"),
        (Event(timestamp=datetime(2026, 1, 1, tzinfo=UTC), reason="CreateContainerConfigError", message="configmap app missing", involved_kind="Pod", involved_name="web-pod"), "ConfigurationMissing"),
        (Event(timestamp=datetime(2026, 1, 1, tzinfo=UTC), reason="FailedScheduling", message="0/1 nodes available", involved_kind="Pod", involved_name="web-pod"), "SchedulingFailure"),
    ],
)
def test_event_rules_produce_specific_category(event: Event, expected: str) -> None:
    report = evaluate_rules(bundle_with(event))
    assert report.category == expected
    assert report.confidence >= 0.88
    assert report.resource_path == ["deployment/web", "replicaset/web-rs", "pod/web-pod"]


def test_oom_rule_combines_container_state_and_event() -> None:
    event = Event(timestamp=datetime(2026, 1, 1, tzinfo=UTC), reason="OOMKilled", message="container exceeded memory", involved_kind="Pod", involved_name="web-pod")
    result = evaluate_rules(bundle_with(event, [ContainerStatus(name="app", terminated_reason="OOMKilled")]))
    assert result.category == "OutOfMemory"
    assert len(result.evidence) == 2
    assert result.confidence == 0.92


def test_unknown_failure_is_explicit_when_no_evidence() -> None:
    result = evaluate_rules(IncidentBundle(name="empty", resources=[], events=[]))
    assert result.category == "Unknown"
    assert result.confidence == 0.25
    assert "Collect Pod events" in result.investigation_steps[0]

