import tkinter as tk
from constants import WINDOW_SIZE, PAGES
from pages import NotesPage, FeedbackPage, StarterPage

def set_current_page(page, current_page_var, content_frame):
    if page in PAGES:
        current_page_var.set(page)
    else:
        raise ValueError(f"Invalid page: {page}")
    
    # Update button states
    if current_page_var.get() == 'notes':
        notes_button.config(relief='sunken', borderwidth=3, state='disabled')
        feedback_button.config(relief='ridge', borderwidth=2, state='normal')
        starter_button.config(relief='ridge', borderwidth=2, state='normal')
        show_page(NotesPage, content_frame)
    elif current_page_var.get() == 'feedback':
        notes_button.config(relief='ridge', borderwidth=2, state='normal')
        feedback_button.config(relief='sunken', borderwidth=3, state='disabled')
        starter_button.config(relief='ridge', borderwidth=2, state='normal')
        show_page(FeedbackPage, content_frame)
    elif current_page_var.get() == 'starter':
        notes_button.config(relief='ridge', borderwidth=2, state='normal')
        feedback_button.config(relief='ridge', borderwidth=2, state='normal')
        starter_button.config(relief='sunken', borderwidth=3, state='disabled')
        show_page(StarterPage, content_frame)

def show_page(page_class, content_frame):
    # Clear the content frame
    for widget in content_frame.winfo_children():
        widget.destroy()
    
    # Create and show the new page
    page = page_class(content_frame)
    page.pack(fill=tk.BOTH, expand=True)

def setup_interface(root, current_page_var):
    # Create a frame to hold the buttons at the top
    button_frame = tk.Frame(root, relief='solid', borderwidth=1)
    button_frame.pack(fill='x', side='top')

    global notes_button, feedback_button, starter_button, content_frame
    
    notes_button = tk.Button(button_frame, text='Note Tool', width=20, relief='sunken', borderwidth=3, state='disabled',
                          command=lambda: set_current_page('notes', current_page_var, content_frame))
    feedback_button = tk.Button(button_frame, text='Feedback Tool', width=20, relief='ridge', borderwidth=2, state='normal',
                          command=lambda: set_current_page('feedback', current_page_var, content_frame))
    starter_button = tk.Button(button_frame, text='Starter Tool', width=20, relief='ridge', borderwidth=2, state='normal',
                               command=lambda: set_current_page('starter', current_page_var, content_frame))

    # Use grid geometry manager for better control
    notes_button.grid(row=0, column=0, padx=0, pady=0, sticky='ew')
    feedback_button.grid(row=0, column=1, padx=0, pady=0, sticky='ew')
    starter_button.grid(row=0, column=2, padx=0, pady=0, sticky='ew')

    # Configure grid columns to be equal width
    button_frame.grid_columnconfigure(0, weight=1)
    button_frame.grid_columnconfigure(1, weight=1)
    button_frame.grid_columnconfigure(2, weight=1)

    # Create a main content frame below the navigation
    content_frame = tk.Frame(root)
    content_frame.pack(expand=True, fill='both', padx=0, pady=0)

    # Show the initial page (Notes)
    show_page(NotesPage, content_frame)
