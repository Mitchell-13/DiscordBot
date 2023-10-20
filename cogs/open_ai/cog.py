import discord
from discord.ext import commands
from discord.utils import get
import logging
import openai
import google.cloud.texttospeech as tts
import os
import asyncio


class RoastCog(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.config = client.config

        openai.api_key = self.config["OPEN_AI_KEY"]
        bot = self.client

    @commands.command()
    async def debug(self, ctx: commands.Context, *, arg: str):
        request = f"{arg}"

        try:

            def generate(prompt):
                response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[
                        {
                            "role": "system",
                            "content": "You will be provided with a piece of code, and your task is to find and fix bugs in it.",
                        },
                        {"role": "user", "content": prompt},
                    ],
                    max_tokens=256,
                )
                return response

            response = generate(request)
            await ctx.send(response["choices"][0]["message"]["content"])

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
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=256,
                )
                return response

            response = generate(request)
            await ctx.send(response["choices"][0]["message"]["content"])

        except Exception as e:
            logging.error(e)
            print(e)

    @commands.command()
    async def roast(self, ctx: commands.Context, *, arg: str):
        request = f"Roast {arg}"

        try:

            def generate_roast(prompt):
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {
                            "role": "system",
                            "content": "You are an AI that roasts people. Speak only like stereotypical Donald Trump",
                        },
                        {"role": "user", "content": prompt},
                    ],
                    max_tokens=256,
                )
                return response

            response = generate_roast(request)
            await ctx.send(response["choices"][0]["message"]["content"])

        except Exception as e:
            logging.error(e)
            print(e)

    @commands.command()
    async def vcroast(self, ctx: commands.Context, *, arg: str):
        request = f"Roast {arg}"
        logging.info(request)

        def text_to_wav(voice_name: str, text: str):
            language_code = "-".join(voice_name.split("-")[:2])
            text_input = tts.SynthesisInput(text=text)
            voice_params = tts.VoiceSelectionParams(
                language_code=language_code, name=voice_name, 
            )
            audio_config = tts.AudioConfig(
                audio_encoding=tts.AudioEncoding.LINEAR16, pitch=-4.8
                )

            client = tts.TextToSpeechClient()
            response = client.synthesize_speech(
                input=text_input,
                voice=voice_params,
                audio_config=audio_config,
            )

            filename = "audio.wav"
            with open(filename, "wb") as out:
                out.write(response.audio_content)
                print(f'Generated speech saved to "{filename}"')

            return filename

        try:

            def generate_roast(prompt):
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {
                            "role": "system",
                            "content": "You are an AI that roasts people. Speak only like stereotypical Donald Trump",
                        },
                        {"role": "user", "content": prompt},
                    ],
                    max_tokens=256,
                )
                return response

            response = generate_roast(request)
            text = response["choices"][0]["message"]["content"]
            logging.info(text)
            mp3 = text_to_wav("en-US-Neural2-J", text)

        except Exception as e:
            logging.error(e)
            print(e)
        if ctx.author.voice:
            channel = ctx.author.voice.channel
            vc = await channel.connect()
            vc.play(discord.FFmpegPCMAudio("audio.wav"))
            while vc.is_playing():
                await asyncio.sleep(1)
            await vc.disconnect()
            os.remove("audio.wav")


async def setup(client: commands.Bot):
    await client.add_cog(RoastCog(client))
