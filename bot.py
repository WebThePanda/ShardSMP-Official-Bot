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
bot = commands.Bot(command_prefix="b! ", intents=intents)

# Functions



# Classes

class SOTWButtons(discord.ui.View):
    def __init__(self, panda_id, cats_id, bamboot_id, filename, endTimeUnix):
        super().__init__(timeout=None)
        self.p_id = panda_id
        self.c_id = cats_id
        self.b_id = bamboot_id
        self.filename = filename
        self.endTimeUnix = endTimeUnix

        if os.path.exists(self.filename):
            with open(self.filename, "r") as f:
                data = json.load(f)
                self.p_votes = data.get("p", 0)
                self.c_votes = data.get("c", 0)
                self.b_votes = data.get("b", 0)
                self.voters = set(data.get("voters", []))
        else:
            self.p_votes = 0
            self.c_votes = 0
            self.b_votes = 0
            self.voters = set()
    
    def save_data(self):
        with open(self.filename, "w") as f:
            json.dump({
                "p": self.p_votes, "c": self.c_votes, "b": self.b_votes,
                "voters": list(self.voters)
            }, f)

    async def update_embed(self, interaction: discord.Interaction):
        embed = interaction.message.embeds[0]
        embed.description = (
            "Staff of The Week!\nVote for this week's best staff!\n\nThis week's choices are:\n"
            f"**WebThePanda (Owner): {self.p_votes}** votes\n"
            f"**Cats (Owner's Alt): {self.c_votes}** votes\n"
            f"**Bamboot (Bot): {self.b_votes}** votes\n\n"
            f"<t:{self.endTimeUnix}:R>"
        )
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Vote Panda", style=discord.ButtonStyle.blurple)
    async def panda_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id in self.voters:
            return await interaction.response.send_message("You already voted!", ephemeral=True)
        
        self.p_votes += 1
        self.voters.add(interaction.user.id)
        self.save_data()
        await self.update_embed(interaction)

    @discord.ui.button(label="Vote Cats", style=discord.ButtonStyle.blurple)
    async def cats_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id in self.voters:
            return await interaction.response.send_message("You already voted!", ephemeral=True)
        
        self.c_votes += 1
        self.voters.add(interaction.user.id)
        self.save_data()
        await self.update_embed(interaction)

    @discord.ui.button(label="Vote Bamboot", style=discord.ButtonStyle.blurple)
    async def bamboot_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id in self.voters:
            return await interaction.response.send_message("You already voted!", ephemeral=True)
        
        self.b_votes += 1
        self.voters.add(interaction.user.id)
        self.save_data()
        await self.update_embed(interaction)

# Commands

@bot.command(name="sotw")
@commands.has_role(1443544544409948272)
async def sotw(ctx, dur: int):
    channel_id = 1479877488510500956
    channel = bot.get_channel(channel_id)
    generalChat_id = 1443544545420771378

    winnerRoleID = 1479924640754307103
    winnerRole = ctx.guild.get_role(winnerRoleID)

    panda = 502141502038999041
    cats = 972943470023041044
    bamboot = 1479571065549357362
    
    file_name = "sotw_data.json"
    duration = dur
    endTimeUnix = int(time.time() + duration)

    if duration >= 3600:
        timeVal = duration // 3600
        unit = "hour" if timeVal == 1 else "hours"
        timeDisplay = f"{timeVal} {unit}"
    elif duration >= 60:
        timeVal = duration //60
        unit = "minute" if timeVal == 1 else "minutes"
        timeDisplay = f"{timeVal} {unit}"
    else:
        timeDisplay = f"{duration} seconds"

    embed = discord.Embed(
        title="Staff of The Week",
        description=(
            "Vote for this weeks best staff!\n\n"
            "This weeks choices are:\n"
            "**WebThePanda (Owner): 0** votes\n"
            "**Cats (Cool Guy): 0** votes\n"
            "**Bamboot (Bot): 0** votes\n\n"
            "<t:{self.endTimeUnix}:R>"
        ),
        colour=discord.Color.blurple()
    )

    if channel:
        view = SOTWButtons(panda_id=panda, cats_id=cats, bamboot_id=bamboot, filename=file_name, endTimeUnix=endTimeUnix)
        msg = await channel.send(embed=embed, view=view)
        await ctx.send(f"Poll started in {channel.mention} for {timeDisplay}!")

        await asyncio.sleep(duration)

        for child in view.children:
            child.disabled = True
        
        id_map = {
            "WebThePanda": view.p_id,
            "Cats": view.c_id,
            "Bamboot": view.b_id
        }

        scores = {"WebThePanda": view.p_votes, "Cats": view.c_votes, "Bamboot": view.b_votes}
        winner_name = max(scores, key=scores.get)

        winner_id = id_map[winner_name]
        member = ctx.guild.get_member(winner_id)

        end_embed = discord.Embed(
            title="Staff of The Week - Results",
            description=f"The results are in!\n\nWinner: **{winner_name}** with **{scores[winner_name]}** votes.\n\nCongratulate them in <#{generalChat_id}>!",
            color=discord.Color.gold()
        )
        if member:
            try:
                for old_winner in winnerRole.members:
                    await old_winner.remove_roles(winnerRole)
                await member.add_roles(winnerRole)
            except discord.Forbidden:
                pass
        else:
            pass
        
        await msg.edit(embed=end_embed, view=None)

        if os.path.exists(file_name):
            os.remove(file_name)


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
    
    if channel:
        await channel.send(embed=embed)

# Error

@purge.error
async def purge_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You do not have the 'Manage Messages' permission to use this command.", ephmeral=True)

@sotw.error
async def sotw_error(ctx, error):
    if isinstance(error, commands.MissingRole):
        await ctx.send("You do not have permission to use this command. Only WebThePanda can use this command!", ephmeral=True)

bot.run(token)