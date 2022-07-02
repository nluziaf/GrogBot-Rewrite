# -----------------------------------------------------------
# BEFORE CONTRIBUTING TO THIS PROJECT, READ README.MD FIRST!
# -----------------------------------------------------------

import asyncio
import aiofiles
import io
import math
import os
import random
from typing import Literal

import discord
import requests
from PIL import Image
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
from mojang import MojangAPI

try:
    from sympy.mpmath import mp
except ImportError:
    from mpmath import mp

# Defining IDs
SERVER_ID = discord.Object(id=966238887456428052)
COLOUR = 0xb27b56

# Defining Auto Responses - Change this
auto_responses = {
    "hello": 'Hello there {username}!',
    "gm": 'Good Morning {username}!',
    "ga": 'Good Afternoon {username}',
    "gn": 'Good Night {username}!',
    "no u": 'No u',
    "shut": "** **"
}

# .env Stuffs!
load_dotenv()
TKN = os.getenv("TOKEN") # Token, hahaha it's in .env kekw

# Defining Bot, no prefixed commands here!
bot = commands.Bot(command_prefix='.', intents=discord.Intents.all(), help_command=None)
tree = bot.tree
bot.warnings = {}

# Ready!
@bot.event
async def on_ready():
    await bot.change_presence(status=discord.Status.online, activity=discord.Game("with Baba Luz :)"))
    for guild in bot.guilds:
        async with aiofiles.open(f'{guild.id}.txt', mode='a'):
            pass
        bot.warnings[guild.id] = {}
    for guild in bot.guilds:
        async with aiofiles.open(f'{guild.id}.txt', mode='r') as file:
            lines = await file.readlines()
            for line in lines:
                data = line.split(" ")
                member_id = int(data[0])
                admin_id = int(data[1])
                reason = " ".join(data[2:]).strip("\n")
                try:
                    bot.warnings[guild.id][member_id][0] += 1
                    bot.warnings[guild.id][member_id][1].append(admin_id, reason)
                except KeyError:
                    bot.warnings[guild.id][member_id] = [1, [(admin_id, reason)]]
    print("GrogBot is ready")

@bot.event
async def on_guild_join(guild):
    bot.warnings[guild.id] = {}

# Chat Bot is Ready!
@bot.listen('on_message')
async def chatbot(message):
    user_message = str(message.content.lower())
    if message.author == bot.user:
        return
    try:
        await message.channel.send(auto_responses[user_message].replace('{username}', message.author.display_name))
    except KeyError:
        pass

def query_processing(query: str):
    query = query.lower() # Making it lower
    new_query = query.replace(" ", "") # Removing space
    return new_query

# -------------------------------------------------------
#                     Commands Here!
# -------------------------------------------------------

@tree.command(guild=SERVER_ID, description="Check bot latency")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(f"Pong! ({round(bot.latency, 4)}s)")

@tree.command(guild=SERVER_ID, description="Get animal image as well as the fact")
@app_commands.describe(animal="What is the animal you want to see?")
async def animal(interaction: discord.Interaction, animal: Literal["Dog", "Cat", "Panda", "Fox", "Red Panda", "Koala", "Bird", "Raccoon", "Kangaroo"]):
    animal_name = query_processing(animal_name)
    
    response = requests.get(f'https://some-random-api.ml/animal/{animal_name}')
    data = response.json()
    
    image = data['image']
    fact = data['fact']
    
    embed = discord.Embed(title=f"Here's the {animal}", description=f'Did you know? {fact}',colour=COLOUR)
    embed.set_image(url=image)
    embed.set_footer(text=f"Command executed by {interaction.user}", icon_url=interaction.user.display_avatar.url)
    await interaction.response.send_message(embed=embed)

