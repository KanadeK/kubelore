"""Generate checked-in demo assets from the current real analysis output."""

from __future__ import annotations

import html
from pathlib import Path

from kubelore.services.analyze import analyze_file
from kubelore.services.render import render_html

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "docs" / "assets"


def main() -> int:
    report = analyze_file(ROOT / "examples" / "bundles" / "image-not-found.json")
    ASSETS.mkdir(parents=True, exist_ok=True)
    (ASSETS / "demo-report.html").write_text(render_html(report), encoding="utf-8")
    chain = report.primary_chain
    evidence = html.escape(chain.evidence[0].detail)
    svg = f"""<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"900\" height=\"330\" viewBox=\"0 0 900 330\" role=\"img\" aria-label=\"Generated KubeLore report\">
<rect width=\"900\" height=\"330\" fill=\"#f7f9fc\"/><rect x=\"25\" y=\"20\" width=\"850\" height=\"290\" rx=\"12\" fill=\"white\" stroke=\"#d7dfeb\"/>
<text x=\"60\" y=\"75\" font-family=\"system-ui, sans-serif\" font-size=\"30\" font-weight=\"700\" fill=\"#172033\">KubeLore incident narrative</text>
<text x=\"60\" y=\"118\" font-family=\"system-ui, sans-serif\" font-size=\"21\" font-weight=\"700\" fill=\"#0757b0\">{html.escape(chain.category)} · {chain.confidence:.0%} confidence</text>
<text x=\"60\" y=\"162\" font-family=\"system-ui, sans-serif\" font-size=\"16\" fill=\"#172033\">Resource chain: {' → '.join(html.escape(item) for item in chain.resource_path)}</text>
<text x=\"60\" y=\"208\" font-family=\"system-ui, sans-serif\" font-size=\"16\" fill=\"#172033\">Evidence: {evidence}</text>
<text x=\"60\" y=\"260\" font-family=\"system-ui, sans-serif\" font-size=\"16\" fill=\"#172033\">Next: {html.escape(chain.investigation_steps[0])}</text></svg>"""
    (ASSETS / "demo-output.svg").write_text(svg, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

