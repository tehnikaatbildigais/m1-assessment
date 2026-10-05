"""OMD reģistra klients. OMD (Official Mailbox Directory) ir izdomāts reģistrs.

Uzvedība pēc API līguma (API contract) docs/openapi.yaml un pieteikuma CR-2.
"""

from dataclasses import dataclass
from enum import Enum

import requests

from app import config

TIMEOUT_SECONDS = 3


class OmdResult(str, Enum):
    ACTIVE = "ACTIVE"
    NOT_ACTIVATED = "NOT_ACTIVATED"
    UNAVAILABLE = "UNAVAILABLE"


@dataclass(frozen=True)
class OmdCheck:
    result: OmdResult
    detail: str = ""


def mailbox_status(personal_code: str) -> OmdCheck:
    """Pārbauda e-adresi OMD reģistrā. Nekad nemin: neskaidra atbilde = UNAVAILABLE."""
    try:
        response = requests.get(
            f"{config.OMD_BASE_URL}/v1/mailbox/{personal_code}",
            headers={"X-Api-Key": config.OMD_API_TOKEN},
            timeout=TIMEOUT_SECONDS,
        )
    except requests.Timeout:
        return OmdCheck(OmdResult.UNAVAILABLE, "noildze")
    except requests.RequestException:
        return OmdCheck(OmdResult.UNAVAILABLE, "nav savienojuma")

    if response.status_code == 404:
        return OmdCheck(OmdResult.NOT_ACTIVATED, "reģistrā nav ieraksta")
    if response.status_code != 200:
        return OmdCheck(OmdResult.UNAVAILABLE, f"HTTP {response.status_code}")

    try:
        status = response.json().get("status")
    except (ValueError, AttributeError):
        return OmdCheck(OmdResult.UNAVAILABLE, "bojāta atbilde")

    if status == "ACTIVE":
        return OmdCheck(OmdResult.ACTIVE)
    if status == "NOT_ACTIVATED":
        return OmdCheck(OmdResult.NOT_ACTIVATED)
    return OmdCheck(OmdResult.UNAVAILABLE, "nedokumentēts statuss")