@tree.command(guild=SERVER_ID, description="Get MC Server data")
@app_commands.describe(server="MC Server IP here (example : hypixel.net)")
async def mcserv(interaction: discord.Interaction, server: str):
    server_data = requests.get(f'https://api.mcsrvstat.us/2/{server}')
    if server_data.status_code == 404:
        await interaction.response.send_message("Server not found")
    else:
        data = server_data.json()
        
        online: bool = data['debug']['ping']
        ip = data['ip']
        port = data['port']
        version: int = data['version']

        embed = discord.Embed(title=f"Data for {server}", colour=COLOUR)
        embed.set_thumbnail(url=f'https://api.mcsrvstat.us/icon/{server}')
        embed.add_field(name="IP", value=ip, inline=False)
        embed.add_field(name="Port", value=port, inline=False)
        embed.add_field(name="Online?", value=online, inline=False)
        embed.add_field(name="Version", value=version, inline=False)
        embed.set_footer(text=f"Command executed by {interaction.user}", icon_url=interaction.user.display_avatar.url)

        if online:
            motd: str = data['motd']['clean'][0].strip()
            online_players: int = data['players']['online']
            max_player: int = data['players']['max']
            embed.add_field(name="MOTD", value=motd, inline=False)
            embed.add_field(name="Online players", value=f"{online_players}/{max_player}", inline=False)
            embed.set_footer(text=f"Command executed by {interaction.user}", icon_url=interaction.user.display_avatar.url)

        await interaction.response.send_message(embed=embed)

@tree.command(guild=SERVER_ID, description="Get MC Player data")
@app_commands.describe(player="MC In-Game Name (IGN) here (example : N_Luziaf)")
async def mcplayer(interaction: discord.Interaction, player: str):
    uuid = MojangAPI.get_uuid(player)
    command13 = f"`/give @p minecraft:player_head{{SkullOwner: \"{player}\"}}`"
    command12 = f"`/give @p minecraft:skull 1 3 {{SkullOwner: \"{player}\"}}`"

    embed = discord.Embed(title=f"Player Data - {player}", colour=COLOUR)
    embed.set_thumbnail(url=f'https://crafatar.com/renders/head/{uuid}?overlay')
    embed.add_field(name="UUID", value=uuid, inline=False)
    embed.add_field(name="Skin", value=f'https://crafatar.com/skins/{uuid}', inline=False)
    embed.add_field(name="Give head command",
                    value=f'**1.13 or later :**\n{command13}\n**1.12 or earlier :**\n{command12}',
                    inline=False)
    embed.set_image(url=f'https://crafatar.com/renders/body/{uuid}?overlay')
    embed.set_footer(text=f"Command executed by {interaction.user}", icon_url=interaction.user.display_avatar.url)

    await interaction.response.send_message(embed=embed)

@tree.command(guild=SERVER_ID, description="Convert temperatures")
@app_commands.describe(unit1="First Temperature Unit (Convert from ...)", unit2="Second Temperature Unit (Convert to ...)", num="Number of the Temperature")
async def tempconvert(interaction: discord.Interaction,
                      unit1: Literal['celsius', 'fahrenheit', 'reaumur', 'kelvin'],
                      unit2: Literal['celsius', 'fahrenheit', 'reaumur', 'kelvin'],
                      num: int = 0):
    x = 0
    k = 0

    conversion = {'celsius': 5, 'fahrenheit': 9, 'reaumur': 4, 'kelvin': 5}
    temp1 = conversion[unit1]
    temp2 = conversion[unit2]

    if unit1 == "fahrenheit":
        num = num - 32
    if unit2 == "fahrenheit":
        x = 32
    if unit1 == "kelvin":
        k = -273.15
    if unit2 == "kelvin":
        k = 273.15

    result = (temp2 / temp1) * num + x + k
    await interaction.response.send_message(f"{unit1.capitalize()} to {unit2.capitalize()}\n{result}")

# -------------------------------------------------------
#                     Classes Here!
# -------------------------------------------------------

