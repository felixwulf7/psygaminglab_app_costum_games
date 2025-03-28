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