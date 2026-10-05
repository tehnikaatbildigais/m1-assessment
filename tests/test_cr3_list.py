"""CR-3: iesniegumu saraksts darbiniekam (tracker/CR-3.md)."""

import pytest

from app import storage

LIST_FIELDS = {"id", "status", "topic", "receivedAt", "dueDate", "replyChannel"}


@pytest.fixture
def seeded(client):
    storage.reset()
    return client


def test_cr3_ac1_filter_by_status(seeded):
    response = seeded.get("/submissions", params={"status": "RECEIVED"})
    assert response.status_code == 200
    items = response.json()
    assert items
    assert all(item["status"] == "RECEIVED" for item in items)


def test_cr3_ac2_filter_by_topic(seeded):
    response = seeded.get("/submissions", params={"topic": "ROADS"})
    assert response.status_code == 200
    assert all(item["topic"] == "ROADS" for item in response.json())


def test_cr3_ac3_both_filters(seeded):
    response = seeded.get(
        "/submissions", params={"status": "IN_PROGRESS", "topic": "PLANNING"}
    )
    assert response.status_code == 200
    assert [item["id"] for item in response.json()] == ["IES-2026-000002"]


def test_cr3_ac4_unknown_status_rejected(seeded):
    response = seeded.get("/submissions", params={"status": "DONE"})
    assert response.status_code == 400
    error = response.json()["error"]
    assert error["code"] == "VALIDATION_ERROR"
    assert error["details"][0]["field"] == "status"


def test_cr3_ac4_injection_rejected(seeded):
    response = seeded.get("/submissions", params={"status": "' OR '1'='1"})
    assert response.status_code == 400


def test_cr3_ac5_only_contract_fields(seeded):
    items = seeded.get("/submissions").json()
    assert len(items) == len(storage.SEED)
    assert all(set(item) == LIST_FIELDS for item in items)
