# Imports
import discord
from discord.ext import commands
from dotenv import load_dotenv
import os

# Load token and id from .env
load_dotenv()
token = os.getenv('token')
clientid = os.getenv('botid')
print(f"Token found: {token is not None}")
print(f"Token length: {len(token) if token else 'None'}")

# Intents
intents = discord.Intents.default()
intents.message_content = True
intents.messages = True

# Bot Setup
bot = commands.Bot(command_prefix="b! ", intents=intents)

bot.run(token)