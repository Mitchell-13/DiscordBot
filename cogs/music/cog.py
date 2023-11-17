import discord, os, asyncio, requests, logging, openai, youtube_dl, utilities
from discord.ext import commands
from discord.utils import get
import google.cloud.texttospeech as tts
from discord.ext import commands

class MusicCog(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.config = client.config

        openai.api_key = self.config["OPEN_AI_KEY"]
        bot = self.client

    FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
    sessions = []
    def check_session(self, ctx):
        """
        Checks if there is a session with the same characteristics (guild and channel) as ctx param.

        :param ctx: discord.ext.commands.Context

        :return: session()
        """
        if len(self.sessions) > 0:
            for i in self.sessions:
                if i.guild == ctx.guild and i.channel == ctx.author.voice.channel:
                    return i
            session = utilities.Session(
                ctx.guild, ctx.author.voice.channel, id=len(self.sessions))
            self.sessions.append(session)
            return session
        else:
            session = utilities.Session(ctx.guild, ctx.author.voice.channel, id=0)
            self.sessions.append(session)
            return session


    def prepare_continue_queue(self, ctx):
        """
        Used to call next song in queue.

        Because lambda functions cannot call async functions, I found this workaround in discord's api documentation
        to let me continue playing the queue when the current song ends.

        :param ctx: discord.ext.commands.Context
        :return: None
        """
        fut = asyncio.run_coroutine_threadsafe(self.continue_queue(ctx), self.client.loop)
        try:
            fut.result()
        except Exception as e:
            print(e)


    async def continue_queue(self, ctx):
        """
        Check if there is a next in queue then proceeds to play the next song in queue.

        As you can see, in this method we create a recursive loop using the prepare_continue_queue to make sure we pass
        through all songs in queue without any mistakes or interaction.

        :param ctx: discord.ext.commands.Context
        :return: None
        """
        session = self.check_session(ctx)
        if not session.q.theres_next():
            await ctx.send("Nothing in queue.")
            return

        session.q.next()

        voice = discord.utils.get(self.client.voice_clients, guild=session.guild)
        source = await discord.FFmpegOpusAudio.from_probe(session.q.current_music.url, **self.FFMPEG_OPTIONS)

        if voice.is_playing():
            voice.stop()

        voice.play(source, after=lambda e: self.prepare_continue_queue(ctx))
        await ctx.send(session.q.current_music.thumb)
        await ctx.send(f"Now Playing: {session.q.current_music.title}")


    @commands.command(name='play')
    async def play(self, ctx, *, arg):
        """
        Checks where the command's author is, searches for the music required, joins the same channel as the command's
        author and then plays the audio directly from YouTube.

        :param ctx: discord.ext.commands.Context
        :param arg: str
            arg can be url to video on YouTube or just as you would search it normally.
        :return: None
        """
        try:
            voice_channel = ctx.author.voice.channel

        # If command's author isn't connected, return.
        except AttributeError as e:
            print(e)
            await ctx.send("You are not connected to a voice channel")
            return

        # Finds author's session.
        session = self.check_session(ctx)

        # Searches for the video
        with youtube_dl.YoutubeDL({'format': 'bestaudio', 'noplaylist': 'True'}) as ydl:
            try:
                requests.get(arg)
            except Exception as e:
                print(e)
                info = ydl.extract_info(f"ytsearch:{arg}", download=False)[
                    'entries'][0]
            else:
                info = ydl.extract_info(arg, download=False)

        url = info['formats'][0]['url']
        thumb = info['thumbnails'][0]['url']
        title = info['title']

        session.q.enqueue(title, url, thumb)

        # Finds an available voice client for the bot.
        voice = discord.utils.get(self.client.voice_clients, guild=ctx.guild)
        if not voice:
            await voice_channel.connect()
            voice = discord.utils.get(self.client.voice_clients, guild=ctx.guild)

        # If it is already playing something, adds to the queue
        if voice.is_playing():
            await ctx.send(thumb)
            await ctx.send(f"Added to queue: {title}")
            return
        else:
            await ctx.send(thumb)
            await ctx.send(f"Now playing: {title}")

            # Guarantees that the requested music is the current music.
            session.q.set_last_as_current()

            source = await discord.FFmpegOpusAudio.from_probe(url, **self.FFMPEG_OPTIONS)
            voice.play(source, after=lambda ee: self.prepare_continue_queue(ctx))


    @commands.command(name='next', aliases=['skip'])
    async def skip(self, ctx):
        """
        Skips the current song, playing the next one in queue if there is one.

        :param ctx: discord.ext.commands.Context
        :return: None
        """
        # Finds author's session.
        session = self.check_session(ctx)
        # If there isn't any song to be played next, return.
        if not session.q.theres_next():
            await ctx.send("Nothing in the queue")
            return

        # Finds an available voice client for the bot.
        voice = discord.utils.get(self.client.voice_clients, guild=session.guild)

        # If it is playing something, stops it. This works because of the "after" argument when calling voice.play as it is
        # a recursive loop and the current song is already going to play the next song when it stops.
        if voice.is_playing():
            voice.stop()
            return
        else:
            # If nothing is playing, finds the next song and starts playing it.
            session.q.next()
            source = await discord.FFmpegOpusAudio.from_probe(session.q.current_music.url, **self.FFMPEG_OPTIONS)
            voice.play(source, after=lambda e: self.prepare_continue_queue(ctx))
            return


    @commands.command(name='print')
    async def print_info(self, ctx):
        """
        A debug command to find session id, what is current playing and what is on the queue.
        :param ctx: discord.ext.commands.Context
        :return: None
        """
        session = self.check_session(ctx)
        await ctx.send(f"Session ID: {session.id}")
        await ctx.send(f"Música atual: {session.q.current_music.title}")
        queue = [q[0] for q in session.q.queue]
        await ctx.send(f"Queue: {queue}")


    @commands.command(name='leave')
    async def leave(self, ctx):
        """
        If bot is connected to a voice channel, it leaves it.

        :param ctx: discord.ext.commands.Context
        :return: None
        """
        voice = discord.utils.get(self.client.voice_clients, guild=ctx.guild)
        if voice.is_connected:
            self.check_session(ctx).q.clear_queue()
            await voice.disconnect()
        else:
            await ctx.send("Bot not connect, so it can't leave.")


    @commands.command(name='pause')
    async def pause(self, ctx):
        """
        If playing audio, pause it.

        :param ctx: discord.ext.commands.Context
        :return: None
        """
        voice = discord.utils.get(self.client.voice_clients, guild=ctx.guild)
        if voice.is_playing():
            voice.pause()
        else:
            await ctx.send("Nothing is playing")


    @commands.command(name='resume')
    async def resume(self, ctx):
        """
        If audio is paused, resumes playing it.

        :param ctx: discord.ext.commands.Context
        :return: None
        """
        voice = discord.utils.get(self.client.voice_clients, guild=ctx.guild)
        if voice.is_paused:
            voice.resume()
        else:
            await ctx.send("Music is already paused")


    @commands.command(name='stop')
    async def stop(self, ctx):
        """
        Stops playing audio and clears the session's queue.

        :param ctx: discord.ext.commands.Context
        :return: None
        """
        session = self.check_session(ctx)
        voice = discord.utils.get(self.client.voice_clients, guild=ctx.guild)
        if voice.is_playing:
            voice.stop()
            session.q.clear_queue()
        else:
            await ctx.send("Nothing is playing")