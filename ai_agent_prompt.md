# AI Agent Prompt: Dynamic Games Next.js Migration

## Task Overview

Migrate the Dynamic Games therapeutic 3D shooter application from its current Flask implementation to a modern Next.js web application. The application generates personalized 3D games where users shoot positive affirmations at negative thoughts to help transform their mindset.

## Source Repository

The source code is available at: https://github.com/felixwulf7/psygaminglab_app_costum_games

This repository contains the current Flask implementation with the following key components:
- Flask server backend
- Three.js-based 3D game implementation
- DeepInfra API integration for AI-generated game content
- HTML templates for game generation

## Detailed Requirements

### 1. Maintain Core Functionality

- User inputs a situation they're struggling with
- AI generates personalized game content (title, negative thoughts, positive affirmations)
- A playable 3D shooter game is generated where users shoot positive thoughts at negative ones
- Multiple difficulty levels are supported

### 2. Technical Migration Requirements

- Convert Flask API endpoints to Next.js API routes
- Maintain DeepInfra API integration for content generation
- Convert raw HTML/JS/CSS Three.js implementation to React components
- Ensure the game behaves identically to the original version
- Support the same configuration options (difficulty levels, etc.)

### 3. Enhanced Features to Implement

- Responsive design for mobile and desktop
- User authentication and saved games
- Improved UI/UX for game creation and selection
- Performance optimizations for Three.js rendering
- Proper error handling and loading states

### 4. Architecture Guidelines

Follow the architecture outlined in the `nextjs_integration_plan.md` file, which includes:
- Next.js App Router structure
- Component breakdown and responsibilities
- API route implementation
- State management approach
- Deployment strategy

### 5. Specific File Conversions

- Convert `server.py` Flask routes to Next.js API routes
- Convert the HTML template to React components
- Implement Three.js in a React-friendly way
- Create TypeScript interfaces for all data structures

## Existing Code Structure

The current implementation has these key files:
- `server.py`: Main Flask application with API endpoints
- `templates/3d_shooter_accepting_being_tired.html`: Game template with Three.js
- `requirements.txt`: Python dependencies
- `README.md`: Documentation

## Project Timeline

Implement the migration in three phases as detailed in the integration plan:
1. Basic migration of core functionality
2. Enhanced features implementation
3. Optimization and scaling

## Additional Resources

- Refer to the `nextjs_integration_plan.md` file for detailed implementation guidance
- The templates directory contains the base game template to convert
- The static directory contains examples of generated games

## Deliverables

1. A complete Next.js codebase implementing all requirements
2. Documentation for running and deploying the application
3. Clear code comments explaining implementation details
4. Proper testing for all components and functionality

## Technical Constraints

- Use TypeScript for all Next.js components and API routes
- Maintain compatibility with modern browsers (Chrome, Firefox, Safari, Edge)
- Optimize for performance on both desktop and mobile devices
- Follow security best practices for API key handling

Please implement this migration while maintaining the therapeutic value and game mechanics of the original application. Refer to the `nextjs_integration_plan.md` file for detailed implementation guidance. 