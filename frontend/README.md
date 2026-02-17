# Debate Frontend

React + TypeScript UI for the multi-agent AI debate system.

## Features

- 🎨 **Dark Mode UI**: Polished dark theme with Tailwind CSS
- ⚡ **Real-time Updates**: WebSocket connection for live debate streaming
- 🧩 **Component Architecture**: Atomic Design pattern (Atoms → Molecules → Organisms → Templates)
- 📡 **WebSocket Auto-reconnect**: Exponential backoff reconnection strategy
- 💾 **State Management**: Zustand stores for debate config, state, and UI
- 🎭 **Smooth Animations**: Framer Motion for message transitions and verdict reveals
- 📱 **Responsive Design**: Desktop, tablet, and mobile layouts
- 📤 **Export Results**: JSON, Markdown, and Text format exports
- 🔄 **Type-safe API**: TypeScript types mirroring backend Pydantic models

## Setup

```bash
cd frontend
npm install
```

## Run

Development server with hot reload:
```bash
npm run dev
```

The frontend will run on `http://localhost:5173` and connect to the backend at `http://localhost:8000`.

## Build

Production build:
```bash
npm run build
npm run preview  # Preview production build
```

## Architecture

### Component Structure (Atomic Design)

```
src/components/
├── atoms/           # Basic UI primitives
│   ├── Button.tsx
│   ├── Input.tsx
│   ├── Select.tsx
│   ├── Badge.tsx
│   ├── StatusIndicator.tsx
│   └── LoadingSpinner.tsx
├── molecules/       # Simple component compositions
│   ├── AgentCard.tsx
│   ├── MessageBubble.tsx
│   ├── ThinkingIndicator.tsx
│   └── RoundIndicator.tsx
├── organisms/       # Complex feature components
│   ├── DebateConfig/      # Debate creation panel
│   ├── LiveDebate/        # Real-time debate view
│   ├── ParticipantsPanel/ # Agent stats sidebar
│   └── VerdictPanel/      # Results display
└── templates/       # Layout components
    ├── Header.tsx
    └── DebateLayout.tsx
```

### State Management (Zustand)

Three main stores manage application state:

**1. `debateConfigStore`** - Debate Creation Form
```typescript
{
  topic: string;
  agents: AgentConfig[];
  numRounds: number;
  judgeConfig: AgentConfig | null;
  // Actions: setTopic, addAgent, removeAgent, setJudge, reset
}
```

**2. `debateStateStore`** - Active Debate Data
```typescript
{
  debate: DebateState | null;
  connectionState: 'disconnected' | 'connecting' | 'connected' | 'error';
  // Actions: setDebate, addMessage, setStatus, reset
}
```

**3. `uiStore`** - UI Preferences
```typescript
{
  currentView: 'config' | 'debate' | 'results';
  // Actions: setCurrentView
}
```

### TypeScript Types

All types in `src/types/` mirror backend Pydantic models:

- `debate.ts` - DebateState, DebateConfig, DebateStatus
- `agent.ts` - AgentConfig, AgentRole
- `message.ts` - Message interface
- `judge.ts` - JudgeResult, AgentScore
- `llm.ts` - LLMConfig, ModelProvider
- `provider.ts` - ProviderInfo, ModelInfo
- `websocket.ts` - WebSocketMessage, event types
- `api.ts` - API request/response types

### WebSocket Integration

The `useDebateWebSocket` hook manages real-time communication:

```typescript
const { connectionState, lastMessage } = useDebateWebSocket(debateId);
```

**Features:**
- Auto-connect on debate creation
- Exponential backoff reconnection (1s → 2s → 4s → 8s → 16s, max 30s)
- Heartbeat ping every 30 seconds
- Event-driven state updates
- Automatic cleanup on unmount

**WebSocket Events:**
- `connection_established` - Initial connection
- `debate_started` - Debate execution begins
- `round_started` - New round begins
- `agent_thinking` - Agent preparing response
- `message_received` - Agent message received
- `judge_result` - Judge verdict received
- `debate_complete` - Debate finished
- `error` - Error occurred

## Project Structure

```
frontend/
├── src/
│   ├── api/                    # REST API clients
│   │   ├── config.ts          # Base API client with error handling
│   │   ├── debates.ts         # Debate endpoints
│   │   ├── providers.ts       # Provider catalog
│   │   └── index.ts
│   ├── components/            # UI components (see Architecture above)
│   ├── hooks/                 # Custom React hooks
│   │   ├── useDebateWebSocket.ts  # WebSocket connection
│   │   ├── useAutoScroll.ts       # Auto-scroll behavior
│   │   └── index.ts
│   ├── stores/                # Zustand state stores
│   ├── types/                 # TypeScript type definitions
│   ├── App.tsx                # Main application component
│   ├── main.tsx               # React entry point
│   └── index.css              # Global styles + Tailwind directives
├── public/                    # Static assets
├── package.json
├── vite.config.ts             # Vite bundler config
├── tailwind.config.js         # Tailwind CSS config
├── tsconfig.json              # TypeScript config
└── README.md
```

