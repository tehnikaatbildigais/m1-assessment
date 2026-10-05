"""CR-1: personas koda pārbaude (tracker/CR-1.md). Viena rinda = viens tests."""

import pytest


def _submit(client, payload, personal_code):
    payload["personalCode"] = personal_code
    return client.post("/submissions", json=payload)


def _stored_code(client, response):
    submission_id = response.json()["id"]
    return client.get(f"/submissions/{submission_id}").json()["personalCode"]


def _assert_issue(response, issue):
    assert response.status_code == 400
    error = response.json()["error"]
    assert error["code"] == "VALIDATION_ERROR"
    assert {"field": "personalCode", "issue": issue} in error["details"]


def test_cr1_ac1_new_format_accepted(client, valid_payload):
    response = _submit(client, valid_payload, "32000000001")
    assert response.status_code == 201
    assert _stored_code(client, response) == "32000000001"


def test_cr1_ac2_hyphen_normalised(client, valid_payload):
    response = _submit(client, valid_payload, "320000-00001")
    assert response.status_code == 201
    assert _stored_code(client, response) == "32000000001"


def test_cr1_ac3_outer_spaces_removed(client, valid_payload):
    response = _submit(client, valid_payload, " 32000000001 ")
    assert response.status_code == 201
    assert _stored_code(client, response) == "32000000001"


@pytest.mark.parametrize(
    "code",
    [
        pytest.param("3200000000", id="ac4_10_digits"),
        pytest.param("320000000012", id="ac5_12_digits"),
        pytest.param("32000000O01", id="ac6_letter_o"),
        pytest.param("3200-0000001", id="ac9_hyphen_wrong_place"),
    ],
)
def test_cr1_invalid_format_rejected(client, valid_payload, code):
    _assert_issue(_submit(client, valid_payload, code), "INVALID_FORMAT")


def test_cr1_ac7_missing_field_required(client, valid_payload):
    del valid_payload["personalCode"]
    _assert_issue(client.post("/submissions", json=valid_payload), "REQUIRED")


def test_cr1_ac7_blank_value_required(client, valid_payload):
    _assert_issue(_submit(client, valid_payload, "   "), "REQUIRED")


def test_cr1_ac8_old_format_accepted(client, valid_payload):
    response = _submit(client, valid_payload, "311299-21233")
    assert response.status_code == 201
    assert _stored_code(client, response) == "31129921233"


def test_cr1_error_does_not_echo_input(client, valid_payload):
    response = _submit(client, valid_payload, "320000000012")
    assert "320000000012" not in response.text
