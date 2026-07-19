"""Small, accessible FastAPI presentation layer for local sample reports."""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse

from kubelore.services.analyze import analyze_file
from kubelore.services.render import render_html

app = FastAPI(title="KubeLore", version="0.1.0", docs_url=None, redoc_url=None)
_BUNDLE_DIR = Path(__file__).resolve().parents[2] / "examples" / "bundles"


def sample_bundles() -> list[str]:
    return sorted(path.name for path in _BUNDLE_DIR.glob("*.json"))


@app.get("/", response_class=HTMLResponse)
def index() -> str:
    links = "".join(f'<li><a href="/report/{name}">{name.removesuffix(".json")}</a></li>' for name in sample_bundles())
    return f"""<!doctype html><html lang=\"en\"><head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width, initial-scale=1\"><title>KubeLore</title><style>body{{font-family:system-ui,sans-serif;max-width:760px;margin:2rem auto;padding:0 1rem}}a{{color:#0757b0}}li{{margin:.8rem 0}}</style></head><body><main><h1>KubeLore</h1><p>Choose a synthetic offline incident bundle. Analysis is deterministic and read-only.</p><nav aria-label=\"Sample incident bundles\"><ul>{links}</ul></nav></main></body></html>"""


@app.get("/report/{bundle_name}", response_class=HTMLResponse)
def report(bundle_name: str) -> str:
    if bundle_name not in sample_bundles():
        raise HTTPException(status_code=404, detail="Unknown bundled incident")
    return render_html(analyze_file(_BUNDLE_DIR / bundle_name))

