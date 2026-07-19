# Competitor scan

Scan date: 2026-07-19. Search was performed with authenticated `gh search repos` for
the exact name, exact slug, `kubernetes rca`, `kubernetes troubleshooting`,
`kubernetes events analyzer`, and `kubernetes diagnostics`.

The exact-name and exact-slug searches returned no repositories. The following public
repositories were inspected through their GitHub metadata. Stars and update timestamps
are the values returned by GitHub on the scan date.

| Repository | Stars | Updated | Main focus | Overlap |
|---|---:|---|---|---|
| [agenticdevops/kube-rca](https://github.com/agenticdevops/kube-rca) | 0 | 2025-11-19 | Kubernetes RCA experiments | Adjacent RCA research |
| [CharjanVinay/k8s-incident-summarizer](https://github.com/CharjanVinay/k8s-incident-summarizer) | 0 | 2026-04-27 | Claude-powered incident RCA | Incident explanation |
| [akuvshinova-ds/graph-traversal-agent-artifact](https://github.com/akuvshinova-ds/graph-traversal-agent-artifact) | 0 | 2026-06-07 | Auditable graph-guided RCA artifact | Graph-guided diagnosis |
| [blackdog0403/k8s-agents-strands](https://github.com/blackdog0403/k8s-agents-strands) | 0 | 2026-05-21 | Agentic EKS RCA | Kubernetes RCA |
| [ripun/rcaops](https://github.com/ripun/rcaops) | 0 | 2026-07-07 | LLM correlation of metrics, logs, traces, events | Incident analysis |
| [cloudexp-io/kubernetes-rca](https://github.com/cloudexp-io/kubernetes-rca) | 0 | 2026-01-27 | Kubernetes RCA project | Domain adjacency |
| [Gayu2710/kubernetes-rca-assistant](https://github.com/Gayu2710/kubernetes-rca-assistant) | 0 | 2026-04-01 | Kubernetes RCA assistant | Domain adjacency |
| [vobbilis/kubernetes-rca-system](https://github.com/vobbilis/kubernetes-rca-system) | 0 | 2025-04-20 | Multi-agent Kubernetes RCA | Domain adjacency |
| [k8sgpt-ai/k8sgpt](https://github.com/k8sgpt-ai/k8sgpt) | 7,992 | 2026-07-19 | AI-assisted Kubernetes tooling | Kubernetes analysis UX |
| [robusta-dev/robusta](https://github.com/robusta-dev/robusta) | 3,055 | 2026-07-17 | Alert enrichment and automatic remediation | Alerting and remediation |

## Decision

No exact `KubeLore` name or `kubelore` slug was found. Adjacent active projects often
depend on LLMs, live telemetry, agents, or remediation. KubeLore therefore narrows its
MVP to a deterministic, credential-free local bundle reader that produces an inspectable
Deployment-to-container evidence chain and never acts on the cluster. This avoids copying
the broader platforms while preserving the core value of faster incident understanding.

