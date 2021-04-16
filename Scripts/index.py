import discord
from discord.ext import commands
from discord.utils import get
import datetime
from urllib import parse, request
import re
import os
from dotenv import load_dotenv


intents = discord.Intents.default()
intents.members = True

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='-', intents=intents)


@bot.command()
async def hi(ctx):
    await ctx.send('MIAUUUUU')


@bot.command()
async def sum(ctx, num1, num2):
    response = int(num1) + int(num2)
    await ctx.send(response)


@bot.command(pass_context=True)
async def connect(ctx):
    channel = ctx.message.author.voice.channel
    if not channel:
        await ctx.send('No estas conectado a un canal de VOZ')
        return
    voice = get(bot.voice_clients, guild=ctx.guild)
    if voice and voice.is_connected():
        await voice.move_to(channel)
    else:
        voice = await channel.connect()


@bot.command()
async def info(ctx):
    embed = discord.Embed(
        title=f"{ctx.guild.name}", description="Descripcion del servidor", timestamp=datetime.datetime.utcnow(), color=discord.Color.green())
    embed.add_field(name="Server created at", value=f"{ctx.guild.created_at}")
    embed.add_field(name="Server Owner", value=f"{ctx.guild.owner}")
    embed.add_field(name="Server Region", value=f"{ctx.guild.region}")
    embed.add_field(name="Server ID", value=f"{ctx.guild.id}")

    file = discord.File(r"img\KingGandalf.jpg")
    embed.set_image(url="attachment://KingGandalf.jpg")

    await ctx.send(file=file, embed=embed)


@bot.command()
async def eren(ctx):
    await ctx.send(r'https://www.youtube.com/watch?v=nOufJAzy3h8')


@bot.command()
async def youtube(ctx, *, search):

    query_string = parse.urlencode({'search_query': search})
    html_content = request.urlopen(
        'http://www.youtube.com/results?' + query_string)
    search_results = re.findall(
        r'/watch\?v=(.{11})', html_content.read().decode())
    await ctx.send('https://www.youtube.com/watch?v=' + search_results[0])

# Events


@ bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Streaming(name='Bot ON', url="http://www.twitch.tv/DragonHack"))
    print('My bot is ready')


# Heroku

bot.run(TOKEN)
