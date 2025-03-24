# Dynamic Games Next.js Integration Plan

This document provides a comprehensive plan for integrating the Dynamic Games therapeutic 3D shooter application into a Next.js web application. It includes architecture, implementation details, and deployment considerations.

## Project Overview

Dynamic Games is a therapeutic web application that generates personalized 3D shooter games where users transform negative thoughts into positive affirmations. The current implementation uses:

- **Backend**: Flask server (Python)
- **Frontend**: HTML/CSS/JavaScript with Three.js for 3D rendering
- **AI Integration**: DeepInfra API for generating personalized game content
- **Game Mechanics**: Players shoot positive affirmations at negative thoughts in a 3D environment

## Current Architecture

### Backend Components
- `server.py`: Flask server that handles API requests and game generation
- Templates directory: Contains the base 3D shooter game template
- Static directory: Stores generated game HTML files
- Debug_games directory: Stores copies of games for debugging

### API Endpoints
- `/api/create-game` (POST): Receives user input, generates game content, creates HTML file
- `/api/models` (GET): Returns available AI models
- `/game/{filename}` (GET): Serves generated game files

### AI Integration
- Uses DeepInfra API (currently Mixtral-8x7B-Instruct-v0.1 model)
- Generates game title, negative thoughts, and positive affirmations based on user input
- JSON response is integrated into HTML template

## Next.js Integration Plan

### 1. Architecture Overview

The new architecture will be a Next.js application with:

- **Frontend**: Next.js React components with Three.js for 3D rendering
- **Backend**: Next.js API routes replacing Flask endpoints
- **AI Integration**: Same DeepInfra API but called from Next.js API routes
- **Database**: Optional MongoDB/Supabase for user accounts and saved games
- **Deployment**: Vercel for hosting (with optional CI/CD pipeline)

### 2. Directory Structure

```
dynamic-games-nextjs/
├── public/
│   ├── templates/             # Game templates (moved from current templates/)
│   ├── assets/                # Static assets (images, models, sounds)
│   └── favicon.ico
├── src/
│   ├── app/                   # Next.js App Router
│   │   ├── page.tsx           # Home page
│   │   ├── layout.tsx         # Root layout
│   │   ├── game/[id]/page.tsx # Dynamic game page
│   │   └── globals.css        # Global styles
│   ├── components/            # React components
│   │   ├── GameForm.tsx       # Form for user input
│   │   ├── GamePlayer.tsx     # Three.js game renderer
│   │   └── ui/                # UI components
│   ├── lib/                   # Shared utility functions
│   │   ├── deepinfra.ts       # DeepInfra API integration
│   │   ├── gameGenerator.ts   # Game generation logic
│   │   └── templateProcessor.ts # HTML template processing
│   ├── pages/api/             # API Routes
│   │   ├── create-game.ts     # Game creation endpoint
│   │   └── models.ts          # Available models endpoint
│   └── types/                 # TypeScript type definitions
├── .env.local                 # Environment variables
├── next.config.js             # Next.js configuration
└── package.json               # Dependencies
```

### 3. Detailed Component Implementation

#### A. Frontend Components

**Home Page (`src/app/page.tsx`):**
- Main landing page with information about the therapeutic game
- Form for users to input their struggle/situation
- Option to choose difficulty level
- Displays previously created games (if user authentication is implemented)

**Game Form Component (`src/components/GameForm.tsx`):**
- Text input for the user's situation
- Difficulty selector (Easy, Medium, Hard)
- Submit button with loading state
- Error handling and validation

**Game Player Component (`src/components/GamePlayer.tsx`):**
- React component that encapsulates Three.js game logic
- Loads game data (title, thoughts, affirmations) from props
- Initializes and manages the 3D environment
- Handles user interaction (mouse/keyboard)
- Manages game state (score, health, level)

**Navigation Component (`src/components/Navigation.tsx`):**
- Navigation bar with links to home, about, previous games
- User authentication UI (if implemented)

#### B. API Routes

**Create Game Endpoint (`src/pages/api/create-game.ts`):**
```typescript
import type { NextApiRequest, NextApiResponse } from 'next';
import { generateGameContent } from '@/lib/deepinfra';
import { processTemplate } from '@/lib/templateProcessor';

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const { userInput, difficulty = 'medium' } = req.body;
    
    // Generate game content using DeepInfra API
    const gameContent = await generateGameContent(userInput);
    
    // Process the template with the generated content
    const { gameId, html } = await processTemplate(gameContent, difficulty);
    
    // Save the game (filesystem in dev, database in production)
    // ...
    
    return res.status(200).json({ 
      gameId,
      url: `/game/${gameId}` 
    });
  } catch (error) {
    console.error('Error creating game:', error);
    return res.status(500).json({ error: 'Failed to create game' });
  }
}
```

**Models Endpoint (`src/pages/api/models.ts`):**
```typescript
import type { NextApiRequest, NextApiResponse } from 'next';

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  const models = [
    { id: 'mistralai/Mixtral-8x7B-Instruct-v0.1', name: 'Mixtral 8x7B' },
    { id: 'meta-llama/Llama-2-70b-chat-hf', name: 'Llama 2 70B' }
  ];
  
  return res.status(200).json({ models });
}
```

#### C. Utility Functions

