import discord
from discord.ext import commands
import logging

class BirthdayCog(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.config = client.config

    @commands.Cog.listener()
    async def on_message(self, message: discord.message.Message):
        # Ignore messages sent by bot
        if message.author == self.client.user:
            return

        if message.author.name == self.config['bday-user']:
            logging.debug(f'User {message.author.name} sent a message.')
            await message.channel.send("Hey, the target user said something in the target channel!")

async def setup(client: commands.Bot):
    await client.add_cog(BirthdayCog(client))