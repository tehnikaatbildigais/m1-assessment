"""CR-A: atbildes atbilst līgumam (API contract) docs/openapi.yaml.

Līgums ir patiesības avots. Šie testi validē visu atbildes ķermeni pret līguma
shēmu, nevis tikai atsevišķus laukus.
"""

from pathlib import Path
from urllib.parse import quote

import pytest
import yaml
from openapi_schema_validator import OAS30Validator, oas30_format_checker
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT4

from app import storage

CONTRACT_PATH = Path(__file__).resolve().parent.parent / "docs" / "openapi.yaml"
CONTRACT = yaml.safe_load(CONTRACT_PATH.read_text(encoding="utf-8"))
CONTRACT_URI = "urn:ezermala:openapi"
WITHDRAW = "/submissions/{id}/withdraw"
AUDIT = "/submissions/{id}/audit"
REASON = "Problēma jau ir atrisināta"
REGISTRY = Registry().with_resource(
    CONTRACT_URI, Resource.from_contents(CONTRACT, default_specification=DRAFT4)
)


def _pointer(*parts: str) -> str:
    # JSON pointer URI fragmentā: "/" -> "~1", pēc tam URL kodējums ("{id}")
    return "/" + "/".join(quote(p.replace("~", "~0").replace("/", "~1")) for p in parts)


def response_schema_ref(path: str, method: str, status: int) -> str:
    """Atgriež atsauci uz atbildes shēmu līgumā, arī caur components/responses."""
    responses = CONTRACT["paths"][path][method]["responses"]
    assert str(status) in responses, (
        f"{method.upper()} {path}: statuss {status} līgumā nav dokumentēts"
    )
    ref = responses[str(status)].get("$ref")
    if ref:
        assert ref.startswith("#/components/responses/"), ref
        pointer = ref[1:]
    else:
        pointer = _pointer("paths", path, method, "responses", str(status))
    return f"{CONTRACT_URI}#{pointer}/content/application~1json/schema"


def assert_matches_contract(response, path: str, method: str = "post") -> None:
    ref = response_schema_ref(path, method, response.status_code)
    # Shēmu validē līguma dokumenta iekšienē, lai atrisinātos #/components/schemas/...
    validator = OAS30Validator(
        {"$ref": ref}, registry=REGISTRY, format_checker=oas30_format_checker
    )
    errors = sorted(validator.iter_errors(response.json()), key=str)
    assert not errors, "\n".join(
        f"{list(e.absolute_path)}: {e.message}" for e in errors
    )


def create(client, payload, status="RECEIVED"):
    submission_id = client.post("/submissions", json=payload).json()["id"]
    if status != "RECEIVED":
        storage.update_status(submission_id, status)
    return submission_id


def withdraw(client, submission_id, body):
    return client.post(f"/submissions/{submission_id}/withdraw", json=body)


# 1., 2. kritērijs
@pytest.mark.parametrize("status", ["RECEIVED", "IN_PROGRESS"])
def test_withdraw_200_matches_contract(client, valid_payload, status):
    submission_id = create(client, valid_payload, status)

    response = withdraw(client, submission_id, {"reason": REASON})

    assert response.status_code == 200
    assert_matches_contract(response, WITHDRAW)


# 6. kritērijs
@pytest.mark.parametrize("body", [{}, {"reason": "īss"}, {"reason": "a" * 501}])
def test_withdraw_400_matches_contract(client, valid_payload, body):
    submission_id = create(client, valid_payload)

    response = withdraw(client, submission_id, body)

    assert response.status_code == 400
    assert_matches_contract(response, WITHDRAW)
    # Līguma Error shēma kodu neierobežo, tāpēc to pārbauda atsevišķi.
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


# 5. kritērijs
def test_withdraw_404_matches_contract(client):
    response = withdraw(client, "IES-2026-999999", {"reason": REASON})

    assert response.status_code == 404
    assert_matches_contract(response, WITHDRAW)
    # Līguma Error shēma kodu neierobežo, tāpēc to pārbauda atsevišķi.
    assert response.json()["error"]["code"] == "NOT_FOUND"


# 3., 4. kritērijs un lēmums par FORWARDED
@pytest.mark.parametrize("status", ["ANSWERED", "FORWARDED", "WITHDRAWN"])
def test_withdraw_409_matches_contract(client, valid_payload, status):
    submission_id = create(client, valid_payload, status)

    response = withdraw(client, submission_id, {"reason": REASON})

    assert response.status_code == 409
    assert_matches_contract(response, WITHDRAW)
    # Līguma Error shēma kodu neierobežo, tāpēc to pārbauda atsevišķi.
    assert response.json()["error"]["code"] == "INVALID_STATE"


# 7. kritērijs
def test_audit_after_withdraw_matches_contract(client, valid_payload):
    submission_id = create(client, valid_payload)
    withdraw(client, submission_id, {"reason": REASON})

    response = client.get(f"/submissions/{submission_id}/audit")

    assert response.status_code == 200
    assert_matches_contract(response, AUDIT, method="get")
    assert response.json()[-1]["action"] == "WITHDRAW"


def test_contract_check_detects_mismatch():
    """Pašpārbaude: validators tiešām noraida atbildi, kas neatbilst līgumam."""

    class Fake:
        status_code = 409

        @staticmethod
        def json():
            return {"error": {"code": "INVALID_STATE"}}  # trūkst "message"

    with pytest.raises(AssertionError, match="message"):
        assert_matches_contract(Fake(), WITHDRAW)


def test_contract_check_detects_mismatch_in_inline_schema():
    """Pašpārbaude ceļam paths/.../responses/200 (bez components/responses)."""

    class Fake:
        status_code = 200

        @staticmethod
        def json():
            return [{"at": "2026-10-05T12:00:00Z", "action": "DELETE"}]

    with pytest.raises(AssertionError, match="DELETE"):
        assert_matches_contract(Fake(), AUDIT, method="get")
