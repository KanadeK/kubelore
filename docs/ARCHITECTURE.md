# Architecture

```text
local JSON / cluster-info dump
          │
     FileBundleAdapter
          │
      IncidentBundle
          │
 ResourceGraphBuilder ──→ NetworkX resource graph
          │
      RuleEngine ──→ Evidence-backed fault chains
          │
   IncidentAnalyzer ──→ text / JSON / HTML / FastAPI
```

`domain` holds immutable Pydantic models, graph construction, rules, and redaction.
`adapters` converts local files to domain bundles. `services` orchestrates analysis
without knowing the presentation channel. `cli` and `api` are thin, read-only entry
points. No domain component imports FastAPI, filesystem APIs, or Kubernetes clients.

## Input contract

A bundle contains `resources` (Kubernetes-like objects) and `events` with an involved
object, timestamp, reason, and message. The adapter also accepts a `kubectl
cluster-info dump`-style list by extracting JSON documents from a directory. Unknown
objects are retained as evidence rather than treated as successful diagnoses.

## Safety boundary

There is no Kubernetes mutating client in the runtime path. KubeLore reads a local
file, redacts rendered evidence, and returns advice only.

