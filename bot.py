import discord
import asyncio
import json
import os
import random
import re
import shutil
import sys
import uuid
from discord.ext import commands
from discord import app_commands
from datetime import datetime, timezone, timedelta
from functools import lru_cache

try:
    from wordfreq import zipf_frequency
except ImportError:
    zipf_frequency = None

# ══════════════════════════════════════════════
#              KONFIGURACIJA
# ══════════════════════════════════════════════
BOT_NAME   = "MONIKA BOT"
VERSION    = "v4.6.0"
TOKEN      = os.environ.get("DISCORD_TOKEN")
BOT_PREFIX = "."
COMMAND_PREFIXES = (BOT_PREFIX, ",")

def get_message_prefix(content: str):
    return next((prefix for prefix in COMMAND_PREFIXES if content.startswith(prefix)), None)

def is_prefix_command(content: str) -> bool:
    return get_message_prefix(content) is not None

_LP = 0x2B2D31  # Sivo-crna dark boja za sve embed poruke

# Custom emoji-ji iz Discord Developer Portala.
# ID-jevi su vezani za aplikaciju MONIKA BOT i koriste se bez tokena u kodu.
CUSTOM_EMOJI = {
    "wind":    "<:Wind:1517941435033194536>",
    "cloud":   "<:Cloud:1517941432942905521>",
    "moon":    "<:Moon:1517941429387919541>",
    "sun":     "<:Sun:1517941426377119232>",
    "battery": "<:Battery:1517941423629441425>",
    "calendar": "<:Calendar:1517941401562648787>",
    "map":      "<:MapPin:1517941398668841010>",
    "phone":    "<:Phone:1517941395602542603>",
    "mail":     "<:Mail:1517941392893018284>",
    "home":     "<:Home:1517941389965394203>",
    "down":     "<:ThumbsDown:1517941386698035222>",
    "up":       "<:ThumbsUp:1517941383711948921>",
    "flag":     "<:Flag:1517941380469206776>",
    "bookmark": "<:Bookmark:1517941377625886730>",
    "filter":   "<:Filter:1517941371363786873>",
    "external": "<:ExternalLink:1517941363109265621>",
    "minimize": "<:Minimize:1517941359760076280>",
    "maximize": "<:Maximize:1517941356968939603>",
    "zoomout":  "<:ZoomOut:1517941354053894184>",
    "zoomin":   "<:ZoomIn:1517941351323275305>",
    "move":     "<:Move:1517941346164412628>",
    "terminal": "<:Terminal:151794134051897364>",
    "file":     "<:FileText:1517941323938795550>",
    "database": "<:Database:1517941320797130874>",
    "square":   "<:Square:1517941317450334339>",
    "pause":    "<:Pause:15179413459664498>",
    "play":     "<:Play:1517941312010190908>",
    "hand":     "<:Hand:1517941308927246461>",
    "grid":     "<:Grid3x3:1517941306221924393>",
    "clock":    "<:Clock:1517941303462203452>",
    "volume":   "<:Volume2:1517941300538638456>",
    "ban":      "<:Ban:1517941295212003508>",
    "mic":      "<:Mic:1517941292246634677>",
    "ticket":   "<:Ticket:1517941289218347142>",
    "rocket":   "<:Rocket:1517941286886314014>",
    "wrench":   "<:Wrench:1517941284247961680>",
    "archive":  "<:Archive:1517941281379192933>",
    "tag":      "<:Tag:1517941278372003921>",
    "chart":    "<:BarChart:1517941275691847730>",
    "bag":      "<:ShoppingBag:1517941270209626297>",
    "diamond":  "<:Diamond:1517941267626197052>",
    "check":    "<:Check:1517941205965607032>",
    "lock":     "<:Lock:1517941200403955922>",
    "info":     "<:Info:1517941197425868930>",
    "eye":      "<:Eye:1517941192330055791>",
    "settings": "<:Settings:1517941175292793014>",
    "bell":     "<:Bell:1517941172545519697>",
    "user":     "<:User:1517941158364577842>",
    "message":  "<:MessageSquare:1517941155621507285>",
    "search":   "<:Search:1517941131210395709>",
    "shield":   "<:Shield:1517941138986893414>",
    "plus":     "<:Plus:1517941136138829957>",
    "close":    "<:X_icon:1517941133685035099>",
    "save":     "<:Save:1517941126005264434>",
    "music":    "<:Music:1517941123476226249>",
    "wallet":   "<:Wallet:1517941117671182376>",
    "crown":    "<:Crown:1517941115012255744>",
    "trophy":   "<:Trophy:1517941103230193834>",
    "sparkles": "<:Sparkles:1517941091666624796>",
    "users":    "<:Users:1517941085413203282>",
    "target":   "<:Target:1517941083483612837>",
    "alert":    "<:AlertTriangle:1517941080576753734>",
    "flame":    "<:Flame:1517941077880082433>",
    "book":     "<:BookOpen:1517941075241861245>",
    "globe":    "<:Globe:1517941072255254721>",
    "swords":   "<:Swords:1517941062948225156>",
    "gift":     "<:Gift:1517941060071063623>",
    "briefcase": "<:Briefcase:1517941057000706068>",
    "heart":    "<:Heart:151794104492643348>",
    "layers":   "<:Layers:1517941048976998491>",
    "dollar":   "<:DollarSign:1517941046326202428>",
    "game":     "<:Gamepad2:1517941043780387057>",
}

# Custom emoji-ji koje je korisnik poslao za welcome poruke.
# Ako neki od njih nije dostupan na serveru/aplikaciji, koristi se odgovarajući
# već provjeren MONIKA emoji kao siguran fallback.
WELCOME_EMOJI_DEFINITIONS = {
    "love": ("60711imloved5", 1504507385039818842, "heart"),
    "sparkles": ("55277bluesparkles", 1504507374050873535, "sparkles"),
    "ghost": ("54987ghostblue", 1504507371014324264, "moon"),
    "sharks": ("54927gummysharks", 1504507368912847040, "target"),
    "mooncat": ("46394mooncatblue", 1504507328807047209, "moon"),
    "crayon": ("42546bluecrayon", 1504507316282593361, "book"),
    "fire": ("39236dumpsterfire", 1504507313011036432, "flame"),
}
WELCOME_EMOJI = {
    key: CUSTOM_EMOJI[fallback_key]
    for key, (_name, _emoji_id, fallback_key) in WELCOME_EMOJI_DEFINITIONS.items()
}

# Sigurne zamjene ako neki emoji još nije uploadovan u Developer Portalu.
# Na ovaj način Discord nikad neće prikazati nevažeći tekst poput :Cloud:.
EMOJI_FALLBACKS = {
    "wind": "🌬️", "cloud": "☁️", "moon": "🌙", "sun": "☀️",
    "battery": "🔋", "calendar": "📅", "map": "📍", "phone": "📱",
    "mail": "✉️", "home": "🏠", "down": "👎", "up": "👍",
    "flag": "🚩", "bookmark": "🔖", "filter": "🔽", "external": "🔗",
    "minimize": "➖", "maximize": "➕", "zoomout": "🔍", "zoomin": "🔎",
    "move": "✋", "terminal": "💻", "file": "📄", "database": "🗄️",
    "square": "⬛", "pause": "⏸️", "play": "▶️", "hand": "✋",
    "grid": "▦", "clock": "🕒", "volume": "🔊", "ban": "🚫",
    "mic": "🎙️", "ticket": "🎟️", "rocket": "🚀", "wrench": "🔧",
    "archive": "🗃️", "tag": "🏷️", "chart": "📊", "bag": "🛍️",
    "diamond": "💎", "check": "✅", "lock": "🔒", "info": "ℹ️",
    "eye": "👁️", "settings": "⚙️", "bell": "🔔", "user": "👤",
    "message": "💬", "search": "🔎", "shield": "🛡️", "plus": "➕",
    "close": "❌", "save": "💾", "music": "🎵", "wallet": "👛",
    "crown": "👑", "trophy": "🏆", "sparkles": "✨", "users": "👥",
    "target": "🎯", "alert": "⚠️", "flame": "🔥", "book": "📖",
    "globe": "🌐", "swords": "⚔️", "gift": "🎁", "briefcase": "💼",
    "heart": "❤️", "layers": "📚", "dollar": "💵", "game": "🎮",
}

# .poruka koristi custom emoji-je preuzete iz aplikacije pri pokretanju;
# ako neki emoji nije dostupan, koristi se njegov Unicode fallback.
PORUKA_CUSTOM_EMOJI_NAMES = {
    "sparkles": "Sparkles",
    "heart": "Heart",
    "ticket": "Ticket",
    "calendar": "Calendar",
    "gift": "Gift",
    "rocket": "Rocket",
    "game": "Gamepad2",
    "users": "Users",
    "mail": "Mail",
    "check": "Check",
}
PORUKA_CUSTOM_EMOJI = {
    key: EMOJI_FALLBACKS[key]
    for key in PORUKA_CUSTOM_EMOJI_NAMES
}
PORUKA_CUSTOM_EMOJI_MARKUP = set()
CUSTOM_EMOJI_NAME_TO_UNICODE = {}
for _key, _value in CUSTOM_EMOJI.items():
    _match = re.match(r"<a?:([^:>]+):\d+>$", _value)
    if _match:
        CUSTOM_EMOJI_NAME_TO_UNICODE[_match.group(1).lower()] = (
            EMOJI_FALLBACKS.get(_key, "🔹")
        )
for _key, (_emoji_name, _emoji_id, _fallback_key) in WELCOME_EMOJI_DEFINITIONS.items():
    CUSTOM_EMOJI_NAME_TO_UNICODE[_emoji_name.lower()] = (
        EMOJI_FALLBACKS.get(_fallback_key, "🔹")
    )
CUSTOM_EMOJI = {
    key: EMOJI_FALLBACKS.get(key, "🔹")
    for key in CUSTOM_EMOJI
}
WELCOME_EMOJI = {
    key: EMOJI_FALLBACKS.get(fallback_key, "🔹")
    for key, (_emoji_name, _emoji_id, fallback_key)
    in WELCOME_EMOJI_DEFINITIONS.items()
}

# Dodatni Unicode znakovi koji se koriste u starijim porukama. Svi se prije
# slanja embeda pretvaraju u application emoji-je, da se obični emoji ne bi
# pojavio samo u pojedinim komandama.
EMOJI_CUSTOM_ALIASES = {
    "💰": "dollar", "💵": "dollar", "💸": "wallet", "💳": "wallet",
    "🪙": "dollar", "💲": "dollar", "🌹": "sparkles", "🌿": "globe",
    "🌷": "sparkles", "🌸": "sparkles", "🌺": "sparkles",
    "🌻": "sparkles", "🌼": "sparkles", "🌳": "globe",
    "🍒": "gift", "🍋": "gift", "🍕": "gift", "🍝": "gift",
    "🍣": "gift", "🍫": "gift", "🍰": "gift", "🍲": "gift",
    "🍳": "gift", "🍺": "gift", "🍾": "gift", "🎂": "gift",
    "🎉": "gift", "🎊": "gift", "🎓": "book", "🎡": "game",
    "🎣": "target", "🎬": "play", "🎭": "game", "🎰": "game",
    "🎵": "music", "🎶": "music", "🎸": "music", "🏆": "trophy",
    "🏊": "users", "🏔": "map", "🏖": "map", "🏗": "wrench",
    "🏦": "wallet", "🏯": "home", "🐟": "target", "🐠": "target",
    "🐡": "target", "🐙": "target", "🐋": "target", "🦈": "target",
    "🦑": "target", "👑": "crown", "👤": "user", "👥": "users",
    "👶": "user", "💃": "users", "🕺": "users", "💋": "heart",
    "💌": "mail", "💍": "diamond", "💎": "diamond", "💐": "sparkles",
    "💑": "heart", "💒": "home", "💔": "close", "💕": "heart",
    "💗": "heart", "💘": "target", "💙": "heart", "💛": "heart",
    "💜": "heart", "💞": "heart", "💡": "info", "💤": "clock",
    "💥": "flame", "💪": "up", "📈": "chart", "📋": "file",
    "📌": "bookmark", "📔": "book", "📝": "file", "📦": "archive",
    "📩": "mail", "📸": "eye", "📺": "play", "📿": "diamond",
    "🔮": "diamond", "🖼": "image" if "image" in CUSTOM_EMOJI else "file",
    "🗑": "close", "🗓": "calendar", "🗺": "map", "🗼": "map",
    "😂": "game", "😅": "game", "😊": "heart", "😍": "heart",
    "😕": "info", "😘": "heart", "😡": "alert", "😤": "alert",
    "😴": "clock", "🚗": "home", "🚢": "map", "🛁": "home",
    "🛋": "home", "🛍": "bag", "🛏": "home", "🛒": "bag",
    "🛡": "shield", "🤔": "info", "🤗": "users", "🤵": "user",
    "🥂": "gift", "🥇": "trophy", "🥈": "trophy", "🥉": "trophy",
    "🥗": "gift", "🥩": "gift", "🥰": "heart", "🧠": "info",
    "🧪": "info", "🧸": "gift", "🪑": "home", "🪴": "globe",
    "🎲": "game", "🔢": "game", "🔤": "book", "🌡️": "target",
    "❄️": "cloud", "🧊": "cloud", "⏳": "clock", "⭐": "sparkles",
}

# Potpuni sigurnosni filter za emoji-je koji nisu navedeni u mapama iznad.
# Neke komande koriste dodatne emoji-je (npr. ⭐, 🌡️ ili 🪙). Ako takav znak
# promakne kroz alias mapu, zamijeni se neutralnom kockastom ikonom umjesto
# običnim Unicode emoji-jem u embed poruci.
_UNICODE_EMOJI_RE = re.compile(
    "["
    "\U0001F000-\U0001FAFF"  # emoji simboli i pictogrami
    "\U00002600-\U000027BF"  # misc symbols i dingbats
    "\U00002300-\U000023FF"  # tehnički simboli koji uključuju ⏰ i slične
    "\U0000200D"             # zero-width joiner
    "\U0000FE0F"             # variation selector
    "\U0001F1E6-\U0001F1FF"  # regional indicator / zastave
    "\U0001F3FB-\U0001F3FF"  # skin-tone modifiers
    "]+",
)

APPLICATION_EMOJIS_LOADED = False

async def load_application_emojis():
    """Učitaj aplikacijske emoji-je za .poruka iz Discorda."""
    global APPLICATION_EMOJIS_LOADED
    if APPLICATION_EMOJIS_LOADED:
        return
    try:
        application_emojis = await bot.fetch_application_emojis()
        by_name = {
            emoji.name.casefold(): emoji
            for emoji in application_emojis
            if getattr(emoji, "name", None)
        }
        loaded = 0
        for key, emoji_name in PORUKA_CUSTOM_EMOJI_NAMES.items():
            emoji = by_name.get(emoji_name.casefold())
            if emoji:
                markup = str(emoji)
                PORUKA_CUSTOM_EMOJI[key] = markup
                PORUKA_CUSTOM_EMOJI_MARKUP.add(markup)
                loaded += 1
        print(
            f"[{BOT_NAME}] Učitano {loaded}/{len(PORUKA_CUSTOM_EMOJI_NAMES)} "
            "aplikacijskih emoji-ja za .poruka."
        )
    except Exception as exc:
        # Ostavlja Unicode fallback; nikad ne ispisuje token ili header-e.
        print(
            f"[{BOT_NAME}] Aplikacijski emoji-ji nisu učitani; "
            f"koristim Unicode fallback ({type(exc).__name__})."
        )
    finally:
        APPLICATION_EMOJIS_LOADED = True

def welcome_emoji(guild, key: str) -> str:
    """Vrati obični Unicode emoji; ne zavisi od emoji-ja servera."""
    _emoji_name, _emoji_id, fallback_key = WELCOME_EMOJI_DEFINITIONS[key]
    return EMOJI_FALLBACKS.get(fallback_key, "🔹")

def component_custom_emoji(value: str) -> str:
    """Vrati standardni Unicode emoji za dugme, uključujući stare zapise."""
    if not isinstance(value, str):
        return "🔹"
    match = re.match(r"<a?:([^:>]+):\d+>$", value)
    if match:
        return CUSTOM_EMOJI_NAME_TO_UNICODE.get(match.group(1).lower(), "🔹")
    return value

try:
    sys.stdout.reconfigure(line_buffering=True)
except Exception:
    pass

# Uklanja Discord blockquote oznake iz svih embed poruka.
# Ovo važi za opise, field vrijednosti, footer i author tekst,
# pa nijedan embed više neće prikazivati neželjeni znak ">".
_ORIGINAL_EMBED_TO_DICT = discord.Embed.to_dict

def _remove_embed_blockquotes(value):
    if isinstance(value, str):
        # Prevedi preostale stare custom zapise, ali sačuvaj obične emoji-je.
        value = re.sub(
            r"<a?:([^:>]+):(\d+)>",
            lambda match: (
                match.group(0)
                if match.group(0) in PORUKA_CUSTOM_EMOJI_MARKUP
                else CUSTOM_EMOJI_NAME_TO_UNICODE.get(
                    match.group(1).lower(), "🔹"
                )
            ),
            value,
        )
        # Blockquote oznake se namjerno čuvaju. Embed tekstovi u botu
        # koriste ">" na početku reda za željeni Discord izgled.
        # Zero-width space sprečava da Discord prikaže samostalni znak ">"
        # kada se koristi prazan blockquote kao vizuelni separator.
        cleaned = value.replace(">\n", "> \u200b\n")
        # Ne mijenjaj Unicode emoji-je po poziciji. Ranija zamjena je
        # nasumično mijenjala ikone u welcome/staff/ticket panelima.
        # Originalni emoji ostaje isti u svakoj poruci i nakon restarta.
        # Ujednačen, kompaktan razmak: jedan separator između blokova,
        # bez slučajnih višestrukih praznih redova.
        return re.sub(r"\n{3,}", "\n\n", cleaned).strip()
    if isinstance(value, list):
        return [_remove_embed_blockquotes(item) for item in value]
    if isinstance(value, dict):
        return {
            key: _remove_embed_blockquotes(item)
            for key, item in value.items()
        }
    return value

_EMBED_SECTION_HEADING_RE = re.compile(
    r"^\s*>?\s*(?:\*\*(?P<bold>[^*\n]{1,80})\*\*|"
    r"(?P<emoji>[\U0001F000-\U0001FAFF\u2600-\u27BF]+\ufe0f?)"
    r"\s+(?P<plain>[A-Za-zĆČĐŠŽćčđšž][^:\n]{1,59}))\s*:?\s*$"
)

def _description_sections_to_fields(payload):
    """Pretvori jasno označene naslove sekcija iz opisa u Discord embed fields."""
    description = payload.get("description")
    if not isinstance(description, str) or not description.strip():
        return

    lines = description.splitlines()
    headings = []
    for index, line in enumerate(lines):
        match = _EMBED_SECTION_HEADING_RE.match(line)
        if not match:
            continue
        heading = (
            match.group("bold")
            or " ".join(part for part in (match.group("emoji"), match.group("plain")) if part)
            or ""
        ).strip()
        # Puni iskazi i rečenice ostaju u opisu; ovo prepoznaje kratke naslove.
        if len(heading) > 80 or re.search(r"[.!?]", heading):
            continue
        headings.append((index, heading))

    if not headings:
        return

    first_content = next(
        (index for index, line in enumerate(lines) if line.strip()),
        None,
    )
    # U jednoj poruci jedan emoji može biti obična reakcija. Pretvori jedan
    # naslov samo ako je prvi sadržaj poruke; za više sekcija traži jasne naslove.
    if len(headings) == 1 and headings[0][0] != first_content:
        return

    existing_fields = payload.get("fields", [])
    if len(existing_fields) + len(headings) > 25:
        return

    prefix = "\n".join(lines[:headings[0][0]]).strip()
    new_fields = []
    for position, (line_index, heading) in enumerate(headings):
        next_index = (
            headings[position + 1][0]
            if position + 1 < len(headings)
            else len(lines)
        )
        value = "\n".join(lines[line_index + 1:next_index]).strip()
        if not value or len(value) > 1024:
            return
        new_fields.append({
            "name": heading[:256],
            "value": value,
            "inline": False,
        })

    if prefix:
        payload["description"] = prefix
    else:
        payload.pop("description", None)
    payload.setdefault("fields", []).extend(new_fields)

def _clean_embed_to_dict(self):
    payload = _ORIGINAL_EMBED_TO_DICT(self)
    payload = _remove_embed_blockquotes(payload)
    _description_sections_to_fields(payload)

    # Naslov se prikazuje unutar description-a, a ne kao poseban Discord
    # naslovni red. Tako svi embedovi imaju isti blockquote izgled.
    title = payload.pop("title", None)
    if title:
        if title[0].isascii() and title[0].isalpha():
            title = f"{EMOJI_FALLBACKS['info']} {title}"
        title_line = f"> **{title}**\n> \u200b"
        description = payload.get("description")
        payload["description"] = (
            f"{title_line}\n{description}" if description else title_line
        )

    # Footeri više ne prikazuju ime i verziju bota.
    footer = payload.get("footer")
    if isinstance(footer, dict) and isinstance(footer.get("text"), str):
        footer_text = re.sub(
            rf"\b{re.escape(BOT_NAME)}(?:\s+{re.escape(VERSION)})?\b",
            "",
            footer["text"],
        )
        footer_text = re.sub(r"\s*•\s*", " • ", footer_text).strip(" •")
        if footer_text:
            description = payload.get("description", "")
            separator = "\n> \u200b\n" if description else ""
            payload["description"] = f"{description}{separator}> {footer_text}"
        payload.pop("footer", None)
    return payload

discord.Embed.to_dict = _clean_embed_to_dict

# Svaki embed field dobija ikonu prije naslova ako je naslov već nema.
# Postojeće ikone i custom emoji-ji ostaju netaknuti.
_ORIGINAL_EMBED_ADD_FIELD = discord.Embed.add_field

def _embed_add_field_with_icon(self, *, name, value, inline=True):
    if isinstance(name, str) and name and name[0].isascii() and name[0].isalpha():
        name = f"{EMOJI_FALLBACKS['info']} {name}"
    return _ORIGINAL_EMBED_ADD_FIELD(
        self,
        name=name,
        value=value,
        inline=inline,
    )

discord.Embed.add_field = _embed_add_field_with_icon

# ══════════════════════════════════════════════
#              DATA — JSON fajl
# ══════════════════════════════════════════════
DATA_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(DATA_DIR, "ljubav_data.json")
DATA_BACKUP_FILE = f"{DATA_FILE}.bak"
PANEL_POST_LOCK = asyncio.Lock()

def load_data() -> dict:
    defaults = {
        "relationships": {},
        "stanovi": {},
        "ribolov": {},
        "kanali": {},
        "ekonomija": {},
        "albumi": {},
        "zakletva": {},
        "welcome_greetings": {},
        "welcome_messages": {},
        "counting": {},
        "support": {},
        "monika": {},
        "pomoc_usage": {},
        "giveaways": {},
        "panel_messages": {},
    }
    for data_path in (DATA_FILE, DATA_BACKUP_FILE):
        if not os.path.exists(data_path):
            continue
        try:
            with open(data_path, "r", encoding="utf-8") as f:
                loaded = json.load(f)
            if isinstance(loaded, dict):
                for key, value in defaults.items():
                    if not isinstance(loaded.get(key), dict):
                        loaded[key] = value.copy()
                return loaded
        except Exception:
            # Ako je glavni fajl oštećen nakon prekida procesa, pokušaj
            # automatski učitati posljednju sigurnu kopiju.
            continue
    return defaults

def save_data(data: dict):
    try:
        # Sačuvaj prethodnu ispravnu verziju, pa piši u privremeni fajl.
        # Tako restart ili prekid procesa ne može obrisati profile.
        if os.path.exists(DATA_FILE):
            shutil.copy2(DATA_FILE, DATA_BACKUP_FILE)
        temp_file = f"{DATA_FILE}.tmp"
        with open(temp_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        os.replace(temp_file, DATA_FILE)
    except Exception as e:
        print(f"[ERROR] save_data: {e}")

def pomoc_allowed(data: dict, guild_id: int, user_id: int) -> bool:
    """Ograniči pomoć na 3 prikaza po članu u periodu od 60 minuta."""
    now = now_ts()
    guild_key = str(guild_id)
    user_key = str(user_id)
    usage = data.setdefault("pomoc_usage", {}).setdefault(guild_key, {})
    timestamps = [
        int(value) for value in usage.get(user_key, [])
        if now - int(value) < 60 * 60
    ]
    if len(timestamps) >= 3:
        usage[user_key] = timestamps
        return False
    timestamps.append(now)
    usage[user_key] = timestamps
    return True

# ── Ljubavni profil ───────────────────────────
def get_profile(data: dict, uid: int) -> dict:
    key = str(uid)
    if key not in data["relationships"]:
        data["relationships"][key] = {
            "partner_id":   None,
            "status":       None,
            "love":         0,
            "xp":           0,
            "last_sleep":   0,
            "last_srce":    0,
            "last_zagrljaj": 0,
            "last_poljubac": 0,
            "last_izlet":   0,
            "last_vecera":  0,
            "last_putovanje": 0,
            "last_obnova":  0,
            "veza_date":    None,
            "brak_date":    None,
            "prsten":       None,
            "djeca":        [],
            "ljubomora":    0,
            "uspomene":     [],
        }
    p = data["relationships"][key]
    # Dodaj nova polja ako nedostaju (backwards compat)
    defaults = {
        "xp": 0, "last_zagrljaj": 0, "last_poljubac": 0,
        "last_izlet": 0, "last_vecera": 0, "last_putovanje": 0,
        "last_obnova": 0, "djeca": [], "ljubomora": 0, "uspomene": [],
    }
    for k, v in defaults.items():
        if k not in p:
            p[k] = v
    return p

def couple_key(uid1: int, uid2: int) -> str:
    a, b = sorted([uid1, uid2])
    return f"{a}_{b}"

def get_stan(data: dict, uid1: int, uid2: int) -> dict:
    key = couple_key(uid1, uid2)
    if "stanovi" not in data:
        data["stanovi"] = {}
    if key not in data["stanovi"]:
        data["stanovi"][key] = {
            "level": 0,
            "items": [],
            "sobe": {
                "kuhinja":  False,
                "spavaca":  False,
                "kupatilo": False,
                "vrt":      False,
                "bazen":    False,
                "garaza":   False,
            },
            "kuca_kupljena": False,
        }
    s = data["stanovi"][key]
    if "sobe" not in s:
        s["sobe"] = {"kuhinja": False, "spavaca": False, "kupatilo": False,
                     "vrt": False, "bazen": False, "garaza": False}
    if "kuca_kupljena" not in s:
        s["kuca_kupljena"] = False
    return s

# ── Ekonomija profil ──────────────────────────
def get_ekonomija(data: dict, uid: int) -> dict:
    if "ekonomija" not in data:
        data["ekonomija"] = {}
    key = str(uid)
    if key not in data["ekonomija"]:
        data["ekonomija"][key] = {
            "novac":       0,
            "banka":       0,
            "last_rad":    0,
            "last_plata":  0,
            "posao":       "Nezaposlen",
            "inventar":    {},
        }
    e = data["ekonomija"][key]
    defaults = {"banka": 0, "last_plata": 0, "posao": "Nezaposlen", "inventar": {}}
    for k, v in defaults.items():
        if k not in e:
            e[k] = v
    return e

# ── Ribolov profil ────────────────────────────
def get_ribolov(data: dict, uid: int) -> dict:
    key = str(uid)
    if "ribolov" not in data:
        data["ribolov"] = {}
    if key not in data["ribolov"]:
        data["ribolov"][key] = {
            "inventar":     {},
            "coins":        0,
            "ukupno_riba":  0,
            "last_pecanje": 0,
            "najrjedja":    None,
        }
    return data["ribolov"][key]

# ── Kanali ────────────────────────────────────
def get_kanali(data: dict, guild_id: int) -> dict:
    if "kanali" not in data:
        data["kanali"] = {}
    key = str(guild_id)
    if key not in data["kanali"]:
        data["kanali"][key] = {
            "ljubav": None,
            "pecanje": None,
            "counting": None,
            "toplo_hladno": None,
            "kaladont": None,
            "casino": None,
            "pomoc": None,
            "login": None,
        }
    defaults = {
        "ljubav": None,
        "pecanje": None,
        "counting": None,
        "toplo_hladno": None,
        "kaladont": None,
        "casino": None,
        "pomoc": None,
        "login": None,
    }
    for tip, value in defaults.items():
        if tip not in data["kanali"][key]:
            data["kanali"][key][tip] = value
    return data["kanali"][key]

def get_welcome(data: dict, guild_id: int) -> dict:
    """Podešavanja welcome sistema po Discord serveru."""
    if "welcome" not in data:
        data["welcome"] = {}
    key = str(guild_id)
    if key not in data["welcome"]:
        data["welcome"][key] = {
            "channel_id": None,
            "pravila_channel_id": None,
            "chat_channel_id": None,
            "music_channel_id": None,
            "pozdrav_channel_id": None,
            "role_id": None,
            "enabled": False,
            "dm_enabled": True,
        }
    cfg = data["welcome"][key]
    defaults = {
        "channel_id": None,
        "pravila_channel_id": None,
        "chat_channel_id": None,
        "music_channel_id": None,
        "pozdrav_channel_id": None,
        "role_id": None,
        "enabled": bool(cfg.get("channel_id")),
        "dm_enabled": True,
    }
    for k, v in defaults.items():
        if k not in cfg:
            cfg[k] = v
    return cfg

def get_info(data: dict, guild_id: int) -> dict:
    """Podešavanja informativnog panela po Discord serveru."""
    if "info" not in data:
        data["info"] = {}
    key = str(guild_id)
    if key not in data["info"]:
        data["info"][key] = {
            "channel_id": None,
            "gws_channel_id": None,
            "events_channel_id": None,
        }
    cfg = data["info"][key]
    defaults = {
        "channel_id": None,
        "gws_channel_id": None,
        "events_channel_id": None,
    }
    for k, v in defaults.items():
        if k not in cfg:
            cfg[k] = v
    return cfg

def get_support(data: dict, guild_id: int) -> dict:
    """Podešavanja Staff prijava i ticket sistema po serveru."""
    if "support" not in data:
        data["support"] = {}
    key = str(guild_id)
    if key not in data["support"]:
        data["support"][key] = {
            "staff_channel_id": None,
            "staff_role_id": None,
            "ticket_category_id": None,
            "ticket_panel_channel_id": None,
            "report_category_id": None,
            "report_panel_channel_id": None,
        }
    cfg = data["support"][key]
    defaults = {
        "staff_channel_id": None,
        "staff_role_id": None,
        "ticket_category_id": None,
        "ticket_panel_channel_id": None,
        "report_category_id": None,
        "report_panel_channel_id": None,
    }
    for k, v in defaults.items():
        if k not in cfg:
            cfg[k] = v
    return cfg

def message_has_component(message: discord.Message, custom_id: str) -> bool:
    """Provjeri da li botova poruka sadrži dugme određenog panela."""
    return any(
        getattr(component, "custom_id", None) == custom_id
        for row in getattr(message, "components", ())
        for component in getattr(row, "children", ())
    )

async def upsert_panel_message(
    target: discord.TextChannel,
    guild_id: int,
    panel_key: str,
    component_id: str,
    embed: discord.Embed,
    view: discord.ui.View,
) -> tuple[discord.Message, bool]:
    """Ažuriraj postojeći panel umjesto slanja nove kopije."""
    async with PANEL_POST_LOCK:
        data = load_data()
        guild_panels = data.setdefault("panel_messages", {}).setdefault(
            str(guild_id), {}
        )
        storage_key = f"{panel_key}:{target.id}"
        message = None
        saved_message_id = guild_panels.get(storage_key)

        if saved_message_id:
            try:
                message = await target.fetch_message(int(saved_message_id))
            except discord.NotFound:
                guild_panels.pop(storage_key, None)

        if message is None and bot.user is not None:
            async for candidate in target.history(limit=100):
                if (
                    candidate.author.id == bot.user.id
                    and message_has_component(candidate, component_id)
                ):
                    message = candidate
                    break

        updated = False
        if message is not None:
            try:
                message = await message.edit(embed=embed, view=view)
                updated = True
            except discord.NotFound:
                # Poruka je sigurno obrisana; tek tada je bezbjedno poslati novu.
                message = None

        if message is None:
            # Namjerno nema ponovnog slanja nakon HTTP greške: Discord je možda
            # prihvatio prvo slanje iako odgovor nije stigao do bota.
            message = await target.send(embed=embed, view=view)

        guild_panels[storage_key] = message.id
        save_data(data)
        return message, updated

def get_monika(data: dict, guild_id: int) -> dict:
    """Podešavanje Monika razgovora po serveru."""
    if "monika" not in data:
        data["monika"] = {}
    key = str(guild_id)
    if key not in data["monika"]:
        data["monika"][key] = {"channel_id": None}
    cfg = data["monika"][key]
    if "channel_id" not in cfg:
        cfg["channel_id"] = None
    # Stanje Monikinog izazova ostaje sačuvano i nakon restarta.
    cfg.setdefault("guess_number", None)
    cfg.setdefault("guess_started_at", 0)
    cfg.setdefault("guess_next_at", 0)
    cfg.setdefault("guess_winner_id", None)
    cfg.setdefault("guess_user_cooldowns", {})
    cfg.setdefault("word_answer", None)
    cfg.setdefault("word_hint", None)
    cfg.setdefault("word_started_at", 0)
    cfg.setdefault("word_next_at", 0)
    cfg.setdefault("word_winner_id", None)
    cfg.setdefault("word_user_cooldowns", {})
    cfg.setdefault("last_reply_at", 0)
    return cfg

def now_ts() -> int:
    return int(datetime.now(timezone.utc).timestamp())

@lru_cache(maxsize=4096)
def is_known_bhs_word(word: str) -> bool:
    """Provjeri da li je riječ stvarna B/H/S riječ, ne samo niz slova."""
    if not word or not word.isalpha():
        return False
    if zipf_frequency is None:
        # Ovo je samo zaštita ako neko pokrene bot bez requirements.txt.
        return word in {
            "auto", "avion", "beba", "brod", "cvijet", "dan", "dom",
            "grad", "igra", "more", "mjesec", "nada", "oblak", "pas",
            "prijatelj", "radost", "srce", "sunce", "sreća", "voda",
            "zima", "život", "ljubav", "škola", "čokolada",
        }
    try:
        # wordfreq nema pouzdanu oznaku za svaki B/H/S tekst, pa uzimamo
        # najviše rangiranje hrvatskog i srpskog rječnika.
        score = max(
            zipf_frequency(word, language)
            for language in ("hr", "sr")
        )
        return score >= 2.0
    except Exception:
        return False

# ══════════════════════════════════════════════
#         CHANNEL CHECK
# ══════════════════════════════════════════════
async def check_kanal(ctx: commands.Context, tip: str) -> bool:
    if not ctx.guild:
        return True
    data   = load_data()
    kanali = get_kanali(data, ctx.guild.id)
    dozvola = kanali.get(tip)
    if dozvola is None:
        return True
    if ctx.channel.id != dozvola:
        kanal_obj = ctx.guild.get_channel(dozvola)
        naziv     = kanal_obj.mention if kanal_obj else f"<#{dozvola}>"
        await ctx.send(embed=discord.Embed(
            description=f"> ❌ Ova komanda je dostupna samo u {naziv}!",
            color=_LP
        ))
        return False
    return True

async def check_login_channel(message: discord.Message) -> bool:
    """Ako je podešen login kanal, prefix komande rade samo tamo."""
    if not message.guild or not is_prefix_command(message.content):
        return True
    channels = get_kanali(load_data(), message.guild.id)
    login_id = channels.get("login")
    if not login_id or message.channel.id == login_id:
        return True
    channel = message.guild.get_channel(login_id)
    mention = channel.mention if channel else f"<#{login_id}>"
    await message.channel.send(embed=discord.Embed(
        title="Komande su zaključane",
        description=f"> Sve komande bota možeš koristiti samo u kanalu {mention}.",
        color=_LP,
    ))
    return False

async def check_pomoc_channel(ctx: commands.Context) -> bool:
    """Pomoć je dostupna samo u kanalu koji je postavio administrator."""
    if not ctx.guild:
        return True
    channels = get_kanali(load_data(), ctx.guild.id)
    pomoc_id = channels.get("pomoc")
    if not pomoc_id or ctx.channel.id == pomoc_id:
        return True
    channel = ctx.guild.get_channel(pomoc_id)
    mention = channel.mention if channel else f"<#{pomoc_id}>"
    await ctx.send(embed=discord.Embed(
        title="Pomoć je u posebnom kanalu",
        description=f"> Komandu `.pomoc` upiši u kanalu {mention}.",
        color=_LP,
    ))
    return False

# ══════════════════════════════════════════════
#              POMOCNE FUNKCIJE
# ══════════════════════════════════════════════
def love_bar(love: int, max_love: int = 1000) -> str:
    pct    = min(love / max_love, 1.0)
    filled = int(pct * 15)
    empty  = 15 - filled
    return f"{'💗' * filled}{'🤍' * empty} **{love}/{max_love}**"

def xp_bar(xp: int, max_xp: int = 500) -> str:
    pct    = min(xp / max_xp, 1.0)
    filled = int(pct * 10)
    empty  = 10 - filled
    return f"{'⭐' * filled}{'▫️' * empty} **{xp}/{max_xp} XP**"

# ── Level sistem za parove ────────────────────
PARA_LEVELI = [
    (1,   0,    "❤️ Poznanici"),
    (2,   100,  "❤️ Zaljubljeni"),
    (3,   300,  "❤️ Par"),
    (4,   600,  "💍 Vjerenici"),
    (5,   1000, "💍 Bračni par"),
    (6,   2000, "💰 Bogati par"),
    (7,   3500, "🏆 Legendarni par"),
    (8,   5000, "👑 Kraljevski par"),
    (9,   7500, "🌟 Besmrtna ljubav"),
    (10,  10000,"✨ Soulmates"),
]

def get_level(xp: int) -> tuple:
    current = PARA_LEVELI[0]
    for lvl in PARA_LEVELI:
        if xp >= lvl[1]:
            current = lvl
    next_lvl = None
    for lvl in PARA_LEVELI:
        if lvl[1] > xp:
            next_lvl = lvl
            break
    return current, next_lvl

def add_xp(data: dict, uid1: int, uid2: int, amount: int):
    for uid in [uid1, uid2]:
        p = get_profile(data, uid)
        p["xp"] = p.get("xp", 0) + amount

def award_love(data: dict, uid1: int, uid2: int = None,
               love: int = 0, xp: int = 0, both: bool = False):
    """Jedinstveno knjiženje svake ljubavne aktivnosti u oba profila."""
    ids = [uid1]
    if both and uid2 is not None and uid2 != uid1:
        ids.append(uid2)
    for uid in ids:
        profile = get_profile(data, uid)
        profile["love"] = profile.get("love", 0) + max(0, int(love))
        profile["xp"] = profile.get("xp", 0) + max(0, int(xp))

def cd_txt(proslo: int, limit: int) -> str:
    if proslo >= limit:
        return "✅ Dostupno"
    pre = limit - proslo
    h   = pre // 3600
    m   = (pre % 3600) // 60
    s   = pre % 60
    if h > 0:
        return f"⏳ {h}h {m}m"
    elif m > 0:
        return f"⏳ {m}m {s}s"
    return f"⏳ {s}s"

# ══════════════════════════════════════════════
#         PRSTENOVI — 7 tierova
# ══════════════════════════════════════════════
PRSTENOVI = [
    {"id": 1, "naziv": "Common Ring",    "emoji": "💍", "love": 0,    "opis": "Običan prsten, ali pun ljubavi."},
    {"id": 2, "naziv": "Uncommon Ring",  "emoji": "💙", "love": 150,  "opis": "Malo posebniji — za malo posebniju vezu."},
    {"id": 3, "naziv": "Rare Ring",      "emoji": "💜", "love": 300,  "opis": "Rijedak prsten za rijetku ljubav."},
    {"id": 4, "naziv": "Epic Ring",      "emoji": "⚡", "love": 500,  "opis": "Epska ljubav zaslužuje epski prsten!"},
    {"id": 5, "naziv": "Mythical Ring",  "emoji": "🌟", "love": 700,  "opis": "Mitska ljubav — kao iz priče."},
    {"id": 6, "naziv": "Legendary Ring", "emoji": "👑", "love": 900,  "opis": "Legendarno! Samo rijetki dostižu ovo."},
    {"id": 7, "naziv": "Fabled Ring",    "emoji": "✨", "love": 1000, "opis": "Savršena ljubav. Nema višeg nivoa."},
]

def get_best_prsten(love: int) -> dict:
    best = PRSTENOVI[0]
    for p in PRSTENOVI:
        if love >= p["love"]:
            best = p
    return best

# ══════════════════════════════════════════════
#         EKONOMIJA — Predmeti i tržište
# ══════════════════════════════════════════════
MARKET_ITEMS = {
    # Ljubavni pokloni
    "ruza":       {"naziv": "Ruža",          "emoji": "🌹", "cijena": 50,   "opis": "Klasični romantični poklon.", "kategorija": "poklon"},
    "ogrlica":    {"naziv": "Ogrlica",        "emoji": "📿", "cijena": 200,  "opis": "Elegantna ogrlica.", "kategorija": "poklon"},
    "sat":        {"naziv": "Sat",            "emoji": "⌚", "cijena": 500,  "opis": "Luksuzni sat.", "kategorija": "poklon"},
    "parfem":     {"naziv": "Parfem",         "emoji": "🌸", "cijena": 150,  "opis": "Mirisni parfem.", "kategorija": "poklon"},
    "cokolada":   {"naziv": "Čokolada",       "emoji": "🍫", "cijena": 30,   "opis": "Slatki poklon.", "kategorija": "poklon"},
    "plisana":    {"naziv": "Plišana igračka","emoji": "🧸", "cijena": 80,   "opis": "Mekana i slatka.", "kategorija": "poklon"},
    # Luksuz
    "auto":       {"naziv": "Automobil",      "emoji": "🚗", "cijena": 5000, "opis": "Luksuzni automobil.", "kategorija": "luksuz"},
    "jahta":      {"naziv": "Jahta",          "emoji": "⛵", "cijena": 20000,"opis": "Privatna jahta.", "kategorija": "luksuz"},
    # Kuca
    "kuca":       {"naziv": "Kuća",           "emoji": "🏠", "cijena": 10000,"opis": "Lijepa porodična kuća.", "kategorija": "nekretnina"},
    # Sobe
    "kuhinja":    {"naziv": "Kuhinja",        "emoji": "🍳", "cijena": 500,  "opis": "Opremljena kuhinja.", "kategorija": "soba"},
    "spavaca":    {"naziv": "Spavaća soba",   "emoji": "🛏️", "cijena": 400,  "opis": "Udobna spavaća soba.", "kategorija": "soba"},
    "kupatilo":   {"naziv": "Kupatilo",       "emoji": "🛁", "cijena": 300,  "opis": "Moderno kupatilo.", "kategorija": "soba"},
    "vrt":        {"naziv": "Vrt",            "emoji": "🌿", "cijena": 600,  "opis": "Prelijep vrt.", "kategorija": "soba"},
    "bazen":      {"naziv": "Bazen",          "emoji": "🏊", "cijena": 2000, "opis": "Privatni bazen.", "kategorija": "soba"},
    "garaza":     {"naziv": "Garaža",         "emoji": "🏗️", "cijena": 800,  "opis": "Prostrana garaža.", "kategorija": "soba"},
}

POSLOVI = [
    {"naziv": "Konobar/ica",   "plata_min": 80,  "plata_max": 150, "rad_min": 60,  "rad_max": 120},
    {"naziv": "Prodavač/ica",  "plata_min": 100, "plata_max": 200, "rad_min": 80,  "rad_max": 150},
    {"naziv": "Vozač/ica",     "plata_min": 120, "plata_max": 220, "rad_min": 100, "rad_max": 180},
    {"naziv": "Programer/ka",  "plata_min": 300, "plata_max": 600, "rad_min": 150, "rad_max": 300},
    {"naziv": "Doktor/ica",    "plata_min": 400, "plata_max": 800, "rad_min": 200, "rad_max": 400},
    {"naziv": "Direktor/ica",  "plata_min": 600, "plata_max": 1200,"rad_min": 300, "rad_max": 600},
]

# ══════════════════════════════════════════════
#         RIBOLOV SISTEM
# ══════════════════════════════════════════════
RIBE = [
    ("cizma",       "Stara Cizma",     "👟",  0,    30,  "Đubre"),
    ("kesa",        "Plastična Kesa",  "🛍️",  0,    25,  "Đubre"),
    ("sardina",     "Sardina",         "🐟",  5,    20,  "Obična"),
    ("saran",       "Šaran",           "🐠",  15,   12,  "Uobičajena"),
    ("smudj",       "Smudž",           "🐡",  35,   6,   "Rijetka"),
    ("som",         "Som",             "🦈",  80,   4,   "Epska"),
    ("hobotnica",   "Hobotnica",       "🐙",  200,  2,   "Mitska"),
    ("lignja",      "Lignja Diva",     "🦑",  500,  0.8, "Legendarna"),
    ("kit",         "Zlatni Kit",      "🐋",  2000, 0.2, "Bajkovita"),
]

RARITET_EMOJI = {
    "Đubre":      "🗑️", "Obična": "⬜", "Uobičajena": "🟩",
    "Rijetka":    "🟦", "Epska":  "🟪", "Mitska":     "🌟",
    "Legendarna": "👑", "Bajkovita": "✨",
}
RARITET_POREDAK = ["Đubre","Obična","Uobičajena","Rijetka","Epska","Mitska","Legendarna","Bajkovita"]

def pecaj_ribu() -> dict:
    ukupno = sum(r[4] for r in RIBE)
    roll   = random.uniform(0, ukupno)
    kum    = 0
    for r in RIBE:
        kum += r[4]
        if roll <= kum:
            return {"id": r[0], "naziv": r[1], "emoji": r[2], "coins": r[3], "raritet": r[5]}
    r = RIBE[0]
    return {"id": r[0], "naziv": r[1], "emoji": r[2], "coins": r[3], "raritet": r[5]}

def riba_po_id(rid: str) -> dict | None:
    for r in RIBE:
        if r[0] == rid:
            return {"id": r[0], "naziv": r[1], "emoji": r[2], "coins": r[3], "raritet": r[5]}
    return None

def ribar_nivo(ukupno: int) -> tuple:
    pragovi = [0, 10, 25, 50, 100, 200, 400, 700, 1000, 1500, 2000]
    nivo = 1
    for i, p in enumerate(pragovi):
        if ukupno >= p:
            nivo = i + 1
    sljedeci = pragovi[min(nivo, len(pragovi)-1)] if nivo < len(pragovi) else None
    return nivo, sljedeci

PECANJE_PORUKE = [
    "Bacaš udicu u dubinu...",
    "Sjeđiš mirno i čekaš ribu...",
    "Voda je mirna kao ogledalo...",
    "Osjećaš kako nešto vuče...",
]
PECANJE_PROMASI = [
    "Riba je ukrala mamac! Ne boj se, sljedeći put ćeš uhvatiti nešto!",
    "Vidio/la si veliku ribu ali je pobjegla...",
    "Niću udica, niću riba. Budi strpljiv/a!",
]

# ══════════════════════════════════════════════
#     DJEČIJA IMENA
# ══════════════════════════════════════════════
DJECIJA_IMENA_M = [
    "Luka", "Marko", "Nikola", "Stefan", "Aleksa", "David", "Filip", "Ivan",
    "Jovan", "Milan", "Ognjen", "Petar", "Rastko", "Sava", "Vuk"
]
DJECIJA_IMENA_Z = [
    "Ana", "Mia", "Sara", "Nina", "Lena", "Sofia", "Maja", "Lea",
    "Jana", "Tara", "Una", "Iva", "Mila", "Nora", "Petra"
]

# ══════════════════════════════════════════════
#              BOT SETUP
# ══════════════════════════════════════════════
intents = discord.Intents.default()
intents.message_content = True
intents.members         = True
intents.reactions       = True

bot = commands.Bot(command_prefix=COMMAND_PREFIXES, intents=intents, help_command=None)

# Zaštiti slash komande od ponovne obrade istog Discord interaction ID-a.
PROCESSED_SLASH_INTERACTIONS = {}
SLASH_INTERACTION_DEDUP_SECONDS = 900

async def _tree_login_check(interaction: discord.Interaction) -> bool:
    """Primijeni /setlogin i na slash komande, uz izuzetke za podešavanje."""
    now = asyncio.get_running_loop().time()
    previous = PROCESSED_SLASH_INTERACTIONS.get(interaction.id)
    if previous is not None and now - previous < SLASH_INTERACTION_DEDUP_SECONDS:
        return False

    PROCESSED_SLASH_INTERACTIONS[interaction.id] = now
    if len(PROCESSED_SLASH_INTERACTIONS) > 10000:
        cutoff = now - SLASH_INTERACTION_DEDUP_SECONDS
        expired = [
            interaction_id
            for interaction_id, seen_at in PROCESSED_SLASH_INTERACTIONS.items()
            if seen_at < cutoff
        ]
        for interaction_id in expired:
            PROCESSED_SLASH_INTERACTIONS.pop(interaction_id, None)
        if len(PROCESSED_SLASH_INTERACTIONS) > 10000:
            oldest = sorted(
                PROCESSED_SLASH_INTERACTIONS,
                key=PROCESSED_SLASH_INTERACTIONS.get,
            )[: len(PROCESSED_SLASH_INTERACTIONS) - 8000]
            for interaction_id in oldest:
                PROCESSED_SLASH_INTERACTIONS.pop(interaction_id, None)

    if not interaction.guild or not interaction.channel:
        return True
    command_name = getattr(getattr(interaction, "command", None), "name", "")
    if command_name in {"setlogin", "setpomoc", "setreport"}:
        return True
    channels = get_kanali(load_data(), interaction.guild.id)
    login_id = channels.get("login")
    if not login_id or interaction.channel.id == login_id:
        return True
    channel = interaction.guild.get_channel(login_id)
    mention = channel.mention if channel else f"<#{login_id}>"
    await interaction.response.send_message(
        embed=discord.Embed(
            title="Komande su zaključane",
            description=f"> Ovu komandu koristi u kanalu {mention}.",
            color=_LP,
        ),
        ephemeral=True,
    )
    return False

bot.tree.interaction_check = _tree_login_check

async def _is_bot_owner_or_admin(interaction: discord.Interaction) -> bool:
    """Dozvoli upravljanje vlasniku bota ili server administratoru."""
    return bool(
        await bot.is_owner(interaction.user)
        or (
            interaction.guild
            and interaction.user.guild_permissions.administrator
        )
    )

# Pamti welcome poruke koje su već dobile jednu dobrodošlicu.
# Svaka welcome poruka može imati samo jedan uspješan klik.
WELCOME_GREETINGS = set()
WELCOME_GREETING_LOCK = asyncio.Lock()
PERSISTENT_VIEWS_REGISTERED = False

class WelcomeView(discord.ui.View):
    """Dugmad koja se prikazuju ispod welcome poruke."""

    def __init__(
        self,
        novi_clan_id: int,
        music_channel_id: int = None,
        guild_id: int = None,
        pozdrav_channel_id: int = None,
        greeting_id: str = None,
    ):
        super().__init__(timeout=None)
        self.novi_clan_id = novi_clan_id
        self.pozdrav_channel_id = pozdrav_channel_id
        self.guild_id = guild_id
        self.greeting_id = greeting_id or (
            f"{guild_id}:{novi_clan_id}:{uuid.uuid4().hex}"
        )

        guild = bot.get_guild(guild_id) if guild_id else None
        greet_emoji = component_custom_emoji(welcome_emoji(guild, "love"))
        for child in self.children:
            if isinstance(child, discord.ui.Button) and child.custom_id == "squad_welcome_greet":
                child.emoji = greet_emoji

        if music_channel_id and guild_id:
            self.add_item(discord.ui.Button(
                label="play music",
                emoji=component_custom_emoji(CUSTOM_EMOJI["music"]),
                style=discord.ButtonStyle.link,
                url=f"https://discord.com/channels/{guild_id}/{music_channel_id}",
            ))
        else:
            self.add_item(discord.ui.Button(
                label="play music",
                emoji=component_custom_emoji(CUSTOM_EMOJI["music"]),
                style=discord.ButtonStyle.secondary,
                disabled=True,
                custom_id="squad_welcome_music_disabled",
            ))

    @discord.ui.button(
        label="Poželi dobrodošlicu",
        emoji="❤️",
        style=discord.ButtonStyle.secondary,
        custom_id="squad_welcome_greet",
    )
    async def pozeli_dobrodoslicu(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button,
    ):
        if interaction.user.bot:
            await interaction.response.send_message(
                "Botovi ne mogu slati dobrodošlice.",
                ephemeral=bool(interaction.guild),
            )
            return

        message_id = interaction.message.id
        guild_id = self.guild_id or (
            interaction.guild.id if interaction.guild else None
        )
        greeting_key = self.greeting_id
        async with WELCOME_GREETING_LOCK:
            data = load_data()
            saved_greetings = data.setdefault("welcome_greetings", {})
            if (
                greeting_key in WELCOME_GREETINGS
                or greeting_key in saved_greetings
                or str(message_id) in saved_greetings
            ):
                await interaction.response.send_message(
                    f"{welcome_emoji(interaction.guild, 'love')} "
                    "Dobrodošlicu je već poslala druga osoba. "
                    "Ovo dugme može biti iskorišteno samo jednom.",
                    ephemeral=bool(interaction.guild),
                )
                return

            WELCOME_GREETINGS.add(greeting_key)
            saved_greetings[greeting_key] = {
                "message_id": message_id,
                "user_id": interaction.user.id,
                "guild_id": guild_id,
                "member_id": self.novi_clan_id,
                "timestamp": now_ts(),
            }
            save_data(data)
            await interaction.response.defer(
                ephemeral=bool(interaction.guild),
                thinking=True,
            )

            # Odmah ugasi dugme na originalnoj poruci.
            for child in self.children:
                if isinstance(child, discord.ui.Button) and child.custom_id == "squad_welcome_greet":
                    child.disabled = True
            try:
                await interaction.message.edit(view=self)
            except discord.HTTPException as exc:
                print(f"[WELCOME] Ne mogu ugasiti iskorišteno dugme: {exc}")

        guild = interaction.guild or (
            bot.get_guild(self.guild_id) if self.guild_id else None
        )
        target = guild.get_member(self.novi_clan_id) if guild else None
        target_mention = target.mention if target else f"<@{self.novi_clan_id}>"
        guild_name = guild.name if guild else "server"

        output_channel = None
        if guild:
            cfg = get_welcome(load_data(), guild.id)
            for channel_id in (self.pozdrav_channel_id, cfg.get("channel_id")):
                configured_channel = (
                    guild.get_channel(channel_id) if channel_id else None
                )
                if configured_channel and hasattr(configured_channel, "send"):
                    output_channel = configured_channel
                    break
        if output_channel is None and interaction.guild:
            output_channel = interaction.channel

        if output_channel is None:
            await interaction.edit_original_response(
                content=(
                    f"{CUSTOM_EMOJI['check']} Hvala! Klik je zabilježen, "
                    "ali welcome kanal nije dostupan za javnu objavu."
                )
            )
            return

        love = welcome_emoji(guild, "love")
        sparkles = welcome_emoji(guild, "sparkles")
        sharks = welcome_emoji(guild, "sharks")
        embed = discord.Embed(
            title=f"{sparkles} Dobrodošlica je poslata!",
            description=(
                f"> {love} {interaction.user.mention} je poslao/la "
                f"dobrodošlicu {target_mention} na **{guild_name}**!\n"
                f">\n"
                f"> {sharks} Prva osoba koja je kliknula dugme poželjela je dobrodošlicu "
                "novom članu."
            ),
            color=_LP,
        )
        embed.set_footer(text=f"{BOT_NAME} {VERSION} • dobrodošlica")
        try:
            # Jedan pokušaj sprečava duplu objavu nakon nejasne HTTP greške.
            await output_channel.send(embed=embed)
        except discord.HTTPException as exc:
            print(f"[WELCOME] Javni pozdrav nije poslan nakon klika: {exc}")
            await interaction.edit_original_response(
                content=(
                    f"{CUSTOM_EMOJI['close']} Klik je zabilježen, ali Discord "
                    "nije prihvatio javnu objavu. Provjeri dozvole welcome kanala."
                )
            )
            return
        await interaction.edit_original_response(
            content=(
                f"{CUSTOM_EMOJI['check']} Hvala! Tvoja dobrodošlica je uspješno "
                "poslana. Dugme je sada iskorišteno."
            )
        )

def build_welcome_embed(member, guild: discord.Guild, cfg: dict, test: bool = False):
    """Kompaktna welcome poruka za nove članove, test i pregled podešavanja."""
    def mention(channel_key: str, fallback: str) -> str:
        channel_id = cfg.get(channel_key)
        return f"<#{channel_id}>" if channel_id else fallback

    def emoji(key: str) -> str:
        return welcome_emoji(guild, key)

    pravila = mention("pravila_channel_id", "#pravila")
    chat = mention("chat_channel_id", "#chat")
    music = mention("music_channel_id", "nije podešen")
    embed = discord.Embed(
        title=(
            f"{emoji('sparkles')} "
            f"{'TEST • ' if test else ''}Dobrodošao/la na {guild.name}!"
        ),
        description=(
            f"{emoji('love')} {member.mention} — dobrodošao/la!\n"
            f"{emoji('fire')} Lijepo se smjesti, upoznaj ekipu i uživaj!\n"
            f"{emoji('crayon')} Klikni ispod da poželiš dobrodošlicu."
        ),
        color=_LP,
    )
    # Tri inline polja daju ravnomjeran raspored pravila, chata i muzike.
    embed.add_field(
        name=f"{emoji('ghost')} Pravila",
        value=f"Pročitaj pravila u {pravila}.",
        inline=True,
    )
    embed.add_field(
        name=f"{emoji('sharks')} Chat",
        value=f"Druži se sa članovima u {chat}.",
        inline=True,
    )
    embed.add_field(
        name=f"{emoji('mooncat')} Muzika",
        value=f"Pronađi muziku u {music}.",
        inline=True,
    )
    avatar = getattr(member, "display_avatar", None)
    if avatar:
        embed.set_thumbnail(url=avatar.url)
    return embed

async def remember_welcome_message(
    message: discord.Message,
    member_id: int,
    music_channel_id: int,
    guild_id: int,
    pozdrav_channel_id: int,
    greeting_id: str = None,
):
    """Sačuvaj i registruj personalizovano dugme da preživi restart."""
    greeting_id = greeting_id or f"legacy:{message.id}"
    record = {
        "member_id": member_id,
        "music_channel_id": music_channel_id,
        "guild_id": guild_id,
        "pozdrav_channel_id": pozdrav_channel_id,
        "greeting_id": greeting_id,
    }
    data = load_data()
    messages = data.setdefault("welcome_messages", {})
    messages[str(message.id)] = record
    # Ograniči indeks da stari serveri ne gomilaju neograničene ID-jeve.
    if len(messages) > 5000:
        for old_id in list(messages)[: len(messages) - 5000]:
            messages.pop(old_id, None)
    save_data(data)
    bot.add_view(
        WelcomeView(
            member_id,
            music_channel_id,
            guild_id,
            pozdrav_channel_id,
            greeting_id,
        ),
        message_id=message.id,
    )

def build_command_catalog_embeds():
    """Napravi čitljiv, ažuran spisak registrovanih prefix i slash komandi."""
    prefix_commands = sorted(
        {f".{command.name}" for command in bot.commands},
        key=str.casefold,
    )
    slash_commands = sorted(
        {f"/{command.name}" for command in bot.tree.get_commands()},
        key=str.casefold,
    )
    embeds = []
    page_size = 30
    pages = [
        prefix_commands[index:index + page_size]
        for index in range(0, len(prefix_commands), page_size)
    ]
    for index, page in enumerate(pages, start=1):
        embeds.append(discord.Embed(
            title=f"📚 Prefix komande ({index}/{len(pages)})",
            description=" · ".join(f"`{name}`" for name in page),
            color=_LP,
        ))
    embeds.append(discord.Embed(
        title="⚙️ Slash komande",
        description=(
            " · ".join(f"`{name}`" for name in slash_commands)
            + "\n\nNeke komande su dostupne samo vlasniku bota ili administratorima."
        ),
        color=_LP,
    ))
    for embed in embeds:
        embed.set_footer(text=f"{BOT_NAME} {VERSION} • prefix: .")
    return embeds

class InfoView(discord.ui.View):
    """Dugmad za detaljne informacije o serveru."""

    def __init__(self):
        super().__init__(timeout=None)
        button_emojis = {
            "squad_info_details": "info",
            "squad_info_all_commands": "book",
            "squad_info_gws_events": "gift",
        }
        for child in self.children:
            if isinstance(child, discord.ui.Button) and child.custom_id in button_emojis:
                child.emoji = component_custom_emoji(
                    CUSTOM_EMOJI[button_emojis[child.custom_id]]
                )

    @discord.ui.button(
        label="Info",
        emoji=CUSTOM_EMOJI["info"],
        style=discord.ButtonStyle.secondary,
        custom_id="squad_info_details",
    )
    async def info_details(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button,
    ):
        if interaction.guild is None:
            await interaction.response.send_message(
                "Ova opcija radi samo na serveru.", ephemeral=True
            )
            return

        data = load_data()
        cfg = get_info(data, interaction.guild.id)
        embed = discord.Embed(
            title=f"{CUSTOM_EMOJI['info']} Informacije — {interaction.guild.name}",
            description=(
                "> Dobrodošao/la na naš server! Ovdje možeš upoznati nove ljude, "
                "zabaviti se i učestvovati u raznim aktivnostima."
            ),
            color=_LP,
        )
        embed.add_field(
            name=f"{CUSTOM_EMOJI['shield']} Pravila servera",
            value=(
                "> • Poštuj sve članove i osoblje.\n"
                "> • Bez vrijeđanja, spama i nepotrebnog tagovanja.\n"
                "> • Bez reklama i nepoželjnog sadržaja.\n"
                "> • Koristi odgovarajuće kanale za odgovarajuće teme.\n"
                "> • Poštuj Discord pravila i odluke osoblja."
            ),
            inline=False,
        )
        embed.add_field(
            name=f"{CUSTOM_EMOJI['home']} O serveru",
            value=(
                f"> **{interaction.guild.name}** je zajednica za druženje, "
                "razgovor i zabavu."
            ),
            inline=False,
        )
        embed.add_field(
            name=f"{CUSTOM_EMOJI['game']} Kako da se zabaviš",
            value=(
                "> `.pomoc` — sve komande bota\n"
                "> `.veza @Korisnik` — ljubavni sistem\n"
                "> `.rad` i `.market` — virtuelna ekonomija\n"
                "> `.pecanje` — ribolov i skupljanje coina\n"
                "> `.topljubav`, `.topbogati` i `.top-ribar` — rang-liste\n"
                "> Prati razgovore, upoznaj ekipu i učestvuj u eventima!"
            ),
            inline=False,
        )
        embed.add_field(
            name=f"{CUSTOM_EMOJI['book']} Kaladont",
            value=(
                "> Pokreni `.kaladont`, pa šalji riječi naizmjenično s drugim članovima.\n"
                "> Uspješan odgovor prikazuje člana kao oznaku i riječ VELIKIM SLOVIMA.\n"
                "> Za cijeli spisak komandi klikni dugme **Opis • sve komande**."
            ),
            inline=False,
        )
        if cfg.get("events_channel_id"):
            embed.add_field(
                name=f"{CUSTOM_EMOJI['calendar']} Eventi",
                value=f"> Najave i detalji: <#{cfg['events_channel_id']}>",
                inline=False,
            )
        if interaction.guild.icon:
            embed.set_thumbnail(url=interaction.guild.icon.url)
        embed.set_footer(text=f"{BOT_NAME} {VERSION} • informacije")
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(
        label="Opis • sve komande",
        emoji=CUSTOM_EMOJI["book"],
        style=discord.ButtonStyle.secondary,
        custom_id="squad_info_all_commands",
    )
    async def all_commands(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button,
    ):
        embeds = build_command_catalog_embeds()
        await interaction.response.send_message(
            embeds=embeds,
            ephemeral=True,
            allowed_mentions=discord.AllowedMentions.none(),
        )

    @discord.ui.button(
        label="GWS & Events",
        emoji=CUSTOM_EMOJI["gift"],
        style=discord.ButtonStyle.secondary,
        custom_id="squad_info_gws_events",
    )
    async def gws_events(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button,
    ):
        if interaction.guild is None:
            await interaction.response.send_message(
                "Ova opcija radi samo na serveru.", ephemeral=True
            )
            return

        data = load_data()
        cfg = get_info(data, interaction.guild.id)
        gws = f"<#{cfg['gws_channel_id']}>" if cfg.get("gws_channel_id") else "nije podešen"
        events = f"<#{cfg['events_channel_id']}>" if cfg.get("events_channel_id") else "nije podešen"

        embed = discord.Embed(
            title=f"{CUSTOM_EMOJI['gift']} Giveaways & Events",
            description=(
                "> Ovdje možeš pratiti nagradne igre, server evente i posebne objave.\n"
                ">\n"
                "> Uključi obavještenja na kanalima kako ne bi propustio/la novu objavu."
            ),
            color=_LP,
        )
        embed.add_field(
            name=f"{CUSTOM_EMOJI['gift']} Giveaways",
            value=f"> Aktivni giveaway-i i nagrade: {gws}",
            inline=False,
        )
        embed.add_field(
            name=f"{CUSTOM_EMOJI['calendar']} Events",
            value=f"> Događaji i takmičenja: {events}",
            inline=False,
        )
        embed.add_field(
            name=f"{CUSTOM_EMOJI['info']} Kako učestvovati",
            value=(
                "> Pročitaj uslove u objavi, klikni traženu reakciju ili dugme "
                "i prati rok za prijavu."
            ),
            inline=False,
        )
        embed.set_footer(text=f"{BOT_NAME} {VERSION} • GWS & Events")
        await interaction.response.send_message(embed=embed, ephemeral=True)

class StaffApplicationModal(discord.ui.Modal, title="Staff prijava"):
    godine = discord.ui.TextInput(
        label="Koliko imaš godina?",
        placeholder="Npr. 18",
        max_length=3,
        required=True,
    )
    iskustvo = discord.ui.TextInput(
        label="Prethodno iskustvo",
        placeholder="Napiši ukratko gdje si ranije bio/bila staff.",
        style=discord.TextStyle.paragraph,
        max_length=800,
        required=True,
    )
    motivacija = discord.ui.TextInput(
        label="Zašto želiš biti staff?",
        placeholder="Šta bi donio/donijela našem serveru?",
        style=discord.TextStyle.paragraph,
        max_length=1000,
        required=True,
    )
    aktivnost = discord.ui.TextInput(
        label="Aktivnost i dostupnost",
        placeholder="Koliko često si online i kada si dostupan/dostupna?",
        style=discord.TextStyle.paragraph,
        max_length=800,
        required=True,
    )

    async def on_submit(self, interaction: discord.Interaction):
        if interaction.guild is None:
            await interaction.response.send_message(
                "Ova prijava se može poslati samo na serveru.", ephemeral=True
            )
            return

        data = load_data()
        cfg = get_support(data, interaction.guild.id)
        channel_id = cfg.get("staff_channel_id")
        staff_channel = interaction.guild.get_channel(channel_id) if channel_id else None
        if staff_channel is None or not hasattr(staff_channel, "send"):
            await interaction.response.send_message(
                "Staff prijave trenutno nisu podešene. Obrati se administratoru.",
                ephemeral=True,
            )
            return

        embed = discord.Embed(
            title=f"{CUSTOM_EMOJI['file']} Nova Staff prijava",
            description=(
                f"Prijava korisnika {interaction.user.mention}"
            ),
            color=_LP,
        )
        embed.add_field(
            name=f"{CUSTOM_EMOJI['calendar']} Godine",
            value=str(self.godine.value),
            inline=True,
        )
        embed.add_field(
            name=f"{CUSTOM_EMOJI['clock']} Aktivnost",
            value=str(self.aktivnost.value),
            inline=False,
        )
        embed.add_field(
            name=f"{CUSTOM_EMOJI['book']} Prethodno iskustvo",
            value=str(self.iskustvo.value),
            inline=False,
        )
        embed.add_field(
            name=f"{CUSTOM_EMOJI['info']} Motivacija",
            value=str(self.motivacija.value),
            inline=False,
        )
        embed.set_footer(text=f"{BOT_NAME} {VERSION} • Staff prijava")

        staff_role = interaction.guild.get_role(cfg.get("staff_role_id")) if cfg.get("staff_role_id") else None
        content = staff_role.mention if staff_role else None
        try:
            await staff_channel.send(content=content, embed=embed)
        except discord.Forbidden:
            await interaction.response.send_message(
                "Ne mogu poslati prijavu u staff kanal. Provjeri dozvole bota.",
                ephemeral=True,
            )
            return
        except discord.HTTPException:
            await interaction.response.send_message(
                "Prijava nije mogla biti poslata. Pokušaj ponovo.",
                ephemeral=True,
            )
            return

        await interaction.response.send_message(
            f"{CUSTOM_EMOJI['check']} Prijava je poslata staff timu. Hvala ti!",
            ephemeral=True,
        )

class StaffPanelView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Staff Apply",
        emoji=CUSTOM_EMOJI["file"],
        style=discord.ButtonStyle.danger,
        custom_id="squad_staff_apply",
    )
    async def staff_apply(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button,
    ):
        if interaction.user.bot:
            await interaction.response.send_message(
                "Botovi ne mogu slati prijave.", ephemeral=True
            )
            return
        await interaction.response.send_modal(StaffApplicationModal())

class TicketCloseView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Zatvori tiket",
        emoji=CUSTOM_EMOJI["lock"],
        style=discord.ButtonStyle.danger,
        custom_id="squad_ticket_close",
    )
    async def close_ticket(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button,
    ):
        if interaction.guild is None or interaction.channel is None:
            await interaction.response.send_message(
                "Ovaj tiket više nije dostupan.", ephemeral=True
            )
            return

        topic = getattr(interaction.channel, "topic", "") or ""
        owner_id = None
        if topic.startswith("squad-ticket:"):
            try:
                owner_id = int(topic.split(":", 1)[1])
            except (TypeError, ValueError):
                owner_id = None

        data = load_data()
        cfg = get_support(data, interaction.guild.id)
        staff_role = (
            interaction.guild.get_role(cfg.get("staff_role_id"))
            if cfg.get("staff_role_id")
            else None
        )
        is_staff = (
            interaction.user.guild_permissions.administrator
            or interaction.user.guild_permissions.manage_channels
            or (staff_role is not None and staff_role in getattr(interaction.user, "roles", []))
        )
        if owner_id != interaction.user.id and not is_staff:
            await interaction.response.send_message(
                "Samo vlasnik ticketa ili staff može zatvoriti ovaj tiket.",
                ephemeral=True,
            )
            return

        await interaction.response.send_message(
            f"{CUSTOM_EMOJI['lock']} Tiket se zatvara...", ephemeral=True
        )
        await asyncio.sleep(1)
        try:
            await interaction.channel.delete(reason="SQUAD ticket zatvoren")
        except discord.Forbidden:
            pass

class TicketPanelView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Otvori Tiket",
        emoji=CUSTOM_EMOJI["ticket"],
        style=discord.ButtonStyle.danger,
        custom_id="squad_ticket_open",
    )
    async def open_ticket(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button,
    ):
        if interaction.guild is None:
            await interaction.response.send_message(
                "Ticketi rade samo na serveru.", ephemeral=True
            )
            return

        existing = next(
            (
                channel
                for channel in interaction.guild.text_channels
                if (getattr(channel, "topic", "") or "") == f"squad-ticket:{interaction.user.id}"
            ),
            None,
        )
        if existing:
            await interaction.response.send_message(
                f"Već imaš otvoren tiket: {existing.mention}",
                ephemeral=True,
            )
            return

        await interaction.response.defer(ephemeral=True)
        data = load_data()
        cfg = get_support(data, interaction.guild.id)
        category = (
            interaction.guild.get_channel(cfg.get("ticket_category_id"))
            if cfg.get("ticket_category_id")
            else getattr(interaction.channel, "category", None)
        )
        staff_role = (
            interaction.guild.get_role(cfg.get("staff_role_id"))
            if cfg.get("staff_role_id")
            else None
        )
        safe_name = re.sub(
            r"[^a-z0-9-]+",
            "-",
            interaction.user.name.lower(),
        ).strip("-")[:20] or str(interaction.user.id)
        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(
                view_channel=False
            ),
            interaction.user: discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                read_message_history=True,
                attach_files=True,
            ),
        }
        if staff_role:
            overwrites[staff_role] = discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                read_message_history=True,
                manage_messages=True,
            )
        if interaction.guild.me:
            overwrites[interaction.guild.me] = discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                read_message_history=True,
                manage_channels=True,
                manage_messages=True,
            )

        try:
            ticket_channel = await interaction.guild.create_text_channel(
                name=f"ticket-{safe_name}",
                category=category if isinstance(category, discord.CategoryChannel) else None,
                overwrites=overwrites,
                topic=f"squad-ticket:{interaction.user.id}",
                reason="SQUAD ticket otvoren",
            )
        except discord.Forbidden:
            await interaction.edit_original_response(
                content="Ne mogu otvoriti tiket. Provjeri Manage Channels dozvolu bota."
            )
            return
        except discord.HTTPException:
            await interaction.edit_original_response(
                content="Ticket nije mogao biti otvoren. Pokušaj ponovo."
            )
            return

        embed = discord.Embed(
            title=f"{CUSTOM_EMOJI['ticket']} Otvoren tiket",
            description=(
                f"Dobrodošao/la {interaction.user.mention}.\n"
                "Napiši kako možemo pomoći i sačekaj odgovor staff tima."
            ),
            color=_LP,
        )
        embed.set_footer(text=f"{BOT_NAME} • Ticket Sistem")
        staff_mention = staff_role.mention if staff_role else None
        await ticket_channel.send(
            content=staff_mention,
            embed=embed,
            view=TicketCloseView(),
        )
        await interaction.edit_original_response(
            content=f"{CUSTOM_EMOJI['check']} Tvoj tiket je otvoren: {ticket_channel.mention}"
        )

class ReportCloseView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Zatvori report",
        emoji=CUSTOM_EMOJI["lock"],
        style=discord.ButtonStyle.danger,
        custom_id="squad_report_close",
    )
    async def close_report(self, interaction: discord.Interaction, button):
        if not interaction.guild or not interaction.channel:
            await interaction.response.send_message("Report više nije dostupan.", ephemeral=True)
            return
        topic = getattr(interaction.channel, "topic", "") or ""
        if not topic.startswith("squad-report:"):
            await interaction.response.send_message("Ovo nije report kanal.", ephemeral=True)
            return
        try:
            owner_id = int(topic.split(":", 1)[1])
        except (TypeError, ValueError):
            owner_id = None
        data = load_data()
        cfg = get_support(data, interaction.guild.id)
        role = interaction.guild.get_role(cfg.get("staff_role_id")) if cfg.get("staff_role_id") else None
        is_staff = (
            interaction.user.guild_permissions.administrator
            or interaction.user.guild_permissions.manage_channels
            or (role and role in getattr(interaction.user, "roles", []))
        )
        if interaction.user.id != owner_id and not is_staff:
            await interaction.response.send_message(
                "Samo autor reporta ili staff može zatvoriti report.", ephemeral=True
            )
            return
        await interaction.response.send_message(
            f"{CUSTOM_EMOJI['lock']} Report se zatvara...",
            ephemeral=True,
        )
        await asyncio.sleep(1)
        try:
            await interaction.channel.delete(reason="Report zatvoren")
        except discord.Forbidden:
            pass

class ReportPanelView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Prijavi korisnika",
        emoji=CUSTOM_EMOJI["alert"],
        style=discord.ButtonStyle.danger,
        custom_id="squad_report_open",
    )
    async def open_report(self, interaction: discord.Interaction, button):
        if not interaction.guild:
            await interaction.response.send_message("Report radi samo na serveru.", ephemeral=True)
            return
        existing = next(
            (
                ch for ch in interaction.guild.text_channels
                if (getattr(ch, "topic", "") or "") == f"squad-report:{interaction.user.id}"
            ),
            None,
        )
        if existing:
            await interaction.response.send_message(
                f"Već imaš otvoren report: {existing.mention}", ephemeral=True
            )
            return
        await interaction.response.defer(ephemeral=True)
        data = load_data()
        cfg = get_support(data, interaction.guild.id)
        category = (
            interaction.guild.get_channel(cfg.get("report_category_id"))
            if cfg.get("report_category_id") else getattr(interaction.channel, "category", None)
        )
        role = interaction.guild.get_role(cfg.get("staff_role_id")) if cfg.get("staff_role_id") else None
        safe_name = re.sub(r"[^a-z0-9-]+", "-", interaction.user.name.lower()).strip("-")[:20] or str(interaction.user.id)
        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(
                view_channel=True, send_messages=True, read_message_history=True, attach_files=True
            ),
        }
        if role:
            overwrites[role] = discord.PermissionOverwrite(
                view_channel=True, send_messages=True, read_message_history=True, manage_messages=True
            )
        if interaction.guild.me:
            overwrites[interaction.guild.me] = discord.PermissionOverwrite(
                view_channel=True, send_messages=True, read_message_history=True,
                manage_channels=True, manage_messages=True
            )
        try:
            report_channel = await interaction.guild.create_text_channel(
                name=f"report-{safe_name}",
                category=category if isinstance(category, discord.CategoryChannel) else None,
                overwrites=overwrites,
                topic=f"squad-report:{interaction.user.id}",
                reason="Report kanal otvoren",
            )
        except (discord.Forbidden, discord.HTTPException):
            await interaction.edit_original_response(
                content="Ne mogu otvoriti report. Provjeri Manage Channels dozvolu bota."
            )
            return
        embed = discord.Embed(
            title=f"{CUSTOM_EMOJI['alert']} Report je otvoren",
            description=(
                f"{interaction.user.mention}, ovdje napiši sve detalje prijave.\n"
                "Staff vidi ovaj kanal i može ga zatvoriti kada se slučaj riješi."
            ),
            color=_LP,
        )
        await report_channel.send(
            content=role.mention if role else None,
            embed=embed,
            view=ReportCloseView(),
        )
        await interaction.edit_original_response(
            content=f"{CUSTOM_EMOJI['check']} Tvoj report je otvoren: {report_channel.mention}"
        )

# ══════════════════════════════════════════════
#              EVENTS
# ══════════════════════════════════════════════
MONIKA_FUN_TERMS = {
    "smijeh", "smiješno", "smijesno", "šala", "sala", "fora", "vic",
    "zabava", "zabavno", "mem", "meme", "haha", "hahaha", "lol",
    "ljubav", "veza", "brak", "svađa", "svadja", "trač", "trac",
    "party", "žurka", "zurka", "igra", "casino", "film", "muzika",
}

MONIKA_REPLIES = (
    "Opet ste napravili sastanak bez dnevnog reda. Srećom, Monika je tu da uvede malo reda.",
    "Ovo je zabavna tema, a vi je obrađujete kao da pišete završni rad.",
    "Čekajte, da li se ovdje priča ozbiljno ili samo pokušavate da me impresionirate?",
    "Imam komentar, ali prvo da provjerim da li je neko ovdje dovoljno spreman za istinu.",
    "Dobro, ovo je već zanimljivo. Nastavite, upravo sam prestala da se pravim zauzeta.",
    "Vaša ekipa ima više zapleta nego dobra serija. Samo vam još nedostaje uvodna špica.",
    "Ne svađajte se oko toga ko je u pravu. Svi znamo da sam ja najbliže tome.",
    "Ovo zvuči kao odlična ideja. Zbog toga će vjerovatno neko za pet minuta napraviti haos.",
    "Monika se javlja iz prve klupe: nastavite, ovo je bolje od većine serija.",
    "Neko je upravo rekao nešto zanimljivo. Nemojte sada stati, tek sam se uključila.",
    "Ako već pravimo haos, barem ga napravimo sa stilom.",
    "Zapisujem sve. Ne pitajte zašto, samo nastavite razgovor.",
    "Ovo je trenutak kada bih trebala dati ozbiljan savjet, ali mi je zabavnije ovako.",
    "Imam pitanje za vas, ali prvo obećajte da nećete kriviti Moniku za odgovor.",
)
MONIKA_ROTATION_QUESTIONS = (
    "koja je tvoja omiljena pjesma ovih dana?",
    "šta bi prvo uradio/la da danas imaš potpuno slobodan dan?",
    "koji film ili seriju bi preporučio/la ekipi?",
    "koja je najčudnija stvar koja ti se skoro desila?",
    "da biraš jednu destinaciju za putovanje, gdje bi otišao/la?",
    "koji je tvoj skriveni talenat?",
    "šta ti je danas popravilo raspoloženje?",
    "koji bi supermoć izabrao/la na jedan dan?",
    "koja pjesma te uvijek vrati u dobro raspoloženje?",
    "šta bi ponio/la na pusto ostrvo?",
    "koji je najbolji kompliment koji si ikad dobio/la?",
    "da možeš upoznati bilo koju poznatu osobu, koga bi izabrao/la?",
    "koja je tvoja najjača osobina?",
    "šta najviše cijeniš kod prijatelja?",
    "koji je tvoj idealan vikend?",
    "koju bi igru mogao/la igrati satima?",
    "šta bi promijenio/la u svijetu kada bi mogao/la?",
)
# Riječi i tragovi za Monikin povremeni chat izazov.
MONIKA_WORD_CHALLENGES = (
    ("ljubav", "Osjećaj zbog kojeg je nastao cijeli ovaj bot."),
    ("more", "Mjesto gdje se spajaju nebo i voda."),
    ("muzika", "Nešto što možeš slušati i bez ekrana."),
    ("prijatelj", "Osoba koja ostaje uz tebe i kada nije lako."),
    ("putovanje", "Nešto što počinje pakovanjem kofera."),
    ("osmijeh", "Često se pojavi kada je neko sretan."),
    ("zvijezda", "Svijetli visoko iznad nas noću."),
    ("vikend", "Dva dana koja mnogi čekaju cijele sedmice."),
    ("pjesma", "Ima stihove, melodiju ili oboje."),
    ("avantura", "Uzbudljivo iskustvo koje se pamti."),
)
# Monika čita poruke samo u kanalu koji je admin podesio. Odgovori imaju
# cooldown, a stanje izazova i vrijeme posljednjeg odgovora se čuvaju u JSON-u.
MONIKA_COOLDOWN_SECONDS = 180
MONIKA_TAG_COOLDOWN_SECONDS = 30
MONIKA_LAST_REPLY = {}
MONIKA_GUESS_INTERVAL_SECONDS = 60 * 60
MONIKA_WORD_INTERVAL_SECONDS = 70 * 60
MONIKA_CHALLENGE_DURATION_SECONDS = 2 * 60
MONIKA_GUESS_TASK = None
POMOC_BATCH_MODE = False
GIVEAWAY_TASKS = {}
GIVEAWAY_DURATION_SECONDS = 24 * 60 * 60

def giveaway_embed(guild: discord.Guild, ends_at: int, ended: bool = False):
    embed = discord.Embed(
        title="🎁 NITRO GIVEAWAY",
        description=(
            "Osvoji **Nitro Boost na 1 mjesec**!\n\n"
            "**Uslovi za učestvovanje:**\n"
            "• Dovedi **2 osobe** na server\n"
            "• Stavi tag **mrak**\n"
            "• Klikni dugme **Učestvuj** ispod\n\n"
            "Giveaway uvijek traje **24 sata**."
        ),
        color=_LP,
    )
    embed.add_field(
        name="Nagrada",
        value="🚀 Nitro Boost — 1 mjesec",
        inline=False,
    )
    embed.add_field(
        name="Status",
        value="Završen" if ended else f"Završava <t:{ends_at}:R>",
        inline=False,
    )
    embed.set_footer(text=f"{guild.name} • 24h giveaway")
    return embed

class GiveawayView(discord.ui.View):
    def __init__(self, giveaway_id: str):
        super().__init__(timeout=None)
        self.giveaway_id = giveaway_id
        button = discord.ui.Button(
            label="Učestvuj",
            emoji=component_custom_emoji(CUSTOM_EMOJI["gift"]),
            style=discord.ButtonStyle.success,
            custom_id=f"squad_giveaway_join:{giveaway_id}",
        )
        button.callback = self.join
        self.add_item(button)

    async def join(self, interaction: discord.Interaction):
        if not interaction.guild:
            await interaction.response.send_message("Ovo radi samo na serveru.", ephemeral=True)
            return
        data = load_data()
        giveaway = data.setdefault("giveaways", {}).get(self.giveaway_id)
        if not giveaway or giveaway.get("ended"):
            await interaction.response.send_message("Ovaj giveaway je završen.", ephemeral=True)
            return
        if now_ts() >= int(giveaway.get("ends_at", 0)):
            await interaction.response.send_message("Ovaj giveaway je istekao.", ephemeral=True)
            return
        entries = giveaway.setdefault("entries", [])
        if interaction.user.id in entries:
            await interaction.response.send_message("Već učestvuješ u giveaway-u.", ephemeral=True)
            return
        entries.append(interaction.user.id)
        save_data(data)
        await interaction.response.send_message(
            "✅ Prijavljen/a si! Ne zaboravi da ispuniš oba uslova: 2 dovedene osobe i tag `mrak`.",
            ephemeral=True,
        )

async def finish_giveaway(giveaway_id: str):
    await bot.wait_until_ready()
    data = load_data()
    giveaway = data.setdefault("giveaways", {}).get(giveaway_id)
    if not giveaway or giveaway.get("ended"):
        return
    delay = max(0, int(giveaway.get("ends_at", 0)) - now_ts())
    await asyncio.sleep(delay)
    data = load_data()
    giveaway = data.setdefault("giveaways", {}).get(giveaway_id)
    if not giveaway or giveaway.get("ended"):
        return
    giveaway["ended"] = True
    winner_id = random.choice(giveaway.get("entries", [])) if giveaway.get("entries") else None
    giveaway["winner_id"] = winner_id
    save_data(data)
    channel = bot.get_channel(giveaway.get("channel_id"))
    if not channel:
        return
    message = await channel.fetch_message(giveaway.get("message_id"))
    await message.edit(embed=giveaway_embed(channel.guild, giveaway["ends_at"], ended=True), view=GiveawayView(giveaway_id))
    if winner_id:
        await channel.send(
            f"🎉 Čestitamo <@{winner_id}>! Osvojio/la si **Nitro Boost na 1 mjesec**.",
            allowed_mentions=discord.AllowedMentions(users=True),
        )
    else:
        await channel.send("Giveaway je završen, ali nije bilo prijavljenih učesnika.")

def monika_should_reply(message: discord.Message) -> bool:
    """Monika odgovara samo na tag ili na poruku sa zabavnom temom."""
    if not bot.user or not message.guild:
        return False
    if bot.user in message.mentions:
        return True
    text = message.content.lower()
    return any(term in text for term in MONIKA_FUN_TERMS)

def monika_next_member(guild: discord.Guild, cfg: dict):
    """Vrati sljedećeg člana po abecedi i pomjeri red u krug."""
    members = sorted(
        (member for member in guild.members if not member.bot),
        key=lambda member: (member.display_name.casefold(), member.id),
    )
    if not members:
        return None

    previous_id = cfg.get("last_member_id")
    next_position = 0
    if previous_id is not None:
        for index, member in enumerate(members):
            if member.id == previous_id:
                next_position = (index + 1) % len(members)
                break

    member = members[next_position]
    cfg["last_member_id"] = member.id
    return member

def monika_rotation_text(member: discord.Member) -> str:
    question = random.choice(MONIKA_ROTATION_QUESTIONS)
    return (
        f"{member.mention}, red je na tebi. "
        f"{question.capitalize()}"
    )

def monika_tag_text(member: discord.Member) -> str:
    replies = (
        "Tu sam, nemoj odmah da me taguješ kao da sam dežurna služba. "
        "Reci, šta se priča?",
        "Vidim te, stigla sam. Hajde, postavi pitanje — Monika sluša.",
        "Evo mene! Ako želiš razgovor, kreni slobodno. Samo bez dosadnih tema.",
        "Tagovana sam i sada nema bježanja. Šta ima kod tebe?",
        "Tu sam, {name}. Imaš moju punu pažnju — za sada.",
        "Monika online. Pričaj sa mnom, ali znaj da ću imati svoje mišljenje.",
    )
    return random.choice(replies).format(name=member.display_name)

def monika_guess_embed(title: str, lines, footer: str = None):
    embed = discord.Embed(title=title, description="\n".join(lines), color=_LP)
    if footer:
        embed.set_footer(text=footer)
    return embed

def monika_user_on_cooldown(cfg: dict, key: str, user_id: int, seconds: int) -> int:
    """Vrati preostale sekunde pokušaja i očisti stare unose."""
    now = now_ts()
    cooldowns = cfg.setdefault(key, {})
    cleaned = {}
    remaining = 0
    for uid, timestamp in cooldowns.items():
        try:
            age = now - int(timestamp)
        except (TypeError, ValueError):
            continue
        if age < seconds:
            cleaned[str(uid)] = int(timestamp)
    cfg[key] = cleaned
    timestamp = cleaned.get(str(user_id))
    if timestamp is not None:
        remaining = max(1, seconds - (now - timestamp))
    return remaining

def monika_word_embed(title: str, lines, footer: str = None):
    return monika_guess_embed(title, lines, footer)

async def monika_guess_loop():
    """Objavi broj svakih 60, a riječ svakih 70 minuta.

    Svaka runda je aktivna samo dvije minute. Interval se računa od
    objavljivanja prethodne runde, pa završena runda ne pokreće novu odmah.
    """
    await bot.wait_until_ready()
    while not bot.is_closed():
        data = load_data()
        changed = False
        current_time = now_ts()
        for guild in bot.guilds:
            cfg = get_monika(data, guild.id)
            channel_id = cfg.get("channel_id")
            if not channel_id:
                continue
            started_at = int(cfg.get("guess_started_at") or 0)
            if (
                cfg.get("guess_number") is not None
                and started_at
                and cfg.get("guess_winner_id") is None
                and current_time - started_at < MONIKA_CHALLENGE_DURATION_SECONDS
            ):
                number_active = True
            else:
                number_active = False
            channel = guild.get_channel(channel_id)
            if channel is None or not hasattr(channel, "send"):
                continue

            # Stari podaci nemaju next_at. Migracija ih čuva od ponovnog
            # objavljivanja izazova odmah nakon restarta.
            number_next_at = int(cfg.get("guess_next_at") or 0)
            if not number_next_at:
                number_next_at = (
                    started_at + MONIKA_GUESS_INTERVAL_SECONDS
                    if started_at else current_time
                )
                cfg["guess_next_at"] = number_next_at
                changed = True

            if (
                cfg.get("guess_number") is not None
                and cfg.get("guess_winner_id") is None
                and started_at
                and current_time - started_at >= MONIKA_CHALLENGE_DURATION_SECONDS
            ):
                cfg["guess_number"] = None
                cfg["guess_started_at"] = 0
                cfg["guess_winner_id"] = None
                cfg["guess_user_cooldowns"] = {}
                number_active = False
                changed = True
                await channel.send(embed=monika_guess_embed(
                    "Monika izazov — Runda završena",
                    ["> Vrijeme za pogađanje broja je isteklo."],
                    "Sljedeća runda za 60 minuta",
                ))

            if not number_active and current_time >= number_next_at:
                cfg["guess_number"] = random.randint(1, 100)
                cfg["guess_started_at"] = current_time
                cfg["guess_next_at"] = current_time + MONIKA_GUESS_INTERVAL_SECONDS
                cfg["guess_winner_id"] = None
                cfg["guess_user_cooldowns"] = {}
                changed = True
                await channel.send(embed=monika_guess_embed(
                    "Monika izazov — Pogodi broj",
                    [
                        "> Pogodi broj od **1 do 100**.",
                        "> Prvi član koji pogodi dobija **100 coin**.",
                        "> Svaki član može pokušati samo **jednom u ovoj rundi**.",
                        "> Runda traje **2 minute**.",
                        "> Odgovori samo brojem u ovom kanalu.",
                    ],
                    "Nagrada: 100 coin • Nova runda svakih 60 minuta",
                ))

            word_started_at = int(cfg.get("word_started_at") or 0)
            word_active = (
                cfg.get("word_answer") is not None
                and word_started_at
                and cfg.get("word_winner_id") is None
                and current_time - word_started_at < MONIKA_CHALLENGE_DURATION_SECONDS
            )
            word_next_at = int(cfg.get("word_next_at") or 0)
            if not word_next_at:
                word_next_at = (
                    word_started_at + MONIKA_WORD_INTERVAL_SECONDS
                    if word_started_at else current_time
                )
                cfg["word_next_at"] = word_next_at
                changed = True

            if (
                cfg.get("word_answer") is not None
                and cfg.get("word_winner_id") is None
                and word_started_at
                and current_time - word_started_at >= MONIKA_CHALLENGE_DURATION_SECONDS
            ):
                cfg["word_answer"] = None
                cfg["word_hint"] = None
                cfg["word_started_at"] = 0
                cfg["word_winner_id"] = None
                cfg["word_user_cooldowns"] = {}
                word_active = False
                changed = True
                await channel.send(embed=monika_word_embed(
                    "Monika izazov — Runda završena",
                    ["> Vrijeme za pogađanje riječi je isteklo."],
                    "Sljedeća runda za 70 minuta",
                ))

            if not word_active and current_time >= word_next_at:
                answer, hint = random.choice(MONIKA_WORD_CHALLENGES)
                cfg["word_answer"] = answer
                cfg["word_hint"] = hint
                cfg["word_started_at"] = current_time
                cfg["word_next_at"] = current_time + MONIKA_WORD_INTERVAL_SECONDS
                cfg["word_winner_id"] = None
                cfg["word_user_cooldowns"] = {}
                changed = True
                await channel.send(embed=monika_word_embed(
                    "Monika izazov — Pogodi riječ",
                    [
                        "> Pogodi skrivenu riječ.",
                        f"> Trag: **{hint}**",
                        "> Prvi član koji pogodi dobija **100 coin**.",
                        "> Svaki član može pokušati samo **jednom u ovoj rundi**.",
                        "> Runda traje **2 minute**.",
                        "> Pošalji samo jednu riječ u ovom kanalu.",
                    ],
                    "Nagrada: 100 coin • Nova runda svakih 70 minuta",
                ))
        if changed:
            save_data(data)
        await asyncio.sleep(60)

async def monika_handle_guess(message: discord.Message, data: dict, cfg: dict):
    """Obradi brojčani pokušaj u Monikinom kanalu."""
    if cfg.get("guess_number") is None or cfg.get("guess_winner_id") is not None:
        return False
    started_at = int(cfg.get("guess_started_at") or 0)
    if not started_at or now_ts() - started_at >= MONIKA_CHALLENGE_DURATION_SECONDS:
        # Loop će poslati poruku o isteku; poruka koja stigne na granici
        # runde ne smije biti prihvaćena dok loop ne očisti stanje.
        return True
    raw = message.content.strip()
    if not raw.isdigit():
        return False
    guess = int(raw)
    target = int(cfg["guess_number"])
    # Jedan pokušaj po članu i po rundi. Pogrešan pokušaj se pamti do kraja
    # runde; nema dodatnog cooldowna od dvije minute.
    if str(message.author.id) in cfg.setdefault("guess_user_cooldowns", {}):
        return True
    cfg.setdefault("guess_user_cooldowns", {})[str(message.author.id)] = now_ts()
    if guess < 1 or guess > 100:
        await message.channel.send(embed=monika_guess_embed(
            "Monika izazov",
            ["> Broj mora biti između **1 i 100**."],
            "Pokušaj ponovo",
        ))
        save_data(data)
        return True
    if guess != target:
        smjer = "veći" if guess < target else "manji"
        await message.channel.send(embed=monika_guess_embed(
            "Monika izazov",
            [f"> Nije taj broj. Probaj broj koji je **{smjer}**."],
            "Runda je još aktivna",
        ))
        save_data(data)
        return True

    cfg["guess_winner_id"] = message.author.id
    wallet = get_ekonomija(data, message.author.id)
    wallet["novac"] += 100
    save_data(data)
    await message.channel.send(
        embed=monika_guess_embed(
            "Monika čestita",
            [
                f"> {message.author.mention} je pogodio/la broj **{target}**!",
                "> Nagrada: **+100 coin**",
            ],
            "Čestitamo pobjedniku!",
        ),
        allowed_mentions=discord.AllowedMentions(
            users=[message.author],
            replied_user=False,
        ),
    )
    return True

async def monika_handle_word(message: discord.Message, data: dict, cfg: dict):
    """Obradi pogađanje riječi uz jedan pokušaj po članu i rundi."""
    answer = str(cfg.get("word_answer") or "").casefold()
    if not answer or cfg.get("word_winner_id") is not None:
        return False
    started_at = int(cfg.get("word_started_at") or 0)
    if not started_at or now_ts() - started_at >= MONIKA_CHALLENGE_DURATION_SECONDS:
        return True
    guess = re.sub(r"\s+", " ", message.content.strip().casefold())
    if not guess or not guess.isalpha():
        return False
    # Jedan pokušaj po članu i po rundi.
    if str(message.author.id) in cfg.setdefault("word_user_cooldowns", {}):
        return True
    cfg.setdefault("word_user_cooldowns", {})[str(message.author.id)] = now_ts()
    if guess != answer:
        save_data(data)
        # Namjerno nema odgovora na svaki pogrešan pokušaj, da igra ne
        # zatrpa kanal. Novi pokušaj je dozvoljen tek u novoj rundi.
        return True

    cfg["word_winner_id"] = message.author.id
    wallet = get_ekonomija(data, message.author.id)
    wallet["novac"] += 100
    save_data(data)
    await message.channel.send(
        embed=monika_word_embed(
            "Monika čestita",
            [
                f"> {message.author.mention} je pogodio/la riječ **{answer}**!",
                "> Nagrada: **+100 coin**",
            ],
            "Pobjednik je pronađen!",
        ),
        allowed_mentions=discord.AllowedMentions(
            users=[message.author],
            replied_user=False,
        ),
    )
    return True

@bot.event
async def on_message(message: discord.Message):
    """Ručno proslijedi poruke command handleru i Moniki."""
    if message.author.bot:
        return
    message_prefix = get_message_prefix(message.content)
    if message.guild and message_prefix:
        command_name = message.content[len(message_prefix):].split(maxsplit=1)[0].lower()
        ctx = await bot.get_context(message)
        if command_name == "pomoc":
            if not await check_pomoc_channel(ctx):
                return
        elif command_name not in {"setlogin", "setpomoc", "setreport"} and not await check_login_channel(message):
            return
    # Jedna Discord poruka smije proizvesti najviše jedan odgovor igre.
    if message.id in PROCESSED_GAME_MESSAGE_IDS:
        return
    PROCESSED_GAME_MESSAGE_IDS.add(message.id)
    if len(PROCESSED_GAME_MESSAGE_IDS) > 10000:
        PROCESSED_GAME_MESSAGE_IDS.clear()
    if is_prefix_command(message.content):
        print(f"[COMMAND] Primljena prefix komanda: {message.content.split()[0]}")
    else:
        # U posebnim kanalima članovi mogu slati samo broj ili riječ.
        # Komanda sa "." i dalje ide kroz standardni command handler.
        raw = message.content.strip()
        ctx = await bot.get_context(message)
        channel_id = message.channel.id
        configured_game_channels = {}
        if message.guild:
            configured_game_channels = get_kanali(load_data(), message.guild.id)
        if (
            configured_game_channels.get("toplo_hladno") == channel_id
        ):
            if raw.isdigit():
                await toplo_hladno.callback(ctx, int(raw))
            elif raw:
                await react_to_game_input(
                    message,
                    "Pošalji broj od 1 do 100 za igru Toplo-hladno.",
                )
            return
        if (
            configured_game_channels.get("counting") == channel_id
        ):
            if raw.isdigit():
                await counting.callback(ctx, int(raw))
            elif raw:
                await react_to_game_input(
                    message,
                    "Brojanje prima samo sljedeći broj.",
                )
            return
        if (
            configured_game_channels.get("kaladont") == channel_id
            and raw
        ):
            await kaladont.callback(ctx, raw)
            return
        if configured_game_channels.get("casino") == channel_id:
            parts = raw.split()
            if len(parts) == 2 and parts[0].lower() in {"coin", "slot"} and parts[1].isdigit():
                await casino.callback(ctx, parts[0], int(parts[1]))
                return
            if raw:
                await react_to_game_input(
                    message,
                    "Za casino koristi `coin 50` ili `slot 50`.",
                    "🎰",
                )
                return
        # Brojevi u Monikinom kanalu prvo pripadaju njenom izazovu.
        if message.guild:
            data = load_data()
            monika_cfg = get_monika(data, message.guild.id)
            if monika_cfg.get("channel_id") == channel_id:
                if await monika_handle_guess(message, data, monika_cfg):
                    return
                if await monika_handle_word(message, data, monika_cfg):
                    return
        # Monika radi samo u kanalu koji je administrator uključio.
        # Ne presreće prefix komande i ne odgovara na svaku običnu poruku.
        if not is_prefix_command(message.content):
            data = load_data()
            monika_cfg = get_monika(data, message.guild.id) if message.guild else {}
            if monika_cfg.get("channel_id") == message.channel.id and monika_should_reply(message):
                now = now_ts()
                is_tag = bot.user in message.mentions if bot.user else False
                cooldown = MONIKA_TAG_COOLDOWN_SECONDS if is_tag else MONIKA_COOLDOWN_SECONDS
                last_reply = max(
                    int(monika_cfg.get("last_reply_at") or 0),
                    MONIKA_LAST_REPLY.get(message.channel.id, 0),
                )
                if now - last_reply >= cooldown:
                    MONIKA_LAST_REPLY[message.channel.id] = now
                    monika_cfg["last_reply_at"] = now
                    save_data(data)
                    if is_tag:
                        # Kada je direktno tagovana, Monika odgovara baš toj
                        # osobi, umjesto da pitanje šalje sljedećem članu.
                        await message.channel.send(
                            monika_tag_text(message.author),
                            allowed_mentions=discord.AllowedMentions(
                                users=[message.author],
                                replied_user=False,
                            ),
                        )
                    else:
                        next_member = monika_next_member(message.guild, monika_cfg)
                        save_data(data)
                        if next_member:
                            await message.channel.send(
                                monika_rotation_text(next_member),
                                allowed_mentions=discord.AllowedMentions(
                                    users=[next_member],
                                    replied_user=False,
                                ),
                            )
                        else:
                            await message.channel.send(random.choice(MONIKA_REPLIES))
                    return
    await bot.process_commands(message)

@bot.event
async def on_ready():
    global PERSISTENT_VIEWS_REGISTERED, MONIKA_GUESS_TASK
    await load_application_emojis()
    synced_commands = await bot.tree.sync()
    print(
        f"[{BOT_NAME}] Registrovano slash komandi: {len(synced_commands)} "
        f"({', '.join(command.name for command in synced_commands)})"
    )
    if not PERSISTENT_VIEWS_REGISTERED:
        bot.add_view(InfoView())
        bot.add_view(StaffPanelView())
        bot.add_view(TicketPanelView())
        bot.add_view(TicketCloseView())
        bot.add_view(ReportPanelView())
        bot.add_view(ReportCloseView())
        for message_id, cfg in load_data().get("welcome_messages", {}).items():
            try:
                bot.add_view(
                    WelcomeView(
                        int(cfg["member_id"]),
                        cfg.get("music_channel_id"),
                        int(cfg["guild_id"]),
                        cfg.get("pozdrav_channel_id"),
                        cfg.get("greeting_id"),
                    ),
                    message_id=int(message_id),
                )
            except (KeyError, TypeError, ValueError, discord.ClientException) as exc:
                print(f"[WELCOME] Ne mogu obnoviti dugme na poruci {message_id}: {exc}")
        PERSISTENT_VIEWS_REGISTERED = True
    if MONIKA_GUESS_TASK is None or MONIKA_GUESS_TASK.done():
        MONIKA_GUESS_TASK = asyncio.create_task(monika_guess_loop())
    for giveaway_id, giveaway in load_data().get("giveaways", {}).items():
        if not giveaway.get("ended"):
            bot.add_view(GiveawayView(giveaway_id))
            task = GIVEAWAY_TASKS.get(giveaway_id)
            if task is None or task.done():
                GIVEAWAY_TASKS[giveaway_id] = asyncio.create_task(
                    finish_giveaway(giveaway_id)
                )
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name=f"{sum(g.member_count or 0 for g in bot.guilds):,} membera",
        )
    )
    print(f"[{BOT_NAME} {VERSION}] Prijavljen kao {bot.user} ({bot.user.id})")
    print(f"[{BOT_NAME} {VERSION}] Prefix: '{BOT_PREFIX}' | Svi sistemi aktivni!")
    print(f"[{BOT_NAME} {VERSION}] Registrovano prefix komandi: {len(bot.commands)}")
    print(
        f"[{BOT_NAME}] Server Members Intent u kodu: {bot.intents.members}. "
        "U Developer Portalu mora biti uključen i isti privileged intent."
    )

@bot.event
async def on_member_join(member: discord.Member):
    """Šalje welcome poruku u podešeni kanal i privatni inbox novog člana."""
    print(f"[WELCOME] Novi član {member.id} na serveru {member.guild.id}.")
    data = load_data()
    cfg = get_welcome(data, member.guild.id)
    channel_id = cfg.get("channel_id")
    welcome_enabled = cfg.get("enabled", bool(channel_id))
    if not welcome_enabled:
        print(f"[WELCOME] Welcome sistem je isključen za server {member.guild.id}.")
        return
    greeting_id = f"{member.guild.id}:{member.id}:{uuid.uuid4().hex}"

    channel = member.guild.get_channel(channel_id) if channel_id else None
    if channel is None and channel_id:
        try:
            channel = await bot.fetch_channel(channel_id)
        except discord.HTTPException as exc:
            print(f"[WELCOME] Kanal {channel_id} nije dostupan: {exc}")

    if isinstance(channel, discord.TextChannel) and channel.guild.id == member.guild.id:
        try:
            channel_view = WelcomeView(
                member.id,
                cfg.get("music_channel_id"),
                member.guild.id,
                cfg.get("pozdrav_channel_id"),
                greeting_id,
            )
            welcome_message = await channel.send(
                embed=build_welcome_embed(member, member.guild, cfg),
                view=channel_view,
                allowed_mentions=discord.AllowedMentions(
                    users=[member],
                    roles=False,
                    everyone=False,
                ),
            )
            await remember_welcome_message(
                welcome_message,
                member.id,
                cfg.get("music_channel_id"),
                member.guild.id,
                cfg.get("pozdrav_channel_id"),
                greeting_id,
            )
            print(f"[WELCOME] Poruka poslata u kanal {channel_id}.")
        except discord.Forbidden:
            print(
                f"[WELCOME] Bot nema Send Messages/Embed Links dozvolu "
                f"u kanalu {channel_id}."
            )
        except discord.HTTPException as exc:
            print(f"[WELCOME] Slanje u kanal {channel_id} nije uspjelo: {exc}")
    elif channel_id:
        print(
            f"[WELCOME] Kanal {channel_id} nije pronađen ili nije tekstualni "
            f"kanal servera {member.guild.id}."
        )
    else:
        print(f"[WELCOME] Nema podešenog welcome kanala za server {member.guild.id}.")

    if cfg.get("dm_enabled", True):
        try:
            dm_view = WelcomeView(
                member.id,
                cfg.get("music_channel_id"),
                member.guild.id,
                cfg.get("pozdrav_channel_id"),
                greeting_id,
            )
            dm_message = await member.send(
                embed=build_welcome_embed(member, member.guild, cfg),
                view=dm_view,
                allowed_mentions=discord.AllowedMentions(
                    users=[member],
                    roles=False,
                    everyone=False,
                ),
            )
            await remember_welcome_message(
                dm_message,
                member.id,
                cfg.get("music_channel_id"),
                member.guild.id,
                cfg.get("pozdrav_channel_id"),
                greeting_id,
            )
            print(f"[WELCOME] Privatna poruka poslata članu {member.id}.")
        except discord.Forbidden:
            print(
                f"[WELCOME] Discord je odbio DM članu {member.id}; "
                "privatne poruke su vjerovatno zatvorene."
            )
        except discord.HTTPException as exc:
            print(f"[WELCOME] Slanje privatne poruke članu {member.id} nije uspjelo: {exc}")
    else:
        print(f"[WELCOME] DM welcome je isključen za server {member.guild.id}.")

    role_id = cfg.get("role_id")
    if role_id:
        role = member.guild.get_role(role_id)
        if role:
            try:
                await member.add_roles(role, reason="SQUAD welcome automatska uloga")
                print(f"[WELCOME] Dodijeljena uloga {role_id} članu {member.id}.")
            except discord.Forbidden:
                print(f"[WELCOME] Bot nema Manage Roles ili je uloga {role_id} iznad bot-ove.")
            except discord.HTTPException as exc:
                print(f"[WELCOME] Dodjela uloge {role_id} nije uspjela: {exc}")
        else:
            print(f"[WELCOME] Podešena uloga {role_id} više ne postoji.")

@bot.event
async def on_command_error(ctx: commands.Context, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(embed=discord.Embed(
            description="> ❌ Nedostaje argument. Ukucaj `.pomoc` za pomoć.",
            color=_LP
        ))
    elif isinstance(error, commands.MemberNotFound):
        await ctx.send(embed=discord.Embed(
            description="> ❌ Korisnik nije pronađen.",
            color=_LP
        ))
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send(embed=discord.Embed(
            description=f"> {CUSTOM_EMOJI['close']} Nemaš dozvolu za ovu komandu!",
            color=_LP
        ))
    elif isinstance(error, commands.CommandNotFound):
        await ctx.send(embed=discord.Embed(
            description=(
                f"> {CUSTOM_EMOJI['info']} Komanda nije pronađena. "
                "Ukucaj `.pomoc` za listu komandi."
            ),
            color=_LP
        ))
    else:
        print(f"[ERROR] {error}")
        await ctx.send(embed=discord.Embed(
            description=(
                f"> {CUSTOM_EMOJI['info']} Komanda je primljena, ali je došlo "
                "do greške. Provjeri konzolu bota."
            ),
            color=_LP
        ))

# ══════════════════════════════════════════════
#   /setkanal — Admin
# ══════════════════════════════════════════════
@bot.tree.command(name="setkanal", description="[ADMIN] Postavi kanal za komande ili mini-igru")
@app_commands.describe(tip="Vrsta komandi ili igre", kanal="Kanal u kome će komanda ili igra biti dostupna")
@app_commands.choices(tip=[
    app_commands.Choice(name="Ljubav", value="ljubav"),
    app_commands.Choice(name="Pecanje", value="pecanje"),
    app_commands.Choice(name="Counting", value="counting"),
    app_commands.Choice(name="Toplo-hladno", value="toplo_hladno"),
    app_commands.Choice(name="Kaladont", value="kaladont"),
    app_commands.Choice(name="Casino", value="casino"),
])
@app_commands.default_permissions(administrator=True)
async def setkanal(interaction: discord.Interaction, tip: str, kanal: discord.TextChannel):
    data   = load_data()
    kanali = get_kanali(data, interaction.guild.id)
    kanali[tip] = kanal.id
    save_data(data)
    naziv_tip = {
        "ljubav": "Ljubavne komande",
        "pecanje": "Ribolov komande",
        "counting": "Counting igra",
        "toplo_hladno": "Toplo-hladno igra",
        "kaladont": "Kaladont igra",
        "casino": "Casino igra",
    }.get(tip, tip)
    await interaction.response.send_message(embed=discord.Embed(
        title="✅ Kanal podešen",
        description=f"> **{naziv_tip}** su sada dostupne samo u {kanal.mention}!",
        color=_LP
    ))

@bot.tree.command(name="setlogin", description="Vlasnik/admin: ograniči komande na jedan kanal")
@app_commands.describe(kanal="Kanal u kojem se mogu koristiti sve prefix i slash komande")
async def setlogin(interaction: discord.Interaction, kanal: discord.TextChannel):
    if not interaction.guild:
        await interaction.response.send_message("Ova komanda radi samo na serveru.", ephemeral=True)
        return
    if not await _is_bot_owner_or_admin(interaction):
        await interaction.response.send_message(
            "Samo vlasnik bota ili administrator servera može podesiti ovaj kanal.",
            ephemeral=True,
        )
        return
    data = load_data()
    get_kanali(data, interaction.guild.id)["login"] = kanal.id
    save_data(data)
    await interaction.response.send_message(embed=discord.Embed(
        title="Login kanal podešen",
        description=f"> Sve prefix i slash komande sada se koriste samo u {kanal.mention}.",
        color=_LP,
    ), ephemeral=True)

@bot.tree.command(name="setpomoc", description="Vlasnik/admin: postavi kanal za .pomoc")
@app_commands.describe(kanal="Kanal u kojem članovi smiju koristiti .pomoc")
async def setpomoc(interaction: discord.Interaction, kanal: discord.TextChannel):
    if not interaction.guild:
        await interaction.response.send_message("Ova komanda radi samo na serveru.", ephemeral=True)
        return
    if not await _is_bot_owner_or_admin(interaction):
        await interaction.response.send_message(
            "Samo vlasnik bota ili administrator servera može podesiti ovaj kanal.",
            ephemeral=True,
        )
        return
    data = load_data()
    get_kanali(data, interaction.guild.id)["pomoc"] = kanal.id
    save_data(data)
    await interaction.response.send_message(embed=discord.Embed(
        title="Kanal za pomoć podešen",
        description=f"> `.pomoc` je sada dostupna samo u {kanal.mention}.",
        color=_LP,
    ), ephemeral=True)

@bot.command(name="setpomoc")
async def setpomoc_prefix(ctx: commands.Context, kanal: discord.TextChannel = None):
    """Prefix verzija podešavanja kanala za .pomoc."""
    kanal = kanal or ctx.channel
    if not ctx.guild:
        await ctx.send("Ova komanda radi samo na serveru.", delete_after=8)
        return
    if not (
        await bot.is_owner(ctx.author)
        or ctx.author.guild_permissions.administrator
    ):
        await ctx.send("Samo vlasnik bota ili administrator servera može podesiti ovaj kanal.", delete_after=8)
        return
    data = load_data()
    get_kanali(data, ctx.guild.id)["pomoc"] = kanal.id
    save_data(data)
    await ctx.send(embed=discord.Embed(
        title="Kanal za pomoć podešen",
        description=f"> `.pomoc` je sada dostupna samo u {kanal.mention}.",
        color=_LP,
    ))

@bot.tree.command(name="ukloni-kanal", description="[ADMIN] Ukloni ograničenje kanala")
@app_commands.describe(tip="Vrsta komandi ili igre")
@app_commands.choices(tip=[
    app_commands.Choice(name="Ljubav", value="ljubav"),
    app_commands.Choice(name="Pecanje", value="pecanje"),
    app_commands.Choice(name="Counting", value="counting"),
    app_commands.Choice(name="Toplo-hladno", value="toplo_hladno"),
    app_commands.Choice(name="Kaladont", value="kaladont"),
    app_commands.Choice(name="Casino", value="casino"),
])
@app_commands.default_permissions(administrator=True)
async def ukloni_kanal(interaction: discord.Interaction, tip: str):
    data   = load_data()
    kanali = get_kanali(data, interaction.guild.id)
    kanali[tip] = None
    save_data(data)
    naziv_tip = {
        "ljubav": "Ljubavne komande",
        "pecanje": "Ribolov komande",
        "counting": "Counting igra",
        "toplo_hladno": "Toplo-hladno igra",
        "kaladont": "Kaladont igra",
        "casino": "Casino igra",
    }.get(tip, tip)
    await interaction.response.send_message(embed=discord.Embed(
        description=f"> ✅ Ograničenje za **{naziv_tip}** je uklonjeno. Komande su dostupne svuda.",
        color=_LP
    ))

# ══════════════════════════════════════════════
#   WELCOME SISTEM — Admin podešavanja
# ══════════════════════════════════════════════
@bot.tree.command(name="welcome-podesi", description="[ADMIN] Podesi welcome kanale i automatsku ulogu")
@app_commands.describe(
    kanal="Kanal u koji se šalje welcome poruka",
    pravila="Kanal sa pravilima (opcionalno)",
    chat="Glavni/chat kanal (opcionalno)",
    music="Kanal za music dugme (opcionalno)",
    pozdrav="Kanal za poruke nakon klika na Poželi dobrodošlicu (opcionalno)",
    uloga="Uloga koja se automatski dodjeljuje novom članu (opcionalno)",
    dm="Pokušaj poslati Welcome poruku novom članu u DM",
)
@app_commands.default_permissions(administrator=True)
async def welcome_podesi(
    interaction: discord.Interaction,
    kanal: discord.TextChannel,
    pravila: discord.TextChannel = None,
    chat: discord.TextChannel = None,
    music: discord.TextChannel = None,
    pozdrav: discord.TextChannel = None,
    uloga: discord.Role = None,
    dm: bool = True,
):
    if interaction.guild is None:
        await interaction.response.send_message(
            "Ova komanda se koristi samo na serveru.", ephemeral=True
        )
        return
    bot_member = interaction.guild.me
    if bot_member is None:
        await interaction.response.send_message(
            "Ne mogu provjeriti dozvole bota na ovom serveru.", ephemeral=True
        )
        return
    channel_permissions = kanal.permissions_for(bot_member)
    if not channel_permissions.send_messages or not channel_permissions.embed_links:
        await interaction.response.send_message(
            f"Bot nema dozvolu **Send Messages** i/ili **Embed Links** u {kanal.mention}. "
            "Podešavanje nije sačuvano.",
            ephemeral=True,
        )
        return

    data = load_data()
    cfg = get_welcome(data, interaction.guild.id)
    cfg["enabled"] = True
    cfg["dm_enabled"] = dm
    cfg["channel_id"] = kanal.id
    cfg["pravila_channel_id"] = pravila.id if pravila else None
    cfg["chat_channel_id"] = chat.id if chat else None
    cfg["music_channel_id"] = music.id if music else None
    cfg["pozdrav_channel_id"] = pozdrav.id if pozdrav else None
    cfg["role_id"] = uloga.id if uloga else None
    save_data(data)

    pravila_txt = pravila.mention if pravila else "nije podešen"
    chat_txt = chat.mention if chat else "nije podešen"
    music_txt = music.mention if music else "nije podešen"
    pozdrav_txt = pozdrav.mention if pozdrav else "welcome kanal"
    role_txt = uloga.mention if uloga else "nije podešena"

    e = lambda key: welcome_emoji(interaction.guild, key)
    embed = discord.Embed(
        title=f"{e('sparkles')} Welcome podešavanja sačuvana",
        color=_LP,
    )
    embed.description = (
        f"> {e('love')} **Welcome kanal:** {kanal.mention}\n"
        f"> {e('ghost')} **Pravila:** {pravila_txt}\n"
        f"> {e('sharks')} **Chat:** {chat_txt}\n"
        f"> {e('mooncat')} **Music:** {music_txt}\n"
        f"> {e('crayon')} **Poruka dobrodošlice:** {pozdrav_txt}\n"
        f"> {e('fire')} **Automatska uloga:** {role_txt}\n"
        f"> {e('mail')} **Welcome u DM:** {'uključen' if dm else 'isključen'}\n"
        f">\n"
        f"> {e('sparkles')} Podešavanja su sačuvana za ovaj server."
    )
    await interaction.response.defer(ephemeral=True, thinking=True)
    preview_greeting_id = (
        f"preview:{interaction.guild.id}:{interaction.user.id}:{uuid.uuid4().hex}"
    )
    welcome_view = WelcomeView(
        interaction.user.id,
        cfg.get("music_channel_id"),
        interaction.guild.id,
        cfg.get("pozdrav_channel_id"),
        preview_greeting_id,
    )
    try:
        preview_message = await kanal.send(
            content="🧪 Test welcome poruka nakon podešavanja",
            embed=build_welcome_embed(interaction.user, interaction.guild, cfg, test=True),
            view=welcome_view,
            allowed_mentions=discord.AllowedMentions.none(),
        )
        await remember_welcome_message(
            preview_message,
            interaction.user.id,
            cfg.get("music_channel_id"),
            interaction.guild.id,
            cfg.get("pozdrav_channel_id"),
            preview_greeting_id,
        )
    except discord.Forbidden:
        await interaction.edit_original_response(
            content=(
                f"Podešavanja su sačuvana, ali bot ne može poslati test u {kanal.mention}. "
                "Provjeri Send Messages i Embed Links."
            )
        )
        return
    except discord.HTTPException as exc:
        await interaction.edit_original_response(
            content=f"Podešavanja su sačuvana, ali test poruka nije poslata: {exc}"
        )
        return
    await interaction.edit_original_response(
        content=(
            f"✅ Welcome je podešen za {kanal.mention} i test poruka je poslata. "
            f"Pri ulasku novog člana bot će pokušati poslati welcome "
            f"{'u server kanal i DM' if dm else 'u server kanal'}."
        )
    )

@bot.tree.command(name="welcome-status", description="[ADMIN] Prikaži trenutna welcome podešavanja")
@app_commands.default_permissions(administrator=True)
async def welcome_status(interaction: discord.Interaction):
    if interaction.guild is None:
        await interaction.response.send_message(
            "Ova komanda se koristi samo na serveru.", ephemeral=True
        )
        return

    data = load_data()
    cfg = get_welcome(data, interaction.guild.id)

    def mention(channel_id):
        return f"<#{channel_id}>" if channel_id else "nije podešen"

    role = interaction.guild.get_role(cfg.get("role_id")) if cfg.get("role_id") else None
    e = lambda key: welcome_emoji(interaction.guild, key)
    embed = discord.Embed(title=f"{e('sparkles')} Welcome status", color=_LP)
    embed.description = (
        f"> {e('love')} **Welcome kanal:** {mention(cfg.get('channel_id'))}\n"
        f"> {e('sparkles')} **Automatski welcome:** "
        f"{'uključen' if cfg.get('enabled', bool(cfg.get('channel_id'))) else 'isključen'}\n"
        f"> {e('mail')} **Welcome u DM:** "
        f"{'uključen' if cfg.get('dm_enabled', True) else 'isključen'}\n"
        f"> {e('ghost')} **Pravila:** {mention(cfg.get('pravila_channel_id'))}\n"
        f"> {e('sharks')} **Chat:** {mention(cfg.get('chat_channel_id'))}\n"
        f"> {e('mooncat')} **Music:** {mention(cfg.get('music_channel_id'))}\n"
        f"> {e('crayon')} **Poruka dobrodošlice:** {mention(cfg.get('pozdrav_channel_id'))}\n"
        f"> {e('fire')} **Automatska uloga:** {role.mention if role else 'nije podešena'}"
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="welcome-test", description="[ADMIN] Pošalji test welcome poruku")
@app_commands.default_permissions(administrator=True)
async def welcome_test(interaction: discord.Interaction):
    if interaction.guild is None:
        await interaction.response.send_message(
            "Ova komanda se koristi samo na serveru.", ephemeral=True
        )
        return

    data = load_data()
    cfg = get_welcome(data, interaction.guild.id)
    channel_id = cfg.get("channel_id")
    channel = interaction.guild.get_channel(channel_id) if channel_id else None
    if channel is None and channel_id:
        try:
            channel = await bot.fetch_channel(channel_id)
        except discord.HTTPException:
            channel = None
    if not isinstance(channel, discord.TextChannel) or channel.guild.id != interaction.guild.id:
        await interaction.response.send_message(
            "Welcome kanal nije podešen ili više ne postoji. Pokreni `/welcome-podesi`.",
            ephemeral=True,
        )
        return
    bot_member = interaction.guild.me
    if not bot_member:
        await interaction.response.send_message(
            "Ne mogu provjeriti dozvole bota na serveru.", ephemeral=True
        )
        return
    permissions = channel.permissions_for(bot_member)
    if not permissions.send_messages or not permissions.embed_links:
        await interaction.response.send_message(
            f"Bot nema Send Messages i/ili Embed Links dozvolu u {channel.mention}.",
            ephemeral=True,
        )
        return

    await interaction.response.defer(ephemeral=True, thinking=True)
    preview_greeting_id = (
        f"preview:{interaction.guild.id}:{interaction.user.id}:{uuid.uuid4().hex}"
    )
    view = WelcomeView(
        interaction.user.id,
        cfg.get("music_channel_id"),
        interaction.guild.id,
        cfg.get("pozdrav_channel_id"),
        preview_greeting_id,
    )
    try:
        preview_message = await channel.send(
            content="🧪 Test welcome poruka",
            embed=build_welcome_embed(interaction.user, interaction.guild, cfg, test=True),
            view=view,
            allowed_mentions=discord.AllowedMentions.none(),
        )
        await remember_welcome_message(
            preview_message,
            interaction.user.id,
            cfg.get("music_channel_id"),
            interaction.guild.id,
            cfg.get("pozdrav_channel_id"),
            preview_greeting_id,
        )
    except discord.Forbidden:
        await interaction.edit_original_response(
            content=f"Discord je odbio slanje u {channel.mention}. Provjeri dozvole kanala."
        )
        return
    except discord.HTTPException as exc:
        await interaction.edit_original_response(content=f"Test welcome nije poslan: {exc}")
        return
    await interaction.edit_original_response(
        content=f"✅ Test welcome poruka je poslata u {channel.mention}."
    )

@bot.tree.command(name="welcome-iskljuci", description="[ADMIN] Isključi automatske welcome poruke")
@app_commands.default_permissions(administrator=True)
async def welcome_iskljuci(interaction: discord.Interaction):
    if interaction.guild is None:
        await interaction.response.send_message(
            "Ova komanda se koristi samo na serveru.", ephemeral=True
        )
        return

    data = load_data()
    cfg = get_welcome(data, interaction.guild.id)
    cfg["channel_id"] = None
    cfg["enabled"] = False
    cfg["dm_enabled"] = False
    save_data(data)
    await interaction.response.send_message(
        "✅ Automatske welcome poruke u server kanalu i DM-u su isključene. "
        "Podešavanja ostalih kanala su sačuvana.",
        ephemeral=True,
    )

# ══════════════════════════════════════════════
#   INFO PANEL — Admin podešavanja
# ══════════════════════════════════════════════
@bot.tree.command(name="info-podesi", description="[ADMIN] Podesi kanal za Info i GWS & Events panel")
@app_commands.describe(
    kanal="Kanal u koji se šalje mali informativni embed",
    gws="Kanal za giveawaye (opcionalno)",
    events="Kanal za evente (opcionalno)",
)
@app_commands.default_permissions(administrator=True)
async def info_podesi(
    interaction: discord.Interaction,
    kanal: discord.TextChannel,
    gws: discord.TextChannel = None,
    events: discord.TextChannel = None,
):
    if interaction.guild is None:
        await interaction.response.send_message(
            "Ova komanda se koristi samo na serveru.", ephemeral=True
        )
        return

    data = load_data()
    cfg = get_info(data, interaction.guild.id)
    cfg["channel_id"] = kanal.id
    cfg["gws_channel_id"] = gws.id if gws else None
    cfg["events_channel_id"] = events.id if events else None
    save_data(data)

    embed = discord.Embed(title="✅ Info panel podešen", color=_LP)
    embed.description = (
        f"> **Info kanal:** {kanal.mention}\n"
        f"> **Giveaways:** {gws.mention if gws else 'nije podešen'}\n"
        f"> **Events:** {events.mention if events else 'nije podešen'}\n"
        ">\n"
        "> ID-evi su sačuvani po serveru."
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="info-postavi", description="[ADMIN] Pošalji mali Info panel u podešeni kanal")
@app_commands.default_permissions(administrator=True)
async def info_postavi(interaction: discord.Interaction):
    if interaction.guild is None:
        await interaction.response.send_message(
            "Ova komanda se koristi samo na serveru.", ephemeral=True
        )
        return

    data = load_data()
    cfg = get_info(data, interaction.guild.id)
    channel_id = cfg.get("channel_id")
    channel = interaction.guild.get_channel(channel_id) if channel_id else None
    if channel is None or not hasattr(channel, "send"):
        await interaction.response.send_message(
            "Prvo podesi kanal komandom `/info-podesi`.", ephemeral=True
        )
        return

    embed = discord.Embed(
        title=f"{CUSTOM_EMOJI['heart']} {interaction.guild.name} — informacije",
        description=(
            "> Klikni **Info** za pravila, **Opis • sve komande** za spisak komandi "
            "ili **GWS & Events** za giveawaye i evente.\n"
            "> Isprobaj i mini-igru `.kaladont`."
        ),
        color=_LP,
    )
    if interaction.guild.icon:
        embed.set_thumbnail(url=interaction.guild.icon.url)
    embed.set_footer(text=f"{BOT_NAME} {VERSION} • klikni za više informacija")

    await interaction.response.defer(ephemeral=True, thinking=True)
    try:
        _message, updated = await upsert_panel_message(
            channel,
            interaction.guild.id,
            "info",
            "squad_info_details",
            embed,
            InfoView(),
        )
    except discord.Forbidden:
        await interaction.edit_original_response(
            content=(
                "Ne mogu provjeriti ili ažurirati Info panel. Botu su potrebne "
                "dozvole View Channel, Read Message History i Send Messages."
            )
        )
        return
    except discord.HTTPException:
        await interaction.edit_original_response(
            content=(
                "Discord nije potvrdio slanje/ažuriranje Info panela. "
                "Nisam ponovio slanje da ne bih napravio duplikat."
            )
        )
        return
    status = "ažuriran" if updated else "postavljen"
    await interaction.edit_original_response(
        content=f"Info panel je {status} u {channel.mention}."
    )

@bot.tree.command(name="info-status", description="[ADMIN] Prikaži Info panel podešavanja")
@app_commands.default_permissions(administrator=True)
async def info_status(interaction: discord.Interaction):
    if interaction.guild is None:
        await interaction.response.send_message(
            "Ova komanda se koristi samo na serveru.", ephemeral=True
        )
        return

    data = load_data()
    cfg = get_info(data, interaction.guild.id)

    def mention(channel_id):
        return f"<#{channel_id}>" if channel_id else "nije podešen"

    embed = discord.Embed(title="⚙️ Info panel status", color=_LP)
    embed.description = (
        f"> **Info kanal:** {mention(cfg.get('channel_id'))}\n"
        f"> **Giveaways:** {mention(cfg.get('gws_channel_id'))}\n"
        f"> **Events:** {mention(cfg.get('events_channel_id'))}"
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)

# ══════════════════════════════════════════════
#   STAFF PRIJAVE I TICKET SISTEM
# ══════════════════════════════════════════════
@bot.tree.command(name="staff-podesi", description="[ADMIN] Podesi kanal i ulogu za Staff prijave")
@app_commands.describe(
    kanal="Kanal u koji stižu Staff prijave",
    uloga="Staff uloga koja dobija obavijest (opcionalno)",
)
@app_commands.default_permissions(administrator=True)
async def staff_podesi(
    interaction: discord.Interaction,
    kanal: discord.TextChannel,
    uloga: discord.Role = None,
):
    if interaction.guild is None:
        await interaction.response.send_message(
            "Ova komanda se koristi samo na serveru.", ephemeral=True
        )
        return

    data = load_data()
    cfg = get_support(data, interaction.guild.id)
    cfg["staff_channel_id"] = kanal.id
    cfg["staff_role_id"] = uloga.id if uloga else None
    save_data(data)

    embed = discord.Embed(
        title="✅ Staff sistem podešen",
        description=(
            f"**Kanal prijava:** {kanal.mention}\n"
            f"**Staff uloga:** {uloga.mention if uloga else 'nije podešena'}"
        ),
        color=_LP,
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="staff-postavi", description="[ADMIN] Postavi Staff Prijava panel")
@app_commands.describe(kanal="Kanal za panel (opcionalno, podrazumijeva trenutni kanal)")
@app_commands.default_permissions(administrator=True)
async def staff_postavi(
    interaction: discord.Interaction,
    kanal: discord.TextChannel = None,
):
    if interaction.guild is None:
        await interaction.response.send_message(
            "Ova komanda se koristi samo na serveru.", ephemeral=True
        )
        return

    target = kanal or interaction.channel
    if not isinstance(target, discord.TextChannel):
        await interaction.response.send_message(
            "Izaberi tekstualni kanal za Staff panel.", ephemeral=True
        )
        return

    embed = discord.Embed(
        title=f"{CUSTOM_EMOJI['file']} STAFF PRIJAVA",
        description=(
            "Otvorene su prijave za Staff tim servera!\n"
            f"{CUSTOM_EMOJI['hand']} Klikni dugme ispod i popuni svoje podatke.\n"
            f"{CUSTOM_EMOJI['lock']} Odgovori su privatni dok ne pošalješ prijavu."
        ),
        color=_LP,
    )
    embed.set_footer(text=f"{BOT_NAME} • Staff Prijava")
    await interaction.response.defer(ephemeral=True, thinking=True)
    try:
        _message, updated = await upsert_panel_message(
            target,
            interaction.guild.id,
            "staff",
            "squad_staff_apply",
            embed,
            StaffPanelView(),
        )
    except discord.Forbidden:
        await interaction.edit_original_response(
            content=(
                "Ne mogu provjeriti ili ažurirati Staff panel. Botu su potrebne "
                "dozvole View Channel, Read Message History i Send Messages."
            )
        )
        return
    except discord.HTTPException:
        await interaction.edit_original_response(
            content=(
                "Discord nije potvrdio slanje/ažuriranje Staff panela. "
                "Nisam ponovio slanje da ne bih napravio duplikat."
            )
        )
        return

    status = "ažuriran" if updated else "postavljen"
    await interaction.edit_original_response(
        content=f"{CUSTOM_EMOJI['check']} Staff panel je {status} u {target.mention}."
    )

@bot.tree.command(name="ticket-podesi", description="[ADMIN] Podesi kategoriju i ulogu za tickete")
@app_commands.describe(
    kategorija="Kategorija u kojoj će se otvarati privatni ticketi (opcionalno)",
    uloga="Staff uloga koja vidi tickete (opcionalno)",
)
@app_commands.default_permissions(administrator=True)
async def ticket_podesi(
    interaction: discord.Interaction,
    kategorija: discord.CategoryChannel = None,
    uloga: discord.Role = None,
):
    if interaction.guild is None:
        await interaction.response.send_message(
            "Ova komanda se koristi samo na serveru.", ephemeral=True
        )
        return

    data = load_data()
    cfg = get_support(data, interaction.guild.id)
    cfg["ticket_category_id"] = kategorija.id if kategorija else None
    cfg["staff_role_id"] = uloga.id if uloga else cfg.get("staff_role_id")
    save_data(data)

    embed = discord.Embed(
        title="✅ Ticket sistem podešen",
        description=(
            f"**Kategorija:** {kategorija.name if kategorija else 'trenutna kategorija'}\n"
            f"**Staff uloga:** {uloga.mention if uloga else 'postojeća/podešena uloga'}"
        ),
        color=_LP,
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="ticket-postavi", description="[ADMIN] Postavi panel za otvaranje ticketa")
@app_commands.describe(kanal="Kanal za panel (opcionalno, podrazumijeva trenutni kanal)")
@app_commands.default_permissions(administrator=True)
async def ticket_postavi(
    interaction: discord.Interaction,
    kanal: discord.TextChannel = None,
):
    if interaction.guild is None:
        await interaction.response.send_message(
            "Ova komanda se koristi samo na serveru.", ephemeral=True
        )
        return

    target = kanal or interaction.channel
    if not isinstance(target, discord.TextChannel):
        await interaction.response.send_message(
            "Izaberi tekstualni kanal za Ticket panel.", ephemeral=True
        )
        return

    data = load_data()
    cfg = get_support(data, interaction.guild.id)
    cfg["ticket_panel_channel_id"] = target.id
    save_data(data)

    embed = discord.Embed(
        title=f"{CUSTOM_EMOJI['ticket']} Otvori Tiket",
        description=(
            "Treba ti pomoć? Otvori tiket!\n"
            f"{CUSTOM_EMOJI['mail']} Privatni kanal vide samo ti i staff.\n"
            f"{CUSTOM_EMOJI['file']} Opiši problem i sačekaj odgovor tima."
        ),
        color=_LP,
    )
    embed.set_footer(text=f"{BOT_NAME} • Ticket Sistem")
    await interaction.response.defer(ephemeral=True, thinking=True)
    try:
        _message, updated = await upsert_panel_message(
            target,
            interaction.guild.id,
            "ticket",
            "squad_ticket_open",
            embed,
            TicketPanelView(),
        )
    except discord.Forbidden:
        await interaction.edit_original_response(
            content=(
                "Ne mogu provjeriti ili ažurirati Ticket panel. Botu su potrebne "
                "dozvole View Channel, Read Message History i Send Messages."
            )
        )
        return
    except discord.HTTPException:
        await interaction.edit_original_response(
            content=(
                "Discord nije potvrdio slanje/ažuriranje Ticket panela. "
                "Nisam ponovio slanje da ne bih napravio duplikat."
            )
        )
        return

    status = "ažuriran" if updated else "postavljen"
    await interaction.edit_original_response(
        content=f"{CUSTOM_EMOJI['check']} Ticket panel je {status} u {target.mention}."
    )

@bot.tree.command(name="embed", description="[ADMIN] Pošalji svoj tekst kao embed")
@app_commands.describe(
    tekst="Tekst koji će biti prikazan u embedu",
    naslov="Naslov embeda (opcionalno)",
    kanal="Kanal za slanje (opcionalno, podrazumijeva trenutni kanal)",
)
@app_commands.default_permissions(administrator=True)
async def posalji_embed(
    interaction: discord.Interaction,
    tekst: str,
    naslov: str = None,
    kanal: discord.TextChannel = None,
):
    if interaction.guild is None:
        await interaction.response.send_message(
            "Ova komanda se koristi samo na serveru.", ephemeral=True
        )
        return

    if not tekst.strip() or len(tekst) > 4096:
        await interaction.response.send_message(
            "Unesi tekst do 4096 znakova.", ephemeral=True
        )
        return
    if naslov and len(naslov) > 256:
        await interaction.response.send_message(
            "Naslov može imati najviše 256 znakova.", ephemeral=True
        )
        return

    target = kanal or interaction.channel
    if not isinstance(target, discord.TextChannel):
        await interaction.response.send_message(
            "Izaberi tekstualni kanal za embed.", ephemeral=True
        )
        return

    embed = discord.Embed(
        title=naslov or None,
        description=tekst,
        color=_LP,
    )
    try:
        await target.send(
            embed=embed,
            allowed_mentions=discord.AllowedMentions.none(),
        )
    except discord.Forbidden:
        await interaction.response.send_message(
            "Ne mogu poslati embed u taj kanal. Provjeri dozvole bota.",
            ephemeral=True,
        )
        return
    except discord.HTTPException:
        await interaction.response.send_message(
            "Discord nije prihvatio embed. Provjeri dužinu teksta i probaj ponovo.",
            ephemeral=True,
        )
        return

    await interaction.response.send_message(
        f"✅ Embed je poslat u {target.mention}.", ephemeral=True
    )

@bot.tree.command(name="setreport", description="Vlasnik/admin: podesi privatni report panel")
@app_commands.describe(
    kanal="Kanal u koji se šalje report panel",
    kategorija="Kategorija za privatne report kanale (opcionalno)",
    uloga="Staff uloga koja vidi report kanale (opcionalno)",
)
async def setreport(
    interaction: discord.Interaction,
    kanal: discord.TextChannel,
    kategorija: discord.CategoryChannel = None,
    uloga: discord.Role = None,
):
    if not interaction.guild:
        await interaction.response.send_message("Ova komanda radi samo na serveru.", ephemeral=True)
        return
    if not await _is_bot_owner_or_admin(interaction):
        await interaction.response.send_message(
            "Samo vlasnik bota ili administrator servera može podesiti report sistem.",
            ephemeral=True,
        )
        return
    data = load_data()
    cfg = get_support(data, interaction.guild.id)
    cfg["report_panel_channel_id"] = kanal.id
    cfg["report_category_id"] = kategorija.id if kategorija else cfg.get("report_category_id")
    if uloga:
        cfg["staff_role_id"] = uloga.id
    save_data(data)
    embed = discord.Embed(
        title=f"{CUSTOM_EMOJI['alert']} Report sistem",
        description=(
            "Prijavi problem, člana ili kršenje pravila privatno staff timu.\n"
            "Klik na dugme otvara kanal koji vide samo autor reporta i staff."
        ),
        color=_LP,
    )
    embed.add_field(
        name=f"{CUSTOM_EMOJI['home']} Kanal",
        value=kanal.mention,
        inline=True,
    )
    embed.add_field(
        name=f"{CUSTOM_EMOJI['grid']} Kategorija",
        value=kategorija.name if kategorija else "trenutna kategorija",
        inline=True,
    )
    await interaction.response.defer(ephemeral=True, thinking=True)
    try:
        _message, updated = await upsert_panel_message(
            kanal,
            interaction.guild.id,
            "report",
            "squad_report_open",
            embed,
            ReportPanelView(),
        )
    except discord.Forbidden:
        await interaction.edit_original_response(
            content=(
                "Podešavanja su sačuvana, ali ne mogu provjeriti ili ažurirati "
                "Report panel. Botu su potrebne dozvole za čitanje historije i slanje poruka."
            )
        )
        return
    except discord.HTTPException:
        await interaction.edit_original_response(
            content=(
                "Discord nije potvrdio slanje/ažuriranje Report panela. "
                "Nisam ponovio slanje da ne bih napravio duplikat."
            )
        )
        return

    status = "ažuriran" if updated else "postavljen"
    await interaction.edit_original_response(
        content=f"{CUSTOM_EMOJI['check']} Report panel je {status} u {kanal.mention}."
    )

# ══════════════════════════════════════════════
#   .veza @Korisnik — Prijedlog za vezu
# ══════════════════════════════════════════════
@bot.command(name="veza")
async def veza(ctx: commands.Context, target: discord.Member = None):
    if not await check_kanal(ctx, "ljubav"): return
    if target is None:
        await ctx.send(embed=discord.Embed(description="> ❌ Navedi korisnika: `.veza @Korisnik`", color=_LP)); return
    if target.id == ctx.author.id:
        await ctx.send(embed=discord.Embed(description="> ❌ Ne možeš biti u vezi sa sobom.", color=_LP)); return
    if target.bot:
        await ctx.send(embed=discord.Embed(description="> ❌ Botovi ne mogu biti u vezi.", color=_LP)); return

    data     = load_data()
    p_sender = get_profile(data, ctx.author.id)
    p_target = get_profile(data, target.id)

    if p_sender["partner_id"] is not None:
        await ctx.send(embed=discord.Embed(description="> ❌ Već si u vezi ili braku!", color=_LP)); return
    if p_target["partner_id"] is not None:
        await ctx.send(embed=discord.Embed(description=f"> ❌ {target.mention} je već u vezi ili braku.", color=_LP)); return

    e = discord.Embed(title="💌 Prijedlog za vezu", color=_LP)
    e.description = (
        f"> **{ctx.author.mention}** šalje prijedlog za vezu **{target.mention}**!\n"
        f">\n"
        f"> Reaguj na poruku:\n"
        f"> ✅ Prihvati\n"
        f"> ❌ Odbij\n"
        f">\n"
        f"> Imaš **60 sekundi** da odlučiš."
    )
    e.set_footer(text=f"{BOT_NAME} {VERSION} • Ljubavni sistem")
    msg = await ctx.send(embed=e)
    await msg.add_reaction("✅")
    await msg.add_reaction("❌")

    def check(reaction, user):
        return user.id == target.id and str(reaction.emoji) in ["✅","❌"] and reaction.message.id == msg.id

    try:
        reaction, _ = await bot.wait_for("reaction_add", timeout=60.0, check=check)
    except asyncio.TimeoutError:
        await msg.edit(embed=discord.Embed(description=f"> ⏰ {target.mention} nije odgovorio/la. Prijedlog je istekao.", color=_LP)); return

    if str(reaction.emoji) == "✅":
        today = datetime.now(timezone.utc).strftime("%d.%m.%Y")
        for pr, pid in [(p_sender, target.id), (p_target, ctx.author.id)]:
            pr["partner_id"] = pid
            pr["status"]     = "veza"
            pr["veza_date"]  = today
        award_love(data, ctx.author.id, target.id, love=50, xp=15, both=True)
        save_data(data)
        ok = discord.Embed(title="💑 Nova veza!", color=_LP)
        ok.description = (
            f"> 🎉 **{ctx.author.mention}** i **{target.mention}** su sada u vezi!\n"
            f">\n"
            f"> Koristite `.spavanje`, `.srce`, `.prsten` i ostale\n"
            f"> komande da povećate ljubav i XP!"
        )
        ok.set_footer(text=f"Veza uspostavljena: {today}")
        await msg.edit(embed=ok)
    else:
        await msg.edit(embed=discord.Embed(description=f"> 💔 {target.mention} je odbio/la prijedlog za vezu.", color=_LP))

# ══════════════════════════════════════════════
#   .brak @Partner — Prijedlog za brak
# ══════════════════════════════════════════════
@bot.command(name="brak")
async def brak(ctx: commands.Context, partner: discord.Member = None):
    if not await check_kanal(ctx, "ljubav"): return
    if partner is None:
        await ctx.send(embed=discord.Embed(description="> ❌ Navedi partnera: `.brak @Partner`\n> 💡 Tip: koristi `.prsten @Partner` za brak s prstenom!", color=_LP)); return

    data      = load_data()
    p_sender  = get_profile(data, ctx.author.id)
    p_partner = get_profile(data, partner.id)

    if p_sender["partner_id"] != partner.id:
        await ctx.send(embed=discord.Embed(description="> ❌ Možeš zatražiti brak samo od svog/e partnera/ice!", color=_LP)); return
    if p_sender["status"] == "brak":
        await ctx.send(embed=discord.Embed(description="> ❌ Već ste u braku!", color=_LP)); return
    if p_sender["love"] < 500:
        nedostaje = 500 - p_sender["love"]
        e = discord.Embed(title="💔 Nedovoljno ljubavi", color=_LP)
        e.description = (
            f"> Potrebno je minimum **500 bodova ljubavi** za brak.\n"
            f"> Trenutno imaš **{p_sender['love']}** bodova.\n"
            f"> Nedostaje još **{nedostaje}** bodova!"
        )
        await ctx.send(embed=e); return

    e = discord.Embed(title="💍 Prijedlog za brak", color=_LP)
    e.description = (
        f"> **{ctx.author.mention}** kleči pred **{partner.mention}**!\n"
        f">\n"
        f"> *\"Hoćeš li biti moj/a?\"*\n"
        f">\n"
        f"> ✅ Da, prihvatam!\n"
        f"> ❌ Odbij\n"
        f">\n"
        f"> **60 sekundi** za odluku."
    )
    e.set_footer(text=f"{BOT_NAME} {VERSION} • Ljubavni sistem")
    msg = await ctx.send(embed=e)
    await msg.add_reaction("✅")
    await msg.add_reaction("❌")

    def check(reaction, user):
        return user.id == partner.id and str(reaction.emoji) in ["✅","❌"] and reaction.message.id == msg.id

    try:
        reaction, _ = await bot.wait_for("reaction_add", timeout=60.0, check=check)
    except asyncio.TimeoutError:
        await msg.edit(embed=discord.Embed(description=f"> ⏰ {partner.mention} nije odgovorio/la. Prijedlog je istekao.", color=_LP)); return

    if str(reaction.emoji) == "✅":
        today = datetime.now(timezone.utc).strftime("%d.%m.%Y")
        p_sender["status"]     = "brak"
        p_sender["brak_date"]  = today
        p_partner["status"]    = "brak"
        p_partner["brak_date"] = today
        award_love(data, ctx.author.id, partner.id, love=100, xp=25, both=True)
        save_data(data)
        ok = discord.Embed(title="💒 Brak je sklopljen!", color=_LP)
        ok.description = (
            f"> 🎊 **{ctx.author.mention}** i **{partner.mention}** su sada u braku!\n"
            f">\n"
            f"> Pokrenite svadbu komandom `.svadba`!"
        )
        ok.set_footer(text=f"Brak sklopljen: {today}")
        await msg.edit(embed=ok)
    else:
        await msg.edit(embed=discord.Embed(description=f"> 💔 {partner.mention} je odbio/la prijedlog za brak.", color=_LP))

# ══════════════════════════════════════════════
#   .prsten — Prstenovi
# ══════════════════════════════════════════════
@bot.command(name="prsten")
async def prsten(ctx: commands.Context, partner: discord.Member = None):
    if not await check_kanal(ctx, "ljubav"): return
    data = load_data()
    p    = get_profile(data, ctx.author.id)
    love = p.get("love", 0)

    if partner is None:
        best  = get_best_prsten(love)
        lines = []
        for ring in PRSTENOVI:
            unlocked = love >= ring["love"]
            tag      = " ← TVOJ" if ring["id"] == best["id"] else ""
            lock     = "✅" if unlocked else "🔒"
            lines.append(f"> `{ring['id']}` {ring['emoji']} **{ring['naziv']}** — {ring['love']:,} bodova {lock}{tag}")

        e = discord.Embed(title="💍 Prodavnica prstena", color=_LP)
        e.description = (
            "> Prstenovi se otključavaju bodovima ljubavi.\n"
            "> Koristi `.prsten @Partner` za brak s prstenom!\n"
            ">\n"
            + "\n".join(lines)
        )
        e.add_field(name="Tvoj trenutni prsten", value=f"> {best['emoji']} **{best['naziv']}**\n> *{best['opis']}*", inline=False)
        e.add_field(name="Bodovi ljubavi",        value=f"> **{love}**", inline=True)
        e.set_footer(text=f"{BOT_NAME} {VERSION} • Bodovi rastu s .spavanje i .srce")
        await ctx.send(embed=e)
        return

    if partner.id == ctx.author.id:
        await ctx.send(embed=discord.Embed(description="> ❌ Ne možeš zaprositi sebe.", color=_LP)); return
    if partner.bot:
        await ctx.send(embed=discord.Embed(description="> ❌ Botovi ne mogu biti u braku.", color=_LP)); return
    if p["partner_id"] != partner.id:
        await ctx.send(embed=discord.Embed(description="> ❌ Možeš zaprositi samo svog/svoju partnera/icu!", color=_LP)); return
    if p["status"] == "brak":
        await ctx.send(embed=discord.Embed(description="> ❌ Već ste u braku!", color=_LP)); return
    if love < 500:
        e = discord.Embed(title="💔 Nedovoljno ljubavi", color=_LP)
        e.description = f"> Potrebno je minimum **500 bodova ljubavi** za brak.\n> Trenutno imaš **{love}** — nedostaje još **{500-love}**!"
        await ctx.send(embed=e); return

    best = get_best_prsten(love)
    e = discord.Embed(title=f"{best['emoji']} Prijedlog za brak s prstenom", color=_LP)
    e.description = (
        f"> **{ctx.author.mention}** klekne pred **{partner.mention}** i izvlači:\n"
        f">\n"
        f"> {best['emoji']} **{best['naziv']}**\n"
        f"> *{best['opis']}*\n"
        f">\n"
        f"> *\"Hoćeš li biti moj/a?\"*\n"
        f">\n"
        f"> ✅ Da, prihvatam!\n"
        f"> ❌ Odbij\n"
        f">\n"
        f"> **60 sekundi** za odluku."
    )
    e.set_footer(text=f"{BOT_NAME} {VERSION} • Ljubavni sistem")
    msg = await ctx.send(embed=e)
    await msg.add_reaction("✅")
    await msg.add_reaction("❌")

    def check(reaction, user):
        return user.id == partner.id and str(reaction.emoji) in ["✅","❌"] and reaction.message.id == msg.id

    try:
        reaction, _ = await bot.wait_for("reaction_add", timeout=60.0, check=check)
    except asyncio.TimeoutError:
        await msg.edit(embed=discord.Embed(description=f"> ⏰ {partner.mention} nije odgovorio/la.", color=_LP)); return

    if str(reaction.emoji) == "✅":
        today     = datetime.now(timezone.utc).strftime("%d.%m.%Y")
        p_partner = get_profile(data, partner.id)
        for pr in [p, p_partner]:
            pr["status"]    = "brak"
            pr["brak_date"] = today
            pr["prsten"]    = best["naziv"]
        award_love(data, ctx.author.id, partner.id, love=150, xp=35, both=True)
        save_data(data)
        ok = discord.Embed(title="💒 Brak je sklopljen!", color=_LP)
        ok.description = (
            f"> 🎊 **{ctx.author.mention}** {best['emoji']} **{partner.mention}**\n"
            f">\n"
            f"> Prsten: **{best['emoji']} {best['naziv']}**\n"
            f">\n"
            f"> Pokrenite svadbu komandom `.svadba`!"
        )
        ok.set_footer(text=f"Brak sklopljen: {today}")
        await msg.edit(embed=ok)
    else:
        await msg.edit(embed=discord.Embed(description=f"> 💔 {partner.mention} je odbio/la prijedlog.", color=_LP))

# ══════════════════════════════════════════════
#   .svadba — Ceremonija
# ══════════════════════════════════════════════
SVADBA_PORUKE = [
    "Neka vaša ljubav traje vječno! 💕",
    "Sve sreće u zajedničkom životu! 🌟",
    "Neka svaki dan bude ljepši od prethodnog! ☀️",
    "Ljubav je vaša supermoć! ⚡",
    "Neka vaš dom uvijek bude pun smijeha! 😊",
]
SVADBA_FAZE = [
    "🎵 Muzika počinje da svira...",
    "👗 Mlada ulazi u crkvu...",
    "🤵 Mladoženja čeka na oltaru...",
    "💍 Razmjenjuju prstenje...",
    "🎊 Cestitamo, sada su muž i žena!",
]

@bot.command(name="svadba")
async def svadba(ctx: commands.Context):
    if not await check_kanal(ctx, "ljubav"): return
    data = load_data()
    p    = get_profile(data, ctx.author.id)

    if p["status"] != "brak" or p["partner_id"] is None:
        await ctx.send(embed=discord.Embed(description="> ❌ Moraš biti u braku da bi pokrenuo/la svadbu!", color=_LP)); return

    partner      = ctx.guild.get_member(p["partner_id"])
    partner_name = partner.mention if partner else f"<@{p['partner_id']}>"
    prsten_info  = p.get("prsten")
    prsten_txt   = f"\n> 💍 Prsten: **{prsten_info}**" if prsten_info else ""

    e = discord.Embed(title="💒 Svadba ceremonija", color=_LP)
    e.description = f"> **{ctx.author.mention}** i **{partner_name}**{prsten_txt}\n>\n> {SVADBA_FAZE[0]}"
    msg = await ctx.send(embed=e)

    for faza in SVADBA_FAZE[1:]:
        await asyncio.sleep(2)
        e.description = f"> **{ctx.author.mention}** i **{partner_name}**{prsten_txt}\n>\n> {faza}"
        await msg.edit(embed=e)

    bonus        = random.randint(50, 150)
    p["love"]    = p.get("love", 0) + bonus
    p["xp"]      = p.get("xp", 0) + 50
    p_partner    = get_profile(data, p["partner_id"])
    p_partner["love"] = p_partner.get("love", 0) + bonus
    p_partner["xp"]   = p_partner.get("xp", 0) + 50
    save_data(data)

    await asyncio.sleep(1)
    ok = discord.Embed(title="🎊 Svadba je završena!", color=_LP)
    ok.description = (
        f"> **{ctx.author.mention}** i **{partner_name}**{prsten_txt}\n"
        f">\n"
        f"> *{random.choice(SVADBA_PORUKE)}*\n"
        f">\n"
        f"> 💗 **+{bonus}** bodova ljubavi kao vjenčani poklon!\n"
        f"> ⭐ **+50 XP** za oboje!"
    )
    ok.set_footer(text=f"Brak od: {p.get('brak_date','?')} • {BOT_NAME} {VERSION}")
    await msg.edit(embed=ok)

# ══════════════════════════════════════════════
#   .obnova — Obnovi bračne zavjete
# ══════════════════════════════════════════════
@bot.command(name="obnova")
async def obnova(ctx: commands.Context):
    if not await check_kanal(ctx, "ljubav"): return
    data = load_data()
    p    = get_profile(data, ctx.author.id)

    if p["status"] != "brak" or p["partner_id"] is None:
        await ctx.send(embed=discord.Embed(description="> ❌ Moraš biti u braku da bi obnovio/la zavjete!", color=_LP)); return

    proslo = now_ts() - p.get("last_obnova", 0)
    if proslo < 7 * 24 * 3600:
        pre = 7 * 24 * 3600 - proslo
        d   = pre // 86400
        h   = (pre % 86400) // 3600
        await ctx.send(embed=discord.Embed(
            description=f"> ⏳ Možeš obnoviti zavjete za **{d}d {h}h**.",
            color=_LP
        )); return

    partner      = ctx.guild.get_member(p["partner_id"])
    partner_name = partner.mention if partner else f"<@{p['partner_id']}>"
    bonus        = random.randint(100, 200)
    p["love"]    = p.get("love", 0) + bonus
    p["xp"]      = p.get("xp", 0) + 30
    p["last_obnova"] = now_ts()
    p_partner    = get_profile(data, p["partner_id"])
    p_partner["love"]       = p_partner.get("love", 0) + bonus
    p_partner["xp"]         = p_partner.get("xp", 0) + 30
    p_partner["last_obnova"] = now_ts()
    save_data(data)

    ZAVJETE_PORUKE = [
        "I danas bih te izabrao/la iznova.",
        "Naša ljubav je jača svaki dan.",
        "Volim te više nego ičim na ovom svijetu.",
        "Ti si moj dom.",
    ]
    e = discord.Embed(title="💍 Obnova bračnih zavjeta", color=_LP)
    e.description = (
        f"> **{ctx.author.mention}** obnavlja zavjete s **{partner_name}**!\n"
        f">\n"
        f"> *\"{random.choice(ZAVJETE_PORUKE)}\"*\n"
        f">\n"
        f"> 💗 **+{bonus}** bodova ljubavi za oboje!\n"
        f"> ⭐ **+30 XP** za oboje!"
    )
    e.set_footer(text=f"Cooldown: 7 dana • {BOT_NAME} {VERSION}")
    await ctx.send(embed=e)

# ══════════════════════════════════════════════
#   .zakletva — Napiši bračnu zakletvu
# ══════════════════════════════════════════════
@bot.command(name="zakletva")
async def zakletva(ctx: commands.Context, *, tekst: str = None):
    if not await check_kanal(ctx, "ljubav"): return
    data = load_data()
    p    = get_profile(data, ctx.author.id)

    if p["status"] is None or p["partner_id"] is None:
        await ctx.send(embed=discord.Embed(description="> ❌ Moraš biti u vezi ili braku da bi napisao/la zakletvu!", color=_LP)); return

    if tekst is None:
        if "zakletva" not in data:
            data["zakletva"] = {}
        ck  = couple_key(ctx.author.id, p["partner_id"])
        zak = data["zakletva"].get(ck)
        if zak:
            partner      = ctx.guild.get_member(p["partner_id"])
            partner_name = partner.mention if partner else f"<@{p['partner_id']}>"
            e = discord.Embed(title="📜 Bračna zakletva", color=_LP)
            e.description = f"> 📖 *\"{zak['tekst']}\"*\n>\n> — {ctx.author.mention} za {partner_name}"
            e.set_footer(text=f"Napisano: {zak.get('datum','?')} • {BOT_NAME} {VERSION}")
            await ctx.send(embed=e)
        else:
            await ctx.send(embed=discord.Embed(
                description="> 📜 Još niste napisali zakletvu!\n> Koristi: `.zakletva Ovdje piši svoju zakletvu...`",
                color=_LP
            ))
        return

    if "zakletva" not in data:
        data["zakletva"] = {}
    ck = couple_key(ctx.author.id, p["partner_id"])
    data["zakletva"][ck] = {
        "tekst": tekst[:500],
        "autor": ctx.author.id,
        "datum": datetime.now(timezone.utc).strftime("%d.%m.%Y"),
    }
    award_love(data, ctx.author.id, p["partner_id"], love=25, xp=8, both=True)
    save_data(data)

    partner      = ctx.guild.get_member(p["partner_id"])
    partner_name = partner.mention if partner else f"<@{p['partner_id']}>"
    e = discord.Embed(title="📜 Zakletva zapisana!", color=_LP)
    e.description = (
        f"> **{ctx.author.mention}** → {partner_name}\n"
        f">\n"
        f"> 📖 *\"{tekst[:500]}\"*"
        f"\n>\n> 💗 **+25 bodova ljubavi za oboje**\n> ⭐ **+8 XP za oboje**"
    )
    e.set_footer(text=f"{BOT_NAME} {VERSION}")
    await ctx.send(embed=e)

# ══════════════════════════════════════════════
#   .spavanje — +30-80 bodova, cooldown 8h
# ══════════════════════════════════════════════
@bot.command(name="spavanje")
async def spavanje(ctx: commands.Context):
    if not await check_kanal(ctx, "ljubav"): return
    data = load_data()
    p    = get_profile(data, ctx.author.id)

    if p["status"] is None or p["partner_id"] is None:
        await ctx.send(embed=discord.Embed(description="> ❌ Nemaš partnera! Koristi `.veza @Korisnik`.", color=_LP)); return

    proslo = now_ts() - p["last_sleep"]
    if proslo < 8 * 3600:
        pre = 8 * 3600 - proslo
        await ctx.send(embed=discord.Embed(
            description=f"> ⏳ Već si spavao/la! Sljedeće spavanje za **{pre//3600}h {(pre%3600)//60}m**.",
            color=_LP
        )); return

    partner      = ctx.guild.get_member(p["partner_id"])
    partner_name = partner.mention if partner else f"<@{p['partner_id']}>"
    bonus        = random.randint(30, 80)
    p["love"]       = p.get("love", 0) + bonus
    p["xp"]         = p.get("xp", 0) + 5
    p["last_sleep"] = now_ts()
    p_partner       = get_profile(data, p["partner_id"])
    p_partner["love"] = p_partner.get("love", 0) + bonus
    p_partner["xp"]   = p_partner.get("xp", 0) + 5
    save_data(data)

    poruke = [
        f"Ti i **{partner_name}** ste zaspali jedno pored drugog... 💤",
        f"Mirno spavanje s **{partner_name}** jača vašu vezu! 🌙",
        f"Noć provedena s **{partner_name}** — ništa bolje nema! ⭐",
    ]
    e = discord.Embed(title="🌙 Laku noć!", color=_LP)
    e.description = (
        f"> {random.choice(poruke)}\n"
        f">\n"
        f"> 💗 **+{bonus}** bodova ljubavi!\n"
        f"> ⭐ **+5 XP**"
    )
    e.add_field(name="Ukupno ljubavi", value=f"> **{p['love']}** bodova", inline=True)
    e.set_footer(text=f"Cooldown: 8h • {BOT_NAME} {VERSION}")
    await ctx.send(embed=e)

# ══════════════════════════════════════════════
#   .srce — Dnevni bonus +100-200, cooldown 24h
# ══════════════════════════════════════════════
@bot.command(name="srce")
async def srce(ctx: commands.Context):
    if not await check_kanal(ctx, "ljubav"): return
    data = load_data()
    p    = get_profile(data, ctx.author.id)

    if p["status"] is None or p["partner_id"] is None:
        await ctx.send(embed=discord.Embed(description="> ❌ Nemaš partnera! Koristi `.veza @Korisnik`.", color=_LP)); return

    proslo = now_ts() - p["last_srce"]
    if proslo < 24 * 3600:
        pre = 24 * 3600 - proslo
        await ctx.send(embed=discord.Embed(
            description=f"> ⏳ Već si poslao/la srce danas! Ponovo za **{pre//3600}h {(pre%3600)//60}m**.",
            color=_LP
        )); return

    partner      = ctx.guild.get_member(p["partner_id"])
    partner_name = partner.mention if partner else f"<@{p['partner_id']}>"
    bonus        = random.randint(100, 200)
    p["love"]      = p.get("love", 0) + bonus
    p["xp"]        = p.get("xp", 0) + 10
    p["last_srce"] = now_ts()
    p_partner      = get_profile(data, p["partner_id"])
    p_partner["love"] = p_partner.get("love", 0) + bonus
    p_partner["xp"]   = p_partner.get("xp", 0) + 10
    save_data(data)

    poruke = [
        "šalje ogromno srce",
        "šalje buket ruža",
        "pušta tvoju omiljenu pjesmu",
        "priprema tvoju omiljenu hranu",
        "ostavlja tajnu poruku ljubavi",
    ]
    e = discord.Embed(title="❤️ Dnevno srce!", color=_LP)
    e.description = (
        f"> **{ctx.author.mention}** {random.choice(poruke)} za **{partner_name}**!\n"
        f">\n"
        f"> 💗 **+{bonus}** bodova ljubavi za oboje!\n"
        f"> ⭐ **+10 XP** za oboje!"
    )
    e.add_field(name="Tvoja ukupna ljubav", value=f"> **{p['love']}** bodova", inline=True)
    e.set_footer(text=f"Cooldown: 24h • {BOT_NAME} {VERSION}")
    await ctx.send(embed=e)

# ══════════════════════════════════════════════
#   .zagrljaj @Partner — +3 XP, cooldown 2h
# ══════════════════════════════════════════════
@bot.command(name="zagrljaj")
async def zagrljaj(ctx: commands.Context, target: discord.Member = None):
    if not await check_kanal(ctx, "ljubav"): return
    if target is None:
        await ctx.send(embed=discord.Embed(description="> ❌ Navedi korisnika: `.zagrljaj @Korisnik`", color=_LP)); return
    if target.id == ctx.author.id:
        await ctx.send(embed=discord.Embed(description="> ❌ Ne možeš zagrliti sebe!", color=_LP)); return

    data = load_data()
    p    = get_profile(data, ctx.author.id)
    proslo = now_ts() - p.get("last_zagrljaj", 0)
    if proslo < 2 * 3600:
        pre = 2 * 3600 - proslo
        await ctx.send(embed=discord.Embed(
            description=f"> ⏳ Sljedeći zagrljaj za **{pre//3600}h {(pre%3600)//60}m**.",
            color=_LP
        )); return

    p["last_zagrljaj"] = now_ts()
    # Aktivnost se uvijek knjiži autoru; partner dobija svoj dio ako je cilj
    # stvarni partner, baš kao kod ostalih ljubavnih komandi.
    award_love(
        data,
        ctx.author.id,
        target.id,
        love=10,
        xp=3,
        both=p.get("partner_id") == target.id,
    )
    save_data(data)

    ZAGRLJAJ_PORUKE = [
        f"{ctx.author.mention} čvrsto grli {target.mention}! 🤗",
        f"{ctx.author.mention} zagrljuje {target.mention} toplim zagrljajem! 💞",
        f"{ctx.author.mention} ogrljuje {target.mention} i ne pušta! 🥰",
    ]
    e = discord.Embed(title="🤗 Zagrljaj!", color=_LP)
    e.description = (
        f"> {random.choice(ZAGRLJAJ_PORUKE)}\n"
        f">\n"
        f"> 💗 **+10 bodova ljubavi**\n"
        f"> ⭐ **+3 XP**"
    )
    e.set_footer(text=f"Cooldown: 2h • {BOT_NAME} {VERSION}")
    await ctx.send(embed=e)

# ══════════════════════════════════════════════
#   .poljubac @Partner — +5 XP, cooldown 1h
# ══════════════════════════════════════════════
@bot.command(name="poljubac")
async def poljubac(ctx: commands.Context, target: discord.Member = None):
    if not await check_kanal(ctx, "ljubav"): return
    if target is None:
        await ctx.send(embed=discord.Embed(description="> ❌ Navedi korisnika: `.poljubac @Korisnik`", color=_LP)); return
    if target.id == ctx.author.id:
        await ctx.send(embed=discord.Embed(description="> ❌ Ne možeš poljubiti sebe!", color=_LP)); return

    data = load_data()
    p    = get_profile(data, ctx.author.id)
    proslo = now_ts() - p.get("last_poljubac", 0)
    if proslo < 3600:
        pre = 3600 - proslo
        await ctx.send(embed=discord.Embed(
            description=f"> ⏳ Sljedeći poljubac za **{pre//60}m {pre%60}s**.",
            color=_LP
        )); return

    p["last_poljubac"] = now_ts()
    award_love(
        data,
        ctx.author.id,
        target.id,
        love=15,
        xp=5,
        both=p.get("partner_id") == target.id,
    )
    save_data(data)

    POLJUBAC_PORUKE = [
        f"{ctx.author.mention} nježno ljubi {target.mention}! 💋",
        f"{ctx.author.mention} ukralo je poljubac od {target.mention}! 😘",
        f"{ctx.author.mention} daje strasan poljubac {target.mention}! 💕",
    ]
    e = discord.Embed(title="💋 Poljubac!", color=_LP)
    e.description = (
        f"> {random.choice(POLJUBAC_PORUKE)}\n"
        f">\n"
        f"> 💗 **+15 bodova ljubavi**\n"
        f"> ⭐ **+5 XP**"
    )
    e.set_footer(text=f"Cooldown: 1h • {BOT_NAME} {VERSION}")
    await ctx.send(embed=e)

# ══════════════════════════════════════════════
#   .ples @Partner — Ples zajedno
# ══════════════════════════════════════════════
@bot.command(name="ples")
async def ples(ctx: commands.Context, target: discord.Member = None):
    if not await check_kanal(ctx, "ljubav"): return
    if target is None:
        await ctx.send(embed=discord.Embed(description="> ❌ Navedi korisnika: `.ples @Korisnik`", color=_LP)); return
    if target.id == ctx.author.id:
        await ctx.send(embed=discord.Embed(description="> ❌ Ne možeš plesati sam/a!", color=_LP)); return

    PLESOVI = [
        f"{ctx.author.mention} i {target.mention} plešu waltz! 💃🕺",
        f"{ctx.author.mention} i {target.mention} plešu tango! 🌹",
        f"{ctx.author.mention} i {target.mention} plešu breakdance! 🎶",
        f"{ctx.author.mention} i {target.mention} vrtoglavo se okreću po parketu! ✨",
    ]
    data = load_data()
    award_love(
        data, ctx.author.id, target.id, love=25, xp=5,
        both=get_profile(data, ctx.author.id).get("partner_id") == target.id,
    )
    save_data(data)
    e = discord.Embed(title="💃 Ples!", color=_LP)
    e.description = (
        f"> {random.choice(PLESOVI)}\n>\n"
        f"> 💗 **+25 bodova ljubavi**\n> ⭐ **+5 XP**"
    )
    e.set_footer(text=f"{BOT_NAME} {VERSION}")
    await ctx.send(embed=e)

# ══════════════════════════════════════════════
#   .pijte — Popijmo zajedno
# ══════════════════════════════════════════════
@bot.command(name="pijte")
async def pijte(ctx: commands.Context):
    if not await check_kanal(ctx, "ljubav"):
        return
    PIJENJA = [
        f"{ctx.author.mention} nazdravlja svima! 🥂",
        f"{ctx.author.mention} naručuje krug za cijeli server! 🍺",
        f"{ctx.author.mention} ispija šampanjac! 🍾",
    ]
    data = load_data()
    award_love(data, ctx.author.id, love=10, xp=2)
    save_data(data)
    e = discord.Embed(title="🍾 Živjeli!", color=_LP)
    e.description = (
        f"> {random.choice(PIJENJA)}\n>\n"
        f"> 💗 **+10 bodova ljubavi**\n> ⭐ **+2 XP**"
    )
    e.set_footer(text=f"{BOT_NAME} {VERSION}")
    await ctx.send(embed=e)

# ══════════════════════════════════════════════
#   .film — Gledaj film
# ══════════════════════════════════════════════
@bot.command(name="film")
async def film(ctx: commands.Context):
    if not await check_kanal(ctx, "ljubav"):
        return
    FILMOVI = [
        "Titanic 🚢", "The Notebook 📔", "La La Land 🎵",
        "Dirty Dancing 💃", "Ghost 👻", "Casablanca 🌹",
        "Pride & Prejudice 📚", "Romeo & Juliet ⚔️",
    ]
    REAKCIJE = [
        "plakao/la na kraju",
        "zaspao/la u pola filma 😴",
        "gledao/la dva puta zaredom",
        "naručio/la popcorn i uživao/la",
    ]
    film_naziv = random.choice(FILMOVI)
    data = load_data()
    award_love(data, ctx.author.id, love=10, xp=2)
    save_data(data)
    e = discord.Embed(title="🎬 Film veče!", color=_LP)
    e.description = (
        f"> {ctx.author.mention} gleda **{film_naziv}**\n"
        f"> i {random.choice(REAKCIJE)}!\n>\n"
        f"> 💗 **+10 bodova ljubavi**\n> ⭐ **+2 XP**"
    )
    e.set_footer(text=f"{BOT_NAME} {VERSION}")
    await ctx.send(embed=e)

# ══════════════════════════════════════════════
#   .istina — Istina ili laž
# ══════════════════════════════════════════════
@bot.command(name="istina")
async def istina(ctx: commands.Context):
    if not await check_kanal(ctx, "ljubav"):
        return
    PITANJA = [
        "Jesi li ikad lagao/la svom partneru?",
        "Ko ti se prvi svidio na serveru?",
        "Imaš li tajnu koju nikome nisi rekao/la?",
        "Kad si zadnji put plakao/la?",
        "Bi li pozajmio/la novac prijatelju?",
        "Ko je tvoja tajna simpatija?",
        "Šta bi uradio/la za 1000€?",
        "Koji je tvoj najveći strah?",
    ]
    data = load_data()
    award_love(data, ctx.author.id, love=10, xp=2)
    save_data(data)
    e = discord.Embed(title="🎯 Istina ili laž!", color=_LP)
    e.description = (
        f"> {ctx.author.mention}, odgovori iskreno:\n>\n"
        f"> ❓ **{random.choice(PITANJA)}**\n>\n"
        f"> 💗 **+10 bodova ljubavi**\n> ⭐ **+2 XP**"
    )
    e.set_footer(text=f"{BOT_NAME} {VERSION}")
    await ctx.send(embed=e)

# ══════════════════════════════════════════════
#   .izazov — Daj izazov
# ══════════════════════════════════════════════
@bot.command(name="izazov")
async def izazov(ctx: commands.Context):
    if not await check_kanal(ctx, "ljubav"):
        return
    IZAZOVI = [
        "Pošalji GIF kako plešeš u sljedećih 5 minuta!",
        "Promijeni username u 'Izazov Champion' na 1 sat!",
        "Napiši pjesmu o sebi u 4 stiha!",
        "Reci 10 komplimenta prvoj osobi koja odgovori!",
        "Promijeni profilnu sliku na nešto smiješno na 30 minuta!",
        "Napiši pismo svojoj prošlosti!",
        "Pjevaj svoju omiljenu pjesmu (tekst u chat)!",
    ]
    data = load_data()
    award_love(data, ctx.author.id, love=15, xp=3)
    save_data(data)
    e = discord.Embed(title="⚡ Izazov!", color=_LP)
    e.description = (
        f"> {ctx.author.mention} prihvata izazov:\n>\n"
        f"> 🎯 **{random.choice(IZAZOVI)}**\n>\n"
        f"> 💗 **+15 bodova ljubavi**\n> ⭐ **+3 XP**"
    )
    e.set_footer(text=f"{BOT_NAME} {VERSION}")
    await ctx.send(embed=e)

# ══════════════════════════════════════════════
#   .ljubavni-test @Korisnik
# ══════════════════════════════════════════════
@bot.command(name="ljubavni-test")
async def ljubavni_test(ctx: commands.Context, target: discord.Member = None):
    if not await check_kanal(ctx, "ljubav"):
        return
    if target is None:
        await ctx.send(embed=discord.Embed(description="> ❌ Navedi korisnika: `.ljubavni-test @Korisnik`", color=_LP)); return
    if target.id == ctx.author.id:
        await ctx.send(embed=discord.Embed(description="> ❌ Ne možeš testirati sebe!", color=_LP)); return

    postotak = random.randint(1, 100)
    if postotak >= 90:
        opis = "Ovo je prava ljubav! 💞"
        emoji = "💕"
    elif postotak >= 70:
        opis = "Jaka privlačnost! 😍"
        emoji = "❤️"
    elif postotak >= 50:
        opis = "Ima potencijala! 😊"
        emoji = "💛"
    elif postotak >= 30:
        opis = "Možda samo prijatelji? 🤔"
        emoji = "💙"
    else:
        opis = "Nema hemije... 😅"
        emoji = "🩶"

    bar_filled = int(postotak / 100 * 15)
    bar = f"{'💗' * bar_filled}{'🤍' * (15 - bar_filled)}"
    data = load_data()
    award_love(data, ctx.author.id, target.id, love=15, xp=3, both=True)
    save_data(data)

    e = discord.Embed(title=f"💘 Ljubavni test!", color=_LP)
    e.description = (
        f"> {ctx.author.mention} {emoji} {target.mention}\n"
        f">\n"
        f"> {bar}\n"
        f"> **{postotak}% kompatibilnosti**\n"
        f">\n"
        f"> {opis}\n>\n"
        f"> 💗 **+15 bodova ljubavi za oboje**\n> ⭐ **+3 XP za oboje**"
    )
    e.set_footer(text=f"{BOT_NAME} {VERSION} • Samo za zabavu!")
    await ctx.send(embed=e)

# ══════════════════════════════════════════════
#   .compatibility @Korisnik
# ══════════════════════════════════════════════
@bot.command(name="compatibility")
async def compatibility(ctx: commands.Context, target: discord.Member = None):
    if not await check_kanal(ctx, "ljubav"):
        return
    if target is None:
        await ctx.send(embed=discord.Embed(description="> ❌ Navedi korisnika: `.compatibility @Korisnik`", color=_LP)); return

    # Deterministički rezultat baziran na ID-evima
    seed = (ctx.author.id + target.id) % 100
    postotak = (seed * 7 + 13) % 100 + 1

    ASPEKTI = [
        ("🧠 Intelektualna", random.randint(40, 100)),
        ("💕 Romantična",    random.randint(40, 100)),
        ("😂 Humoristička",  random.randint(40, 100)),
        ("💪 Fizička",       random.randint(40, 100)),
        ("🌟 Duhovna",       random.randint(40, 100)),
    ]

    linije = []
    for naziv, val in ASPEKTI:
        bar = "█" * (val // 10) + "░" * (10 - val // 10)
        linije.append(f"> {naziv}: `{bar}` {val}%")

    data = load_data()
    award_love(data, ctx.author.id, target.id, love=15, xp=3, both=True)
    save_data(data)
    e = discord.Embed(title="🔮 Compatibility analiza", color=_LP)
    e.description = (
        f"> {ctx.author.mention} & {target.mention}\n"
        f">\n"
        f"> **Ukupna kompatibilnost: {postotak}%**\n"
        f">\n"
        + "\n".join(linije)
        + "\n>\n> 💗 **+15 bodova ljubavi za oboje**\n> ⭐ **+3 XP za oboje**"
    )
    e.set_footer(text=f"{BOT_NAME} {VERSION} • Samo za zabavu!")
    await ctx.send(embed=e)

# ══════════════════════════════════════════════
#   .poklon @Partner — Pošalji poklon
# ══════════════════════════════════════════════
@bot.command(name="poklon")
async def poklon(ctx: commands.Context, target: discord.Member = None):
    if not await check_kanal(ctx, "ljubav"): return
    if target is None:
        await ctx.send(embed=discord.Embed(description="> ❌ Navedi korisnika: `.poklon @Korisnik`", color=_LP)); return
    if target.id == ctx.author.id:
        await ctx.send(embed=discord.Embed(description="> ❌ Ne možeš pokloniti sebi!", color=_LP)); return

    POKLONI_LIST = [
        ("🌹", "buket ruža"),
        ("🍫", "kutiju čokolade"),
        ("🧸", "plišanu igračku"),
        ("💐", "šareni buket cvijeća"),
        ("🍰", "tortu"),
        ("🎁", "misteriozan poklon"),
        ("📿", "ogrlicu"),
        ("🌸", "parfem"),
    ]
    emoji, naziv = random.choice(POKLONI_LIST)
    data = load_data()
    p    = get_profile(data, ctx.author.id)
    is_partner = p.get("partner_id") == target.id
    award_love(
        data,
        ctx.author.id,
        target.id,
        love=30 if is_partner else 10,
        xp=8 if is_partner else 2,
        both=is_partner,
    )
    save_data(data)
    xp_txt = (
        f"\n> 💗 **+{30 if is_partner else 10} bodova ljubavi**"
        f"{' za oboje' if is_partner else ''}!"
        f"\n> ⭐ **+{8 if is_partner else 2} XP**"
        f"{' za oboje' if is_partner else ''}!"
    )

    e = discord.Embed(title="🎁 Poklon poslan!", color=_LP)
    e.description = (
        f"> **{ctx.author.mention}** poklanja {emoji} **{naziv}**\n"
        f"> osobi **{target.mention}**!{xp_txt}"
    )
    e.set_footer(text=f"{BOT_NAME} {VERSION}")
    await ctx.send(embed=e)

# ══════════════════════════════════════════════
#   .cvijece @Partner — Pošalji ružu
# ══════════════════════════════════════════════
@bot.command(name="cvijece")
async def cvijece(ctx: commands.Context, target: discord.Member = None):
    if not await check_kanal(ctx, "ljubav"): return
    if target is None:
        await ctx.send(embed=discord.Embed(description="> ❌ Navedi korisnika: `.cvijece @Korisnik`", color=_LP)); return

    CVIJECE = ["🌹", "🌷", "🌸", "💐", "🌺", "🌻", "🌼"]
    emoji = random.choice(CVIJECE)
    e = discord.Embed(title=f"{emoji} Cvijeće!", color=_LP)
    e.description = f"> **{ctx.author.mention}** šalje {emoji} **{target.mention}**!\n> *Neka svaki dan bude pun ljepote!* 🌸"
    e.set_footer(text=f"{BOT_NAME} {VERSION}")
    await ctx.send(embed=e)

# ══════════════════════════════════════════════
#   .cokolada @Partner
# ══════════════════════════════════════════════
@bot.command(name="cokolada")
async def cokolada(ctx: commands.Context, target: discord.Member = None):
    if not await check_kanal(ctx, "ljubav"): return
    if target is None:
        await ctx.send(embed=discord.Embed(description="> ❌ Navedi korisnika: `.cokolada @Korisnik`", color=_LP)); return

    VRSTE = ["mliječna", "crna", "bijela", "s lješnjacima", "s karamelom"]
    e = discord.Embed(title="🍫 Čokolada!", color=_LP)
    e.description = (
        f"> **{ctx.author.mention}** poklanja 🍫 **{random.choice(VRSTE)} čokoladu**\n"
        f"> osobi **{target.mention}**!\n"
        f"> *Slatko kao tvoj osmijeh!* 😊"
    )
    e.set_footer(text=f"{BOT_NAME} {VERSION}")
    await ctx.send(embed=e)

# ══════════════════════════════════════════════
#   .ljubomora — Prikazuje ljubomoru
# ══════════════════════════════════════════════
@bot.command(name="ljubomora")
async def ljubomora(ctx: commands.Context):
    if not await check_kanal(ctx, "ljubav"): return
    data = load_data()
    p    = get_profile(data, ctx.author.id)

    if p["status"] is None or p["partner_id"] is None:
        await ctx.send(embed=discord.Embed(description="> ❌ Nemaš partnera! Nema koga da budeš ljubomoran/a.", color=_LP)); return

    p["ljubomora"] = p.get("ljubomora", 0) + 1
    save_data(data)
    nivo = p["ljubomora"]

    if nivo <= 3:
        opis = "Mala ljubomora... to je slatko! 😊"
        emoji = "😕"
    elif nivo <= 7:
        opis = "Počinješ da briješ... 😤"
        emoji = "😤"
    elif nivo <= 15:
        opis = "Ozbiljno si ljubomoran/a! 😡"
        emoji = "😡"
    else:
        opis = "MAKSIMALNA LJUBOMORA! Razgovaraj s partnerom! 🔥"
        emoji = "🔥"

    partner      = ctx.guild.get_member(p["partner_id"])
    partner_name = partner.mention if partner else f"<@{p['partner_id']}>"

    e = discord.Embed(title=f"{emoji} Ljubomora!", color=_LP)
    e.description = (
        f"> **{ctx.author.mention}** je ljubomoran/a na **{partner_name}**!\n"
        f">\n"
        f"> {opis}\n"
        f"> Nivo ljubomore: **{nivo}** 📊"
    )
    e.set_footer(text=f"{BOT_NAME} {VERSION}")
    await ctx.send(embed=e)

# ══════════════════════════════════════════════
#   .djeca — Virtualna porodica
# ══════════════════════════════════════════════
@bot.command(name="djeca")
async def djeca(ctx: commands.Context):
    if not await check_kanal(ctx, "ljubav"): return
    data = load_data()
    p    = get_profile(data, ctx.author.id)

    if p["status"] is None or p["partner_id"] is None:
        await ctx.send(embed=discord.Embed(description="> ❌ Moraš biti u vezi ili braku da bi imao/la djecu!", color=_LP)); return

    djeca_lista = p.get("djeca", [])
    partner      = ctx.guild.get_member(p["partner_id"])
    partner_name = partner.mention if partner else f"<@{p['partner_id']}>"

    if not djeca_lista:
        e = discord.Embed(title="👨‍👩‍👧‍👦 Vaša porodica", color=_LP)
        e.description = (
            f"> {ctx.author.mention} & {partner_name}\n"
            f">\n"
            f"> Još nemate djece!\n"
            f"> Koristi `.beba` da dobiješ dijete! 🍼"
        )
    else:
        lista_txt = "\n".join(f"> {i+1}. {d['emoji']} **{d['ime']}** ({d['spol']}, {d['datum']})" for i, d in enumerate(djeca_lista))
        e = discord.Embed(title="👨‍👩‍👧‍👦 Vaša porodica", color=_LP)
        e.description = (
            f"> {ctx.author.mention} & {partner_name}\n"
            f">\n"
            f"> Vaša djeca ({len(djeca_lista)}):\n"
            + lista_txt
        )
    e.set_footer(text=f"{BOT_NAME} {VERSION}")
    await ctx.send(embed=e)

# ══════════════════════════════════════════════
#   .beba — Dobij dijete
# ══════════════════════════════════════════════
@bot.command(name="beba")
async def beba(ctx: commands.Context):
    if not await check_kanal(ctx, "ljubav"): return
    data = load_data()
    p    = get_profile(data, ctx.author.id)

    if p["status"] != "brak" or p["partner_id"] is None:
        await ctx.send(embed=discord.Embed(description="> ❌ Moraš biti u **braku** da bi dobio/la dijete!", color=_LP)); return

    if len(p.get("djeca", [])) >= 5:
        await ctx.send(embed=discord.Embed(description="> ❌ Već imate 5 djece — to je maksimum!", color=_LP)); return

    p_partner = get_profile(data, p["partner_id"])
    spol  = random.choice(["Dječak", "Djevojčica"])
    emoji = "👦" if spol == "Dječak" else "👧"
    ime   = random.choice(DJECIJA_IMENA_M if spol == "Dječak" else DJECIJA_IMENA_Z)
    datum = datetime.now(timezone.utc).strftime("%d.%m.%Y")

    dijete = {"ime": ime, "spol": spol, "emoji": emoji, "datum": datum}
    if "djeca" not in p:
        p["djeca"] = []
    p["djeca"].append(dijete)
    if "djeca" not in p_partner:
        p_partner["djeca"] = []
    p_partner["djeca"].append(dijete)

    p["xp"]         = p.get("xp", 0) + 20
    p_partner["xp"] = p_partner.get("xp", 0) + 20
    save_data(data)

    partner      = ctx.guild.get_member(p["partner_id"])
    partner_name = partner.mention if partner else f"<@{p['partner_id']}>"

    e = discord.Embed(title=f"{emoji} Dobrodošli roditelji!", color=_LP)
    e.description = (
        f"> **{ctx.author.mention}** i **{partner_name}**\n"
        f"> dobili su dijete!\n"
        f">\n"
        f"> {emoji} **{ime}** ({spol})\n"
        f"> Datum: **{datum}**\n"
        f">\n"
        f"> ⭐ **+20 XP** za oboje!"
    )
    e.set_footer(text=f"{BOT_NAME} {VERSION}")
    await ctx.send(embed=e)

# ══════════════════════════════════════════════
#   .izlet — Idite na dejt
# ══════════════════════════════════════════════
@bot.command(name="izlet")
async def izlet(ctx: commands.Context):
    if not await check_kanal(ctx, "ljubav"): return
    data = load_data()
    p    = get_profile(data, ctx.author.id)

    if p["status"] is None or p["partner_id"] is None:
        await ctx.send(embed=discord.Embed(description="> ❌ Moraš biti u vezi za izlet!", color=_LP)); return

    proslo = now_ts() - p.get("last_izlet", 0)
    if proslo < 12 * 3600:
        pre = 12 * 3600 - proslo
        await ctx.send(embed=discord.Embed(
            description=f"> ⏳ Sljedeći izlet za **{pre//3600}h {(pre%3600)//60}m**.",
            color=_LP
        )); return

    IZLETI = [
        ("🎡 Lunapark", "Vrtite se na vrtuljku i jedete šećernu vatu!"),
        ("🍕 Pizzeria", "Uživate u pizzi i razgovoru!"),
        ("🏖️ Plaža",   "Šetate po pijesku i gledate zalazak sunca!"),
        ("🎬 Kino",     "Gledate romantični film zajedno!"),
        ("🎭 Pozorište","Uživate u predstavi!"),
        ("🌳 Park",     "Šetate kroz park i hranjite patke!"),
        ("☕ Kafić",    "Pijete kafu i razgovarate satima!"),
        ("🏔️ Planina",  "Perete se na planinu i divite se prirodi!"),
    ]
    naziv, opis_str = random.choice(IZLETI)
    bonus = random.randint(30, 60)

    p["love"]      = p.get("love", 0) + bonus
    p["xp"]        = p.get("xp", 0) + 15
    p["last_izlet"] = now_ts()
    p_partner      = get_profile(data, p["partner_id"])
    p_partner["love"]      = p_partner.get("love", 0) + bonus
    p_partner["xp"]        = p_partner.get("xp", 0) + 15
    p_partner["last_izlet"] = now_ts()
    save_data(data)

    partner      = ctx.guild.get_member(p["partner_id"])
    partner_name = partner.mention if partner else f"<@{p['partner_id']}>"

    e = discord.Embed(title=f"🗺️ Izlet — {naziv}", color=_LP)
    e.description = (
        f"> **{ctx.author.mention}** i **{partner_name}** idu na izlet!\n"
        f">\n"
        f"> {opis_str}\n"
        f">\n"
        f"> 💗 **+{bonus}** bodova ljubavi!\n"
        f"> ⭐ **+15 XP** za oboje!"
    )
    e.set_footer(text=f"Cooldown: 12h • {BOT_NAME} {VERSION}")
    await ctx.send(embed=e)

# ══════════════════════════════════════════════
#   .vecera — Romantična večera
# ══════════════════════════════════════════════
@bot.command(name="vecera")
async def vecera(ctx: commands.Context):
    if not await check_kanal(ctx, "ljubav"): return
    data = load_data()
    p    = get_profile(data, ctx.author.id)

    if p["status"] is None or p["partner_id"] is None:
        await ctx.send(embed=discord.Embed(description="> ❌ Moraš biti u vezi za večeru!", color=_LP)); return

    proslo = now_ts() - p.get("last_vecera", 0)
    if proslo < 8 * 3600:
        pre = 8 * 3600 - proslo
        await ctx.send(embed=discord.Embed(
            description=f"> ⏳ Sljedeća večera za **{pre//3600}h {(pre%3600)//60}m**.",
            color=_LP
        )); return

    VECERE = [
        ("🥩 Restoran", "Jedete filet mignon uz svjećice!"),
        ("🍝 Talijanska", "Pasta carbonara i vino!"),
        ("🍣 Sushi", "Japanski omakase doživljaj!"),
        ("🥗 Romantic picnic", "Piknik pod zvijezdama!"),
        ("🍲 Domaća kuhinja", "Babina recept — ništa bolje!"),
    ]
    naziv, opis_str = random.choice(VECERE)
    bonus = random.randint(40, 80)

    p["love"]      = p.get("love", 0) + bonus
    p["xp"]        = p.get("xp", 0) + 12
    p["last_vecera"] = now_ts()
    p_partner      = get_profile(data, p["partner_id"])
    p_partner["love"]       = p_partner.get("love", 0) + bonus
    p_partner["xp"]         = p_partner.get("xp", 0) + 12
    p_partner["last_vecera"] = now_ts()
    save_data(data)

    partner      = ctx.guild.get_member(p["partner_id"])
    partner_name = partner.mention if partner else f"<@{p['partner_id']}>"

    e = discord.Embed(title=f"🍽️ Romantična večera — {naziv}", color=_LP)
    e.description = (
        f"> **{ctx.author.mention}** i **{partner_name}**\n"
        f">\n"
        f"> {opis_str}\n"
        f">\n"
        f"> 💗 **+{bonus}** bodova ljubavi!\n"
        f"> ⭐ **+12 XP** za oboje!"
    )
    e.set_footer(text=f"Cooldown: 8h • {BOT_NAME} {VERSION}")
    await ctx.send(embed=e)

# ══════════════════════════════════════════════
#   .putovanje — Otputujte zajedno
# ══════════════════════════════════════════════
@bot.command(name="putovanje")
async def putovanje(ctx: commands.Context):
    if not await check_kanal(ctx, "ljubav"): return
    data = load_data()
    p    = get_profile(data, ctx.author.id)

    if p["status"] is None or p["partner_id"] is None:
        await ctx.send(embed=discord.Embed(description="> ❌ Moraš biti u vezi za putovanje!", color=_LP)); return

    proslo = now_ts() - p.get("last_putovanje", 0)
    if proslo < 24 * 3600:
        pre = 24 * 3600 - proslo
        await ctx.send(embed=discord.Embed(
            description=f"> ⏳ Sljedeće putovanje za **{pre//3600}h {(pre%3600)//60}m**.",
            color=_LP
        )); return

    DESTINACIJE = [
        ("🗼 Pariz", "Šetnja Champs-Elysées i večera s pogledom na Eiffelov toranj!"),
        ("🏖️ Maldivi", "Kristalno čisto more i bungalovi nad vodom!"),
        ("🏯 Tokio", "Sakura, sushi i neonska noć!"),
        ("🎭 Rim", "Kolizej, tjestenina i ljubav!"),
        ("🏔️ Alpи", "Skijaška avantura i topla čokolada!"),
        ("🌅 Santorini", "Bijele kuće i plavo more!"),
        ("🎰 Las Vegas", "Sjaj, zabava i spontana avantura!"),
        ("🌿 Bali", "Džungla, hramovi i mир!"),
    ]
    naziv, opis_str = random.choice(DESTINACIJE)
    bonus = random.randint(80, 150)

    p["love"]         = p.get("love", 0) + bonus
    p["xp"]           = p.get("xp", 0) + 25
    p["last_putovanje"] = now_ts()
    uspomena = {"naziv": naziv, "datum": datetime.now(timezone.utc).strftime("%d.%m.%Y")}
    if "uspomene" not in p:
        p["uspomene"] = []
    p["uspomene"].append(uspomena)

    p_partner = get_profile(data, p["partner_id"])
    p_partner["love"]         = p_partner.get("love", 0) + bonus
    p_partner["xp"]           = p_partner.get("xp", 0) + 25
    p_partner["last_putovanje"] = now_ts()
    if "uspomene" not in p_partner:
        p_partner["uspomene"] = []
    p_partner["uspomene"].append(uspomena)
    save_data(data)

    partner      = ctx.guild.get_member(p["partner_id"])
    partner_name = partner.mention if partner else f"<@{p['partner_id']}>"

    e = discord.Embed(title=f"✈️ Putovanje — {naziv}", color=_LP)
    e.description = (
        f"> **{ctx.author.mention}** i **{partner_name}** putuju!\n"
        f">\n"
        f"> {opis_str}\n"
        f">\n"
        f"> 💗 **+{bonus}** bodova ljubavi!\n"
        f"> ⭐ **+25 XP** za oboje!\n"
        f"> 📸 Uspomena dodana u album!"
    )
    e.set_footer(text=f"Cooldown: 24h • {BOT_NAME} {VERSION}")
    await ctx.send(embed=e)

# ══════════════════════════════════════════════
#   .album — Zajedničke uspomene
# ══════════════════════════════════════════════
@bot.command(name="album")
async def album(ctx: commands.Context):
    if not await check_kanal(ctx, "ljubav"): return
    data = load_data()
    p    = get_profile(data, ctx.author.id)

    if p["status"] is None or p["partner_id"] is None:
        await ctx.send(embed=discord.Embed(description="> ❌ Moraš biti u vezi da vidiš album!", color=_LP)); return

    uspomene = p.get("uspomene", [])
    partner      = ctx.guild.get_member(p["partner_id"])
    partner_name = partner.mention if partner else f"<@{p['partner_id']}>"

    e = discord.Embed(title="📸 Album uspomena", color=_LP)
    if not uspomene:
        e.description = (
            f"> {ctx.author.mention} & {partner_name}\n"
            f">\n"
            f"> Album je prazan! Koristite `.putovanje` da\n"
            f"> napravite prve uspomene! ✈️"
        )
    else:
        linije = [f"> 📍 **{u['naziv']}** — {u['datum']}" for u in uspomene[-10:]]
        e.description = (
            f"> {ctx.author.mention} & {partner_name}\n"
            f"> Ukupno uspomena: **{len(uspomene)}**\n"
            f">\n"
            + "\n".join(linije)
        )
    e.set_footer(text=f"{BOT_NAME} {VERSION}")
    await ctx.send(embed=e)

# ══════════════════════════════════════════════
#   .datum — Koliko ste zajedno
# ══════════════════════════════════════════════
@bot.command(name="datum")
async def datum(ctx: commands.Context):
    if not await check_kanal(ctx, "ljubav"): return
    data = load_data()
    p    = get_profile(data, ctx.author.id)

    if p["status"] is None or p["partner_id"] is None:
        await ctx.send(embed=discord.Embed(description="> ❌ Nisi u vezi ni braku!", color=_LP)); return

    partner      = ctx.guild.get_member(p["partner_id"])
    partner_name = partner.mention if partner else f"<@{p['partner_id']}>"

    veza_date = p.get("veza_date") or p.get("brak_date")
    if not veza_date:
        await ctx.send(embed=discord.Embed(description="> ❌ Datum veze nije zabilježen.", color=_LP)); return

    try:
        start = datetime.strptime(veza_date, "%d.%m.%Y").replace(tzinfo=timezone.utc)
        now   = datetime.now(timezone.utc)
        diff  = now - start
        dani  = diff.days
        mj    = dani // 30
        god   = dani // 365
    except Exception:
        await ctx.send(embed=discord.Embed(description="> ❌ Greška pri čitanju datuma.", color=_LP)); return

    e = discord.Embed(title="📅 Datum veze", color=_LP)
    e.description = (
        f"> {ctx.author.mention} & {partner_name}\n"
        f">\n"
        f"> Zajedno od: **{veza_date}**\n"
        f">\n"
        f"> ⏱️ **{dani} dana**\n"
        f"> 📅 **{mj} mjeseci**\n"
        f"> 🗓️ **{god} godina**"
    )
    e.set_footer(text=f"{BOT_NAME} {VERSION}")
    await ctx.send(embed=e)

# ══════════════════════════════════════════════
#   .godisnjica — Godišnjica
# ══════════════════════════════════════════════
@bot.command(name="godisnjica")
async def godisnjica(ctx: commands.Context):
    if not await check_kanal(ctx, "ljubav"): return
    data = load_data()
    p    = get_profile(data, ctx.author.id)

    if p["status"] is None or p["partner_id"] is None:
        await ctx.send(embed=discord.Embed(description="> ❌ Nisi u vezi ni braku!", color=_LP)); return

    partner      = ctx.guild.get_member(p["partner_id"])
    partner_name = partner.mention if partner else f"<@{p['partner_id']}>"

    veza_date = p.get("veza_date") or p.get("brak_date")
    if not veza_date:
        await ctx.send(embed=discord.Embed(description="> ❌ Datum veze nije zabilježen.", color=_LP)); return

    try:
        start = datetime.strptime(veza_date, "%d.%m.%Y").replace(tzinfo=timezone.utc)
        now   = datetime.now(timezone.utc)
        # Sljedeća godišnjica
        sljedeca = start.replace(year=now.year)
        if sljedeca <= now:
            sljedeca = sljedeca.replace(year=now.year + 1)
        preostalo = sljedeca - now
        d = preostalo.days
        h = preostalo.seconds // 3600
    except Exception:
        await ctx.send(embed=discord.Embed(description="> ❌ Greška pri čitanju datuma.", color=_LP)); return

    e = discord.Embed(title="🎂 Godišnjica", color=_LP)
    e.description = (
        f"> {ctx.author.mention} & {partner_name}\n"
        f">\n"
        f"> Veza od: **{veza_date}**\n"
        f"> Sljedeća godišnjica: **{sljedeca.strftime('%d.%m.%Y')}**\n"
        f">\n"
        f"> ⏰ Preostalo: **{d} dana i {h} sati**"
    )
    e.set_footer(text=f"{BOT_NAME} {VERSION}")
    await ctx.send(embed=e)

# ══════════════════════════════════════════════
#   .razina — Level vaše veze
# ══════════════════════════════════════════════
@bot.command(name="razina")
async def razina(ctx: commands.Context):
    if not await check_kanal(ctx, "ljubav"): return
    data = load_data()
    p    = get_profile(data, ctx.author.id)

    if p["status"] is None or p["partner_id"] is None:
        await ctx.send(embed=discord.Embed(description="> ❌ Nisi u vezi ni braku!", color=_LP)); return

    xp       = p.get("xp", 0)
    current, next_lvl = get_level(xp)
    partner      = ctx.guild.get_member(p["partner_id"])
    partner_name = partner.mention if partner else f"<@{p['partner_id']}>"

    linije = []
    for lvl in PARA_LEVELI:
        unlocked = xp >= lvl[1]
        current_tag = " ← VAŠA RAZINA" if lvl[0] == current[0] else ""
        lock = "✅" if unlocked else "🔒"
        linije.append(f"> `{lvl[0]:2}.` {lock} {lvl[2]} — {lvl[1]} XP{current_tag}")

    e = discord.Embed(title="📈 Level sistem za parove", color=_LP)
    e.description = (
        f"> {ctx.author.mention} & {partner_name}\n"
        f">\n"
        + "\n".join(linije)
    )
    e.add_field(name="Vaš XP",      value=f"> **{xp} XP**", inline=True)
    e.add_field(name="Vaša razina", value=f"> {current[2]}", inline=True)
    if next_lvl:
        e.add_field(name="Sljedeća razina", value=f"> {next_lvl[1] - xp} XP nedostaje", inline=True)
    e.set_footer(text=f"{BOT_NAME} {VERSION}")
    await ctx.send(embed=e)

# ══════════════════════════════════════════════
#   .statistika — Sve statistike para
# ══════════════════════════════════════════════
@bot.command(name="statistika")
async def statistika(ctx: commands.Context):
    if not await check_kanal(ctx, "ljubav"): return
    data = load_data()
    p    = get_profile(data, ctx.author.id)

    if p["status"] is None or p["partner_id"] is None:
        await ctx.send(embed=discord.Embed(description="> ❌ Nisi u vezi ni braku!", color=_LP)); return

    partner      = ctx.guild.get_member(p["partner_id"])
    partner_name = partner.mention if partner else f"<@{p['partner_id']}>"
    xp           = p.get("xp", 0)
    love         = p.get("love", 0)
    current, _   = get_level(xp)
    best         = get_best_prsten(love)
    djeca_br     = len(p.get("djeca", []))
    uspomene_br  = len(p.get("uspomene", []))

    stan_data = get_stan(data, ctx.author.id, p["partner_id"])
    sobe_br   = sum(1 for v in stan_data.get("sobe", {}).values() if v)

    status_txt = "U braku 💍" if p["status"] == "brak" else "U vezi ❤️"
    e = discord.Embed(title=f"📊 Statistika para", color=_LP)
    e.description = f"> {ctx.author.mention} & {partner_name}"
    e.add_field(name="Status",    value=f"> {status_txt}",        inline=True)
    e.add_field(name="Razina",    value=f"> {current[2]}",        inline=True)
    e.add_field(name="XP",        value=xp_bar(xp),               inline=False)
    e.add_field(name="Ljubav",    value=love_bar(love),            inline=False)
    e.add_field(name="Prsten",    value=f"> {best['emoji']} {best['naziv']}", inline=True)
    e.add_field(name="Djeca",     value=f"> **{djeca_br}**",       inline=True)
    e.add_field(name="Uspomene",  value=f"> **{uspomene_br}** putovanja", inline=True)
    e.add_field(name="Sobe",      value=f"> **{sobe_br}/6** soba", inline=True)

    if p.get("veza_date") or p.get("brak_date"):
        vd = p.get("veza_date") or p.get("brak_date")
        e.add_field(name="Zajedno od", value=f"> **{vd}**", inline=True)

    e.set_footer(text=f"{BOT_NAME} {VERSION}")
    await ctx.send(embed=e)

# ══════════════════════════════════════════════
#   .profil — Ljubavni profil
# ══════════════════════════════════════════════
STATUS_EMOJI = {None: "💔 Slobodan/na", "veza": "❤️ U vezi", "brak": "💍 U braku"}

@bot.command(name="profil")
async def profil(ctx: commands.Context, korisnik: discord.Member = None):
    if not await check_kanal(ctx, "ljubav"): return
    target = korisnik or ctx.author
    data   = load_data()
    p      = get_profile(data, target.id)
    love   = p.get("love", 0)
    xp     = p.get("xp", 0)
    best   = get_best_prsten(love)
    current, next_lvl = get_level(xp)

    e = discord.Embed(title="👤 Ljubavni profil", color=_LP)
    e.set_thumbnail(url=target.display_avatar.url)

    status_txt = STATUS_EMOJI.get(p["status"], "Nepoznato")
    e.description = (
        f"> **Član:** {target.mention}\n"
        f"> **Status:** {status_txt}\n"
        f"> **Prsten:** {best['emoji']} {best['naziv']}\n"
        f"> **Razina:** {current[2]}"
    )

    if p["partner_id"] is not None:
        partner      = ctx.guild.get_member(p["partner_id"])
        partner_name = partner.mention if partner else f"<@{p['partner_id']}>"
        e.description += f"\n> **Partner:** {partner_name}"
        if p["status"] == "veza"  and p.get("veza_date"):
            e.description += f"\n> **Zajedno od:** {p['veza_date']}"
        elif p["status"] == "brak" and p.get("brak_date"):
            e.description += f"\n> **Vjenčani od:** {p['brak_date']}"
        if p.get("prsten"):
            e.description += f"\n> **Bračni prsten:** {p.get('prsten')}"

    e.add_field(name="💗 Bodovi ljubavi", value=love_bar(love), inline=False)
    e.add_field(name="⭐ XP",             value=xp_bar(xp),     inline=False)

    proslo_sleep = now_ts() - p.get("last_sleep", 0)
    proslo_srce  = now_ts() - p.get("last_srce",  0)
    proslo_izl   = now_ts() - p.get("last_izlet",  0)
    proslo_put   = now_ts() - p.get("last_putovanje", 0)
    e.add_field(name=f"{CUSTOM_EMOJI['moon']} Spavanje", value=f"> {cd_txt(proslo_sleep, 8*3600)}", inline=True)
    e.add_field(name="❤️ Srce",       value=f"> {cd_txt(proslo_srce,  24*3600)}", inline=True)
    e.add_field(name="🗺️ Izlet",      value=f"> {cd_txt(proslo_izl,   12*3600)}", inline=True)
    e.add_field(name="✈️ Putovanje",  value=f"> {cd_txt(proslo_put,   24*3600)}", inline=True)

    djeca_br = len(p.get("djeca", []))
    if djeca_br > 0:
        e.add_field(name="👶 Djeca", value=f"> **{djeca_br}**", inline=True)

    e.set_footer(text=f"{BOT_NAME} {VERSION} • Ljubavni sistem")
    await ctx.send(embed=e)

# ══════════════════════════════════════════════
#   .razvod — Raskid/razvod
# ══════════════════════════════════════════════
RAZVOD_PORUKE = [
    "Ponekad putevi jednostavno krenu u različitim smjerovima... 💙",
    "Svaki kraj je i novi početak. 🌅",
    "Bolje je biti sretan/sretna sam/sama nego nesretan/nesretna s nekim. 💪",
]

@bot.command(name="razvod")
async def razvod(ctx: commands.Context):
    if not await check_kanal(ctx, "ljubav"): return
    data = load_data()
    p    = get_profile(data, ctx.author.id)

    if p["status"] is None or p["partner_id"] is None:
        await ctx.send(embed=discord.Embed(description="> ❌ Nisi u vezi ni braku!", color=_LP)); return

    partner      = ctx.guild.get_member(p["partner_id"])
    partner_name = partner.mention if partner else f"<@{p['partner_id']}>"
    tip          = "razvod" if p["status"] == "brak" else "raskid"

    e = discord.Embed(title=f"💔 Potvrda {tip}a", color=_LP)
    e.description = (
        f"> Da li si siguran/na da želiš **{tip}** s {partner_name}?\n"
        f">\n"
        f"> ⚠️ Svi bodovi ljubavi i prsten bit će izgubljeni!\n"
        f">\n"
        f"> ✅ Da, želim {tip}\n"
        f"> ❌ Odustani"
    )
    msg = await ctx.send(embed=e)
    await msg.add_reaction("✅")
    await msg.add_reaction("❌")

    def check(reaction, user):
        return user.id == ctx.author.id and str(reaction.emoji) in ["✅","❌"] and reaction.message.id == msg.id

    try:
        reaction, _ = await bot.wait_for("reaction_add", timeout=30.0, check=check)
    except asyncio.TimeoutError:
        await msg.edit(embed=discord.Embed(description="> ⏰ Potvrda istekla. Ništa nije promijenjeno.", color=_LP)); return

    if str(reaction.emoji) == "✅":
        pid       = p["partner_id"]
        p_partner = get_profile(data, pid)
        for pr in [p, p_partner]:
            pr.update({
                "partner_id": None, "status": None, "love": 0, "xp": 0,
                "last_sleep": 0, "last_srce": 0, "last_zagrljaj": 0,
                "last_poljubac": 0, "last_izlet": 0, "last_vecera": 0,
                "last_putovanje": 0, "last_obnova": 0,
                "veza_date": None, "brak_date": None, "prsten": None,
                "djeca": [], "ljubomora": 0, "uspomene": [],
            })
        data["stanovi"].pop(couple_key(ctx.author.id, pid), None)
        save_data(data)
        ok = discord.Embed(title=f"💔 {tip.capitalize()} je završen", color=_LP)
        ok.description = f"> *{random.choice(RAZVOD_PORUKE)}*\n>\n> Svi podaci su obrisani."
        await msg.edit(embed=ok)
    else:
        await msg.edit(embed=discord.Embed(description="> ✅ Odustao/la si. Ništa nije promijenjeno.", color=_LP))

# ══════════════════════════════════════════════
#   .stan — Pregled stana / kuće
# ══════════════════════════════════════════════
@bot.command(name="stan")
async def stan_cmd(ctx: commands.Context):
    if not await check_kanal(ctx, "ljubav"): return
    data = load_data()
    p    = get_profile(data, ctx.author.id)

    if p["status"] is None or p["partner_id"] is None:
        await ctx.send(embed=discord.Embed(description="> ❌ Nemaš partnera!", color=_LP)); return

    partner      = ctx.guild.get_member(p["partner_id"])
    partner_name = partner.mention if partner else f"<@{p['partner_id']}>"
    s            = get_stan(data, ctx.author.id, p["partner_id"])

    naslov = "🏠 Vaša kuća" if s.get("kuca_kupljena") else "🏠 Stan"
    e = discord.Embed(title=naslov, color=_LP)
    e.description = f"> {ctx.author.mention} & {partner_name}"

    # Sobe
    sobe_status = []
    SOBE_INFO = {
        "kuhinja":  ("🍳", "Kuhinja"),
        "spavaca":  ("🛏️", "Spavaća soba"),
        "kupatilo": ("🛁", "Kupatilo"),
        "vrt":      ("🌿", "Vrt"),
        "bazen":    ("🏊", "Bazen"),
        "garaza":   ("🏗️", "Garaža"),
    }
    sobe = s.get("sobe", {})
    for k, (emoji, naziv) in SOBE_INFO.items():
        status = "✅" if sobe.get(k) else "🔒"
        sobe_status.append(f"> {emoji} {naziv}: {status}")

    e.add_field(name="Sobe", value="\n".join(sobe_status), inline=False)
    sobe_br = sum(1 for v in sobe.values() if v)
    e.add_field(name="Kupljene sobe", value=f"> **{sobe_br}/6**", inline=True)

    if not s.get("kuca_kupljena"):
        e.add_field(name="💡 Savjet", value="> Kupi kuću sa `.kuca`\n> Opreмi sobe sa `.kupi soba_naziv`", inline=False)

    e.set_footer(text=f"{BOT_NAME} {VERSION}")
    await ctx.send(embed=e)

# ══════════════════════════════════════════════
#   .kuca — Kupi kuću
# ══════════════════════════════════════════════
@bot.command(name="kuca")
async def kuca(ctx: commands.Context):
    if not await check_kanal(ctx, "ljubav"): return
    data = load_data()
    p    = get_profile(data, ctx.author.id)

    if p["status"] is None or p["partner_id"] is None:
        await ctx.send(embed=discord.Embed(description="> ❌ Moraš biti u vezi da kupiš kuću!", color=_LP)); return

    s = get_stan(data, ctx.author.id, p["partner_id"])
    if s.get("kuca_kupljena"):
        await ctx.send(embed=discord.Embed(description="> ✅ Već imate kuću! Koristite `.stan` za pregled.", color=_LP)); return

    cijena = MARKET_ITEMS["kuca"]["cijena"]
    e_kupac = get_ekonomija(data, ctx.author.id)
    ukupno  = e_kupac["novac"] + e_kupac["banka"]

    if ukupno < cijena:
        e = discord.Embed(title="🏠 Kupovina kuće", color=_LP)
        e.description = (
            f"> 🏠 Cijena kuće: **{cijena:,} 💰**\n"
            f"> Tvoj novac: **{ukupno:,} 💰**\n"
            f"> Nedostaje: **{cijena - ukupno:,} 💰**\n"
            f">\n"
            f"> Zaradi novac sa `.rad` i `.plata`!"
        )
        await ctx.send(embed=e); return

    # Skini novac
    if e_kupac["novac"] >= cijena:
        e_kupac["novac"] -= cijena
    else:
        ostatak = cijena - e_kupac["novac"]
        e_kupac["novac"] = 0
        e_kupac["banka"] -= ostatak

    s["kuca_kupljena"] = True
    save_data(data)

    partner      = ctx.guild.get_member(p["partner_id"])
    partner_name = partner.mention if partner else f"<@{p['partner_id']}>"
    e = discord.Embed(title="🏠 Kuća kupljena!", color=_LP)
    e.description = (
        f"> **{ctx.author.mention}** i **{partner_name}** kupili su kuću!\n"
        f">\n"
        f"> 🏠 Platili ste: **{cijena:,} 💰**\n"
        f"> Sada opremite sobe sa `.soba` komandama!"
    )
    e.set_footer(text=f"{BOT_NAME} {VERSION}")
    await ctx.send(embed=e)

# ══════════════════════════════════════════════
#   .soba / .kuhinja / .spavaca / itd.
# ══════════════════════════════════════════════
async def kupi_sobu(ctx: commands.Context, soba_id: str):
    if not await check_kanal(ctx, "ljubav"): return
    data = load_data()
    p    = get_profile(data, ctx.author.id)

    if p["status"] is None or p["partner_id"] is None:
        await ctx.send(embed=discord.Embed(description="> ❌ Moraš biti u vezi da kupiš sobu!", color=_LP)); return

    s = get_stan(data, ctx.author.id, p["partner_id"])
    if not s.get("kuca_kupljena"):
        await ctx.send(embed=discord.Embed(description="> ❌ Prvo kupi kuću sa `.kuca`!", color=_LP)); return

    item = MARKET_ITEMS.get(soba_id)
    if not item:
        await ctx.send(embed=discord.Embed(description="> ❌ Nepoznata soba.", color=_LP)); return

    sobe = s.get("sobe", {})
    if sobe.get(soba_id):
        await ctx.send(embed=discord.Embed(
            description=f"> ✅ Već imate **{item['emoji']} {item['naziv']}**!",
            color=_LP
        )); return

    cijena  = item["cijena"]
    e_kupac = get_ekonomija(data, ctx.author.id)
    ukupno  = e_kupac["novac"] + e_kupac["banka"]

    if ukupno < cijena:
        e = discord.Embed(title=f"{item['emoji']} Kupovina sobe", color=_LP)
        e.description = (
            f"> Cijena: **{cijena:,} 💰**\n"
            f"> Tvoj novac: **{ukupno:,} 💰**\n"
            f"> Nedostaje: **{cijena - ukupno:,} 💰**"
        )
        await ctx.send(embed=e); return

    if e_kupac["novac"] >= cijena:
        e_kupac["novac"] -= cijena
    else:
        ostatak = cijena - e_kupac["novac"]
        e_kupac["novac"] = 0
        e_kupac["banka"] -= ostatak

    sobe[soba_id] = True
    s["sobe"] = sobe
    save_data(data)

    e = discord.Embed(title=f"{item['emoji']} Soba kupljena!", color=_LP)
    e.description = (
        f"> **{item['emoji']} {item['naziv']}** je dodana u vašu kuću!\n"
        f"> Platili ste: **{cijena:,} 💰**\n"
        f">\n"
        f"> *{item['opis']}*"
    )
    e.set_footer(text=f"{BOT_NAME} {VERSION}")
    await ctx.send(embed=e)

@bot.command(name="soba")
async def soba(ctx: commands.Context, naziv: str = None):
    if not await check_kanal(ctx, "ljubav"): return
    if naziv is None:
        data = load_data()
        p    = get_profile(data, ctx.author.id)
        if p["status"] is None or p["partner_id"] is None:
            await ctx.send(embed=discord.Embed(description="> ❌ Moraš biti u vezi!", color=_LP)); return
        s = get_stan(data, ctx.author.id, p["partner_id"])
        sobe = s.get("sobe", {})
        SOBE_INFO = {
            "kuhinja":  ("🍳", "Kuhinja",       500),
            "spavaca":  ("🛏️", "Spavaća soba",  400),
            "kupatilo": ("🛁", "Kupatilo",       300),
            "vrt":      ("🌿", "Vrt",            600),
            "bazen":    ("🏊", "Bazen",          2000),
            "garaza":   ("🏗️", "Garaža",         800),
        }
        linije = []
        for k, (emoji, naziv_s, cijena) in SOBE_INFO.items():
            status = "✅ Kupljeno" if sobe.get(k) else f"🔒 {cijena:,} 💰"
            linije.append(f"> {emoji} **{naziv_s}** — {status}")
        e = discord.Embed(title="🏠 Sobe u kući", color=_LP)
        e.description = "\n".join(linije)
        e.set_footer(text="Kupi sobu sa .kuhinja, .spavaca, .kupatilo, .vrt, .bazen ili .garaza")
        await ctx.send(embed=e)
        return
    await kupi_sobu(ctx, naziv.lower())

@bot.command(name="kuhinja")
async def kuhinja(ctx): await kupi_sobu(ctx, "kuhinja")

@bot.command(name="spavaca")
async def spavaca(ctx): await kupi_sobu(ctx, "spavaca")

@bot.command(name="kupatilo")
async def kupatilo(ctx): await kupi_sobu(ctx, "kupatilo")

@bot.command(name="vrt")
async def vrt(ctx): await kupi_sobu(ctx, "vrt")

@bot.command(name="bazen")
async def bazen(ctx): await kupi_sobu(ctx, "bazen")

@bot.command(name="garaza")
async def garaza(ctx): await kupi_sobu(ctx, "garaza")

# ══════════════════════════════════════════════
#   .namjestaj — Kupi namještaj
# ══════════════════════════════════════════════
@bot.command(name="namjestaj")
async def namjestaj(ctx: commands.Context):
    if not await check_kanal(ctx, "ljubav"): return
    NAMJESTAJ_LISTA = [
        ("🛋️", "Sofa",        200),
        ("🪑", "Stolica",      50),
        ("🖼️", "Slika",        80),
        ("🪴", "Biljka",       30),
        ("📺", "Televizor",    400),
        ("🎮", "PlayStation",  600),
        ("🎸", "Gitara",       350),
        ("📚", "Polica knjiga", 150),
    ]
    data    = load_data()
    e_kupac = get_ekonomija(data, ctx.author.id)
    linije  = [f"> {emoji} **{naziv}** — {cijena:,} 💰" for emoji, naziv, cijena in NAMJESTAJ_LISTA]
    e = discord.Embed(title="🪑 Namještaj", color=_LP)
    e.description = "\n".join(linije) + f"\n>\n> Tvoj novac: **{e_kupac['novac']:,} 💰**"
    e.set_footer(text=f"Koristi .market za kupovinu • {BOT_NAME} {VERSION}")
    await ctx.send(embed=e)

# ══════════════════════════════════════════════
#   EKONOMIJA
# ══════════════════════════════════════════════

@bot.command(name="rad")
async def rad(ctx: commands.Context):
    data = load_data()
    e    = get_ekonomija(data, ctx.author.id)

    proslo = now_ts() - e.get("last_rad", 0)
    posao  = e.get("posao", "Nezaposlen")

    posao_info = None
    for p_info in POSLOVI:
        if p_info["naziv"] == posao:
            posao_info = p_info
            break

    if posao == "Nezaposlen" or not posao_info:
        # Auto-assign a job
        posao_info = POSLOVI[0]
        e["posao"] = posao_info["naziv"]
        save_data(data)

    cooldown = posao_info.get("rad_min", 60) * 60

    if proslo < cooldown:
        pre = cooldown - proslo
        await ctx.send(embed=discord.Embed(
            description=f"> ⏳ Već si radio/la! Sljedeće radno mjesto za **{pre//3600}h {(pre%3600)//60}m {pre%60}s**.",
            color=_LP
        )); return

    zarada = random.randint(posao_info["plata_min"], posao_info["plata_max"])
    e["novac"]   = e.get("novac", 0) + zarada
    e["last_rad"] = now_ts()
    save_data(data)

    RAD_PORUKE = [
        f"Odlično si obavio/la posao!",
        f"Šef je zadovoljan!",
        f"Produktivan radni dan!",
        f"Marljivo si radio/la!",
    ]
    emb = discord.Embed(title="💼 Rad", color=_LP)
    emb.description = (
        f"> 💼 Posao: **{e['posao']}**\n"
        f"> {random.choice(RAD_PORUKE)}\n"
        f">\n"
        f"> 💰 Zaradio/la si: **{zarada:,} 💰**\n"
        f"> 💳 Ukupno: **{e['novac']:,} 💰**"
    )
    emb.set_footer(text=f"Cooldown: {posao_info['rad_min']}min • {BOT_NAME} {VERSION}")
    await ctx.send(embed=emb)

@bot.command(name="plata")
async def plata(ctx: commands.Context):
    data = load_data()
    e    = get_ekonomija(data, ctx.author.id)

    proslo = now_ts() - e.get("last_plata", 0)
    if proslo < 24 * 3600:
        pre = 24 * 3600 - proslo
        await ctx.send(embed=discord.Embed(
            description=f"> ⏳ Sljedeća plata za **{pre//3600}h {(pre%3600)//60}m**.",
            color=_LP
        )); return

    posao = e.get("posao", "Nezaposlen")
    posao_info = next((p for p in POSLOVI if p["naziv"] == posao), POSLOVI[0])
    plata_iznos = posao_info["plata_max"] * 5

    e["novac"]     = e.get("novac", 0) + plata_iznos
    e["last_plata"] = now_ts()
    save_data(data)

    emb = discord.Embed(title="💵 Dnevna plata!", color=_LP)
    emb.description = (
        f"> 💼 Posao: **{posao}**\n"
        f"> 💵 Primio/la si dnevnu platu: **{plata_iznos:,} 💰**\n"
        f"> 💳 Ukupno: **{e['novac']:,} 💰**"
    )
    emb.set_footer(text=f"Cooldown: 24h • {BOT_NAME} {VERSION}")
    await ctx.send(embed=emb)

@bot.command(name="novac")
async def novac(ctx: commands.Context, korisnik: discord.Member = None):
    target = korisnik or ctx.author
    data   = load_data()
    e      = get_ekonomija(data, target.id)

    emb = discord.Embed(title="💰 Novčanik", color=_LP)
    emb.description = (
        f"> **Član:** {target.mention}\n"
        f"> 💳 Gotovina: **{e['novac']:,} 💰**\n"
        f"> 🏦 Banka: **{e['banka']:,} 💰**\n"
        f"> 💎 Ukupno: **{e['novac'] + e['banka']:,} 💰**\n"
        f">\n"
        f"> 💼 Posao: **{e.get('posao','Nezaposlen')}**"
    )
    emb.set_thumbnail(url=target.display_avatar.url)
    emb.set_footer(text=f"{BOT_NAME} {VERSION}")
    await ctx.send(embed=emb)

@bot.command(name="banka")
async def banka_cmd(ctx: commands.Context):
    data = load_data()
    e    = get_ekonomija(data, ctx.author.id)

    emb = discord.Embed(title="🏦 Banka", color=_LP)
    emb.description = (
        f"> 🏦 Stanje na računu: **{e['banka']:,} 💰**\n"
        f"> 💳 Gotovina: **{e['novac']:,} 💰**\n"
        f">\n"
        f"> Koristite `.uplati <iznos>` ili `.podigni <iznos>`"
    )
    emb.set_footer(text=f"{BOT_NAME} {VERSION}")
    await ctx.send(embed=emb)

@bot.command(name="uplati")
async def uplati(ctx: commands.Context, iznos: int = None):
    if iznos is None or iznos <= 0:
        await ctx.send(embed=discord.Embed(description="> ❌ Navedi iznos: `.uplati 500`", color=_LP)); return
    data = load_data()
    e    = get_ekonomija(data, ctx.author.id)

    if e["novac"] < iznos:
        await ctx.send(embed=discord.Embed(
            description=f"> ❌ Nemaš dovoljno gotovine! Imaš **{e['novac']:,} 💰**.",
            color=_LP
        )); return

    e["novac"] -= iznos
    e["banka"] = e.get("banka", 0) + iznos
    save_data(data)

    emb = discord.Embed(title="🏦 Uplata", color=_LP)
    emb.description = (
        f"> 💰 Uplaćeno: **{iznos:,} 💰** u banku\n"
        f"> 💳 Gotovina: **{e['novac']:,} 💰**\n"
        f"> 🏦 Banka: **{e['banka']:,} 💰**"
    )
    emb.set_footer(text=f"{BOT_NAME} {VERSION}")
    await ctx.send(embed=emb)

@bot.command(name="podigni")
async def podigni(ctx: commands.Context, iznos: int = None):
    if iznos is None or iznos <= 0:
        await ctx.send(embed=discord.Embed(description="> ❌ Navedi iznos: `.podigni 500`", color=_LP)); return
    data = load_data()
    e    = get_ekonomija(data, ctx.author.id)

    if e.get("banka", 0) < iznos:
        await ctx.send(embed=discord.Embed(
            description=f"> ❌ Nemaš dovoljno u banci! Imaš **{e.get('banka',0):,} 💰**.",
            color=_LP
        )); return

    e["banka"]  = e.get("banka", 0) - iznos
    e["novac"] += iznos
    save_data(data)

    emb = discord.Embed(title="🏦 Podizanje", color=_LP)
    emb.description = (
        f"> 💰 Podignuto: **{iznos:,} 💰** iz banke\n"
        f"> 💳 Gotovina: **{e['novac']:,} 💰**\n"
        f"> 🏦 Banka: **{e['banka']:,} 💰**"
    )
    emb.set_footer(text=f"{BOT_NAME} {VERSION}")
    await ctx.send(embed=emb)

@bot.command(name="transfer")
async def transfer(ctx: commands.Context, target: discord.Member = None, iznos: int = None):
    if target is None or iznos is None or iznos <= 0:
        await ctx.send(embed=discord.Embed(description="> ❌ Koristi: `.transfer @Korisnik 500`", color=_LP)); return
    if target.id == ctx.author.id:
        await ctx.send(embed=discord.Embed(description="> ❌ Ne možeš transferovati samom sebi!", color=_LP)); return

    data    = load_data()
    e_from  = get_ekonomija(data, ctx.author.id)
    e_to    = get_ekonomija(data, target.id)

    if e_from["novac"] < iznos:
        await ctx.send(embed=discord.Embed(
            description=f"> ❌ Nemaš dovoljno gotovine! Imaš **{e_from['novac']:,} 💰**.",
            color=_LP
        )); return

    e_from["novac"] -= iznos
    e_to["novac"]   += iznos
    save_data(data)

    emb = discord.Embed(title="💸 Transfer", color=_LP)
    emb.description = (
        f"> **{ctx.author.mention}** → **{target.mention}**\n"
        f">\n"
        f"> 💰 Poslano: **{iznos:,} 💰**\n"
        f"> Tvoja gotovina: **{e_from['novac']:,} 💰**"
    )
    emb.set_footer(text=f"{BOT_NAME} {VERSION}")
    await ctx.send(embed=emb)

@bot.command(name="market")
async def market(ctx: commands.Context):
    data = load_data()
    e    = get_ekonomija(data, ctx.author.id)

    kategorije = {}
    for item_id, item in MARKET_ITEMS.items():
        kat = item.get("kategorija", "ostalo")
        if kat not in kategorije:
            kategorije[kat] = []
        kategorije[kat].append((item_id, item))

    KAT_NAZIVI = {
        "poklon":     "🎁 Pokloni",
        "luksuz":     "💎 Luksuz",
        "nekretnina": "🏠 Nekretnine",
        "soba":       "🛋️ Sobe",
        "ostalo":     "📦 Ostalo",
    }

    emb = discord.Embed(title="🛒 Tržište", color=_LP)
    for kat, stavke in kategorije.items():
        linije = [f"> `{iid}` {item['emoji']} **{item['naziv']}** — {item['cijena']:,} 💰" for iid, item in stavke]
        emb.add_field(name=KAT_NAZIVI.get(kat, kat), value="\n".join(linije), inline=False)
    emb.add_field(name="💳 Tvoj novac", value=f"> **{e['novac']:,} 💰** gotovina\n> **{e['banka']:,} 💰** banka", inline=False)
    emb.set_footer(text=f"Kupuj sa .kupi <naziv> • Prodaj sa .prodaj <naziv> • {BOT_NAME} {VERSION}")
    await ctx.send(embed=emb)

@bot.command(name="kupi")
async def kupi(ctx: commands.Context, item_id: str = None):
    if item_id is None:
        await ctx.send(embed=discord.Embed(description="> ❌ Navedi predmet: `.kupi ruza`\n> Pogledaj tržište sa `.market`", color=_LP)); return

    item_id = item_id.lower()
    item = MARKET_ITEMS.get(item_id)
    if not item:
        await ctx.send(embed=discord.Embed(description=f"> ❌ Predmet **{item_id}** nije pronađen. Pogledaj `.market`!", color=_LP)); return

    data   = load_data()
    e_data = get_ekonomija(data, ctx.author.id)

    if item.get("kategorija") == "soba":
        await kupi_sobu(ctx, item_id)
        return

    if item.get("kategorija") == "nekretnina" and item_id == "kuca":
        await ctx.invoke(kuca)
        return

    if e_data["novac"] < item["cijena"]:
        emb = discord.Embed(title="❌ Nemaš dovoljno novca", color=_LP)
        emb.description = (
            f"> {item['emoji']} **{item['naziv']}** — {item['cijena']:,} 💰\n"
            f"> Tvoj novac: **{e_data['novac']:,} 💰**\n"
            f"> Nedostaje: **{item['cijena'] - e_data['novac']:,} 💰**"
        )
        await ctx.send(embed=emb); return

    e_data["novac"] -= item["cijena"]
    inv = e_data.get("inventar", {})
    inv[item_id] = inv.get(item_id, 0) + 1
    e_data["inventar"] = inv
    save_data(data)

    emb = discord.Embed(title=f"{item['emoji']} Kupljeno!", color=_LP)
    emb.description = (
        f"> Kupio/la si **{item['emoji']} {item['naziv']}**!\n"
        f"> Platili ste: **{item['cijena']:,} 💰**\n"
        f"> Gotovina: **{e_data['novac']:,} 💰**\n"
        f">\n"
        f"> *{item['opis']}*"
    )
    emb.set_footer(text=f"{BOT_NAME} {VERSION}")
    await ctx.send(embed=emb)

@bot.command(name="pokloni")
async def pokloni_cmd(ctx: commands.Context, target: discord.Member = None, item_id: str = None):
    if target is None or item_id is None:
        await ctx.send(embed=discord.Embed(description="> ❌ Koristi: `.pokloni @Korisnik ruza`\n> Pogledaj inventar sa `.novac`", color=_LP)); return

    item_id = item_id.lower()
    item = MARKET_ITEMS.get(item_id)
    if not item:
        await ctx.send(embed=discord.Embed(description=f"> ❌ Predmet **{item_id}** nije pronađen.", color=_LP)); return

    data   = load_data()
    e_from = get_ekonomija(data, ctx.author.id)
    inv    = e_from.get("inventar", {})

    if inv.get(item_id, 0) < 1:
        await ctx.send(embed=discord.Embed(description=f"> ❌ Nemaš **{item['naziv']}** u inventaru!\n> Kupi ga sa `.kupi {item_id}`.", color=_LP)); return

    inv[item_id] -= 1
    if inv[item_id] == 0:
        del inv[item_id]
    e_from["inventar"] = inv

    e_to  = get_ekonomija(data, target.id)
    inv_t = e_to.get("inventar", {})
    inv_t[item_id] = inv_t.get(item_id, 0) + 1
    e_to["inventar"] = inv_t
    save_data(data)

    emb = discord.Embed(title=f"{item['emoji']} Poklon poslan!", color=_LP)
    emb.description = (
        f"> **{ctx.author.mention}** poklanja {item['emoji']} **{item['naziv']}**\n"
        f"> osobi **{target.mention}**!"
    )
    emb.set_footer(text=f"{BOT_NAME} {VERSION}")
    await ctx.send(embed=emb)

# ══════════════════════════════════════════════
#   Brze poklon komande
# ══════════════════════════════════════════════
async def brzi_poklon(ctx: commands.Context, target: discord.Member, item_id: str):
    if not await check_kanal(ctx, "ljubav"): return
    if target is None:
        await ctx.send(embed=discord.Embed(description=f"> ❌ Navedi korisnika: `.{item_id} @Korisnik`", color=_LP)); return
    item = MARKET_ITEMS.get(item_id, {})
    emoji = item.get("emoji", "🎁")
    naziv = item.get("naziv", item_id)
    e = discord.Embed(title=f"{emoji} Poklon!", color=_LP)
    e.description = f"> **{ctx.author.mention}** šalje {emoji} **{naziv}** osobi **{target.mention}**!\n> *S ljubavlju!* 💕"
    e.set_footer(text=f"{BOT_NAME} {VERSION}")
    await ctx.send(embed=e)

@bot.command(name="ruza")
async def ruza(ctx: commands.Context, target: discord.Member = None):
    await brzi_poklon(ctx, target, "ruza")

@bot.command(name="ogrlica")
async def ogrlica_cmd(ctx: commands.Context, target: discord.Member = None):
    await brzi_poklon(ctx, target, "ogrlica")

@bot.command(name="sat")
async def sat_cmd(ctx: commands.Context, target: discord.Member = None):
    await brzi_poklon(ctx, target, "sat")

@bot.command(name="parfem")
async def parfem_cmd(ctx: commands.Context, target: discord.Member = None):
    await brzi_poklon(ctx, target, "parfem")

@bot.command(name="auto")
async def auto_cmd(ctx: commands.Context, target: discord.Member = None):
    await brzi_poklon(ctx, target, "auto")

@bot.command(name="jahte")
async def jahte_cmd(ctx: commands.Context, target: discord.Member = None):
    await brzi_poklon(ctx, target, "jahta")

# ══════════════════════════════════════════════
#   RIBOLOV SISTEM
# ══════════════════════════════════════════════
@bot.command(name="pecanje")
async def pecanje(ctx: commands.Context):
    if not await check_kanal(ctx, "pecanje"): return
    data = load_data()
    r    = get_ribolov(data, ctx.author.id)

    proslo = now_ts() - r["last_pecanje"]
    if proslo < 30 * 60:
        pre = 30 * 60 - proslo
        await ctx.send(embed=discord.Embed(
            description=f"> ⏳ Već si pecao/la! Sljedeće pecanje za **{pre//60}m {pre%60}s**.",
            color=_LP
        )); return

    e = discord.Embed(title="🎣 Ribolov", color=_LP)
    e.description = f"> {random.choice(PECANJE_PORUKE)}"
    msg = await ctx.send(embed=e)
    await asyncio.sleep(2)

    if random.random() < 0.10:
        r["last_pecanje"] = now_ts()
        save_data(data)
        e.description = f"> 😅 {random.choice(PECANJE_PROMASI)}"
        await msg.edit(embed=e); return

    riba = pecaj_ribu()
    r["last_pecanje"] = now_ts()
    r["ukupno_riba"]  = r.get("ukupno_riba", 0) + 1
    inventar          = r.get("inventar", {})
    inventar[riba["id"]] = inventar.get(riba["id"], 0) + 1
    r["inventar"]     = inventar

    stara_rar = r.get("najrjedja")
    nova_rar  = riba["raritet"]
    if stara_rar is None or RARITET_POREDAK.index(nova_rar) > RARITET_POREDAK.index(stara_rar):
        r["najrjedja"] = nova_rar

    save_data(data)
    nivo, _ = ribar_nivo(r["ukupno_riba"])
    rar_emoji = RARITET_EMOJI.get(riba["raritet"], "")

    e = discord.Embed(title="🎣 Uhvatio/la si ribu!", color=_LP)
    e.description = (
        f"> {riba['emoji']} **{riba['naziv']}** uhvaćeno!\n"
        f">\n"
        f"> Raritet: {rar_emoji} **{riba['raritet']}**\n"
        f"> Vrijednost: **{riba['coins']} coina**\n"
        f">\n"
        f"> Ukupno riba: **{r['ukupno_riba']}** | Nivo ribara: **{nivo}**"
    )
    if riba["coins"] == 0:
        e.description += "\n> *(Đubre nema vrijednost)*"
    e.set_footer(text=f"Cooldown: 30min • {BOT_NAME} {VERSION}")
    await msg.edit(embed=e)

@bot.command(name="ribnjak")
async def ribnjak(ctx: commands.Context, korisnik: discord.Member = None):
    if not await check_kanal(ctx, "pecanje"): return
    target = korisnik or ctx.author
    data   = load_data()
    r      = get_ribolov(data, target.id)
    inv    = r.get("inventar", {})

    if not inv:
        await ctx.send(embed=discord.Embed(
            description=f"> 🎣 {target.mention} još nema riba u inventaru!",
            color=_LP
        )); return

    def riba_sortkey(rid):
        info = riba_po_id(rid)
        return RARITET_POREDAK.index(info["raritet"]) if info else -1

    linije = []
    ukupna_vr = 0
    for rid in sorted(inv.keys(), key=riba_sortkey, reverse=True):
        kolicina = inv[rid]
        info     = riba_po_id(rid)
        if info:
            rar_e  = RARITET_EMOJI.get(info["raritet"], "")
            vr     = info["coins"] * kolicina
            ukupna_vr += vr
            linije.append(f"> {info['emoji']} **{info['naziv']}** x{kolicina} — {rar_e} — **{vr} coina**")

    nivo, _ = ribar_nivo(r.get("ukupno_riba", 0))
    e = discord.Embed(title="🐠 Ribnjak", color=_LP)
    e.description = f"> **Član:** {target.mention}\n>\n" + "\n".join(linije)
    e.add_field(name="💰 Ukupna vrijednost", value=f"> **{ukupna_vr} coina**",         inline=True)
    e.add_field(name="🐟 Ukupno riba",       value=f"> **{r.get('ukupno_riba', 0)}**", inline=True)
    e.add_field(name="🎣 Nivo ribara",        value=f"> **{nivo}**",                    inline=True)
    e.set_footer(text=f"Koristi .prodaj da prodaš sve ribe • {BOT_NAME} {VERSION}")
    await ctx.send(embed=e)

@bot.command(name="prodaj")
async def prodaj(ctx: commands.Context):
    if not await check_kanal(ctx, "pecanje"): return
    data = load_data()
    r    = get_ribolov(data, ctx.author.id)
    inv  = r.get("inventar", {})

    if not inv:
        await ctx.send(embed=discord.Embed(description="> ❌ Nemaš riba za prodati!", color=_LP)); return

    ukupno  = 0
    detalji = []
    for rid, kolicina in inv.items():
        info = riba_po_id(rid)
        if info and info["coins"] > 0:
            zarada = info["coins"] * kolicina
            ukupno += zarada
            detalji.append(f"> {info['emoji']} {info['naziv']} x{kolicina} = **{zarada} coina**")

    r["coins"]    = r.get("coins", 0) + ukupno
    r["inventar"] = {}
    save_data(data)

    e = discord.Embed(title="💰 Riba prodana!", color=_LP)
    if detalji:
        e.description = "\n".join(detalji) + f"\n>\n> 💰 Ukupno zarade: **{ukupno} coina**\n> 🪙 Tvoji coini: **{r['coins']} coina**"
    else:
        e.description = "> Imao/la si samo đubre — zarade 0 coina.\n> Inventar je očišćen."
    e.set_footer(text=f"{BOT_NAME} {VERSION} • Ribolov sistem")
    await ctx.send(embed=e)

@bot.command(name="ribar")
async def ribar_profil(ctx: commands.Context, korisnik: discord.Member = None):
    if not await check_kanal(ctx, "pecanje"): return
    target = korisnik or ctx.author
    data   = load_data()
    r      = get_ribolov(data, target.id)

    ukupno_riba = r.get("ukupno_riba", 0)
    coins       = r.get("coins", 0)
    najrjedja   = r.get("najrjedja", "Ništa još")
    nivo, sl    = ribar_nivo(ukupno_riba)

    proslo = now_ts() - r.get("last_pecanje", 0)
    if proslo >= 30 * 60:
        cd = "✅ Dostupno"
    else:
        pre = 30 * 60 - proslo
        cd  = f"⏳ {pre//60}m {pre%60}s"

    nivo_max = 10
    pct      = min(nivo / nivo_max, 1.0)
    filled   = int(pct * 10)
    nivo_bar = "🟦" * filled + "⬜" * (10 - filled) + f" Nivo {nivo}/{nivo_max}"

    e = discord.Embed(title="🎣 Ribar profil", color=_LP)
    e.set_thumbnail(url=target.display_avatar.url)
    e.description = (
        f"> **Član:** {target.mention}\n"
        f"> **Nivo:** {nivo_bar}\n"
        f"> **Ukupno ulovljeno:** {ukupno_riba} riba\n"
        f"> **Coini:** {coins:,}\n"
        f"> **Najrjeđa ulovljena:** {RARITET_EMOJI.get(najrjedja, '')} {najrjedja}\n"
        f"> **Sljedeće pecanje:** {cd}"
    )
    if sl:
        e.description += f"\n> **Do sljedećeg nivoa:** {sl - ukupno_riba} riba"
    e.set_footer(text=f"{BOT_NAME} {VERSION} • Ribolov sistem")
    await ctx.send(embed=e)

# ══════════════════════════════════════════════
#   LEADERBOARDI
# ══════════════════════════════════════════════
@bot.command(name="topljubav")
async def topljubav(ctx: commands.Context):
    data  = load_data()
    rels  = data.get("relationships", {})
    lista = []
    seen  = set()

    for uid_str, p in rels.items():
        uid = int(uid_str)
        pid = p.get("partner_id")
        if pid and p.get("status"):
            ck = couple_key(uid, pid)
            if ck not in seen:
                seen.add(ck)
                m1 = ctx.guild.get_member(uid)
                m2 = ctx.guild.get_member(pid)
                if m1 and m2:
                    lista.append((m1.mention, m2.mention, p.get("love", 0)))

    lista.sort(key=lambda x: x[2], reverse=True)
    top = lista[:10]

    if not top:
        await ctx.send(embed=discord.Embed(description="> ❤️ Još nema parova na serveru!", color=_LP)); return

    medalje = ["🥇","🥈","🥉","4️⃣","5️⃣","6️⃣","7️⃣","8️⃣","9️⃣","🔟"]
    linije  = [f"> {medalje[i]} {n1} ❤️ {n2} — {love:,} bodova" for i, (n1, n2, love) in enumerate(top)]

    e = discord.Embed(title="❤️ Top Ljubavnih Parova", color=_LP)
    e.description = "\n".join(linije)
    e.set_footer(text=f"{BOT_NAME} {VERSION}")
    await ctx.send(embed=e)

@bot.command(name="topxp")
async def topxp(ctx: commands.Context):
    data  = load_data()
    rels  = data.get("relationships", {})
    lista = []
    seen  = set()

    for uid_str, p in rels.items():
        uid = int(uid_str)
        pid = p.get("partner_id")
        if pid and p.get("status"):
            ck = couple_key(uid, pid)
            if ck not in seen:
                seen.add(ck)
                m1 = ctx.guild.get_member(uid)
                m2 = ctx.guild.get_member(pid)
                if m1 and m2:
                    xp = p.get("xp", 0)
                    current, _ = get_level(xp)
                    lista.append((m1.mention, m2.mention, xp, current[2]))

    lista.sort(key=lambda x: x[2], reverse=True)
    top = lista[:10]

    if not top:
        await ctx.send(embed=discord.Embed(description="> ⭐ Još nema parova s XP-om!", color=_LP)); return

    medalje = ["🥇","🥈","🥉","4️⃣","5️⃣","6️⃣","7️⃣","8️⃣","9️⃣","🔟"]
    linije  = [f"> {medalje[i]} {n1} & {n2} — {xp:,} XP {lvl}" for i, (n1, n2, xp, lvl) in enumerate(top)]

    e = discord.Embed(title="⭐ Top XP Parova", color=_LP)
    e.description = "\n".join(linije)
    e.set_footer(text=f"{BOT_NAME} {VERSION}")
    await ctx.send(embed=e)

@bot.command(name="topbogati")
async def topbogati(ctx: commands.Context):
    data  = load_data()
    ekon  = data.get("ekonomija", {})
    lista = []

    for uid_str, e in ekon.items():
        try:
            member = ctx.guild.get_member(int(uid_str))
            if member:
                ukupno = e.get("novac", 0) + e.get("banka", 0)
                lista.append((member.mention, ukupno, e.get("posao", "?")))
        except Exception:
            pass

    lista.sort(key=lambda x: x[1], reverse=True)
    top = lista[:10]

    if not top:
        await ctx.send(embed=discord.Embed(description="> 💰 Još nema korisnika s novcem!", color=_LP)); return

    medalje = ["🥇","🥈","🥉","4️⃣","5️⃣","6️⃣","7️⃣","8️⃣","9️⃣","🔟"]
    linije  = [f"> {medalje[i]} {ime} — {ukupno:,} 💰 | {posao}" for i, (ime, ukupno, posao) in enumerate(top)]

    e = discord.Embed(title="💰 Top Bogatih", color=_LP)
    e.description = "\n".join(linije)
    e.set_footer(text=f"{BOT_NAME} {VERSION}")
    await ctx.send(embed=e)

@bot.command(name="topparovi")
async def topparovi(ctx: commands.Context):
    data  = load_data()
    rels  = data.get("relationships", {})
    lista = []
    seen  = set()

    for uid_str, p in rels.items():
        uid = int(uid_str)
        pid = p.get("partner_id")
        if pid and p.get("status") == "brak":
            ck = couple_key(uid, pid)
            if ck not in seen:
                seen.add(ck)
                m1 = ctx.guild.get_member(uid)
                m2 = ctx.guild.get_member(pid)
                if m1 and m2:
                    djeca_br = len(p.get("djeca", []))
                    lista.append((m1.mention, m2.mention, p.get("brak_date","?"), djeca_br))

    top = lista[:10]
    if not top:
        await ctx.send(embed=discord.Embed(description="> 💍 Još nema bračnih parova!", color=_LP)); return

    medalje = ["🥇","🥈","🥉","4️⃣","5️⃣","6️⃣","7️⃣","8️⃣","9️⃣","🔟"]
    linije  = [f"> {medalje[i]} {n1} 💍 {n2} — od {datum} | 👶 {djeca}" for i, (n1, n2, datum, djeca) in enumerate(top)]

    e = discord.Embed(title="💍 Bračni parovi", color=_LP)
    e.description = "\n".join(linije)
    e.set_footer(text=f"{BOT_NAME} {VERSION}")
    await ctx.send(embed=e)

@bot.command(name="topstanovi")
async def topstanovi(ctx: commands.Context):
    data   = load_data()
    stan_d = data.get("stanovi", {})
    lista  = []

    for ck, s in stan_d.items():
        if not s.get("kuca_kupljena"):
            continue
        ids = ck.split("_")
        if len(ids) == 2:
            m1 = ctx.guild.get_member(int(ids[0]))
            m2 = ctx.guild.get_member(int(ids[1]))
            if m1 and m2:
                sobe_br = sum(1 for v in s.get("sobe", {}).values() if v)
                lista.append((m1.mention, m2.mention, sobe_br))

    lista.sort(key=lambda x: x[2], reverse=True)
    top = lista[:10]

    if not top:
        await ctx.send(embed=discord.Embed(description="> 🏠 Još nema parova s kućom!", color=_LP)); return

    medalje = ["🥇","🥈","🥉","4️⃣","5️⃣","6️⃣","7️⃣","8️⃣","9️⃣","🔟"]
    linije  = [f"> {medalje[i]} {n1} & {n2} — {sobe}/6 soba" for i, (n1, n2, sobe) in enumerate(top)]

    e = discord.Embed(title="🏠 Top Stanovi/Kuće", color=_LP)
    e.description = "\n".join(linije)
    e.set_footer(text=f"{BOT_NAME} {VERSION}")
    await ctx.send(embed=e)

@bot.command(name="top-ribar")
async def top_ribar(ctx: commands.Context):
    if not await check_kanal(ctx, "pecanje"): return
    data  = load_data()
    lista = []

    for uid_str, r in data.get("ribolov", {}).items():
        try:
            member = ctx.guild.get_member(int(uid_str))
            if member:
                lista.append((member.mention, r.get("ukupno_riba", 0), r.get("coins", 0)))
        except Exception:
            pass

    lista.sort(key=lambda x: x[1], reverse=True)
    top = lista[:10]

    if not top:
        await ctx.send(embed=discord.Embed(description="> 🎣 Još nema ribara na serveru!", color=_LP)); return

    medalje = ["🥇","🥈","🥉","4️⃣","5️⃣","6️⃣","7️⃣","8️⃣","9️⃣","🔟"]
    linije  = [f"> {medalje[i]} {ime} — {ukupno} riba | {coins:,} coina" for i, (ime, ukupno, coins) in enumerate(top)]

    e = discord.Embed(title="🎣 Top 10 Ribara", color=_LP)
    e.description = "\n".join(linije)
    e.set_footer(text=f"{BOT_NAME} {VERSION} • Ribolov sistem")
    await ctx.send(embed=e)

# ══════════════════════════════════════════════
#   .pomoc — Sve komande
# ══════════════════════════════════════════════
def pomoc_pages():
    """Kreiraj tri stranice pomoći koje se mijenjaju u istoj Discord poruci."""
    return [
        discord.Embed(
            title="📖 Pomoć — Strana 1/3",
            description=(
                f"> **Prefix:** `{BOT_PREFIX}` | **Verzija:** {VERSION}\n\n"
                "> **Ljubavni sistem**\n"
                "> `.veza @Korisnik` — Prijedlog za vezu\n"
                "> `.profil [@Korisnik]` — Ljubavni profil\n"
                "> `.brak @Partner` — Prijedlog za brak\n"
                "> `.prsten [@Partner]` — Prikaži ili odaberi prsten\n"
                "> `.svadba` · `.obnova` · `.zakletva [tekst]`\n"
                "> `.razvod` · `.datum` · `.godisnjica` · `.ljubomora`\n"
                "> `.razina` · `.statistika` · `.djeca` · `.beba` · `.album`\n\n"
                "> **Ljubavne aktivnosti**\n"
                "> `.spavanje` · `.srce` · `.zagrljaj @Korisnik`\n"
                "> `.poljubac @Korisnik` · `.ples @Korisnik`\n"
                "> `.izlet` · `.vecera` · `.putovanje`"
            ),
            color=_LP,
        ),
        discord.Embed(
            title="📖 Pomoć — Strana 2/3",
            description=(
                "> **Pokloni**\n"
                "> `.poklon @Korisnik` — Slučajni poklon\n"
                "> `.cvijece` · `.cokolada` · `.ruza` · `.ogrlica`\n"
                "> `.sat` · `.parfem` · `.auto` · `.jahte`\n\n"
                "> **Ekonomija**\n"
                "> `.ekonomija` · `.rad` · `.plata` · `.novac`\n"
                "> `.banka` · `.uplati <iznos>` · `.podigni <iznos>`\n"
                "> `.transfer @Korisnik <iznos>` · `.market`\n"
                "> `.kupi <predmet>` · `.pokloni @Korisnik <predmet>`\n"
                "> `.casino coin <ulog>` · `.casino slot <ulog>`\n\n"
                "> **Kuća**\n"
                "> `.kuca` · `.stan` · `.soba` · `.namjestaj`\n"
                "> `.kuhinja` · `.spavaca` · `.kupatilo` · `.vrt` · `.bazen` · `.garaza`"
            ),
            color=_LP,
        ),
        discord.Embed(
            title="📖 Pomoć — Strana 3/3",
            description=(
                "> **Ribolov**\n"
                "> `.pecanje` · `.ribnjak [@Korisnik]` · `.prodaj` · `.ribar`\n\n"
                "> **Mini-igre**\n"
                "> `.counting 1` — Zajedničko brojanje\n"
                "> `.toplo-hladno [broj]` — Pogodi broj\n"
                "> `.kaladont [riječ]` — Igra riječima\n"
                "> `,-xo @Korisnik` ili `.xo @Korisnik` — XO duel na klik kroz dugmad\n"
                "> `.pijte` · `.film` · `.istina` · `.izazov`\n"
                "> `.ljubavni-test @Korisnik` · `.compatibility @Korisnik`\n\n"
                "> **Rang-liste**\n"
                "> `.topljubav` · `.topxp` · `.topbogati`\n"
                "> `.topparovi` · `.topstanovi` · `.top-ribar`\n\n"
                "> Klikni dugmad ispod poruke za promjenu stranice."
            ),
            color=_LP,
        ),
    ]

class PomocView(discord.ui.View):
    """Navigacija kroz pomoć u jednoj DM poruci."""
    def __init__(self, pages, user_id: int, current: int = 0):
        super().__init__(timeout=900)
        self.pages = pages
        self.user_id = user_id
        self.current = current
        self._refresh_buttons()

    def _refresh_buttons(self):
        for child in self.children:
            if isinstance(child, discord.ui.Button) and child.custom_id == "pomoc_page":
                child.label = f"{self.current + 1}/{len(self.pages)}"
                child.disabled = True
            elif isinstance(child, discord.ui.Button):
                child.disabled = False
        self.children[0].disabled = self.current == 0
        self.children[2].disabled = self.current == len(self.pages) - 1

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(
                "Ova navigacija pripada članu koji je zatražio pomoć.",
                ephemeral=True,
            )
            return False
        return True

    @discord.ui.button(
        label="Prethodna",
        emoji=CUSTOM_EMOJI["move"],
        style=discord.ButtonStyle.secondary,
        custom_id="pomoc_previous",
    )
    async def previous(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current -= 1
        self._refresh_buttons()
        await interaction.response.edit_message(embed=self.pages[self.current], view=self)

    @discord.ui.button(
        label="1/3",
        emoji=CUSTOM_EMOJI["grid"],
        style=discord.ButtonStyle.primary,
        custom_id="pomoc_page",
    )
    async def page(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()

    @discord.ui.button(
        label="Sljedeća",
        emoji=CUSTOM_EMOJI["move"],
        style=discord.ButtonStyle.secondary,
        custom_id="pomoc_next",
    )
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current += 1
        self._refresh_buttons()
        await interaction.response.edit_message(embed=self.pages[self.current], view=self)

    @discord.ui.button(
        label="Zatvori",
        emoji=CUSTOM_EMOJI["close"],
        style=discord.ButtonStyle.danger,
        custom_id="pomoc_close",
    )
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button):
        for child in self.children:
            child.disabled = True
        await interaction.response.edit_message(view=self)

async def send_pomoc_dm(ctx: commands.Context, embed: discord.Embed, view=None):
    """Pošalji pomoć u DM; ako Discord blokira DM, prikaži je u kanalu."""
    try:
        await ctx.author.send(embed=embed, view=view)
        return True
    except (discord.Forbidden, discord.NotFound):
        # Bot ne može zaobići korisnikove Discord privacy postavke. Umjesto
        # beskonačne opomene, pomoć ipak ostaje dostupna u kanalu.
        await ctx.send(
            "Discord trenutno ne dozvoljava DM poruke ovom korisniku, "
            "pa je pomoć prikazana ovdje.",
            embed=embed,
            view=None,
        )
        return False
    except discord.HTTPException as exc:
        # Ne šalji ponovo u kanal nakon nejasne mrežne greške: DM je možda
        # već stigao, a ponavljanje bi napravilo drugu vidljivu kopiju.
        print(f"[POMOC] DM slanje nije potvrđeno; bez ponovnog slanja: {exc}")
        return False

@bot.command(name="pomoc")
async def pomoc(ctx: commands.Context, stranica: str = "1"):
    global POMOC_BATCH_MODE
    if not POMOC_BATCH_MODE and not await check_pomoc_channel(ctx):
        return
    stranica = str(stranica).lower()
    if ctx.guild and not POMOC_BATCH_MODE:
        data = load_data()
        if not pomoc_allowed(data, ctx.guild.id, ctx.author.id):
            await send_pomoc_dm(ctx, discord.Embed(
                title="Pomoć je privremeno ograničena",
                description=(
                    "> Iskoristio/la si 3 prikaza pomoći u posljednjih 60 minuta.\n"
                    "> Sačekaj da se jedan prikaz oslobodi pa pokušaj ponovo."
                ),
                color=_LP,
            ))
            return
        save_data(data)

    # Nova verzija pomoći koristi jednu poruku i dugmad za listanje stranica.
    # Stari blokovi ispod ostaju kao kompatibilnost za tekstualne stranice, ali
    # ovaj povratak sprečava slanje tri odvojene poruke.
    if stranica in ("1", "2", "3", "osnovno", "brak", "ekonomija", "ribolov", "zabava"):
        pages = pomoc_pages()
        page_index = 0
        if stranica in ("2", "brak", "ekonomija"):
            page_index = 1
        elif stranica in ("3", "ribolov", "zabava"):
            page_index = 2
        view = PomocView(pages, ctx.author.id, page_index)
        await send_pomoc_dm(ctx, pages[page_index], view)
        return

    if stranica in ("2", "brak", "ekonomija"):
        e = discord.Embed(title="📖 Pomoc — Strana 2/3", color=_LP)
        e.add_field(name="💍 Brak & Porodica", value=(
            "> `.brak @Partner` — Prijedlog za brak\n"
            "> `.prsten @Partner` — Brak s prstenom\n"
            "> `.svadba` — Svadba ceremonija\n"
            "> `.obnova` — Obnovi zavjete (7d)\n"
            "> `.zakletva [tekst]` — Bračna zakletva\n"
            "> `.beba` — Dobij dijete\n"
            "> `.djeca` — Pregled porodice\n"
            "> `.razina` — Level vaše veze\n"
            "> `.statistika` — Sve statistike para\n"
            "> `.album` — Uspomene s putovanja"
        ), inline=False)
        e.add_field(name="💰 Ekonomija", value=(
            "> `.rad` — Radi za novac\n"
            "> `.plata` — Dnevna plata (24h)\n"
            "> `.novac [@Korisnik]` — Pregled novca\n"
            "> `.banka` — Stanje u banci\n"
            "> `.uplati <iznos>` — Uplati u banku\n"
            "> `.podigni <iznos>` — Podigni iz banke\n"
            "> `.transfer @Korisnik <iznos>` — Pošalji novac\n"
            "> `.market` — Tržište predmeta\n"
            "> `.kupi <predmet>` — Kupi predmet\n"
            "> `.pokloni @Korisnik <predmet>` — Pokloni iz inventara"
        ), inline=False)
        e.set_footer(text=f"Strana 2/3 • {BOT_NAME} {VERSION} • .pomoc 3 za više")
        await send_pomoc_dm(ctx, e)
        return

    if stranica in ("3", "ribolov", "zabava"):
        e = discord.Embed(title="📖 Pomoc — Strana 3/3", color=_LP)
        e.add_field(name="🏠 Stan & Kuća", value=(
            "> `.kuca` — Kupi kuću (10,000 💰)\n"
            "> `.stan` — Pregled kuće\n"
            "> `.soba` — Lista soba\n"
            "> `.kuhinja` `.spavaca` `.kupatilo` — Kupi sobu\n"
            "> `.vrt` `.bazen` `.garaza` — Kupi sobu\n"
            "> `.namjestaj` — Lista namještaja"
        ), inline=False)
        e.add_field(name="🎁 Brzi pokloni", value=(
            "> `.poklon @Korisnik` — Slučajni poklon\n"
            "> `.cvijece @Korisnik` — Pošalji cvijeće\n"
            "> `.cokolada @Korisnik` — Čokolada\n"
            "> `.ruza @Korisnik` `.ogrlica @Korisnik`\n"
            "> `.sat @Korisnik` `.parfem @Korisnik`\n"
            "> `.auto @Korisnik` `.jahte @Korisnik`"
        ), inline=False)
        e.add_field(name="🎣 Ribolov", value=(
            "> `.pecanje` — Idi na ribolov (30min)\n"
            "> `.ribnjak [@Korisnik]` — Inventar riba\n"
            "> `.prodaj` — Prodaj sve ribe za coine\n"
            "> `.ribar [@Korisnik]` — Ribolov profil\n"
            "> `.top-ribar` — Top 10 ribara"
        ), inline=False)
        e.add_field(name="🎮 Zabava", value=(
            "> `.zagrljaj @Korisnik` — Zagrljaj (+3 XP)\n"
            "> `.poljubac @Korisnik` — Poljubac (+5 XP)\n"
            "> `.ples @Korisnik` — Ples\n"
            "> `.pijte` — Nazdravite!\n"
            "> `.film` — Gledaj film\n"
            "> `.istina` — Pitanje istine\n"
            "> `.izazov` — Izazov\n"
            "> `.ljubavni-test @Korisnik` — Ljubavni test\n"
            "> `.compatibility @Korisnik` — Kompatibilnost"
        ), inline=False)
        e.add_field(name="🏆 Leaderboardi", value=(
            "> `.topljubav` `.topxp` `.topbogati`\n"
            "> `.topparovi` `.topstanovi` `.top-ribar`"
        ), inline=False)
        e.set_footer(text=f"Strana 3/3 • {BOT_NAME} {VERSION}")
        await send_pomoc_dm(ctx, e)
        return

    # Strana 1 (default)
    e = discord.Embed(title="📖 Pomoc — Strana 1/3", color=_LP)
    e.description = f"> **Prefix:** `{BOT_PREFIX}` | **Verzija:** {VERSION}"
    e.add_field(name="❤️ Ljubavni sistem", value=(
        "> `.veza @Korisnik` — Prijedlog za vezu\n"
        "> `.profil [@Korisnik]` — Ljubavni profil\n"
        "> `.razvod` — Raskid/razvod\n"
        "> `.datum` — Koliko ste zajedno\n"
        "> `.godisnjica` — Vijeme do godišnjice\n"
        "> `.ljubomora` — Nivo ljubomore"
    ), inline=False)
    e.add_field(name="💗 Bodovi ljubavi & XP", value=(
        "> `.spavanje` — +30-80 bodova (8h)\n"
        "> `.srce` — +100-200 bodova (24h)\n"
        "> `.zagrljaj @` — +3 XP (2h)\n"
        "> `.poljubac @` — +5 XP (1h)\n"
        "> `.izlet` — +30-60 bodova (12h)\n"
        "> `.vecera` — +40-80 bodova (8h)\n"
        "> `.putovanje` — +80-150 bodova (24h)"
    ), inline=False)
    e.add_field(name="⚙️ Admin komande", value=(
        "> `/setkanal ljubav #kanal` — Postavi kanal\n"
        "> `/setkanal pecanje #kanal` — Kanal za ribolov\n"
        "> `/ukloni-kanal ljubav` — Ukloni ograničenje\n"
        "> `/welcome-podesi` — Podesi welcome kanale\n"
        "> `/welcome-status` — Pregled welcome podešavanja\n"
        "> `/welcome-test` — Pošalji test poruku\n"
        "> `/welcome-iskljuci` — Isključi welcome sistem\n"
        "> `/info-podesi` — Podesi Info/GWS kanal\n"
        "> `/info-postavi` — Pošalji Info panel\n"
        "> `/info-status` — Pregled Info podešavanja"
    ), inline=False)
    e.set_footer(text=f"Strana 1/3 • {BOT_NAME} {VERSION} • .pomoc 2 | .pomoc 3 za više komandi")
    poslato_u_dm = await send_pomoc_dm(ctx, e)
    if poslato_u_dm and stranica in ("1", "osnovno"):
        # Jedan `.pomoc` šalje sva tri pregledna panela kao tri poruke.
        POMOC_BATCH_MODE = True
        try:
            await pomoc.callback(ctx, "2")
            await pomoc.callback(ctx, "3")
        finally:
            POMOC_BATCH_MODE = False

# ══════════════════════════════════════════════
#              IGRE — prefix komande
# ══════════════════════════════════════════════
# Prefix je uvijek ".". Stanje mini-igara je odvojeno po kanalu da se
# igre na različitim kanalima ne miješaju.
KALADONT_GAMES = {}
COUNTING_LOCKS = {}
HOT_COLD_GAMES = {}
PROCESSED_GAME_MESSAGE_IDS = set()
KALADONT_STICKER_FILES = (
    "game_sticker_kaladont.png",
    "kaladont_sticker_1.jpg",
    "kaladont_sticker_2.jpg",
)
GAME_STICKER_FILES = {
    "counting": ("game_sticker_counting.png", "game_sticker_trophy.png"),
    "toplo_hladno": (
        "game_sticker_toplo_hladno.png",
        "game_sticker_kaladont.png",
    ),
    "kaladont": KALADONT_STICKER_FILES,
    "casino": ("game_sticker_casino.png", "game_sticker_trophy.png"),
}
GAME_STICKER_ROTATION = {}

def game_embed(title: str, lines, footer: str = None):
    e = discord.Embed(title=title, color=_LP)
    e.description = "\n".join(lines)
    if footer:
        e.set_footer(text=footer)
    return e

XO_ACTIVE_GAMES = {}
XO_CREATE_LOCK = asyncio.Lock()
XO_DURATION_SECONDS = 120
XO_WIN_LINES = (
    (0, 1, 2), (3, 4, 5), (6, 7, 8),
    (0, 3, 6), (1, 4, 7), (2, 5, 8),
    (0, 4, 8), (2, 4, 6),
)

def games_menu_embed():
    return game_embed(
        "Mini-igre",
        [
            "> Izaberi dugme ispod za pravila i brzo pokretanje igre.",
            "> **XO** se igra direktno klikom na polja.",
            "> Ostale igre nastavljaju koristiti postojeće tekstualne komande.",
        ],
        "Prefix komandi: .",
    )

class GamesMenuView(discord.ui.View):
    """Klikabilni meni za postojeće mini-igre i novu XO igru."""

    def __init__(self):
        super().__init__(timeout=300)

    @discord.ui.button(label="XO", emoji="❌", style=discord.ButtonStyle.primary, row=0)
    async def xo_info(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(
            "Pokreni duel sa `,-xo @član`, `.xo @član` ili `/xo`. "
            "Svaka partija ima svoju tablu i traje najviše 2 minuta.",
            ephemeral=True,
        )

    @discord.ui.button(label="Casino", emoji="🎰", style=discord.ButtonStyle.secondary, row=0)
    async def casino_info(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(
            "Casino: `.casino coin 50` ili `.casino slot 50` "
            "(minimalni ulog je 10 novčića).",
            ephemeral=True,
        )

    @discord.ui.button(label="Counting", emoji="🔢", style=discord.ButtonStyle.secondary, row=0)
    async def counting_info(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(
            "Započni sa `.counting 1`; nakon toga članovi naizmjenično šalju sljedeći broj.",
            ephemeral=True,
        )

    @discord.ui.button(label="Toplo-hladno", emoji="🌡️", style=discord.ButtonStyle.secondary, row=1)
    async def hot_cold_info(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(
            "Započni rundu sa `.toplo-hladno`, pa pogađaj broj od 1 do 100.",
            ephemeral=True,
        )

    @discord.ui.button(label="Kaladont", emoji="🔤", style=discord.ButtonStyle.secondary, row=1)
    async def kaladont_info(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(
            "Započni sa `.kaladont`, zatim naizmjenično šaljite riječi "
            "koje počinju posljednja dva slova prethodne riječi.",
            ephemeral=True,
        )

class TicTacToeView(discord.ui.View):
    """XO tabla za dva člana; potezi se prave klikom na dugmad."""

    def __init__(self, player_x: discord.abc.User, player_o: discord.abc.User, channel_id: int):
        super().__init__(timeout=None)
        self.player_x = player_x
        self.player_o = player_o
        self.current_player = player_x
        self.channel_id = channel_id
        self.game_id = uuid.uuid4().hex[:12]
        self.deadline = asyncio.get_running_loop().time() + XO_DURATION_SECONDS
        self.expires_at = int(datetime.now(timezone.utc).timestamp()) + XO_DURATION_SECONDS
        self.board = [None] * 9
        self.finished = False
        self.expired = False
        self.result = None
        self.message = None
        self.expiry_task = None
        self.move_lock = asyncio.Lock()
        for index in range(9):
            button = discord.ui.Button(
                label=str(index + 1),
                style=discord.ButtonStyle.secondary,
                row=index // 3,
                custom_id=f"xo:{self.game_id}:{index}",
            )
            button.callback = self._make_callback(index)
            self.add_item(button)

    def make_embed(self):
        if self.expired:
            time_text = "isteklo"
        elif self.finished:
            time_text = "završeno"
        else:
            # Discord sam odbrojava relativni timestamp do isteka.
            time_text = f"<t:{self.expires_at}:R>"
        description = (
            f"> {self.player_x.mention} izazvao/la je {self.player_o.mention}\n"
            f"> ⏱️ Time: {time_text}"
        )
        # Bez naslova i dodatnih pravila: samo izazov i odbrojavanje.
        return discord.Embed(description=description, color=_LP)

    def start_expiry_timer(self):
        self.expiry_task = asyncio.create_task(self.expire_after_timeout())

    def cancel_expiry_timer(self):
        task = self.expiry_task
        if task and not task.done() and task is not asyncio.current_task():
            task.cancel()

    def _refresh_buttons(self):
        for button in self.children:
            if not isinstance(button, discord.ui.Button):
                continue
            index = int(button.custom_id.rsplit(":", 1)[-1])
            mark = self.board[index]
            button.label = mark or str(index + 1)
            button.style = (
                discord.ButtonStyle.primary if mark == "X"
                else discord.ButtonStyle.danger if mark == "O"
                else discord.ButtonStyle.secondary
            )
            button.disabled = self.finished or mark is not None

    def _make_callback(self, index: int):
        async def callback(interaction: discord.Interaction):
            await self._play(interaction, index)
        return callback

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id not in {self.player_x.id, self.player_o.id}:
            await interaction.response.send_message(
                "Ova XO partija je namijenjena samo označenim igračima.",
                ephemeral=True,
            )
            return False
        return True

    async def _play(self, interaction: discord.Interaction, index: int):
        async with self.move_lock:
            if self.finished:
                await interaction.response.send_message("Ova partija je završena.", ephemeral=True)
                return
            if asyncio.get_running_loop().time() >= self.deadline:
                self.finished = True
                self.expired = True
                self.result = "⏰ Vrijeme je isteklo — ova partija više ne važi."
                self._refresh_buttons()
                XO_ACTIVE_GAMES.pop(self.game_id, None)
                self.cancel_expiry_timer()
                await interaction.response.edit_message(embed=self.make_embed(), view=self)
                self.stop()
                return
            if interaction.user.id != self.current_player.id:
                await interaction.response.send_message("Sada je potez drugog igrača.", ephemeral=True)
                return
            if self.board[index] is not None:
                await interaction.response.send_message("To polje je već zauzeto.", ephemeral=True)
                return

            mark = "X" if interaction.user.id == self.player_x.id else "O"
            self.board[index] = mark
            winning_line = next(
                (line for line in XO_WIN_LINES if all(self.board[cell] == mark for cell in line)),
                None,
            )
            if winning_line:
                self.finished = True
                self.result = f"🏆 {interaction.user.mention} pobjeđuje kao **{mark}**!"
            elif all(self.board):
                self.finished = True
                self.result = "🤝 Neriješeno — puna tabla!"
            else:
                self.current_player = (
                    self.player_o if mark == "X" else self.player_x
                )

            self._refresh_buttons()
            await interaction.response.edit_message(embed=self.make_embed(), view=self)
            if self.finished:
                XO_ACTIVE_GAMES.pop(self.game_id, None)
                self.cancel_expiry_timer()
                if winning_line:
                    winner_embed = discord.Embed(
                        title="🏆 Pobjeda u XO!",
                        description=f"> {interaction.user.mention} je pobijedio/la!",
                        color=_LP,
                    )
                    try:
                        await self.message.channel.send(
                            embed=winner_embed,
                            allowed_mentions=discord.AllowedMentions(
                                users=[interaction.user],
                                replied_user=False,
                            ),
                        )
                    except discord.HTTPException as exc:
                        print(f"[XO] Nije poslat embed pobjednika: {exc}")
                self.stop()

    async def expire_after_timeout(self):
        try:
            remaining = max(
                0,
                self.deadline - asyncio.get_running_loop().time(),
            )
            await asyncio.sleep(remaining)
            async with self.move_lock:
                if self.finished:
                    return
                self.finished = True
                self.expired = True
                self.result = "⏰ Vrijeme je isteklo — ova partija više ne važi."
                self._refresh_buttons()
                XO_ACTIVE_GAMES.pop(self.game_id, None)
                if self.message:
                    try:
                        await self.message.edit(embed=self.make_embed(), view=self)
                    except discord.HTTPException as exc:
                        print(f"[XO] Ne mogu ažurirati istekli panel: {exc}")
                self.stop()
        except asyncio.CancelledError:
            return

async def post_xo_game(channel, player_x: discord.abc.User, player_o: discord.abc.User):
    """Objavi nezavisnu XO tablu; više partija može trajati u istom kanalu."""
    async with XO_CREATE_LOCK:
        view = TicTacToeView(player_x, player_o, channel.id)
        message = await channel.send(
            embed=view.make_embed(),
            view=view,
            allowed_mentions=discord.AllowedMentions.none(),
        )
        view.message = message
        XO_ACTIVE_GAMES[view.game_id] = view
        view.start_expiry_timer()
        return view

async def react_to_game_input(
    message: discord.Message,
    reply_text: str,
    emoji: str = "🔢",
):
    """Daj kratku emoji potvrdu za tekst u igri koja prima samo brojeve."""
    try:
        await message.add_reaction(emoji)
    except discord.Forbidden:
        try:
            await message.reply(
                reply_text,
                mention_author=False,
                allowed_mentions=discord.AllowedMentions.none(),
            )
        except discord.HTTPException as exc:
            print(f"[IGRE] Nije moguće odgovoriti na poruku {message.id}: {exc}")
    except discord.HTTPException as exc:
        # Ne šalji drugi odgovor nakon neizvjesne greške; Discord je možda
        # već prihvatio reakciju prije prekida veze.
        print(f"[IGRE] Reakcija nije potvrđena za poruku {message.id}: {exc}")

async def send_game_embed(
    ctx: commands.Context,
    embed: discord.Embed,
    game: str,
    *,
    reply: bool = False,
):
    """Pošalji jedan embed sa odgovarajućim stikerom za mini-igru."""
    filenames = GAME_STICKER_FILES.get(game, ())
    channel_key = f"{ctx.guild.id if ctx.guild else 0}:{ctx.channel.id}:{game}"
    image_index = GAME_STICKER_ROTATION.get(channel_key, 0)
    filename = filenames[image_index % len(filenames)] if filenames else None
    image_path = os.path.join(DATA_DIR, filename) if filename else None

    if image_path and os.path.isfile(image_path):
        embed.set_thumbnail(url=f"attachment://{filename}")
        file = discord.File(image_path, filename=filename)
        if reply and ctx.message:
            await ctx.reply(
                embed=embed,
                file=file,
                mention_author=False,
                allowed_mentions=discord.AllowedMentions.none(),
            )
        else:
            await ctx.send(
                embed=embed,
                file=file,
                allowed_mentions=discord.AllowedMentions.none(),
            )
        GAME_STICKER_ROTATION[channel_key] = (image_index + 1) % len(filenames)
        return

    print(f"[IGRE] Nedostaje stiker za igru {game}: {filename or 'nije podešen'}")
    if reply and ctx.message:
        await ctx.reply(
            embed=embed,
            mention_author=False,
            allowed_mentions=discord.AllowedMentions.none(),
        )
    else:
        await ctx.send(
            embed=embed,
            allowed_mentions=discord.AllowedMentions.none(),
        )

async def send_kaladont_embed(ctx: commands.Context, embed: discord.Embed):
    """Odgovori na riječ stikerom i embedom, uz samo jedno Discord slanje."""
    await send_game_embed(ctx, embed, "kaladont", reply=True)

def counting_embed(number: int, next_number: int = None, author_mention: str = None, error: str = None):
    """Embed za brojanje u stilu Discord reply kartice iz korisničkog primjera."""
    if error:
        description = (
            f"> ❌ {error}\n>\n"
            f"**Poslao/la:** {author_mention or 'Član'}"
        )
    else:
        description = (
            f"> ✅ **#{number}** · sljedeći: **{next_number}**\n>\n"
            f"**Brojao/la:** {author_mention or 'Član'}"
        )
    return discord.Embed(description=description, color=_LP)

async def send_counting_reply(ctx: commands.Context, embed: discord.Embed):
    """Odgovori direktno na poruku s brojem, umjesto slanja nepovezane poruke."""
    try:
        await send_game_embed(ctx, embed, "counting", reply=True)
    except discord.HTTPException as exc:
        # Ne pokušavaj drugo slanje: prvi odgovor je možda već stigao do Discorda.
        print(f"[COUNTING] Jedini reply nije uspio u kanalu {ctx.channel.id}: {exc}")

@bot.command(name="igre")
async def igre_prefix(ctx: commands.Context):
    """Prikaži klikabilni meni mini-igara."""
    await ctx.send(
        embed=games_menu_embed(),
        view=GamesMenuView(),
        allowed_mentions=discord.AllowedMentions.none(),
    )

@bot.command(name="xo", aliases=["-xo"])
async def xo_prefix(ctx: commands.Context, protivnik: discord.Member = None):
    """Pokreni XO duel koji se igra klikom na tablu."""
    if ctx.guild is None:
        await ctx.send("XO se može pokrenuti na Discord serveru.")
        return
    if protivnik is None:
        await ctx.send(
            "Upotreba: `,-xo @član` — izazovi člana na XO duel. "
            "Svaka partija traje najviše 2 minuta."
        )
        return
    if protivnik.id == ctx.author.id or protivnik.bot:
        await ctx.send("Izaberi drugog člana servera koji nije bot.")
        return
    view = await post_xo_game(ctx.channel, ctx.author, protivnik)
    if view is None:
        await ctx.send("XO tabla nije mogla biti pokrenuta. Pokušaj ponovo.")

@bot.tree.command(name="xo", description="Pokreni XO duel koji se igra klikom")
@app_commands.describe(protivnik="Član servera kojeg izazivaš")
async def xo_slash(interaction: discord.Interaction, protivnik: discord.Member):
    if interaction.guild is None or interaction.channel is None:
        await interaction.response.send_message(
            "XO se može pokrenuti na Discord serveru.",
            ephemeral=True,
        )
        return
    if protivnik.id == interaction.user.id or protivnik.bot:
        await interaction.response.send_message(
            "Izaberi drugog člana servera koji nije bot.",
            ephemeral=True,
        )
        return
    await interaction.response.defer(ephemeral=True)
    view = await post_xo_game(interaction.channel, interaction.user, protivnik)
    if view is None:
        await interaction.followup.send(
            "U ovom kanalu već postoji aktivna XO partija.",
            ephemeral=True,
        )
    else:
        await interaction.followup.send(
            f"XO tabla je postavljena za tebe i {protivnik.mention}.",
            ephemeral=True,
            allowed_mentions=discord.AllowedMentions.none(),
        )

@bot.command(name="ekonomija")
async def ekonomija_igra(ctx: commands.Context):
    data = load_data()
    wallet = get_ekonomija(data, ctx.author.id)
    e = game_embed(
        "💰 Ekonomija",
        [
            "> Upravljaj svojim novcem i inventarom.",
            "> ",
            f"> 💵 Gotovina: **{wallet.get('novac', 0):,}**",
            f"> 🏦 Banka: **{wallet.get('banka', 0):,}**",
            f"> 💼 Posao: **{wallet.get('posao', 'Nezaposlen')}**",
            "> ",
            "> Komande:",
            "> `.rad` · `.plata` · `.banka` · `.market`",
            "> `.uplati <iznos>` · `.podigni <iznos>` · `.transfer @korisnik <iznos>`",
        ],
        "Koristi .pomoc za sve komande",
    )
    await ctx.send(embed=e)

@bot.command(name="casino")
async def casino(ctx: commands.Context, igra: str = None, iznos: int = None):
    if not await check_kanal(ctx, "casino"):
        return
    if not igra:
        await send_game_embed(ctx, game_embed(
            "🎰 Casino",
            [
                "> Dobrodošao/la u casino!",
                "> ",
                "> `.casino coin <iznos>` — glava ili pismo",
                "> `.casino slot <iznos>` — slot mašina",
                "> Minimalni ulog: **10** novčića.",
            ],
            "Sretno!",
        ), "casino")
        return
    igra = igra.lower()
    if igra not in {"coin", "slot"}:
        await send_game_embed(
            ctx,
            game_embed("🎰 Casino", ["> ❌ Izaberi `coin` ili `slot`."], "Koristi .casino"),
            "casino",
        )
        return
    if iznos is None or iznos < 10:
        await send_game_embed(
            ctx,
            game_embed(
                "🎰 Casino",
                ["> ❌ Upiši ulog od najmanje **10** novčića."],
                "Primjer: .casino coin 50",
            ),
            "casino",
        )
        return
    data = load_data()
    wallet = get_ekonomija(data, ctx.author.id)
    novac = wallet.get("novac", 0)
    if iznos > novac:
        await send_game_embed(
            ctx,
            game_embed(
                "🎰 Casino",
                [f"> ❌ Nemaš dovoljno novca. Imaš **{novac:,}** novčića."],
                "Uplati ili zaradi novac",
            ),
            "casino",
        )
        return
    wallet["novac"] -= iznos
    if igra == "coin":
        izbor = random.choice(["glava", "pismo"])
        dobitak = iznos * 2 if izbor == random.choice(["glava", "pismo"]) else 0
        rezultat = f"🪙 Ispalo je **{izbor}**."
    else:
        simboli = ["🍒", "🍋", "🔔", "⭐", "💎"]
        rezultat_simbola = [random.choice(simboli) for _ in range(3)]
        rezultat = f"🎰 {' '.join(rezultat_simbola)}"
        dobitak = iznos * (5 if len(set(rezultat_simbola)) == 1 else 2 if len(set(rezultat_simbola)) == 2 else 0)
    wallet["novac"] += dobitak
    save_data(data)
    neto = dobitak - iznos
    await send_game_embed(
        ctx,
        game_embed(
            "🎰 Casino",
            [
                f"> {rezultat}",
                f"> {'✅ Dobitak' if dobitak else '❌ Nema dobitka'}: **{dobitak:,}**",
                f"> Rezultat: **{'+' if neto >= 0 else ''}{neto:,}** novčića",
            ],
            f"Stanje: {wallet['novac']:,}",
        ),
        "casino",
    )

@bot.command(name="counting")
async def counting(ctx: commands.Context, broj: int = None):
    if not await check_kanal(ctx, "counting"):
        return
    channel_id = ctx.channel.id
    guild_id = ctx.guild.id if ctx.guild else 0
    game_key = f"{guild_id}:{channel_id}"
    lock = COUNTING_LOCKS.setdefault(game_key, asyncio.Lock())
    async with lock:
        data = load_data()
        counting_data = data.setdefault("counting", {})
        if not isinstance(counting_data, dict):
            counting_data = data["counting"] = {}
        state = counting_data.setdefault(
            game_key,
            {"next": 1, "last_user_id": None},
        )
        if not isinstance(state, dict):
            state = counting_data[game_key] = {"next": 1, "last_user_id": None}
        expected = max(1, int(state.get("next", 1) or 1))
    if broj is None:
        await send_game_embed(
            ctx,
            discord.Embed(
                description=(
                    f"> 🔢 Sljedeći broj je **{expected}**.\n>\n"
                    "Pošalji samo broj u counting kanalu ili koristi "
                    "`.counting <broj>`."
                ),
                color=_LP,
            ),
            "counting",
        )
        return
    async with lock:
        # Učitaj ponovo unutar brave: dvije poruke u isto vrijeme ne mogu
        # prihvatiti isti broj niti prepisati stanje jedna drugoj.
        data = load_data()
        counting_data = data.setdefault("counting", {})
        if not isinstance(counting_data, dict):
            counting_data = data["counting"] = {}
        state = counting_data.setdefault(
            game_key,
            {"next": 1, "last_user_id": None},
        )
        if not isinstance(state, dict):
            state = counting_data[game_key] = {"next": 1, "last_user_id": None}
        expected = max(1, int(state.get("next", 1) or 1))
        last_user_id = state.get("last_user_id")

        if broj != expected:
            state.update({"next": 1, "last_user_id": None})
            save_data(data)
            embed = counting_embed(
                broj,
                author_mention=ctx.author.mention,
                error=f"Pogrešan broj — očekivao se **{expected}**. Brojanje se vraća na **1**.",
            )
        elif expected > 1 and last_user_id == ctx.author.id:
            state.update({"next": 1, "last_user_id": None})
            save_data(data)
            embed = counting_embed(
                broj,
                author_mention=ctx.author.mention,
                error="Ne možeš brojati dva puta zaredom. Brojanje se vraća na **1**.",
            )
        else:
            state.update({"next": expected + 1, "last_user_id": ctx.author.id})
            reward = 5 if expected % 10 == 0 else 1
            wallet = get_ekonomija(data, ctx.author.id)
            wallet["novac"] += reward
            save_data(data)
            embed = counting_embed(
                broj,
                next_number=broj + 1,
                author_mention=ctx.author.mention,
            )
    await send_counting_reply(ctx, embed)

@bot.command(name="toplo-hladno")
async def toplo_hladno(ctx: commands.Context, pogodak: int = None):
    if not await check_kanal(ctx, "toplo_hladno"):
        return
    channel_id = ctx.channel.id
    if pogodak is None:
        HOT_COLD_GAMES[channel_id] = random.randint(1, 100)
        await send_game_embed(
            ctx,
            game_embed(
                "🌡️ Toplo-hladno",
                [
                    "> 🎯 Zamislio/la sam broj od **1 do 100**.",
                    "> Pošalji samo broj u kanalu ili koristi `.toplo-hladno <broj>`.",
                ],
                "Nova runda je počela",
            ),
            "toplo_hladno",
        )
        return
    if not 1 <= pogodak <= 100:
        await send_game_embed(
            ctx,
            game_embed(
                "🌡️ Toplo-hladno",
                ["> ❌ Broj mora biti između **1 i 100**."],
                "Pokušaj ponovo",
            ),
            "toplo_hladno",
        )
        return
    target = HOT_COLD_GAMES.setdefault(channel_id, random.randint(1, 100))
    if pogodak == target:
        HOT_COLD_GAMES.pop(channel_id, None)
        await send_game_embed(
            ctx,
            game_embed(
                "🌡️ Toplo-hladno",
                [
                    f"> 🎉 Tačan pogodak: **{target}**!",
                    "> Nova runda počinje sa `.toplo-hladno`.",
                ],
                "Čestitamo!",
            ),
            "toplo_hladno",
        )
        return
    razlika = abs(target - pogodak)
    temperatura = "🔥 VRELO" if razlika <= 5 else "🌡️ Toplo" if razlika <= 15 else "❄️ Hladno"
    smjer = "veći" if pogodak < target else "manji"
    await send_game_embed(
        ctx,
        game_embed(
            "🌡️ Toplo-hladno",
            [
                f"> 🎯 Tvoj broj: **{pogodak}**",
                f"> {temperatura}",
                f"> Pokušaj ponovo sa brojem koji je **{smjer}**.",
            ],
            "Runda je aktivna",
        ),
        "toplo_hladno",
    )

@bot.command(name="kaladont")
async def kaladont(ctx: commands.Context, rijec: str = None):
    if not await check_kanal(ctx, "kaladont"):
        return
    channel_id = ctx.channel.id
    game = KALADONT_GAMES.get(channel_id)
    if not rijec:
        KALADONT_GAMES[channel_id] = {
            "last": None,
            "last_author_id": None,
            "used": set(),
        }
        await send_kaladont_embed(ctx, game_embed(
            "🔤 Kaladont",
            ["> Nova runda je počela!", "> Prva osoba šalje riječ komandom `.kaladont <riječ>`.", "> Riječ mora imati najmanje 2 slova.", "> Isti igrač ne može igrati dva puta zaredom."],
            "Ako riječ završava na „ka“, igrač gubi",
        ))
        return
    rijec = rijec.lower().strip()
    if len(rijec) < 2 or not rijec.isalpha():
        await send_kaladont_embed(ctx, game_embed(
            "🔤 Kaladont",
            ["> ❌ Riječ mora sadržati samo slova i imati najmanje 2 slova."],
            "Primjer: .kaladont more",
        ))
        return
    if not is_known_bhs_word(rijec):
        await send_kaladont_embed(ctx, game_embed(
            "🔤 Kaladont",
            [f"> ❌ Riječ **{rijec.upper()}** nije pronađena u B/H/S rječniku.",
             "> Unesi stvarnu riječ, bez izmišljanja slova."],
            "Riječ nije prihvaćena",
        ))
        return
    if game is None:
        game = {"last": None, "last_author_id": None, "used": set()}
        KALADONT_GAMES[channel_id] = game
    game.setdefault("used", set())
    if game.get("last") and game.get("last_author_id") == ctx.author.id:
        await send_kaladont_embed(ctx, game_embed(
            "🔤 Kaladont",
            [f"> ⏳ {ctx.author.mention}, sačekaj da drugi član pošalje riječ.",
             "> Isti igrač ne može igrati dva puta zaredom."],
            "Red je na drugom igraču",
        ))
        return
    if rijec in game["used"]:
        await send_kaladont_embed(ctx, game_embed(
            "🔤 Kaladont",
            [f"> ❌ {ctx.author.mention}, ta riječ je već iskorištena."],
            "Probaj drugu riječ",
        ))
        return
    if game["last"] and not rijec.startswith(game["last"][-2:]):
        await send_kaladont_embed(ctx, game_embed(
            "🔤 Kaladont",
            [f"> ❌ Riječ mora početi sa **{game['last'][-2:].upper()}**."],
            "Kaladont pravilo",
        ))
        return
    game["used"].add(rijec)
    game["last"] = rijec
    game["last_author_id"] = ctx.author.id
    if rijec.endswith("ka"):
        KALADONT_GAMES.pop(channel_id, None)
        poruka = [
            f"> 💥 {ctx.author.mention} je poslao/la **{rijec.upper()}**.",
            "> Riječ se završava na „KA“ — runda je završena!",
        ]
    else:
        poruka = [
            f"> ✅ {ctx.author.mention}: **{rijec.upper()}**",
            f"> Sljedeća riječ počinje sa **{rijec[-2:].upper()}**.",
        ]
    await send_kaladont_embed(
        ctx,
        game_embed("🔤 Kaladont", poruka, "Nova runda: .kaladont"),
    )

# ══════════════════════════════════════════════
#   MONIKA — kontrola zabavnog razgovora
# ══════════════════════════════════════════════
@bot.tree.command(name="setmonika", description="[ADMIN] Uključi Moniku u izabranom kanalu")
@app_commands.describe(kanal="Kanal u kojem Monika smije odgovarati; prazno znači trenutni kanal")
@app_commands.default_permissions(administrator=True)
async def setmonika(
    interaction: discord.Interaction,
    kanal: discord.TextChannel = None,
):
    if not interaction.guild:
        await interaction.response.send_message(
            "Ova komanda radi samo na serveru.",
            ephemeral=True,
        )
        return
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message(
            "Samo administrator može uključiti Moniku.",
            ephemeral=True,
        )
        return

    target_channel = kanal or interaction.channel
    if not isinstance(target_channel, discord.TextChannel):
        await interaction.response.send_message(
            "Izaberi tekstualni kanal.",
            ephemeral=True,
        )
        return

    data = load_data()
    cfg = get_monika(data, interaction.guild.id)
    cfg["channel_id"] = target_channel.id
    save_data(data)
    await interaction.response.send_message(
        f"Monika je uključena u kanalu {target_channel.mention}.\n"
        "Pratiće razgovor, ali će se javiti najviše jednom u 3 minute kada "
        "prepozna zabavnu temu ili je neko označi. Tada taguje članove "
        "po abecedi i postavlja pitanje, kružeći kroz cijeli server.",
        ephemeral=True,
    )

@bot.tree.command(name="iskljuci-moniku", description="[ADMIN] Isključi Moniku na serveru")
@app_commands.default_permissions(administrator=True)
async def iskljuci_moniku(interaction: discord.Interaction):
    if not interaction.guild:
        await interaction.response.send_message(
            "Ova komanda radi samo na serveru.",
            ephemeral=True,
        )
        return
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message(
            "Samo administrator može isključiti Moniku.",
            ephemeral=True,
        )
        return

    data = load_data()
    cfg = get_monika(data, interaction.guild.id)
    cfg["channel_id"] = None
    save_data(data)
    await interaction.response.send_message(
        "Monika je isključena. Više neće odgovarati u chatu.",
        ephemeral=True,
    )

# ══════════════════════════════════════════════
#   GIVEAWAY I /opis
# ══════════════════════════════════════════════
@bot.command(name="giveaways")
async def giveaways(ctx: commands.Context):
    """Vlasnik objavljuje Nitro giveaway koji traje 24 sata."""
    if not await bot.is_owner(ctx.author):
        await ctx.send(embed=discord.Embed(
            description="> Ovu komandu može koristiti samo vlasnik bota.",
            color=_LP,
        ))
        return
    if not ctx.guild:
        await ctx.send("Giveaway se može objaviti samo na serveru.")
        return
    giveaway_id = f"{ctx.guild.id}-{ctx.channel.id}-{now_ts()}"
    ends_at = now_ts() + GIVEAWAY_DURATION_SECONDS
    data = load_data()
    data.setdefault("giveaways", {})[giveaway_id] = {
        "guild_id": ctx.guild.id,
        "channel_id": ctx.channel.id,
        "message_id": None,
        "ends_at": ends_at,
        "entries": [],
        "ended": False,
        "winner_id": None,
    }
    message = await ctx.send(embed=giveaway_embed(ctx.guild, ends_at), view=GiveawayView(giveaway_id))
    data["giveaways"][giveaway_id]["message_id"] = message.id
    save_data(data)
    GIVEAWAY_TASKS[giveaway_id] = asyncio.create_task(finish_giveaway(giveaway_id))

@bot.command(name="poruka", aliases=["poruke"])
async def poruka(
    ctx: commands.Context,
    server_link: str = None,
    limit: int = 100,
):
    """Vlasnik bota ili servera šalje najviše 100 pozivnica u DM."""
    if ctx.guild is None:
        await ctx.send("> Komandu `.poruka` ili `.poruke` pokreni u kanalu servera.", delete_after=8)
        return

    try:
        is_bot_owner = await bot.is_owner(ctx.author)
    except discord.HTTPException as exc:
        is_bot_owner = False
        print(f"[PORUKA] Provjera vlasnika bota nije uspjela: {exc}")
    is_guild_owner = ctx.author.id == ctx.guild.owner_id
    if not (is_bot_owner or is_guild_owner):
        await ctx.send(
            "> Ovu komandu može koristiti vlasnik bota ili vlasnik ovog servera.",
            delete_after=12,
        )
        return

    if not server_link:
        await ctx.send(
            "> Upotreba: `.poruka <link-servera> [broj 1-100]` "
            "ili `.poruke <link-servera> [broj 1-100]`.\n"
            "> Primjer: `.poruke https://discord.gg/tvoj-link 100`",
            delete_after=12,
        )
        return
    if not 1 <= limit <= 100:
        await ctx.send(
            "> Broj mora biti između **1 i 100**. Discord može odbiti DM "
            "članovima koji ne dozvoljavaju privatne poruke.",
            delete_after=12,
        )
        return

    server_link = server_link.strip().strip("<>")
    if server_link.startswith("discord.gg/"):
        server_link = f"https://{server_link}"

    # Dozvoli samo Discord invite link, da se u poruku ne ubaci pogrešan
    # ili neočekivan URL.
    if not re.match(
        r"^https?://(?:www\.)?(?:discord\.gg|discord\.com/invite)/[A-Za-z0-9_-]+/?$",
        server_link,
        re.IGNORECASE,
    ):
        await ctx.send(
            "> Link mora biti Discord invite link, npr. "
            "`https://discord.gg/tvoj-link`.",
            delete_after=12,
        )
        return

    embed = discord.Embed(
        title=f"{PORUKA_CUSTOM_EMOJI['sparkles']} Dobro došao/la u {ctx.guild.name}!",
        description=(
            f"> {PORUKA_CUSTOM_EMOJI['heart']} Baš nam je drago što si ovde! "
            "Upoznaj ekipu, uključi se u zajedničke aktivnosti i napravi lepe uspomene.\n"
            ">\n"
            f"> {PORUKA_CUSTOM_EMOJI['ticket']} [Tvoj poziv na server — klikni ovde]({server_link})\n"
            ">\n"
            f"> {PORUKA_CUSTOM_EMOJI['sparkles']} Jedva čekamo da te upoznamo!"
        ),
        color=_LP,
    )
    embed.add_field(
        name=f"{PORUKA_CUSTOM_EMOJI['calendar']} Događaji i nagrade",
        value=(
            f"> {PORUKA_CUSTOM_EMOJI['calendar']} Dnevni eventi i druženja\n"
            f"> {PORUKA_CUSTOM_EMOJI['gift']} Nagrade i posebna iznenađenja\n"
            f"> {PORUKA_CUSTOM_EMOJI['rocket']} Nitro nagrade i giveaway-i"
        ),
        inline=False,
    )
    embed.add_field(
        name=f"{PORUKA_CUSTOM_EMOJI['sparkles']} Još mnogo toga",
        value=(
            "> 🎨 Dekoracije, posebne role i tematski sadržaji\n"
            f"> {PORUKA_CUSTOM_EMOJI['game']} Igre, razgovori i mnogo lepih trenutaka\n"
            f"> {PORUKA_CUSTOM_EMOJI['users']} Nova poznanstva i ekipa koja je tu za tebe"
        ),
        inline=False,
    )
    if ctx.guild.icon:
        embed.set_thumbnail(url=ctx.guild.icon.url)

    status_embed = discord.Embed(
        title=f"{PORUKA_CUSTOM_EMOJI['mail']} Slanje pozivnice",
        description=(
            f"> Počinjem slanje u privatne poruke za najviše **{limit} članova** "
            f"servera **{ctx.guild.name}**."
        ),
        color=_LP,
    )
    status_message = await ctx.send(embed=status_embed)
    poslato = 0
    preskoceno = 0
    pokusano = 0
    dm_odbijeno = 0
    dm_http_greske = 0
    prva_dm_greska = None
    ucitavanje_greska = None
    try:
        async for member in ctx.guild.fetch_members(limit=None):
            if member.bot:
                preskoceno += 1
                continue
            if pokusano >= limit:
                break
            pokusano += 1
            try:
                await member.send(embed=embed)
                poslato += 1
            except discord.Forbidden:
                # Discord često odbija DM kada član ima zatvorene privatne
                # poruke ili bot nema dozvolu da mu se javi.
                dm_odbijeno += 1
            except discord.HTTPException as exc:
                dm_http_greske += 1
                if prva_dm_greska is None:
                    prva_dm_greska = f"HTTP {exc.status}, Discord kod {exc.code}"
                print(
                    f"[PORUKA] Slanje DM-a nije uspjelo: "
                    f"HTTP {exc.status}, Discord kod {exc.code}."
                )
            # Drži slanje ispod Discordovog DM rate limita.
            await asyncio.sleep(0.25)
    except (discord.Forbidden, discord.HTTPException) as exc:
        ucitavanje_greska = exc
        print(f"[PORUKA] Učitavanje članova nije uspjelo: {exc}")

    if ucitavanje_greska and poslato == 0 and preskoceno == 0:
        final_embed = discord.Embed(
            title=f"{PORUKA_CUSTOM_EMOJI['mail']} Slanje nije pokrenuto",
            description=(
                "> Nisam mogao učitati članove servera, pa poruka nije poslata. "
                "U Discord Developer Portalu uključi **Server Members Intent**, "
                "sačuvaj promjenu i restartuj bota."
            ),
            color=_LP,
        )
    else:
        description = f"> Slanje privatnih pozivnica za **{ctx.guild.name}** je završeno."
        if dm_http_greske:
            description += (
                f"\n> Ostale HTTP greške: **{dm_http_greske}**"
                + (f" (prva: {prva_dm_greska})." if prva_dm_greska else ".")
            )
        if ucitavanje_greska:
            description += "\n> Učitavanje članova je prekinuto; dio članova možda nije obrađen."
        final_embed = discord.Embed(
            title=(
                f"{PORUKA_CUSTOM_EMOJI['mail']} Slanje završeno"
                if dm_http_greske or ucitavanje_greska
                else f"{PORUKA_CUSTOM_EMOJI['check']} Slanje završeno"
            ),
            description=description,
            color=_LP,
        )
        for label, value in (
            ("Pokušano", f"{pokusano}/{limit}"),
            ("Poslato", str(poslato)),
            ("Botovi preskočeni", str(preskoceno)),
            ("DM odbijen", str(dm_odbijeno)),
        ):
            final_embed.add_field(name=label, value=f"> **{value}**", inline=True)
    final_embed.set_footer(text=f"{BOT_NAME} • .poruka / .poruke")
    await status_message.edit(content=None, embed=final_embed)

@bot.tree.command(name="opis", description="[OWNER] Objavi kompletno uputstvo za korištenje bota")
async def opis_slash(interaction: discord.Interaction):
    """Objavljuje kompletno, višedijelno uputstvo samo kada ga pozove vlasnik bota."""
    if not await bot.is_owner(interaction.user):
        await interaction.response.send_message(
            "Ovu komandu može koristiti samo vlasnik bota.",
            ephemeral=True,
        )
        return

    # Naslovi počinju tačkom da ih zajednički stil embedova ne bi pretvorio
    # u naslov sa dodatnom ikonom. Uputstvo namjerno nema emoji-je.
    embeds = [
        discord.Embed(
            title="• MONIKA BOT — Uputstvo 1/7",
            description=(
                "> **Dobrodošli u uputstvo za članske komande MONIKA BOT-a.**\n"
                ">\n"
                "> Ovaj pregled objašnjava komande koje članovi mogu koristiti za druženje, "
                "ljubavne odnose, virtuelnu ekonomiju, "
                "kuće, ribolov, rang-liste, mini-igre i podršku članovima.\n"
                ">\n"
                "> Sve prefix komande počinju tačkom: `.komanda`.\n"
                "> Slash komande počinju kosom crtom: `/komanda`.\n"
                ">\n"
                "> Argument u uglastim zagradama je opcionalan: `[argument]`.\n"
                "> Argument u šiljastim zagradama je obavezan: `<argument>`.\n"
                "> Oznaka `@Korisnik` znači da treba označiti člana servera."
            ),
            color=_LP,
        ),
        discord.Embed(
            title="• MONIKA BOT — Ljubav i profil 2/7",
            description=(
                "> **Ljubavni sistem**\n"
                "> `.veza @Korisnik` — Pošalji prijedlog za vezu.\n"
                "> `.profil [@Korisnik]` — Prikaži ljubavni profil.\n"
                "> `.brak @Partner` — Pošalji prijedlog za brak.\n"
                "> `.prsten [@Partner]` — Prikaži ili odaberi prsten.\n"
                "> `.svadba` — Pokreni ceremoniju vjenčanja.\n"
                "> `.obnova` — Obnovi bračne zavjete, uz cooldown.\n"
                "> `.zakletva [tekst]` — Dodaj bračnu zakletvu.\n"
                "> `.razvod` — Prekini vezu ili brak.\n"
                "> `.datum` — Prikaži koliko veza traje.\n"
                "> `.godisnjica` — Prikaži vrijeme do godišnjice.\n"
                "> `.ljubomora` — Prikaži nivo ljubomore.\n"
                "> `.razina` — Prikaži nivo veze.\n"
                "> `.statistika` — Prikaži statistiku para.\n"
                "> `.djeca` — Prikaži članove porodice.\n"
                "> `.beba` — Dobij dijete ako ispunjavaš uslove.\n"
                "> `.album` — Prikaži sačuvane uspomene."
            ),
            color=_LP,
        ),
        discord.Embed(
            title="• MONIKA BOT — Bodovi i aktivnosti 3/7",
            description=(
                "> **Ljubavni bodovi, XP i aktivnosti**\n"
                "> `.spavanje` — Dodaj ljubavne bodove nakon odmora.\n"
                "> `.srce` — Pošalji ljubav i osvoji bodove.\n"
                "> `.zagrljaj @Korisnik` — Pošalji zagrljaj i XP.\n"
                "> `.poljubac @Korisnik` — Pošalji poljubac i XP.\n"
                "> `.ples @Korisnik` — Ples sa članom.\n"
                "> `.izlet` — Zajednički izlet i nagrada.\n"
                "> `.vecera` — Romantična večera i nagrada.\n"
                "> `.putovanje` — Putovanje i veći broj bodova.\n"
                "> `.poklon @Korisnik` — Pošalji slučajni poklon.\n"
                "> `.cvijece @Korisnik` — Pošalji cvijeće.\n"
                "> `.cokolada @Korisnik` — Pošalji čokoladu.\n"
                "> `.ruza`, `.ogrlica`, `.sat`, `.parfem` — Brzi pokloni.\n"
                "> `.auto @Korisnik`, `.jahte @Korisnik` — Luksuzni pokloni.\n"
                ">\n"
                "> Uspješne aktivnosti se upisuju u profile oba učesnika. "
                "Cooldown sprečava pretjerano ponavljanje iste aktivnosti."
            ),
            color=_LP,
        ),
        discord.Embed(
            title="• MONIKA BOT — Ekonomija 4/7",
            description=(
                "> **Novac, banka i market**\n"
                "> `.ekonomija` — Brzi pregled novca i ekonomskih komandi.\n"
                "> `.rad` — Radi i zaradi novčiće.\n"
                "> `.plata` — Preuzmi dnevnu platu, jednom u 24 sata.\n"
                "> `.novac [@Korisnik]` — Pregled gotovine člana.\n"
                "> `.banka` — Pregled stanja u banci.\n"
                "> `.uplati <iznos>` — Prebaci novac u banku.\n"
                "> `.podigni <iznos>` — Podigni novac iz banke.\n"
                "> `.transfer @Korisnik <iznos>` — Pošalji novac drugom članu.\n"
                "> `.market` — Prikaži predmete koji su dostupni za kupovinu.\n"
                "> `.kupi <predmet>` — Kupi predmet iz marketa.\n"
                "> `.pokloni @Korisnik <predmet>` — Pokloni predmet iz inventara.\n"
                "> `.casino coin <ulog>` — Igra glava ili pismo.\n"
                "> `.casino slot <ulog>` — Igra slot mašine.\n"
                ">\n"
                "> Minimalni ulog u casinu je 10 novčića. Predmeti, novac i inventar "
                "čuvaju se u fajlu `ljubav_data.json`."
            ),
            color=_LP,
        ),
        discord.Embed(
            title="• MONIKA BOT — Kuća i ribolov 5/7",
            description=(
                "> **Kuća, sobe i ribolov**\n"
                "> `.kuca` — Kupi kuću ako imaš dovoljno novca.\n"
                "> `.stan` — Prikaži svoju kuću i napredak.\n"
                "> `.soba` — Prikaži dostupne sobe.\n"
                "> `.kuhinja`, `.spavaca`, `.kupatilo` — Kupi ili prikaži sobu.\n"
                "> `.vrt`, `.bazen`, `.garaza` — Kupi ili prikaži dodatak kući.\n"
                "> `.namjestaj` — Prikaži dostupni namještaj.\n"
                "> `.pecanje` — Pokreni ribolov, uz cooldown.\n"
                "> `.ribnjak [@Korisnik]` — Prikaži inventar ulovljenih riba.\n"
                "> `.prodaj` — Prodaj ulov i dobij novčiće.\n"
                "> `.ribar [@Korisnik]` — Prikaži ribolovni profil.\n"
                ">\n"
                "> Ribolov, kuća, sobe i inventar vode se odvojeno za svakog člana."
            ),
            color=_LP,
        ),
        discord.Embed(
            title="• MONIKA BOT — Mini-igre 6/7",
            description=(
                "> **Igre za kanal i članove**\n"
                "> `.counting 1` — Započni brojanje; zatim se šalje sljedeći broj.\n"
                "> `.toplo-hladno` — Zamisli broj od 1 do 100 i pogađaj.\n"
                "> `.toplo-hladno <broj>` — Pošalji pokušaj u aktivnoj rundi.\n"
                "> `.kaladont` — Pokreni igru riječima.\n"
                "> `.kaladont <riječ>` — Pošalji riječ koja počinje zadnja dva slova.\n"
                "> `,-xo @Korisnik`, `.xo @Korisnik` ili `/xo` — XO potezima na dugmad; partija traje 2 minuta.\n"
                "> `.pijte` — Pokreni zabavnu poruku za društvo.\n"
                "> `.film` — Pokreni izbor filma.\n"
                "> `.istina` — Dobij pitanje istine.\n"
                "> `.izazov` — Dobij tekstualni izazov.\n"
                "> `.ljubavni-test @Korisnik` — Izračunaj ljubavni test.\n"
                "> `.compatibility @Korisnik` — Izračunaj kompatibilnost.\n"
                ">\n"
                "> Stanje svake igre je odvojeno po kanalu. U kanalima čiji naziv "
                "sadrži `counting`, `toplo-hladno`, `kaladont` ili `casino` mogući "
                "su i unosi bez prefixa, kada je runda već pokrenuta."
            ),
            color=_LP,
        ),
        discord.Embed(
            title="• MONIKA BOT — Rang-liste i pomoć 7/7",
            description=(
                "> **Rang-liste**\n"
                "> `.topljubav` — Najviše ljubavnih bodova.\n"
                "> `.topxp` — Najviše XP bodova.\n"
                "> `.topbogati` — Najbogatiji članovi.\n"
                "> `.topparovi` — Najuspješniji parovi.\n"
                "> `.topstanovi` — Najbolje kuće i stanovi.\n"
                "> `.top-ribar` — Najuspješniji ribari.\n"
                ">\n"
                "> **Pomoć i pregledi**\n"
                "> `.pomoc` — Prva stranica pomoći.\n"
                "> `.pomoc 2` — Brak, porodica i ekonomija.\n"
                "> `.pomoc 3` — Kuća, pokloni, ribolov i zabava.\n"
                "> `/komande` — Kratak pregled svih članskih komandi.\n"
                "> `/igre` — Kratak pregled mini-igara.\n"
                ">\n"
                "> Ako komanda ne radi, provjeri prefix, obavezne argumente, cooldown "
                "i kanal u kojem je komanda dozvoljena."
            ),
            color=_LP,
        ),
    ]
    # Discord ograničava ukupan broj znakova svih embedova u jednoj poruci.
    # Zato se uputstvo objavljuje kao niz povezanih poruka, umjesto da se
    # posljednji dijelovi odrežu ili da Discord odbije cijelu objavu.
    # Na svaki dio dodaj malu sliku servera. Tako svaki embed ima vizuelni
    # identitet, bez ubacivanja emoji-ja u tekst komandi.
    slika_url = None
    if interaction.guild and interaction.guild.icon:
        slika_url = interaction.guild.icon.url
    elif bot.user and bot.user.display_avatar:
        slika_url = bot.user.display_avatar.url

    for index, embed in enumerate(embeds, start=1):
        if slika_url:
            embed.set_thumbnail(url=slika_url)
        embed.set_footer(
            text=f"{BOT_NAME} {VERSION} • dio {index}/{len(embeds)} • članske komande"
        )
        if index == 1:
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.followup.send(embed=embed)

@bot.tree.command(name="komande", description="Pregled svih prefix komandi i mini-igara")
async def komande_slash(interaction: discord.Interaction):
    e = game_embed(
        "📚 Sve komande",
        [
            "> Sve prefix komande počinju tačkom (`.`).",
            "> ",
            "> Mini-igre:",
            "> `.casino [coin|slot] <ulog>`",
            "> `.counting [broj]`",
            "> `.toplo-hladno [broj]`",
            "> `.kaladont [riječ]`",
            "> `,-xo @Korisnik`, `.xo @Korisnik` ili `/xo` — XO na dugmad; 2 minuta",
            "> `.ekonomija`",
            "> ",
            "> Ljubav: `.veza` · `.profil` · `.brak` · `.prsten` · `.svadba`",
            "> Ekonomija: `.rad` · `.plata` · `.novac` · `.banka` · `.market`",
            "> Kuća: `.stan` · `.kuca` · `.soba` · `.namjestaj`",
            "> Ribolov: `.pecanje` · `.ribnjak` · `.prodaj` · `.ribar`",
            "> Pomoć: `.pomoc` · `.pomoc 2` · `.pomoc 3`",
        ],
        "Prefix: .",
    )
    await interaction.response.send_message(embed=e)

@bot.tree.command(name="igre", description="Pregled mini-igara")
async def igre_slash(interaction: discord.Interaction):
    await interaction.response.send_message(
        embed=games_menu_embed(),
        view=GamesMenuView(),
        allowed_mentions=discord.AllowedMentions.none(),
    )

# ══════════════════════════════════════════════
#              POKRETANJE — Auto-reconnect
# ══════════════════════════════════════════════
import time

if __name__ == "__main__":
    if not TOKEN:
        print("[ERROR] DISCORD_TOKEN nije postavljen!")
        sys.exit(1)

    while True:
        try:
            print(f"[{BOT_NAME}] Pokretanje bota...")
            bot.run(TOKEN, reconnect=True, log_handler=None)
        except discord.LoginFailure:
            print("[ERROR] Neispravni token! Provjeri DISCORD_TOKEN.")
            sys.exit(1)
        except (discord.GatewayNotFound, discord.ConnectionClosed,
                discord.HTTPException, OSError) as e:
            print(f"[WARN] Veza prekinuta ({type(e).__name__}: {e}). Ponovni pokušaj za 10s...")
            time.sleep(10)
        except KeyboardInterrupt:
            print(f"[{BOT_NAME}] Gašenje bota...")
            break
        except Exception as e:
            print(f"[ERROR] Neočekivana greška: {e}. Ponovni pokušaj za 15s...")
            time.sleep(15)
        finally:
            # Reset bot state za ponovni pokušaj
            if not bot.is_closed():
                pass  # bot.run se već pobrinuo
        print(f"[{BOT_NAME}] Reconnect petlja — nastavlja se...")
