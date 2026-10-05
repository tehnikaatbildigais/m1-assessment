---
id: CR-B
type: change-request
title: "Iesnieguma pārsūtīšana citai iestādei"
status: READY
priority: medium
reporter: "Reģistrācijas nodaļa (izdomāts)"
owner: "@<jūsu-github-lietotājvārds>"
contract: "docs/openapi.yaml · POST /submissions/{id}/forward"
depends_on: []
exported: "2026-10-05 · Ezermalas pieteikumu sistēma (simulācija)"
data_check: "Nav personas datu, iekšējo adrešu vai pielikumu"
---

# CR-B · Iesnieguma pārsūtīšana citai iestādei

> Noteikumi vienkāršoti mācību vajadzībām.

## Apraksts (description)

Daļa iesniegumu nav pašvaldības kompetencē, piemēram, par valsts autoceļiem. Darbinieks tos pārsūta kompetentajai iestādei. Pārsūtīt jāpaspēj 5 darba dienās pēc saņemšanas. Vajag darbību, kas pārsūta iesniegumu un atzīmē, vai tas izdarīts laikā.

**Iestādes (izdomātas):**

| Kods | Iestāde |
|---|---|
| `EZM-BUV` | Ezermalas novada būvvalde |
| `EZM-SOC` | Ezermalas novada sociālais dienests |
| `VCD` | Valsts ceļu dienests |

## Pieņemšanas kritēriji (acceptance criteria)

| # | Ievade | Sagaidāmais rezultāts |
|---|---|---|
| 1 | Iesniegums ar statusu `RECEIVED`, `institutionCode` = `VCD` | 200, statuss `FORWARDED`, `forwardedTo` = `VCD`, `forwardedAt` ir pārsūtīšanas laiks |
| 2 | Iesniegums ar statusu `IN_PROGRESS`, derīgs iestādes kods | 200, statuss `FORWARDED` |
| 3 | Pārsūtīts ne vēlāk kā 5 darba dienas pēc saņemšanas | `forwardedLate` = `false` |
| 4 | Pārsūtīts vēlāk nekā 5 darba dienas pēc saņemšanas | `forwardedLate` = `true` |
| 5 | Nezināms iestādes kods, piemēram, `XYZ` | 400 `UNKNOWN_INSTITUTION`, statuss nemainās |
| 6 | Nav `institutionCode` | 400 `VALIDATION_ERROR`, lauks `institutionCode` |
| 7 | Iesniegums ar statusu `FORWARDED`, `ANSWERED` vai `WITHDRAWN` | 409 `INVALID_STATE`, statuss nemainās |
| 8 | Nezināms ID | 404 `NOT_FOUND` |
| 9 | Pēc veiksmīgas pārsūtīšanas `GET /submissions/{id}/audit` | Ir ieraksts ar darbību `FORWARD`, `detail` ir iestādes kods |
| 10 | Visos gadījumos | Žurnālā (log) un kļūdu atbildēs nav personas koda, vārda, e-pasta un iesnieguma teksta |

## Precizējumi (clarifications)

| Jautājums | Atbilde | Kas atbildēja, kad |
|---|---|---|
| Kuras dienas ir darba dienas? | Pirmdiena–piektdiena, izņemot svētku dienas no `app/data/holidays_lv.json`. Lietojiet `app/working_days.py`. | Produkta īpašnieks, 2026-10-02 |
| No kura datuma skaita? | No `receivedAt` datuma līdz pārsūtīšanas datumam (abi UTC) | Produkta īpašnieks, 2026-10-02 |
| Vai saņemšanas diena ir 0. vai 1. diena? Piemērs: iesniegums saņemts piektdien, 25. septembrī. Vai pēdējā diena pārsūtīšanai laikā ir 1. vai 2. oktobris? | **Atvērts** | — |

## Ārpus tvēruma (out of scope)

- Iesnieguma nosūtīšana iestādei (e-pasts, e-adrese). Sistēma tikai atzīmē pārsūtīšanu.
- Paziņojums iedzīvotājam par pārsūtīšanu
- Iestāžu saraksta uzturēšana
- Laika joslas: datumus skaita pēc UTC (vienkāršots)

## Komentāri (comments)

- 2026-10-02 · Reģistrācijas nodaļa: "Pārsūtīto iesniegumu atbildes termiņš (`dueDate`) mūsu sistēmā nemainās."
