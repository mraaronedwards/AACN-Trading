import discord
from discord.ext  import commands

bot = commands.Bot(command_prefix=".",intents=discord.Intents.all())

@bot.event
async def on_ready():
    print("Chris Bot is online")

with open("Chris_bot_token.txt") as file:
    token = file.read()

bot.run(token)