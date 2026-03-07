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

@bot.command(name="purge")
@commands.has_permissions(manage_messages=True)
async def purge(ctx, amount: int):
    if amount <= 0:
        await ctx.send("Please specify a number greater than zero.")
        return
    
    try:
        deleted = await ctx.channel.purge(limit=amount + 1)
        await ctx.send(f"Purged {len(deleted) - 1} messages.", delete_after=5)
    except discord.Forbidden:
        await ctx.send("I do not have the 'Manage Messages' permission to do this.")
    except Exception as e:
        await ctx.send(f"An error occured: {e}")


# Events

@bot.event
async def on_member_join(member):
    channel_id = 1443544545261518850
    channel = bot.get_channel(channel_id)
    embed = discord.Embed(
        title="Welcome to the community. 🐼",
        description=f"Welcome {member} to the community server of WebThePanda. I hope you enjoy your stay.",
        color=discord.Color.pink()
    )
    embed.set_author(
        name=f"New Member: {member.display_name}",
        icon_url=member.display_avatar.url
    )
    embed.set_footer(text="Made by WebThePanda")
    if channel:
        await channel.send(embed=embed)

# Error

@purge.error
async def purge_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You do not have the 'Manage Messages' permission to use this command.")

bot.run(token)