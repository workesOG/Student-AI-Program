import tkinter as tk
from constants import WINDOW_SIZE
from interface import setup_interface

root = tk.Tk(screenName='Student Assistant', baseName='Student Assistant', className='Tk', useTk=1)
root.title("Student Assistant")
root.geometry("1200x800")

# Create a StringVar to track the current page
current_page = tk.StringVar(value='notes')

setup_interface(root, current_page)
root.mainloop()