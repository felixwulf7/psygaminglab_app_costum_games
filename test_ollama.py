#!/usr/bin/env python3
import requests
import sys
import subprocess
import time
import platform

def check_ollama():
    """Check if Ollama is running and accessible."""
    print("Testing Ollama connection...")
    try:
        response = requests.get("http://localhost:11434/api/version", timeout=5)
        if response.status_code == 200:
            print("✅ Ollama is running!")
            return True
        else:
            print(f"❌ Ollama returned status code {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to Ollama")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def start_ollama():
    """Attempt to start Ollama."""
    print("Attempting to start Ollama...")
    
    system = platform.system()
    if system == "Darwin":  # macOS
        subprocess.Popen(["open", "-a", "Ollama"])
        print("Launched Ollama application")
    elif system == "Windows":
        subprocess.Popen(["start", "Ollama"], shell=True)
        print("Launched Ollama application")
    elif system == "Linux":
        subprocess.Popen(["ollama", "serve"])
        print("Started Ollama service")
    else:
        print(f"Unknown operating system: {system}")
        return False
    
    # Wait for Ollama to start
    for i in range(1, 11):
        print(f"Waiting for Ollama to start... ({i}/10)")
        time.sleep(2)
        if check_ollama():
            return True
    
    return False

def list_models():
    """List available models in Ollama."""
    print("\nChecking available models...")
    try:
        response = requests.get("http://localhost:11434/api/tags")
        if response.status_code == 200:
            models = response.json().get("models", [])
            if models:
                print("Available models:")
                for model in models:
                    print(f"  - {model['name']}")
            else:
                print("No models found. You may need to pull models using 'ollama pull MODEL_NAME'")
                print("Recommended: ollama pull gemma3:4b")
        else:
            print(f"Failed to get models: Status code {response.status_code}")
    except Exception as e:
        print(f"Error listing models: {str(e)}")

def test_generation():
    """Test basic generation with Ollama."""
    models = []
    try:
        response = requests.get("http://localhost:11434/api/tags")
        if response.status_code == 200:
            models = [model["name"] for model in response.json().get("models", [])]
    except:
        pass
    
    if not models:
        print("\nNo models available for testing generation")
        return
    
    model = models[0]  # Use first available model
    print(f"\nTesting generation with model: {model}")
    print("Prompt: 'Generate a positive affirmation for someone feeling anxious'")
    
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": model, "prompt": "Generate a positive affirmation for someone feeling anxious", "stream": False},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("\nGeneration result:")
            print(result.get("response", "No response"))
        else:
            print(f"Generation failed: Status code {response.status_code}")
    except Exception as e:
        print(f"Error during generation: {str(e)}")

if __name__ == "__main__":
    print("Ollama Connection Test Utility")
    print("=============================")
    
    # Check if Ollama is already running
    if not check_ollama():
        # Try to start Ollama
        if not start_ollama():
            print("\n❌ Could not start Ollama automatically")
            print("Please make sure Ollama is installed and start it manually")
            print("Download from: https://ollama.ai/")
            sys.exit(1)
    
    # List available models
    list_models()
    
    # Test generation if models are available
    test_generation()
    
    print("\n✅ Test completed!")
    print("If everything looks good, you can run the dynamic games application:")
    print("  1. Run './start_app.sh' on macOS/Linux or 'start_app.bat' on Windows")
    print("  2. Open your browser to http://localhost:5000") 