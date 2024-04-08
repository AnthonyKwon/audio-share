import pyaudio
import wave
import pulse

print("Generating device...")
modules, default_device = pulse.create_device()

print("Done. Initializing Pyaudio...")
p = pyaudio.PyAudio()
device = None

print("\nList of devices:")
for i in range(p.get_device_count()):
    print(p.get_device_info_by_index(i))

# check and assign device
for i in range(p.get_device_count()):
    dev = p.get_device_info_by_index(i)
    if (dev['name'] == 'Virtual Loopback' and dev['hostApi'] == 2):
        device = dev

# exit when device is not available
if device == None:
    print("Device failed to create or not available!")
    pulse.remove_device(modules, default_device)
    exit(1)

print("\nCurrently Seleted Device information:")
print(device)

# device information
FORMAT = pyaudio.paInt16
CHANNELS = device['maxInputChannels']
INDEX = device['index']
RATE = int(device['defaultSampleRate'])
TIME = 5
CHUNK = int(RATE / (TIME*60))

print(f"\nStarting test record for {TIME} second(s)...")

# open audio stream
stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, input_device_index=INDEX, frames_per_buffer=CHUNK)
frames = []

# read audio stream
for i in range(0, int((device['defaultSampleRate'] / CHUNK) * TIME)):
    data = stream.read(CHUNK)
    frames.append(data)

stream.stop_stream()
stream.close()
p.terminate()

print("Saving to file...")

filename = "result.wav"
wf = wave.open(filename, 'wb')
wf.setnchannels(CHANNELS)
wf.setsampwidth(p.get_sample_size(FORMAT))
wf.setframerate(RATE)
wf.writeframes(b''.join(frames))

print(f"Done. File saved to \"{filename}\".")

print("Closing and removing device...")
wf.close()
pulse.remove_device(modules, default_device)
