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
    async def roast(self, ctx: commands.Context, *, arg: str):
        request = f"Roast {arg}"

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

    @commands.command()
    async def vcroast(self, ctx: commands.Context, *, arg: str):
        request = f"Roast {arg}"
        logging.info(request)
        def text_to_wav(voice_name: str, text: str):
            language_code = "-".join(voice_name.split("-")[:2])
            text_input = tts.SynthesisInput(text=text)
            voice_params = tts.VoiceSelectionParams(
                language_code=language_code, name=voice_name
            )
            audio_config = tts.AudioConfig(audio_encoding=tts.AudioEncoding.LINEAR16)

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
                        "content": "You are a bully who roasts people, try to make them cry. Use profanity"
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
            text = response['choices'][0]['message']['content']
            logging.info(text)
            mp3 =text_to_wav("en-US-Neural2-A", text)
            
        except Exception as e:
            logging.error(e)
            print(e)
        if ctx.author.voice:
            channel = ctx.author.voice.channel
            vc = await channel.connect()
            vc.play(discord.FFmpegPCMAudio('audio.wav'))
            while vc.is_playing():
                await asyncio.sleep(1)
            await vc.disconnect()
            os.remove("audio.wav")




async def setup(client: commands.Bot):
    await client.add_cog(RoastCog(client))