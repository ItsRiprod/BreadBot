import discord
from discord import app_commands
from discord.ext import commands
from dotenv import dotenv_values

import random
import warnings


warnings.filterwarnings("ignore", category=RuntimeWarning)


intents = discord.Intents.all()
intents.voice_states = True
intents.messages = True

client = commands.Bot(command_prefix='+', activity=discord.Game(name="/help To know more"), intents=intents)

@client.event
async def on_ready():
    print(f'Logged in as {client.user.name}')

@client.event
async def on_message(message):
    has_emoji = any(char in emoji.UNICODE_EMOJI['en'] for char in message.content)
    
    # Check if the message has any emojis
    if not has_emoji:
        # Delete the message
        await message.delete()
        print(f'Message deleted from {message.author.name}: {message.content}')
    else:
        await message.add_reaction('🍞')
        
    await client.process_commands(message)



client.run(dotenv_values("./breadbotapp/token.env")["BOT_TOKEN"])



