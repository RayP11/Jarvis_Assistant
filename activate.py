import sounddevice as sd
import numpy as np
from functions import ai_response
import threading


# Parameters
threshold = 0.9  # Threshold for detecting a clap (higher = less sensitive)
clap_count = 0  # Counter for detected claps

# Callback function to process audio data
def audio_callback(indata, frames, time, status):
    global clap_count
    if status:
        print(status)
    # Convert audio to a numpy array
    audio_data = np.abs(indata)
    # Check if the audio data exceeds the threshold
    if np.max(audio_data) > threshold:
        clap_count += 1
        print(f'Clap detected: {clap_count}')
        if clap_count == 2:
            # Stop the stream after detecting two claps
            raise sd.CallbackStop

clap_stop = False

def getClap():
    global clap_count
    # Set up the audio stream
    with sd.InputStream(callback=audio_callback):
        print("Listening for claps...")
        # Keep the program running to listen for claps
        sd.sleep(1)
        if clap_count == 2:
            ai_response("Hello Jarvis")
            return True
        

def clap_thread():
    c_t = threading.Thread(target = getClap, daemon=True)
    c_t.start()