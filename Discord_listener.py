import discord

intents = discord.Intents.default()
intents.message_content = True  # Enable message content intent

client = discord.Client(intents=intents)

@client.event
async def on_message(message):
        print(f"Message from {message.author}: {message.content}")

client.run('MTMzMzYxOTAyMTA4OTczODc1Mg.G0ygyn.7PNpPIM3v6lomMXedf3kQqPNwTSXTWdIazphNA')  # Authorisation key grabbed from Chrome

@client.event
async def on_message(message):
        print(f"Message from {message.author}: {message.content}")