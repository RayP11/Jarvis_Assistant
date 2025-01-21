"""
Main module for JARVIS, a voice-activated assistant.

Handles user interactions, processes commands, manages various functionalities like opening applications,
providing responses, and performing facial recognition to detect the presence of the user.
"""

import threading
import random
import time
import speech_recognition as sr
import face_recognition
import cv2
from flask import (Flask, jsonify, send_from_directory)
import webbrowser
from get_weather import (get_weather)
from recognize_speech import (listen, r)
from openaiAPI import (Create_Jarvis, messages, genImage, SpeakText, capture_and_analyze, camera_response)
from messages import (sendText)
from user_commands import (google_open, edge_open, netflix_open, weather_forecast, spotify_open,
                           play_music, what_time, play_video, timer_command,
                           random_song, generate_image, j_sleep, volume_decrease, volume_increase,
                           send_message, wake_up, send_soph, find_match)
from functions import (playMusic, get_time, play_youtube, timer, volumeDown, volumeUp, handle_schedule_command, scheduleText, handle_schedule_text, start_edge, start_netflix)

# Initialize Flask app
app = Flask(__name__)
responses = []

@app.route('/api/responses', methods=['GET'])
def get_responses():
    """
    Retrieve the latest responses from JARVIS.
    Responses include both text and an optional image URL.
    """
    formatted_responses = [
        {"text": response["text"], "imageUrl": response.get("imageUrl")}
        if isinstance(response, dict) else {"text": response, "imageUrl": None}
        for response in responses
    ]
    return jsonify(formatted_responses)

@app.route('/')
def serve_html():
    """Serve the HTML file for the main user interface."""
    return send_from_directory('', 'index.html')  # Serve the HTML file

@app.route('/api/delete_image', methods=['POST'])
def delete_image():
    """
    Clear the image URL from the latest response if one exists.
    """
    if responses:  # Check if there are any responses
        responses[-1]['imageUrl'] = None  # Clear the image URL from the last response
    return jsonify(success=True)

# Define states for Jarvis
class JarvisState:
    ACTIVE = "active"
    SLEEP = "sleep"
    STOPPED = "stopped"

class JarvisMode:
    HARDWARE = "hardware"
    SOFTWARE = "software"
    DEFAULT = "default"

#initialize mode
mode = JarvisMode.DEFAULT

# Initialize state, sleep timer
state = JarvisState.ACTIVE
sleep_timer = None

def activate_sleep_mode():
    """
    Start timers for sleep mode and facial recognition. JARVIS will enter sleep mode after
    300 seconds of inactivity and activate facial recognition after 10 minutes.
    """
    global state, sleep_timer
    if sleep_timer:
        sleep_timer.cancel()  # Cancel any existing timer
    sleep_timer = threading.Timer(300.0, set_sleep_mode)  # Set sleep mode after 300 seconds of inactivity
    sleep_timer.start()

def set_sleep_mode():
    """
    Set JARVIS to sleep mode and reset the timers.
    """
    global state
    state = JarvisState.SLEEP
    activate_sleep_mode()

def reset_sleep_timer():
    """
    Reset sleep timer.
    """
    global sleep_timer
    if sleep_timer:
        sleep_timer.cancel()  # Cancel existing sleep timer
    activate_sleep_mode()  # Start both timers again


def ai_response(text):
    """
    Generate a response and speak it - using the OpenAI API
    """ 
    messages.append({"role": "user", "content": text})
    response = Create_Jarvis(messages)
    responses.append(response)  # Append the response to the list
    SpeakText(response)

def screen_respose(text):
    messages.append({"role": "user", "content": text})
    response = capture_and_analyze(text)
    responses.append(response)
    SpeakText(response)

def vision_response(text):
    response = camera_response(text)
    responses.append(response)
    SpeakText(response)

def generate_image_response(text):
    """
    Generate an image based on user input and return the response with the image URL.
    """
    choices = [
        "Generating image for you ... please wait", 
        "You got it ... please wait a moment", 
        "Creating that image now...please wait"
    ]
    response_text = random.choice(choices)
    SpeakText(response_text)
    responses.append(response_text)

    image_url = genImage(text)  # Generate the image and get its URL

    # Append both the response text and image URL
    responses.append({
        "text": "your image",
        "imageUrl": image_url
    })

    return {
        "text": "your image",
        "imageUrl": image_url
    }