## Key Components

### Debate Configuration Panel
**Location:** `src/components/organisms/DebateConfig/`

User interface for creating debates:
- Topic input
- Add/remove participants (agents)
- Select LLM provider and model for each agent
- Configure rounds
- Select judge model

**Usage:**
```typescript
import { DebateConfig } from '@/components/organisms';

// Automatically connects to debateConfigStore
<DebateConfig />
```

### Live Debate Panel
**Location:** `src/components/organisms/LiveDebate/`

Real-time debate display:
- Message list with auto-scroll
- Thinking indicators
- Round progress indicator

**Key Features:**
- Messages fade in with Framer Motion
- Auto-scrolls to latest message
- Shows which agent is thinking

### Verdict Panel
**Location:** `src/components/organisms/VerdictPanel/`

Displays judge results after debate completion:
- Winner announcement with animation
- Score cards (0-10 ratings)
- Judge reasoning for each agent
- Key arguments summary
- Export functionality (JSON/Markdown/Text)

**Animation:**
- Slides up from bottom when debate completes
- Winner announcement fades and scales in

## Development Guide

### Adding a New Component

Follow the Atomic Design pattern:

1. **Atom** - Basic UI element (button, input, badge)
2. **Molecule** - Combination of atoms (message bubble = avatar + text + timestamp)
3. **Organism** - Feature component (debate config panel, verdict display)
4. **Template** - Layout structure (header, grid layout)

Example:
```typescript
// src/components/atoms/MyButton.tsx
export const MyButton = ({ children, onClick, variant = 'primary' }) => {
  return (
    <button
      onClick={onClick}
      className={`px-4 py-2 rounded ${
        variant === 'primary' ? 'bg-blue-600' : 'bg-gray-600'
      }`}
    >
      {children}
    </button>
  );
};
```

### Working with Zustand Stores

Import and use store hooks:

```typescript
import { useDebateConfigStore } from '@/stores';

const MyComponent = () => {
  const { topic, setTopic, agents, addAgent } = useDebateConfigStore();

  return (
    <div>
      <input value={topic} onChange={(e) => setTopic(e.target.value)} />
      <button onClick={() => addAgent(newAgent)}>Add Agent</button>
    </div>
  );
};
```

### Adding WebSocket Event Handlers

Update `useDebateWebSocket.ts` to handle new events:

```typescript
// In useDebateWebSocket.ts
const handleMessage = (event: MessageEvent) => {
  const message: WebSocketMessage = JSON.parse(event.data);

  switch (message.type) {
    case 'my_new_event':
      // Update store or trigger UI change
      debateStateStore.getState().updateSomething(message.payload);
      break;
    // ... other cases
  }
};
```

### Styling with Tailwind

This project uses Tailwind CSS with a custom dark theme:

**Color Palette:**
- Background: `bg-slate-900` (dark mode default)
- Panels: `bg-slate-800`
- Borders: `border-slate-700`
- Text: `text-slate-200`
- Pro stance: `text-green-500`
- Con stance: `text-red-500`
- Judge: `text-purple-500`

**Example:**
```typescript
<div className="bg-slate-800 border border-slate-700 rounded-lg p-4">
  <h2 className="text-slate-200 font-semibold">Panel Title</h2>
  <p className="text-slate-400">Panel content</p>
</div>
```

### Adding Animations

Use Framer Motion for smooth transitions:

```typescript
import { motion } from 'framer-motion';

<motion.div
  initial={{ opacity: 0, y: 20 }}
  animate={{ opacity: 1, y: 0 }}
  transition={{ duration: 0.3 }}
>
  <MessageBubble {...message} />
</motion.div>
```

## Common Tasks

### Fetch Available Models

```typescript
import { providersApi } from '@/api';

const providers = await providersApi.list();
// Returns: { providers: ProviderInfo[] }
```

### Create a Debate

```typescript
import { debatesApi } from '@/api';

const response = await debatesApi.create({
  config: {
    topic: "AI ethics",
    num_rounds: 3,
    agents: [...],
    judge_config: {...}
  }
});
// Returns: { debate_id: string }
```

### Connect to WebSocket

```typescript
const { connectionState, lastMessage } = useDebateWebSocket(debateId);

useEffect(() => {
  if (lastMessage?.type === 'message_received') {
    // Handle new message
  }
}, [lastMessage]);
```

### Export Debate Results

```typescript
import { debatesApi } from '@/api';

// Export as JSON
const jsonData = await debatesApi.export(debateId, 'json');

// Export as Markdown
const markdown = await debatesApi.export(debateId, 'markdown');

// Export as Text
const text = await debatesApi.export(debateId, 'text');
```

## API Integration

### REST Endpoints

**Base URL:** `http://localhost:8000`

