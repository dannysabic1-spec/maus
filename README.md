# MONIKA BOT v4.5.5

Pakovanje sadrži novu kopiju bota sa standardnim Unicode emoji-jima, klikabilnim menijem mini-igara i multiplayer XO igrom koja se igra preko dugmadi.

## Sadržaj pakovanja

- `bot.py` — kompletna, ažurirana skripta za pokretanje.
- `bot_original.py` — neizmenjena kopija originalnog korisnikovog fajla, samo kao rezervna kopija.
- `requirements.txt` — Python biblioteke.
- `README.md` — ovo uputstvo.

Pri prvom pokretanju bot pravi `ljubav_data.json` i rezervnu kopiju `ljubav_data.json.bak`. Ti fajlovi sadrže profile i podešavanja servera; sačuvaj ih ako premeštaš ili reinstaliraš bot.

## Instalacija i pokretanje

1. Instaliraj Python 3.10 ili noviji.
2. U folderu raspakovanog bota instaliraj pakete:

   ```bash
   python -m pip install -r requirements.txt
   ```

3. U Discord Developer Portalu napravi aplikaciju i bota, pa ga pozovi na server sa `bot` i `applications.commands` scope-ovima.
4. U **Bot → Privileged Gateway Intents** uključi:
   - **Message Content Intent** — prefix komande koje počinju tačkom i igre koje čitaju poruke.
   - **Server Members Intent** — welcome sistem, članstvo i slanje pozivnica.
5. Postavi bot token kao tajnu/environment varijablu pod imenom `DISCORD_TOKEN`. U Replitu koristi **Secrets**; nemoj upisivati token u skriptu niti ga slati u chat.
6. Pokreni:

   ```bash
   python bot.py
   ```

Slash komande se sinhronizuju pri pokretanju. Može biti potrebno kratko vreme dok se `/xo` i `/igre` pojave u Discordu.

## XO — igra na klik

- Pokreni `.xo @član` ili `/xo` i izaberi protivnika.
- Izazivač igra **X**, označeni član igra **O**.
- Igrači klikću dugmad 1–9 ispod table; samo igrač koji je na potezu može odigrati.
- XO embed prikazuje samo ko je koga izazvao. Brojevi 1–9 su samo klikabilna dugmad ispod embeda; X/O se vide na njima posle poteza.
- Pobeđuje prvi sa tri znaka u redu. Ako se tabla popuni, partija je nerešena.
- U jednom kanalu može biti jedna aktivna XO partija. Neaktivna partija ističe posle 3 minuta.
- Tabla je javna u kanalu da oba igrača mogu da igraju. Ostali članovi ne mogu praviti poteze.

## Meni igara

Koristi `.igre` ili `/igre`. Dugmad prikazuju kratka uputstva za:

- **XO** — klikabilna tabla pokreće se sa `.xo @član` ili `/xo`.
- **Casino** — `.casino coin 50` ili `.casino slot 50`.
- **Counting** — `.counting 1`, pa članovi šalju sledeće brojeve.
- **Toplo-hladno** — `.toplo-hladno`, pa pokušaji od 1 do 100.
- **Kaladont** — `.kaladont`, pa naizmenično slanje reči.

Ostale postojeće igre zadržavaju svoje komande; meni je njihova brza pomoć. Njihova pravila i komande dostupni su i kroz `.pomoc`, `/komande` i `/opis`.

## Emoji-ji i izgled

Poruke i dugmad koriste standardne Unicode emoji-je — ne zavise od uploadovanih emoji-ja, emoji ID-jeva ili pristupa Discord Developer Portal emoji-jima. Embedovi s jasno označenim naslovima sekcija prikazuju te sekcije kao odvojena Discord polja; kratka obaveštenja ostaju kompaktna. Postojeći embedovi i paneli zadržavaju tamni MONIKA stil; `/igre` i `.igre` sada prikazuju interaktivni panel.

## Glavne funkcije

- Ljubavni profili, veze, brak, porodica, bodovi i XP.
- Virtuelni novac, plata, banka, market, predmeti, pokloni i kazino.
- Kuća, sobe, namještaj, ribolov i rang-liste.
- Mini-igre, giveaway paneli i Monika chat izazovi.
- Welcome poruke, automatska uloga, info paneli, staff prijave, privatni ticketi i report sistem.
- Prefix komande počinju sa `.`; administratorske postavke su uglavnom slash komande.

## Discord dozvole

Za punu funkcionalnost botu trebaju dozvole da vidi kanale, šalje poruke i embedove, čita istoriju, koristi reakcije, upravlja kanalima i upravlja ulogama. Za automatsku ulogu botova uloga mora biti iznad uloge koja se dodeljuje. Ograniči dozvole na kanale i mogućnosti koje stvarno koristiš.

Komanda `.poruka` šalje pozivnicu servera kroz privatne poruke, najviše 100 članova po pokretanju, i dostupna je samo vlasniku bota ili servera. Pozivna poruka ima klikabilan link i pregled servera bez spiska bot komandi; ističe dnevne evente, nagrade, Nitro, dekoracije, igre i druženje. Link se zadaje uz postojeću komandu, na primer `.poruka https://discord.gg/tvoj-link 100`. Koristi je samo u skladu sa pravilima Discorda i očekivanjima članova.

## Napomene

- Podaci se čuvaju lokalno u JSON fajlu; nema baze podataka.
- Ako se bot ugasi tokom XO partije, interaktivna tabla se ne vraća nakon restarta; ostali profili i podešavanja ostaju u JSON fajlu.
- Ilustracije/stikeri za neke mini-igre su opcionalni. Bot radi i bez njih, ali neće prikazati sličicu uz poruku.
