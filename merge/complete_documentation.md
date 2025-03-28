# PsyGaming Lab App - Complete Documentation

# Technical Overview

## Application Summary
The PsyGaming Lab App is a therapeutic gaming platform that creates custom 3D games where players shoot positive thoughts (affirmations) at negative thoughts, based on user input about their specific mental health challenges. Each game is dynamically generated with personalized content.

## Technology Stack
- **Backend**: Flask (Python)
- **Frontend**: HTML/CSS/JavaScript with Three.js for 3D graphics
- **AI Integration**: Multiple LLM API options (DeepInfra, Ollama, OpenAI, Anthropic)
- **Default LLM**: meta-llama/Llama-2-70b-chat-hf via DeepInfra

## Key Features
- Custom game generation based on user input
- 3D interactive therapeutic gameplay
- Personalized positive and negative thought content
- Multiple LLM backend options
- Debug mode for game development

## Deployment
- Development server on http://localhost:5002
- Not configured for production deployment (uses Flask development server)
- Optional parameters for port configuration

# Application Architecture

## Directory Structure
```
/
├── server.py                # Main Flask application
├── requirements.txt         # Python dependencies
├── templates/               # HTML templates
│   └── 3d_shooter_accepting_being_tired.html  # Base game template
├── static/                  # Static assets and generated games
│   └── custom_game_*.html   # Generated game files
├── debug_games/             # Copies of generated games for debugging
│   └── debug_custom_game_*.html
└── docs/                    # Documentation
```

## Application Flow
1. User submits a mental health challenge through the web interface
2. Server processes the request and generates a prompt for the LLM
3. LLM generates customized content (game title, positive thoughts, negative thoughts)
4. Server validates and formats the LLM response
5. Server generates a new HTML game file based on the template and LLM content
6. Server returns the URL to the newly created game
7. User plays the 3D game in their browser

## Server Components
- **Flask Application**: Handles HTTP requests, serves static files
- **LLM Integration**: Multiple API connectors (DeepInfra, Ollama, OpenAI, Anthropic)
- **Game Generator**: Creates custom HTML files based on templates and LLM responses
- **Debug Tools**: Saves copies of games for debugging purposes

## Game Structure
- **3D Environment**: Built with Three.js
- **Game Mechanics**: Player shoots "positive thoughts" at "negative thoughts"
- **Matching System**: Each positive thought must be matched with its corresponding negative thought
- **Dynamic Content**: Each game's content is uniquely generated based on user input

# API Documentation

## Endpoints

### GET /
- **Description**: Serves the main application interface
- **Response**: HTML page with the game creation form

### GET /api/models
- **Description**: Returns the list of available LLM models
- **Response**: JSON array of model information
  ```json
  {
    "models": [
      {
        "id": "meta-llama/Llama-2-70b-chat-hf",
        "name": "Llama 2 70B",
        "description": "Meta's large language model"
      },
      ...
    ]
  }
  ```

### POST /api/create-game
- **Description**: Creates a custom game based on user input
- **Request Body**:
  ```json
  {
    "userInput": "User's mental health challenge",
    "model": "model_id" (optional)
  }
  ```
- **Response**: JSON object with game URL
  ```json
  {
    "gameUrl": "/game/custom_game_1234567890.html",
    "status": "success"
  }
  ```

### GET /game/{game_filename}
- **Description**: Serves a specific game file
- **Parameters**: `game_filename` - The filename of the generated game
- **Response**: HTML game file

## LLM Integration API

The application supports multiple LLM backends:

### DeepInfra API
- **Endpoint**: `https://api.deepinfra.com/v1/inference/meta-llama/Llama-2-70b-chat-hf`
- **Authentication**: API key in request header
- **Request Format**: JSON with prompt and parameters
- **Response Format**: JSON with generated text

### Ollama API
- **Endpoint**: `http://localhost:11434/api/generate`
- **Request Format**: JSON with model name and prompt
- **Response Format**: JSON with generated response

### Other Supported APIs
- OpenAI API
- Anthropic API

Each API has specific formatting and response handling in the server code.

# Setup Guide

