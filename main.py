import discord
import json
import atexit
import pulse

bot = discord.Bot()
bot.load_extension('cogs.audio')

# create virtual audio device and register remove event
print("[audio-share] creating virtual device...")
devices, default_device = pulse.create_device()
@atexit.register
def onexit():
    print("[audio-share] removing virtual device...")
    pulse.remove_device(devices, default_device)

# define bot events
@bot.event
async def on_ready():
    print(f"[audio-share] {bot.user} is ready!")

# read settings json file to dict
settings_file = open('config/settings.json')
settings = json.load(settings_file)

# start the bot
bot.run(settings["token"])
