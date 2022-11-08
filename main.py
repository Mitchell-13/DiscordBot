import discord
from discord.ext import commands
import json
import logging
import asyncio
import os


# Logging
logging.basicConfig(
    filename="jazzbot.log",
    encoding='utf-8',
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S'
    )

# Config
config_filename = 'config.json'
logging.debug(f'Opening config file: {config_filename}')
with open(config_filename, 'r') as cjson:
    logging.debug('Loading JSON from config file.')
    config = json.load(cjson)
    logging.debug('Successfully loaded configuration.')

# Setup client
logging.debug('Setting up Discord client/bot.')
intents = discord.Intents.all()
intents.message_content = True
client = commands.Bot(command_prefix=config['command_prefix'], intents=intents)
client.config = config


@client.event
async def on_ready():
    logging.info(f'''We have logged in as {client.user}   
Command prefix = \'{config['command_prefix']}\'''')

async def main():
    # Dynamically register cogs
    logging.debug('Registering cogs...')
    for folder in os.listdir('cogs'):
        if os.path.exists(os.path.join('cogs', folder, 'cog.py')):
            logging.debug(f'Found cog {folder}.')
            await client.load_extension(f'cogs.{folder}.cog')

    logging.debug('Starting Discord client.')
    await client.start(config['client_token'])

if __name__ == '__main__':
    asyncio.run(main())