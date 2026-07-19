"""Present reports without allowing the presentation channel to affect analysis."""

from __future__ import annotations

import html
import json

from kubelore.domain.models import IncidentReport


def render_text(report: IncidentReport) -> str:
    chain = report.primary_chain
    lines = [f"KubeLore incident: {report.bundle_name}", f"Primary chain: {chain.category} ({chain.confidence:.0%})", f"Summary: {chain.summary}", "Resource path: " + " → ".join(chain.resource_path), "Evidence:"]
    lines.extend(f"- {item.reference}: {item.detail}" for item in chain.evidence)
    lines.append("Investigation steps:")
    lines.extend(f"{number}. {step}" for number, step in enumerate(chain.investigation_steps, start=1))
    return "\n".join(lines)


def render_json(report: IncidentReport) -> str:
    return report.model_dump_json(indent=2)


def render_html(report: IncidentReport) -> str:
    chain = report.primary_chain
    evidence = "".join(f"<li><code>{html.escape(item.reference)}</code> — {html.escape(item.detail)}</li>" for item in chain.evidence)
    steps = "".join(f"<li>{html.escape(step)}</li>" for step in chain.investigation_steps)
    timeline = "".join(f"<li><time>{entry.timestamp.isoformat()}</time> {html.escape(entry.reference)}: {html.escape(entry.reason)} — {html.escape(entry.detail)}</li>" for entry in report.timeline)
    path = " <span aria-hidden=\"true\">→</span> ".join(html.escape(item) for item in chain.resource_path)
    report_json = html.escape(json.dumps(report.model_dump(mode="json"), indent=2))
    return f"""<!doctype html>
<html lang=\"en\"><head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width, initial-scale=1\"><title>KubeLore — {html.escape(report.bundle_name)}</title>
<style>body{{font-family:system-ui,sans-serif;max-width:900px;margin:2rem auto;padding:0 1rem;color:#172033;background:#f7f9fc}}main{{background:white;border:1px solid #d7dfeb;border-radius:12px;padding:2rem;box-shadow:0 2px 8px #17203312}}.badge{{background:#e4efff;color:#0757b0;border-radius:99px;padding:.2rem .6rem;font-weight:700}}code,time{{color:#49576b}}li{{margin:.55rem 0}}pre{{overflow:auto;background:#101828;color:#dbeafe;padding:1rem;border-radius:8px}}</style></head>
<body><main><p><a href=\"/\">← Bundles</a></p><h1>KubeLore incident narrative</h1><p class=\"badge\">{html.escape(chain.category)} · {chain.confidence:.0%} confidence</p><h2>{html.escape(chain.summary)}</h2><p><strong>Resource chain:</strong> {path}</p><h3>Evidence</h3><ul>{evidence}</ul><h3>Suggested investigation</h3><ol>{steps}</ol><h3>Timeline</h3><ul>{timeline}</ul><details><summary>Machine-readable report</summary><pre>{report_json}</pre></details></main></body></html>"""

