import discord
import json

bot = discord.Bot()
bot.load_extension('cogs.audio')

# define bot events
@bot.event
async def on_ready():
    print(f"{bot.user} is ready and online!")

# read settings json file to dict
settings_file = open('config/settings.json')
settings = json.load(settings_file)

# start the bot
bot.run(settings["token"])
