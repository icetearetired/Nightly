import asyncio
import io
import logging
import os

import discord
import mss
from discord.ext import commands
from dotenv import load_dotenv
from PIL import Image


load_dotenv()
logging.basicConfig(level=logging.INFO)

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
OWNER_ID = os.getenv("OWNER_ID")

if not DISCORD_TOKEN:
    raise RuntimeError("Set DISCORD_TOKEN in your .env file.")
if not OWNER_ID or not OWNER_ID.isdigit():
    raise RuntimeError("Set OWNER_ID to your numeric Discord user ID in .env.")


def capture_primary_screen() -> io.BytesIO:
    with mss.mss() as screen_capture:
        monitor = screen_capture.monitors[1]
        screenshot = screen_capture.grab(monitor)

    image = Image.frombytes(
        "RGB",
        (screenshot.width, screenshot.height),
        screenshot.rgb,
    )
    image_data = io.BytesIO()
    image.save(image_data, format="JPEG", quality=85)
    image_data.seek(0)
    return image_data


class ScreenshotBot(commands.Bot):
    async def setup_hook(self) -> None:
        await self.tree.sync()


bot = ScreenshotBot(command_prefix="!", intents=discord.Intents.default())


@bot.tree.command(name="screenshot", description="Send a screenshot of your primary display")
async def screenshot_command(interaction: discord.Interaction) -> None:
    if interaction.user.id != int(OWNER_ID):
        await interaction.response.send_message(
            "This command is restricted to the configured owner.",
            ephemeral=True,
        )
        return

    await interaction.response.defer(ephemeral=True, thinking=True)

    try:
        image_data = await asyncio.to_thread(capture_primary_screen)
    except Exception:
        logging.exception("Screenshot capture failed")
        await interaction.followup.send(
            "Could not capture the primary display on this PC.",
            ephemeral=True,
        )
        return

    await interaction.followup.send(
        file=discord.File(image_data, filename="screenshot.jpg"),
        ephemeral=True,
    )


bot.run(DISCORD_TOKEN)