import discord
from discord.ext import tasks
import requests
from datetime import datetime, timedelta
import random
from os import getenv
from dotenv import load_dotenv

load_dotenv()
token = getenv('TOKEN')
channel_gamers = 763214150423674891
channel_bot = 361286957587890187
role_arbys = '<@&1037279992087846952>'
lastPlayed = None
msg = [
    " Free Arby's today with the Jazz app!!!",
    " Free food alert! Use the jazz app for free Arby's all today",
    " What do you call Arby's barbeque sauce? \nARBYque sauce!! \n\nAnyways... free food today with the Jazz app",
    " Did you hear they had to close the Arby's in the Burj Khalifa? \n The steaks were too high \n\nGet your free Arby's today with the Jazz app.",
    " What is a pirates favorite restaurant? \nArrrby's\n\nFree food today in the Jazz app"]
rand = random.randrange(0,5)
intents = discord.Intents.all()
client = discord.Client(intents=intents)

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
            channel = client.get_channel(channel_gamers)
            if l[0] >= 111:
                await channel.send(f"{role_arbys}\n{msg[rand]}\n\nYesterday's game score: \n{l[1]}")
            else:
                await channel.send(f"No free Arby's today :(\n\nYesterday's game score: \n{l[1]}")
            lastPlayed = datetime.now()

# send message about game outcome
@client.event
async def on_ready():
    await free_food_message.start()

client.run(token)
