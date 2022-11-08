from discord.ext import commands, tasks
from datetime import datetime, timedelta
import random
import requests
from dateutil import tz
import logging

class freearbys(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.config = client.config
        self.last_played_intro = None

    lastPlayed = None
    rand = random.randrange(0,5)
    MST = tz.gettz('Mountain Standard Time')

    @commands.Cog.listener()
    async def on_ready(self):
        
        # Check yesterdays games to see if jazz won | returns jazz score and game result 
        def check_game():
            date_yesterday = datetime.strftime(datetime.now() - timedelta(1), '%Y-%m-%d')
            r = requests.get(f"https://balldontlie.io/api/v1/games?start_date={date_yesterday}&end_date={date_yesterday}&team_ids[]=29")
            logging.debug(f"status code of api query for yesterday's game: {r}")
            j = r.json()
            length = j['meta']['total_count']
            if length > 0:
                logging.debug(f"Found game for {date_yesterday}")
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

        # Count how many times free arby's has been won this season
        def check_count():
            count = 0
            r = requests.get("https://balldontlie.io/api/v1/games?start_date=2022-10-19&team_ids[]=29")
            logging.debug(f"status code of api query for all games: {r}")
            j = r.json()
            for games in j['data']:
                if games['home_team']['full_name'] == "Utah Jazz":
                    if games['home_team_score'] >= 111:
                        count +=1
                if games['visitor_team']['full_name'] == "Utah Jazz":
                    if games['visitor_team_score'] >= 111:
                        count+=1
            return count

        # Send message every day at 12:00
        @tasks.loop(minutes=1)
        async def free_food_message():
            time = datetime.strftime(datetime.now(), '%H:%M')
            global lastPlayed
            if (self.lastPlayed == None or abs((self.lastPlayed - datetime.now())) > timedelta(hours=2)) and time == "12:00":
                l = check_game()
                count = check_count()
                if l is not None:
                    channel = self.client.get_channel(self.config['channel_bot'])
                    if l[0] >= 111:
                        await channel.send(f"{self.config['role_arbys']}\n{self.config['msg'][self.rand]}\n\nYesterday's game score: \n{l[1]}\n\nArby's won this season: {count}")
                        logging.info("send message for free arby's")
                    else:
                        await channel.send(f"No free Arby's today :(\n\nYesterday's game score: \n{l[1]}\n\nFree Arby's this season so far: {count}")
                        logging.info("sent message for no arby's")
                    lastPlayed = datetime.now()

        free_food_message.start()
    
async def setup(client: commands.Bot):
    await client.add_cog(freearbys(client))