# Calculator View
class CalcView(discord.ui.View):
    def __init__(self, ctx: commands.Context, embed: discord.Embed):
        self.ctx = ctx
        self.embed = embed
        self._all_ans = [0]
        self.equation = ""
        super().__init__(timeout=120)

    def parse_equation(self):
        new_equation = self.equation.replace("%", " / 100")
        new_equation = new_equation.replace("x", "*")
        new_equation = new_equation.replace("÷", "/")
        new_equation = new_equation.replace("^", "**")
        new_equation = new_equation.replace("Ans", f"{self._all_ans[0]}")
        new_equation = new_equation.replace("π", "3.141592653589793")
        return new_equation

    async def calculate(self):
        """Calculate the equation"""
        log = math.log
        try:
            ans = eval(self.parse_equation())
            self._all_ans[0] = ans
        except Exception as e:
            self._all_ans[0] = 0
            ans = "Error! Make sure you closed your parenthesis and brackets!\n\n Do not do `number(...)` Instead use `number x (...)`\n Do not combine numbers into each other - Ex: `π6^2` Instead do `π*6^2` \n**They Will Result In Different Answers!**\n\nDon't also do leave operations on its own"
        self.equation = ""

        return ans

    def _remove_placeholder(self):
        self.embed.description = ""

    def _placeholder(self):
        self.embed.description = "`Enter your equation below`"

    def new_equation(self, value: str):
        self.equation += value

    def new_embed(self, value: str):
        self.new_equation(value)
        self.embed.description = f"```{self.equation}```"
        return self.embed

    @discord.ui.button(row=0, label="^", style=discord.ButtonStyle.secondary)
    async def power(self, inter: discord.Interaction, button: discord.ui.Button):
        """Add the exponent operation to the equation"""
        await inter.response.defer()
        await inter.edit_original_message(embed=self.new_embed(button.label))

    @discord.ui.button(row=0, label="(", style=discord.ButtonStyle.success)
    async def left_parathesis(self, inter: discord.Interaction, button: discord.ui.Button):
        """Add the left parenthesis to the equation"""
        await inter.response.defer()
        await inter.edit_original_message(embed=self.new_embed(button.label))

    @discord.ui.button(row=0, label=")", style=discord.ButtonStyle.success)
    async def right_parenthesis(self, inter: discord.Interaction, button: discord.ui.Button):
        """Add the right parenthesis to the equation"""
        await inter.response.defer()
        await inter.edit_original_message(embed=self.new_embed(button.label))

    @discord.ui.button(row=0, label="AC", style=discord.ButtonStyle.danger)
    async def ac(self, inter: discord.Interaction, button: discord.ui.Button):
        """Delete the last character of the equation"""
        await inter.response.defer()
        if len(self.equation) <= 1:
            self._placeholder()
        else:
            self.equation = self.equation.rstrip(self.equation[-1])
            self.embed.description = self.equation
        await inter.edit_original_message(embed=self.embed)

    @discord.ui.button(row=0, label="CE", style=discord.ButtonStyle.danger)
    async def ce(self, inter: discord.Interaction, button: discord.ui.Button):
        """Clear the equation"""
        await inter.response.defer()
        self._placeholder()
        self.equation = ""
        await inter.edit_original_message(embed=self.embed)

    @discord.ui.button(row=1, label="%", style=discord.ButtonStyle.secondary)
    async def percentage(self, inter: discord.Interaction, button: discord.ui.Button):
        """Add the percentage operation to the equation"""
        await inter.response.defer()
        await inter.edit_original_message(embed=self.new_embed(button.label))

    @discord.ui.button(row=1, label="7", style=discord.ButtonStyle.success)
    async def seven(self, inter: discord.Interaction, button: discord.ui.Button):
        """Add the number 7 to the equation"""
        await inter.response.defer()
        await inter.edit_original_message(embed=self.new_embed(button.label))

    @discord.ui.button(row=1, label="8", style=discord.ButtonStyle.success)
    async def eight(self, inter: discord.Interaction, button: discord.ui.Button):
        """Add the number 8 to the equation"""
        await inter.response.defer()
        await inter.edit_original_message(embed=self.new_embed(button.label))

    @discord.ui.button(row=1, label="9", style=discord.ButtonStyle.success)
    async def nine(self, inter: discord.Interaction, button: discord.ui.Button):
        """Add the number 9 to the equation"""
        await inter.response.defer()
        await inter.edit_original_message(embed=self.new_embed(button.label))

    @discord.ui.button(row=1, label="÷", style=discord.ButtonStyle.secondary)
    async def divide(self, inter: discord.Interaction, button: discord.ui.Button):
        """Add the division operation to the equation"""
        await inter.response.defer()
        await inter.edit_original_message(embed=self.new_embed(button.label))

    @discord.ui.button(row=2, label="Ans", style=discord.ButtonStyle.secondary)
    async def ans(self, inter: discord.Interaction, button: discord.ui.Button):
        """Get previous answer"""
        await inter.response.defer()
        await inter.edit_original_message(embed=self.new_embed(button.label))

    @discord.ui.button(row=2, label="6", style=discord.ButtonStyle.success)
    async def six(self, inter: discord.Interaction, button: discord.ui.Button):
        """Add the number 6 to the equation"""
        await inter.response.defer()
        await inter.edit_original_message(embed=self.new_embed(button.label))

    @discord.ui.button(row=2, label="5", style=discord.ButtonStyle.success)
    async def five(self, inter: discord.Interaction, button: discord.ui.Button):
        """Add the number 5 to the equation"""
        await inter.response.defer()
        await inter.edit_original_message(embed=self.new_embed(button.label))

    @discord.ui.button(row=2, label="4", style=discord.ButtonStyle.success)
    async def four(self, inter: discord.Interaction, button: discord.ui.Button):
        """Add the number 4 to the equation"""
        await inter.response.defer()
        await inter.edit_original_message(embed=self.new_embed(button.label))

    @discord.ui.button(row=2, label="x", style=discord.ButtonStyle.secondary)
    async def multiply(self, inter: discord.Interaction, button: discord.ui.Button):
        """Add the mutiplication operation to the equation"""
        await inter.response.defer()
        await inter.edit_original_message(embed=self.new_embed(button.label))

    @discord.ui.button(row=3, label="log(", style=discord.ButtonStyle.secondary)
    async def log(self, inter: discord.Interaction, button: discord.ui.Button):
        """Add the sin math function to the equation"""
        await inter.response.defer()
        await inter.edit_original_message(embed=self.new_embed(button.label))

    @discord.ui.button(row=3, label="3", style=discord.ButtonStyle.success)
    async def three(self, inter: discord.Interaction, button: discord.ui.Button):
        """Add the number 3 to the equation"""
        await inter.response.defer()
        await inter.edit_original_message(embed=self.new_embed(button.label))

    @discord.ui.button(row=3, label="2", style=discord.ButtonStyle.success)
    async def two(self, inter: discord.Interaction, button: discord.ui.Button):
        """Add the number 2 to the equation"""
        await inter.response.defer()
        await inter.edit_original_message(embed=self.new_embed(button.label))

    @discord.ui.button(row=3, label="1", style=discord.ButtonStyle.success)
    async def one(self, inter: discord.Interaction, button: discord.ui.Button):
        """Add the number 1 to the equation"""
        await inter.response.defer()
        await inter.edit_original_message(embed=self.new_embed(button.label))

    @discord.ui.button(row=3, label="-", style=discord.ButtonStyle.secondary)
    async def subtract(self, inter: discord.Interaction, button: discord.ui.Button):
        """Add the subtract operation to the equation"""
        await inter.response.defer()
        await inter.edit_original_message(embed=self.new_embed(button.label))

    @discord.ui.button(row=4, label="π", style=discord.ButtonStyle.secondary)
    async def pi(self, inter: discord.Interaction, button: discord.ui.Button):
        """Add Cos math function"""
        await inter.response.defer()
        await inter.edit_original_message(embed=self.new_embed(button.label))

    @discord.ui.button(row=4, label="0", style=discord.ButtonStyle.success)
    async def zero(self, inter: discord.Interaction, button: discord.ui.Button):
        """Add zero to the equation"""
        await inter.response.defer()
        await inter.edit_original_message(embed=self.new_embed(button.label))

    @discord.ui.button(row=4, label="(.)", style=discord.ButtonStyle.secondary)
    async def decimal(self, inter: discord.Interaction, button: discord.ui.Button):
        """Add a decimal to the equation"""
        await inter.response.defer()
        await inter.edit_original_message(embed=self.new_embed('.'))

    @discord.ui.button(row=4, label="=", style=discord.ButtonStyle.primary)
    async def solve(self, inter: discord.Interaction, button: discord.ui.Button):
        """Solve the equation"""
        await inter.response.defer()
        ans = await self.calculate()
        self.embed.description = str(ans)
        await inter.edit_original_message(embed=self.embed)

    @discord.ui.button(row=4, label="+", style=discord.ButtonStyle.secondary)
    async def add(self, inter: discord.Interaction, button: discord.ui.Button):
        """Math Add operation Button"""
        await inter.response.defer()
        await inter.edit_original_message(embed=self.new_embed(button.label))

