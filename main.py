import tkinter as tk
from tkinter import messagebox
from constants import WINDOW_SIZE
from interface import setup_interface
import os
from pathlib import Path
from dotenv import load_dotenv

# Check if .env file exists, create one with defaults if not
def ensure_env_file_exists():
    env_path = '.env'
    if not os.path.exists(env_path):
        print("No .env file found. Creating one with default values...")
        with open(env_path, 'w') as f:
            f.write("OPENAI_API_KEY=\n")
            f.write("OPENAI_MODEL=gpt-4o-mini\n")
            f.write("MAX_TOKENS=5000\n")
        print(".env file created. Please set your OpenAI API key.")
        return True  # Indicates a new file was created
    return False  # File already existed

def check_api_key():
    """Check if API key is set and show a warning if not"""
    load_dotenv()  # Reload env variables to ensure we have the latest
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key.strip() == "":
        messagebox.showwarning(
            "API Key Missing",
            "No OpenAI API key found. AI features will be disabled.\n\n"
            "To enable AI features:\n"
            "1. Get an API key from https://platform.openai.com/api-keys\n"
            "2. Add your key to the .env file\n"
            "3. Restart the application"
        )

# Ensure .env file exists before importing modules that might use it
new_file_created = ensure_env_file_exists()

root = tk.Tk(screenName='Student Assistant', baseName='Student Assistant', className='Tk', useTk=1)
root.title("Student Assistant")
root.geometry("1200x800")

# Create a StringVar to track the current page
current_page = tk.StringVar(value='notes')

setup_interface(root, current_page)

# Check API key after GUI is initialized to show the warning message
root.after(1000, check_api_key)  # Check after 1 second to allow GUI to load first

root.mainloop()