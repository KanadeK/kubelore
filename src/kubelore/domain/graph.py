"""Resource-relationship graph construction independent of input adapters."""

from __future__ import annotations

import networkx as nx

from kubelore.domain.models import IncidentBundle, Resource


def resource_key(resource: Resource) -> str:
    return f"{resource.kind}/{resource.namespace}/{resource.name}"


def build_resource_graph(bundle: IncidentBundle) -> nx.DiGraph:
    """Build owner-to-dependent edges, including synthetic container nodes."""
    graph = nx.DiGraph()
    index = {(item.kind, item.namespace, item.name): item for item in bundle.resources}
    for resource in bundle.resources:
        key = resource_key(resource)
        graph.add_node(key, kind=resource.kind, reference=resource.reference)
        for owner in resource.owners:
            owner_key = (owner.kind, resource.namespace, owner.name)
            if owner_key in index:
                graph.add_edge(resource_key(index[owner_key]), key, relation="owns")
        for container in resource.containers:
            container_key = f"Container/{resource.namespace}/{resource.name}/{container.name}"
            graph.add_node(container_key, kind="Container", reference=f"container/{container.name}")
            graph.add_edge(key, container_key, relation="contains")
    return graph


def resource_path(bundle: IncidentBundle, target_reference: str) -> list[str]:
    """Return the shortest Deployment-to-target path, or the target by itself."""
    graph = build_resource_graph(bundle)
    targets = [node for node, data in graph.nodes(data=True) if data["reference"] == target_reference]
    deployments = [node for node, data in graph.nodes(data=True) if data["kind"] == "Deployment"]
    if not targets:
        return [target_reference]
    for deployment in deployments:
        for target in targets:
            if nx.has_path(graph, deployment, target):
                return [str(graph.nodes[node]["reference"]) for node in nx.shortest_path(graph, deployment, target)]
    return [target_reference]

