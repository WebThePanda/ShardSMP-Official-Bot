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

if token:
    print(f"✅ Token found! Length: {len(token)} characters.")
else:
    print("❌ FATAL: No token found in Railway Variables.")
    # This lists all available keys (but NOT values) to help us debug
    print(f"Available variables: {list(os.environ.keys())}")

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
    print(f"Logged in as {bot.user.name}")

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
        await ctx.send("I do not have the 'Manage Messages' permission to do this.", ephemeral=True)
    except Exception as e:
        await ctx.send(f"An error occured: {e}", ephemeral=True)


@purge.error
async def purge_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You do not have the 'Manage Messages' permission to use this command.", ephemeral=True)

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

    if not message.author.bot and message.channel.id == countChannelID:
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
    pass


#Sync
@bot.command(name="sync")
@commands.is_owner()
async def sync(ctx):
    print("sync command triggered")  # Check your console
    await ctx.send("Syncing...")     # Confirm bot can send messages
    bot.tree.copy_global_to(guild=ctx.guild)
    synced = await bot.tree.sync(guild=ctx.guild)
    await ctx.send(f"Done! {len(synced)} slash commands are now live in this server.")

@sync.error
async def sync_error(ctx, error):
    if isinstance(error, commands.NotOwner):
        await ctx.send("Only the bot owner can use this command.")

#Shutdown
@bot.command(name="shutdown")
@commands.is_owner()
async def shutdown(ctx):
    await ctx.send("Bot is shutting down.")
    await bot.close()

if __name__ == "__main__":
    if not token:
        print("❌ ERROR: The 'token' variable is missing in Railway Variables!")
    else:
        try:
            bot.run(token)
        except Exception as e:
            print(f"❌ CRITICAL ERROR DURING STARTUP: {e}")