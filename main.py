import asyncio
import json
import logging
from pathlib import Path

import discord
from discord.ext import commands


# Logging
logging.basicConfig(
    filename="jazzbot.log",
    encoding="utf-8",
    format="%(asctime)s %(levelname)-8s %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S",
)


def load_config(config_path: Path) -> dict:
    logging.debug("Opening config file: %s", config_path)
    with config_path.open("r", encoding="utf-8") as cjson:
        logging.debug("Loading JSON from config file.")
        return json.load(cjson)


config = load_config(Path("config.json"))

# Setup client
logging.debug("Setting up Discord client/bot.")
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.voice_states = True

client = commands.Bot(command_prefix=config["command_prefix"], intents=intents)
client.config = config


@client.event
async def on_ready():
    logging.info(
        "We have logged in as %s | Command prefix = '%s'",
        client.user,
        config["command_prefix"],
    )


async def load_cogs() -> None:
    cogs_dir = Path("cogs")
    logging.debug("Registering cogs...")
    for cog_file in cogs_dir.glob("*/cog.py"):
        extension = f"cogs.{cog_file.parent.name}.cog"
        try:
            await client.load_extension(extension)
            logging.info("Loaded cog: %s", extension)
        except Exception:
            logging.exception("Failed to load cog: %s", extension)


async def main():
    await load_cogs()
    logging.debug("Starting Discord client.")
    await client.start(config["client_token"])


if __name__ == "__main__":
    asyncio.run(main())
