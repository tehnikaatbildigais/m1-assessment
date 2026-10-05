"""OMD reģistra imitācija (izdomāts reģistrs). Palaišana: make mock (ports 8001).

Izsaukšanas kodi (trigger codes) dod vienādu uzvedību visiem dalībniekiem:

| Personas kods | Atbilde                                   |
|---------------|-------------------------------------------|
| 32000000001   | 200 ACTIVE                                |
| 32000000002   | 200 NOT_ACTIVATED                         |
| 32000000404   | 404 (reģistrā nav ieraksta)               |
| 32000000503   | 503 (apkope)                              |
| 32000000408   | 200 ACTIVE pēc 10 sekundēm                |
| 32000000999   | 200 ar nedokumentētu statusu SUSPENDED    |
| 32000000500   | 200 ar bojātu atbildes ķermeni (nav JSON) |
| citi kodi     | 200 NOT_ACTIVATED                         |
"""

import time
from typing import Annotated

from fastapi import FastAPI, Header
from fastapi.responses import JSONResponse, PlainTextResponse

app = FastAPI(title="OMD reģistra imitācija", version="1.0.0")


@app.get("/v1/mailbox/{personal_code}")
def mailbox(
    personal_code: str,
    x_api_key: Annotated[str | None, Header()] = None,
):
    if not x_api_key:
        return JSONResponse(status_code=401, content={"error": "MISSING_API_KEY"})
    if personal_code == "32000000404":
        return JSONResponse(status_code=404, content={"error": "NOT_FOUND"})
    if personal_code == "32000000503":
        return JSONResponse(status_code=503, content={"error": "MAINTENANCE"})
    if personal_code == "32000000500":
        return PlainTextResponse("<html><body>Bad Gateway</body></html>")
    if personal_code == "32000000408":
        time.sleep(10)
        status = "ACTIVE"
    elif personal_code == "32000000999":
        status = "SUSPENDED"
    elif personal_code == "32000000001":
        status = "ACTIVE"
    else:
        status = "NOT_ACTIVATED"
    return {"personalCode": personal_code, "status": status}
