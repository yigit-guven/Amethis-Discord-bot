import os
import discord
from discord.ext import commands

# Try to load from .env file for local development, 
# but will use Heroku's environment variables in production
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("Loaded environment variables from .env file")
except ImportError:
    print("dotenv not available, using system environment variables")

TOKEN = os.getenv('DISCORD_TOKEN')

if not TOKEN:
    raise ValueError("No DISCORD_TOKEN found in environment variables!")

bot = commands.Bot(command_prefix='!')

@bot.event
async def on_ready():
    print(f'{bot.user.name} has logged in successfully!')

@bot.command(name='ping')
async def ping(ctx):
    await ctx.send(f'Pong! {round(bot.latency * 1000)}ms')

bot.run(TOKEN)