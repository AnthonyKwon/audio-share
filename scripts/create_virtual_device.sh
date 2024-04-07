#!/bin/bash

# loopback audio from default deice to virtual device
export LC_ALL=C
DEFAULT_OUTPUT=$(pactl info|sed -n -e 's/^.*Default Sink: //p')
pactl load-module module-null-sink sink_name=virtual_speaker sink_properties="'device.description=\"Virtual Speaker\"'"
pactl set-default-sink virtual_speaker
pactl load-module module-loopback source=virtual_speaker.monitor sink=$DEFAULT_OUTPUT
nohup pw-loopback -n "virtual_loopback" -g "virtual_speaker" --capture-props='node.target=virtual_speaker' --playback-props='media.class=Audio/Source node.name=virtual_speaker node.description="Monitor of Virtual Speaker"' >/dev/null &