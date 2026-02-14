# Multi-Agent Debate UI - MVP Implementation Plan

## Context

The user has provided a wireframe for a debate UI that needs to be implemented in React + TypeScript with Tailwind CSS. The goal is to build a polished, dark-mode interface that connects to the existing FastAPI backend via WebSocket for real-time debate updates.

**Current State:**
- Frontend exists but is minimal (only a health check component)
- Backend is complete with WebSocket support at `/api/ws/{debate_id}`
- No styling framework, no TypeScript types, no WebSocket hooks yet
- Clean slate for building the UI from scratch

**User Requirements:**
- MVP-first approach focusing on core functionality
- Dark mode with Tailwind CSS
- Subtle animations for polish
- Real-time updates via WebSocket
- Only implement features supported by the backend

**Backend Capabilities:**
- WebSocket endpoint: `WS /api/ws/{debate_id}` with event-driven updates
- REST endpoints: Create debates, start debates, export results
- Provider catalog API: `GET /api/providers` for model selection
- Event types: `debate_started`, `round_started`, `agent_thinking`, `message_received`, `judge_result`, `debate_complete`, etc.
- Export formats: JSON, Markdown, Text

---

## MVP Feature Scope

### Included in MVP ✅

**1. Header**
- App title
- Start Debate button (triggers debate execution)
- Export button (download results as JSON/Markdown/Text)

**2. Left Panel - Debate Configuration**
- Topic input field
- Participants list showing agents with model and stance
- Add Participant button (opens modal to configure new agent)
- Rounds input (number of debate rounds)
- Judge selection dropdown
- Start Debate button

**3. Center Panel - Live Debate**
- Round indicator showing current round
- Message list displaying agent responses in real-time
- Thinking indicator when agent is preparing response
- Auto-scroll to latest message

**4. Right Panel - Participants & Stats**
- Agent cards showing:
  - Agent name and stance (Pro/Con)
  - Model name
  - Current status (thinking/waiting/completed)
- Basic stats from backend:
  - Judge scores (after completion)
  - Message count

**5. Bottom Panel - Debate Verdict**
- Winner announcement
- Score cards for each agent (0-10 scores)
- Judge's reasoning per agent
- Key arguments identified by judge
- Export Results button

**6. WebSocket Integration**
- Real-time connection to `/api/ws/{debate_id}`
- Auto-reconnection with exponential backoff
- Event handling for all debate lifecycle events
- Connection status indicator

**7. Styling & Polish**
- Dark mode as default theme
- Tailwind CSS for all styling
- Subtle animations:
  - Message fade-in when received
  - Pulsing dots for thinking indicator
  - Verdict panel slide-up animation
- Responsive layout (desktop-first, mobile-friendly)

### Excluded from MVP ❌