# COMMAND CLASSES
class Fun(app_commands.Group):
    binary = app_commands.Group(name='binary', description="Binary Commands")
    base64 = app_commands.Group(name='base64', description="Base64 Commands")
    
    @app_commands.command(name="8ball", description="Ask questions, get answers")
    @app_commands.describe(question="So, what is your question?")
    async def eightball(self, interaction: discord.Interaction, *, question: str):
        responses = ["As I see it, yes.", "Ask again later.", "Better not tell you now.", "Cannot predict now.",
                    "Concentrate and ask again.", "Do not count on it.", "It is certain.", "It is decidedly so.",
                    "Most likely.", "My reply is no.", "My sources say no.", "Outlook not so good.", "Outlook good.",
                    "Reply hazy, try again.", "Signs point to yes.", "Very doubtful.", "Without a doubt.", "Yes.",
                    "Yes, definitely.", "You may rely on it."]
        response = random.choice(responses)
        embed = discord.Embed(title='', description=f'Question : {question}\nAnswer : {response}', colour=COLOUR)
        embed.set_footer(text=f"Command executed by {interaction.user}", icon_url=interaction.user.display_avatar.url)
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="joke", description="Get a joke")
    async def joke(self, interaction: discord.Interaction):
        response = requests.get('https://some-random-api.ml/joke')
        data = response.json()
        
        joke = data['joke']
        
        embed = discord.Embed(title="Here's a joke", description=joke, colour=COLOUR)
        embed.set_footer(text=f"Command executed by {interaction.user}", icon_url=interaction.user.display_avatar.url)
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="meme", description="Generate memes from random meme subreddits")
    async def meme(self, interaction: discord.Interaction):
        memeapi = requests.get('https://meme-api.herokuapp.com/gimme')
        memedata = memeapi.json()

        memeurl = memedata['url']
        memename = memedata['title']
        memeposter = memedata['author']
        memesubreddit = memedata['subreddit']

        embed = discord.Embed(title=memename, description=f"Meme by {memeposter} from Subreddit {memesubreddit}", colour=COLOUR)
        embed.set_image(url=memeurl)
        embed.set_footer(text=f"Command executed by {interaction.user}", icon_url=interaction.user.display_avatar.url)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="token", description="Mess up with other bot devs")
    async def token(self, interaction: discord.Interaction):
        response = requests.get('https://some-random-api.ml/bottoken')
        data = response.json()
        
        faketoken = data['token']
        
        embed = discord.Embed(title="Haha! I got your bot token!", description=faketoken, colour=COLOUR)
        embed.set_footer(text=f"Command executed by {interaction.user}", icon_url=interaction.user.display_avatar.url)
        await interaction.response.send_message(embed=embed)
    
    @binary.command(name="encode", description="Encode to Binary")
    @app_commands.describe(string="String you want to encode")
    async def binary_encode(self, interaction: discord.Interaction, string: str):
        response = requests.get(f"https://some-random-api.ml/binary?encode={string}")
        data = response.json()
        
        encoded = data['binary']
        
        embed = discord.Embed(title="Binary Encode", description=encoded, colour=COLOUR)
        embed.set_footer(text=f"Command executed by {interaction.user}", icon_url=interaction.user.display_avatar.url)
        await interaction.response.send_message(embed=embed)
        
    @binary.command(name="decode", description="Decode from Binary")
    @app_commands.describe(binary="Binary you want to decode")
    async def binary_decode(self, interaction: discord.Interaction, binary: int):
        response = requests.get(f"https://some-random-api.ml/binary?encode={binary}")
        if 300 > response.status_code >= 200 :
            data = response.json()
            decoded = data['text']
        
            embed = discord.Embed(title="Binary Decode", description=decoded, colour=COLOUR)
            embed.set_footer(text=f"Command executed by {interaction.user}", icon_url=interaction.user.display_avatar.url)
        else:
            embed = discord.Embed(title="Binary Decode", description="Binary must contain only 0 or 1", colour=COLOUR)
            embed.set_footer(text=f"Command executed by {interaction.user}", icon_url=interaction.user.display_avatar.url)

        await interaction.response.send_message(embed=embed)
    
    @base64.command(name="encode", description="Encode to Base64")
    @app_commands.describe(string="String you want to encode")
    async def base64_encode(self, interaction: discord.Interaction, string: str):
        response = requests.get(f"https://some-random-api.ml/base64?encode={string}")
        data = response.json()
        
        encoded = data['base64']
        
        embed = discord.Embed(title="Base64 Encode", description=encoded, colour=COLOUR)
        embed.set_footer(text=f"Command executed by {interaction.user}", icon_url=interaction.user.display_avatar.url)
        await interaction.response.send_message(embed=embed)
        
    @base64.command(name="decode", description="Decode from Base64")
    @app_commands.describe(base64="Base64 you want to decode")
    async def base64_decode(self, interaction: discord.Interaction, base64: str):
        response = requests.get(f"https://some-random-api.ml/base64?decode={base64}")
        data = response.json()
        
        decoded = data['text']
        
        embed = discord.Embed(title="Base64 Encode", description=decoded, colour=COLOUR)
        embed.set_footer(text=f"Command executed by {interaction.user}", icon_url=interaction.user.display_avatar.url)
        await interaction.response.send_message(embed=embed)

