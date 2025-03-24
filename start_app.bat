@echo off
TITLE Dynamic Therapeutic Games Launcher

:: Configuration
set API_TYPE=deepinfra
set DEEPINFRA_API_KEY=xXIq1CQzz2C2a3tIycGCZwDBAYjqnB4T

:: Check if Python is installed
python --version 2>NUL
if %ERRORLEVEL% NEQ 0 (
    echo Python is not installed or not in PATH. Please install Python 3 to continue.
    pause
    exit /b 1
)

:: Check if pip is installed
pip --version 2>NUL
if %ERRORLEVEL% NEQ 0 (
    echo pip is not installed or not in PATH. Please install pip to continue.
    pause
    exit /b 1
)

:: Ask which API to use
echo Which API would you like to use?
echo 1) DeepInfra (cloud API, no local installation required)
echo 2) Ollama (local installation required)
choice /c 12 /m "Enter choice [1-2] (default: 1): "

if %ERRORLEVEL% EQU 2 (
    set API_TYPE=ollama
    
    :: Check if Ollama is installed
    where ollama 2>NUL
    if %ERRORLEVEL% NEQ 0 (
        echo Ollama is not installed or not in PATH.
        echo Please install Ollama from https://ollama.ai/
        echo Do you want to continue anyway? (Y/N)
        choice /c YN /m "Continue without Ollama? "
        if %ERRORLEVEL% EQU 2 exit /b 1
    )

    :: Check if Ollama is running
    echo Checking if Ollama is running...
    curl -s localhost:11434/api/version >NUL 2>&1
    if %ERRORLEVEL% NEQ 0 (
        echo Ollama is not running. Attempting to start it...
        start /b Ollama
        
        :: Wait for Ollama to start
        echo Waiting for Ollama to start...
        for /l %%i in (1, 1, 10) do (
            curl -s localhost:11434/api/version >NUL 2>&1
            if %ERRORLEVEL% EQU 0 (
                echo Ollama is now running!
                goto :ollama_running
            )
            
            if %%i EQU 10 (
                echo Could not connect to Ollama. Please ensure it's running before continuing.
                echo Do you want to continue anyway? (Y/N)
                choice /c YN /m "Continue without Ollama? "
                if %ERRORLEVEL% EQU 2 exit /b 1
                goto :ollama_running
            )
            
            echo Waiting... (%%i/10)
            timeout /t 2 >NUL
        )
    )

:ollama_running
    :: Check for required model
    echo Checking for required model gemma3:4b...
    ollama list | findstr "gemma3:4b" >NUL
    if %ERRORLEVEL% NEQ 0 (
        echo The default model 'gemma3:4b' is not downloaded.
        echo Would you like to download it now? (Y/N)
        choice /c YN /m "Download gemma3:4b now? "
        if %ERRORLEVEL% EQU 1 (
            echo Downloading gemma3:4b (this may take a while)...
            ollama pull gemma3:4b
        ) else (
            echo Without the model, the application may not work properly.
            echo You can pull other models later using 'ollama pull MODEL_NAME'
        )
    )
) else (
    :: Using DeepInfra
    echo Using DeepInfra API for model generation
    echo Default API key: %DEEPINFRA_API_KEY:~0,5%*****
    
    choice /c YN /m "Would you like to use a different API key? "
    if %ERRORLEVEL% EQU 1 (
        set /p new_key="Enter your DeepInfra API key: "
        if not "%new_key%"=="" (
            set DEEPINFRA_API_KEY=%new_key%
            echo API key updated
        )
    )
)

:: Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

:: Create static directory if it doesn't exist
if not exist static mkdir static

:: Start the server with the selected API type
echo Starting server on http://localhost:5000 using %API_TYPE% API
echo Press Ctrl+C to stop the server

:: Update the server.py file with the correct API type and key
if "%API_TYPE%"=="deepinfra" (
    powershell -Command "(Get-Content server.py) -replace 'LLM_API_TYPE = \".*\"', 'LLM_API_TYPE = \"deepinfra\"' | Set-Content server.py.tmp"
    powershell -Command "(Get-Content server.py.tmp) -replace 'DEEPINFRA_API_KEY = \".*\"', 'DEEPINFRA_API_KEY = \"%DEEPINFRA_API_KEY%\"' | Set-Content server.py"
    del server.py.tmp
) else (
    powershell -Command "(Get-Content server.py) -replace 'LLM_API_TYPE = \".*\"', 'LLM_API_TYPE = \"ollama\"' | Set-Content server.py.tmp"
    move /y server.py.tmp server.py
)

:: Run the app
python server.py 