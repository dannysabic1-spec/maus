import asyncio
import os
import re

import discord
from discord.ext import commands


BOT_NAME = "MONIKA BOT"
XO_TIMEOUT_SECONDS = 120
MAX_INVITE_RECIPIENTS = 100


class MinimalBot(commands.Bot):
    async def setup_hook(self) -> None:
        # Ukloni ranije objavljene slash komande ove aplikacije.
        self.tree.clear_commands(guild=None)
        await self.tree.sync()


intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = MinimalBot(
    command_prefix=".",
    intents=intents,
    help_command=None,
)


def xo_embed(view: "XOView") -> discord.Embed:
    x_name = discord.utils.escape_markdown(view.player_x.display_name)
    o_name = discord.utils.escape_markdown(view.player_o.display_name)
    embed = discord.Embed(
        title="⭕ XO duel",
        description=(
            f"**X:** {x_name}\n"
            f"**O:** {o_name}\n\n"
            f"{view.status}"
        ),
        color=discord.Color.blurple(),
    )
    if view.finished:
        embed.set_footer(text="Partija je završena.")
    else:
        embed.set_footer(text="Klikni polje na tabli. Partija traje najviše 2 minuta.")
    return embed


class XOButton(discord.ui.Button["XOView"]):
    def __init__(self, position: int):
        super().__init__(
            label=str(position + 1),
            style=discord.ButtonStyle.secondary,
            row=position // 3,
        )
        self.position = position

    async def callback(self, interaction: discord.Interaction) -> None:
        await self.view.play(interaction, self.position)


class XOView(discord.ui.View):
    def __init__(self, player_x: discord.abc.User, player_o: discord.abc.User):
        super().__init__(timeout=XO_TIMEOUT_SECONDS)
        self.player_x = player_x
        self.player_o = player_o
        self.board = [""] * 9
        self.current_player = player_x
        self.finished = False
        self.message: discord.Message | None = None
        self.move_lock = asyncio.Lock()
        self.status = f"Potez je na **{player_x.display_name} (X)**."
        for position in range(9):
            self.add_item(XOButton(position))

    @staticmethod
    def winning_line(board: list[str]) -> bool:
        lines = (
            (0, 1, 2), (3, 4, 5), (6, 7, 8),
            (0, 3, 6), (1, 4, 7), (2, 5, 8),
            (0, 4, 8), (2, 4, 6),
        )
        return any(
            board[a] and board[a] == board[b] == board[c]
            for a, b, c in lines
        )

    def refresh_buttons(self) -> None:
        for item in self.children:
            if not isinstance(item, XOButton):
                continue
            mark = self.board[item.position]
            item.label = mark or str(item.position + 1)
            item.disabled = self.finished or bool(mark)
            if mark == "X":
                item.style = discord.ButtonStyle.primary
            elif mark == "O":
                item.style = discord.ButtonStyle.danger
            else:
                item.style = discord.ButtonStyle.secondary

    async def play(
        self,
        interaction: discord.Interaction,
        position: int,
    ) -> None:
        async with self.move_lock:
            if self.finished:
                await interaction.response.send_message(
                    "Ova XO partija je završena.",
                    ephemeral=True,
                )
                return

            if interaction.user.id not in (self.player_x.id, self.player_o.id):
                await interaction.response.send_message(
                    "Ova tabla je samo za igrače koje je izazivač odabrao.",
                    ephemeral=True,
                )
                return

            if interaction.user.id != self.current_player.id:
                await interaction.response.send_message(
                    "Sada nije tvoj potez.",
                    ephemeral=True,
                )
                return

            if self.board[position]:
                await interaction.response.send_message(
                    "To polje je već zauzeto.",
                    ephemeral=True,
                )
                return

            mark = "X" if interaction.user.id == self.player_x.id else "O"
            self.board[position] = mark

            if self.winning_line(self.board):
                self.finished = True
                self.status = (
                    f"🏆 **{discord.utils.escape_markdown(interaction.user.display_name)} "
                    f"pobeđuje kao {mark}!**"
                )
            elif all(self.board):
                self.finished = True
                self.status = "🤝 **Nerešeno — tabla je puna.**"
            else:
                self.current_player = (
                    self.player_o if mark == "X" else self.player_x
                )
                self.status = (
                    f"Potez je na **"
                    f"{discord.utils.escape_markdown(self.current_player.display_name)} "
                    f"({'O' if mark == 'X' else 'X'})**."
                )

            self.refresh_buttons()
            await interaction.response.edit_message(
                embed=xo_embed(self),
                view=self,
            )
            if self.finished:
                self.stop()

    async def on_timeout(self) -> None:
        async with self.move_lock:
            if self.finished:
                return
            self.finished = True
            self.status = "⏰ **Vreme je isteklo — partija više ne važi.**"
            self.refresh_buttons()
            if self.message is not None:
                try:
                    await self.message.edit(embed=xo_embed(self), view=self)
                except discord.HTTPException as exc:
                    print(f"[XO] Tabla nije mogla biti ažurirana: {exc}")


