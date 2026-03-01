import asyncio
import json
import logging
import os
import urllib.error
import urllib.request

import discord
from discord.ext import commands
from openai import OpenAI


class Roast(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.config = client.config

        # Import OPENAI API key from config file
        api_key = self.config["OPEN_AI_KEY"]
        self.aiclient = OpenAI(api_key=api_key)

    def _github_headers(self):
        token = self.config.get("GITHUB_TOKEN", "")
        return {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28",
            "Content-Type": "application/json",
        }

    def _create_change_request_issue(self, request: str, requested_by: discord.Member):
        repo = self.config.get("GITHUB_REPO", "")
        endpoint = f"https://api.github.com/repos/{repo}/issues"

        issue_payload = {
            "title": f"AI Change Request: {request[:72]}",
            "body": (
                "## Requested Change\n"
                f"{request}\n\n"
                "## Requested By\n"
                f"- Discord user: {requested_by} (`{requested_by.id}`)\n\n"
                "## Notes\n"
                "- This issue was created by the Discord bot.\n"
                "- Run the AI automation workflow and open a PR for review."
            ),
            "labels": self.config.get("GITHUB_CHANGE_REQUEST_LABELS", ["ai-change"]),
        }

        req = urllib.request.Request(
            endpoint,
            data=json.dumps(issue_payload).encode("utf-8"),
            headers=self._github_headers(),
            method="POST",
        )

        with urllib.request.urlopen(req, timeout=20) as response:
            return json.loads(response.read().decode("utf-8"))

    @commands.command(help="Debugs any given code")
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
                parts = [response[i : i + 2000] for i in range(0, len(response), 2000)]
                for part in parts:
                    await ctx.send(part)
            else:
                await ctx.send(response)

        except Exception as e:
            logging.error(e)
            print(e)

    @commands.command(help="Ask the bot any question")
    async def ask(self, ctx: commands.Context, *, arg: str):
        request = f"{arg}"

        try:

            def generate(prompt):
                response = self.aiclient.chat.completions.create(
                    model="gpt-5-nano",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=1024,
                )
                return response.choices[0].message.content

            response = generate(request)

            # Split the response if it's longer than 2000 characters
            if len(response) > 2000:
                parts = [response[i : i + 2000] for i in range(0, len(response), 2000)]
                for part in parts:
                    await ctx.send(part)
            else:
                await ctx.send(response)

        except Exception as e:
            logging.error(e)
            print(e)

    @commands.command(help="Ask the bot to generate a roast")
    async def roast(self, ctx: commands.Context, *, arg: str):
        request = f"Roast {arg}"

        try:

            def generate_roast(prompt):
                response = self.aiclient.chat.completions.create(
                    model="gpt-5-nano",
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

    @commands.command(help="Joins the voice chat to deliver generated roast")
    async def vcroast(self, ctx: commands.Context, *, arg: str):
        request = f"Roast {arg}"
        logging.info(request)

        def text_to_mp3(text: str):

            model_file = "tts_voices/model.onnx"
            model_config = "tts_voices/model.onnx.json"

            # Check if both files exist
            if os.path.exists(model_file) and os.path.exists(model_config):
                os.system(
                    f"echo \"{text}\" | piper --model {model_file} --output_file speech.wav"
                )
                logging.info("Speech generation started.")
            else:
                logging.error(f"Required files not found: {model_file} or {model_config}")

        def generate_roast(prompt):
            response = self.aiclient.chat.completions.create(
                model="gpt-5-nano",
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

    @commands.command(
        name="codexchange",
        help="Create a GitHub change request for AI/Codex automation (restricted users only)",
    )
    async def codex_change_request(self, ctx: commands.Context, *, arg: str):
        allowed_users = {int(uid) for uid in self.config.get("CODEX_ALLOWED_USERS", [])}
        if ctx.author.id not in allowed_users:
            await ctx.send("You are not allowed to use this command.")
            return

        if not self.config.get("GITHUB_REPO") or not self.config.get("GITHUB_TOKEN"):
            await ctx.send("Bot is missing GitHub configuration for change requests.")
            return

        try:
            issue = self._create_change_request_issue(arg, ctx.author)
            reviewer_id = self.config.get("CODEX_REVIEWER_DISCORD_ID")
            reviewer_mention = f"<@{reviewer_id}> " if reviewer_id else ""
            await ctx.send(
                f"{reviewer_mention}New Codex change request created: {issue['html_url']}\n"
                "I will ping you again when a PR is ready to review."
            )
        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8", errors="replace")
            logging.error("GitHub issue creation failed: %s", error_body)
            await ctx.send(
                "Failed to create the GitHub change request. Check bot logs for details."
            )
        except Exception as e:
            logging.error("Unexpected error creating change request: %s", e)
            await ctx.send("Failed to create the GitHub change request.")


async def setup(client: commands.Bot):
    await client.add_cog(Roast(client))
