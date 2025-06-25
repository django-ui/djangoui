#!/usr/bin/env python
# 
import sounddevice as sd
import numpy as np
from openwakeword.model import Model

# Load the model with the desired wakeword
oww = Model()
#owm = Model(wakeword_models=["hey jarvis"], inference_framework="onnx")

#oww.enable_custom_wakeword("hey_jarvis")  # built-in wakeword in openWakeWord

# Constants
SAMPLE_RATE = 16000  # must match model's expected rate
BLOCK_SIZE = 10240
CHANNELS = 1

print("Listening for 'Hey Jarvis'...")
result, i, audio_data, paudio_data =0,0, [], []
def audio_callback(indata, frames, time, status):
    if status:
        print(f"Error: {status}")
        return
    global result, i, audio_data, paudio_data
    
    i += 1
    # Preprocess audio
    audio_data = np.squeeze(indata)
    #audio_data = indata
    if ( np.all(audio_data <0.09) ):
        print(f"SILENT: {len(paudio_data)} { len(audio_data)} {audio_data[0]} \r", end="")
        paudio_data = audio_data
        return
    elif ( len(paudio_data) > 0 and np.all(audio_data == paudio_data) ):
        print(f"DIFF/SAME: {len(paudio_data)} { len(audio_data)} {paudio_data}")
        #return
    sd.play(indata,  blocking=True)
        
    paudio_data = audio_data
    print()
    # Feed audio to the model
    result = oww.predict(audio_data)
    print(f'{i} Result: {result["hey_jarvis"]} {result["alexa"]} {time} Status: {status}\r', end="\n")

    # Check for trigger
    #if result["hey_jarvis"] > 0.5:
    #    print("==> Wake word 'Hey Jarvis' detected!")
    for t in result:
        if result[t] > 0.5:
            print( f"==> {t} Wake word detected!")
            

# Start audio stream
with sd.InputStream(callback=audio_callback,
                    channels=CHANNELS,
                    samplerate=SAMPLE_RATE,
                    blocksize=BLOCK_SIZE):
    input("Press Enter to stop...\n")
