"""CR-A: iedzīvotājs atsauc iesniegumu (POST /submissions/{id}/withdraw)."""

import logging

import pytest

from app import storage

REASON = "Problēma jau ir atrisināta"
JSON = {"Content-Type": "application/json"}


def create(client, payload, status="RECEIVED"):
    submission_id = client.post("/submissions", json=payload).json()["id"]
    if status != "RECEIVED":
        storage.update_status(submission_id, status)
    return submission_id


def withdraw(client, submission_id, body):
    return client.post(f"/submissions/{submission_id}/withdraw", json=body)


def status_of(client, submission_id):
    return client.get(f"/submissions/{submission_id}").json()["status"]


def assert_unchanged(client, submission_id):
    assert status_of(client, submission_id) == "RECEIVED"
    audit = client.get(f"/submissions/{submission_id}/audit").json()
    assert [e["action"] for e in audit] == ["CREATE"]


# 1., 2. kritērijs
@pytest.mark.parametrize("status", ["RECEIVED", "IN_PROGRESS"])
def test_withdraw_allowed_status_returns_200(client, valid_payload, status):
    submission_id = create(client, valid_payload, status)
    before = client.get(f"/submissions/{submission_id}").json()

    response = withdraw(client, submission_id, {"reason": REASON})

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == submission_id
    assert data["status"] == "WITHDRAWN"
    assert status_of(client, submission_id) == "WITHDRAWN"
    # Precizējums: dueDate nemainās.
    assert data["dueDate"] == before["dueDate"]


# 3., 4. kritērijs un precizējums par FORWARDED
@pytest.mark.parametrize("status", ["ANSWERED", "WITHDRAWN", "FORWARDED"])
def test_withdraw_not_allowed_status_returns_409(client, valid_payload, status):
    submission_id = create(client, valid_payload, status)

    response = withdraw(client, submission_id, {"reason": REASON})

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "INVALID_STATE"
    assert status_of(client, submission_id) == status
    actions = [
        e["action"] for e in client.get(f"/submissions/{submission_id}/audit").json()
    ]
    assert "WITHDRAW" not in actions


# 4. kritērijs: atkārtota atsaukšana caur API
def test_withdraw_twice_returns_409(client, valid_payload):
    submission_id = create(client, valid_payload)
    assert withdraw(client, submission_id, {"reason": REASON}).status_code == 200

    response = withdraw(client, submission_id, {"reason": REASON})

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "INVALID_STATE"
    audit = client.get(f"/submissions/{submission_id}/audit").json()
    assert [e["action"] for e in audit].count("WITHDRAW") == 1


# 5. kritērijs
def test_withdraw_unknown_id_returns_404(client):
    response = withdraw(client, "IES-2026-999999", {"reason": REASON})
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"


# 6. kritērijs
@pytest.mark.parametrize(
    ("body", "issue"),
    [
        ({}, "REQUIRED"),
        ({"reason": None}, "INVALID_FORMAT"),
        ({"reason": ""}, "INVALID_FORMAT"),
        ({"reason": "a" * 9}, "INVALID_FORMAT"),
        ({"reason": "          "}, "INVALID_FORMAT"),
        ({"reason": "   abcdef   "}, "INVALID_FORMAT"),
        ({"reason": "a" * 501}, "TOO_LONG"),
    ],
)
def test_withdraw_invalid_reason_returns_400(client, valid_payload, body, issue):
    submission_id = create(client, valid_payload)

    response = withdraw(client, submission_id, body)

    assert response.status_code == 400
    error = response.json()["error"]
    assert error["code"] == "VALIDATION_ERROR"
    assert error["details"] == [{"field": "reason", "issue": issue}]
    assert status_of(client, submission_id) == "RECEIVED"


@pytest.mark.parametrize("length", [10, 500])
def test_withdraw_reason_length_boundaries_are_valid(client, valid_payload, length):
    submission_id = create(client, valid_payload)
    response = withdraw(client, submission_id, {"reason": "a" * length})
    assert response.status_code == 200


# 7. kritērijs
def test_withdraw_writes_audit_entry_with_reason(client, valid_payload):
    submission_id = create(client, valid_payload)
    withdraw(client, submission_id, {"reason": f"  {REASON}  "})

    audit = client.get(f"/submissions/{submission_id}/audit").json()

    assert [e["action"] for e in audit] == ["CREATE", "WITHDRAW"]
    assert audit[-1]["detail"] == REASON


