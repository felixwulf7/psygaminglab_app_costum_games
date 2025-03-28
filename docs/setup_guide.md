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