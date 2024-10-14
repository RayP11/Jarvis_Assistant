"""
Main module for JARVIS, a voice-activated assistant.

Handles user interactions, processes commands, and manages functionalities like opening applications and providing responses.
"""

import threading
import random
import time
import speech_recognition as sr
import face_recognition
import cv2
from flask import Flask, jsonify, send_from_directory
from openaiAPI import Create_Jarvis, messages
import webbrowser
from recognize_speech import (listen, r)
from openaiAPI import (genImage, SpeakText, capture_and_analyze)
from get_weather import (weather)
from messages import (sendText)
from user_commands import (google_open, edge_open, netflix_open, today_weather, spotify_open,
                           play_music, what_time, stop_commands, play_video, timer_command,
                           random_song, generate_image, j_sleep, j_night, volume_decrease, volume_increase,
                           send_message, look_screen, wake_up, find_match)
from functions import (playMusic, get_time, play_youtube, timer, volumeDown, volumeUp, handle_schedule_command, start_edge, start_netflix)

# Initialize Flask app
app = Flask(__name__)
responses = []

@app.route('/api/responses', methods=['GET'])
def get_responses():
    formatted_responses = [
        {"text": response["text"], "imageUrl": response.get("imageUrl")}
        if isinstance(response, dict) else {"text": response, "imageUrl": None}
        for response in responses
    ]
    return jsonify(formatted_responses)

@app.route('/')
def serve_html():
    return send_from_directory('', 'index.html')  # Serve the HTML file

@app.route('/api/weather', methods=['GET'])
def get_weather_data():
    weather_info = weather("Salisbury")  # Fetch the weather data
    # Example response parsing
    temp_str = weather_info.split("currently ")[1].split(" degrees")[0]
    description_str = weather_info.split("and it is ")[1].strip(".")

    # Mapping weather descriptions to emojis
    emoji_map = {
        "Sunny": "☀️",
        "Cloudy": "☁️",
        "Rain": "🌧️",
        "Snow": "❄️",
        "Thunderstorm": "⛈️",
        "Clear": "🌤️",
        "Overcast": "🌥️",
    }

    # Get emoji based on description
    emoji = emoji_map.get(description_str, "🌈")  # Default to a rainbow if not found

    # Create structured JSON response
    response_data = {
        "weather": {
            "description": description_str,
            "emoji": emoji
        },
        "main": {
            "temp": temp_str
        }
    }

    return jsonify(response_data)

@app.route('/api/delete_image', methods=['POST'])
def delete_image():
    if responses:  # Check if there are any responses
        responses[-1]['imageUrl'] = None  # Clear the image URL from the last response
    return jsonify(success=True)

# Define states for Jarvis
class JarvisState:
    ACTIVE = "active"
    SLEEP = "sleep"
    STOPPED = "stopped"

# Initialize state and sleep timer
state = JarvisState.ACTIVE
sleep_timer = None



def activate_sleep_mode():
    global state, sleep_timer
    if sleep_timer:
        sleep_timer.cancel()  # Cancel any existing timer
    sleep_timer = threading.Timer(300.0, set_sleep_mode)  # Set sleep mode after 300 seconds of inactivity
    sleep_timer.start()

def set_sleep_mode():
    global state
    state = JarvisState.SLEEP

def reset_sleep_timer():
    global sleep_timer
    if sleep_timer:
        sleep_timer.cancel()  # Cancel existing timer
    activate_sleep_mode()  # Start a new timer

def ai_response(text):
    """Get a response from ChatGPT and speak it.""" 
    messages.append({"role": "user", "content": text})
    response = Create_Jarvis(messages)
    responses.append(response)  # Append the response to the list
    SpeakText(response)

def generate_image_response(text):
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

# Load your known face image and get its encoding
known_image = face_recognition.load_image_file("C:\\Users\\Raypo\\OneDrive\\Pictures\\Camera Roll\\my_face.jpg")
known_face_encoding = face_recognition.face_encodings(known_image)[0]  # Get the encoding


faceId_run = False