# 8. kritērijs
@pytest.mark.parametrize(
    ("status", "body", "expected"),
    [
        ("RECEIVED", {"reason": REASON}, 200),
        ("ANSWERED", {"reason": REASON}, 409),
        ("RECEIVED", {"reason": "īss"}, 400),
    ],
)
def test_withdraw_logs_and_errors_have_no_personal_data(
    client, valid_payload, caplog, status, body, expected
):
    submission_id = create(client, valid_payload, status)
    caplog.clear()

    with caplog.at_level(logging.DEBUG):
        response = withdraw(client, submission_id, body)

    assert response.status_code == expected
    personal = [
        valid_payload["personalCode"],
        valid_payload["fullName"],
        valid_payload["email"],
        valid_payload["body"],
    ]
    for value in personal:
        assert value not in caplog.text
        assert value not in (response.text if expected != 200 else "")


def test_status_change_log_has_no_personal_data(client, valid_payload, caplog):
    submission_id = create(client, valid_payload)
    caplog.clear()

    with caplog.at_level(logging.DEBUG):
        storage.update_status(submission_id, "IN_PROGRESS")

    assert submission_id in caplog.text
    for field in ("personalCode", "fullName", "email", "body"):
        assert valid_payload[field] not in caplog.text


def test_unexpected_error_hides_internal_details(client, monkeypatch, caplog):
    secret = "32000000101 iekšēja informācija"

    def boom(*args, **kwargs):
        raise RuntimeError(secret)

    monkeypatch.setattr(storage, "change_status", boom)
    from fastapi.testclient import TestClient

    from app.main import app

    with caplog.at_level(logging.DEBUG):
        response = TestClient(app, raise_server_exceptions=False).post(
            "/submissions/IES-2026-000001/withdraw", json={"reason": REASON}
        )

    assert response.status_code == 500
    assert response.json() == {
        "error": {"code": "INTERNAL_ERROR", "message": "Internal server error"}
    }
    assert secret not in caplog.text


# 6. kritērijs: ķermenis nav derīgs JSON objekts. Lēmums: kļūda attiecas uz visu
# pieprasījumu (field "request"), jo lauka "reason" vispār nav.
@pytest.mark.parametrize(
    ("content", "headers", "issue"),
    [
        pytest.param(b"", JSON, "REQUIRED", id="empty"),
        pytest.param(b"null", JSON, "REQUIRED", id="null"),
        pytest.param(b'{"reason":', JSON, "INVALID_FORMAT", id="broken-json"),
        pytest.param(b'["x"]', JSON, "INVALID_FORMAT", id="array"),
        pytest.param(
            b'{"reason": "Problema jau ir atrisinata"}',
            {},
            "INVALID_FORMAT",
            id="no-ct",
        ),
    ],
)
def test_withdraw_malformed_body_returns_400(
    client, valid_payload, content, headers, issue
):
    submission_id = create(client, valid_payload)

    response = client.post(
        f"/submissions/{submission_id}/withdraw", content=content, headers=headers
    )

    assert response.status_code == 400
    error = response.json()["error"]
    assert error["code"] == "VALIDATION_ERROR"
    assert error["details"] == [{"field": "request", "issue": issue}]
    assert_unchanged(client, submission_id)


# 6. kritērijs: iemesls nav teksts
@pytest.mark.parametrize(
    "reason", [123, ["Problēma jau ir atrisināta"], {"text": REASON}, True]
)
def test_withdraw_reason_wrong_type_returns_400(client, valid_payload, reason):
    submission_id = create(client, valid_payload)

    response = withdraw(client, submission_id, {"reason": reason})

    assert response.status_code == 400
    assert response.json()["error"]["details"] == [
        {"field": "reason", "issue": "INVALID_FORMAT"}
    ]
    assert_unchanged(client, submission_id)


# 1. kritērijs un precizējums par dueDate: lieki lauki neko nemaina
def test_withdraw_ignores_extra_fields(client, valid_payload):
    submission_id = create(client, valid_payload)
    before = client.get(f"/submissions/{submission_id}").json()

    response = withdraw(
        client,
        submission_id,
        {"reason": REASON, "status": "ANSWERED", "dueDate": "2000-01-01", "id": "X"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == submission_id
    assert data["status"] == "WITHDRAWN"
    assert data["dueDate"] == before["dueDate"]


# 5. kritērijs: neparasts ID dod 404, nevis 500, un citus iesniegumus neskar
@pytest.mark.parametrize(
    "submission_id",
    [
        pytest.param("IES-2026-000001' OR '1'='1", id="sql"),
        pytest.param("IES-2026-000001%", id="like"),
        pytest.param("X" * 5000, id="long"),
        pytest.param("IES-ā-ž", id="unicode"),
    ],
)
def test_withdraw_unusual_id_returns_404(client, valid_payload, submission_id):
    existing = create(client, valid_payload)
    assert existing == "IES-2026-000001"

    response = withdraw(client, submission_id, {"reason": REASON})

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"
    assert_unchanged(client, existing)
