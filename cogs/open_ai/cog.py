import discord
from discord.ext import commands
from discord.utils import get
import logging
from openai import OpenAI
import os
import asyncio



class Roast(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.config = client.config

        # Import OPENAI API key from config file
        api_key = self.config["OPEN_AI_KEY"]
        self.aiclient = OpenAI(api_key=api_key)

    @commands.command(
            help="Debugs any given code"
    )
    async def debug(self, ctx: commands.Context, *, arg: str):
            # Get user input
            request = f"{arg}"
            try:
                # OPENAI API call with user's input
                def generate(prompt):
                    response = self.aiclient.chat.completions.create(
                        model="gpt-4o",
                        messages=[
                            {
                                "role": "system",
                                "content": "You will be provided with a piece of code, and your task is to find and fix bugs in it",
                            },
                            {"role": "user", "content": prompt},
                        ],
                        max_tokens=1024,
                    )
                    return response.choices[0].message.content

                response = generate(request)
                # Split the response if it's longer than 2000 characters
                if len(response) > 2000:
                    parts = [response[i:i+2000] for i in range(0, len(response), 2000)]
                    for part in parts:
                        await ctx.send(part)
                else:
                    await ctx.send(response)

            except Exception as e:
                logging.error(e)
                print(e)

    @commands.command(
            help="Ask the bot any question"
    )
    async def ask(self, ctx: commands.Context, *, arg: str):
        request = f"{arg}"

        try:

            def generate(prompt):
                response = self.aiclient.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=1024,
                )
                return response.choices[0].message.content

            response = generate(request)

            # Split the response if it's longer than 2000 characters
            if len(response) > 2000:
                parts = [response[i:i+2000] for i in range(0, len(response), 2000)]
                for part in parts:
                    await ctx.send(part)
            else:
                await ctx.send(response)


        except Exception as e:
            logging.error(e)
            print(e)

    @commands.command(
            help="Ask the bot to generate a roast"
    )
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

    @commands.command(
            help="Joins the voice chat to deliver generated roast"
    )
    async def vcroast(self, ctx: commands.Context, *, arg: str):
        request = f"Roast {arg}"
        logging.info(request)

        def text_to_mp3(text: str):
           
            model_file = "tts_voices/model.onnx"
            model_config = "tts_voices/model.onnx.json"

            # Check if both files exist
            if os.path.exists(model_file) and os.path.exists(model_config):
                os.system(f"echo \"{text}\" | piper --model {model_file} --output_file speech.wav")
                logging.info("Speech generation started.")
            else:
                logging.error(f"Required files not found: {model_file} or {model_config}")

        def generate_roast(prompt):
            response = self.aiclient.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are Donald Trump. You roast people. Only speak like Donald Trump",
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
            vc.play(discord.FFmpegPCMAudio("speech.wav"))
            while vc.is_playing():
                await asyncio.sleep(1)
            await vc.disconnect()
            os.remove("speech.wav")


async def setup(client: commands.Bot):
        await client.add_cog(Roast(client))
