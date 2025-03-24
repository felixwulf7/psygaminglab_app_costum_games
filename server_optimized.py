import os
import json
import requests
import re
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import subprocess
import sys
import time
import shutil

app = Flask(__name__, static_folder='static')
CORS(app)  # Allow cross-origin requests

# Configuration
LLM_API_TYPE = "ollama"  # Options: "ollama", "openai", "anthropic"
DEFAULT_MODEL = "gemma3:4b"  # Default model for Ollama
TEMPLATE_GAME_PATH = "../Deepresearch_development_dynamic_games/game_3d_shooter/3d_shooter_accepting_being_tired.html"
DEBUG_GAMES_DIR = "debug_games"  # Directory for storing debug copies of generated games

# Check if Ollama is running
def check_ollama_running():
    try:
        response = requests.get("http://localhost:11434/api/version")
        return response.status_code == 200
    except:
        return False

# Start Ollama if not running
def start_ollama():
    print("Starting Ollama...")
    try:
        if sys.platform == "darwin":  # macOS
            subprocess.Popen(["open", "-a", "Ollama"])
        elif sys.platform == "win32":  # Windows
            subprocess.Popen(["start", "Ollama"], shell=True)
        else:  # Linux
            subprocess.Popen(["ollama", "serve"])
        
        # Wait for Ollama to start
        for _ in range(10):
            if check_ollama_running():
                print("Ollama started successfully")
                return True
            time.sleep(2)
        
        print("Failed to start Ollama automatically")
        return False
    except Exception as e:
        print(f"Error starting Ollama: {e}")
        return False

# Generate only the custom content with Ollama (title, thoughts)
def generate_content_with_ollama(user_input, model=DEFAULT_MODEL):
    if not check_ollama_running():
        if not start_ollama():
            return {"error": "Ollama is not running and couldn't be started automatically."}
    
    prompt = f"""
    You are an expert in therapeutic game design and cognitive-behavioral therapy.
    You are creating content for a 3D therapeutic game where players shoot positive thoughts (affirmations) at negative thoughts.
    
    The user has shared that they are struggling with: "{user_input}"
    
    Create custom content SPECIFICALLY TAILORED to this situation:
    
    1. Create a meaningful title for the game that directly relates to {user_input}
    2. Create 5 positive affirmations/thoughts that would help someone dealing with {user_input}
    3. Create 5 corresponding negative thoughts that someone struggling with {user_input} might experience
    
    **VERY IMPORTANT INSTRUCTION**: Each positive thought must DIRECTLY counter a specific negative thought.
    The game mechanics REQUIRE that:
    - Positive thought #0 should counter negative thought with correctAmmo: 0
    - Positive thought #1 should counter negative thought with correctAmmo: 1
    - Positive thought #2 should counter negative thought with correctAmmo: 2
    - Positive thought #3 should counter negative thought with correctAmmo: 3
    - Positive thought #4 should counter negative thought with correctAmmo: 4
    
    Your response MUST be a valid JSON object with this exact structure:
    {{
        "title": "Game Title: Subtitle",
        "positiveThoughts": ["positive1", "positive2", "positive3", "positive4", "positive5"],
        "negativeThoughts": [
            {{"text": "negative1", "correctAmmo": 0}},
            {{"text": "negative2", "correctAmmo": 1}},
            {{"text": "negative3", "correctAmmo": 2}},
            {{"text": "negative4", "correctAmmo": 3}},
            {{"text": "negative5", "correctAmmo": 4}}
        ]
    }}
    
    Make all thoughts concise (under 10 words if possible), impactful, and therapeutically sound.
    Each thought should be highly specific to the user's situation about {user_input}.
    Return only the JSON object without any additional text.
    """
    
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": model, "prompt": prompt, "stream": False}
        )
        
        if response.status_code == 200:
            result = response.json()
            # Try to extract valid JSON from the response
            content = result.get("response", "")
            
            # Find JSON content
            start_idx = content.find('{')
            end_idx = content.rfind('}') + 1
            
            if start_idx >= 0 and end_idx > start_idx:
                json_content = content[start_idx:end_idx]
                try:
                    return json.loads(json_content)
                except json.JSONDecodeError:
                    return {"error": "Failed to parse JSON from LLM response"}
            else:
                return {"error": "No valid JSON found in LLM response"}
        else:
            return {"error": f"Ollama API returned status code {response.status_code}"}
    except Exception as e:
        return {"error": f"Error connecting to Ollama API: {str(e)}"}

