"""CR-A pieņemšanas testi: POST /submissions/{id}/withdraw.

Sagaidāmās vērtības ņemtas no tracker/CR-A.md kritērijiem (1-8), precizējumiem
un lietotāja lēmumiem (FORWARDED -> 409; issue kodi; atstarpju apgriešana;
robežvērtības 10/500; dueDate nemainās). Ne no koda.
"""

import logging

import pytest

from app import storage

REASON = "Problēma jau ir atrisināta"
UNKNOWN_ID = "IES-2026-999999"


# --- palīgfunkcijas ---------------------------------------------------------


def _create(client, payload, status=None):
    response = client.post("/submissions", json=payload)
    assert response.status_code == 201
    submission_id = response.json()["id"]
    if status is not None and status != "RECEIVED":
        assert storage.update_status(submission_id, status) is not None
    return submission_id


def _withdraw(client, submission_id, body):
    return client.post(f"/submissions/{submission_id}/withdraw", json=body)


def _get(client, submission_id):
    response = client.get(f"/submissions/{submission_id}")
    assert response.status_code == 200
    return response.json()


def _withdraw_entries(client, submission_id):
    response = client.get(f"/submissions/{submission_id}/audit")
    assert response.status_code == 200
    return [e for e in response.json() if e["action"] == "WITHDRAW"]


def _assert_error(response, status, code):
    assert response.status_code == status
    error = response.json()["error"]
    assert error["code"] == code
    assert isinstance(error["message"], str)
    return error


# --- 1. kritērijs -----------------------------------------------------------


def test_cra_ac1_received_withdrawn(client, valid_payload):
    """1. kritērijs: RECEIVED + "Problēma jau ir atrisināta" -> 200, WITHDRAWN.

    Precizējums: dueDate pēc atsaukšanas nemainās.
    """
    submission_id = _create(client, valid_payload)
    before = _get(client, submission_id)
    assert before["status"] == "RECEIVED"

    response = _withdraw(client, submission_id, {"reason": REASON})

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == submission_id
    assert data["status"] == "WITHDRAWN"
    assert data["dueDate"] == before["dueDate"]
    after = _get(client, submission_id)
    assert after["status"] == "WITHDRAWN"
    assert after["dueDate"] == before["dueDate"]


# --- 2. kritērijs -----------------------------------------------------------


def test_cra_ac2_in_progress_withdrawn(client, valid_payload):
    """2. kritērijs: IN_PROGRESS + derīgs iemesls -> 200, WITHDRAWN.

    Precizējums: dueDate pēc atsaukšanas nemainās.
    """
    submission_id = _create(client, valid_payload, "IN_PROGRESS")
    before = _get(client, submission_id)

    response = _withdraw(client, submission_id, {"reason": "Vairs nav aktuāli man"})

    assert response.status_code == 200
    assert response.json()["status"] == "WITHDRAWN"
    assert response.json()["dueDate"] == before["dueDate"]
    after = _get(client, submission_id)
    assert after["status"] == "WITHDRAWN"
    assert after["dueDate"] == before["dueDate"]


# --- 3. kritērijs (+ lēmums par FORWARDED) ---------------------------------


@pytest.mark.parametrize("status", ["ANSWERED", "FORWARDED"])
def test_cra_ac3_not_withdrawable_invalid_state(client, valid_payload, status):
    """3. kritērijs: ANSWERED -> 409 INVALID_STATE, statuss nemainās.

    Lietotāja lēmums: FORWARDED uzvedas tāpat (409, statuss nemainās).
    Negatīvs gadījums: WITHDRAW audita ieraksts netiek pievienots.
    """
    submission_id = _create(client, valid_payload, status)
    before = _get(client, submission_id)

    response = _withdraw(client, submission_id, {"reason": REASON})

    _assert_error(response, 409, "INVALID_STATE")
    after = _get(client, submission_id)
    assert after["status"] == status
    assert after["dueDate"] == before["dueDate"]
    assert _withdraw_entries(client, submission_id) == []


# --- 4. kritērijs -----------------------------------------------------------


def test_cra_ac4_repeat_withdraw_invalid_state(client, valid_payload):
    """4. kritērijs: atkārtota atsaukšana -> 409 INVALID_STATE.

    Statuss paliek WITHDRAWN, otrs WITHDRAW audita ieraksts netiek pievienots.
    """
    submission_id = _create(client, valid_payload)
    assert _withdraw(client, submission_id, {"reason": REASON}).status_code == 200

    response = _withdraw(client, submission_id, {"reason": "Otrs mēģinājums atsaukt"})

    _assert_error(response, 409, "INVALID_STATE")
    assert _get(client, submission_id)["status"] == "WITHDRAWN"
    entries = _withdraw_entries(client, submission_id)
    assert len(entries) == 1
    assert entries[0]["detail"] == REASON


# --- 5. kritērijs -----------------------------------------------------------


def test_cra_ac5_unknown_id_not_found(client, valid_payload):
    """5. kritērijs: nezināms ID -> 404 NOT_FOUND.

    Esošie iesniegumi netiek skarti.
    """
    existing = _create(client, valid_payload)

    response = _withdraw(client, UNKNOWN_ID, {"reason": REASON})

    _assert_error(response, 404, "NOT_FOUND")
    assert _get(client, existing)["status"] == "RECEIVED"
    assert _withdraw_entries(client, existing) == []


