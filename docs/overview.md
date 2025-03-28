# PsyGaming Lab App - Technical Overview

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