import speech_recognition as sr
import pyttsx3
import time

# Initialize the speech recognition and text-to-speech engines
r = sr.Recognizer()
engine = pyttsx3.init()

def SpeakText(command):
    """
    Converts text to speech and speaks it out loud.

    Args:
        command (str): The text to be spoken.

    Returns:
        None
    """
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[0].id)
    engine.say(command)
    engine.runAndWait()

def listen(source, timeout=5):
    """
    Listens for audio input from the specified source.

    Args:
        source (sr.AudioSource): The source to listen to (e.g., microphone).
        timeout (int): The time in seconds to wait for audio input.

    Returns:
        sr.AudioData: The audio data captured from the source.
    """
    audio_data = None
    start_time = time.time()

    while time.time() - start_time < timeout:
        try:
            audio_data = r.listen(source)
            return audio_data  # Return the audio data if captured successfully
        except sr.WaitTimeoutError:
            print("Timeout occurred, retrying...")
            continue
        except sr.RequestError as e:
            print(f"Speech recognition request error: {e}")
            # Optionally retry or handle as needed
        except sr.UnknownValueError:
            print("Speech recognition could not understand audio")
            # Optionally retry or handle as needed

    return audio_data