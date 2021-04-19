import discord
from discord.ext import commands
from discord.voice_client import VoiceClient
import os
import re
import datetime
from dotenv import load_dotenv
import youtube_dl
import asyncio
from urllib import parse, request

intents = discord.Intents.default()
intents.members = True

load_dotenv()
TOKEN = os.getenv('Discord_Token')

client = commands.Bot(command_prefix='-')

# Commands
youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    # bind to ipv4 since ipv6 addresses cause issues sometimes
    'source_address': '0.0.0.0'
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


@client.command()
async def ping(ctx):
    await ctx.send(f'**Pong!** Latency:{round(client.latency * 1000)}ms')


@client.command()
async def hello(ctx):
    await ctx.send('Miauuuuu')


@client.command()
async def youtube(ctx, *, search):

    query_string = parse.urlencode({'search_query': search})
    html_content = request.urlopen(
        'http://www.youtube.com/results?' + query_string)
    search_results = re.findall(
        r'/watch\?v=(.{11})', html_content.read().decode())
    await ctx.send('https://www.youtube.com/watch?v=' + search_results[0])


@client.command()
async def play(ctx, url):
    if not ctx.message.author.voice:
        await ctx.send('Para poner musica, necesitas estar un canal de voz')
        return
    else:
        channel = ctx.message.author.voice.channel
    await channel.connect()
    server = ctx.message.guild
    voice_channel = server.voice_client

    async with ctx.typing():

        query_string = parse.urlencode({'search_query': url})
        html_content = request.urlopen(
            'http://www.youtube.com/results?' + query_string)
        search_results = re.findall(
            r'/watch\?v=(.{11})', html_content.read().decode())

    player = await YTDLSource.from_url('https://www.youtube.com/watch?v=' + search_results[0], loop=client.loop)
    voice_channel.play(player, after=lambda e: print(
        'Player error: %s' % e) if e else None)
    await ctx.send('**Now playing:** {}'.format(player.title))


@client.command()
async def stop(ctx):

    if not ctx.message.author.voice:
        await ctx.send('Para sacar musica, debes estar en un canal de voz.')
    else:
        voice_client = ctx.message.guild.voice_client
        await voice_client.disconnect()


@client.command()
async def eren(ctx):
    await ctx.send('https://www.youtube.com/watch?v=nOufJAzy3h8')


@client.command()
async def info(ctx):
    embed = discord.Embed(
        title=f"{ctx.guild.name}", description="Descripcion del servidor", timestamp=datetime.datetime.utcnow(), color=discord.Color.green())
    embed.add_field(name="Server created at",
                    value=f"{ctx.guild.created_at}")
    embed.add_field(name="Server Owner", value=f"{ctx.guild.owner}")
    embed.add_field(name="Server Region", value=f"{ctx.guild.region}")
    embed.add_field(name="Server ID", value=f"{ctx.guild.id}")

    file = discord.File(r"img\KingGandalf.jpg")
    embed.set_image(url="attachment://KingGandalf.jpg")

    await ctx.send(file=file, embed=embed)


@client.event
async def on_ready():
    await client.change_presence(activity=discord.Streaming(name='Bot ON', url="http://www.twitch.tv/DragonHack"))
    print('My bot is ready')


client.run(TOKEN)
