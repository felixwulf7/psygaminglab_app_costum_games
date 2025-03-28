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
LLM_API_TYPE = "deepinfra"  # Options: "ollama", "deepinfra", "openai", "anthropic"
DEFAULT_MODEL = "meta-llama/Llama-2-70b-chat-hf"  # Default model for DeepInfra
TEMPLATE_GAME_PATH = "templates/3d_shooter_accepting_being_tired.html"  # Local path to template
DEBUG_GAMES_DIR = "debug_games"  # Directory for storing debug copies of generated games
DEEPINFRA_API_KEY = "xXIq1CQzz2C2a3tIycGCZwDBAYjqnB4T"  # Your DeepInfra API key

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

# Generate game content with Ollama
def generate_with_ollama(user_input, model=DEFAULT_MODEL):
    if not check_ollama_running():
        if not start_ollama():
            return {"error": "Ollama is not running and couldn't be started automatically."}
    
    prompt = f"""
    You are an expert in therapeutic game design and cognitive-behavioral therapy.
    You are creating content for a 3D therapeutic game where players shoot positive thoughts (affirmations) at negative thoughts.
    
    The user has shared that they are struggling with: "{user_input}"
    
    You need to create custom content SPECIFICALLY TAILORED to this situation:
    
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
    
    For example:
    - If negative thought with correctAmmo 0 is "I'm worthless because I failed this test", 
      then positive thought #0 should be "My worth is not defined by a single outcome".
    - If negative thought with correctAmmo 1 is "Nobody will ever love me",
      then positive thought #1 should be "I am worthy of love and connection".
    
    Be CERTAIN that each positive thought is a direct, logical counter to its matching negative thought.
    The content must be SPECIFICALLY related to {user_input}, not generic affirmations.
    
    CRITICAL JAVASCRIPT SYNTAX INSTRUCTIONS:
    - The game will BREAK if your JSON is not properly formatted
    - In JavaScript arrays, each element MUST be separated by a comma
    - Comments should NOT have commas in them (use "// Red" not "// Red,")
    - Make sure the JSON structure is valid and follows the exact format specified below
    
    **CORRECT ARRAY SYNTAX EXAMPLE:**
    ```javascript
    const negativeThoughts = [
        {{ text: "First thought", correctAmmo: 0, color: 0xe74c3c }}, // Red
        {{ text: "Second thought", correctAmmo: 1, color: 0x3498db }}, // Blue
        {{ text: "Third thought", correctAmmo: 2, color: 0xf1c40f }}, // Yellow
        {{ text: "Fourth thought", correctAmmo: 3, color: 0x2ecc71 }}, // Green
        {{ text: "Fifth thought", correctAmmo: 4, color: 0x9b59b6 }}  // Purple
    ];
    ```
    
    **INCORRECT ARRAY SYNTAX EXAMPLE (WILL BREAK THE GAME):**
    ```javascript
    const negativeThoughts = [
        {{ text: "First thought", correctAmmo: 0, color: 0xe74c3c }} // Red, <-- COMMA IN COMMENT WILL BREAK THE GAME
        {{ text: "Second thought", correctAmmo: 1, color: 0x3498db }} // Blue <-- MISSING COMMA AFTER OBJECT WILL BREAK THE GAME
    ];
    ```

    Your response must be a valid JSON object with this exact structure:
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
                    parsed_content = json.loads(json_content)
                    
                    # Validate required fields
                    if not all(key in parsed_content for key in ["title", "positiveThoughts", "negativeThoughts"]):
                        missing = [k for k in ["title", "positiveThoughts", "negativeThoughts"] if k not in parsed_content]
                        return {"error": f"Missing required fields in LLM response: {', '.join(missing)}"}
                    
                    # Normalize the negative thoughts to ensure they're in the correct format
                    normalized_negative_thoughts = []
                    for i, thought in enumerate(parsed_content["negativeThoughts"]):
                        if isinstance(thought, dict) and "text" in thought:
                            # Ensure correctAmmo is present and an integer
                            if "correctAmmo" not in thought or not isinstance(thought["correctAmmo"], int):
                                thought["correctAmmo"] = i
                            normalized_negative_thoughts.append(thought)
                        elif isinstance(thought, str):
                            # Convert string to proper format
                            normalized_negative_thoughts.append({"text": thought, "correctAmmo": i})
                        else:
                            # Handle unexpected format
                            normalized_negative_thoughts.append({"text": str(thought), "correctAmmo": i})
                    
                    parsed_content["negativeThoughts"] = normalized_negative_thoughts
                    return parsed_content
                except json.JSONDecodeError:
                    # Try to extract partial content using regex if full JSON parsing fails
                    try:
                        title_match = re.search(r'"title"\s*:\s*"([^"]+)"', content)
                        title = title_match.group(1) if title_match else "Custom Game"
                        
                        # Extract positive thoughts
                        pos_thoughts = []
                        pos_pattern = r'"positiveThoughts"\s*:\s*\[\s*"([^"]+)"(?:\s*,\s*"([^"]+)")?(?:\s*,\s*"([^"]+)")?(?:\s*,\s*"([^"]+)")?(?:\s*,\s*"([^"]+)")?\s*\]'
                        pos_match = re.search(pos_pattern, content, re.DOTALL)
                        if pos_match:
                            pos_thoughts = [g for g in pos_match.groups() if g]
                        
                        # If we couldn't find any, try alternate pattern
                        if not pos_thoughts:
                            alt_pos = re.findall(r'"text"\s*:\s*"([^"]+)"', content)
                            pos_thoughts = alt_pos[:5] if alt_pos else ["Stay positive", "You can do this", "Believe in yourself", "Keep going", "You are worthy"]
                        
                        # Extract negative thoughts - try to get structured data first
                        neg_pattern = r'"negativeThoughts"\s*:\s*\[(.*?)\]'
                        neg_match = re.search(neg_pattern, content, re.DOTALL)
                        neg_thoughts = []
                        
                        if neg_match:
                            neg_text = neg_match.group(1)
                            # Try to extract properly formatted objects
                            neg_obj_pattern = r'\{\s*"text"\s*:\s*"([^"]+)"\s*,\s*"correctAmmo"\s*:\s*(\d+)\s*\}'
                            neg_objs = re.findall(neg_obj_pattern, neg_text)
                            
                            for i, (text, ammo) in enumerate(neg_objs):
                                neg_thoughts.append({"text": text, "correctAmmo": int(ammo)})
                        
                        # If we couldn't find structured negative thoughts, try to extract just text patterns
                        if not neg_thoughts:
                            neg_text_pattern = r'"text"\s*:\s*"([^"]+)"'
                            neg_texts = re.findall(neg_text_pattern, content)
                            for i, text in enumerate(neg_texts[:5]):
                                neg_thoughts.append({"text": text, "correctAmmo": i})
                        
                        # If still no negative thoughts, create default ones based on positive thoughts
                        if not neg_thoughts:
                            for i, pos in enumerate(pos_thoughts[:5]):
                                neg_thoughts.append({"text": f"Negative version of: {pos}", "correctAmmo": i})
                        
                        # Ensure we have exactly 5 of each
                        while len(pos_thoughts) < 5:
                            pos_thoughts.append(f"Positive thought {len(pos_thoughts)+1}")
                        while len(neg_thoughts) < 5:
                            neg_thoughts.append({"text": f"Negative thought {len(neg_thoughts)+1}", "correctAmmo": len(neg_thoughts)})
                        
                        return {
                            "title": title,
                            "positiveThoughts": pos_thoughts[:5],
                            "negativeThoughts": neg_thoughts[:5]
                        }
                    except Exception as regex_error:
                        return {"error": f"Failed to parse JSON and regex extraction failed: {str(regex_error)}"}
            else:
                return {"error": "No valid JSON found in LLM response"}
        else:
            return {"error": f"Ollama API returned status code {response.status_code}"}
    except Exception as e:
        return {"error": f"Error connecting to Ollama API: {str(e)}"}

# Generate game content with DeepInfra
def generate_with_deepinfra(user_input, model=DEFAULT_MODEL):
    prompt = f"""
    You are an expert in therapeutic game design and cognitive-behavioral therapy.
    You are creating content for a 3D therapeutic game where players shoot positive thoughts (affirmations) at negative thoughts.
    
    The user has shared that they are struggling with: "{user_input}"
    
    You need to create custom content SPECIFICALLY TAILORED to this situation:
    
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
    
    For example:
    - If negative thought with correctAmmo 0 is "I'm worthless because I failed this test", 
      then positive thought #0 should be "My worth is not defined by a single outcome".
    - If negative thought with correctAmmo 1 is "Nobody will ever love me",
      then positive thought #1 should be "I am worthy of love and connection".
    
    Be CERTAIN that each positive thought is a direct, logical counter to its matching negative thought.
    The content must be SPECIFICALLY related to {user_input}, not generic affirmations.
    
    CRITICAL JAVASCRIPT SYNTAX INSTRUCTIONS:
    - The game will BREAK if your JSON is not properly formatted
    - In JavaScript arrays, each element MUST be separated by a comma
    - Comments should NOT have commas in them (use "// Red" not "// Red,")
    - Make sure the JSON structure is valid and follows the exact format specified below
    
    **CORRECT ARRAY SYNTAX EXAMPLE:**
    ```javascript
    const negativeThoughts = [
        {{ text: "First thought", correctAmmo: 0, color: 0xe74c3c }}, // Red
        {{ text: "Second thought", correctAmmo: 1, color: 0x3498db }}, // Blue
        {{ text: "Third thought", correctAmmo: 2, color: 0xf1c40f }}, // Yellow
        {{ text: "Fourth thought", correctAmmo: 3, color: 0x2ecc71 }}, // Green
        {{ text: "Fifth thought", correctAmmo: 4, color: 0x9b59b6 }}  // Purple
    ];
    ```
    
    **INCORRECT ARRAY SYNTAX EXAMPLE (WILL BREAK THE GAME):**
    ```javascript
    const negativeThoughts = [
        {{ text: "First thought", correctAmmo: 0, color: 0xe74c3c }} // Red, <-- COMMA IN COMMENT WILL BREAK THE GAME
        {{ text: "Second thought", correctAmmo: 1, color: 0x3498db }} // Blue <-- MISSING COMMA AFTER OBJECT WILL BREAK THE GAME
    ];
    ```

    Your response must be a valid JSON object with this exact structure:
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
        print(f"Sending request to DeepInfra API for model: {model}")
        response = requests.post(
            f"https://api.deepinfra.com/v1/inference/{model}",
            headers={
                "Authorization": f"Bearer {DEEPINFRA_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "input": prompt,
                "max_tokens": 2000,
                "temperature": 0.7
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            # The response format differs between models
            if "generated_text" in result:
                content = result.get("generated_text", "")
            elif "results" in result:
                content = result.get("results", [{}])[0].get("generated_text", "")
            else:
                print(f"Unexpected response format: {result}")
                content = str(result)
                
            print(f"DeepInfra response received: {len(content)} characters")
            
            # Find JSON content
            start_idx = content.find('{')
            end_idx = content.rfind('}') + 1
            
            if start_idx >= 0 and end_idx > start_idx:
                json_content = content[start_idx:end_idx]
                try:
                    parsed_content = json.loads(json_content)
                    print(f"Successfully parsed JSON from DeepInfra response")
                    
                    # Validate required fields
                    if not all(k in parsed_content for k in ["title", "positiveThoughts", "negativeThoughts"]):
                        print("Error: Missing required fields in JSON response")
                        print(f"Available keys: {list(parsed_content.keys())}")
                        return None
                    
                    return parsed_content
                except json.JSONDecodeError as e:
                    print(f"Error decoding JSON from DeepInfra response: {e}")
                    print(f"JSON content attempted to parse: {json_content}")
                    
                    # Last resort: Try to extract content manually using regex
                    title_match = re.search(r'"title":\s*"([^"]+)"', json_content)
                    title = title_match.group(1) if title_match else "Generated Game"
                    
                    # Extract positive thoughts
                    positive_thoughts = []
                    pos_matches = re.findall(r'"positiveThoughts":\s*\[\s*"([^"]+)"', json_content)
                    if pos_matches:
                        positive_thoughts.append(pos_matches[0])
                        pos_matches = re.findall(r'"([^"]+)"', json_content[json_content.find(pos_matches[0])+len(pos_matches[0]):json_content.find("negativeThoughts")])
                        positive_thoughts.extend(pos_matches[:4])  # Get up to 4 more matches
                    
                    # Ensure we have 5 positive thoughts
                    while len(positive_thoughts) < 5:
                        positive_thoughts.append(f"Positive thought #{len(positive_thoughts)}")
                    
                    # Extract negative thoughts
                    negative_thoughts = []
                    neg_matches = re.findall(r'"text":\s*"([^"]+)",\s*"correctAmmo":\s*(\d+)', json_content)
                    for text, ammo in neg_matches[:5]:
                        negative_thoughts.append({"text": text, "correctAmmo": int(ammo)})
                    
                    # Ensure we have 5 negative thoughts
                    for i in range(len(negative_thoughts), 5):
                        negative_thoughts.append({"text": f"Negative thought #{i}", "correctAmmo": i})
                    
                    manual_extract = {
                        "title": title,
                        "positiveThoughts": positive_thoughts,
                        "negativeThoughts": negative_thoughts
                    }
                    
                    print(f"Created content through manual extraction: {manual_extract}")
                    return manual_extract
            else:
                print("No JSON content found in DeepInfra response")
                print(f"Response content: {content}")
                return None
        else:
            print(f"DeepInfra API error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Error generating content with DeepInfra: {str(e)}")
        return None

# Validate the game HTML for common syntax errors
def validate_game_html(html_content):
    """
    Check the game HTML for common JavaScript syntax errors.
    Returns (is_valid, error_message)
    """
    # Check for proper array syntax in negativeThoughts
    negative_thoughts_match = re.search(r'const\s+negativeThoughts\s*=\s*\[(.*?)\];', html_content, re.DOTALL)
    if negative_thoughts_match:
        negative_thoughts = negative_thoughts_match.group(1)
        # Count opening braces
        opening_braces = negative_thoughts.count('{')
        # Count commas that are correctly placed between array items
        commas = len(re.findall(r'}\s*,', negative_thoughts))
        
        # Look for commas inside comments (incorrect) 
        comment_commas = len(re.findall(r'//.*?,', negative_thoughts))
        if comment_commas > 0:
            return False, f"Found {comment_commas} commas in comments in negativeThoughts array. Comments should not contain commas."
        
        if opening_braces - commas != 1:
            return False, f"Syntax error in negativeThoughts array: expected {opening_braces-1} commas between items, found {commas}"
    
    # Check for proper array syntax in positiveResources
    positive_resources_match = re.search(r'const\s+positiveResources\s*=\s*\[(.*?)\];', html_content, re.DOTALL)
    if positive_resources_match:
        positive_resources = positive_resources_match.group(1)
        # Count opening braces
        opening_braces = positive_resources.count('{')
        # Count commas that are correctly placed between array items
        commas = len(re.findall(r'}\s*,', positive_resources))
        
        # Look for commas inside comments (incorrect)
        comment_commas = len(re.findall(r'//.*?,', positive_resources))
        if comment_commas > 0:
            return False, f"Found {comment_commas} commas in comments in positiveResources array. Comments should not contain commas."
        
        if opening_braces - commas != 1:
            return False, f"Syntax error in positiveResources array: expected {opening_braces-1} commas between items, found {commas}"
    
    return True, ""

# Generate game HTML based on user input
def create_custom_game(user_input, model=DEFAULT_MODEL):
    # Generate content with appropriate LLM backend
    print(f"Generating game content for user input: '{user_input}' using model: {model}")
    
    if LLM_API_TYPE == "ollama":
        content = generate_with_ollama(user_input, model)
    elif LLM_API_TYPE == "deepinfra":
        content = generate_with_deepinfra(user_input, model)
    else:
        print(f"Unsupported LLM API type: {LLM_API_TYPE}")
        return {"error": f"Unsupported LLM API type: {LLM_API_TYPE}"}
    
    if content is None:
        return {"error": "Failed to generate content"}
    
    if "error" in content:
        print(f"Error generating content: {content['error']}")
        return {"error": content['error']}
    
    # Print the generated content for debugging
    print("\n===== GENERATED CONTENT =====")
    print(f"Title: {content.get('title', 'No title generated')}")
    print("\nPositive Thoughts:")
    for i, thought in enumerate(content.get('positiveThoughts', [])):
        print(f"{i}: {thought}")
    
    print("\nNegative Thoughts:")
    for i, thought in enumerate(content.get('negativeThoughts', [])):
        # Add type checking to avoid string indices error
        if isinstance(thought, dict) and 'text' in thought and 'correctAmmo' in thought:
            print(f"{i}: {thought['text']} (correctAmmo: {thought['correctAmmo']})")
        else:
            print(f"{i}: {thought} (Format error: not a properly formatted object)")
    print("============================\n")
    
    # Read the template file
    try:
        with open(TEMPLATE_GAME_PATH, 'r', encoding='utf-8') as file:
            template = file.read()
        
        # Replace the title in all locations (HTML title, info div, and gameMenu h1)
        if "title" in content:
            template = template.replace("<title>Energy Wisdom: Embracing Your Natural Rhythms</title>", 
                                     f"<title>{content['title']}</title>")
            template = template.replace('<div id="info">Energy Wisdom: Embracing Your Natural Rhythms</div>', 
                                     f'<div id="info">{content["title"]}</div>')
            template = template.replace('<h1>Energy Wisdom: Embracing Your Natural Rhythms</h1>', 
                                     f'<h1>{content["title"]}</h1>')
        
        # Replace positive thoughts (ammo types) in the HTML
        if "positiveThoughts" in content and len(content["positiveThoughts"]) >= 5:
            for i, thought in enumerate(content["positiveThoughts"][:5]):
                original_thought = ""
                if i == 0:
                    original_thought = "My tiredness is a valid message from my body."
                elif i == 1:
                    original_thought = "Rest is a necessary part of being productive."
                elif i == 2:
                    original_thought = "I deserve the same compassion I'd offer others."
                elif i == 3:
                    original_thought = "My worth isn't measured by my energy or output."
                elif i == 4:
                    original_thought = "Working with my energy, not against it, is wisdom."
                
                template = template.replace(
                    f'&#9755; "{original_thought}"',
                    f'&#9755; "{thought}"'
                )
        
        # Replace the game description paragraphs with user-specific content
        game_description = f"""
        <p>Transform self-judgmental thoughts about {user_input} into self-compassion.</p>
        <p>Learn to recognize and challenge negative thoughts related to {user_input}.</p>
        <p>Use WASD to move, SPACE to jump, MOUSE to aim, and LEFT CLICK to shoot.</p>
        <p>Select different wisdom perspectives with 1-5 keys or click on them.</p>
        <p>Match each negative thought with its compassionate counterpart.</p>
        <p>Navigate through obstacles toward greater self-acceptance!</p>
        """
        
        # Replace the description text
        template = template.replace("""
        <p>Transform self-judgmental thoughts about tiredness into self-compassion.</p>
        <p>Learn to honor your body's signals and release the pressure of constant productivity.</p>
        <p>Use WASD to move, SPACE to jump, MOUSE to aim, and LEFT CLICK to shoot.</p>
        <p>Select different wisdom perspectives with 1-5 keys or click on them.</p>
        <p>Match each pressure-filled thought with its compassionate counterpart.</p>
        <p>Navigate through obstacles toward greater self-acceptance!</p>
        """, game_description)
        
        # Replace JavaScript arrays for negative thoughts and positive resources
        if "positiveThoughts" in content and "negativeThoughts" in content:
            # Create the positive resources array string
            positive_resources_str = "        const positiveResources = [\n"
            for i, thought in enumerate(content["positiveThoughts"][:5]):
                # Use original colors to maintain the visual design
                color_code = ""
                if i == 0:
                    color_code = "0xc0392b" # Dark red
                elif i == 1:
                    color_code = "0x2980b9" # Dark blue
                elif i == 2:
                    color_code = "0x8e44ad" # Dark purple
                elif i == 3:
                    color_code = "0x27ae60" # Dark green
                elif i == 4:
                    color_code = "0xf39c12" # Dark orange
                
                positive_resources_str += f'            {{ text: "{thought}", color: {color_code} }}'
                # Add comment based on color
                if i == 0:
                    positive_resources_str += " // Dark red"
                elif i == 1:
                    positive_resources_str += " // Dark blue"
                elif i == 2:
                    positive_resources_str += " // Dark purple" 
                elif i == 3:
                    positive_resources_str += " // Dark green"
                elif i == 4:
                    positive_resources_str += " // Dark orange"
                # Add comma if not the last item
                if i < 4:
                    positive_resources_str += ","
                positive_resources_str += "\n"
            positive_resources_str += "        ];"
            
            # Replace positive resources array
            template = template.replace("""        const positiveResources = [
            { text: "My tiredness is a valid message from my body", color: 0xc0392b }, // Dark red
            { text: "Rest is a necessary part of being productive", color: 0x2980b9 }, // Dark blue
            { text: "I deserve the same compassion I'd offer others", color: 0x8e44ad }, // Dark purple
            { text: "My worth isn't measured by my energy or output", color: 0x27ae60 }, // Dark green
            { text: "Working with my energy, not against it, is wisdom", color: 0xf39c12 } // Dark orange
        ];""", positive_resources_str)
            
            # Create negative thoughts array string
            negative_thoughts_str = "        const negativeThoughts = [\n"
            
            # Find color codes for negative thoughts
            color_codes = ["0xe74c3c", "0x3498db", "0xf1c40f", "0x2ecc71", "0x9b59b6"]
            color_comments = ["// Red", "// Blue", "// Yellow", "// Green", "// Purple"]
            
            for i, thought in enumerate(content["negativeThoughts"][:5]):
                # Add type checking to handle both string and dict type thoughts
                if isinstance(thought, dict) and 'text' in thought and 'correctAmmo' in thought:
                    thought_text = thought["text"]
                    correct_ammo = thought["correctAmmo"]
                else:
                    # If it's a string or improperly formatted, use the string as text and default correctAmmo
                    thought_text = str(thought)
                    correct_ammo = i  # Default to index as correctAmmo
                
                negative_thoughts_str += f'            {{ text: "{thought_text}", correctAmmo: {correct_ammo}, color: {color_codes[i]} }}'
                # Add color comment
                if color_comments[i]:
                    negative_thoughts_str += f" {color_comments[i]}"
                # Add comma if not the last item
                if i < 4:
                    negative_thoughts_str += ","
                negative_thoughts_str += "\n"
            negative_thoughts_str += "        ];"
            
            # Replace negative thoughts array
            template = template.replace("""        // Negative thoughts and their corresponding positive resources (tiredness-focused)
        const negativeThoughts = [
            { text: "I should be ashamed of being tired all the time", correctAmmo: 2, color: 0xe74c3c }, // Red
            { text: "Taking breaks means I'm lazy and unproductive", correctAmmo: 1, color: 0x3498db }, // Blue
            { text: "I need to push through my tiredness to be worthy", correctAmmo: 3, color: 0xf1c40f }, // Yellow
            { text: "My body is weak for needing so much rest", correctAmmo: 0, color: 0x2ecc71 }, // Green
            { text: "I must force myself to maintain high energy", correctAmmo: 4, color: 0x9b59b6 }  // Purple
        ];""", "        // Negative thoughts and their corresponding positive resources\n" + negative_thoughts_str)
        
        # Save the custom game to the static directory (for serving)
        game_filename = f"custom_game_{int(time.time())}.html"
        game_path = os.path.join("static", game_filename)
        
        os.makedirs(os.path.dirname(game_path), exist_ok=True)
        
        # Validate the generated HTML for syntax errors
        is_valid, error_message = validate_game_html(template)
        if not is_valid:
            print(f"WARNING: Potential syntax error detected: {error_message}")
            print("Attempting to fix common issues...")
            
            # Fix common issues with commas in arrays
            
            # 1. Remove commas from comments - replace "// Red," with "// Red"
            template = re.sub(r'(//[^,\n]*),([^,\n]*\n)', r'\1\2', template)
            
            # 2. Add missing commas between array elements
            template = re.sub(r'(}\s*//.*?\n\s*)(\{)', r'}, \n        \2', template)
            
            # 3. Fix last array element (shouldn't have comma)
            template = re.sub(r'},(\s*//.*?\n\s*])', r'}\1', template)
            
            # Revalidate after fixes
            is_valid, error_message = validate_game_html(template)
            if not is_valid:
                print(f"Still found potential issues: {error_message}")
                print("The game may not function correctly. Manual review recommended.")
                
                # Last resort fix: completely regenerate arrays
                # This takes the generated content but applies our own formatting to ensure correct syntax
                if "negativeThoughts" in content and "positiveThoughts" in content:
                    print("Applying last-resort fix: Regenerating arrays with correct syntax")
                    
                    # Create negative thoughts array with proper syntax
                    neg_array = "        const negativeThoughts = [\n"
                    for i, thought in enumerate(content["negativeThoughts"]):
                        color_code = ["0xe74c3c", "0x3498db", "0xf1c40f", "0x2ecc71", "0x9b59b6"][i]
                        color_comment = ["// Red", "// Blue", "// Yellow", "// Green", "// Purple"][i]
                        ending = ",\n" if i < 4 else "\n"
                        
                        # Add type checking to handle both string and dict type thoughts
                        if isinstance(thought, dict) and 'text' in thought and 'correctAmmo' in thought:
                            thought_text = thought["text"]
                            correct_ammo = thought["correctAmmo"]
                        else:
                            # If it's a string or improperly formatted, use the string as text and default correctAmmo
                            thought_text = str(thought)
                            correct_ammo = i  # Default to index as correctAmmo
                        
                        neg_array += f'            {{ text: "{thought_text}", correctAmmo: {correct_ammo}, color: {color_code} }} {color_comment}{ending}'
                    neg_array += "        ];"
                    
                    # Create positive resources array with proper syntax
                    pos_array = "        const positiveResources = [\n"
                    for i, thought in enumerate(content["positiveThoughts"]):
                        color_code = ["0xc0392b", "0x2980b9", "0x8e44ad", "0x27ae60", "0xf39c12"][i]
                        color_comment = ["// Dark red", "// Dark blue", "// Dark purple", "// Dark green", "// Dark orange"][i]
                        ending = ",\n" if i < 4 else "\n"
                        pos_array += f'            {{ text: "{thought}", color: {color_code} }} {color_comment}{ending}'
                    pos_array += "        ];"
                    
                    # Replace both arrays in the template
                    template = re.sub(r'const\s+negativeThoughts\s*=\s*\[.*?\];', neg_array, template, flags=re.DOTALL)
                    template = re.sub(r'const\s+positiveResources\s*=\s*\[.*?\];', pos_array, template, flags=re.DOTALL)
                    
                    print("Arrays regenerated with correct syntax")
        
        with open(game_path, 'w', encoding='utf-8') as file:
            file.write(template)
        
        # Save a copy to the debug directory (for analysis)
        debug_filename = f"debug_{game_filename}"
        debug_path = os.path.join(DEBUG_GAMES_DIR, debug_filename)
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
    if LLM_API_TYPE == "ollama":
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
    elif LLM_API_TYPE == "deepinfra":
        # For DeepInfra, we'll return a fixed list of available models
        models = [
            "mistralai/Mixtral-8x7B-Instruct-v0.1",
            "meta-llama/Llama-2-70b-chat-hf",
            "microsoft/phi-2"
        ]
        return jsonify({"models": models})
    else:
        return jsonify({"error": f"Unsupported LLM API type: {LLM_API_TYPE}"}), 500

if __name__ == '__main__':
    # Create static directory if it doesn't exist
    os.makedirs('static', exist_ok=True)
    
    # Create debug games directory if it doesn't exist
    os.makedirs(DEBUG_GAMES_DIR, exist_ok=True)
    print(f"Debug games will be saved to: {os.path.abspath(DEBUG_GAMES_DIR)}")
    
    # Check API configuration
    if LLM_API_TYPE == "deepinfra":
        if not DEEPINFRA_API_KEY:
            print("WARNING: DeepInfra API key not set. Please set DEEPINFRA_API_KEY in the code or environment.")
        else:
            print(f"Using DeepInfra API with model: {DEFAULT_MODEL}")
    elif LLM_API_TYPE == "ollama":
        # Check if Ollama is installed and running
        if not check_ollama_running():
            print("Ollama is not running. Trying to start it...")
            if not start_ollama():
                print("WARNING: Ollama is not running. Please start it manually.")
    
    # Start the server
    print("Starting server on http://localhost:5002")
    app.run(debug=True, port=5002) 
