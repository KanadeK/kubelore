from datetime import UTC, datetime

from kubelore.domain.graph import build_resource_graph, resource_path
from kubelore.domain.models import Event, IncidentBundle, OwnerReference, Resource
from kubelore.domain.redaction import redact


def fixture_bundle() -> IncidentBundle:
    return IncidentBundle(name="graph", resources=[Resource(kind="Deployment", name="api"), Resource(kind="ReplicaSet", name="api-rs", owners=[OwnerReference(kind="Deployment", name="api")]), Resource(kind="Pod", name="api-pod", owners=[OwnerReference(kind="ReplicaSet", name="api-rs")])], events=[Event(timestamp=datetime(2026, 1, 1, tzinfo=UTC), reason="Failed", message="x", involved_kind="Pod", involved_name="api-pod")])


def test_graph_has_owner_edges_and_shortest_path() -> None:
    graph = build_resource_graph(fixture_bundle())
    assert graph.number_of_nodes() == 3
    assert graph.number_of_edges() == 2
    assert resource_path(fixture_bundle(), "pod/api-pod") == ["deployment/api", "replicaset/api-rs", "pod/api-pod"]


def test_unlinked_resource_has_self_path() -> None:
    bundle = IncidentBundle(name="orphan", resources=[Resource(kind="Pod", name="one")], events=[])
    assert resource_path(bundle, "pod/one") == ["pod/one"]
    assert resource_path(bundle, "pod/missing") == ["pod/missing"]


def test_redaction_removes_key_values_and_bearer_tokens() -> None:
    rendered = redact("password=hunter2; Authorization: abc Bearer abc.def-123")
    assert "hunter2" not in rendered
    assert "abc.def-123" not in rendered
    assert rendered.count("[REDACTED]") == 3

