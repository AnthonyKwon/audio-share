import pyaudio
import wave

p = pyaudio.PyAudio()
deviceProps = []

for i in range(p.get_device_count()):
    print(p.get_device_info_by_index(i))

# check and assign device
for i in range(p.get_device_count()):
    dev = p.get_device_info_by_index(i)
    if (dev['name'] == 'Virtual Speaker' and dev['hostApi'] == 2):
        deviceProps = dev

# exit when device is not available
if deviceProps == []:
    print("Device not available!")
    exit

print(deviceProps)

# device information
FORMAT = pyaudio.paInt16
CHANNELS = deviceProps['maxInputChannels']
INDEX = deviceProps['index']
RATE = int(deviceProps['defaultSampleRate'])
TIME = 5
CHUNK = int(RATE / (TIME*60))

# open audio stream
stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, input_device_index=INDEX, frames_per_buffer=CHUNK)

frames = []

# read audio stream
for i in range(0, int((deviceProps['defaultSampleRate'] / CHUNK) * TIME)):
    data = stream.read(CHUNK)
    frames.append(data)

stream.stop_stream()
stream.close()
p.terminate()

wf = wave.open("result.wav", 'wb')
wf.setnchannels(CHANNELS)
wf.setsampwidth(p.get_sample_size(FORMAT))
wf.setframerate(RATE)
wf.writeframes(b''.join(frames))
wf.close()