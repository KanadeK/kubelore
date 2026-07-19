"""Offline incident-analysis use case."""

from __future__ import annotations

from pathlib import Path

from kubelore.adapters.files import load_bundle
from kubelore.domain.graph import build_resource_graph
from kubelore.domain.models import IncidentBundle, IncidentReport, TimelineEntry
from kubelore.domain.redaction import redact
from kubelore.domain.rules import evaluate_rules


def analyze_bundle(bundle: IncidentBundle) -> IncidentReport:
    graph = build_resource_graph(bundle)
    timeline = [TimelineEntry(timestamp=event.timestamp, reference=event.reference, reason=event.reason, detail=redact(event.message)) for event in sorted(bundle.events, key=lambda item: item.timestamp)]
    return IncidentReport(bundle_name=bundle.name, primary_chain=evaluate_rules(bundle), timeline=timeline, graph_nodes=graph.number_of_nodes(), graph_edges=graph.number_of_edges())


def analyze_file(path: Path) -> IncidentReport:
    return analyze_bundle(load_bundle(path))

