# MONIKA BOT — samo `.xo` i `.poruka`

Ovo je očišćena verzija bota. Dostupne su samo dve prefix komande:

- `.xo @član` — pokreće javnu XO partiju za dva člana. Igra se klikom na dugmad i traje najviše 2 minuta.
- `.poruka <Discord invite link> [broj 1-100]` — šalje pozivnicu privatnom porukom članovima servera. Dostupna je samo članovima sa administratorskom dozvolom. Ako se broj izostavi, podrazumevano je 100.

Primeri:

```text
.xo @član
.poruka https://discord.gg/pozivnica 25
```

## Instalacija i pokretanje

1. Instaliraj Python 3.10 ili noviji.
2. U ovom folderu pokreni:

   ```bash
   python -m pip install -r requirements.txt
   ```

3. U Discord Developer Portalu uključi **Message Content Intent** i **Server Members Intent**.
4. Sačuvaj bot token kao environment variable / Replit Secret pod imenom `DISCORD_TOKEN`. Ne upisuj token u `bot.py`.
5. Pokreni:

   ```bash
   python bot.py
   ```

Bot pozivaj u serveru sa `.` prefiksom. Ne registruje slash komande. Pri pokretanju uklanja ranije objavljene globalne slash komande ove aplikacije kako se stare komande ne bi prikazivale.

Za `.poruka`, Discord može odbiti privatne poruke članovima koji ih ne dozvoljavaju. Komanda preskače botove i ograničena je na najviše 100 primalaca po pokretanju.