## Prerequisites
- Python 3.7+
- pip (Python package manager)
- Git (optional, for cloning the repository)

## Installation

### 1. Clone the Repository (optional)
```bash
git clone https://github.com/felixwulf7/28marchapp.git
cd 28marchapp
```

### 2. Set Up Virtual Environment (recommended)
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

## Configuration

### LLM API Configuration
The application supports multiple LLM backends. By default, it uses DeepInfra's API.

To change the LLM backend, modify these variables in `server.py`:
```python
# Configuration
LLM_API_TYPE = "deepinfra"  # Options: "ollama", "deepinfra", "openai", "anthropic"
DEFAULT_MODEL = "meta-llama/Llama-2-70b-chat-hf"  # Default model
```

### API Keys
If using DeepInfra, OpenAI, or Anthropic, you need to set your API key:
```python
DEEPINFRA_API_KEY = "your_api_key_here"
# or
OPENAI_API_KEY = "your_api_key_here"
# or
ANTHROPIC_API_KEY = "your_api_key_here"
```

## Running the Application

### Start the Server
```bash
python server.py
```

The server will start on http://localhost:5002 by default.

### Access the Application
Open your web browser and navigate to:
```
http://localhost:5002
```

## Using Ollama (Local LLM)
If you want to use Ollama as your LLM backend:

1. Install Ollama from https://ollama.ai/
2. Start the Ollama server
3. Set `LLM_API_TYPE = "ollama"` in `server.py`
4. Run the application

The application will automatically try to start Ollama if it's not running.

# Game Customization Guide

## Game Template Structure
The game is generated from a template HTML file located at `templates/3d_shooter_accepting_being_tired.html`. 
You can customize this template to change the game's appearance, mechanics, or behavior.

## Key Components to Customize

### 1. Game Title and Text Content
The LLM generates a title and text content, which are injected into the template:
```javascript
const gameTitle = "Generated Title";
const positiveThoughts = [ /* Array of positive thoughts */ ];
const negativeThoughts = [ /* Array of negative thoughts */ ];
```

### 2. 3D Environment
The game environment is built with Three.js. You can modify:
- Scene background
- Lighting
- Textures and materials
- World size and boundaries

Main environment setup:
```javascript
function createScene() {
    // Three.js scene creation code
    scene = new THREE.Scene();
    scene.background = new THREE.Color(0x87CEEB); // Sky blue background
    
    // Set up lights, camera, renderer, etc.
}
```

### 3. Game Mechanics
The core game mechanics involve:
- Player movement (WASD keys)
- Aiming (mouse)
- Shooting positive thoughts (mouse click)
- Hitting negative thoughts with matching positive thoughts

Key game mechanics code:
```javascript
function shootPositiveThought() {
    // Code for shooting positive thoughts
}

function checkCollisions() {
    // Code for detecting collisions between thoughts
}
```

### 4. UI Elements
The UI includes:
- Positive thought selector
- Score display
- Game messages

UI elements are created and managed in:
```javascript
function createUI() {
    // UI creation code
}

function updateUI() {
    // UI update code
}
```

## Creating Custom Game Templates

1. Copy the existing template to a new file:
   ```bash
   cp templates/3d_shooter_accepting_being_tired.html templates/my_custom_template.html
   ```

2. Modify the template file to change appearance and behavior

3. Update the template path in `server.py`:
   ```python
   TEMPLATE_GAME_PATH = "templates/my_custom_template.html"
   ```

## LLM Response Format
To ensure compatibility with your template, the LLM response should follow this structure:
```json
{
  "title": "Game Title",
  "positiveThoughts": ["thought1", "thought2", "thought3", "thought4", "thought5"],
  "negativeThoughts": [
    {"text": "negative1", "correctAmmo": 0},
    {"text": "negative2", "correctAmmo": 1},
    {"text": "negative3", "correctAmmo": 2},
    {"text": "negative4", "correctAmmo": 3},
    {"text": "negative5", "correctAmmo": 4}
  ]
}
```

If you modify this structure in your template, you'll need to update the prompt in `server.py` to ensure the LLM generates compatible content. 