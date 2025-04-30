import tkinter as tk
from tkinter import ttk, simpledialog, filedialog, messagebox
import ai_handler
import threading
import os
import json
from pathlib import Path
import subjects  # Import the subjects module
import assignment_types  # Import the assignment types module

# Constants
NOTES_DIR = os.path.join(str(Path.home()), "Documents", "SAII", "Notes")

# Ensure the notes directory exists
os.makedirs(NOTES_DIR, exist_ok=True)

class APICheckWindow(tk.Toplevel):
    def __init__(self, parent, on_complete):
        super().__init__(parent)
        self.parent = parent
        self.on_complete = on_complete
        
        # Configure the window
        self.title("Checking API Connection")
        self.geometry("300x100")
        self.resizable(False, False)
        
        # Make window modal to block interaction with parent
        self.transient(parent)
        self.grab_set()
        
        # Center on parent
        parent_x = parent.winfo_rootx()
        parent_y = parent.winfo_rooty()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
        
        x = parent_x + (parent_width // 2) - (300 // 2)
        y = parent_y + (parent_height // 2) - (100 // 2)
        
        self.geometry(f"+{x}+{y}")
        
        # Create a label
        self.label = tk.Label(self, text="Checking OpenAI API connection...", font=("Helvetica", 10))
        self.label.pack(pady=15)
        
        # Create a progress bar
        self.progress = ttk.Progressbar(self, orient='horizontal', length=200, mode='indeterminate')
        self.progress.pack(pady=10)
        self.progress.start(10)
        
        # Start the check in a separate thread to avoid UI freezing
        self.check_thread = threading.Thread(target=self.check_api_connection)
        self.check_thread.daemon = True
        self.check_thread.start()
    
    def check_api_connection(self):
        # Test the API connection
        api_connected = ai_handler.test_api_connection()
        
        # Schedule the callback on the main thread
        self.after(100, lambda: self.complete_check(api_connected))
    
    def complete_check(self, api_connected):
        self.progress.stop()
        self.destroy()
        self.on_complete(api_connected)

class AIPromptWindow(tk.Toplevel):
    def __init__(self, parent, callback):
        super().__init__(parent)
        self.parent = parent
        self.callback = callback
        
        # Configure the window
        self.title("AI Note Generator")
        self.geometry("700x500")
        self.minsize(500, 400)
        
        # Make window modal-like without blocking (user can still interact with main window)
        self.transient(parent)
        self.grab_set()
        
        self.setup_ui()
        
    def setup_ui(self):
        # Description header
        description_frame = tk.Frame(self, pady=5)
        description_frame.pack(fill='x', padx=20, pady=(10, 0))
        
        description_text = "The AI will generate well-structured notes based on your topic and any context you provide."
        description_label = tk.Label(description_frame, text=description_text, font=("Helvetica", 10), anchor='w', justify='left')
        description_label.pack(fill='x')
        
        # Main goal / Topic
        topic_frame = tk.Frame(self, pady=10)
        topic_frame.pack(fill='x', padx=20, pady=5)
        
        topic_label = tk.Label(topic_frame, text="Main Goal / Topic:", font=("Helvetica", 12, "bold"))
        topic_label.pack(anchor='w')
        
        self.topic_entry = tk.Entry(topic_frame, font=("Helvetica", 11))
        self.topic_entry.pack(fill='x', pady=5)
        
        # Context
        context_frame = tk.Frame(self, pady=10)
        context_frame.pack(fill='both', expand=True, padx=20, pady=5)
        
        context_label = tk.Label(context_frame, text="Context:", font=("Helvetica", 12, "bold"))
        context_label.pack(anchor='w')
        
        context_hint = tk.Label(context_frame, text="Add any information, questions, or details that will help generate better notes", font=("Helvetica", 9), fg="gray")
        context_hint.pack(anchor='w', pady=(0, 5))
        
        self.context_text = tk.Text(context_frame, wrap='word', height=10, font=("Helvetica", 11))
        self.context_text.pack(fill='both', expand=True, pady=5)
        
        # Submit button
        button_frame = tk.Frame(self)
        button_frame.pack(fill='x', padx=20, pady=15)
        
        cancel_button = ttk.Button(button_frame, text="Cancel", command=self.destroy)
        cancel_button.pack(side='right', padx=5)
        
        submit_button = ttk.Button(button_frame, text="Generate Notes", command=self.submit_prompt)
        submit_button.pack(side='right', padx=5)
    
    def submit_prompt(self):
        topic = self.topic_entry.get()
        context = self.context_text.get('1.0', 'end-1c')
        
        if not topic:
            messagebox.showwarning("Missing Information", "Please enter a topic or main goal.")
            return
        
        # Call the callback with the prompt information
        self.callback(topic, context)
        self.destroy()

class NotesPage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.notes = []  # List to store notes
        self.current_note = None
        self.setup_ui()
        self.load_notes()

    def setup_ui(self):
        # Create the left frame (side menu) with fixed width
        self.side_menu = tk.Frame(self, relief='solid', borderwidth=1)
        self.side_menu.pack(fill='y', side='left')
        
        title_label = tk.Label(self.side_menu, text="Notes", font=("Helvetica", 16, "bold"), height=1)
        title_label.grid(row=0, column=0, padx=0, pady=10, sticky='ew')
        
        new_button = tk.Button(self.side_menu, text='New Note', width=25, relief='ridge', borderwidth=2, 
                              command=self.create_new_note)
        new_button.grid(row=1, column=0, padx=0, pady=0, sticky='ew')
        
        # Frame to hold the list of notes
        self.notes_list_frame = tk.Frame(self.side_menu)
        self.notes_list_frame.grid(row=2, column=0, padx=0, pady=0, sticky='nsew')
        
        # Configure side menu column weights
        self.side_menu.grid_columnconfigure(0, weight=1)
        self.side_menu.grid_rowconfigure(2, weight=1)  # Make the notes list expandable
        
        # Create the right frame (workspace) that fills all remaining space
        self.workspace = tk.Frame(self, relief='solid', borderwidth=1)
        self.workspace.pack(fill='both', expand=True, side='right')
        
        # Create a default empty workspace
        self.show_empty_workspace()
    
    def load_notes(self):
        """Load notes from the SAII/Notes directory"""
        try:
            # Clear existing notes
            self.notes = []
            
            # Clear notes list in sidebar
            for widget in self.notes_list_frame.winfo_children():
                widget.destroy()
            
            # Get all .json files in the notes directory
            note_files = [f for f in os.listdir(NOTES_DIR) if f.endswith('.json')]
            
            # Load each note
            for i, filename in enumerate(note_files):
                file_path = os.path.join(NOTES_DIR, filename)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        note_data = json.load(f)
                        
                    # Ensure the note has the required fields
                    if 'title' not in note_data or 'content' not in note_data:
                        continue
                    
                    # Add ID if not present
                    if 'id' not in note_data:
                        note_data['id'] = i
                    
                    # Add the note to our list
                    self.notes.append(note_data)
                    
                    # Add note to the sidebar
                    note_button = tk.Button(self.notes_list_frame, text=note_data['title'], relief='flat', anchor='w',
                                          command=lambda id=note_data['id']: self.open_note(id))
                    note_button.pack(fill='x', padx=0, pady=0)
                    
                except Exception as e:
                    print(f"Error loading note {filename}: {e}")
            
            print(f"Loaded {len(self.notes)} notes")
            
        except Exception as e:
            print(f"Error loading notes: {e}")
    
    def save_note_to_disk(self, note):
        """Save a note to disk"""
        if not note:
            return
            
        # Create a safe filename based on the note ID
        filename = f"note_{note['id']}.json"
        file_path = os.path.join(NOTES_DIR, filename)
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(note, f, ensure_ascii=False, indent=2)
            print(f"Saved note to {file_path}")
        except Exception as e:
            print(f"Error saving note: {e}")
            messagebox.showerror("Save Error", f"Could not save note: {e}")
    
    def delete_note_from_disk(self, note_id):
        """Delete a note file from disk"""
        filename = f"note_{note_id}.json"
        file_path = os.path.join(NOTES_DIR, filename)
        
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"Deleted note file: {file_path}")
        except Exception as e:
            print(f"Error deleting note file: {e}")
            messagebox.showerror("Delete Error", f"Could not delete note file: {e}")
    
    def show_empty_workspace(self):
        # Clear workspace
        for widget in self.workspace.winfo_children():
            widget.destroy()
            
        # Show a message
        empty_label = tk.Label(self.workspace, text="No note selected or created yet.\nClick 'New Note' to get started.", 
                             font=("Helvetica", 12))
        empty_label.place(relx=0.5, rely=0.5, anchor='center')
    
    def create_new_note(self):
        # Prompt user for note title
        title = simpledialog.askstring("New Note", "Enter note title:")
        if title:
            # Create a new note
            note_id = max([note['id'] for note in self.notes], default=-1) + 1
            new_note = {"id": note_id, "title": title, "content": ""}
            self.notes.append(new_note)
            
            # Add note to the sidebar
            note_button = tk.Button(self.notes_list_frame, text=title, relief='flat', anchor='w',
                                  command=lambda id=note_id: self.open_note(id))
            note_button.pack(fill='x', padx=0, pady=0)
            
            # Save to disk
            self.save_note_to_disk(new_note)
            
            # Open the new note
            self.open_note(note_id)
    
    def open_note(self, note_id):
        # Get the note data
        self.current_note = next((note for note in self.notes if note["id"] == note_id), None)
        if not self.current_note:
            return
        
        # Clear workspace
        for widget in self.workspace.winfo_children():
            widget.destroy()
        
        # Create the note editing interface
        # Title bar
        title_frame = tk.Frame(self.workspace)
        title_frame.pack(fill='x', padx=10, pady=5)
        
        title_label = tk.Label(title_frame, text=self.current_note["title"], font=("Helvetica", 14, "bold"))
        title_label.pack(side='left')
        
        # Add rename and delete buttons in the title bar
        button_group = tk.Frame(title_frame)
        button_group.pack(side='right')
        
        rename_button = tk.Button(button_group, text="Rename", command=self.rename_current_note)
        rename_button.pack(side='left', padx=5)
        
        delete_button = tk.Button(button_group, text="Delete", command=self.delete_current_note)
        delete_button.pack(side='left', padx=5)
        
        # Text editing area
        self.text_area = tk.Text(self.workspace, wrap='word')
        self.text_area.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Set current content
        self.text_area.insert('1.0', self.current_note["content"])
        
        # Button bar
        button_frame = tk.Frame(self.workspace)
        button_frame.pack(fill='x', padx=10, pady=5)
        
        save_button = tk.Button(button_frame, text="Save", command=self.save_current_note)
        save_button.pack(side='left', padx=5)
        
        ai_button = tk.Button(button_frame, text="Generate Notes with AI", command=self.ask_ai)
        ai_button.pack(side='left', padx=5)
    
    def rename_current_note(self):
        """Rename the current note"""
        if not self.current_note:
            return
            
        # Prompt for new title
        new_title = simpledialog.askstring("Rename Note", "Enter new title:", initialvalue=self.current_note["title"])
        if not new_title:
            return  # User cancelled or entered empty string
            
        # Update note title
        old_title = self.current_note["title"]
        self.current_note["title"] = new_title
        
        # Update UI
        for widget in self.notes_list_frame.winfo_children():
            if isinstance(widget, tk.Button) and widget.cget("text") == old_title:
                widget.config(text=new_title)
                break
        
        # Update title in the workspace
        for widget in self.workspace.winfo_children()[0].winfo_children():
            if isinstance(widget, tk.Label):
                widget.config(text=new_title)
                break
        
        # Save the note to disk
        self.save_current_note()
    
    def delete_current_note(self):
        """Delete the current note"""
        if not self.current_note:
            return
            
        # Confirm deletion
        confirm = messagebox.askyesno("Delete Note", f"Are you sure you want to delete '{self.current_note['title']}'?")
        if not confirm:
            return
            
        # Remove the note from the list
        note_id = self.current_note["id"]
        note_title = self.current_note["title"]
        self.notes = [note for note in self.notes if note["id"] != note_id]
        
        # Remove the note from disk
        self.delete_note_from_disk(note_id)
        
        # Remove the note button from sidebar
        for widget in self.notes_list_frame.winfo_children():
            if isinstance(widget, tk.Button) and widget.cget("text") == note_title:
                widget.destroy()
                break
        
        # Show empty workspace
        self.current_note = None
        self.show_empty_workspace()
    
    def save_current_note(self):
        if self.current_note:
            # Update note content
            self.current_note["content"] = self.text_area.get('1.0', 'end-1c')
            
            # Save to disk
            self.save_note_to_disk(self.current_note)
            
            print(f"Saved note: {self.current_note['title']}")
    
    def ask_ai(self):
        """Check for API connection and then open the AI prompt window"""
        if not self.current_note:
            return
        
        # Create a waiting window to check the API connection
        APICheckWindow(self, self.on_api_check_complete)
    
    def on_api_check_complete(self, api_connected):
        """Callback for when the API connection check is complete"""
        if not api_connected:
            messagebox.showerror(
                "API Connection Error", 
                "Could not connect to OpenAI API. Please check your API key in the .env file and ensure you have an internet connection."
            )
            self.text_area.insert('end', "\n[Error: Could not connect to OpenAI API. Please check your API key.]\n")
            self.text_area.see('end')
            return
        
        # If the connection was successful, open the AI prompt window
        AIPromptWindow(self, self.process_ai_prompt)
    
    def process_ai_prompt(self, topic, context):
        """Process the AI prompt and update the note with the response"""
        if not self.current_note:
            return
            
        # Store the current content and cursor position
        cursor_position = self.text_area.index(tk.INSERT)
        current_content = self.text_area.get('1.0', 'end-1c')
        
        # Add a marker for where the AI response will be inserted with proper spacing
        if current_content and not current_content.endswith('\n\n'):
            if current_content.endswith('\n'):
                self.text_area.insert('end', '\n')  # Add one more newline for spacing
            else:
                self.text_area.insert('end', '\n\n')  # Add two newlines for spacing
        
        # Add the processing message
        self.text_area.insert('end', "[Processing AI request...]\n")
        response_start_mark = self.text_area.index('end-1l linestart')
        self.text_area.see('end')
        self.update_idletasks()  # Update the UI to show the processing message
        
        # Create a progress indicator
        progress_frame = tk.Frame(self.text_area)
        progress = ttk.Progressbar(progress_frame, orient="horizontal", length=200, mode="indeterminate")
        progress.pack(pady=5)
        
        # Create a window for the progress bar
        progress_window = self.text_area.window_create('end', window=progress_frame)
        progress.start(10)
        self.update_idletasks()
        
        # Create a function to process the AI request in the background
        def process_in_background():
            try:
                # Call the AI handler to get a response with the note_taker role
                response = ai_handler.generate_response(
                    topic=topic, 
                    context=context,
                    role="note_taker"  # Use the note_taker role for the Notes page
                )
                
                # Schedule the UI update on the main thread
                self.after(0, lambda: self.update_with_response(response, progress_frame, response_start_mark))
                
            except Exception as e:
                error_msg = f"An error occurred: {str(e)}"
                self.after(0, lambda: self.update_with_error(error_msg, progress_frame, response_start_mark))
        
        # Start the background thread
        thread = threading.Thread(target=process_in_background)
        thread.daemon = True
        thread.start()
    
    def update_with_response(self, response, progress_frame, response_start_mark):
        """Update the note with the AI response after processing"""
        # Remove the progress indicator
        progress_frame.destroy()
        
        # Replace the processing message with the AI response
        # Clean up any extra whitespace at the start or end of the response
        response = response.strip()
        
        # Replace the processing message with the AI response
        self.text_area.delete(response_start_mark, 'end-1c')
        self.text_area.insert(response_start_mark, response + "\n\n")  # Add newlines after response
        self.text_area.see(response_start_mark)  # Scroll to show the response
        
        # Save the note with the new content
        self.save_current_note()

    def update_with_error(self, error_msg, progress_frame, response_start_mark):
        """Update the note with an error message"""
        # Remove the progress indicator
        progress_frame.destroy()
        
        # Replace the processing message with the error
        self.text_area.delete(response_start_mark, 'end-1c')
        self.text_area.insert(response_start_mark, f"[Error: {error_msg}]\n\n")  # Add newlines after error
        self.text_area.see(response_start_mark)
        
        # Show an error dialog
        messagebox.showerror("Error", error_msg)

class FeedbackPage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.setup_ui()
        self.load_subjects()
        self.load_assignment_types()

    def load_subjects(self):
        """Load subjects into the dropdown"""
        subject_names = subjects.get_subject_names()
        self.subject_dropdown['values'] = subject_names
        if subject_names:
            self.subject_dropdown.current(0)

    def load_assignment_types(self):
        """Load assignment types into the dropdown"""
        type_names = assignment_types.get_assignment_type_names()
        self.assignment_type_dropdown['values'] = type_names
        if type_names:
            self.assignment_type_dropdown.current(0)

    def setup_ui(self):
        title_label = tk.Label(self, text="Assignment Feedback", font=("Helvetica", 16, "bold"))
        title_label.pack(pady=10)
        
        description = tk.Label(self, text="Use AI to get feedback on your assignments and improve your work.", 
                             font=("Helvetica", 10))
        description.pack(pady=5)
        
        # Create main content area
        content_frame = tk.Frame(self)
        content_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Subject selection section
        subject_frame = tk.Frame(content_frame)
        subject_frame.pack(fill='x', pady=2)
        
        subject_label = tk.Label(subject_frame, text="Subject:", font=("Helvetica", 11, "bold"))
        subject_label.pack(side='left', padx=(0, 10))
        
        self.subject_dropdown = ttk.Combobox(subject_frame)
        self.subject_dropdown.pack(side='left', fill='x', expand=True)
        
        manage_subjects_button = ttk.Button(subject_frame, text="Manage Subjects", command=self.manage_subjects)
        manage_subjects_button.pack(side='right', padx=5)
        
        # Assignment type section
        type_frame = tk.Frame(content_frame)
        type_frame.pack(fill='x', pady=2)
        
        type_label = tk.Label(type_frame, text="Assignment Type:", font=("Helvetica", 11, "bold"))
        type_label.pack(side='left', padx=(0, 10))
        
        self.assignment_type_dropdown = ttk.Combobox(type_frame)
        self.assignment_type_dropdown.pack(side='left', fill='x', expand=True)
        
        manage_types_button = ttk.Button(type_frame, text="Manage Types", command=self.manage_assignment_types)
        manage_types_button.pack(side='right', padx=5)
        
        # Assignment section
        assignment_frame = tk.Frame(content_frame)
        assignment_frame.pack(fill='x', pady=10)
        
        assignment_label = tk.Label(assignment_frame, text="Assignment Text:", font=("Helvetica", 11, "bold"))
        assignment_label.pack(anchor='w')
        
        self.assignment_text = tk.Text(assignment_frame, wrap='word', height=10, font=("Helvetica", 11))
        self.assignment_text.pack(fill='both', expand=True, pady=5)
        
        # Feedback section
        feedback_frame = tk.Frame(content_frame)
        feedback_frame.pack(fill='both', expand=True, pady=10)
        
        feedback_label = tk.Label(feedback_frame, text="Feedback:", font=("Helvetica", 11, "bold"))
        feedback_label.pack(anchor='w')
        
        self.feedback_text = tk.Text(feedback_frame, wrap='word', height=10, font=("Helvetica", 11), state='disabled')
        self.feedback_text.pack(fill='both', expand=True, pady=5)
        
        # Button section
        button_frame = tk.Frame(content_frame)
        button_frame.pack(fill='x', pady=10)
        
        self.get_feedback_button = ttk.Button(button_frame, text="Get Feedback", command=self.get_feedback)
        self.get_feedback_button.pack(side='right', padx=5)
        
        self.clear_button = ttk.Button(button_frame, text="Clear", command=self.clear_fields)
        self.clear_button.pack(side='right', padx=5)
        
        self.export_button = ttk.Button(button_frame, text="Export to Notes", command=self.export_to_notes, state='disabled')
        self.export_button.pack(side='right', padx=5)
    
    def manage_subjects(self):
        """Open the subject management dialog"""
        SubjectManagerDialog(self)
        # Reload subjects after dialog is closed
        self.load_subjects()
    
    def manage_assignment_types(self):
        """Open the assignment type management dialog"""
        AssignmentTypeManagerDialog(self)
        # Reload assignment types after dialog is closed
        self.load_assignment_types()
    
    def get_feedback(self):
        subject_name = self.subject_dropdown.get()
        assignment_type_name = self.assignment_type_dropdown.get()
        assignment_text = self.assignment_text.get('1.0', 'end-1c').strip()
        
        if not subject_name:
            messagebox.showwarning("Missing Information", "Please select a subject.")
            return
        
        if not assignment_type_name:
            messagebox.showwarning("Missing Information", "Please select an assignment type.")
            return
        
        if not assignment_text:
            messagebox.showwarning("Missing Information", "Please enter your assignment text.")
            return
        
        # Check API connection first
        APICheckWindow(self, self.on_api_check_complete)
    
    def on_api_check_complete(self, api_connected):
        if not api_connected:
            messagebox.showerror(
                "API Connection Error", 
                "Could not connect to OpenAI API. Please check your API key in the .env file and ensure you have an internet connection."
            )
            return
        
        # Get the subject, assignment type, and assignment text
        subject_name = self.subject_dropdown.get()
        subject = subjects.get_subject_by_name(subject_name)
        
        assignment_type_name = self.assignment_type_dropdown.get()
        assignment_type = assignment_types.get_assignment_type_by_name(assignment_type_name)
        
        assignment_text = self.assignment_text.get('1.0', 'end-1c').strip()
        
        # Prepare context with subject and assignment type info
        context = f"Subject: {subject_name}\n"
        if subject and subject.get("description"):
            context += f"Subject Description: {subject['description']}\n\n"
        
        context += f"Assignment Type: {assignment_type_name}\n"
        if assignment_type and assignment_type.get("description"):
            context += f"Assignment Type Description: {assignment_type['description']}\n\n"
        
        context += f"Assignment Text:\n{assignment_text}"
        
        # Disable buttons while processing
        self.get_feedback_button.config(state='disabled')
        self.clear_button.config(state='disabled')
        self.export_button.config(state='disabled')
        
        # Clear previous feedback
        self.feedback_text.config(state='normal')
        self.feedback_text.delete('1.0', 'end')
        self.feedback_text.insert('end', "Processing your assignment... Please wait.")
        self.feedback_text.config(state='disabled')
        self.update_idletasks()
        
        # Process in background thread
        def process_in_background():
            try:
                # Call AI handler with feedback role
                response = ai_handler.generate_response(
                    topic=f"Assignment Feedback for {subject_name} - {assignment_type_name}",
                    context=context,
                    role="feedback_giver"
                )
                
                # Update UI on main thread
                self.after(0, lambda: self.update_with_feedback(response))
                
            except Exception as e:
                error_msg = f"An error occurred: {str(e)}"
                self.after(0, lambda: self.update_with_error(error_msg))
        
        # Start background thread
        thread = threading.Thread(target=process_in_background)
        thread.daemon = True
        thread.start()
    
    def update_with_feedback(self, feedback):
        # Enable buttons
        self.get_feedback_button.config(state='normal')
        self.clear_button.config(state='normal')
        self.export_button.config(state='normal')
        
        # Update feedback text
        self.feedback_text.config(state='normal')
        self.feedback_text.delete('1.0', 'end')
        self.feedback_text.insert('1.0', feedback)
        self.feedback_text.config(state='disabled')
    
    def update_with_error(self, error_msg):
        # Enable buttons
        self.get_feedback_button.config(state='normal')
        self.clear_button.config(state='normal')
        self.export_button.config(state='disabled')
        
        # Update feedback text with error
        self.feedback_text.config(state='normal')
        self.feedback_text.delete('1.0', 'end')
        self.feedback_text.insert('1.0', f"Error: {error_msg}")
        self.feedback_text.config(state='disabled')
        
        # Show error dialog
        messagebox.showerror("Error", error_msg)
    
    def clear_fields(self):
        self.assignment_text.delete('1.0', 'end')
        self.feedback_text.config(state='normal')
        self.feedback_text.delete('1.0', 'end')
        self.feedback_text.config(state='disabled')
        self.export_button.config(state='disabled')
    
    def export_to_notes(self):
        """Export the generated feedback to a new note"""
        feedback = self.feedback_text.get('1.0', 'end-1c')
        if not feedback or feedback.startswith("Error:"):
            messagebox.showwarning("Export Error", "There is no valid feedback to export.")
            return
        
        # Get assignment text
        assignment_text = self.assignment_text.get('1.0', 'end-1c').strip()
        
        # Get subject and assignment type for note title
        subject_name = self.subject_dropdown.get()
        assignment_type_name = self.assignment_type_dropdown.get()
        
        # Create a title based on subject and assignment type
        note_title = f"Feedback: {subject_name} - {assignment_type_name}"
        
        # Format the note content with both assignment and feedback
        note_content = f"SUBJECT: {subject_name}\n"
        note_content += f"ASSIGNMENT TYPE: {assignment_type_name}\n\n"
        note_content += f"ASSIGNMENT TEXT:\n{'-' * 80}\n{assignment_text}\n{'-' * 80}\n\n"
        note_content += f"FEEDBACK:\n{'-' * 80}\n{feedback}\n{'-' * 80}\n"
        
        try:
            # Create a new note
            note_id = 0
            existing_notes = [int(f.split('_')[1].split('.')[0]) for f in os.listdir(NOTES_DIR) 
                             if f.startswith('note_') and f.endswith('.json')]
            if existing_notes:
                note_id = max(existing_notes) + 1
            
            # Create note data
            note_data = {
                "id": note_id,
                "title": note_title,
                "content": note_content
            }
            
            # Save to disk
            filename = f"note_{note_id}.json"
            file_path = os.path.join(NOTES_DIR, filename)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(note_data, f, ensure_ascii=False, indent=2)
            
            messagebox.showinfo("Export Successful", f"Feedback exported to Notes as '{note_title}'")
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export to Notes: {str(e)}")

class SubjectManagerDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("Manage Subjects")
        self.geometry("600x400")
        self.minsize(500, 300)
        
        # Make dialog modal
        self.transient(parent)
        self.grab_set()
        
        self.setup_ui()
        self.load_subjects()
        
        # Wait for window to be closed
        self.wait_window()
    
    def setup_ui(self):
        # Create main frame
        main_frame = tk.Frame(self)
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Create subject list frame
        list_frame = tk.Frame(main_frame)
        list_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        list_label = tk.Label(list_frame, text="Subjects", font=("Helvetica", 12, "bold"))
        list_label.pack(anchor='w', pady=(0, 5))
        
        # Create subject listbox with scrollbar
        list_container = tk.Frame(list_frame)
        list_container.pack(fill='both', expand=True)
        
        self.subject_listbox = tk.Listbox(list_container, font=("Helvetica", 11))
        self.subject_listbox.pack(side='left', fill='both', expand=True)
        
        scrollbar = ttk.Scrollbar(list_container, orient='vertical', command=self.subject_listbox.yview)
        scrollbar.pack(side='right', fill='y')
        self.subject_listbox.config(yscrollcommand=scrollbar.set)
        
        # Bind selection event
        self.subject_listbox.bind('<<ListboxSelect>>', self.on_subject_select)
        
        # Create edit frame
        edit_frame = tk.Frame(main_frame)
        edit_frame.pack(side='right', fill='both', expand=True, padx=(10, 0))
        
        edit_label = tk.Label(edit_frame, text="Edit Subject", font=("Helvetica", 12, "bold"))
        edit_label.pack(anchor='w', pady=(0, 5))
        
        # Name field
        name_frame = tk.Frame(edit_frame)
        name_frame.pack(fill='x', pady=5)
        
        name_label = tk.Label(name_frame, text="Name:", font=("Helvetica", 11))
        name_label.pack(side='left', padx=(0, 5))
        
        self.name_entry = tk.Entry(name_frame, font=("Helvetica", 11))
        self.name_entry.pack(side='right', fill='x', expand=True)
        
        # Description field
        desc_label = tk.Label(edit_frame, text="Description:", font=("Helvetica", 11))
        desc_label.pack(anchor='w', pady=(5, 0))
        
        self.desc_text = tk.Text(edit_frame, wrap='word', height=5, font=("Helvetica", 11))
        self.desc_text.pack(fill='both', expand=True, pady=5)
        
        # Buttons
        button_frame = tk.Frame(edit_frame)
        button_frame.pack(fill='x', pady=10)
        
        self.save_button = ttk.Button(button_frame, text="Save", command=self.save_subject)
        self.save_button.pack(side='right', padx=5)
        
        self.delete_button = ttk.Button(button_frame, text="Delete", command=self.delete_subject)
        self.delete_button.pack(side='right', padx=5)
        
        self.new_button = ttk.Button(button_frame, text="New", command=self.new_subject)
        self.new_button.pack(side='right', padx=5)
        
        # Initialize state
        self.current_subject_id = None
        self.update_button_states()
    
    def load_subjects(self):
        """Load subjects into the listbox"""
        self.subject_listbox.delete(0, tk.END)
        
        all_subjects = subjects.load_subjects()
        self.subjects_data = all_subjects
        
        for subject in all_subjects:
            self.subject_listbox.insert(tk.END, subject["name"])
    
    def on_subject_select(self, event):
        """Handle subject selection"""
        selection = self.subject_listbox.curselection()
        if not selection:
            return
        
        index = selection[0]
        if index < len(self.subjects_data):
            subject = self.subjects_data[index]
            self.current_subject_id = subject["id"]
            
            # Update fields
            self.name_entry.delete(0, tk.END)
            self.name_entry.insert(0, subject["name"])
            
            self.desc_text.delete('1.0', tk.END)
            self.desc_text.insert('1.0', subject["description"])
            
            self.update_button_states()
    
    def update_button_states(self):
        """Update button states based on selection"""
        if self.current_subject_id is None:
            self.save_button.config(state='disabled')
            self.delete_button.config(state='disabled')
        else:
            self.save_button.config(state='normal')
            self.delete_button.config(state='normal')
    
    def save_subject(self):
        """Save the current subject"""
        if self.current_subject_id is None:
            return
        
        name = self.name_entry.get().strip()
        description = self.desc_text.get('1.0', 'end-1c').strip()
        
        if not name:
            messagebox.showwarning("Missing Information", "Please enter a subject name.")
            return
        
        # Update subject
        success = subjects.edit_subject(self.current_subject_id, name, description)
        
        if success:
            messagebox.showinfo("Success", "Subject updated successfully.")
            self.load_subjects()
    
    def delete_subject(self):
        """Delete the current subject"""
        if self.current_subject_id is None:
            return
        
        # Confirm deletion
        subject_name = self.name_entry.get().strip()
        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{subject_name}'?")
        if not confirm:
            return
        
        # Delete subject
        success = subjects.delete_subject(self.current_subject_id)
        
        if success:
            messagebox.showinfo("Success", "Subject deleted successfully.")
            self.current_subject_id = None
            self.name_entry.delete(0, tk.END)
            self.desc_text.delete('1.0', tk.END)
            self.update_button_states()
            self.load_subjects()
    
    def new_subject(self):
        """Create a new subject"""
        # Clear selection
        self.subject_listbox.selection_clear(0, tk.END)
        self.current_subject_id = None
        
        # Clear fields
        self.name_entry.delete(0, tk.END)
        self.desc_text.delete('1.0', tk.END)
        
        # Update states
        self.update_button_states()
        
        # Focus name entry
        self.name_entry.focus_set()
        
        # Add save handler for new subject
        self.save_button.config(state='normal', command=self.save_new_subject)
    
    def save_new_subject(self):
        """Save a new subject"""
        name = self.name_entry.get().strip()
        description = self.desc_text.get('1.0', 'end-1c').strip()
        
        if not name:
            messagebox.showwarning("Missing Information", "Please enter a subject name.")
            return
        
        # Add new subject
        success = subjects.add_subject(name, description)
        
        if success:
            messagebox.showinfo("Success", "Subject added successfully.")
            self.save_button.config(command=self.save_subject)
            self.load_subjects()
        else:
            messagebox.showwarning("Error", "A subject with this name already exists.")

class AssignmentTypeManagerDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("Manage Assignment Types")
        self.geometry("600x400")
        self.minsize(500, 300)
        
        # Make dialog modal
        self.transient(parent)
        self.grab_set()
        
        self.setup_ui()
        self.load_types()
        
        # Wait for window to be closed
        self.wait_window()
    
    def setup_ui(self):
        # Create main frame
        main_frame = tk.Frame(self)
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Create type list frame
        list_frame = tk.Frame(main_frame)
        list_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        list_label = tk.Label(list_frame, text="Assignment Types", font=("Helvetica", 12, "bold"))
        list_label.pack(anchor='w', pady=(0, 5))
        
        # Create type listbox with scrollbar
        list_container = tk.Frame(list_frame)
        list_container.pack(fill='both', expand=True)
        
        self.type_listbox = tk.Listbox(list_container, font=("Helvetica", 11))
        self.type_listbox.pack(side='left', fill='both', expand=True)
        
        scrollbar = ttk.Scrollbar(list_container, orient='vertical', command=self.type_listbox.yview)
        scrollbar.pack(side='right', fill='y')
        self.type_listbox.config(yscrollcommand=scrollbar.set)
        
        # Bind selection event
        self.type_listbox.bind('<<ListboxSelect>>', self.on_type_select)
        
        # Create edit frame
        edit_frame = tk.Frame(main_frame)
        edit_frame.pack(side='right', fill='both', expand=True, padx=(10, 0))
        
        edit_label = tk.Label(edit_frame, text="Edit Assignment Type", font=("Helvetica", 12, "bold"))
        edit_label.pack(anchor='w', pady=(0, 5))
        
        # Name field
        name_frame = tk.Frame(edit_frame)
        name_frame.pack(fill='x', pady=5)
        
        name_label = tk.Label(name_frame, text="Name:", font=("Helvetica", 11))
        name_label.pack(side='left', padx=(0, 5))
        
        self.name_entry = tk.Entry(name_frame, font=("Helvetica", 11))
        self.name_entry.pack(side='right', fill='x', expand=True)
        
        # Description field
        desc_label = tk.Label(edit_frame, text="Description:", font=("Helvetica", 11))
        desc_label.pack(anchor='w', pady=(5, 0))
        
        self.desc_text = tk.Text(edit_frame, wrap='word', height=5, font=("Helvetica", 11))
        self.desc_text.pack(fill='both', expand=True, pady=5)
        
        # Buttons
        button_frame = tk.Frame(edit_frame)
        button_frame.pack(fill='x', pady=10)
        
        self.save_button = ttk.Button(button_frame, text="Save", command=self.save_type)
        self.save_button.pack(side='right', padx=5)
        
        self.delete_button = ttk.Button(button_frame, text="Delete", command=self.delete_type)
        self.delete_button.pack(side='right', padx=5)
        
        self.new_button = ttk.Button(button_frame, text="New", command=self.new_type)
        self.new_button.pack(side='right', padx=5)
        
        # Initialize state
        self.current_type_id = None
        self.update_button_states()
    
    def load_types(self):
        """Load assignment types into the listbox"""
        self.type_listbox.delete(0, tk.END)
        
        all_types = assignment_types.load_assignment_types()
        self.types_data = all_types
        
        for type_obj in all_types:
            self.type_listbox.insert(tk.END, type_obj["name"])
    
    def on_type_select(self, event):
        """Handle assignment type selection"""
        selection = self.type_listbox.curselection()
        if not selection:
            return
        
        index = selection[0]
        if index < len(self.types_data):
            type_obj = self.types_data[index]
            self.current_type_id = type_obj["id"]
            
            # Update fields
            self.name_entry.delete(0, tk.END)
            self.name_entry.insert(0, type_obj["name"])
            
            self.desc_text.delete('1.0', tk.END)
            self.desc_text.insert('1.0', type_obj["description"])
            
            self.update_button_states()
    
    def update_button_states(self):
        """Update button states based on selection"""
        if self.current_type_id is None:
            self.save_button.config(state='disabled')
            self.delete_button.config(state='disabled')
        else:
            self.save_button.config(state='normal')
            self.delete_button.config(state='normal')
    
    def save_type(self):
        """Save the current assignment type"""
        if self.current_type_id is None:
            return
        
        name = self.name_entry.get().strip()
        description = self.desc_text.get('1.0', 'end-1c').strip()
        
        if not name:
            messagebox.showwarning("Missing Information", "Please enter an assignment type name.")
            return
        
        # Update type
        success = assignment_types.edit_assignment_type(self.current_type_id, name, description)
        
        if success:
            messagebox.showinfo("Success", "Assignment type updated successfully.")
            self.load_types()
    
    def delete_type(self):
        """Delete the current assignment type"""
        if self.current_type_id is None:
            return
        
        # Confirm deletion
        type_name = self.name_entry.get().strip()
        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{type_name}'?")
        if not confirm:
            return
        
        # Delete type
        success = assignment_types.delete_assignment_type(self.current_type_id)
        
        if success:
            messagebox.showinfo("Success", "Assignment type deleted successfully.")
            self.current_type_id = None
            self.name_entry.delete(0, tk.END)
            self.desc_text.delete('1.0', tk.END)
            self.update_button_states()
            self.load_types()
    
    def new_type(self):
        """Create a new assignment type"""
        # Clear selection
        self.type_listbox.selection_clear(0, tk.END)
        self.current_type_id = None
        
        # Clear fields
        self.name_entry.delete(0, tk.END)
        self.desc_text.delete('1.0', tk.END)
        
        # Update states
        self.update_button_states()
        
        # Focus name entry
        self.name_entry.focus_set()
        
        # Add save handler for new type
        self.save_button.config(state='normal', command=self.save_new_type)
    
    def save_new_type(self):
        """Save a new assignment type"""
        name = self.name_entry.get().strip()
        description = self.desc_text.get('1.0', 'end-1c').strip()
        
        if not name:
            messagebox.showwarning("Missing Information", "Please enter an assignment type name.")
            return
        
        # Add new type
        success = assignment_types.add_assignment_type(name, description)
        
        if success:
            messagebox.showinfo("Success", "Assignment type added successfully.")
            self.save_button.config(command=self.save_type)
            self.load_types()
        else:
            messagebox.showwarning("Error", "An assignment type with this name already exists.")

class StarterPage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.setup_ui()
        self.load_subjects()
        self.load_assignment_types()

    def load_subjects(self):
        """Load subjects into the dropdown"""
        subject_names = subjects.get_subject_names()
        self.subject_dropdown['values'] = subject_names
        if subject_names:
            self.subject_dropdown.current(0)

    def load_assignment_types(self):
        """Load assignment types into the dropdown"""
        type_names = assignment_types.get_assignment_type_names()
        self.assignment_type['values'] = type_names
        if type_names:
            self.assignment_type.current(0)

    def setup_ui(self):
        title_label = tk.Label(self, text="Assignment Starter", font=("Helvetica", 16, "bold"))
        title_label.pack(pady=10)
        
        description = tk.Label(self, text="Get help starting your assignments with AI-generated outlines and ideas.", 
                             font=("Helvetica", 10))
        description.pack(pady=5)
        
        # Create main content area
        content_frame = tk.Frame(self)
        content_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Subject selection section
        subject_frame = tk.Frame(content_frame)
        subject_frame.pack(fill='x', pady=2)
        
        subject_label = tk.Label(subject_frame, text="Subject:", font=("Helvetica", 11, "bold"))
        subject_label.pack(side='left', padx=(0, 10))
        
        self.subject_dropdown = ttk.Combobox(subject_frame)
        self.subject_dropdown.pack(side='left', fill='x', expand=True)
        
        manage_subjects_button = ttk.Button(subject_frame, text="Manage Subjects", command=self.manage_subjects)
        manage_subjects_button.pack(side='right', padx=5)
        
        # Assignment type section
        type_frame = tk.Frame(content_frame)
        type_frame.pack(fill='x', pady=2)
        
        type_label = tk.Label(type_frame, text="Assignment Type:", font=("Helvetica", 11, "bold"))
        type_label.pack(side='left', padx=(0, 10))
        
        self.assignment_type = ttk.Combobox(type_frame)
        self.assignment_type.pack(side='left', fill='x', expand=True)
        
        manage_types_button = ttk.Button(type_frame, text="Manage Types", command=self.manage_assignment_types)
        manage_types_button.pack(side='right', padx=5)
        
        # Description section
        description_frame = tk.Frame(content_frame)
        description_frame.pack(fill='x', pady=10)
        
        description_label = tk.Label(description_frame, text="Assignment Description:", font=("Helvetica", 11, "bold"))
        description_label.pack(anchor='w')
        
        self.description_text = tk.Text(description_frame, wrap='word', height=6, font=("Helvetica", 11))
        self.description_text.pack(fill='both', expand=True, pady=5)
        
        # Generated content section
        output_frame = tk.Frame(content_frame)
        output_frame.pack(fill='both', expand=True, pady=10)
        
        output_label = tk.Label(output_frame, text="Starter Content:", font=("Helvetica", 11, "bold"))
        output_label.pack(anchor='w')
        
        self.output_text = tk.Text(output_frame, wrap='word', height=12, font=("Helvetica", 11), state='disabled')
        self.output_text.pack(fill='both', expand=True, pady=5)
        
        # Button section
        button_frame = tk.Frame(content_frame)
        button_frame.pack(fill='x', pady=10)
        
        self.generate_button = ttk.Button(button_frame, text="Generate Starter", command=self.generate_starter)
        self.generate_button.pack(side='right', padx=5)
        
        self.clear_button = ttk.Button(button_frame, text="Clear", command=self.clear_fields)
        self.clear_button.pack(side='right', padx=5)
        
        self.export_button = ttk.Button(button_frame, text="Export to Notes", command=self.export_to_notes, state='disabled')
        self.export_button.pack(side='right', padx=5)
    
    def manage_subjects(self):
        """Open the subject management dialog"""
        SubjectManagerDialog(self)
        # Reload subjects after dialog is closed
        self.load_subjects()
    
    def manage_assignment_types(self):
        """Open the assignment type management dialog"""
        AssignmentTypeManagerDialog(self)
        # Reload assignment types after dialog is closed
        self.load_assignment_types()
    
    def generate_starter(self):
        subject_name = self.subject_dropdown.get()
        assignment_type_name = self.assignment_type.get()
        description = self.description_text.get('1.0', 'end-1c').strip()
        
        if not subject_name:
            messagebox.showwarning("Missing Information", "Please select a subject.")
            return
        
        if not assignment_type_name:
            messagebox.showwarning("Missing Information", "Please select an assignment type.")
            return
        
        if not description:
            messagebox.showwarning("Missing Information", "Please enter your assignment description.")
            return
        
        # Check API connection first
        APICheckWindow(self, self.on_api_check_complete)
    
    def on_api_check_complete(self, api_connected):
        if not api_connected:
            messagebox.showerror(
                "API Connection Error", 
                "Could not connect to OpenAI API. Please check your API key in the .env file and ensure you have an internet connection."
            )
            return
        
        # Get inputs
        subject_name = self.subject_dropdown.get()
        subject = subjects.get_subject_by_name(subject_name)
        
        assignment_type_name = self.assignment_type.get()
        assignment_type = assignment_types.get_assignment_type_by_name(assignment_type_name)
        
        description = self.description_text.get('1.0', 'end-1c').strip()
        
        # Prepare context with subject and assignment type info
        context = f"Subject: {subject_name}\n"
        if subject and subject.get("description"):
            context += f"Subject Description: {subject['description']}\n\n"
        
        context += f"Assignment Type: {assignment_type_name}\n"
        if assignment_type and assignment_type.get("description"):
            context += f"Assignment Type Description: {assignment_type['description']}\n\n"
        
        context += f"Assignment Description: {description}"
        
        # Disable buttons while processing
        self.generate_button.config(state='disabled')
        self.clear_button.config(state='disabled')
        self.export_button.config(state='disabled')
        
        # Clear previous output
        self.output_text.config(state='normal')
        self.output_text.delete('1.0', 'end')
        self.output_text.insert('end', "Generating starter content... Please wait.")
        self.output_text.config(state='disabled')
        self.update_idletasks()
        
        # Process in background thread
        def process_in_background():
            try:
                # Call AI handler with assignment_starter role
                response = ai_handler.generate_response(
                    topic=f"Assignment Starter for {subject_name} - {assignment_type_name}",
                    context=context,
                    role="assignment_starter"
                )
                
                # Update UI on main thread
                self.after(0, lambda: self.update_with_starter(response))
                
            except Exception as e:
                error_msg = f"An error occurred: {str(e)}"
                self.after(0, lambda: self.update_with_error(error_msg))
        
        # Start background thread
        thread = threading.Thread(target=process_in_background)
        thread.daemon = True
        thread.start()
    
    def update_with_starter(self, starter_content):
        # Enable buttons
        self.generate_button.config(state='normal')
        self.clear_button.config(state='normal')
        self.export_button.config(state='normal')
        
        # Update output text
        self.output_text.config(state='normal')
        self.output_text.delete('1.0', 'end')
        self.output_text.insert('1.0', starter_content)
        self.output_text.config(state='disabled')
    
    def update_with_error(self, error_msg):
        # Enable buttons
        self.generate_button.config(state='normal')
        self.clear_button.config(state='normal')
        self.export_button.config(state='disabled')
        
        # Update output text with error
        self.output_text.config(state='normal')
        self.output_text.delete('1.0', 'end')
        self.output_text.insert('1.0', f"Error: {error_msg}")
        self.output_text.config(state='disabled')
        
        # Show error dialog
        messagebox.showerror("Error", error_msg)
    
    def clear_fields(self):
        self.description_text.delete('1.0', 'end')
        self.output_text.config(state='normal')
        self.output_text.delete('1.0', 'end')
        self.output_text.config(state='disabled')
        self.export_button.config(state='disabled')
    
    def export_to_notes(self):
        """Export the generated starter content to a new note"""
        starter_content = self.output_text.get('1.0', 'end-1c')
        if not starter_content or starter_content.startswith("Error:"):
            messagebox.showwarning("Export Error", "There is no valid content to export.")
            return
        
        # Get assignment description
        description = self.description_text.get('1.0', 'end-1c').strip()
        
        # Get subject and assignment type for note title
        subject_name = self.subject_dropdown.get()
        assignment_type_name = self.assignment_type.get()
        
        # Create a title based on subject and assignment type
        note_title = f"Starter: {subject_name} - {assignment_type_name}"
        
        # Format the note content with both description and starter content
        note_content = f"SUBJECT: {subject_name}\n"
        note_content += f"ASSIGNMENT TYPE: {assignment_type_name}\n\n"
        note_content += f"ASSIGNMENT DESCRIPTION:\n{'-' * 80}\n{description}\n{'-' * 80}\n\n"
        note_content += f"STARTER CONTENT:\n{'-' * 80}\n{starter_content}\n{'-' * 80}\n"
        
        try:
            # Create a new note
            note_id = 0
            existing_notes = [int(f.split('_')[1].split('.')[0]) for f in os.listdir(NOTES_DIR) 
                             if f.startswith('note_') and f.endswith('.json')]
            if existing_notes:
                note_id = max(existing_notes) + 1
            
            # Create note data
            note_data = {
                "id": note_id,
                "title": note_title,
                "content": note_content
            }
            
            # Save to disk
            filename = f"note_{note_id}.json"
            file_path = os.path.join(NOTES_DIR, filename)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(note_data, f, ensure_ascii=False, indent=2)
            
            messagebox.showinfo("Export Successful", f"Starter content exported to Notes as '{note_title}'")
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export to Notes: {str(e)}") 