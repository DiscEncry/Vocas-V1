import discord, os
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')
    for filename in os.listdir("./functions"):
        if filename.endswith(".py"):  # Only load Python files
            cog_name = f"functions.{filename[:-3]}"  # Remove the .py extension
            try:
                bot.load_extension(cog_name)
                print(f"Loaded {cog_name}")
            except Exception as e:
                print(f"Failed to load {cog_name}: {e}")

bot.run("secret")