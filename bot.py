# Imports
import discord
from discord.ext import commands
from dotenv import load_dotenv
import os

# Load token and id from .env
load_dotenv()
token = os.getenv('token')
clientid = os.getenv('botid')

# Intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.messages = True

# Bot Setup
bot = commands.Bot(command_prefix="b! ", intents=intents)

# Functions



# Commands



# Events

@bot.event
async def on_member_join(member):
    member = member
    channel_id = 1443544545261518850
    channel = bot.get_channel(channel_id)
    embed = discord.Embed(
        title="Welcome to the community. 🐼",
        description=f"Welcome {member} to the community server of WebThePanda. I hope you enjoy your stay.",
        color=discord.Color.pink()
    )
    embed.set_author(text=f"{member}")
    embed.set_footer(text="Made by WebThePanda")
    if channel:
        await channel.send(embed=embed)

bot.run(token)