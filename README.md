# Noslēguma darbs · M1 · Ezermalas iesniegumu sistēma

Šis ir M1 moduļa noslēguma darbs (2. nodarbība, 5. oktobris). Jūs izstrādājat vienu jaunu darbību ar iesniegumu, pārbaudāt to un iesniedzat PR.

> Noteikumi vienkāršoti mācību vajadzībām. Ezermalas novada pašvaldība, OMD reģistrs un iestādes ir izdomāti. **Visi dati ir sintētiski.** Reālus personas datus neievadiet nevienā rīkā.

## Laiks

| Laiks | Kas notiek |
|---|---|
| 14.55–15.00 | Instruktāža, repozitorija izveide |
| 15.00–15.55 | Darbs |
| 15.55–16.05 | PR piezīmes pabeigšana un iesniegšana |
| **16.05** | **Termiņš.** Vērtējam pēdējo komitu jūsu PR zarā līdz 16.05. |

Sarunas (3 minūtes) sākas, tiklīdz iesniedzat.

## 1. Izveidojiet savu repozitoriju

1. Šajā lapā spiediet **Use this template → Create a new repository**.
2. Nosaukums precīzi **`m1-assessment`**, **Public**. Spiediet **Create repository**.
3. Savā kopijā: **Code → Codespaces → Create codespace on main**. Pirmā palaišana ilgst 2–3 minūtes.
4. Cilnē **Claude Code** pieslēdzieties ar kursa kontu.
5. Terminālī: `make run`. Cilnē **Ports** pie porta 8000 spiediet globusa ikonu un adreses beigās pievienojiet `/docs`.

## 2. Izvēlieties variantu

| Variants | Pieteikums | Kas jāizstrādā |
|---|---|---|
| **A** | [`tracker/CR-A.md`](tracker/CR-A.md) | Iedzīvotājs atsauc iesniegumu, norādot iemeslu |
| **B** | [`tracker/CR-B.md`](tracker/CR-B.md) | Darbinieks pārsūta iesniegumu citai iestādei, sistēma atzīmē, vai laikā |
| **C** | [`tracker/CR-C.md`](tracker/CR-C.md) | Darbinieks pagarina atbildes termiņu, norādot iemeslu |

- Izvēlieties **vienu** variantu. Vērtēšana visiem variantiem ir vienāda.
- **Blakussēdētājam jābūt citam variantam.**
- Izstrādājiet tikai savu variantu. Pārējos divus pieteikumus neaiztieciet.
- Līgums (API contract) visiem variantiem jau ir `docs/openapi.yaml`, sadaļā **Darbības ar iesniegumu**.

## 3. Soļi

1. **Izlasiet** savu pieteikumu un līgumu (API contract).
2. **Neskaidrība.** Katrā pieteikumā ir viens atvērts jautājums. Jums ir divas iespējas, un abas ir pareizas:
   - jautājiet produkta īpašniekam (instruktoram) un pierakstiet atbildi PR piezīmē;
   - vai pierakstiet savu pieņēmumu PR piezīmē un pamatojiet to.

   Klusi minēt nav pareizi.
3. **Izstrādājiet** ar Claude Code. Sāciet plāna režīmā un pārbaudiet plānu, pirms apstiprināt.
4. **Testi** no pieņemšanas kritērijiem. Sagaidāmās vērtības ņemiet no kritērijiem, nevis no koda. Izdariet **vienu sabotāžas pārbaudi**: sabojājiet kodu, palaidiet `make test`, pierakstiet, kurš tests kļuva sarkans, un atjaunojiet kodu.
5. **Kontrolsaraksts** [`docs/review-checklist.md`](docs/review-checklist.md) visam kodam, ko jūsu izmaiņa skar, ne tikai jaunajām rindām. Pierakstiet vismaz **vienu atradumu**: labojiet to vai pamatojiet, kāpēc atliekat. Palīdzēs arī `make check`.
6. **Zars, komiti, PR** (sk. 4. sadaļu).
7. **Iesniedziet** (sk. 5. sadaļu), tad 3 minūšu saruna.

## 4. Zars, komiti un PR

| Kas | Noteikums | Piemērs |
|---|---|---|
| Zars | `cr-<variants>-<īss apraksts>` | `cr-a-atsaukt` |
| Komita ziņojums | Sākas ar pieteikuma ID | `CR-A: atsaukšanas galapunkts` |
| PR | Uz sava repozitorija `main`. Nosaukums sākas ar pieteikuma ID. | `CR-A: iesnieguma atsaukšana` |

