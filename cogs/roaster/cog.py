import discord
from discord.ext import commands
import logging
import openai

class RoastCog(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.config = client.config

        openai.api_key = self.config["OPEN_AI_KEY"]

    @commands.command()
    async def roast(self, ctx: commands.Context, *, arg: str):
        print("got message")
        request = f"Roast {arg}"
        print(request)

        try:
            def generate_roast(prompt):
                response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a bully who roasts people, try to make them cry"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=256,
                            )
                return response
            response = generate_roast(request)
            await ctx.send(response['choices'][0]['message']['content'])
            
            
        except Exception as e:
            logging.error(e)
            print(e)

        
async def setup(client: commands.Bot):
    await client.add_cog(RoastCog(client))