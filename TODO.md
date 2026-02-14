# Multi-Agent Debate System - TODO

> **Current Sprint:** Debate UI MVP (Phase 1-8)
>
> **Branch:** `feat/debate-ui-mvp`
>
> **Detailed Plan:** See [docs/phase1-plan.md](docs/phase1-plan.md) for full implementation details

---

## ✅ Completed

### Phase 1: Foundation & Setup
- [x] Install frontend dependencies (Tailwind, Zustand, Framer Motion, etc.)
- [x] Configure Tailwind CSS v4 with dark mode and custom colors
- [x] Create TypeScript type system (8 type files mirroring backend Pydantic models)
- [x] Set up Zustand stores (debateConfigStore, debateStateStore, uiStore)

### Phase 2: Core UI Components
- [x] Build atomic components (`components/atoms/`)
  - [x] Button.tsx
  - [x] Input.tsx
  - [x] Select.tsx
  - [x] Badge.tsx
  - [x] StatusIndicator.tsx
  - [x] LoadingSpinner.tsx
- [x] Build molecular components (`components/molecules/`)
  - [x] AgentCard.tsx
  - [x] MessageBubble.tsx
  - [x] ThinkingIndicator.tsx
  - [x] RoundIndicator.tsx
- [x] Create layout templates (`components/templates/`)
  - [x] Header.tsx
  - [x] DebateLayout.tsx

### Phase 3: Configuration Panel
- [x] Create API client modules (`api/`)
  - [x] debates.ts
  - [x] providers.ts
  - [x] config.ts (base API client)
- [x] Build debate config components (`organisms/DebateConfig/`)
  - [x] index.tsx (main container)
  - [x] TopicInput.tsx
  - [x] ParticipantsList.tsx
  - [x] AddParticipantModal.tsx
  - [x] RoundsInput.tsx
  - [x] JudgeSelect.tsx
- [x] Integrate config store with UI
- [x] Add form validation

**Last Commit:** `b8d274a` - feat: add molecular components and layout templates

---

## 🚧 In Progress

### Phase 4: WebSocket & Live Debate
- [ ] Build WebSocket hook (`hooks/useDebateWebSocket.ts`)
  - [ ] Connection management
  - [ ] Auto-reconnection with exponential backoff
  - [ ] Event handling
  - [ ] Heartbeat (ping every 30s)

---

## 📋 Up Next

### Phase 4: WebSocket & Live Debate (continued)
- [ ] Build WebSocket hook (`hooks/useDebateWebSocket.ts`)
  - [ ] Connection management
  - [ ] Auto-reconnection with exponential backoff
  - [ ] Event handling
  - [ ] Heartbeat (ping every 30s)
- [ ] Build live debate panel (`organisms/LiveDebate/`)
  - [ ] index.tsx
  - [ ] MessageList.tsx
  - [ ] Auto-scroll logic
- [ ] Create auto-scroll hook (`hooks/useAutoScroll.ts`)

### Phase 5: Participants Panel
- [ ] Build participants panel (`organisms/ParticipantsPanel/`)
  - [ ] index.tsx
  - [ ] AgentStatsCard.tsx
- [ ] Show agent status (thinking/waiting/completed)
- [ ] Display message counts

### Phase 6: Verdict Panel
- [ ] Build verdict panel (`organisms/VerdictPanel/`)
  - [ ] index.tsx (with slide-up animation)
  - [ ] WinnerAnnouncement.tsx
  - [ ] ScoreCards.tsx
  - [ ] KeyArguments.tsx
  - [ ] DebateSummary.tsx
- [ ] Add export functionality
  - [ ] JSON export
  - [ ] Markdown export
  - [ ] Text export

### Phase 7: Integration & Polish
- [ ] Integrate all components in App.tsx
  - [ ] Compose layout with all organisms
  - [ ] Handle view navigation (config → debate → results)
  - [ ] Manage global state
- [ ] Add animations with Framer Motion
  - [ ] Message fade-in
  - [ ] Thinking indicator pulse
  - [ ] Verdict slide-up
- [ ] Implement responsive design
  - [ ] Desktop (1440px+)
  - [ ] Tablet (768px)
  - [ ] Mobile (640px)

### Phase 8: Testing & Refinement
- [ ] End-to-end testing
  - [ ] Create debate with 2 agents, 2 rounds
  - [ ] Start debate and observe real-time messages
  - [ ] Verify thinking indicators
  - [ ] Check verdict panel display
  - [ ] Test export in all 3 formats
  - [ ] Test WebSocket reconnection
- [ ] Bug fixes
- [ ] Performance optimization
- [ ] Accessibility checks

---

## 🎯 Definition of Done (MVP)

- [ ] User can create a debate with custom agents and configuration
- [ ] Real-time messages appear instantly via WebSocket
- [ ] Thinking indicators show when agent is preparing response
- [ ] Verdict panel displays judge scores and winner after completion
- [ ] Export functionality works in all 3 formats (JSON, Markdown, Text)
- [ ] WebSocket auto-reconnects after disconnection
- [ ] UI is fully functional in dark mode
- [ ] Responsive design works on desktop, tablet, mobile
- [ ] No console errors during normal operation
- [ ] Page load time < 2 seconds on fast connection

---

## 🚀 Future Enhancements (Post-MVP)

- [ ] Debate Library (browse past debates)
- [ ] Replay Mode (playback with speed control)
- [ ] Multi-debate View (monitor multiple debates)
- [ ] Debate Templates (save/load presets)
- [ ] Advanced Analytics (sentiment, argument mapping)
- [ ] Spectator Mode (multi-user with chat)
- [ ] Agent Personas (pre-configured templates)
- [ ] Custom Themes (beyond dark mode)
- [ ] Export Highlights (auto-generated summaries)
- [ ] Real-time Collaboration

---

## 📝 Notes

- **Backend Status:** Complete with WebSocket support at `/api/ws/{debate_id}`
- **WebSocket Events:** `connection_established`, `debate_started`, `round_started`, `agent_thinking`, `message_received`, `judge_result`, `debate_complete`, `error`
- **Backend uses 0-indexed rounds:** Frontend should display as 1-indexed
- **No authentication required** in MVP
- **Provider catalog API:** `GET /api/providers` for model selection

---

## 🔄 How to Use This TODO

1. **Starting work:** Check "In Progress" and "Up Next" sections
2. **After completing a task:** Move it to "Completed" with `[x]`
3. **Committing:** Update this file in the same commit as your work
4. **New session:** Read this file first to understand current state
5. **Context cleared:** This persists - use it as source of truth

---

**Last Updated:** 2026-02-14
