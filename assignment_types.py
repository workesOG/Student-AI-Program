import os
import json
from pathlib import Path

# Constants
APP_DIR = os.path.join(str(Path.home()), "Documents", "SAII")
ASSIGNMENT_TYPES_FILE = os.path.join(APP_DIR, "assignment_types.json")

# Ensure the app directory exists
os.makedirs(APP_DIR, exist_ok=True)

def load_assignment_types():
    """Load assignment types from the assignment_types.json file"""
    if not os.path.exists(ASSIGNMENT_TYPES_FILE):
        # Create default assignment types file if it doesn't exist
        default_types = [
            {
                "id": 1,
                "name": "Essay",
                "description": "A formal piece of writing that analyzes or evaluates a specific topic, often requiring citations and research."
            },
            {
                "id": 2,
                "name": "Report",
                "description": "A structured document that presents facts, findings, and analysis on a specific topic or event."
            },
            {
                "id": 3,
                "name": "Research Paper",
                "description": "An in-depth academic paper based on original research, typically requiring a thesis, evidence, and citations."
            },
            {
                "id": 4, 
                "name": "Lab Report",
                "description": "A formal document describing a scientific experiment, including methods, results, and conclusions."
            },
            {
                "id": 5,
                "name": "Presentation",
                "description": "A visual and verbal delivery of information, often accompanied by slides or other visual aids."
            },
            {
                "id": 6,
                "name": "Case Study",
                "description": "An in-depth analysis of a specific situation, person, group, or event to demonstrate application of concepts."
            },
            {
                "id": 7,
                "name": "Code Project",
                "description": "A programming assignment that requires designing, implementing, and testing software."
            },
            {
                "id": 8,
                "name": "Literature Review",
                "description": "A comprehensive summary and critical analysis of existing research on a specific topic."
            },
            {
                "id": 9,
                "name": "Problem Set",
                "description": "A collection of problems or exercises requiring step-by-step solutions, often in math or science."
            },
            {
                "id": 10,
                "name": "Other",
                "description": "Any other type of assignment not covered by the standard categories."
            }
        ]
        save_assignment_types(default_types)
        return default_types
    
    try:
        with open(ASSIGNMENT_TYPES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading assignment types: {e}")
        return []

def save_assignment_types(types):
    """Save assignment types to the assignment_types.json file"""
    try:
        with open(ASSIGNMENT_TYPES_FILE, 'w', encoding='utf-8') as f:
            json.dump(types, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Error saving assignment types: {e}")
        return False

def get_assignment_type_names():
    """Get a list of assignment type names for dropdowns"""
    types = load_assignment_types()
    return [type_obj["name"] for type_obj in types]

def get_assignment_type_by_name(name):
    """Get an assignment type by name"""
    types = load_assignment_types()
    for type_obj in types:
        if type_obj["name"] == name:
            return type_obj
    return None

def add_assignment_type(name, description):
    """Add a new assignment type"""
    types = load_assignment_types()
    
    # Check if type already exists
    for type_obj in types:
        if type_obj["name"] == name:
            return False
    
    # Create new ID
    new_id = max([type_obj["id"] for type_obj in types], default=0) + 1
    
    # Add new type
    types.append({
        "id": new_id,
        "name": name,
        "description": description
    })
    
    # Save changes
    return save_assignment_types(types)

def edit_assignment_type(type_id, name, description):
    """Edit an existing assignment type"""
    types = load_assignment_types()
    
    # Find type by ID
    for type_obj in types:
        if type_obj["id"] == type_id:
            type_obj["name"] = name
            type_obj["description"] = description
            return save_assignment_types(types)
    
    return False

def delete_assignment_type(type_id):
    """Delete an assignment type by ID"""
    types = load_assignment_types()
    
    # Find type by ID
    for i, type_obj in enumerate(types):
        if type_obj["id"] == type_id:
            types.pop(i)
            return save_assignment_types(types)
    
    return False 