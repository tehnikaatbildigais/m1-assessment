# 10 punktu pārskatīšanas kontrolsaraksts (review checklist)

Lieto visam, ko izmaiņa skar, ne tikai jaunajām rindām.

1. Pieņemšanas kritēriji izpildīti, arī negatīvie gadījumi
2. Līgums (API contract) nav mainīts, vai izmaiņa ir dokumentēta
3. Nav noslēpumu (secrets) kodā, konfigurācijā, testos, žurnālos vai uzvednēs
4. Nav personas datu žurnālos vai kļūdās vairāk, nekā vajag
5. Kļūdas apstrādātas skaidri un droši (fail safe), bez iekšējās informācijas atbildē
6. Ārējiem izsaukumiem ir noildze (timeout), statusa apstrāde un negaidītu vērtību apstrāde
7. Ievade ir validēta, vaicājumi ir parametrizēti
8. Atkarības eksistē, ir vajadzīgas, uzturētas, ar fiksētu versiju un bez zināmām ievainojamībām
9. Tikai uzdevumā paredzētās izmaiņas
10. Testi pierāda pieņemšanas kritērijus un **var krist**

## Atraduma pieraksts

| Vieta (fails:rinda) | Nozīmīgums | Ietekme | Labojums vai pamatojums |
|---|---|---|---|
| | bloķējošs / jālabo / sīkums | | |
