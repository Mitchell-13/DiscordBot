from discord.ext import commands, tasks
from datetime import datetime, timedelta, time
import random
import requests
import logging

class freearbys(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.config = client.config

        self.free_food_message.start()
   
    # Check yesterdays games to see if jazz won | returns jazz score and game result 
    def check_game(self):
        date_yesterday = datetime.strftime(datetime.now() - timedelta(1), '%Y-%m-%d')
        r = requests.get(f"https://balldontlie.io/api/v1/games?start_date={date_yesterday}&end_date={date_yesterday}&team_ids[]=29")
        logging.debug(f"status code of api query for yesterday's game: {r}")
        j = r.json()
        length = j['meta']['total_count']
        if length == 0:
            return
        logging.debug(f"Found game for {date_yesterday}")
        if j['data'][0]['home_team']['name'] == 'Jazz':
            jazz_score = j['data'][0]['home_team_score']
            opScore = j['data'][0]['visitor_team_score']
            opName = j['data'][0]['visitor_team']['full_name']
        else:
            jazz_score = j['data'][0]['visitor_team_score']
            opScore = j['data'][0]['home_team_score']
            opName = j['data'][0]['home_team']['full_name']
        game_score = f"Utah Jazz: {str(jazz_score)} | {opName}: {str(opScore)}"
        return [jazz_score, game_score]

    # Count how many times free arby's has been won this season
    def check_count(self):
        count = 0
        r = requests.get("https://balldontlie.io/api/v1/games?start_date=2023-10-19&team_ids[]=29")
        j = r.json()
        page_count = j['meta']['total_pages']
        for i in range(page_count):
            r = requests.get(f"https://balldontlie.io/api/v1/games?start_date=2023-10-19&team_ids[]=29&page={i + 1}")
            data=r.json()
            for games in data['data']:
                if games['home_team']['full_name'] == "Utah Jazz" and games['home_team_score'] >= 111:
                    count +=1
                if games['visitor_team']['full_name'] == "Utah Jazz" and games['visitor_team_score'] >= 111:
                    count+=1
        return count

    # Send message every day at 10:00
    @tasks.loop(time=time(hour = 17, minute = 0,))
    async def free_food_message(self):
        score = self.check_game()
        if score is None:
            return
        count = self.check_count()
        channel = self.client.get_channel(self.config['channel_to_send'])
        jazz_score = score[0]
        if jazz_score >= 111:
            rand = random.randrange(0,5)
            await channel.send(f"{self.config['role_to_notify']}\n{self.config['msg'][rand]}\n\nYesterday's game score: \n{score[1]}\n\nArby's won this season: {count}")
            logging.info("sent message for free arby's")
        else:
            await channel.send(f"No free Arby's today :(\n\nYesterday's game score: \n{score[1]}\n\nFree Arby's this season so far: {count}")
            logging.info("sent message for no arby's")
    
async def setup(client: commands.Bot):
    await client.add_cog(freearbys(client))
