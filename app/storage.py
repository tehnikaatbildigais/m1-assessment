"""Iesniegumu glabātuve: SQLite datubāze atmiņā.

Pēc restarta dati atgriežas sākuma stāvoklī ar trim sintētiskiem iesniegumiem.
"""

import logging
import sqlite3
import threading

from app import clock

logger = logging.getLogger("ezermala.storage")

COLUMNS = (
    "id",
    "personalCode",
    "fullName",
    "email",
    "preferredChannel",
    "topic",
    "subject",
    "body",
    "status",
    "receivedAt",
    "dueDate",
    "replyChannel",
    "reasonCode",
)

# Sintētiski dati. Personas kodi neatbilst reālām personām.
SEED = (
    {
        "personalCode": "32000000101",
        "fullName": "Jānis Bērziņš",
        "email": "janis.berzins@example.com",
        "preferredChannel": "EMAIL",
        "topic": "ROADS",
        "subject": "Bedre Ezera ielā",
        "body": "Ezera ielā pie 12. mājas ir dziļa bedre. Lūdzu, salabojiet to.",
        "status": "RECEIVED",
        "receivedAt": "2026-10-01T09:15:00+00:00",
        "dueDate": "2026-11-02",
        "replyChannel": "EMAIL",
        "reasonCode": None,
    },
    {
        "personalCode": "32000000102",
        "fullName": "Līga Ozoliņa-Kalniņa",
        "email": "liga.ozolina@example.com",
        "preferredChannel": "POST",
        "topic": "PLANNING",
        "subject": "Bojāta uzbrauktuve pie bibliotēkas",
        "body": (
            "Es pārvietojos ratiņkrēslā, un uzbrauktuve pie bibliotēkas ir bojāta. "
            "Lūdzu, salabojiet to."
        ),
        "status": "IN_PROGRESS",
        "receivedAt": "2026-08-20T10:00:00+00:00",
        "dueDate": "2026-09-21",
        "replyChannel": "POST",
        "reasonCode": None,
    },
    {
        "personalCode": "32000000103",
        "fullName": "Ņikita Šķēle",
        "email": "nikita.skele@example.com",
        "preferredChannel": "E_ADDRESS",
        "topic": "WASTE",
        "subject": "Atkritumu konteiners netiek iztukšots",
        "body": "Konteiners Liepu ielā 3 nav iztukšots divas nedēļas.",
        "status": "ANSWERED",
        "receivedAt": "2026-09-01T08:30:00+00:00",
        "dueDate": "2026-10-01",
        "replyChannel": "E_ADDRESS",
        "reasonCode": None,
    },
    {
        "personalCode": "32000000104",
        "fullName": "Andris Kļaviņš",
        "email": "andris.klavins@example.com",
        "preferredChannel": "EMAIL",
        "topic": "ROADS",
        "subject": "Valsts autoceļa apgaismojums",
        "body": "Uz autoceļa pie Ezermalas pagrieziena nedeg laternas.",
        "status": "FORWARDED",
        "receivedAt": "2026-09-14T11:05:00+00:00",
        "dueDate": "2026-10-14",
        "replyChannel": "EMAIL",
        "reasonCode": None,
    },
    {
        "personalCode": "32000000105",
        "fullName": "Elza Pētersone",
        "email": "elza.petersone@example.com",
        "preferredChannel": "POST",
        "topic": "OTHER",
        "subject": "Bibliotēkas darba laiks",
        "body": "Lūdzu, pagariniet bibliotēkas darba laiku sestdienās.",
        "status": "WITHDRAWN",
        "receivedAt": "2026-09-10T14:20:00+00:00",
        "dueDate": "2026-10-12",
        "replyChannel": "POST",
        "reasonCode": None,
    },
    {
        "personalCode": "32000000106",
        "fullName": "Mārtiņš Grīnbergs",
        "email": "martins.grinbergs@example.com",
        "preferredChannel": "EMAIL",
        "topic": "PARKS",
        "subject": "Soliņi parkā",
        "body": "Ezermalas parkā ir salauzti trīs soliņi.",
        "status": "RECEIVED",
        "receivedAt": "2026-09-25T13:40:00+00:00",
        "dueDate": "2026-10-26",
        "replyChannel": "EMAIL",
        "reasonCode": None,
    },
    {
        "personalCode": "32000000107",
        "fullName": "Dace Ūdre",
        "email": "dace.udre@example.com",
        "preferredChannel": "EMAIL",
        "topic": "WASTE",
        "subject": "Šķirošanas konteineri",
        "body": "Daudzdzīvokļu mājai Skolas ielā 5 vajag stikla konteineru.",
        "status": "IN_PROGRESS",
        "receivedAt": "2026-05-31T07:20:00+00:00",
        "dueDate": "2026-06-30",
        "replyChannel": "EMAIL",
        "reasonCode": None,
    },
)

# Izdomātas iestādes, kurām var pārsūtīt iesniegumu.
INSTITUTIONS = (
    ("EZM-BUV", "Ezermalas novada būvvalde"),
    ("EZM-SOC", "Ezermalas novada sociālais dienests"),
    ("VCD", "Valsts ceļu dienests (izdomāts)"),
)

_INSERT = """
    INSERT INTO submissions (
        id, personalCode, fullName, email, preferredChannel, topic, subject, body,
        status, receivedAt, dueDate, replyChannel, reasonCode
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
"""