class Mod(app_commands.Group):
    @app_commands.command(name="nuke", description="Channel Nuke (ADMIN ONLY)")
    @app_commands.checks.has_permissions(administrator=True)
    async def nuke(self, interaction: discord.Interaction):
        await interaction.channel.delete(reason="Nuked Channel")
        clean_channel = await interaction.channel.clone(reason="Nuked Channel")
        
        embed = discord.Embed(title=f"Boom! Channel {interaction.channel.name} has been nuked", description=f"Nuked by {interaction.user.mention}", colour=COLOUR)
        
        await clean_channel.send(embed=embed)
        
    @app_commands.command(name="purge", description="Purge messages from this channel")
    @app_commands.checks.has_permissions(manage_messages=True)
    @app_commands.describe(amount="Amount of messages that you want to delete")
    async def purge(self, interaction: discord.Interaction, amount: int):
        await interaction.channel.purge(limit=amount)
        await interaction.response.send_message(f"Deleted {amount} messages", ephemeral=True)

    @app_commands.command(name="ban", description="Ban the member")
    @app_commands.checks.has_permissions(kick_members=True, ban_members=True)
    @app_commands.describe(member="Member who will be banned")
    async def ban(self, interaction: discord.Interaction, member: discord.Member):
        await interaction.guild.ban(member)
        await interaction.response.send_message(f"Banned {member.mention}")

    @app_commands.command(name="kick", description="Kick the member")
    @app_commands.checks.has_permissions(kick_members=True, ban_members=True)
    @app_commands.describe(member="Member who will be kicked")
    async def kick(self, interaction: discord.Interaction, member: discord.Member):
        await interaction.guild.kick(member)
        await interaction.response.send_message(f"Kicked {member.mention}")

    @app_commands.command(name="unban", description="Unban the user")
    @app_commands.checks.has_permissions(kick_members=True, ban_members=True)
    @app_commands.describe(user="ID of the user who will be unbanned")
    async def unban(self, interaction: discord.Interaction, user: str):
        ctx = await bot.get_context(interaction)
        try:
            user = await commands.UserConverter().convert(ctx, user)
        except (discord.NotFound, commands.UserNotFound):
            return await interaction.response.send_message('User not found', ephemeral=True)
        try:
            await interaction.guild.unban(user)
        except discord.NotFound:
            return await interaction.response.send_message("User is not banned", ephemeral=True)
        await interaction.response.send_message(f"Unbanned {user}")

    @app_commands.command(name="warn", description="Warn the member")
    @app_commands.checks.has_permissions(kick_members=True, ban_members=True)
    @app_commands.describe(member="Member who will be warned")
    async def warn(self, interaction: discord.Interaction, member: discord.Member, *, reason: str = "No reason provided"):
        try:
            first_warning = False
            bot.warnings[interaction.guild.id][member.id][0] += 1
            bot.warnings[interaction.guild.id][member.id][1].append((interaction.user.id, reason))
        except KeyError:
            first_warning = True
            bot.warnings[interaction.guild.id][member.id] = [1, [(interaction.user.id, reason)]]
        count = bot.warnings[interaction.guild.id][member.id][0]
        async with aiofiles.open(f"{interaction.guild.id}.txt", mode="a") as file:
            await file.write(f"{member.id} {interaction.user.id} {reason}\n")
            
        await interaction.response.send_message(f"Warned {member.mention} for {reason}!")

