# Imports
import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import json
import asyncio
import time

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
bot = commands.Bot(command_prefix="s!", intents=intents)

# -- Purge --
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
        await ctx.send("I do not have the 'Manage Messages' permission to do this.", ephmeral=True)
    except Exception as e:
        await ctx.send(f"An error occured: {e}", ephmeral=True)


@purge.error
async def purge_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You do not have the 'Manage Messages' permission to use this command.", ephmeral=True)

# Welcome message + Autorole
@bot.event
async def on_member_join(member):
    channel_id = 1443544545261518850
    channel = bot.get_channel(channel_id)
    memberRole = member.guild.get_role(1443544544409948267)
    
    embed = discord.Embed(
        title="Welcome to ShardSMP.",
        description=(
            f"<:pinkChicken:1480189572100001842> Hey {member.mention}, fancy seeing you here!\n"
            "Make sure to check out our channels and to have an awesome stay here at ShardSMP!\n"
            "<:connectionHeart:1480198420718289026> **IP:** server-adress\n"
            "<:mcBedrock:1480198677380333703> **Port:** port\n"
            "<:shoppingCart:1480199374318600202> **Shop:** store-link\n"
        ),
        color=discord.Color.pink()
    )
    embed.set_image(url="https://www.imgur.com/a/rI5BPrc")
    embed.set_author(
        name=f"Enjoy your stay",
        icon_url=member.guild.icon.url
    )
    
    if channel:
        await channel.send(embed=embed)
    if memberRole:
        await member.add_roles(memberRole)

@bot.command(name="test")
async def test(ctx):
    await ctx.send("<:pinkChicken:1480189572100001842>")


bot.run(token)