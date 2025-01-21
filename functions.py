import os
import time
import datetime
import pywhatkit
import pyautogui
import re
from messages import sendGfText
from openaiAPI import Create_Jarvis, messages, SpeakText 
from Spotify_API import play_playlist, play_song
from flask import Flask, jsonify, send_from_directory
import threading


app = Flask(__name__)
responses = []

@app.route('/api/responses', methods=['GET'])
def get_responses():
    return jsonify(responses)

@app.route('/')
def serve_html():
    return send_from_directory('', 'index.html')  # Serve the HTML file

def ai_response(text):
    """Get a response from ChatGPT and speak it."""
    messages.append({"role": "user", "content": text})
    response = Create_Jarvis(messages)
    responses.append(response)
    SpeakText(response)

def run_flask():
    app.run(host='0.0.0.0', port=8000)  # Run Flask app

def start_netflix():
    """Open Netflix application."""
    SpeakText("Opening Netflix for you sir")
    os.system('start Netflix:')

def start_google():
    """Open Google Chrome."""
    SpeakText("Opening Google for you sir")
    os.startfile("C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe")

def start_edge():
    """Open Microsoft Edge."""
    SpeakText("Opening Microsoft Edge for you sir")
    os.startfile("C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe")

def start_spotify():
    """Open Spotify application."""
    SpeakText("Opening Spotify for you sir")
    os.system('spotify')

def playMusic(music):
    """Play specified music on Spotify."""
    try:
        os.system('spotify')
        
        music = music.lower()
        if " on spotify" in music:
            music, _ = music.split("on spotify", 1)
            music = music.strip()
        if "play " in music:
            _, music = music.split("play", 1)
            music = music.strip()
        response = "Playing " + music + " on Spotify"
        SpeakText(response)
        time.sleep(1.5)
        if "playlist" in music:
            music = music.replace("playlist", "").strip()
            play_playlist(music)
        else:
            play_song(music)
        return(response)
    except Exception as e:
        print(f"Error playing music: {e}")
        return

def get_time():
    """Get and speak the current time."""
    strTime = datetime.datetime.now().strftime("%H:%M:%S")
    SpeakText("Sir, the time is " + strTime)

def play_youtube(text):
    """Play a video on YouTube based on the provided text."""
    try:
        if " on youtube" in text:
            text, _ = text.split("on youtube", 1)
            text = text.strip()
        if "play " in text:
            _, text = text.split("play", 1)
            text = text.strip()
        time.sleep(0.2) # Delay audio to help with timing
        pywhatkit.playonyt(text)
        return ("Playing " + text + " on YouTube")
    except Exception as e:
        print(f"Error playing YouTube video: {e}")
        return("Sorry sir, there was an error opening youtube")
    

def timer(text):
    """Set a timer based on the provided text and play a song when the timer ends."""
    timer_duration = 0
    time_units = {"hour": 3600, "minute": 60, "second": 1}
    matches = re.findall(r'(\d+)\s*(hour|minute|second)', text) # Extract number and unit pairs from the text
    for match in matches:
        number, unit = match
        timer_duration += int(number) * time_units[unit]

    SpeakText("Setting timer for you sir")
    
    while timer_duration > 0:
        time.sleep(1)
        timer_duration -= 1
    SpeakText("Time is up sir...")
    playMusic("Low Rider")

def volumeUp():
    """Increase the volume on the computer"""
    pyautogui.press("volumeup", 10)

def volumeDown():
    """"Decrease the volume on the computer"""
    pyautogui.press("volumedown", 10)




morningResponse = ''
alarm = True

def schedule_wake_up(hour, minute):
    alarm = True
    print(f"Scheduling wake-up for {hour:02d}:{minute:02d}.")
    
    while alarm == True:
        current_time = datetime.datetime.now()
        print(f"Current time: {current_time.hour:02d}:{current_time.minute:02d}")  # Debugging current time
        
        # Check if the current hour and minute match the scheduled time
        if current_time.hour == hour and current_time.minute == minute:
            morningResponse = (f"Good morning! It's {hour:02d}:{minute:02d}! ")
            alarm = False
            SpeakText(morningResponse)  # Speak the wake-up message
            playMusic("Lovely Day")
        
        time.sleep(5)  # Check every 5 seconds
    
    

def handle_schedule_command(text):
    print(f"Received command: {text}")  # Debugging input

    match = re.search(r'(?:wake me up at|set an alarm for)\s*(\d{1,2})(?::(\d{2}))?\s*(am|pm)?', text, re.IGNORECASE)
    
    if match:
        hour = int(match.group(1))
        minute = int(match.group(2)) if match.group(2) else 0
        

        # Convert to 24-hour format
        if 'p.m.' in text and hour < 12:
            hour+=12
        elif 'a.m.' in text and hour == 12:
            hour = 0

        print(f"Parsed time: {hour:02d}:{minute:02d}")  # Debugging parsed time

        # Start the scheduling thread
        threading.Thread(target=schedule_wake_up, args=(hour, minute), daemon=True).start()
        if 'p.m.' in text and hour > 12:
            hour = hour-12
        response = f"Scheduled wake-up at {hour:02d}:{minute:02d}. "
        responses.append(response)
        SpeakText(response)
    else:
        print("No match found.")  # Debugging if no match is found

def scheduleText(hour, minute):
    alarm = True
    print(f"Sending message at {hour:02d}:{minute:02d}.")
    
    while alarm == True:
        current_time = datetime.datetime.now()
        print(f"Current time: {current_time.hour:02d}:{current_time.minute:02d}")  # Debugging current time
        
        # Check if the current hour and minute match the scheduled time
        if current_time.hour == hour and current_time.minute == minute:
            sendGfText()
            #messages.append({"role": "user", "content": "Alert me that you just sent my message to Sophie"}) 
            SpeakText("Message sent for you")
            alarm = False
        
        time.sleep(5)  # Check every 5 seconds

def handle_schedule_text(text):
    print(f"Received command: {text}")  # Debugging input

    match = re.search(r'(?:send a text to sophie at|message sophie at|message to sophie at|text sophie at)\s*(\d{1,2})(?::(\d{2}))?\s*(am|pm)?', text, re.IGNORECASE)
    
    if match:
        hour = int(match.group(1))
        minute = int(match.group(2)) if match.group(2) else 0
        

        # Convert to 24-hour format
        if 'p.m.' in text and hour < 12:
            hour+=12
        elif 'a.m.' in text and hour == 12:
            hour = 0

        print(f"Parsed time: {hour:02d}:{minute:02d}")  # Debugging parsed time

        # Start the scheduling thread
        threading.Thread(target=scheduleText, args=(hour, minute), daemon=True).start()
        if 'p.m.' in text and hour > 12:
            hour = hour-12
        response = f"Scheduled message at {hour:02d}:{minute:02d}. "
        responses.append(response)
        SpeakText(response)
    else:
        print("No match found.")  # Debugging if no match is found

if __name__ == "__main__":
    handle_schedule_command("jarvis wake me up at 11:22 p.m.")
    while(True):
        time.sleep(1)