class Info(app_commands.Group):
    @app_commands.command(name="whois", description="Get user's information")
    @app_commands.describe(member="Discord Member")
    async def info_whois(self, interaction: discord.Interaction, member: discord.Member = None):
        if member is None:
            member = interaction.user
        embed = discord.Embed(title=f"User Info - {member}", colour=COLOUR)
        embed.set_thumbnail(url=member.avatar.url)
        embed.set_footer(text=f"Requested by - {interaction.user}", icon_url=interaction.user.avatar.url)
        embed.add_field(name='ID', value=member.id, inline=False)
        embed.add_field(name='Name', value=member.display_name, inline=False)
        embed.add_field(name='Created at', value=member.created_at, inline=False)
        embed.add_field(name="Joined at", value=member.joined_at, inline=False)
        embed.set_footer(text=f"Command executed by {interaction.user}", icon_url=interaction.user.display_avatar.url)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name='avatar', description="Get user's information")
    @app_commands.describe(type="Which avatar? (Default is Server avatar)", member="Discord Member")
    async def info_avatar(self, interaction: discord.Interaction, type: Literal["Server avatar", "User avatar"] = "Server avatar", member: discord.Member = None):
        if member is None:
            member = interaction.user
        avatar = member.display_avatar.url if type == "Server avatar" else member.avatar.url
        embed = discord.Embed(title=f"{member.name}#{member.discriminator}'s avatar", colour=COLOUR)
        embed.set_image(url=avatar)
        embed.set_footer(text=f"Command executed by {interaction.user}", icon_url=interaction.user.display_avatar.url)
        await interaction.response.send_message(embed=embed)

