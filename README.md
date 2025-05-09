# Student AI Program

An exam-project program to act as an interface between students and AI.

## Features

- **Note Tool**: Create, edit, save, and delete notes with AI-assisted note generation
- **Feedback Tool**: Get AI-generated feedback on your assignments
- **Starter Tool**: Generate AI-powered outlines and starter content for assignments

## Requirements

- Python 3.8 or higher
- OpenAI API key

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/Student-AI-Program.git
cd Student-AI-Program
```

2. Create and enter virtual environment:

```bash
python -m venv .venv
.\.venv\scripts\activate.bat
```

3. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Configuration

Before running the program, you need to set up your OpenAI API key
You can get your API key from: Get an API key from [OpenAI Platform](https://platform.openai.com/api-keys)

The program will automatically create a `.env` file for you if one doesn't exist, but you'll need to add your API key to it:

```env
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=o4-mini
MAX_TOKENS=5000
```

Replace `your_api_key_here` with your actual OpenAI API key. You can change both model and max tokens if you feel like it.

## Running the Program

After installing dependencies and configuring your API key, run the program:

```bash
python main.py
```
