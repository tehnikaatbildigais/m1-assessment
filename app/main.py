"""Ezermalas pieteikumu sistēma · iesniegumu API (mācību prototips)."""

import logging
from collections.abc import Callable
from datetime import timedelta
from pathlib import Path
from typing import Annotated

from fastapi import Depends, FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from app import clock, omd_client, storage
from app.errors import InvalidState, SubmissionNotFound, register_error_handlers
from app.models import (
    AuditEntry,
    Error,
    Health,
    PreferredChannel,
    ReasonCode,
    ReplyChannel,
    Submission,
    SubmissionCreate,
    SubmissionCreated,
    SubmissionListItem,
    SubmissionStatus,
    Topic,
    TopicItem,
    WithdrawRequest,
)

VERSION = "0.1.0"
TOPIC_NAMES = {
    Topic.ROADS: "Ceļi un ielas",
    Topic.WASTE: "Atkritumi",
    Topic.PLANNING: "Teritorijas plānošana",
    Topic.PARKS: "Parki un skvēri",
    Topic.OTHER: "Cits",
}
# CR-A: atsaukt drīkst tikai no šiem statusiem. FORWARDED nē (lēmums CR-A PR).
WITHDRAWABLE = (SubmissionStatus.RECEIVED.value, SubmissionStatus.IN_PROGRESS.value)
REPLY_DAYS = 30  # Vienkāršots termiņš: 30 kalendāra dienas
UI_DIR = Path(__file__).resolve().parent.parent / "ui"

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("ezermala.submissions")

app = FastAPI(title="Ezermalas pieteikumu sistēma · iesniegumu API", version=VERSION)
register_error_handlers(app)
storage.reset()


OmdLookup = Callable[[str], omd_client.OmdCheck]


def get_omd() -> OmdLookup:
    return omd_client.mailbox_status


def decide_reply_channel(
    preferred: PreferredChannel, check: omd_client.OmdCheck
) -> tuple[ReplyChannel, ReasonCode | None]:
    """CR-2: atbildes kanāls pēc OMD atbildes. Ja reģistrs neatbild skaidri, nemin."""
    if check.result is omd_client.OmdResult.ACTIVE:
        return ReplyChannel.E_ADDRESS, None
    if check.result is omd_client.OmdResult.NOT_ACTIVATED:
        if preferred is PreferredChannel.E_ADDRESS:
            return ReplyChannel.EMAIL, ReasonCode.E_ADDRESS_NOT_ACTIVE
        return ReplyChannel(preferred.value), None
    return ReplyChannel.PENDING_CHANNEL_CHECK, ReasonCode.REGISTER_UNAVAILABLE


@app.get("/", include_in_schema=False)
def root() -> RedirectResponse:
    return RedirectResponse("/ui/")


@app.get("/health", response_model=Health, tags=["Sistēma"])
def get_health() -> Health:
    return Health(status="ok", version=VERSION)


@app.get("/topics", response_model=list[TopicItem], tags=["Klasifikatori"])
def list_topics() -> list[TopicItem]:
    return [TopicItem(code=code, name=name) for code, name in TOPIC_NAMES.items()]


@app.post(
    "/submissions",
    status_code=201,
    response_model=SubmissionCreated,
    responses={400: {"model": Error}},
    tags=["Iesniegumi"],
)
def create_submission(
    data: SubmissionCreate,
    omd: Annotated[OmdLookup, Depends(get_omd)],
) -> SubmissionCreated:
    received_at = clock.now()
    check = omd(data.personalCode)
    reply_channel, reason = decide_reply_channel(data.preferredChannel, check)

    record = storage.add(
        {
            **data.model_dump(mode="json"),
            "status": SubmissionStatus.RECEIVED.value,
            "receivedAt": received_at.isoformat(),
            "dueDate": (received_at.date() + timedelta(days=REPLY_DAYS)).isoformat(),
            "replyChannel": reply_channel.value,
            "reasonCode": reason.value if reason else None,
        }
    )
    storage.add_audit(record["id"], "CREATE")
    # Žurnālā tikai iesnieguma ID un iemesls. Nekad personas kods vai teksts.
    logger.info("Iesniegums saņemts: %s", record["id"])
    if check.result is omd_client.OmdResult.UNAVAILABLE:
        logger.warning(
            "OMD pārbaude neizdevās: iesniegums %s, iemesls %s (%s)",
            record["id"],
            ReasonCode.REGISTER_UNAVAILABLE.value,
            check.detail,
        )
    return SubmissionCreated(**record)


@app.get(
    "/submissions",
    response_model=list[SubmissionListItem],
    tags=["Iesniegumi"],
)
def list_submissions(
    status: SubmissionStatus | None = None, topic: Topic | None = None
) -> list[SubmissionListItem]:
    records = storage.list_submissions(
        status=status.value if status else None,
        topic=topic.value if topic else None,
    )
    return [SubmissionListItem(**record) for record in records]


@app.get(
    "/submissions/{submission_id}",
    response_model=Submission,
    responses={404: {"model": Error}},
    tags=["Iesniegumi"],
)
def get_submission(submission_id: str) -> Submission:
    record = storage.get(submission_id)
    if record is None:
        raise SubmissionNotFound()
    return Submission(**record)


@app.get(
    "/submissions/{submission_id}/audit",
    response_model=list[AuditEntry],
    responses={404: {"model": Error}},
    tags=["Iesniegumi"],
)
def get_submission_audit(submission_id: str) -> list[AuditEntry]:
    if storage.get(submission_id) is None:
        raise SubmissionNotFound()
    return [AuditEntry(**entry) for entry in storage.list_audit(submission_id)]


@app.post(
    "/submissions/{submission_id}/withdraw",
    response_model=Submission,
    responses={400: {"model": Error}, 404: {"model": Error}, 409: {"model": Error}},
    tags=["Darbības ar iesniegumu"],
)
def withdraw_submission(submission_id: str, data: WithdrawRequest) -> Submission:
    record = storage.change_status(
        submission_id,
        allowed=WITHDRAWABLE,
        status=SubmissionStatus.WITHDRAWN.value,
        action="WITHDRAW",
        detail=data.reason,
    )
    if record is None:
        if storage.get(submission_id) is None:
            raise SubmissionNotFound()
        raise InvalidState()
    # Žurnālā tikai ID. Iemeslu nežurnalējam: tas ir brīvs teksts.
    logger.info("Iesniegums atsaukts: %s", submission_id)
    return Submission(**record)


app.mount("/ui", StaticFiles(directory=UI_DIR, html=True), name="ui")
