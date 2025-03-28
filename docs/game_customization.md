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