**DeepInfra API Integration (`src/lib/deepinfra.ts`):**
```typescript
import axios from 'axios';

export async function generateGameContent(userInput: string) {
  const apiKey = process.env.DEEPINFRA_API_KEY;
  const modelId = 'mistralai/Mixtral-8x7B-Instruct-v0.1';
  
  const prompt = `Generate a personalized therapeutic game based on this situation: "${userInput}"...`;
  
  const response = await axios.post(
    `https://api.deepinfra.com/v1/inference/${modelId}`,
    {
      input: prompt,
      max_new_tokens: 1024,
    },
    {
      headers: {
        'Authorization': `Bearer ${apiKey}`,
        'Content-Type': 'application/json'
      }
    }
  );
  
  // Parse and validate the response
  // ...
  
  return {
    title: '...',
    positiveThoughts: [...],
    negativeThoughts: [...]
  };
}
```

**Template Processor (`src/lib/templateProcessor.ts`):**
```typescript
import fs from 'fs';
import path from 'path';
import { nanoid } from 'nanoid';

export async function processTemplate(gameContent, difficulty) {
  // Read the template file
  const templatePath = path.join(process.cwd(), 'public', 'templates', '3d_shooter_accepting_being_tired.html');
  let template = fs.readFileSync(templatePath, 'utf8');
  
  // Replace placeholders with game content
  template = template.replace('{{GAME_TITLE}}', gameContent.title);
  // ... more replacements
  
  // Generate unique ID for the game
  const gameId = `game_${Date.now()}_${nanoid(6)}`;
  
  // In development, save to filesystem
  if (process.env.NODE_ENV === 'development') {
    const outputPath = path.join(process.cwd(), 'public', 'games', `${gameId}.html`);
    fs.writeFileSync(outputPath, template);
  }
  
  // In production, could save to database or cloud storage
  
  return {
    gameId,
    html: template
  };
}
```

### 4. Database Integration (Optional)

For a more robust application with user accounts and saved games:

**Schema Design:**
- Users: ID, email, name, password (hashed), created_at
- Games: ID, user_ID, title, content (JSON), created_at, play_count
- UserProgress: ID, user_ID, game_ID, level, score, completed

**Database Options:**
- MongoDB Atlas: Document database, good for flexible schema
- Supabase: Postgres-based, offers auth and storage
- Planetscale: MySQL-compatible, serverless

**Integration with Next.js:**
- Use Prisma ORM for type-safe database access
- Implement NextAuth.js for authentication

### 5. State Management

**Client-Side State:**
- React Context for global app state
- React Query for API data fetching and caching
- Local state with useState for component-specific state

**Game State:**
- Custom Three.js state management for the game
- Consider Zustand for more complex state requirements

### 6. Deployment Strategy

**Vercel Deployment:**
- Connect GitHub repository to Vercel
- Configure environment variables for API keys
- Setup custom domain if needed

**Performance Considerations:**
- Implement caching for API responses
- Use Next.js Image component for optimized images
- Consider edge functions for global performance

### 7. Testing Strategy

**Unit Tests:**
- Jest for utility functions
- React Testing Library for components

**Integration Tests:**
- Test API routes with supertest
- Test form submissions and API interactions

**E2E Tests:**
- Cypress for full application flows
- Test game generation and gameplay

### 8. Security Considerations

- Secure handling of API keys (environment variables)
- Rate limiting for API endpoints
- Input validation and sanitization
- Content security policy for Three.js
- CORS configuration

### 9. Accessibility

- Keyboard navigation for all UI elements
- Screen reader support
- Alternative game modes for different abilities
- Color contrast and text size considerations

### 10. Implementation Phases

**Phase 1: Basic Migration**
- Setup Next.js project structure
- Implement core API endpoints
- Create React components for the UI
- Basic game rendering with Three.js

**Phase 2: Enhanced Features**
- User authentication
- Game history and saving
- Analytics and tracking
- Improved game mechanics

**Phase 3: Optimization and Scale**
- Performance optimizations
- Mobile responsiveness
- Multi-language support
- Advanced customization options

## Technical Requirements

- Node.js 18+ for Next.js development
- npm or yarn for package management
- DeepInfra API key for AI integration
- Basic knowledge of React, Next.js, and Three.js
- Git for version control

## Resources

- [Next.js Documentation](https://nextjs.org/docs)
- [Three.js Documentation](https://threejs.org/docs/)
- [DeepInfra API Documentation](https://deepinfra.com/docs/api)
- [Current Flask Server](https://github.com/felixwulf7/psygaminglab_app_costum_games)

## Potential Challenges and Solutions

**Challenge: Three.js Integration with React**
- Solution: Use libraries like react-three-fiber for declarative Three.js in React
- Alternative: Load Three.js in a useEffect hook with proper cleanup

**Challenge: Server-Side Game Generation**
- Solution: Use Next.js API routes for template processing
- Alternative: Pre-generate game templates and hydrate with client-side data

**Challenge: SEO for Dynamic Games**
- Solution: Implement OpenGraph metadata for shareable games
- Use dynamic metadata in Next.js app directory

**Challenge: Mobile Performance**
- Solution: Detect device capabilities and adjust game complexity
- Implement progressive enhancement for different devices

## Conclusion

This integration plan provides a comprehensive roadmap for converting the current Flask-based Dynamic Games application to a modern Next.js implementation. By following this architectural approach and implementation details, the resulting application will be more maintainable, scalable, and user-friendly while preserving the core therapeutic value of the original concept. 