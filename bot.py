import asyncio
import io
import logging
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import uuid4

import discord
import mss
import mss.tools
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv


load_dotenv()
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%H:%M:%S",
)
LOGGER = logging.getLogger("nightly")


@dataclass(frozen=True)
class Settings:
    token: str
    owner_id: int

    @classmethod
    def from_environment(cls) -> "Settings":
        token = os.getenv("DISCORD_TOKEN")
        owner_id = os.getenv("OWNER_ID")
        if not token:
            raise RuntimeError("Set DISCORD_TOKEN in your .env file.")
        if not owner_id or not owner_id.isdigit():
            raise RuntimeError("Set OWNER_ID to your numeric Discord user ID in .env.")
        return cls(token=token, owner_id=int(owner_id))


SETTINGS = Settings.from_environment()


def capture_primary_screen() -> tuple[io.BytesIO, tuple[int, int]]:
    with mss.mss() as screen_capture:
        monitor = screen_capture.monitors[1]
        screenshot = screen_capture.grab(monitor)

    image_data = io.BytesIO()
    image_data.write(mss.tools.to_png(screenshot.rgb, screenshot.size))
    image_data.seek(0)
    return image_data, screenshot.size


def is_owner(interaction: discord.Interaction) -> bool:
    return interaction.user.id == SETTINGS.owner_id


class ScreenshotBot(commands.Bot):
    async def setup_hook(self) -> None:
        await self.tree.sync()
        LOGGER.info("Slash commands synced")

    async def on_ready(self) -> None:
        assert self.user is not None
        await self.change_presence(
            activity=discord.Game(name="/screenshot | private screen capture")
        )
        LOGGER.info("Logged in as %s (%s)", self.user, self.user.id)


bot = ScreenshotBot(command_prefix="!", intents=discord.Intents.default())


@bot.tree.command(name="screenshot", description="Send a private snapshot of the primary display")
@app_commands.check(is_owner)
async def screenshot_command(interaction: discord.Interaction) -> None:
    await interaction.response.defer(ephemeral=True, thinking=True)

    try:
        image_data, (width, height) = await asyncio.to_thread(capture_primary_screen)
    except Exception:
        LOGGER.exception("Screenshot capture failed")
        await interaction.followup.send(
            "Could not capture the primary display on this PC.", ephemeral=True
        )
        return

    captured_at = datetime.now(timezone.utc)
    embed = discord.Embed(
        title="Screenshot ready",
        description="Your primary display was captured and sent privately.",
        colour=discord.Colour.blurple(),
        timestamp=captured_at,
    )
    embed.add_field(name="Resolution", value=f"{width} x {height}")
    embed.set_footer(text="Nightly • never saved to disk")

    filename = f"nightly-{captured_at:%Y%m%d-%H%M%S}-{uuid4().hex[:8]}.png"
    attachment = discord.File(image_data, filename=filename)
    embed.set_image(url=f"attachment://{filename}")
    await interaction.followup.send(embed=embed, file=attachment, ephemeral=True)


@screenshot_command.error
async def screenshot_command_error(
    interaction: discord.Interaction, error: app_commands.AppCommandError
) -> None:
    if isinstance(error, app_commands.CheckFailure):
        message = "This command is restricted to the configured owner."
    else:
        LOGGER.exception("Unhandled screenshot command error", exc_info=error)
        message = "Something went wrong while preparing the screenshot."

    if interaction.response.is_done():
        await interaction.followup.send(message, ephemeral=True)
    else:
        await interaction.response.send_message(message, ephemeral=True)


bot.run(SETTINGS.token, log_handler=None)
