from datetime import UTC, datetime

from kubelore.domain.models import Event, IncidentBundle, Resource
from kubelore.services.analyze import analyze_bundle
from kubelore.services.render import render_html, render_text


def test_rendered_evidence_redacts_secret_shaped_values() -> None:
    bundle = IncidentBundle(
        name="private",
        resources=[Resource(kind="Pod", name="api")],
        events=[
            Event(
                timestamp=datetime(2026, 1, 1, tzinfo=UTC),
                reason="ErrImagePull",
                message="pull failed authorization=super-secret-token",
                involved_kind="Pod",
                involved_name="api",
            )
        ],
    )
    report = analyze_bundle(bundle)
    assert "super-secret-token" not in render_text(report)
    assert "super-secret-token" not in render_html(report)
    assert "[REDACTED]" in report.primary_chain.evidence[0].detail

