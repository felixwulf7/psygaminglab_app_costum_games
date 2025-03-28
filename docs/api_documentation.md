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