# Create custom game by replacing specific elements in the template
def create_custom_game(user_input, model=DEFAULT_MODEL):
    # Generate content with LLM
    print(f"Generating game content for user input: '{user_input}' using model: {model}")
    content = generate_content_with_ollama(user_input, model)
    
    if "error" in content:
        print(f"Error generating content: {content['error']}")
        return {"error": content["error"]}
    
    # Print the generated content for debugging
    print("\n===== GENERATED CONTENT =====")
    print(f"Title: {content.get('title', 'No title generated')}")
    print("\nPositive Thoughts:")
    for i, thought in enumerate(content.get('positiveThoughts', [])):
        print(f"{i}: {thought}")
    
    print("\nNegative Thoughts:")
    for i, thought in enumerate(content.get('negativeThoughts', [])):
        print(f"{i}: {thought['text']} (correctAmmo: {thought['correctAmmo']})")
    print("============================\n")
    
    # Read the template file
    try:
        with open(TEMPLATE_GAME_PATH, 'r', encoding='utf-8') as file:
            template = file.read()
        
        # Step 1: Extract template elements
        # These are the only arrays we need to modify directly rather than doing complex string replacements
        positiveResources_template = [
            { "text": "My tiredness is a valid message from my body", "color": "0xc0392b" },
            { "text": "Rest is a necessary part of being productive", "color": "0x2980b9" },
            { "text": "I deserve the same compassion I'd offer others", "color": "0x8e44ad" },
            { "text": "My worth isn't measured by my energy or output", "color": "0x27ae60" },
            { "text": "Working with my energy, not against it, is wisdom", "color": "0xf39c12" }
        ]
        
        negativeThoughts_template = [
            { "text": "I should be ashamed of being tired all the time", "correctAmmo": 2, "color": "0xe74c3c" },
            { "text": "Taking breaks means I'm lazy and unproductive", "correctAmmo": 1, "color": "0x3498db" },
            { "text": "I need to push through my tiredness to be worthy", "correctAmmo": 3, "color": "0xf1c40f" },
            { "text": "My body is weak for needing so much rest", "correctAmmo": 0, "color": "0x2ecc71" },
            { "text": "I must force myself to maintain high energy", "correctAmmo": 4, "color": "0x9b59b6" }
        ]
        
        # Step 2: Replace the title in three locations
        if "title" in content:
            template = template.replace("<title>Energy Wisdom: Embracing Your Natural Rhythms</title>", 
                                     f"<title>{content['title']}</title>")
            template = template.replace('<div id="info">Energy Wisdom: Embracing Your Natural Rhythms</div>', 
                                     f'<div id="info">{content["title"]}</div>')
            template = template.replace('<h1>Energy Wisdom: Embracing Your Natural Rhythms</h1>', 
                                     f'<h1>{content["title"]}</h1>')
        
        # Step 3: Replace the game description paragraphs
        game_description = f"""
        <p>Transform self-judgmental thoughts about {user_input} into self-compassion.</p>
        <p>Learn to recognize and challenge negative thoughts related to {user_input}.</p>
        <p>Use WASD to move, SPACE to jump, MOUSE to aim, and LEFT CLICK to shoot.</p>
        <p>Select different wisdom perspectives with 1-5 keys or click on them.</p>
        <p>Match each negative thought with its compassionate counterpart.</p>
        <p>Navigate through obstacles toward greater self-acceptance!</p>
        """
        
        # Replace the description section
        template = template.replace("""
        <p>Transform self-judgmental thoughts about tiredness into self-compassion.</p>
        <p>Learn to honor your body's signals and release the pressure of constant productivity.</p>
        <p>Use WASD to move, SPACE to jump, MOUSE to aim, and LEFT CLICK to shoot.</p>
        <p>Select different wisdom perspectives with 1-5 keys or click on them.</p>
        <p>Match each pressure-filled thought with its compassionate counterpart.</p>
        <p>Navigate through obstacles toward greater self-acceptance!</p>
        """, game_description)
        
        # Step 4: Replace positive thoughts in ammo selector 
        if "positiveThoughts" in content and len(content["positiveThoughts"]) >= 5:
            for i, thought in enumerate(content["positiveThoughts"][:5]):
                original_thought = positiveResources_template[i]["text"]
                template = template.replace(
                    f'&#9755; "{original_thought}"',
                    f'&#9755; "{thought}"'
                )
        
        # Step 5: Build JavaScript arrays directly with proper syntax
        if "positiveThoughts" in content and "negativeThoughts" in content:
            # Create arrays with our own formatting to ensure correct JavaScript syntax
            color_codes_positive = ["0xc0392b", "0x2980b9", "0x8e44ad", "0x27ae60", "0xf39c12"]
            color_comments_positive = ["// Dark red", "// Dark blue", "// Dark purple", "// Dark green", "// Dark orange"]
            
            positive_resources_str = "        const positiveResources = [\n"
            for i, thought in enumerate(content["positiveThoughts"][:5]):
                positive_resources_str += f'            {{ text: "{thought}", color: {color_codes_positive[i]} }}'
                positive_resources_str += f" {color_comments_positive[i]}"
                # Add comma if not the last item
                if i < 4:
                    positive_resources_str += ","
                positive_resources_str += "\n"
            positive_resources_str += "        ];"
            
            color_codes_negative = ["0xe74c3c", "0x3498db", "0xf1c40f", "0x2ecc71", "0x9b59b6"]
            color_comments_negative = ["// Red", "// Blue", "// Yellow", "// Green", "// Purple"]
            
            negative_thoughts_str = "        const negativeThoughts = [\n"
            for i, thought in enumerate(content["negativeThoughts"][:5]):
                negative_thoughts_str += f'            {{ text: "{thought["text"]}", correctAmmo: {thought["correctAmmo"]}, color: {color_codes_negative[i]} }}'
                negative_thoughts_str += f" {color_comments_negative[i]}"
                # Add comma if not the last item
                if i < 4:
                    negative_thoughts_str += ","
                negative_thoughts_str += "\n"
            negative_thoughts_str += "        ];"
            
            # Replace the arrays in the template using regex for precise targeting
            template = re.sub(
                r'const\s+positiveResources\s*=\s*\[[\s\S]*?\];',
                positive_resources_str,
                template
            )
            
            template = re.sub(
                r'const\s+negativeThoughts\s*=\s*\[[\s\S]*?\];',
                negative_thoughts_str,
                template
            )
        
        # Save the custom game to the static directory (for serving)
        game_filename = f"custom_game_{int(time.time())}.html"
        game_path = os.path.join("static", game_filename)
        
        os.makedirs(os.path.dirname(game_path), exist_ok=True)
        
        with open(game_path, 'w', encoding='utf-8') as file:
            file.write(template)
        
        # Save a copy to the debug directory (for analysis)
        debug_filename = f"debug_{game_filename}"
        debug_path = os.path.join(DEBUG_GAMES_DIR, debug_filename)
        os.makedirs(os.path.dirname(debug_path), exist_ok=True)
        shutil.copy(game_path, debug_path)
        
        print(f"\n===== GAME CREATED =====")
        print(f"Game file created at: {os.path.abspath(game_path)}")
        print(f"Debug copy saved at: {os.path.abspath(debug_path)}")
        print(f"Access URL: /game/{game_filename}")
        print("=======================\n")
        
        return {
            "filename": game_filename,
            "url": f"/game/{game_filename}"
        }
    
    except Exception as e:
        print(f"Error creating custom game: {str(e)}")
        return {"error": f"Error creating custom game: {str(e)}"}

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/api/create-game', methods=['POST'])
def api_create_game():
    data = request.json
    user_input = data.get('userInput', '')
    model = data.get('model', DEFAULT_MODEL)
    
    if not user_input:
        return jsonify({"error": "No input provided"}), 400
    
    result = create_custom_game(user_input, model)
    if "error" in result:
        return jsonify(result), 500
    
    return jsonify(result)

