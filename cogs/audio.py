# list of referenced code:
# https://stackoverflow.com/a/70502611
# https://stackoverflow.com/a/57928940
# https://github.com/respeaker/usb_4_mic_array/issues/22#issuecomment-435764587

import discord
from discord.ext import commands
import pyaudio
import numpy as np

def get_device_by_name(p, name):
    # check and return when matching device found
    for i in range(p.get_device_count()):
        dev = p.get_device_info_by_index(i)
        if (dev['name'] == name and dev['hostApi'] == 2):
            return dev
    
    # exit when device is not available
    raise Exception()

class PyAudioPCM(discord.AudioSource):
    def __init__(self, channels=2, rate=48000, chunk=960, input_device=-1) -> None:
        p = pyaudio.PyAudio()

        # get index of device from parameter
        index = -1
        if type(input_device) == str:
            device = get_device_by_name(p, input_device)
            # overwrite parameter with with device default
            index = device['index']
            channels = device['maxInputChannels']
            rate=int(device['defaultSampleRate'])
        else:
            index = input_device
        
        self.chunks = chunk
        self.channels = channels
        self.input_stream = p.open(format=pyaudio.paInt16, channels=channels, rate=rate, input=True, input_device_index=index, frames_per_buffer=chunk)

    def read(self) -> bytes:
        data = self.input_stream.read(self.chunks)

        if self.channels > 2:
            # convert string to numpy array
            data_array = np.fromstring(data, dtype='int16')

            # deinterleave, select 1 channel
            channel0 = data_array[0::self.channels]
            channel1 = data_array[1::self.channels]
            merged_channel = np.ravel([channel0, channel1], 'F')
            
            return bytes(merged_channel)
        else:
            return data

class Audio(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.slash_command(name="join", description="Join the voice channel.", ephemeral=True)
    async def join(self, ctx):
        vc = ctx.voice_client

        if not vc:
            vc = await ctx.author.voice.channel.connect()

            if ctx.author.voice.channel.id != vc.channel.id:
                return await ctx.respond("You must be in the same voice channel as the bot.", ephemeral=True)

        await ctx.respond("Connected to voice channel.", ephemeral=True)

    @commands.slash_command(name="play", description="Mirror the system sound.")
    async def play(self, ctx):
        vc = ctx.voice_client

        if not vc:
            return await ctx.respond("Please use `/join` first!", ephemeral=True)
        
        vc.play(PyAudioPCM(input_device='Virtual Speaker'))
        await ctx.respond("Playing system audio to voice channel.", ephemeral=True)

    @commands.slash_command(name="leave", description="Leave the voice channel.")
    async def leave(self, ctx):
        vc = ctx.voice_client
        
        if not vc:
            return await ctx.respond("I'm not in the voice channel.", ephemeral=True)
        
        await vc.disconnect()
        await ctx.respond("Disconnected from voice channel!", ephemeral=True)

def setup(bot):
    bot.add_cog(Audio(bot))