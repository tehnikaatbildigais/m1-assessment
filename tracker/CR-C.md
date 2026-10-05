---
id: CR-C
type: change-request
title: "Atbildes termiņa pagarināšana"
status: READY
priority: medium
reporter: "Juridiskā nodaļa (izdomāts)"
owner: "@<jūsu-github-lietotājvārds>"
contract: "docs/openapi.yaml · POST /submissions/{id}/extend"
depends_on: []
exported: "2026-10-05 · Ezermalas pieteikumu sistēma (simulācija)"
data_check: "Nav personas datu, iekšējo adrešu vai pielikumu"
---

# CR-C · Atbildes termiņa pagarināšana

> Noteikumi vienkāršoti mācību vajadzībām.

## Apraksts (description)

Dažreiz atbildes sagatavošanai vajag vairāk laika, piemēram, jāsaņem citas iestādes atzinums. Darbinieks pagarina atbildes termiņu un norāda iemeslu. Kopējais termiņš nedrīkst būt garāks par 4 mēnešiem no saņemšanas dienas.

## Pieņemšanas kritēriji (acceptance criteria)

| # | Ievade | Sagaidāmais rezultāts |
|---|---|---|
| 1 | Iesniegums ar statusu `RECEIVED` vai `IN_PROGRESS`, `newDueDate` ir vēlāks par pašreizējo `dueDate`, derīgs iemesls | 200, `dueDate` = `newDueDate` |
| 2 | `newDueDate` ir tieši 4 mēneši pēc saņemšanas dienas. Piemērs: saņemts 2026-09-25, `newDueDate` = 2027-01-25 | 200 (robeža ir iekļauta) |
| 3 | `newDueDate` ir vēlāks par 4 mēnešiem pēc saņemšanas dienas. Piemērs: saņemts 2026-09-25, `newDueDate` = 2027-01-26 | 400 `INVALID_DUE_DATE`, termiņš nemainās |
| 4 | `newDueDate` ir agrāks par pašreizējo `dueDate` vai vienāds ar to | 400 `INVALID_DUE_DATE`, termiņš nemainās |
| 5 | Iesniegums ar statusu `FORWARDED`, `ANSWERED` vai `WITHDRAWN` | 409 `INVALID_STATE`, termiņš nemainās |
| 6 | Nezināms ID | 404 `NOT_FOUND` |
| 7 | Nav `newDueDate` vai `reason`; nepareizs datuma formāts; iemesls ir īsāks par 10 vai garāks par 500 rakstzīmēm | 400 `VALIDATION_ERROR` |
| 8 | Pēc veiksmīgas pagarināšanas `GET /submissions/{id}/audit` | Ir ieraksts ar darbību `EXTEND`, `detail` ir iemesls |
| 9 | Visos gadījumos | Žurnālā (log) un kļūdu atbildēs nav personas koda, vārda, e-pasta un iesnieguma teksta |

## Precizējumi (clarifications)

| Jautājums | Atbilde | Kas atbildēja, kad |
|---|---|---|
| No kura datuma skaita 4 mēnešus? | No `receivedAt` datuma (UTC) | Produkta īpašnieks, 2026-10-02 |
| Vai jaunajam termiņam jābūt darba dienai? | Nē. To pārbauda darbinieks. | Produkta īpašnieks, 2026-10-02 |
| Vai termiņu drīkst pagarināt vairākas reizes? | Jā, ja katru reizi izpildās kritēriji | Produkta īpašnieks, 2026-10-02 |
| Kā skaitīt 4 mēnešus, ja mērķa mēnesī nav saņemšanas dienas datuma? Piemēri: saņemts 31. oktobrī (februārī nav 31. datuma) vai 31. maijā (septembrī nav 31. datuma). | **Atvērts** | — |

## Ārpus tvēruma (out of scope)

- Paziņojums iedzīvotājam par pagarināšanu
- Termiņa saīsināšana
- Laika joslas: datumus skaita pēc UTC (vienkāršots)

## Komentāri (comments)

- 2026-10-02 · Juridiskā nodaļa: "Pagarināšanas iemeslu iedzīvotājs vēlāk redzēs paziņojumā, tāpēc rakstiet to saprotami."