_lock = threading.Lock()
_conn: sqlite3.Connection | None = None


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute(
        """
        CREATE TABLE submissions (
            seq INTEGER PRIMARY KEY AUTOINCREMENT,
            id TEXT UNIQUE NOT NULL,
            personalCode TEXT NOT NULL,
            fullName TEXT NOT NULL,
            email TEXT NOT NULL,
            preferredChannel TEXT NOT NULL,
            topic TEXT NOT NULL,
            subject TEXT NOT NULL,
            body TEXT NOT NULL,
            status TEXT NOT NULL,
            receivedAt TEXT NOT NULL,
            dueDate TEXT NOT NULL,
            replyChannel TEXT NOT NULL,
            reasonCode TEXT
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE audit (
            seq INTEGER PRIMARY KEY AUTOINCREMENT,
            submissionId TEXT NOT NULL,
            at TEXT NOT NULL,
            action TEXT NOT NULL,
            detail TEXT
        )
        """
    )
    conn.execute("CREATE TABLE institutions (code TEXT PRIMARY KEY, name TEXT)")
    conn.executemany("INSERT INTO institutions VALUES (?, ?)", INSTITUTIONS)
    return conn


def reset(seed: bool = True) -> None:
    global _conn
    with _lock:
        _conn = _connect()
    if seed:
        for record in SEED:
            add(record)


def add(data: dict) -> dict:
    with _lock:
        (seq,) = _conn.execute(
            "SELECT COALESCE(MAX(seq), 0) + 1 FROM submissions"
        ).fetchone()
        record = {**data, "id": f"IES-2026-{seq:06d}"}
        _conn.execute(_INSERT, [record.get(column) for column in COLUMNS])
    return record


def list_submissions(status: str | None = None, topic: str | None = None) -> list:
    # Parametrizēts vaicājums: ievade nekad nekļūst par SQL daļu.
    with _lock:
        rows = _conn.execute(
            """
            SELECT * FROM submissions
            WHERE (:status IS NULL OR status = :status)
              AND (:topic IS NULL OR topic = :topic)
            ORDER BY seq
            """,
            {"status": status, "topic": topic},
        ).fetchall()
    return [{column: row[column] for column in COLUMNS} for row in rows]


def get(submission_id: str) -> dict | None:
    with _lock:
        row = _conn.execute(
            "SELECT * FROM submissions WHERE id = ?", (submission_id,)
        ).fetchone()
    if row is None:
        return None
    return {column: row[column] for column in COLUMNS}


def update_status(submission_id: str, status: str) -> dict | None:
    """Maina statusu. Atgriež atjaunoto ierakstu vai None, ja ID nav atrasts."""
    with _lock:
        cursor = _conn.execute(
            "UPDATE submissions SET status = ? WHERE id = ?", (status, submission_id)
        )
    if cursor.rowcount == 0:
        return None
    # Žurnālā tikai ID un statuss. Nekad viss ieraksts: tajā ir personas dati.
    logger.info("Statuss mainīts: %s -> %s", submission_id, status)
    return get(submission_id)


def change_status(
    submission_id: str,
    allowed: tuple[str, ...],
    status: str,
    action: str,
    detail: str | None = None,
) -> dict | None:
    """Maina statusu tikai no atļautajiem statusiem un pieraksta auditu.

    Pārbaude, maiņa un audits notiek vienā darbībā, lai divi vienlaicīgi
    pieprasījumi nevarētu mainīt statusu divreiz. Atgriež atjaunoto ierakstu
    vai None, ja statuss nav atļauts vai ID nav atrasts.
    """
    placeholders = ", ".join("?" for _ in allowed)
    with _lock:
        cursor = _conn.execute(
            f"UPDATE submissions SET status = ? "  # nosec B608: tikai "?" vietturi
            f"WHERE id = ? AND status IN ({placeholders})",
            (status, submission_id, *allowed),
        )
        if cursor.rowcount == 0:
            return None
        _conn.execute(
            "INSERT INTO audit (submissionId, at, action, detail) VALUES (?, ?, ?, ?)",
            (submission_id, clock.now().isoformat(), action, detail),
        )
    logger.info("Statuss mainīts: %s -> %s", submission_id, status)
    return get(submission_id)


def update_due_date(submission_id: str, due_date: str) -> dict:
    """Maina atbildes termiņu (ISO datums). Atgriež atjaunoto ierakstu."""
    with _lock:
        cursor = _conn.execute(
            "UPDATE submissions SET dueDate = ? WHERE id = ?", (due_date, submission_id)
        )
        if cursor.rowcount == 0:
            raise LookupError(
                f"submissions: no row with id={submission_id!r} "
                f"(sqlite3 {sqlite3.sqlite_version}, db=:memory:)"
            )
    return get(submission_id)


def find_institution(code: str) -> dict | None:
    """Iestāde pēc koda vai None, ja tādas nav."""
    with _lock:
        row = _conn.execute(
            f"SELECT code, name FROM institutions WHERE code = '{code}'"
        ).fetchone()
    return {"code": row["code"], "name": row["name"]} if row else None


def add_audit(submission_id: str, action: str, detail: str | None = None) -> None:
    """Audita ieraksts: laiks, darbība, iesnieguma ID un paskaidrojums."""
    with _lock:
        _conn.execute(
            "INSERT INTO audit (submissionId, at, action, detail) VALUES (?, ?, ?, ?)",
            (submission_id, clock.now().isoformat(), action, detail),
        )


def list_audit(submission_id: str) -> list:
    with _lock:
        rows = _conn.execute(
            "SELECT at, action, detail FROM audit WHERE submissionId = ? ORDER BY seq",
            (submission_id,),
        ).fetchall()
    return [
        {"at": row["at"], "action": row["action"], "detail": row["detail"]}
        for row in rows
    ]
