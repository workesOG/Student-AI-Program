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
python -m venv /.venv
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

Replace `your_api_key_here` with your actual OpenAI API key.
You can change both model and max tokens if you feel like it.

## Running the Program

After installing dependencies and configuring your API key, run the program:

```bash
python main.py
```

The application will start with the Notes Tool active by default.

## How to Use

### Notes Tool

- Click "New Note" to create a new note
- Enter a title for your note
- Type your content in the text area
- Click "Save" to save your note
- Use "Generate Notes with AI" to get AI assistance with your notes
  - Enter a topic and provide context for the AI
  - The AI-generated content will be added to your current note

### Feedback Tool

- Select a subject from the dropdown
- Select an assignment type from the dropdown
- Enter your assignment text
- Click "Get Feedback" to receive AI-generated feedback
- Use "Export to Notes" to save the feedback as a note

### Starter Tool

- Select a subject from the dropdown
- Select an assignment type from the dropdown
- Enter your assignment description
- Click "Generate Starter" to get AI-generated outline and starter content
- Use "Export to Notes" to save the starter content as a note

## Notes Storage

All notes are saved as JSON files in your Documents folder under `SAII/Notes/`.

## Subjects and Assignment Types

You can manage subjects and assignment types by clicking the "Manage Subjects" or "Manage Types" buttons in the Feedback or Starter tools.

## Troubleshooting

### API Key Issues

If you see a warning about a missing API key:

1. Make sure you've created a `.env` file with your API key
2. Check that your API key is valid and not expired
3. Restart the application after adding or updating your API key

### Connection Issues

If the application can't connect to the OpenAI API:

1. Check your internet connection
2. Verify your API key is correct
3. Make sure you haven't exceeded your API usage limits

## License

[MIT License](LICENSE)