# --- 6. kritērijs (+ lēmumi par issue kodiem, apgriešanu, robežām) ---------


@pytest.mark.parametrize(
    ("body", "expected_issue"),
    [
        pytest.param({}, "REQUIRED", id="missing"),
        pytest.param({"reason": "a" * 9}, "INVALID_FORMAT", id="len9"),
        pytest.param({"reason": "ā" * 9}, "INVALID_FORMAT", id="len9-non-ascii"),
        pytest.param({"reason": "a" * 501}, "TOO_LONG", id="len501"),
        pytest.param({"reason": ""}, "INVALID_FORMAT", id="empty"),
        pytest.param({"reason": " " * 20}, "INVALID_FORMAT", id="only-spaces"),
        pytest.param(
            {"reason": "   " + "a" * 9 + "   "}, "INVALID_FORMAT", id="len9-padded"
        ),
        pytest.param(
            {"reason": "  " + "a" * 501 + "  "}, "TOO_LONG", id="len501-padded"
        ),
        pytest.param({"reason": "ok"}, "INVALID_FORMAT", id="short"),
        # Derīgas robežvērtības (lēmums: 10 un 500 ir derīgas, arī ar atstarpēm).
        pytest.param({"reason": "a" * 10}, None, id="len10-valid"),
        pytest.param({"reason": "ā" * 10}, None, id="len10-non-ascii-valid"),
        pytest.param({"reason": "a" * 500}, None, id="len500-valid"),
        pytest.param({"reason": "  " + "a" * 500 + "  "}, None, id="len500-padded"),
    ],
)
def test_cra_ac6_reason_validation(client, valid_payload, body, expected_issue):
    """6. kritērijs: nav iemesla / <10 / >500 -> 400 VALIDATION_ERROR, lauks reason,
    statuss nemainās.

    Lietotāja lēmumi: īss -> INVALID_FORMAT, garš -> TOO_LONG, trūkst -> REQUIRED;
    atstarpes apgriež pirms garuma pārbaudes; 10 un 500 derīgi, 9 un 501 nē.
    """
    submission_id = _create(client, valid_payload)

    response = _withdraw(client, submission_id, body)

    if expected_issue is None:
        assert response.status_code == 200
        assert _get(client, submission_id)["status"] == "WITHDRAWN"
        return

    error = _assert_error(response, 400, "VALIDATION_ERROR")
    assert error["details"] == [{"field": "reason", "issue": expected_issue}]
    assert _get(client, submission_id)["status"] == "RECEIVED"
    assert _withdraw_entries(client, submission_id) == []


# --- 7. kritērijs -----------------------------------------------------------


def test_cra_ac7_audit_withdraw_with_reason(client, valid_payload):
    """7. kritērijs: pēc atsaukšanas auditā ir WITHDRAW, detail ir iemesls.

    Lietotāja lēmums: detail ir apgrieztais iemesls (bez atstarpēm malās).
    """
    submission_id = _create(client, valid_payload)

    response = _withdraw(client, submission_id, {"reason": "   " + REASON + "  "})
    assert response.status_code == 200

    audit = client.get(f"/submissions/{submission_id}/audit")
    assert audit.status_code == 200
    entries = [e for e in audit.json() if e["action"] == "WITHDRAW"]
    assert len(entries) == 1
    assert entries[0]["detail"] == REASON
    assert entries[0]["at"]


# --- 8. kritērijs -----------------------------------------------------------


def _pii(payload):
    return {
        "personalCode": payload["personalCode"],
        "fullName": payload["fullName"],
        "email": payload["email"],
        "body": payload["body"],
    }


@pytest.mark.parametrize("case", ["200", "400", "404", "409"])
def test_cra_ac8_no_personal_data_in_logs_or_errors(
    client, valid_payload, caplog, case
):
    """8. kritērijs: žurnālā un kļūdu atbildēs nav personas koda, vārda,
    e-pasta un iesnieguma teksta (200, 400, 404, 409 gadījumi).
    """
    submission_id = _create(client, valid_payload)
    if case == "409":
        storage.update_status(submission_id, "ANSWERED")
    target = UNKNOWN_ID if case == "404" else submission_id
    if case == "400":
        # Pārāk garš iemesls, kurā ir personas dati: tie nedrīkst atgriezties atbildē.
        reason = (valid_payload["fullName"] + " " + valid_payload["email"] + " ") * 20
        assert len(reason.strip()) > 500
    else:
        reason = REASON

    caplog.clear()
    caplog.set_level(logging.DEBUG)
    response = _withdraw(client, target, {"reason": reason})

    assert response.status_code == int(case)
    log_text = "\n".join([r.getMessage() for r in caplog.records] + [caplog.text])
    texts = {"log": log_text}
    if case != "200":
        texts["error response"] = response.text
    for where, text in texts.items():
        for name, value in _pii(valid_payload).items():
            assert value not in text, f"{name} atrasts: {where}"
