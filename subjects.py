import os
import json
from pathlib import Path

# Constants
APP_DIR = os.path.join(str(Path.home()), "Documents", "SAII")
SUBJECTS_FILE = os.path.join(APP_DIR, "subjects.json")

# Ensure the app directory exists
os.makedirs(APP_DIR, exist_ok=True)

def load_subjects():
    """Load subjects from the subjects.json file"""
    if not os.path.exists(SUBJECTS_FILE):
        # Create default subjects file if it doesn't exist
        default_subjects = [
            {
                "id": 1,
                "name": "Mathematics",
                "description": "The study of numbers, quantities, and shapes, including algebra, calculus, geometry, and statistics."
            },
            {
                "id": 2,
                "name": "Computer Science",
                "description": "The study of computers and computational systems, including programming, algorithms, data structures, and software engineering."
            },
            {
                "id": 3,
                "name": "Physics",
                "description": "The natural science that studies matter, motion, energy, and force, including mechanics, thermodynamics, and quantum physics."
            },
            {
                "id": 4, 
                "name": "Chemistry",
                "description": "The study of matter, its properties, composition, structure, and changes during interactions."
            },
            {
                "id": 5,
                "name": "Biology",
                "description": "The study of life and living organisms, including their structure, function, growth, and evolution."
            },
            {
                "id": 6,
                "name": "History",
                "description": "The study of past events, particularly human affairs, social, economic, and political developments."
            },
            {
                "id": 7,
                "name": "Literature",
                "description": "The study of written works, including fiction, non-fiction, poetry, and drama."
            },
            {
                "id": 8,
                "name": "Psychology",
                "description": "The scientific study of the mind and behavior, including cognitive processes, emotions, and social interactions."
            },
            {
                "id": 9,
                "name": "Economics",
                "description": "The study of how individuals, businesses, and societies allocate resources, including production, consumption, and exchange."
            },
            {
                "id": 10,
                "name": "Political Science",
                "description": "The study of governments, political behavior, and power relations, including political systems, public policy, and international relations."
            }
        ]
        save_subjects(default_subjects)
        return default_subjects
    
    try:
        with open(SUBJECTS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading subjects: {e}")
        return []

def save_subjects(subjects):
    """Save subjects to the subjects.json file"""
    try:
        with open(SUBJECTS_FILE, 'w', encoding='utf-8') as f:
            json.dump(subjects, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Error saving subjects: {e}")
        return False

def get_subject_names():
    """Get a list of subject names for dropdowns"""
    subjects = load_subjects()
    return [subject["name"] for subject in subjects]

def get_subject_by_name(name):
    """Get a subject by name"""
    subjects = load_subjects()
    for subject in subjects:
        if subject["name"] == name:
            return subject
    return None

def add_subject(name, description):
    """Add a new subject"""
    subjects = load_subjects()
    
    # Check if subject already exists
    for subject in subjects:
        if subject["name"] == name:
            return False
    
    # Create new ID
    new_id = max([subject["id"] for subject in subjects], default=0) + 1
    
    # Add new subject
    subjects.append({
        "id": new_id,
        "name": name,
        "description": description
    })
    
    # Save changes
    return save_subjects(subjects)

def edit_subject(subject_id, name, description):
    """Edit an existing subject"""
    subjects = load_subjects()
    
    # Find subject by ID
    for subject in subjects:
        if subject["id"] == subject_id:
            subject["name"] = name
            subject["description"] = description
            return save_subjects(subjects)
    
    return False

def delete_subject(subject_id):
    """Delete a subject by ID"""
    subjects = load_subjects()
    
    # Find subject by ID
    for i, subject in enumerate(subjects):
        if subject["id"] == subject_id:
            subjects.pop(i)
            return save_subjects(subjects)
    
    return False 