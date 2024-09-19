import discord
from discord.ext import commands
from discord.utils import get
import logging
from openai import OpenAI
import os
import asyncio



class RoastCog(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.config = client.config

        api_key = self.config["OPEN_AI_KEY"]
        self.aiclient = OpenAI(api_key=api_key)
        bot = self.client

    @commands.command()
    async def debug(self, ctx: commands.Context, *, arg: str):
            request = f"{arg}"

            try:

                def generate(prompt):
                    response = self.client.chat.completions.create(
                        model="gpt-4o",
                        messages=[
                            {
                                "role": "system",
                                "content": "You will be provided with a piece of code, and your task is to find and fix bugs in it.",
                            },
                            {"role": "user", "content": prompt},
                        ],
                        max_tokens=512,
                    )
                    return response.choices[0].message.content

                response = generate(request)
                await ctx.send(response)

            except Exception as e:
                logging.error(e)
                print(e)

    @commands.command()
    async def cmds(self, ctx: commands.Context):
        try:
            await ctx.send(
                "Bot Commands:\n$roast will generate a roast\n$vcroast will generate a roast and join a Voice Channel\n$debug will debug given code\n$ask will generate a response to your input"
            )

        except Exception as e:
            logging.error(e)
            print(e)

    @commands.command()
    async def ask(self, ctx: commands.Context, *, arg: str):
        request = f"{arg}"

        try:

            def generate(prompt):
                response = self.aiclient.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=256,
                )
                return response.choices[0].message.content

            response = generate(request)
            await ctx.send(response)

        except Exception as e:
            logging.error(e)
            print(e)

    @commands.command()
    async def roast(self, ctx: commands.Context, *, arg: str):
        request = f"Roast {arg}"

        try:

            def generate_roast(prompt):
                response = self.aiclient.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {
                            "role": "system",
                            "content": "You are an AI that roasts people",
                        },
                        {"role": "user", "content": prompt},
                    ],
                    max_tokens=256,
                )
                return response.choices[0].message.content

            response = generate_roast(request)
            await ctx.send(response)

        except Exception as e:
            logging.error(e)
            print(e)

    @commands.command()
    async def vcroast(self, ctx: commands.Context, *, arg: str):
        request = f"Roast {arg}"
        logging.info(request)

        def text_to_mp3(text: str):
            speech_file_path = "./speech.mp3"
            response = self.aiclient.audio.speech.create(
                model="tts-1",
                voice="alloy",
                input=text,
            )
            filename = "speech.mp3"
            response.stream_to_file(speech_file_path)
            logging.info(f'Generated speech saved to "{filename}"')

            return filename

        def generate_roast(prompt):
            response = self.aiclient.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an AI that roasts people",
                    },
                    {"role": "user", "content": prompt},
                ],
                max_tokens=256,
            )
            return response.choices[0].message.content

        try:
            response = generate_roast(request)
            text = response
            logging.info(text)
            text_to_mp3(text)

        except Exception as e:
            logging.error(e)
            print(e)
        if ctx.author.voice:
            channel = ctx.author.voice.channel
            vc = await channel.connect()
            vc.play(discord.FFmpegPCMAudio("speech.mp3"))
            while vc.is_playing():
                await asyncio.sleep(1)
            await vc.disconnect()
            os.remove("speech.mp3")


async def setup(client: commands.Bot):
        await client.add_cog(RoastCog(client))