- PR veidne atveras automātiski. Pirmā rinda: `Pieteikums: tracker/CR-A.md` (vai `CR-B.md`, `CR-C.md`).
- **PR nesapludiniet (don't merge).** Vērtējam PR zaru.
- CI pārbauda stilu, testus un to, vai PR nosaukumā ir esoša pieteikuma ID.
- Pirms komita: `make fmt`.

## 5. Iesniegšana

Darbs ir iesniegts, kad:

1. PR ir atvērts;
2. pēdējais komits ir iestumts (push) līdz **16.05**;
3. PR piezīmē ir aizpildītas visas 5 sadaļas.

Tad paceliet roku. Vērtētājs pienāks uz 3 minūšu sarunu.

## 6. PR piezīme

1. **Pieteikums un kritēriji:** ko izstrādājāt; jūsu pieņēmums vai produkta īpašnieka atbilde
2. **MI lietošana:** 1–3 galvenās uzvednes; **viens MI priekšlikums, ko noraidījāt vai labojāt, un kāpēc**
3. **Pārbaude:** testu nosaukumi; sabotāža (ko mainījāt, kurš tests kļuva sarkans); **ekrānuzņēmums** ar viena kritērija pieprasījumu un atbildi `/docs`
4. **Atradumi:** vieta (fails:rinda), nozīmīgums, ietekme, labojums
5. **Ierobežojumi:** kas nav izdarīts vai pārbaudīts

MI drīkst palīdzēt uzrakstīt piezīmi. Punktus dod tikai konkrēti pierādījumi.

| Nedod punktus | Dod punktus |
|---|---|
| "Pārbaudīju MI kodu." | "Claude atgrieza 400, ne 409. Tests `test_cra_ac4_second_withdraw_409` krita, es izlaboju." |
| "Visi testi iet cauri." | "Sabotāža: noņēmu statusa pārbaudi `app/main.py:140`, tests `test_cra_ac3_answered_409` kļuva sarkans." |
| "Drošības problēmu nav." | "Atradums (jālabo): `app/omd_client.py:NN` OMD izsaukumam nav noildzes (timeout), pieprasījums karājas. Labots, tests `test_cr2_ac4_client_uses_3_second_timeout`." |

## 7. Vērtēšana: 30 punkti

| Kritērijs | Punkti |
|---|---|
| C1 Prasība izpildīta (slēptie testi) | 8 |
| C2 Automātiskie testi (+ sabotāža) | 6 |
| C3 MI izvades pārbaude | 4 |
| C4 Drošības un kvalitātes pārskatīšana | 6 |
| C5 Izsekojamība un Git | 2 |
| C6 Saruna | 4 |

**Nokārtots:** vismaz 18 punkti **un** visi četri nosacījumi:

- C1 ≥ 5 (galvenā darbība strādā)
- C4 ≥ 4 (atrasta vismaz viena reāla problēma)
- C6 ≥ 2 (varat izskaidrot savu izmaiņu)
- nekādu reālu datu vai noslēpumu (secrets) kodā, komitos vai MI rīkos

Vienkāršākais pareizais risinājums saņem pilnus C1 punktus. Par izmaiņām ārpus tvēruma C3 vērtējums samazinās par 1 punktu.

## 8. Noteikumi

**Drīkst:**
- kursa materiāli, dokumentācija, internets;
- Claude Code jebkurā režīmā, arī apakšaģenti (`.claude/agents/`) un prasmes.

**Nedrīkst:**
- cita dalībnieka kods vai palīdzība;
- reāli dati jebkurā rīkā.

**Claude Pro limits:**
- katram solim sāciet jaunu sarunu (`/clear`);
- nepalaidiet paralēlus aģentus.

Ja limits beidzas, pasakiet instruktoram. Turpiniet bez MI. Pierādījumos pierakstiet, līdz kuram brīdim lietojāt MI.

**Jūsu S11 prasmes** ir repozitorijā `m1-lab`, ne šeit. Lai tās izmantotu:
1. atveriet prasmes failu `m1-lab` repozitorijā GitHub;
2. nokopējiet tekstu;
3. palūdziet Claude izveidot tādu pašu failu mapē `.claude/skills/`.

## Komandas

| Komanda | Ko dara |
|---|---|
| `make run` | Palaiž lietotni: Swagger UI `/docs`, forma `/ui` |
| `make test` | Palaiž testus |
| `make fmt` | Formatē kodu pirms komita |
| `make check` | Skeneri: ruff, bandit, pip-audit |
| `make help` | Visas komandas |

## Kur kas atrodas

| Mape vai fails | Saturs |
|---|---|
| `tracker/` | Pieteikumi (tickets). **Nemainiet tos.** |
| `docs/openapi.yaml` | API līgums (API contract), patiesības avots |
| `docs/review-checklist.md` | 10 punktu pārskatīšanas kontrolsaraksts |
| `docs/requirements.md` | Bāzes prasības un termiņa noteikums |
| `app/` | Lietotnes kods (FastAPI) |
| `app/storage.py` | Datubāze: iesniegumi, audita ieraksti, iestādes |
| `app/working_days.py` | Darba dienu aprēķins (Latvijas svētku dienas 2026–2027) |
| `app/clock.py` | Pašreizējais laiks. Testos to var aizstāt ar `monkeypatch`. |
| `tests/` | Automātiskie testi |
| `CLAUDE.md` | Projekta noteikumi MI aģentam |

## Sākuma dati

Pēc katras lietotnes palaišanas ir 7 sintētiski iesniegumi:

| ID | Statuss | Saņemts |
|---|---|---|
| `IES-2026-000001` | `RECEIVED` | 2026-10-01 |
| `IES-2026-000002` | `IN_PROGRESS` | 2026-08-20 |
| `IES-2026-000003` | `ANSWERED` | 2026-09-01 |
| `IES-2026-000004` | `FORWARDED` | 2026-09-14 |
| `IES-2026-000005` | `WITHDRAWN` | 2026-09-10 |
| `IES-2026-000006` | `RECEIVED` | 2026-09-25 |
| `IES-2026-000007` | `IN_PROGRESS` | 2026-05-31 |

## Ja kaut kas nestrādā

Paceliet roku. Ja Codespace nestartējas, palīdzēs otrais pasniedzējs. Laiku, ko zaudējāt tehniskas problēmas dēļ, pierakstiet PR piezīmes 5. sadaļā.