- Pause/Stop/Resume controls (backend doesn't support)
- Turn timer countdown (backend doesn't send time limits)
- Speed control (not applicable for live debates)
- Momentum charts (requires complex frontend calculation)
- Evidence counting (requires message content analysis)
- Interruptions tracking (backend doesn't track)
- Toxicity meter (backend doesn't implement)
- Debate timeline visualization (nice-to-have for later)
- Win rate across debates (requires persistence)
- Auto-scroll toggle (just always auto-scroll)
- Advanced statistics dashboard

---

## Implementation Phases

### Phase 1: Foundation & Setup (Days 1-2)

**1.1 Install Dependencies**
```bash
npm install -D tailwindcss postcss autoprefixer
npm install zustand clsx date-fns lucide-react framer-motion
npm install @headlessui/react
```

**1.2 Configure Tailwind CSS**
- Initialize Tailwind: `npx tailwindcss init -p`
- Configure `tailwind.config.js` with dark mode and custom colors
- Set up dark theme color palette (dark backgrounds, borders, text)
- Add animation utilities
- Update `src/index.css` with Tailwind directives

**1.3 Create TypeScript Type System**

Create `src/types/` directory with exact mirrors of backend Pydantic models:

**Files to create:**
- `types/debate.ts` - DebateState, DebateConfig, DebateStatus enum
- `types/agent.ts` - AgentConfig, AgentRole enum
- `types/message.ts` - Message interface
- `types/judge.ts` - JudgeResult, AgentScore
- `types/llm.ts` - LLMConfig, ModelProvider enum
- `types/provider.ts` - ProviderInfo, ModelInfo (from provider catalog)
- `types/websocket.ts` - WebSocketMessage, event payload types
- `types/index.ts` - Export all types

**Critical type definitions:**
```typescript
// Backend models to mirror exactly
enum DebateStatus { CREATED, IN_PROGRESS, COMPLETED, FAILED }
enum DebateEventType { DEBATE_STARTED, ROUND_STARTED, AGENT_THINKING, MESSAGE_RECEIVED, etc. }
interface DebateState { debate_id, config, status, current_round, history, judge_result, ... }
interface Message { agent_id, agent_name, content, round_number, timestamp, stance }
interface JudgeResult { summary, agent_scores, winner_id, winner_name, key_arguments }
```

**1.4 Set Up Zustand Stores**

Create `src/stores/` directory with state management:

- `stores/debateConfigStore.ts` - Topic, agents, rounds, judge (for creating debates)
- `stores/debateStateStore.ts` - Active debate state, messages, current round/turn
- `stores/uiStore.ts` - Dark mode, connection status, current view

**Store structure:**
```typescript
// debateConfigStore: Manages debate creation form
interface DebateConfigStore {
  topic: string;
  agents: AgentConfig[];
  numRounds: number;
  judgeConfig: AgentConfig | null;
  actions: { setTopic, addAgent, removeAgent, setNumRounds, setJudge, reset }
}

// debateStateStore: Manages live debate data
interface DebateStateStore {
  debate: DebateState | null;
  connectionState: 'disconnected' | 'connecting' | 'connected' | 'error';
  actions: { setDebate, addMessage, setStatus, setConnectionState, reset }
}
```

### Phase 2: Core UI Components (Days 3-4)

**2.1 Atomic Components (src/components/atoms/)**

Build reusable UI primitives:

- `Button.tsx` - Primary, secondary, danger variants with loading states
- `Input.tsx` - Text input with dark mode styling
- `Select.tsx` - Dropdown select component
- `Badge.tsx` - Status badges (Pro/Con/Judge, color-coded)
- `StatusIndicator.tsx` - Connection status dot (green/yellow/red)
- `LoadingSpinner.tsx` - Animated spinner for loading states

**2.2 Molecular Components (src/components/molecules/)**

- `AgentCard.tsx` - Display agent info (name, model, stance badge, status)
- `MessageBubble.tsx` - Chat-style message with avatar, content, timestamp
- `ThinkingIndicator.tsx` - Animated "Agent is thinking..." with pulsing dots
- `RoundIndicator.tsx` - Current round display (e.g., "Round 2 of 4")

**2.3 Layout Structure (src/components/templates/)**

- `Header.tsx` - Top bar with app title and action buttons
- `DebateLayout.tsx` - Three-column responsive grid layout:
  - Left column: 25% width (config panel)
  - Center column: 50% width (live debate)
  - Right column: 25% width (participants/stats)
  - Bottom section: Full width (verdict, shown after completion)

### Phase 3: Configuration Panel (Days 5-6)

**3.1 Build Config Components (src/components/organisms/DebateConfig/)**

- `index.tsx` - Main config panel container
- `TopicInput.tsx` - Textarea for debate topic with character count
- `ParticipantsList.tsx` - List of current agents with remove buttons
- `ParticipantCard.tsx` - Individual agent display in config list
- `AddParticipantModal.tsx` - Modal for adding new agent:
  - Fetch providers from `GET /api/providers`
  - Dropdown to select provider (Anthropic/OpenAI)
  - Dropdown to select model (Claude 3.5, GPT-4o, etc.)
  - Input for agent name
  - Input for stance (Pro/Con/custom)
  - Textarea for system prompt (optional)
  - Temperature slider (0.0-2.0, default 1.0)
  - Max tokens input (default 1024)
- `RoundsInput.tsx` - Number input for rounds (minimum 1)
- `JudgeSelect.tsx` - Dropdown to select judge model from providers

**3.2 Integrate Config Store**

- Connect all form inputs to `debateConfigStore`
- Validate config before allowing debate creation:
  - Topic must not be empty
  - At least 2 agents required
  - All agent IDs must be unique
  - Judge must be selected
  - Rounds ≥ 1
- Save/load config to localStorage for persistence
- "Start Debate" button creates debate via `POST /api/debates`

**3.3 API Integration for Config**

Create `src/api/debates.ts`:
```typescript
export const debatesApi = {
  create: (config: DebateConfig) => POST('/api/debates', config),
  start: (id: string) => POST(`/api/debates/${id}/start`),
  get: (id: string) => GET(`/api/debates/${id}`),
  export: (id: string, format: 'json' | 'markdown' | 'text') =>
    GET(`/api/debates/${id}/export?format=${format}`)
};
```

Create `src/api/providers.ts`:
```typescript
export const providersApi = {
  list: () => GET('/api/providers')
};
```

### Phase 4: WebSocket & Live Debate (Days 7-9)

**4.1 Build WebSocket Hook (src/hooks/useDebateWebSocket.ts)**

Custom hook for WebSocket connection management:

**Features:**
- Connect to `ws://localhost:8000/api/ws/{debate_id}`
- Auto-reconnection with exponential backoff (1s, 2s, 4s, 8s, 16s, max 30s)
- Heartbeat: Send `{type: "ping"}` every 30 seconds
- Event-driven message handling
- Connection state tracking (connecting, connected, disconnected, error)
- Cleanup on unmount

**Hook interface:**
```typescript
interface UseDebateWebSocketReturn {
  connectionState: 'disconnected' | 'connecting' | 'connected' | 'error';
  connect: (debateId: string) => void;
  disconnect: () => void;
  lastMessage: WebSocketMessage | null;
}

// Usage in component:
const { connectionState, connect, lastMessage } = useDebateWebSocket();
```

**Event handlers update debateStateStore:**
- `connection_established` → Initialize UI with current state
- `debate_started` → Set status to IN_PROGRESS
- `round_started` → Update current round
- `agent_thinking` → Show thinking indicator for agent
- `message_received` → Add message to history, hide thinking indicator
- `judge_result` → Store judge result, show verdict panel
- `debate_complete` → Set status to COMPLETED
- `error` → Show error notification

**4.2 Build Live Debate Panel (src/components/organisms/LiveDebate/)**

- `index.tsx` - Main container for live debate view
- `MessageList.tsx` - Scrollable message container:
  - Map over `debate.history` to render messages
  - Show `MessageBubble` for each agent message
  - Show `ThinkingIndicator` when agent is preparing response (from `agent_thinking` event)
  - Auto-scroll to bottom when new message arrives
  - Use `useRef` for scroll container
- `RoundIndicator.tsx` - Display current round and total (e.g., "Round 2 of 4 — Agent A's Turn")

**4.3 Auto-Scroll Logic (src/hooks/useAutoScroll.ts)**

```typescript
const useAutoScroll = (dependencies: any[]) => {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight;
    }
  }, dependencies);

  return containerRef;
};
```

**4.4 Message Display Logic**

- Agent messages alternate visually (left/right alignment based on stance or agent ID)
- Each message shows:
  - Agent avatar (colored circle with initial or icon)
  - Agent name with stance badge
  - Message content (markdown support optional)
  - Timestamp (formatted as "2:34 PM" using date-fns)
- Thinking indicator appears when `agent_thinking` event received
- Indicator disappears when `message_received` event arrives

### Phase 5: Participants Panel & Basic Stats (Day 10)

**5.1 Build Participants Panel (src/components/organisms/ParticipantsPanel/)**

- `index.tsx` - Right sidebar container
- `AgentStatsCard.tsx` - Card for each agent showing:
  - Agent name
  - Stance badge (Pro/Con with color)
  - Model name (e.g., "Claude 3.5 Sonnet")
  - Current status:
    - "Thinking..." (when agent_thinking)
    - "Waiting..." (when other agent's turn)
    - "Completed" (when debate done)
  - Message count for this agent (filter `debate.history` by `agent_id`)

**5.2 Basic Statistics Display**

Only show stats available from backend:
- **Message count**: Total messages in debate (`debate.history.length`)
- **Current round**: `debate.current_round + 1` (backend is 0-indexed)
- **Judge scores**: After completion, show `judge_result.agent_scores` with 0-10 ratings

No complex charts needed for MVP - just simple stat cards with numbers.

### Phase 6: Verdict Panel (Days 11-12)

**6.1 Build Verdict Panel (src/components/organisms/VerdictPanel/)**

Bottom panel that slides up when debate completes:

- `index.tsx` - Container with slide-up animation (framer-motion)
- `WinnerAnnouncement.tsx` - Large winner display:
  - Agent name
  - Winning score vs runner-up score
  - Subtle celebration animation (fade + scale)
- `ScoreCards.tsx` - Grid of cards for each agent:
  - Agent name and stance
  - Score out of 10 (large number)
  - Progress bar visualization (0-10 scale)
  - Judge's reasoning for this agent
- `KeyArguments.tsx` - Bulleted list of key arguments from `judge_result.key_arguments`
- `DebateSummary.tsx` - Judge's overall summary from `judge_result.summary`

**6.2 Animation**

Use framer-motion for slide-up:
```typescript
<motion.div
  initial={{ y: '100%' }}
  animate={{ y: 0 }}
  transition={{ type: 'spring', damping: 25 }}
>
  {/* Verdict content */}
</motion.div>
```

**6.3 Export Functionality**

- Export button in verdict panel (and header)
- Dropdown with 3 options:
  - Export as JSON → `GET /api/debates/{id}/export?format=json`
  - Export as Markdown → `GET /api/debates/{id}/export?format=markdown`
  - Export as Text → `GET /api/debates/{id}/export?format=text`
- Download file to user's computer with proper filename

### Phase 7: Polish & Integration (Day 13)

**7.1 Header Component**

- `Header.tsx` with:
  - App title: "AI Debate App"
  - Connection status indicator (colored dot with tooltip)
  - Action buttons:
    - **Start** - Triggers `POST /api/debates/{id}/start` (only enabled when debate created)
    - **Export** - Opens export dropdown (only enabled when debate completed)

**7.2 Animation & Transitions**

Add subtle animations using framer-motion:

- **Message fade-in**: Each new message fades in from bottom
  ```typescript
  <motion.div
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ duration: 0.3 }}
  >
    <MessageBubble {...message} />
  </motion.div>
  ```

- **Thinking indicator**: Pulsing dots animation (CSS or framer-motion)
  ```typescript
  <motion.div
    animate={{ opacity: [0.5, 1, 0.5] }}
    transition={{ repeat: Infinity, duration: 1.5 }}
  >
    Agent is thinking...
  </motion.div>
  ```

- **Verdict slide-up**: Panel slides from bottom when debate completes

**7.3 Dark Mode Styling**

Tailwind dark mode configuration:
```javascript
// tailwind.config.js
module.exports = {
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        dark: {
          bg: '#0f172a',      // Slate 900
          panel: '#1e293b',   // Slate 800
          border: '#334155',  // Slate 700
          text: '#e2e8f0',    // Slate 200
        },
        pro: '#10b981',       // Green for Pro
        con: '#ef4444',       // Red for Con
      }
    }
  }
}
```

Apply dark theme by default:
```typescript
// In main.tsx or App.tsx
document.documentElement.classList.add('dark');
```

**7.4 Responsive Design**

- Desktop-first approach (1440px+ primary target)
- Tablet breakpoint (768px): Stack panels vertically
- Mobile breakpoint (640px): Single column, use tabs for config/debate/stats

### Phase 8: Testing & Refinement (Day 14)

**8.1 End-to-End Testing**

Manual test flows:
1. Create debate with 2 agents, 2 rounds
2. Start debate and observe real-time messages
3. Verify thinking indicators appear/disappear correctly
4. Check verdict panel shows after completion
5. Test export in all 3 formats (JSON, Markdown, Text)
6. Test WebSocket reconnection (stop backend, restart, verify reconnect)

**8.2 Error Handling**

- **WebSocket connection fails**: Show error message, attempt reconnection
- **API errors**: Show toast notifications with error details
- **Invalid config**: Show field-level validation errors before submit
- **Backend errors during debate**: Display error event message to user

**8.3 Performance Optimization**

- Memoize expensive components (`React.memo` on MessageBubble, AgentCard)
- Debounce statistics recalculation if needed
- Lazy load verdict panel (only render when debate completes)

**8.4 Accessibility**

- All buttons keyboard accessible (Tab, Enter)
- Focus indicators on all interactive elements
- ARIA labels for icon buttons
- Proper heading hierarchy (h1 → h2 → h3)
- Color contrast meets WCAG AA standards

---

## Critical Files to Implement

### Priority 1: Foundation (Must implement first)

1. **`frontend/src/types/index.ts`** - Complete TypeScript type system
   - Mirror all backend Pydantic models
   - Export all types from single entry point
   - Enable type safety across entire app

2. **`frontend/src/stores/debateStateStore.ts`** - Central state management
   - Manage active debate state
   - Store messages, current round, status
   - Provide actions for state updates

3. **`frontend/src/hooks/useDebateWebSocket.ts`** - WebSocket connection
   - Handle real-time communication with backend
   - Auto-reconnection logic
   - Event-driven state updates

### Priority 2: Core UI (Implement after foundation)

4. **`frontend/src/components/organisms/DebateConfig/index.tsx`** - Config panel
   - User entry point for creating debates
   - Integrate all config subcomponents
   - Validate and submit debate creation

5. **`frontend/src/components/organisms/LiveDebate/MessageList.tsx`** - Message display
   - Primary UI for watching debate unfold
   - Render messages with animations
   - Auto-scroll and thinking indicators

6. **`frontend/src/components/organisms/VerdictPanel/index.tsx`** - Results display
   - Show judge decision and scores
   - Animate panel entrance
   - Export functionality

### Priority 3: Integration (Connect everything)

7. **`frontend/src/App.tsx`** - Main application component
   - Compose all organisms into full layout
   - Handle navigation between config and live views
   - Manage global state (debate ID, current view)

---

## File Structure

```
frontend/
├── src/
│   ├── api/
│   │   ├── debates.ts              # REST API calls for debates
│   │   ├── providers.ts            # Provider catalog API
│   │   └── index.ts
│   ├── components/
│   │   ├── atoms/
│   │   │   ├── Button.tsx
│   │   │   ├── Input.tsx
│   │   │   ├── Select.tsx
│   │   │   ├── Badge.tsx
│   │   │   ├── StatusIndicator.tsx
│   │   │   ├── LoadingSpinner.tsx
│   │   │   └── index.ts
│   │   ├── molecules/
│   │   │   ├── AgentCard.tsx
│   │   │   ├── MessageBubble.tsx
│   │   │   ├── ThinkingIndicator.tsx
│   │   │   ├── RoundIndicator.tsx
│   │   │   └── index.ts
│   │   ├── organisms/
│   │   │   ├── DebateConfig/
│   │   │   │   ├── index.tsx
│   │   │   │   ├── TopicInput.tsx
│   │   │   │   ├── ParticipantsList.tsx
│   │   │   │   ├── AddParticipantModal.tsx
│   │   │   │   ├── RoundsInput.tsx
│   │   │   │   └── JudgeSelect.tsx
│   │   │   ├── LiveDebate/
│   │   │   │   ├── index.tsx
│   │   │   │   ├── MessageList.tsx
│   │   │   │   └── RoundIndicator.tsx
│   │   │   ├── ParticipantsPanel/
│   │   │   │   ├── index.tsx
│   │   │   │   └── AgentStatsCard.tsx
│   │   │   ├── VerdictPanel/
│   │   │   │   ├── index.tsx
│   │   │   │   ├── WinnerAnnouncement.tsx
│   │   │   │   ├── ScoreCards.tsx
│   │   │   │   ├── KeyArguments.tsx
│   │   │   │   └── DebateSummary.tsx
│   │   │   └── index.ts
│   │   ├── templates/
│   │   │   ├── Header.tsx
│   │   │   ├── DebateLayout.tsx
│   │   │   └── index.ts
│   │   └── index.ts
│   ├── hooks/
│   │   ├── useDebateWebSocket.ts   # WebSocket connection management
│   │   ├── useAutoScroll.ts        # Auto-scroll logic
│   │   └── index.ts
│   ├── stores/
│   │   ├── debateConfigStore.ts    # Debate creation config
│   │   ├── debateStateStore.ts     # Active debate state
│   │   ├── uiStore.ts              # UI preferences
│   │   └── index.ts
│   ├── types/
│   │   ├── debate.ts               # Debate types
│   │   ├── agent.ts                # Agent types
│   │   ├── message.ts              # Message types
│   │   ├── judge.ts                # Judge types
│   │   ├── llm.ts                  # LLM config types
│   │   ├── provider.ts             # Provider catalog types
│   │   ├── websocket.ts            # WebSocket message types
│   │   └── index.ts
│   ├── utils/
│   │   ├── formatting.ts           # Date/time formatting helpers
│   │   └── index.ts
│   ├── App.tsx                     # Main app component
│   ├── main.tsx                    # React entry point
│   └── index.css                   # Tailwind directives + global styles
├── public/
├── package.json
├── tailwind.config.js              # Tailwind configuration
├── postcss.config.js               # PostCSS configuration
├── vite.config.ts                  # Vite bundler config
└── tsconfig.json                   # TypeScript config
```

---

## Dependencies to Install

```bash
# Tailwind CSS
npm install -D tailwindcss postcss autoprefixer

# State management & utilities
npm install zustand clsx date-fns

# UI components & animations
npm install framer-motion lucide-react @headlessui/react

# TypeScript types (if needed)
npm install -D @types/node
```

**Dependency rationale:**
- **zustand**: Lightweight state management (simpler than Redux)
- **clsx**: Conditional className utilities for Tailwind
- **date-fns**: Date formatting (lightweight alternative to moment.js)
- **framer-motion**: Animation library for smooth transitions
- **lucide-react**: Icon library (MIT licensed, tree-shakeable)
- **@headlessui/react**: Accessible UI primitives (modals, dropdowns)

---

## Development Workflow

### Step-by-step execution order:

1. **Setup** (Day 1)
   - Install all dependencies
   - Configure Tailwind with dark mode
   - Set up folder structure

2. **Types** (Day 1-2)
   - Create all TypeScript types mirroring backend
   - Test type imports across files

3. **Stores** (Day 2)
   - Implement Zustand stores
   - Test store actions in isolation

4. **Atoms & Molecules** (Day 3)
   - Build reusable UI components
   - Test components with Storybook or simple test page

5. **WebSocket Hook** (Day 4)
   - Implement WebSocket connection logic
   - Test reconnection scenarios

6. **Config Panel** (Day 5-6)
   - Build debate configuration UI
   - Integrate provider catalog API
   - Test debate creation flow

7. **Live Debate** (Day 7-8)
   - Build message list and real-time updates
   - Connect WebSocket events to UI
   - Test with real debate execution

8. **Participants Panel** (Day 9-10)
   - Build agent cards and basic stats
   - Show current agent status

9. **Verdict Panel** (Day 11-12)
   - Build judge result display
   - Add export functionality
   - Test with completed debates

10. **Polish** (Day 13)
    - Add animations
    - Refine dark mode styling
    - Responsive design

11. **Testing** (Day 14)
    - End-to-end testing
    - Fix bugs
    - Performance optimization

---

## Technical Considerations

### WebSocket Connection Flow

```
1. User fills out debate config
2. Click "Start Debate" → POST /api/debates
3. Backend returns debate_id
4. Frontend connects WebSocket: ws://localhost:8000/api/ws/{debate_id}
5. Backend sends connection_established event
6. Frontend calls POST /api/debates/{debate_id}/start
7. Backend runs debate, sends real-time events
8. Frontend updates UI on each event
9. On debate_complete, show verdict panel
10. Keep WebSocket open until user disconnects
```

### State Synchronization

- Backend is source of truth for debate state
- Frontend only displays data, doesn't mutate debate logic
- On reconnect, fetch latest state via `GET /api/debates/{debate_id}`
- Handle stale data by periodically syncing (every 30s during active debate)

### Error Handling Strategy

- **Network errors**: Show retry button, attempt auto-reconnect
- **Validation errors**: Show field-specific error messages
- **Backend errors**: Display error event message, allow export of partial results
- **WebSocket disconnect**: Show reconnecting indicator, exponential backoff

### Performance Considerations

- **Message list**: Use React.memo to prevent unnecessary re-renders
- **Auto-scroll**: Only trigger on new messages, not on all state updates
- **Verdict panel**: Lazy render (only mount when debate completes)
- **Large debates**: If message count exceeds 100, consider virtual scrolling (defer to future iteration)

---

## Known Limitations & Future Enhancements

### Not Included in MVP

- **Pause/Resume**: Backend doesn't support pausing debates
- **Stop**: Backend doesn't have explicit stop endpoint
- **Turn timer**: Backend doesn't send time limits per turn
- **Advanced statistics**: Momentum, evidence, toxicity, interruptions (requires complex analysis or backend support)
- **Debate timeline visualization**: Nice-to-have for showing round progression
- **Win rate tracking**: Requires multi-debate persistence
- **Speed control**: Only relevant for replay mode (future feature)
- **View Highlights**: Automatic highlight extraction (AI-powered feature for later)

### Future Enhancements (Post-MVP)

1. **Debate Library**: Browse past debates, search/filter
2. **Replay Mode**: Playback completed debates with speed control
3. **Multi-debate View**: Monitor multiple debates simultaneously
4. **Debate Templates**: Save/load preset configurations
5. **Advanced Analytics**: Sentiment analysis, argument mapping, evidence quality scores
6. **Spectator Mode**: Multiple users watching same debate with chat
7. **Agent Personas**: Pre-configured agent templates (e.g., "Devil's Advocate", "Academic Researcher")
8. **Custom Themes**: User-selectable color schemes beyond dark mode
9. **Export Highlights**: Auto-generated summary with top arguments
10. **Real-time Collaboration**: Multiple users creating debates together

---

## Verification Plan

After implementation, verify end-to-end functionality:

### Test Scenarios

1. **Create and start a debate**
   - Fill out config with 2 agents, 2 rounds
   - Select Claude 3.5 Sonnet for both agents
   - Set topic: "Should AI be regulated?"
   - Click Start → Verify debate creates and WebSocket connects
   - Observe messages appearing in real-time
   - Verify thinking indicators show between messages
   - Confirm verdict panel appears after completion

2. **Test WebSocket reconnection**
   - Start debate
   - Stop backend server mid-debate
   - Verify "Reconnecting..." indicator appears
   - Restart backend
   - Verify auto-reconnect succeeds and messages resume

3. **Test export functionality**
   - Complete a debate
   - Click Export → JSON (verify JSON downloads)
   - Click Export → Markdown (verify formatted markdown)
   - Click Export → Text (verify plain text)

4. **Test responsive design**
   - Resize browser to tablet width (768px)
   - Verify layout adapts (panels stack)
   - Resize to mobile width (375px)
   - Verify single-column layout

5. **Test dark mode**
   - Verify all text is readable
   - Check color contrast (use browser DevTools)
   - Ensure buttons/inputs are visible

6. **Test accessibility**
   - Navigate entire UI with keyboard only (Tab, Enter, Space)
   - Verify focus indicators are visible
   - Test with screen reader (optional but recommended)

### Success Criteria

✅ User can create a debate with custom agents and configuration
✅ Real-time messages appear instantly via WebSocket
✅ Thinking indicators show when agent is preparing response
✅ Verdict panel displays judge scores and winner after completion
✅ Export functionality works in all 3 formats
✅ WebSocket auto-reconnects after disconnection
✅ UI is fully functional in dark mode
✅ Responsive design works on desktop, tablet, mobile
✅ No console errors during normal operation
✅ Page load time < 2 seconds on fast connection

---

## Notes

- WebSocket endpoint is `/api/ws/{debate_id}`, not `/debates/{id}/stream` as initially mentioned
- Backend uses 0-indexed rounds, frontend should display 1-indexed (e.g., "Round 1 of 4")
- All timestamps from backend are ISO 8601 format, use `date-fns` for formatting
- Provider catalog includes "recommended" flags for suggested models
- Judge uses up to 3000 tokens (higher than debaters' default 1024)
- Backend has rate limiting between turns (1 second delay) - this is not exposed to frontend
- Export endpoints return different content types (JSON, text/markdown, text/plain)
- No authentication required in MVP (backend doesn't implement auth yet)
