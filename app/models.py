"""Datu modeļi pēc API līguma (API contract) docs/openapi.yaml."""

import re
from datetime import date, datetime
from enum import Enum
from typing import Annotated

from pydantic import BaseModel, StringConstraints, field_validator
from pydantic_core import PydanticCustomError

# CR-1: 11 cipari vai DDMMYY-NNNNN. Tikai formāts, bez kontrolcipara.
PERSONAL_CODE = re.compile(r"[0-9]{6}-?[0-9]{5}")


class PreferredChannel(str, Enum):
    EMAIL = "EMAIL"
    POST = "POST"
    E_ADDRESS = "E_ADDRESS"


class ReplyChannel(str, Enum):
    EMAIL = "EMAIL"
    POST = "POST"
    E_ADDRESS = "E_ADDRESS"
    PENDING_CHANNEL_CHECK = "PENDING_CHANNEL_CHECK"


class ReasonCode(str, Enum):
    E_ADDRESS_NOT_ACTIVE = "E_ADDRESS_NOT_ACTIVE"
    REGISTER_UNAVAILABLE = "REGISTER_UNAVAILABLE"


class Topic(str, Enum):
    ROADS = "ROADS"
    WASTE = "WASTE"
    PLANNING = "PLANNING"
    PARKS = "PARKS"
    OTHER = "OTHER"


class TopicItem(BaseModel):
    code: Topic
    name: str


class SubmissionStatus(str, Enum):
    RECEIVED = "RECEIVED"
    IN_PROGRESS = "IN_PROGRESS"
    FORWARDED = "FORWARDED"
    ANSWERED = "ANSWERED"
    WITHDRAWN = "WITHDRAWN"


class SubmissionCreate(BaseModel):
    personalCode: str
    fullName: str
    email: str  # TODO: pārbaudīt e-pasta formātu
    preferredChannel: PreferredChannel
    topic: Topic
    subject: str
    body: str

    @field_validator("personalCode")
    @classmethod
    def normalise_personal_code(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise PydanticCustomError("missing", "Personas kods ir obligāts")
        if not PERSONAL_CODE.fullmatch(value):
            raise PydanticCustomError("invalid_format", "Nepareizs formāts")
        return value.replace("-", "")


class SubmissionCreated(BaseModel):
    id: str
    status: SubmissionStatus
    receivedAt: datetime
    dueDate: date
    replyChannel: ReplyChannel
    reasonCode: ReasonCode | None = None


class Submission(SubmissionCreated, SubmissionCreate):
    pass


class SubmissionListItem(BaseModel):
    """CR-3, 5. kritērijs: tikai šie lauki. Bez vārda un iesnieguma teksta."""

    id: str
    status: SubmissionStatus
    topic: Topic
    receivedAt: datetime
    dueDate: date
    replyChannel: ReplyChannel


class WithdrawRequest(BaseModel):
    # CR-A: atstarpes sākumā un beigās neskaita, tāpēc tukšs iemesls nav derīgs.
    reason: Annotated[
        str, StringConstraints(strip_whitespace=True, min_length=10, max_length=500)
    ]


class AuditEntry(BaseModel):
    at: datetime
    action: str
    detail: str | None = None


class Health(BaseModel):
    status: str
    version: str


class ErrorDetail(BaseModel):
    field: str
    issue: str


class ErrorBody(BaseModel):
    code: str
    message: str
    details: list[ErrorDetail] | None = None


class Error(BaseModel):
    error: ErrorBody