class Picture(app_commands.Group):
    @app_commands.command(name="filter", description="Avatar Filters")
    @app_commands.describe(filter="Filter", member="Discord Member")
    async def picture_filter(self, interaction: discord.Interaction, filter: Literal["Invert", "Greyscale", "Invert Greyscale", "Sepia", "Brightness", "Threshold", "Pixelate", "Blur"], member: discord.Member = None):
        filter_name = query_processing(filter)
        if member is None:
            member = interaction.user
            
        response = f'https://some-random-api.ml/canvas/{filter_name}?avatar={member.display_avatar.url}'
        
        embed = discord.Embed(title=f"Filter command - {filter}", colour=COLOUR)
        embed.set_image(url=response)
        embed.set_footer(text=f"Command executed by {interaction.user}", icon_url=interaction.user.display_avatar.url)
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="eatme", description="Get eaten by Grog")
    async def picture_eatme(self, interaction: discord.Interaction):
        grog = Image.open(r'./pics/eatme.jpg')
        asset = interaction.user.display_avatar.with_size(256)
        data = io.BytesIO(await asset.read())
        pfp = Image.open(data)
        pfp = pfp.resize((144, 144))

        grog.paste(pfp, (90, 222))
        grog.save("Image.jpg")
        await interaction.response.send_message(file=discord.File("Image.jpg"))

    @app_commands.command(name="marry", description="Marry a discord member")
    @app_commands.describe(member="Discord Member to marry")
    async def picture_marry(self, interaction: discord.Interaction, member: discord.Member):
        marriage = Image.open(r'./pics/thing.jpg')
        asset1 = interaction.user.display_avatar.with_size(128)
        data1 = io.BytesIO(await asset1.read())
        pfp1 = Image.open(data1)
        pfp1 = pfp1.resize((54, 54))

        asset2 = member.display_avatar.with_size(128)
        data2 = io.BytesIO(await asset2.read())
        pfp2 = Image.open(data2)
        pfp2 = pfp2.resize((54, 54))

        marriage.paste(pfp1, (140, 21))
        marriage.paste(pfp2, (262, 20))

        marriage.save("Image.jpg")
        await interaction.response.send_message(file=discord.File("Image.jpg"))