@app.route('/game/<filename>')
def serve_game(filename):
    return send_from_directory('static', filename)

@app.route('/api/models')
def get_models():
    # Check if Ollama is running
    if not check_ollama_running():
        if not start_ollama():
            return jsonify({"error": "Ollama is not running and couldn't be started"}), 500
    
    try:
        response = requests.get("http://localhost:11434/api/tags")
        if response.status_code == 200:
            models = response.json().get("models", [])
            return jsonify({"models": [model["name"] for model in models]})
        else:
            return jsonify({"error": "Failed to get models from Ollama"}), 500
    except Exception as e:
        return jsonify({"error": f"Error connecting to Ollama: {str(e)}"}), 500

if __name__ == '__main__':
    # Create static directory if it doesn't exist
    os.makedirs('static', exist_ok=True)
    
    # Create debug games directory if it doesn't exist
    os.makedirs(DEBUG_GAMES_DIR, exist_ok=True)
    print(f"Debug games will be saved to: {os.path.abspath(DEBUG_GAMES_DIR)}")
    
    # Check if Ollama is installed and running
    if not check_ollama_running():
        print("Ollama is not running. Trying to start it...")
        if not start_ollama():
            print("WARNING: Ollama is not running. Please start it manually.")
    
    # Start the server
    print("Starting server on http://localhost:5000")
    app.run(debug=True, port=5000) 