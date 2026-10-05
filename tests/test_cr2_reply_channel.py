"""CR-2: atbildes kanāla pārbaude OMD reģistrā (tracker/CR-2.md)."""

import logging

import pytest
import requests

from app import config, omd_client
from app.omd_client import OmdCheck, OmdResult


def _post(client, payload, code, preferred="EMAIL"):
    payload["personalCode"] = code
    payload["preferredChannel"] = preferred
    response = client.post("/submissions", json=payload)
    assert response.status_code == 201
    return response.json()


# --- Lēmums pēc OMD atbildes (viltots OMD klients) ---


def test_cr2_ac1_active_overrides_preference(client, valid_payload):
    data = _post(client, valid_payload, "32000000001", preferred="POST")
    assert data["replyChannel"] == "E_ADDRESS"
    assert data["reasonCode"] is None


def test_cr2_ac2_not_activated_keeps_preference(client, valid_payload):
    data = _post(client, valid_payload, "32000000002", preferred="POST")
    assert data["replyChannel"] == "POST"
    assert data["reasonCode"] is None


def test_cr2_ac2_e_address_not_active_falls_back_to_email(client, valid_payload):
    data = _post(client, valid_payload, "32000000002", preferred="E_ADDRESS")
    assert data["replyChannel"] == "EMAIL"
    assert data["reasonCode"] == "E_ADDRESS_NOT_ACTIVE"


def test_cr2_ac4_unavailable_register_is_pending(client, valid_payload, fake_omd):
    fake_omd.results["32000000503"] = OmdCheck(OmdResult.UNAVAILABLE, "HTTP 503")
    data = _post(client, valid_payload, "32000000503", preferred="EMAIL")
    assert data["replyChannel"] == "PENDING_CHANNEL_CHECK"
    assert data["reasonCode"] == "REGISTER_UNAVAILABLE"


def test_cr2_ac5_log_has_id_but_no_personal_data(
    client, valid_payload, fake_omd, caplog
):
    fake_omd.results["32000000503"] = OmdCheck(OmdResult.UNAVAILABLE, "HTTP 503")
    with caplog.at_level(logging.INFO):
        data = _post(client, valid_payload, "32000000503")
    warnings = [r.getMessage() for r in caplog.records if r.levelname == "WARNING"]
    assert any(data["id"] in w and "REGISTER_UNAVAILABLE" in w for w in warnings)
    assert "32000000503" not in caplog.text
    assert valid_payload["body"] not in caplog.text


# --- OMD klients: reģistra atbilžu kartēšana (requests.get aizstāts) ---


class _Response:
    def __init__(self, status_code, body=None, invalid_json=False):
        self.status_code = status_code
        self._body = body
        self._invalid_json = invalid_json

    def json(self):
        if self._invalid_json:
            raise ValueError("not JSON")
        return self._body


@pytest.fixture
def omd_get(monkeypatch):
    calls = []

    def install(result):
        def fake_get(url, headers=None, timeout=None):
            calls.append({"url": url, "headers": headers, "timeout": timeout})
            if isinstance(result, Exception):
                raise result
            return result

        monkeypatch.setattr(omd_client.requests, "get", fake_get)
        return calls

    return install


@pytest.mark.parametrize(
    ("response", "expected"),
    [
        pytest.param(_Response(200, {"status": "ACTIVE"}), "ACTIVE", id="active"),
        pytest.param(
            _Response(200, {"status": "NOT_ACTIVATED"}),
            "NOT_ACTIVATED",
            id="not_activated",
        ),
        pytest.param(_Response(404, {}), "NOT_ACTIVATED", id="ac3_404"),
        pytest.param(_Response(503, {}), "UNAVAILABLE", id="ac4_503"),
        pytest.param(
            _Response(200, {"status": "SUSPENDED"}),
            "UNAVAILABLE",
            id="ac4_undocumented",
        ),
        pytest.param(
            _Response(200, invalid_json=True), "UNAVAILABLE", id="ac4_malformed"
        ),
        pytest.param(_Response(200, ["x"]), "UNAVAILABLE", id="ac4_not_an_object"),
        pytest.param(requests.Timeout(), "UNAVAILABLE", id="ac4_timeout"),
        pytest.param(requests.ConnectionError(), "UNAVAILABLE", id="ac4_no_connection"),
    ],
)
def test_cr2_client_maps_register_answers(omd_get, response, expected):
    omd_get(response)
    assert omd_client.mailbox_status("32000000001").result.value == expected


def test_cr2_ac4_client_uses_3_second_timeout(omd_get):
    calls = omd_get(_Response(200, {"status": "ACTIVE"}))
    omd_client.mailbox_status("32000000001")
    assert calls[0]["timeout"] == 3


def test_cr2_ac6_token_comes_from_configuration(omd_get, monkeypatch):
    monkeypatch.setattr(config, "OMD_API_TOKEN", "token-no-vides")
    calls = omd_get(_Response(200, {"status": "ACTIVE"}))
    omd_client.mailbox_status("32000000001")
    assert calls[0]["headers"]["X-Api-Key"] == "token-no-vides"
