from io import BytesIO
import pygame
from dotenv import load_dotenv
import os
from elevenlabs.client import ElevenLabs
from elevenlabs import VoiceSettings

# Load environment variables from a .env file
load_dotenv()

# Load API key and voice ID from environment variables
elevenlabs_api_key = os.getenv('ELEVENLABS_API_KEY')
elevenlabs_voice_id = os.getenv("VOICE_ID")

if not elevenlabs_api_key:
    raise ValueError("ELEVENLABS_API_KEY environment variable not set")

# Initialize ElevenLabs client with the provided API key
client = ElevenLabs(api_key=elevenlabs_api_key)

# Initialize the pygame mixer for audio playback
pygame.mixer.init()

def SpeakText(text):
    """
    Convert text to speech using the ElevenLabs API and play it using pygame.

    Args:
        text (str): The text to be converted to speech.

    Raises:
        ValueError: If the ElevenLabs API key is not set in the environment variables.
        Exception: If there's an error during the text-to-speech conversion or playback.
    """
    try:
        # Convert text to speech using ElevenLabs API
        response = client.text_to_speech.convert(
            voice_id=elevenlabs_voice_id,  # ID of the pre-made voice
            optimize_streaming_latency="0",
            output_format="mp3_22050_32",
            text=text,
            model_id="eleven_turbo_v2",  # Model used for low latency
            voice_settings=VoiceSettings(
                stability=0.0,
                similarity_boost=1.0,
                style=0.0,
                use_speaker_boost=True
            ),
        )
        
        # Create a BytesIO object to hold the audio data
        audio_stream = BytesIO()
        
        # Write each chunk of audio data to the BytesIO stream
        for chunk in response:
            if chunk:
                audio_stream.write(chunk)
        
        # Reset the stream position to the beginning for reading
        audio_stream.seek(0)
        
        # Load the audio data into pygame mixer and play it
        pygame.mixer.music.load(audio_stream)
        pygame.mixer.music.play()
        
        # Wait for the audio playback to finish
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
    
    except ValueError as e:
        print(f"ValueError: {e}")
    except Exception as e:
        print(f"Exception occurred: {e}")