"""CR-A, 8. kritērijs: īsta servera žurnālā (lietotne un uvicorn) nav personas datu.

Palaiž uvicorn atsevišķā procesā ar sākuma (SEED) datiem un nolasa visu tā izvadi.
POST /submissions netiek izsaukts, tāpēc nav OMD izsaukuma un tīkla.
"""

import socket
import subprocess
import sys
import time
from pathlib import Path

import httpx
import pytest

from app import storage

ROOT = Path(__file__).resolve().parent.parent
REASON = "Problēma jau ir atrisināta"
STARTUP_TIMEOUT = 10


# Visos izsaukumos trust_env=False: lokālajam serverim neizmanto proxy no vides
# (HTTP_PROXY u.c.), citādi CI vidē tests kristu ar maldinošu kļūdu.


def _free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


@pytest.fixture(scope="module")
def live_server(tmp_path_factory):
    port = _free_port()
    log_path = tmp_path_factory.mktemp("server") / "uvicorn.log"
    with log_path.open("w", encoding="utf-8") as log:
        process = subprocess.Popen(
            [
                sys.executable,
                *("-m", "uvicorn", "app.main:app"),
                *("--host", "127.0.0.1", "--port", str(port)),
            ],
            cwd=ROOT,
            stdout=log,
            stderr=subprocess.STDOUT,
        )
    base_url = f"http://127.0.0.1:{port}"
    try:
        deadline = time.monotonic() + STARTUP_TIMEOUT
        while True:
            try:
                health = httpx.get(f"{base_url}/health", timeout=1, trust_env=False)
                if health.status_code == 200:
                    break
            except httpx.TransportError:
                pass
            if process.poll() is not None or time.monotonic() > deadline:
                pytest.fail(
                    f"Serveris nestartēja:\n{log_path.read_text(encoding='utf-8')}"
                )
            time.sleep(0.1)
        yield base_url, log_path
    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()


def _seed_personal_data() -> dict[str, str]:
    values = {}
    for record in storage.SEED:
        for field in ("personalCode", "fullName", "email", "body"):
            values[f"{field}={record[field]}"] = record[field]
    return values


def test_server_log_has_no_personal_data(live_server):
    base_url, log_path = live_server
    with httpx.Client(base_url=base_url, timeout=5, trust_env=False) as http:
        url = "/submissions/{}/withdraw"
        calls = [
            (url.format("IES-2026-000001"), {"json": {"reason": REASON}}, 200),
            (url.format("IES-2026-000003"), {"json": {"reason": REASON}}, 409),
            (url.format("IES-2026-999999"), {"json": {"reason": REASON}}, 404),
            (url.format("IES-2026-000006"), {"json": {"reason": "īss"}}, 400),
            (
                url.format("IES-2026-000006"),
                {
                    "content": b'{"reason":',
                    "headers": {"Content-Type": "application/json"},
                },
                400,
            ),
        ]
        for path, kwargs, expected in calls:
            assert http.post(path, **kwargs).status_code == expected, path

    # Žurnāls tiek rakstīts asinhroni: gaida, līdz parādās piekļuves ieraksts.
    deadline = time.monotonic() + 5
    while time.monotonic() < deadline:
        output = log_path.read_text(encoding="utf-8")
        if output.count("/withdraw") >= len(calls):
            break
        time.sleep(0.1)

    # Pierāda, ka nolasīts gan lietotnes, gan uvicorn piekļuves žurnāls.
    assert "Iesniegums atsaukts: IES-2026-000001" in output
    assert "POST /submissions/IES-2026-000001/withdraw" in output
    leaked = [name for name, value in _seed_personal_data().items() if value in output]
    assert not leaked, f"Žurnālā ir personas dati: {leaked}"