def chat():
    """
    Handles microphone input and all user commands for JARVIS.
    Processes recognized text to determine the appropriate command or response.
    """
    global state, mode
    wake_word = 'jarvis'
    state = JarvisState.ACTIVE
    mode = JarvisMode.DEFAULT

    

    while state != JarvisState.STOPPED:
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source)  # Adjust for ambient noise
            audio_data = listen(source, timeout=5)  # Listen for audio input

            if audio_data:
                try:
                    text = r.recognize_google(audio_data).lower()  # Recognize and lower case the text

                    if state == JarvisState.SLEEP and wake_word in text:
                        state = JarvisState.ACTIVE
                        reset_sleep_timer()

                    if state == JarvisState.ACTIVE:
                        reset_sleep_timer()  # Reset timer whenever a command is processed
                        # Process user commands based on recognized text
                        if find_match(google_open, text):
                            response = "Opening Google for you."
                            responses.append(response)
                            SpeakText(response)
                        elif find_match(j_sleep, text):
                            reset_sleep_timer()
                            ai_response(text)
                            set_sleep_mode()
                        elif find_match(play_music, text):
                            response = playMusic(text)
                            responses.append(response)
                            state = JarvisState.SLEEP
                        elif find_match(random_song, text):
                            music = "Give me a random song in the rock, rap, pop, or alternative genre. Try to keep the songs different to what you usually pick, and remember my preferences. This response should only say the song name and nothing else, not even the artist."
                            messages.append({"role": "user", "content": music})
                            response = Create_Jarvis(messages)
                            response = playMusic(response)
                            responses.append(response)
                            state = JarvisState.SLEEP
                        elif find_match(generate_image, text):
                            response = generate_image_response(text)
                            if response:
                                responses.append(response) 
                                SpeakText("I've provided your image here")
                        elif find_match(weather_forecast, text):
                            text = "give a brief response only specifying what I ask. Make sure you don't abbreviate the degrees or unit" + text
                            forecast = get_weather()
                            has_forecast = False
                            #Only feed weather info to OpenAI if there is no prior updated data
                            for message in messages:
                                if forecast in message:
                                    has_forecast = True
                                    break
                            if has_forecast:
                                ai_response(text)
                            else:
                                ai_response(text + forecast)
                        elif "hardware mode" in text:
                            mode = JarvisMode.HARDWARE
                            #ai_response(text)
                            SpeakText("Activating Hardware mode")
                        elif "software mode" in text:
                            mode = JarvisMode.SOFTWARE
                            SpeakText("Activating software mode")
                        elif "default mode" in text:
                            mode = JarvisMode.DEFAULT
                            SpeakText("Activating default mode sir")
                        elif find_match(wake_up, text):
                            if 'jarvis' in text:
                                text = text.replace("jarvis", '')
                            handle_schedule_command(text)
                        elif find_match(send_soph, text):
                            if 'jarvis' in text:
                                text = text.replace("jarvis", '')
                            handle_schedule_text(text)
                        elif find_match(edge_open, text):
                            response = "Opening Microsoft Edge for you"
                            responses.append(response)
                            start_edge()
                        elif find_match(netflix_open, text):
                            response = "Opening Netflix for you"
                            responses.append(response)
                            start_netflix()
                        elif find_match(send_message, text):
                            response = "Sending message for you sir"
                            responses.append(response)
                            SpeakText(response)
                            sendText(text)
                        elif find_match(volume_increase, text):
                            volumeUp()
                        elif find_match(volume_decrease, text):
                            volumeDown()
                        elif find_match(play_video, text):
                            response = play_youtube(text)
                            responses.append(response)
                            SpeakText(response)
                            state = JarvisState.SLEEP
                        elif find_match(timer_command, text):
                            response = "timer set for you sir"
                            responses.append(response)
                            def timerUI():
                                timer(text)
                            threading.Thread(target=timerUI, daemon=True).start()
                        elif "jarvis power off" in text:
                            ai_response(text)
                            state = JarvisState.STOPPED
                        else:
                            if mode == JarvisMode.DEFAULT:
                                ai_response(text)
                            elif mode == JarvisMode.HARDWARE:
                                vision_response(text)
                            else:
                                screen_respose(text)

                except sr.UnknownValueError:
                    pass  # Ignore errors due to unrecognized speech
                except sr.RequestError as e:
                    print(f"Error with the recognition service: {e}")  # Print error for debugging

def main():
    """
    Main function to start the user interfaceand chat functions.
    """
    # Start the Flask app in a separate thread
    threading.Thread(target=app.run, kwargs={'host': '0.0.0.0', 'port': 8000, 'debug': False}, daemon=True).start()
    
    # Open the browser interface
    webbrowser.open('http://localhost:8000')

    # start the chat function in the main thread
    chat()

if __name__ == "__main__":
    main()
