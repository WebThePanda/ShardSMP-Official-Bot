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

@bot.event
async def on_ready():
    await bot.tree.sync()

# -- Purge --
@bot.hybrid_command(name="purge", description="Deletes X amount of messages.")
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
    channel_id = 1470121423161790560
    channel = bot.get_channel(channel_id)
    memberRole = member.guild.get_role(1469860668525117613)
    
    embed = discord.Embed(
        title="Welcome to ShardSMP! 🥳",
        description=(
            f"<:emoji_50:1470201146667696229> Hey {member.mention}, fancy seeing you here!\n"
            "Make sure to check out our channels and to have an awesome stay here at ShardSMP!\n"
            "<:M_connection:1469864216046473343>  **IP:** server-adress\n"
            "<:1000022062:1469864439770775634>  **Port:** port\n"
            "<:crash_dollar:1469864431738552381> **Shop:** store-link\n"
        ),
        color=discord.Color.purple()
    )
    embed.set_image(url="https://i.imgur.com/Xt0RmUE.png")
    embed.set_footer(
        text=f"Enjoy your stay",
        icon_url=member.guild.icon.url
    )
    
    if channel:
        await channel.send(embed=embed)
    if memberRole:
        await member.add_roles(memberRole)

# Counting System
class countingManager:
    def __init__(self, filePath="counts.json"):
        self.filePath = filePath
        self.data = self._loadData()
    
    def _loadData(self):
        if os.path.exists(self.filePath):
            with open(self.filePath, "r") as f:
                return json.load(f)
        return {"currentNum": 0, "lastUserID": None, "highScore": 0}
    
    def saveData(self):
        with open(self.filePath, "w") as f:
            json.dump(self.data, f, indent=4)
    
    def checkNum(self, userID, number):
        expected = self.data["currentNum"] + 1

        if number != expected:
            self.reset()
            return False, f"Wrong number! The next number was **{expected}**. Please restart at **1**."
        
        if userID == self.data["lastUserID"]:
            self.reset()
            return False, "You can't count twice in a row! Please restart at **1**"

        self.data["currentNum"] = number
        self.data["lastUserID"] = userID
        
        if number > self.data["highScore"]:
            self.data["highScore"] = number
        
        self.saveData()
        return True, "✅"
    
    def reset(self):
        self.data["currentNum"] = 0
        self.data["lastUserID"] = None
        self.saveData()


counter = countingManager()

@bot.event
async def on_message(message):
    countChannelID = 1470445117621010670


    if message.author.bot or message.channel.id != countChannelID:
        return
    
    if message.content.isdigit():
        num = int(message.content)
        success, resultMSG = counter.checkNum(message.author.id, num)

        if success:
            await message.add_reaction("✅")
        else:
            await message.add_reaction("❌")
            await message.channel.send(resultMSG)
    
    await bot.process_commands(message)

@bot.hybrid_command(name="countscore", description="Shows current number and highscore for counting minigame.")
async def countscore(ctx):
    current = counter.data["currentNum"]
    high = counter.data["highScore"]
    await ctx.send(f"📊 **Stats:**\n- Current: **{current}**\n- High Score: **{high}**")

#Tickets
@bot.hybrid_command(name="ticketsetup", description="Use this command to setup the Ticket system.")
@commands.has_permissions(administrator=True)
async def ticketsetup(ctx, channel: discord.TextChannel):
    await ctx.send(f"Ticket embed sent in {channel.mention}")

@bot.command(name="sync")
@commands.has_permissions(administrator=True)
async def sync(ctx):
    bot.tree.copy_global_to(guild=ctx.guild)
    synced = await bot.tree.sync(guild=ctx.guild)
    await ctx.send(f"Done! {len(synced)} commands are now live in this server.")
    

bot.run(token)