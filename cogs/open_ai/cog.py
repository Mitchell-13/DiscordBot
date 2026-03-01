import asyncio
import logging
import subprocess
from pathlib import Path

import discord
from discord.ext import commands
from openai import OpenAI


MAX_DISCORD_MESSAGE_LEN = 2000


class Roast(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.config = client.config
        self.aiclient = OpenAI(api_key=self.config["OPEN_AI_KEY"])

    async def _send_long_message(self, ctx: commands.Context, message: str) -> None:
        if not message:
            await ctx.send("I got an empty response. Please try again.")
            return

        parts = [
            message[i : i + MAX_DISCORD_MESSAGE_LEN]
            for i in range(0, len(message), MAX_DISCORD_MESSAGE_LEN)
        ]
        for part in parts:
            await ctx.send(part)

    async def _generate_chat_completion(
        self,
        messages: list[dict[str, str]],
        *,
        model: str,
        max_completion_tokens: int,
    ) -> str:
        # OpenAI call is synchronous in this SDK usage; offload it to a thread.
        def _generate() -> str:
            response = self.aiclient.chat.completions.create(
                model=model,
                messages=messages,
                max_completion_tokens=max_completion_tokens,
            )
            return response.choices[0].message.content or ""

        return await asyncio.to_thread(_generate)

    @commands.command(help="Debugs any given code")
    async def debug(self, ctx: commands.Context, *, arg: str):
        try:
            response = await self._generate_chat_completion(
                [
                    {
                        "role": "system",
                        "content": (
                            "You will be provided with a piece of code, and your task "
                            "is to find and fix bugs in it"
                        ),
                    },
                    {"role": "user", "content": arg},
                ],
                model="gpt-4o-mini",
                max_completion_tokens=1024,
            )
            await self._send_long_message(ctx, response)
        except Exception:
            logging.exception("debug command failed")
            await ctx.send("Something went wrong while debugging that snippet.")

    @commands.command(help="Ask the bot any question")
    async def ask(self, ctx: commands.Context, *, arg: str):
        try:
            response = await self._generate_chat_completion(
                [{"role": "user", "content": arg}],
                model="gpt-4o-mini",
                max_completion_tokens=1024,
            )
            await self._send_long_message(ctx, response)
        except Exception:
            logging.exception("ask command failed")
            await ctx.send("I hit an error while answering that. Please try again.")

    @commands.command(help="Ask the bot to generate a roast")
    async def roast(self, ctx: commands.Context, *, arg: str):
        request = f"Roast {arg}"
        try:
            response = await self._generate_chat_completion(
                [
                    {"role": "system", "content": "You are an AI that roasts people"},
                    {"role": "user", "content": request},
                ],
                model="gpt-4o-mini",
                max_completion_tokens=256,
            )
            await self._send_long_message(ctx, response)
        except Exception:
            logging.exception("roast command failed")
            await ctx.send("I couldn't generate a roast right now.")

    def _text_to_wav(self, text: str) -> Path:
        model_file = Path("tts_voices/model.onnx")
        model_config = Path("tts_voices/model.onnx.json")
        output_file = Path("speech.wav")

        if not model_file.exists() or not model_config.exists():
            raise FileNotFoundError(
                f"Required files not found: {model_file} and/or {model_config}"
            )

        process = subprocess.run(
            ["piper", "--model", str(model_file), "--output_file", str(output_file)],
            input=text,
            text=True,
            capture_output=True,
            check=False,
        )
        if process.returncode != 0:
            raise RuntimeError(
                f"piper exited with {process.returncode}: {process.stderr.strip()}"
            )

        return output_file

    async def _connect_to_author_channel(
        self, ctx: commands.Context
    ) -> discord.VoiceClient | None:
        if not ctx.author.voice or not ctx.author.voice.channel:
            await ctx.send("You need to be in a voice channel first.")
            return None

        target_channel = ctx.author.voice.channel
        voice_client = discord.utils.get(self.client.voice_clients, guild=ctx.guild)

        try:
            if voice_client and voice_client.is_connected():
                if voice_client.channel != target_channel:
                    await voice_client.move_to(target_channel)
                return voice_client

            return await target_channel.connect()
        except discord.ClientException as exc:
            logging.exception("voice connection error")
            await ctx.send(f"I couldn't join voice: {exc}")
            return None

    @commands.command(help="Joins voice chat to deliver generated roast")
    async def vcroast(self, ctx: commands.Context, *, arg: str):
        request = f"Roast {arg}"
        logging.info("vcroast request: %s", request)

        try:
            response = await self._generate_chat_completion(
                [
                    {
                        "role": "system",
                        "content": (
                            "You are Donald Trump. You roast people. "
                            "Only speak like Donald Trump"
                        ),
                    },
                    {"role": "user", "content": request},
                ],
                model="gpt-4o-mini",
                max_completion_tokens=256,
            )

            output_wav = await asyncio.to_thread(self._text_to_wav, response)

            voice_client = await self._connect_to_author_channel(ctx)
            if not voice_client:
                return

            if voice_client.is_playing():
                voice_client.stop()

            playback_finished = asyncio.Event()

            def _after_playback(error: Exception | None):
                if error:
                    logging.error("audio playback failed: %s", error)
                self.client.loop.call_soon_threadsafe(playback_finished.set)

            voice_client.play(discord.FFmpegPCMAudio(str(output_wav)), after=_after_playback)
            await playback_finished.wait()

            await voice_client.disconnect()
            if output_wav.exists():
                output_wav.unlink()

        except FileNotFoundError as exc:
            logging.exception("vcroast missing tts files")
            await ctx.send(f"TTS setup issue: {exc}")
        except Exception:
            logging.exception("vcroast command failed")
            await ctx.send("I ran into an error while doing vcroast.")


async def setup(client: commands.Bot):
    await client.add_cog(Roast(client))
