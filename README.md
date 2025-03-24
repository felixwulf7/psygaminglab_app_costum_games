# Dynamic Games - Therapeutic 3D Shooter

A therapeutic 3D game application where players shoot positive thoughts (affirmations) at negative thoughts, customized based on user input.

## Features

- Generates custom 3D shooter games based on user input
- Uses AI to create personalized positive affirmations and negative thoughts
- Beautiful 3D interface with three.js
- Multiple difficulty levels

## Important Requirements

**The application requires a virtual environment with specific dependencies to run correctly.**

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Internet connection (for DeepInfra API)

## Setup Instructions

1. **Create a virtual environment named `venv_new`** (this exact name is expected by the start script):
   ```
   python -m venv venv_new
   ```

2. **Activate the virtual environment**:
   - macOS/Linux: `source venv_new/bin/activate`
   - Windows: `venv_new\Scripts\activate`

3. **Install dependencies**:
   ```
   pip install -r requirements.txt
   ```

4. **Start the server**:
   - Using the script: `./start_app.sh`
   - Or manually: `source venv_new/bin/activate && python server.py`

5. **Access the application**:
   - Open your browser and go to http://localhost:5000
   - Enter your situation or feelings in the form to generate a customized game

## How It Works

1. User inputs a situation they're struggling with (e.g., "feeling overwhelmed with work")
2. The AI generates:
   - A custom game title
   - 5 negative thoughts related to the situation
   - 5 positive affirmations that counter those negative thoughts
3. The application creates a custom 3D game where players shoot positive thoughts at negative ones
4. Players learn to recognize and challenge negative thought patterns

## Technical Details

- **API Integration**: Using DeepInfra cloud-based API service
- **Template File**: Located in `templates/3d_shooter_accepting_being_tired.html`
- **Generated Games**: Stored in the `static/` directory
- **Debug Files**: Copies of generated games saved in `debug_games/` for troubleshooting

## Directory Structure

- `server.py` - Main Flask application
- `templates/` - Contains the base game template
- `static/` - Folder for serving generated games
- `debug_games/` - Copies of generated games for debugging
- `requirements.txt` - Lists required Python packages
- `start_app.sh` - Shell script for starting the application

## Troubleshooting

- **Port in Use**: If port 5000 is already in use, you may need to kill existing processes or use a different port
- **Virtual Environment Issues**: Ensure you're using the correct virtual environment (`venv_new`)
- **Missing Dependencies**: Make sure all dependencies from requirements.txt are installed

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Three.js for the 3D game engine
- Flask and Flask-CORS for the web framework
- Ollama and DeepInfra for AI capabilities 