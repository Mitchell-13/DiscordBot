import discord
from discord.ext import tasks, commands
import requests
from datetime import datetime, timedelta
import random
import json
import logging
import asyncio
import os


# Logging
logging.basicConfig(
    filename="jazzbot.log",
    encoding='utf-8',
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.DEBUG,
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


def check_game():
# Check if a game happened yesterday and get team scores score
    date_yesterday = datetime.strftime(datetime.now() - timedelta(1), '%Y-%m-%d')
    r = requests.get(f"https://balldontlie.io/api/v1/games?start_date={date_yesterday}&end_date={date_yesterday}&team_ids[]=29")
    j = r.json()
    length = j['meta']['total_count']
    if length > 0:
        # Find game scores and opposing team name
        if j['data'][0]['home_team']['name'] == 'Jazz':
            jazzScore = j['data'][0]['home_team_score']
            opScore = j['data'][0]['visitor_team_score']
            opName = j['data'][0]['visitor_team']['full_name']
        else:
            jazzScore = j['data'][0]['visitor_team_score']
            opScore = j['data'][0]['home_team_score']
            opName = j['data'][0]['home_team']['full_name']
        gameScore = f"Utah Jazz: {str(jazzScore)} | {opName}: {str(opScore)}"
        return [jazzScore, gameScore];

@tasks.loop(minutes=1)
async def free_food_message():
    time = datetime.strftime(datetime.now(), '%H:%M')
    global lastPlayed
    if (lastPlayed == None or abs((lastPlayed - datetime.now())) > timedelta(hours=2)) and time == "12:00":
        l = check_game()
        if l is not None:
            channel = client.get_channel(config['channel_gamers'])
            if l[0] >= 111:
                await channel.send(f"{config['role_arbys']}\n{config['msg'][rand]}\n\nYesterday's game score: \n{l[1]}")
            else:
                await channel.send(f"No free Arby's today :(\n\nYesterday's game score: \n{l[1]}")
            lastPlayed = datetime.now()

# send message about game outcome
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