"""Typed, serializable objects for KubeLore's offline analysis domain."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class OwnerReference(BaseModel):
    kind: str
    name: str


class ContainerStatus(BaseModel):
    name: str
    waiting_reason: str | None = None
    terminated_reason: str | None = None
    restart_count: int = 0


class Resource(BaseModel):
    kind: str
    name: str
    namespace: str = "default"
    owners: list[OwnerReference] = Field(default_factory=list)
    containers: list[ContainerStatus] = Field(default_factory=list)
    conditions: dict[str, str] = Field(default_factory=dict)

    @property
    def reference(self) -> str:
        return f"{self.kind.lower()}/{self.name}"


class Event(BaseModel):
    timestamp: datetime
    reason: str
    message: str
    involved_kind: str
    involved_name: str
    event_type: str = "Warning"

    @property
    def reference(self) -> str:
        return f"{self.involved_kind.lower()}/{self.involved_name}"


class IncidentBundle(BaseModel):
    name: str
    resources: list[Resource]
    events: list[Event]


class Evidence(BaseModel):
    reference: str
    detail: str
    timestamp: datetime | None = None


class TimelineEntry(BaseModel):
    timestamp: datetime
    reference: str
    reason: str
    detail: str


class FaultChain(BaseModel):
    category: str
    confidence: float
    summary: str
    evidence: list[Evidence]
    investigation_steps: list[str]
    resource_path: list[str]


class IncidentReport(BaseModel):
    bundle_name: str
    primary_chain: FaultChain
    timeline: list[TimelineEntry]
    graph_nodes: int
    graph_edges: int

