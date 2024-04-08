CURRENTLY NOT TESTED IN OTHER ENVIRONMENTS!

## Installation
- Initialize venv: `python -m venv venv`
- Install dependencies: `venv/bin/pip install -r requirements.txt`  
- Test if PyAudio is working correctly: `venv/bin/python -m utils.pyaudio_test`
- Copy example configuration file and add your bot token

## Usage
Launch command is `venv/bin/python main.py`.  
Script will remove virtual devices when exited gracefully.   
If not, you will have to remove generated virtual devices manually.  