def find_ray():
    """Facial recognition to identify if I'm present."""
    global findingRay, state, faceId_run  # Include state to modify it
    findingRay = True  # Initialize findingRay

    video_capture = cv2.VideoCapture(0)

    while findingRay:
        # Check if Jarvis is still in sleep mode
        if state != JarvisState.SLEEP:
            findingRay = False  # Stop searching for the face
            break  # Exit the loop if JARVIS is activated

        # Capture a single frame of video
        ret, frame = video_capture.read()

        if not ret:
            print("Failed to capture image")
            break

        # Resize the frame for faster processing
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

        # Find all the faces and face encodings in the frame
        face_locations = face_recognition.face_locations(small_frame)
        face_encodings = face_recognition.face_encodings(small_frame, face_locations)

        for face_encoding in face_encodings:
            # See if the face is a match for the known face(s)
            match = face_recognition.compare_faces([known_face_encoding], face_encoding)  # Use the encoding
            if match[0]:  # If there is a match
                # Face found
                findingRay = False  # Stop searching for the face
                faceId_run = False #ensure face_id is not run multiple times
                ai_response("ask me about something, any reminders, past conversations, how I'm doing, anything you can help me with. Make it very brief. Make sure it's something we've talked about")  # Prompt ChatGPT response
                state = JarvisState.ACTIVE  # Change state to ACTIVE
                time.sleep(.5)
                reset_sleep_timer()  # Reset the sleep timer
                break  # Exit the loop after finding the face

    # Release handle to the webcam
    video_capture.release()
    cv2.destroyAllWindows()


def chat():
    """
    handles the microphone input and all of the user commands that Jarvis can take in.
    Checks through each list of possible commands to determine what the user wants Jarvis to do
    If no commands are found - a standard chatGPT response is given
    """
    global state, faceId_run
    wake_word = 'jarvis'
    state = JarvisState.ACTIVE

    while state != JarvisState.STOPPED:
        if state == JarvisState.SLEEP and faceId_run == False:
            # Start facial recognition in a separate thread while in sleep mode
            threading.Thread(target=find_ray, daemon=True).start()
            faceId_run = True

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
                        elif find_match(today_weather, text):
                            response = weather("Salisbury")
                            responses.append(response)
                            SpeakText(response)
                        elif find_match(j_sleep, text):
                            reset_sleep_timer()
                            ai_response(text)
                            set_sleep_mode()
                        elif find_match(play_music, text):
                            response = playMusic(text)
                            responses.append(response)
                        elif find_match(random_song, text):
                            choices = ["Blinding Lights", "Goosbumps", "back in black acdc", "Do I wanna know"]
                            song = random.choice(choices)
                            response = playMusic(song)
                            responses.append(response)
                        elif find_match(generate_image, text):
                            response = generate_image_response(text)
                            if response:
                                responses.append(response)  # Append the entire response object
                                SpeakText("I've provided your image here")
                        elif find_match(look_screen, text):
                            response = capture_and_analyze(text)
                            responses.append(response)
                            SpeakText(response)
                        elif find_match(wake_up, text):
                            if 'jarvis' in text:
                                text = text.replace("jarvis", '')
                            handle_schedule_command(text)
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
                        elif find_match(timer_command, text):
                            response = "timer set for you sir"
                            responses.append(response)
                            def timerUI():
                                timer(text)
                            threading.Thread(target=timerUI, daemon=True).start()
                        else:
                            ai_response(text)

                except sr.UnknownValueError:
                    pass  # Ignore errors due to unrecognized speech
                except sr.RequestError as e:
                    print(f"Error with the recognition service: {e}")  # Print error for debugging

def main():
    """Main function to start the user interface, facial recognition, and chat functions."""
    # Start the Flask app in a separate thread
    threading.Thread(target=app.run, kwargs={'host': '0.0.0.0', 'port': 8000, 'debug': False}, daemon=True).start()
    
    # Open the browser interface
    webbrowser.open('http://localhost:8000')

    # start the chat function in the main thread
    chat()

if __name__ == "__main__":
    main()
