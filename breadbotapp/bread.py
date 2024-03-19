import discord
from discord.ext import commands
from discord import app_commands
from dotenv import dotenv_values
import re
import json

intents = discord.Intents.all()
intents.voice_states = True
intents.messages = True

bot = commands.Bot(command_prefix='+', activity=discord.Game(name="/help To know more"), intents=intents)


# Dictionary to store user scores
user_scores = {}
SCORES_FILE = "user_scores.json"

# Load user scores from file
def load_user_scores():
    try:
        with open(SCORES_FILE, "r") as file:
            user_scores_str = json.load(file)
            # Convert user IDs from strings to integers
            return {int(user_id): score for user_id, score in user_scores_str.items()}
    except FileNotFoundError:
        return {}

# Save user scores to file
def save_user_scores():
    # Convert user IDs from integers to strings
    user_scores_str = {str(user_id): score for user_id, score in user_scores.items()}
    with open(SCORES_FILE, "w") as file:
        json.dump(user_scores_str, file)

def translate_to_emojis(text):
    translation = []
    for char in text.upper():
        if char.isalpha():
            translation.append(f':{char.upper()}bread:')
    return ''.join(translation)

@bot.event
async def on_ready():
    global user_scores
    user_scores = load_user_scores()
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} Commands")
    except Exception as e:
        print(e)
    print(f'Logged in as {bot.user.name}')
    
        
@bot.event
async def on_reaction_add(reaction, user):
    # Check if the reaction is added to the specific message
    if reaction.message.channel.id == 1219547466370777109:
        # Fetch the channel
        channel = bot.get_channel(1219547466370777109)
        # Fetch the most recent message in the channel
        message = await channel.fetch_message(channel.last_message_id)
        if message and reaction.message == message:
            guild = reaction.message.guild
            role = discord.utils.get(guild.roles, name="breaderfied")
            if role and reaction.emoji == "🍞":  # Assuming the reaction emoji is a bread
                await user.add_roles(role)
                print("Added role 'breaderfied'")

@bot.event
async def on_message(message):
    # Check if the message author is not a bot
    if message.author.bot:
        return

    # Check if the message contains only emojis
    emojis = re.findall(r'<:[a-zA-Z0-9_]+:\d+>|[\U0001F300-\U0001F5FF\U0001F600-\U0001F64F\U0001F680-\U0001F6FF\U0001F700-\U0001F77F\U0001F780-\U0001F7FF\U0001F800-\U0001F8FF\U0001F900-\U0001F9FF\U0001FA00-\U0001FA6F\U0001FA70-\U0001FAFF\U00002702-\U000027B0\U00002639]+', message.content)
    
    if emojis and len(''.join(emojis)) == len(message.content.replace(" ", "").replace("\n", "")):
        for emoji in emojis:
            if "bread" in emoji or "🍞" in emoji:
                await message.add_reaction("🍞")
                user_scores[message.author.id] = user_scores.get(message.author.id, 0) + 1
                save_user_scores()
                role_thresholds = {
                    "🍞BREAD 10": 10,
                    "🍞BREAD 100": 100,
                    "🍞BREAD 500": 500,
                    "🍞BREAD 1,000": 1000,
                    "🍞BREAD 20,000": 20000,
                    "🍞BREAD 100,000": 100000
                }

                for role_name, threshold in role_thresholds.items():
                    if user_scores[message.author.id] >= threshold:
                        role = discord.utils.get(message.author.guild.roles, name=role_name)
                        if role:
                            await message.author.add_roles(role)
                        else:
                            break
    else:
        # Delete the message if it doesn't meet the criteria
        await message.delete()

    await bot.process_commands(message)


@bot.tree.command(name="translate", description="Translates your message into bread emoji")
@app_commands.describe(text = "Enter your message using normal characters")
async def translate(interaction: discord.Interaction, text:str):
    translated_text = translate_to_emojis(text)
    return await interaction.response.send_message(f"{translated_text}", ephemeral= True)

@bot.tree.command(name="score", description="Gives your current score")
async def get_score(interaction: discord.Interaction):
    user_id = interaction.user.id
    user_score = user_scores.get(user_id, 0)
    await interaction.response.send_message(f"Your current score is: {user_score}", ephemeral=True)

@bot.tree.command(name="leaderboard", description="Shows the leaderboard of users with the most bread")
async def leaderboard(interaction: discord.Interaction):
    sorted_scores = sorted(user_scores.items(), key=lambda x: x[1], reverse=True)
    
    leaderboard_message = "🍞 **Leaderboard** 🍞\n"
    for index, (user_id, score) in enumerate(sorted_scores[:10], start=1):
        user = bot.get_user(user_id)
        if user:
            leaderboard_message += f"{index}. {user.display_name}: {score}\n"
    
    await interaction.response.send_message(leaderboard_message, ephemeral=True)


bot.run(dotenv_values("./newToken.env")["BOT_TOKEN"])
