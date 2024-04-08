from pulsectl import Pulse

def create_device():
    modules = []
    with Pulse("virtual-device") as pulse:
        # get default audio device
        default_device = pulse.server_info().default_sink_name

        # create virtual audio device
        new_module = pulse.module_load("module-null-sink", args=("sink_name=virtual_speaker", "sink_properties='device.description=\"Virtual Speaker\"'"))
        modules.insert(0, new_module)
        pulse.default_set(pulse.get_sink_by_name('virtual_speaker'))
        new_module = pulse.module_load("module-loopback", args=("source=virtual_speaker.monitor", f"sink={default_device}"))
        modules.insert(0, new_module)
        # weirdly, under pipewire(maybe?), PyAudio works correctly only when we create fake source device.
        new_module = pulse.module_load("module-remap-source", args=("master=virtual_speaker.monitor", "source_name=virtual_loopback", "source_properties='device.description=\"Virtual Loopback\"'"))
        modules.insert(0, new_module)
        
        print("[audio] virtual devices created.")
        pulse.close()
    
    return modules, default_device

def remove_device(devices, default_device):
    with Pulse("virtual-device") as pulse:
        # restore default audio device
        pulse.default_set(pulse.get_sink_by_name(default_device))

        # remove all virtual devices
        for device in devices:
            pulse.module_unload(device)
        
        print("[audio] virtual devices removed.")
        pulse.close()