from openai import OpenAI
from dotenv import load_dotenv
import os
import pygame
import io
import requests
import pyautogui
import tempfile
import base64
import cv2
import time



load_dotenv()

# Initialize OpenAI client once
openai_api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=openai_api_key)

# Context for Jarvis
messages = [{"role": "system", "content": "My name is Ray, your creator. You are Jarvis, my personal ai voice assistant. You will mimic JARVIS from Iron Man and address me as sir. Try to keep your answers brief but to the point and helpful"}]

def Create_Jarvis(messages, model="gpt-4o-mini"):
    """
    Create a response from Jarvis using OpenAI's GPT model.

    Args:
        messages (list): A list of messages to provide context for the completion.
        model (str): The model to use for generating the response (default is "gpt-4o-mini").

    Returns:
        str: The generated response from the model.
    """
    completion = client.chat.completions.create(
        model=model,
        messages=messages,
        max_tokens=500,
        n=1,
        temperature=0.9
    )
    message = completion.choices[0].message.content
    messages.append(completion.choices[0].message)
    return message

def SpeakText(text):
    """
    Convert text to speech using OpenAI's text-to-speech model, play it, then display response.

    Args:
        text (str): The text to be converted to speech.
    """
    response = client.audio.speech.create(
        model="tts-1",
        voice="onyx",
        input=text
    )
    audio_data = io.BytesIO(response.content)
    
    pygame.init()
    pygame.mixer.init()
    pygame.mixer.music.load(audio_data, "mp3")
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)
    
    

def show_image(image):
    """
    Display an image using the default image viewer.

    Args:
        image (PIL.Image.Image): The image to be displayed.
    """
    try:
        image.show()
    except Exception as e:
        print(f"Error displaying image: {e}")

def genImage(text):
    """
    Generate an image from text using OpenAI's DALL-E model and return the image URL.

    Args:
        text (str): The text prompt to generate the image.
    """
    try:
        response = client.images.generate(  
            model="dall-e-3",
            prompt=text,
            size="1024x1024",
            quality="standard",
            n=1
        )
        image_url = response.data[0].url
        
        # Return the image URL
        print(image_url)
        return image_url
    except Exception as e:
        print(f"Error generating image: {e}")
        return None
    except requests.RequestException as e:
        print(f"Error downloading image: {e}")
    except Exception as e:
        print(f"Error generating or displaying image: {e}")

# Function to encode the image
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def capture_and_analyze(text):
    # Capture the screen
    screenshot = pyautogui.screenshot()

    # Save the screenshot to a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
        screenshot.save(temp_file.name)
        print(f"Screenshot saved to {temp_file.name}")

        # Getting the base64 string
        base64_image = encode_image(temp_file.name)

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {openai_api_key}"
        }

        payload = {
            "model": "gpt-4o-mini",  # Adjust as necessary
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "You are Jarvis. " + text},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": 4000
        }

        # Sending the request to OpenAI API
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

        # Process the response
        if response.status_code == 200:
            response_data = response.json()
            # extract relevant information from the response
            completion_text = response_data['choices'][0]['message']['content']
        else:
            print(f"Error: {response.status_code}, {response.text}")
            return None
        
        return(completion_text)
        

    # Delete the temporary file
    os.remove(temp_file.name)
    print(f"Deleted temporary file: {temp_file.name}")

def resize_image(frame, width=100, height=150):
    """
    Resizes the image to the specified width and height.
    """
    resized_frame = cv2.resize(frame, (width, height))
    return resized_frame

def camera_response(text):
    """
    Opens the camera, takes a screenshot, and provides an AI response based on the image and user query.
    """
    # Initialize the camera
    camera = cv2.VideoCapture(0)
    if not camera.isOpened():
        print("Error: Could not access the camera.")
        return None

    # Capture the image
    ret, frame = camera.read()
    camera.release()
    if not ret:
        print("Error: Failed to capture image.")
        return None

    # Resize the image to a smaller size to reduce the payload
    frame = resize_image(frame)

    # Save the image to a temporary file
    temp_file_name = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
            temp_file_name = temp_file.name
            # Write the resized image using OpenCV after the file is closed
            cv2.imwrite(temp_file_name, frame)
            print(f"Image saved to {temp_file_name}")
            time.sleep(0.1)
            cv2.destroyAllWindows()

            # Encode the resized image
            base64_image = encode_image(temp_file_name)
    finally:
        # Ensure the temporary file is deleted
        if temp_file_name and os.path.exists(temp_file_name):
            os.remove(temp_file_name)
            print(f"Deleted temporary file: {temp_file_name}")

    # Prepare API request
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {openai_api_key}"
    }

    payload = {
            "model": "gpt-4o-mini",  # Adjust as necessary
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "You are Jarvis, I am the person in these images, don't worry about the person. " + text},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": 4000
        }

    # Send the request
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

    # Process the response
    if response.status_code == 200:
        response_data = response.json()
        completion_text = response_data['choices'][0]['message']['content']
        return completion_text
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return None


    