@bot.command(name="xo")
async def xo(ctx: commands.Context, protivnik: discord.Member = None) -> None:
    """Pokreni javni XO duel koji se igra klikom na dugmad."""
    if ctx.guild is None:
        await ctx.send("Komanda `.xo` radi samo na serveru.")
        return
    if protivnik is None:
        await ctx.send("Upotreba: `.xo @član`")
        return
    if protivnik.id == ctx.author.id or protivnik.bot:
        await ctx.send("Izaberi drugog člana servera koji nije bot.")
        return

    view = XOView(ctx.author, protivnik)
    view.message = await ctx.send(
        embed=xo_embed(view),
        view=view,
        allowed_mentions=discord.AllowedMentions.none(),
    )


def valid_invite_link(value: str) -> str | None:
    value = value.strip().strip("<>")
    if value.lower().startswith("discord.gg/"):
        value = f"https://{value}"
    if re.fullmatch(
        r"https?://(?:www\.)?(?:discord\.gg|discord\.com/invite)/[A-Za-z0-9_-]+/?",
        value,
        re.IGNORECASE,
    ):
        return value
    return None


@bot.command(name="poruka")
@commands.guild_only()
@commands.has_guild_permissions(administrator=True)
async def poruka(
    ctx: commands.Context,
    server_link: str = None,
    limit: int = MAX_INVITE_RECIPIENTS,
) -> None:
    """Admin command: pošalji Discord pozivnicu članovima servera u DM."""
    if not server_link:
        await ctx.send(
            "Upotreba: `.poruka <Discord invite link> [broj 1-100]`\n"
            "Primer: `.poruka https://discord.gg/pozivnica 25`"
        )
        return
    if not 1 <= limit <= MAX_INVITE_RECIPIENTS:
        await ctx.send("Broj mora biti između 1 i 100.")
        return

    invite = valid_invite_link(server_link)
    if invite is None:
        await ctx.send(
            "Unesi važeći Discord pozivni link, npr. "
            "`https://discord.gg/pozivnica`."
        )
        return

    guild_name = discord.utils.escape_markdown(ctx.guild.name)
    invite_embed = discord.Embed(
        title=f"Dobro došli u {guild_name}!",
        description=(
            "Pozivamo te da se pridružiš našem Discord serveru.\n\n"
            f"[Klikni ovde da se pridružiš]({invite})"
        ),
        color=discord.Color.blurple(),
    )
    if ctx.guild.icon:
        invite_embed.set_thumbnail(url=ctx.guild.icon.url)

    status = await ctx.send(
        f"Šaljem pozivnicu najviše **{limit}** članovima servera "
        f"**{guild_name}**…",
        allowed_mentions=discord.AllowedMentions.none(),
    )

    attempted = 0
    sent = 0
    bots_skipped = 0
    dm_blocked = 0
    dm_forbidden_codes: dict[str, int] = {}
    http_errors = 0
    member_load_failed = False

    try:
        async for member in ctx.guild.fetch_members(limit=None):
            if member.bot:
                bots_skipped += 1
                continue
            if attempted >= limit:
                break

            attempted += 1
            try:
                await member.send(
                    embed=invite_embed,
                    allowed_mentions=discord.AllowedMentions.none(),
                )
                sent += 1
            except discord.Forbidden as exc:
                dm_blocked += 1
                code = str(exc.code)
                dm_forbidden_codes[code] = dm_forbidden_codes.get(code, 0) + 1
                print(
                    f"[PORUKA] Discord je odbio DM za člana {member.id}: "
                    f"HTTP {exc.status}, kod {exc.code}"
                )
            except discord.HTTPException as exc:
                http_errors += 1
                print(
                    f"[PORUKA] DM nije poslat članu {member.id}: "
                    f"HTTP {exc.status}, Discord kod {exc.code}"
                )
            await asyncio.sleep(0.25)
    except (discord.Forbidden, discord.HTTPException) as exc:
        member_load_failed = True
        print(f"[PORUKA] Učitavanje članova nije uspelo: {exc}")

    if member_load_failed:
        result_title = "Slanje nije završeno"
        result_description = (
            "Učitavanje članova nije uspelo; deo članova možda nije obrađen. "
            "Proveri Server Members Intent."
        )
    elif attempted > 0 and sent == 0:
        result_title = "Nijedna pozivnica nije poslata"
        result_description = (
            "Discord je odbio sve pokušane privatne poruke. "
            "Bot ne može da zaobiđe DM ograničenja članova. "
            "Objavi pozivni link u kanalu da bi bio dostupan svima."
        )
    elif attempted == 0:
        result_title = "Nema primalaca za slanje"
        result_description = "Nije pronađen nijedan član kome se može poslati DM."
    else:
        result_title = "Slanje pozivnice završeno"
        result_description = f"Završeno za server **{guild_name}**."

    result = discord.Embed(
        title=result_title,
        description=result_description,
        color=(
            discord.Color.red()
            if sent == 0
            else discord.Color.orange()
            if member_load_failed or http_errors
            else discord.Color.green()
        ),
    )
    result.add_field(name="Pokušano", value=str(attempted), inline=True)
    result.add_field(name="Poslato", value=str(sent), inline=True)
    result.add_field(name="Botovi preskočeni", value=str(bots_skipped), inline=True)
    result.add_field(name="DM odbijen", value=str(dm_blocked), inline=True)
    result.add_field(name="HTTP greške", value=str(http_errors), inline=True)
    if dm_forbidden_codes:
        codes = ", ".join(
            f"{code} ({count}×)"
            for code, count in sorted(dm_forbidden_codes.items())
        )
        result.add_field(name="Discord kod odbijanja", value=codes, inline=False)
    await status.edit(content=None, embed=result)


@bot.event
async def on_command_error(
    ctx: commands.Context,
    error: commands.CommandError,
) -> None:
    if isinstance(error, commands.CommandNotFound):
        return
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("Komandu `.poruka` mogu koristiti samo administratori servera.")
    elif isinstance(error, commands.NoPrivateMessage):
        await ctx.send("Komanda `.poruka` radi samo na serveru.")
    elif isinstance(error, commands.MemberNotFound):
        await ctx.send("Ne mogu da pronađem tog člana. Probaj `.xo @član`.")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("Proveri unos. Za `.poruka` koristi broj od 1 do 100.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Nedostaje argument. Za XO koristi `.xo @član`.")
    else:
        print(f"[BOT] Greška komande: {error!r}")
        await ctx.send("Došlo je do greške pri izvršavanju komande.")


@bot.event
async def on_ready() -> None:
    print(f"{BOT_NAME} je pokrenut kao {bot.user}.")
    print("Dostupne prefix komande: .xo, .poruka")


if __name__ == "__main__":
    token = os.environ.get("DISCORD_TOKEN")
    if not token:
        raise SystemExit(
            "Nedostaje DISCORD_TOKEN. Dodaj ga u environment variables / Replit Secrets."
        )
    bot.run(token, reconnect=True)
