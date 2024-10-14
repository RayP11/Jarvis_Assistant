
from tkinter import *
from PIL import Image, ImageTk, ImageSequence
import tkinter as tk
import os

def createUI():
    """
    Create a Tkinter window to display a GIF animation.

    This function initializes a Tkinter window, loads a GIF file, and displays it in an animation loop.
    The GIF frames are updated every 25 milliseconds to create the animation effect.

    Raises:
        Exception: If there is an error loading the GIF file.
    """
    root = Tk()
    root.configure(bg="black")
    root.title("JARVIS")
    root.resizable(width=False, height=False)

    # Define the relative path
    script_dir = os.path.dirname(__file__)  # Directory of the current script
    image_path = os.path.join(script_dir, "jarvis_gif.gif")  # Relative path to the GIF file

    try:
        gif = Image.open(image_path)
        frames = [ImageTk.PhotoImage(img) for img in ImageSequence.Iterator(gif)]
    except FileNotFoundError:
        print(f"GIF file not found at path: {image_path}")
        return
    except Exception as e:
        print(f"Error loading GIF: {e}")
        return

    label = Label(root)
    label.pack()

    idx = 0

    def update_image():
        """
        Update the displayed GIF frame.
        
        This function is called recursively to update the GIF frame shown in the Tkinter window.
        """
        nonlocal idx
        idx = (idx + 1) % len(frames)
        label.configure(image=frames[idx])
        label.image = frames[idx]
        root.after(40, update_image)  # Schedule the next frame update

    update_image()
    root.mainloop()

def loading_screen():
    """
    Create a Tkinter window displaying a loading message.

    This function initializes a Tkinter window with a centered loading message. The window closes automatically
    after 6 seconds.

    Raises:
        Exception: If there is an error creating or displaying the loading screen.
    """
    try:
        root = tk.Tk()
        root.configure(bg='black')
        root.title("JARVIS")

        width = 800
        height = 400
        root.geometry(f"{width}x{height}")

        # Center the window on the screen
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        
        root.geometry(f"+{x}+{y}")
        root.resizable(width=False, height=False)

        # Create and display the loading message
        loading_label = tk.Label(root, text="Loading image for you sir...", fg='light blue', bg='black', font=('impact', 20))
        loading_label.pack(pady=50)

        # Close the window after 6 seconds
        root.after(6000, root.destroy)
        root.mainloop()
    except Exception as e:
        print(f"Error displaying loading screen: {e}")

def sleep_screen():
    """
    Create a fullscreen Tkinter window that can be closed by pressing 'q'.

    This function initializes a fullscreen Tkinter window with a black background. The window can be closed by
    pressing the 'q' key.

    Raises:
        Exception: If there is an error creating or displaying the fullscreen window.
    """
    try:
        root = tk.Tk()

        # Get screen dimensions
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()

        # Set the window size to full screen
        root.geometry(f"{screen_width}x{screen_height}+1000+1000")
        root.attributes('-fullscreen', True)
        root.configure(bg='black')
        root.overrideredirect(True)  # Hide the title bar

        def close(event):
            """
            Close the Tkinter window.

            Args:
                event (tk.Event): The event that triggered the function.
            """
            root.destroy()

        # Bind the 'q' key to the close function
        root.bind('<q>', close)
        root.mainloop()
    except Exception as e:
        print(f"Error displaying sleep screen: {e}")



    