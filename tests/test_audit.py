"""Audita ieraksti (GET /submissions/{id}/audit)."""

from datetime import datetime, timezone

from app import clock


def test_create_writes_audit_entry(client, valid_payload, monkeypatch):
    # Laiku aizstāj, lai testā būtu zināma vērtība.
    fixed = datetime(2026, 10, 5, 12, 0, tzinfo=timezone.utc)
    monkeypatch.setattr(clock, "now", lambda: fixed)

    created = client.post("/submissions", json=valid_payload).json()
    response = client.get(f"/submissions/{created['id']}/audit")

    assert response.status_code == 200
    assert response.json() == [
        {"at": "2026-10-05T12:00:00Z", "action": "CREATE", "detail": None}
    ]
    assert created["receivedAt"] == "2026-10-05T12:00:00Z"


def test_audit_unknown_submission_returns_404(client):
    response = client.get("/submissions/IES-2026-999999/audit")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"
