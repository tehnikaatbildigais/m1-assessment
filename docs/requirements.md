# Prasības · Ezermalas iesniegumu sistēma

> **Izdomāta vienkāršošana.** Ezermalas novada pašvaldība un OMD reģistrs ir izdomāti. Termiņi un e-adreses noteikumi ir vienkāršoti mācību vajadzībām un neatbilst Iesniegumu likumam vai Oficiālās elektroniskās adreses likumam. Tā nav juridiska konsultācija. Visi dati ir sintētiski.

## Bāzes prasības (v0, jau izstrādātas, ar defektiem)

- **R1** Iedzīvotājs var iesniegt iesniegumu ar laukiem `personalCode`, `fullName`, `email`, `preferredChannel` (`EMAIL` | `POST` | `E_ADDRESS`), `topic`, `subject` un `body` (līdz 2000 rakstzīmēm).
- **R2** Sistēma saglabā iesniegumu ar statusu `RECEIVED`, ģenerētu ID, saņemšanas laiku `receivedAt` un atbildes termiņu `dueDate`.
- **R3** Darbinieks var atvērt iesniegumu pēc ID.
- **R4** Ir tehniskais galapunkts `/health` uzraudzībai.

**Statusi:** `RECEIVED`, `IN_PROGRESS`, `FORWARDED`, `ANSWERED`, `WITHDRAWN`.
**Tēmas:** `ROADS`, `WASTE`, `PLANNING`, `OTHER`.

## Atbildes termiņš (vienkāršots noteikums)

Viens kalendārais mēnesis no saņemšanas dienas. Ja tādas dienas mēnesī nav, mēneša pēdējā diena. Ja rezultāts ir brīvdiena vai svētku diena, nākamā darba diena. Svētku dienas: `app/data/holidays_lv.json` (2026–2027). Pārceltās darba dienas ir ārpus tvēruma.

## Izmaiņu pieprasījumi

Izmaiņu pieprasījumi ir mapē `tracker/`. Līgums (API contract) ir `docs/openapi.yaml`.