class Math(app_commands.Group):
    @app_commands.command(name="trigonometry", description="Math feature")
    @app_commands.describe(method="Trigonometry methods", deg="Number in degrees, not radians")
    async def math_trigonometry(self, interaction: discord.Interaction,
                           method: Literal['sin', 'sinh', 'asin', 'asinh', 'cos', 'cosh', 'acos', 'acosh', 'tan', 'tanh', 'atan', 'atanh'],
                           deg: int):
        number = math.radians(deg)
        if method == "sin":
            result = math.sin(number)
            await interaction.response.send_message(result)
        if method == "sinh":
            result = math.sinh(number)
            await interaction.response.send_message(result)
        if method == "asin":
            result = math.asin(number)
            await interaction.response.send_message(result)
        if method == "asinh":
            result = math.asinh(number)
            await interaction.response.send_message(result)
        if method == "cos":
            result = math.cos(number)
            await interaction.response.send_message(result)
        if method == "cosh":
            result = math.cosh(number)
            await interaction.response.send_message(result)
        if method == "acos":
            result = math.acos(number)
            await interaction.response.send_message(result)
        if method == "acosh":
            result = math.acosh(number)
            await interaction.response.send_message(result)
        if method == "tan":
            result = math.tan(number)
            await interaction.response.send_message(result)
        if method == "tanh":
            result = math.tanh(number)
            await interaction.response.send_message(result)
        if method == "atan":
            result = math.atan(number)
            await interaction.response.send_message(result)
        if method == "atanh":
            result = math.atanh(number)
            await interaction.response.send_message(result)

    @app_commands.command(name="pi", description="Math feature")
    @app_commands.describe(decimals="Amount of Decimals")
    async def math_pi(self, interaction: discord.Interaction, decimals: int):
        mp.dps = decimals
        await interaction.response.send_message(mp.pi)

    @app_commands.command(name="factorial", description="Math feature")
    @app_commands.describe(number="Factorial of ...")
    async def math_factorial(self, interaction: discord.Interaction, number: int):
        result = math.factorial(number)
        await interaction.response.send_message(result)

    @app_commands.command(name="calculator", description="Math feature")
    async def math_calculator(self, interaction: discord.Interaction):
        embed = discord.Embed(title='Calculator', description='`Enter your equation below`', colour=COLOUR)
        await interaction.response.send_message(embed=embed, view=CalcView(interaction, embed))

# LOADING CLASSES
tree.add_command(Fun(), guild=SERVER_ID)
tree.add_command(Mod(), guild=SERVER_ID)
tree.add_command(Info(), guild=SERVER_ID)
tree.add_command(Picture(), guild=SERVER_ID)
tree.add_command(Math(), guild=SERVER_ID)

# RUNNING THE BOT

async def sync_slash():
    await bot.wait_for('ready')
    await tree.sync(guild=SERVER_ID)

async def main():
    async with bot:
        bot.loop.create_task(sync_slash())
        await bot.start(TKN)

asyncio.run(main())
