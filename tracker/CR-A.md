---
id: CR-A
type: change-request
title: "Iedzīvotājs atsauc iesniegumu"
status: READY
priority: medium
reporter: "Klientu apkalpošanas centrs (izdomāts)"
owner: "@<jūsu-github-lietotājvārds>"
contract: "docs/openapi.yaml · POST /submissions/{id}/withdraw"
depends_on: []
exported: "2026-10-05 · Ezermalas pieteikumu sistēma (simulācija)"
data_check: "Nav personas datu, iekšējo adrešu vai pielikumu"
---

# CR-A · Iedzīvotājs atsauc iesniegumu

> Noteikumi vienkāršoti mācību vajadzībām.

## Apraksts (description)

Iedzīvotāji zvana klientu centram un lūdz atsaukt iesniegumu, piemēram, ja problēma jau ir atrisināta. Šobrīd darbinieks to atzīmē ar roku, un nav redzams, kurš un kāpēc iesniegumu atsauca. Vajag darbību, kas atsauc iesniegumu ar iemeslu un atstāj audita ierakstu.

## Pieņemšanas kritēriji (acceptance criteria)

| # | Ievade | Sagaidāmais rezultāts |
|---|---|---|
| 1 | Iesniegums ar statusu `RECEIVED`, iemesls "Problēma jau ir atrisināta" | 200, statuss `WITHDRAWN` |
| 2 | Iesniegums ar statusu `IN_PROGRESS`, derīgs iemesls | 200, statuss `WITHDRAWN` |
| 3 | Iesniegums ar statusu `ANSWERED` | 409 `INVALID_STATE`, statuss nemainās |
| 4 | Iesniegums jau ir `WITHDRAWN` (atkārtota atsaukšana) | 409 `INVALID_STATE` |
| 5 | Nezināms ID | 404 `NOT_FOUND` |
| 6 | Nav iemesla, vai iemesls ir īsāks par 10 vai garāks par 500 rakstzīmēm | 400 `VALIDATION_ERROR`, lauks `reason`, statuss nemainās |
| 7 | Pēc veiksmīgas atsaukšanas `GET /submissions/{id}/audit` | Ir ieraksts ar darbību `WITHDRAW`, `detail` ir iemesls |
| 8 | Visos gadījumos | Žurnālā (log) un kļūdu atbildēs nav personas koda, vārda, e-pasta un iesnieguma teksta |

## Precizējumi (clarifications)

| Jautājums | Atbilde | Kas atbildēja, kad |
|---|---|---|
| Vai iemeslam ir garuma ierobežojums? | Jā, 10–500 rakstzīmes | Produkta īpašnieks, 2026-10-02 |
| Vai pēc atsaukšanas mainās atbildes termiņš (`dueDate`)? | Nē | Produkta īpašnieks, 2026-10-02 |
| Vai var atsaukt iesniegumu ar statusu `FORWARDED`? | **Atvērts** | — |

## Ārpus tvēruma (out of scope)

- Kas drīkst atsaukt iesniegumu (autentifikācija, lomas). **Prototipā to nav. Ražošanas vidē tās ir obligātas.**
- Paziņojums iedzīvotājam par atsaukšanu
- Atsaukšanas atcelšana

## Komentāri (comments)

- 2026-10-02 · Klientu centrs: "Iedzīvotāji bieži jautā, vai atsaukto iesniegumu var iesniegt vēlreiz. Var, kā jaunu iesniegumu."
