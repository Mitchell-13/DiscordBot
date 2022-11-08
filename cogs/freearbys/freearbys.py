import discord
from discord.ext import commands, tasks
from datetime import datetime, timedelta
import random
import requests
from dateutil import tz
import asyncio
import logging


lastPlayed = None
rand = random.randrange(0,5)
MST = tz.gettz('Mountain Standard Time')


class freearbys(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.config = client.config
        self.last_played_intro = None

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
                return [jazzScore, gameScore]

        @tasks.loop(time=datetime.time(12, 0, 0, 0, tzinfo=MST))
        async def free_food_message():
            time = datetime.strftime(datetime.now(), '%H:%M')
            global lastPlayed
            if (lastPlayed == None or abs((lastPlayed - datetime.now())) > timedelta(hours=2)) and time == "12:00":
                l = check_game()
                if l is not None:
                    channel = client.get_channel(self.config['channel_gamers'])
                    if l[0] >= 111:
                        await channel.send(f"{self.config['role_arbys']}\n{self.config['msg'][rand]}\n\nYesterday's game score: \n{l[1]}")
                    else:
                        await channel.send(f"No free Arby's today :(\n\nYesterday's game score: \n{l[1]}")
                    lastPlayed = datetime.now()



        @commands.Cog.listener()
        async def start(self, ctx: commands.Context):

            free_food_message.start()
    
   

async def setup(client: commands.Bot):
    await client.add_cog(freearbys(client))
