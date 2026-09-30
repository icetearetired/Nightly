# Nightly
A private Discord utility that captures a screenshot of its host PC when you invoke `/screenshot`.

The response is styled as a compact Discord card with the capture time and display resolution. It is visible only to the configured owner, and the image is kept in memory rather than written to disk.

## Setup

1. Install Python 3.10 or newer.
2. Create a bot application in the [Discord Developer Portal](https://discord.com/developers/applications). Copy its bot token and invite it to your server with the `bot` and `applications.commands` scopes. Grant it permission to send messages and attach files.
3. In PowerShell, from this folder, create and activate a virtual environment and install dependencies:

	```powershell
	py -3 -m venv .venv
	.\.venv\Scripts\Activate.ps1
	pip install -r requirements.txt
	```

4. Copy `.env.example` to `.env`. Set `DISCORD_TOKEN` to the bot token and `OWNER_ID` to your numeric Discord user ID. You can copy your user ID from Discord with Developer Mode enabled.
5. Start the bot by double-clicking `Start Nightly.cmd` in File Explorer. Its terminal closes as soon as Nightly starts; the bot continues running in the background. The launcher prevents a second copy from starting. To stop it, end `pythonw.exe` in Task Manager or restart the PC.

   Alternatively, start it from a terminal:

	```powershell
	.\.venv\Scripts\python.exe bot.py
	```

The bot syncs its slash command when it starts and announces when it is ready in the terminal. Use `/screenshot` in a server where the bot is installed. Only the configured owner can run it, and the screenshot is captured from the primary display only when that command is accepted. The reply is ephemeral, so it is visible only to you. The image is held in memory and sent directly to Discord; it is not saved to disk by the bot.

Keep `.env` private. Anyone with the bot token can control the bot, and anyone who can access the configured Discord account can request screenshots while the bot is running.
