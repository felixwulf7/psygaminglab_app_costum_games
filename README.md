# Dynamic Therapeutic Games

A web application that generates personalized 3D games to help users transform negative thoughts into positive affirmations through interactive gameplay.

## Features

- Generates custom therapeutic games based on user input
- Uses AI to create personalized content specific to the user's situation
- Interactive 3D shooter game where players target negative thoughts with positive affirmations
- Support for both local (Ollama) and cloud-based (DeepInfra) AI models

## Cloud API Integration

This version supports both Ollama (local) and DeepInfra (cloud) API integration:

- **Ollama**: Runs locally on your machine, requires installation and model downloads
- **DeepInfra**: Cloud-based API service, no local installation needed, just requires an API key

Benefits of the DeepInfra integration:
- No dependency on local LLM installation
- Extremely cost-effective (approximately $0.0015 per game generation)
- Access to powerful models like Llama-2-70b
- Suitable for web deployment and scalable hosting

## Setup and Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- For Ollama mode only: Ollama installed (https://ollama.ai/)

### Installation

1. **Create a virtual environment** (recommended):
   ```
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**:
   ```
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```
   # On macOS/Linux:
   ./start_app.sh
   
   # On Windows:
   start_app.bat
   ```

The start script will guide you through choosing between Ollama and DeepInfra APIs.

## Using DeepInfra API

The application comes preconfigured with a DeepInfra API key, but you can use your own:

1. Create an account at [DeepInfra](https://deepinfra.com/)
2. Generate an API key in your dashboard
3. When running the start script, choose the DeepInfra option and enter your API key when prompted

## How It Works

1. User inputs a situation they're struggling with
2. The AI generates:
   - A custom game title
   - 5 negative thoughts related to the situation
   - 5 positive affirmations that counter those negative thoughts
3. The application creates a custom 3D game where players shoot positive thoughts at negative ones
4. Players learn to recognize and challenge negative thought patterns

## Deep Research Prompts

This project includes a directory of comprehensive research prompts in `/deepsearchprompt` to help with future development:

- **Next.js Integration**: For integrating with a Next.js frontend
- **Monetization Strategies**: For implementing sustainable revenue models
- **UX & Gamification**: For enhancing user experience and engagement
- **AI Optimization**: For improving AI model usage and prompt engineering
- **Security & Privacy**: For implementing best practices in data protection

These prompts are designed to help you research specific aspects of enhancing and scaling the application.

## Troubleshooting

- **API Key Issues**: If you encounter authentication errors with DeepInfra, verify your API key is correct
- **Model Errors**: If using Ollama, ensure the selected model is downloaded
- **Browser Compatibility**: The 3D game works best in Chrome, Firefox, or Edge

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Three.js for the 3D game engine
- Flask and Flask-CORS for the web framework
- Ollama and DeepInfra for AI capabilities 