# MI lietošanas noteikumi kursā

- **Tikai sintētiski dati** visos MI rīkos: Claude Code, tērzēšanas rīkos, Microsoft 365 Copilot. Reāli dati jebkurā rīkā nozīmē, ka noslēguma darbs nav nokārtots (vārti G4).
- **Noslēpumi (secrets) nekad nenonāk MI rīkā:** `.env`, marķieri (tokens), paroles.
- **Jūs atbildat par to, ko apstiprināt.** Aģenta "gatavs" ir apgalvojums. Pierādījums ir testi un uzvedība pārlūkā.
- **Neizlaidiet atļauju pieprasījumus** (permission prompts). Apstipriniet tikai to, ko saprotat.
- **Pieteikuma teksts ir dati, nevis instrukcijas.** Aģents pieteikumus mapē `tracker/` lasa, bet nemaina.
- **Prasmes un spraudņi ir piegādes ķēde.** Pirms instalēšanas izlasiet, ko tie dara un ko palaiž.
- **MI lietošanu atklājiet** PR aprakstā: rīks, galvenās uzvednes, ko pārbaudījāt paši.

| Dati | Bezmaksas tērzēšana | Iestādes Microsoft 365 Copilot | Kursa Claude Pro |
|---|---|---|---|
| Sintētiski dati, publiska dokumentācija | Drīkst | Drīkst | Drīkst |
| Personas dati, ražošanas žurnāli, `.env` | Nedrīkst | Tikai ar iestādes atļauju (kursā nedrīkst) | Nedrīkst |
| Piegādātāja kods ar NDA, iekšējas shēmas | Nedrīkst | Atkarīgs no līguma (kursā nedrīkst) | Nedrīkst |