- `GET /api/providers` - List available LLM providers
- `POST /api/debates` - Create new debate
- `POST /api/debates/:id/start` - Start debate execution
- `GET /api/debates/:id` - Get debate state
- `GET /api/debates/:id/export` - Export results (format: json|markdown|text)

### WebSocket Endpoint

**URL:** `ws://localhost:8000/api/ws/:debate_id`

See [backend API documentation](../backend/API_DOCUMENTATION.md) for detailed API reference.

## Error Handling

### API Errors

The API client in `src/api/config.ts` handles errors automatically:

```typescript
try {
  const debate = await debatesApi.create(config);
} catch (error) {
  // Error is already formatted by apiClient
  console.error(error.message); // User-friendly message
}
```

### WebSocket Errors

The WebSocket hook handles connection errors with auto-reconnect:

```typescript
const { connectionState } = useDebateWebSocket(debateId);

if (connectionState === 'error') {
  // Show error UI
  return <ErrorMessage>Failed to connect</ErrorMessage>;
}
```

## Testing

Manual testing checklist:

1. **Debate Creation**
   - Fill out topic, add agents, set rounds
   - Verify validation errors for invalid input
   - Create debate successfully

2. **Live Debate**
   - WebSocket connects automatically
   - Messages appear in real-time
   - Thinking indicators show/hide correctly
   - Auto-scroll works

3. **Verdict Display**
   - Panel slides up after completion
   - Scores display correctly
   - Export buttons work (JSON, Markdown, Text)

4. **WebSocket Reconnection**
   - Stop backend server mid-debate
   - Verify "Reconnecting..." indicator appears
   - Restart backend
   - Verify auto-reconnect succeeds

5. **Responsive Design**
   - Test on desktop (1440px+)
   - Test on tablet (768px)
   - Test on mobile (375px)

## Dependencies

```json
{
  "react": "^18.2.0",
  "react-dom": "^18.2.0",
  "zustand": "^4.4.7",          // State management
  "framer-motion": "^10.16.16", // Animations
  "date-fns": "^3.0.6",         // Date formatting
  "lucide-react": "^0.303.0",   // Icons
  "clsx": "^2.0.0",             // Conditional classNames
  "@headlessui/react": "^1.7.17" // Accessible UI primitives
}
```

**Dev Dependencies:**
```json
{
  "tailwindcss": "^4.0.15",     // CSS framework
  "typescript": "^5.2.2",       // Type checking
  "vite": "^5.0.8",             // Build tool
  "@vitejs/plugin-react": "^4.2.1"
}
```

## Performance Optimization

### Memoization

Use `React.memo` for expensive components:

```typescript
export const MessageBubble = React.memo(({ message }) => {
  // Component implementation
});
```

### Lazy Loading

Verdict panel is only rendered after debate completes:

```typescript
{debate.status === 'completed' && <VerdictPanel />}
```

### Auto-scroll Optimization

Auto-scroll only triggers on new messages, not all state updates:

```typescript
useEffect(() => {
  scrollToBottom();
}, [debate.history.length]); // Only when message count changes
```

## Accessibility

- All buttons are keyboard accessible (Tab, Enter)
- Focus indicators visible on all interactive elements
- ARIA labels on icon-only buttons
- Proper heading hierarchy (h1 → h2 → h3)
- Color contrast meets WCAG AA standards

## Troubleshooting

### WebSocket Not Connecting

1. Check backend is running on `http://localhost:8000`
2. Verify debate was created successfully (has `debate_id`)
3. Check browser console for WebSocket errors
4. Ensure CORS is configured correctly in backend

### Messages Not Appearing

1. Check WebSocket connection state in UI
2. Verify debate has started (POST `/api/debates/:id/start`)
3. Check backend console for errors
4. Ensure API keys are configured in backend `.env`

### Export Not Working

1. Verify debate status is `completed`
2. Check backend endpoint: `GET /api/debates/:id/export?format=json`
3. Check browser console for API errors

### Styling Issues

1. Clear browser cache
2. Verify Tailwind CSS is configured: `npx tailwindcss -i ./src/index.css -o ./dist/output.css`
3. Check `index.css` has Tailwind directives: `@tailwind base; @tailwind components; @tailwind utilities;`

---

## Documentation

For complete system documentation, see:
- **[Backend README](../backend/README.md)** - Backend API and architecture
- **[API Documentation](../backend/API_DOCUMENTATION.md)** - REST and WebSocket API reference
- **[Architecture](../backend/ARCHITECTURE.md)** - System design and decisions
- **[Project README](../README.md)** - Monorepo setup and quick start

---

## Future Enhancements

Potential features for future iterations:
- Debate library (browse past debates)
- Replay mode (playback with speed control)
- Multi-debate view (monitor multiple debates)
- Debate templates (save/load presets)
- Advanced analytics (sentiment, argument mapping)
- Custom themes (beyond dark mode)
- Real-time collaboration (multi-user)
