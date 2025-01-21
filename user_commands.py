# All user commands for JARVIS to open applications and execute various actions

# Commands to open Google Chrome
google_open = [
    "open google", "open chrome", "start google", "start chrome"
]

# Commands to open Microsoft Edge
edge_open = [
    "open edge", "open microsoft edge", "open microsoft", "start edge", "start microsoft edge", "start microsoft"
]

# Commands to open Netflix
netflix_open = [
    "open netflix", "start netflix", "play netflix"
]

# Commands to get the weather for today
weather_forecast = [
    "weather", "forecast"
]

# Commands to open Spotify
spotify_open = [
    "open spotify", "start spotify", "play spotify", "run spotify"
]

# Command to play music on Spotify
play_music = [
    "on spotify"
]

# Commands for time
what_time = [
    "what's the time", "what time is it", "tell me the time", "what's the current time"
]

# Commands to play a video on YouTube
play_video = [
    "on youtube"
]

# Commands for setting a timer
timer_command = [
    "set a timer for", "make a timer for", "create a timer for"
]

# Commands to play a random song
random_song = [
    "drop my needle", "drop the needle", "play something for me", "play me some music", "jarvis music", "music please", "give me some music", "play me something", "play music", "give me music", "play some tunes", "tunes please", "music please", "next song"
]

# Commands to turn volume up
volume_increase = [
    "volume up", "increase volume"
]

# Commands to turn the volume down
volume_decrease = [
    "volume down", "decrease volume"
]

# Commands to generate an image
generate_image = [
    "jarvis generate", "generate me", "make me an image", "draw a picture", "make an image", 
    "draw an image", "generate an image", "generate me an image", "draw me an image"
]

#commands to send text message to self
send_message = [
    "send me a reminder", "send me a message", "message me", "me a text", "send a text", "remind me to"
]

# Commands to stop running JARVIS
stop_commands = [
    "goodbye", "bye", "jarvis stop"
]

# Commands to put JARVIS into sleep mode
j_sleep = [
    "that's all", "that is all", "talk to you soon"
]

#commands to prompt jarvis to set a wake up alarm
wake_up = [
    "wake me up at", "set an alarm for"
]

#commands to send a text message to Sophie
send_soph = [
    "send a text to sophie at", "message sophie at", "message to sophie at", "text sophie at"
]


def find_match(command_list, text):
    """
    Finds if any of the commands in the list match the given text.

    Args:
        command_list (list): A list of command phrases to check against.
        text (str): The text to be checked for matching commands.

    Returns:
        bool: True if a match is found, False otherwise.
    """
    return any(item in text.lower() for item in command_list)
 