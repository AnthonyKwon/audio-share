# list of referenced code:
# https://stackoverflow.com/a/70502611
# https://stackoverflow.com/a/57928940
# https://github.com/respeaker/usb_4_mic_array/issues/22#issuecomment-435764587

import discord
from discord.ext import commands
import pyaudio
import numpy as np

async def join_voice(self, ctx):
    vc = ctx.voice_client

    if not vc:
        vc = await ctx.author.voice.channel.connect()

        if ctx.author.voice.channel.id != vc.channel.id:
            return None

    return vc

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
        # read audio stream data from device
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
    
    # join to the voice channel
    @commands.slash_command(name="join", description="Join the voice channel.", ephemeral=True)
    async def join(self, ctx):
        # join to the voice channel
        vc = await join_voice(self, ctx)

        # if failed to join voice channel (user not joined to vc)
        if vc == None:
            return await ctx.respond("You must be in the same voice channel as the bot.", ephemeral=True)

        # show message
        await ctx.respond("Connected to voice channel.", ephemeral=True)

    # leave the voice channel
    @commands.slash_command(name="leave", description="Leave the voice channel.")
    async def leave(self, ctx):
        vc = ctx.voice_client
        
        # if bot is not in the voice channel
        if not vc:
            return await ctx.respond("I'm not in the voice channel.", ephemeral=True)
        
        # leave voice channel
        await vc.disconnect()
        await ctx.respond("Disconnected from voice channel!", ephemeral=True)

    # play the system audio to the voice channel
    @commands.slash_command(name="play", description="Play the system audio.")
    async def play(self, ctx):
        vc = ctx.voice_client

        # if bot is not in the voice channel
        if not vc:
            vc = await join_voice(self, ctx)
            # when failed to join voice channel
            if vc == None:
                return await ctx.respond("You must be in the same voice channel as the bot.", ephemeral=True)

        # if bot is already playng audio
        if vc.is_playing():
            return await ctx.respond("I'm playing audio!", ephemeral=True)
        
        try:
            # try to play audio
            vc.play(PyAudioPCM(input_device='Virtual Loopback'))
            await ctx.respond("Playing system audio to voice channel.", ephemeral=True)
        except Exception as err:
            await ctx.respond("Failed to play system audio!", ephemeral=True)
            print(err)

    # stop playing the system audio to the voice channel
    @commands.slash_command(name="stop", description="Stop playing the audio.")
    async def stop(self, ctx):
        vc = ctx.voice_client

        # if bot is not in the voice channel
        if not vc:
            vc = await join_voice(self, ctx)
            # when failed to join voice channel
            if vc == None:
                return await ctx.respond("You must be in the same voice channel as the bot.", ephemeral=True)

        # if bot is already playing audio
        if not vc.is_playing():
            return await ctx.respond("I'm not playing audio!", ephemeral=True)
        
        # stop playing audio
        vc.stop()
        await ctx.respond("Stopped playing audio.", ephemeral=True)

def setup(bot):
    bot.add_cog(Audio(bot))