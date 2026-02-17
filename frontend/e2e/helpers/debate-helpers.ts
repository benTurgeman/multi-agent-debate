/**
 * Debate test helpers
 * Reusable utilities for E2E testing debate flows
 */

import { Page, expect } from '@playwright/test';

export interface WebSocketMessage {
  type: string;
  payload?: any;
  timestamp?: string;
}

export interface DebateEventTracker {
  events: WebSocketMessage[];
  getEventsByType: (type: string) => WebSocketMessage[];
  waitForEvent: (type: string, timeoutMs?: number) => Promise<WebSocketMessage>;
  getLastEvent: (type: string) => WebSocketMessage | undefined;
  clear: () => void;
}

/**
 * Create a WebSocket event tracker
 * Captures all WebSocket messages for verification
 */
export function createEventTracker(page: Page): DebateEventTracker {
  const events: WebSocketMessage[] = [];

  // Intercept console.log calls that log WebSocket messages
  page.on('console', (msg) => {
    const text = msg.text();

    // Look for WebSocket message logs
    if (text.includes('WebSocket message received:') || text.includes('Received:')) {
      try {
        // Try to extract JSON from log message
        const jsonMatch = text.match(/\{.*\}/);
        if (jsonMatch) {
          const event = JSON.parse(jsonMatch[0]);
          events.push(event);
        }
      } catch (e) {
        // Ignore parse errors
      }
    }
  });

  return {
    events,

    getEventsByType: (type: string) => {
      return events.filter(e => e.type === type);
    },

    waitForEvent: async (type: string, timeoutMs: number = 30000) => {
      const startTime = Date.now();

      while (Date.now() - startTime < timeoutMs) {
        const event = events.find(e => e.type === type);
        if (event) {
          return event;
        }
        await page.waitForTimeout(100);
      }

      throw new Error(
        `Timeout waiting for event "${type}" after ${timeoutMs}ms.\n` +
        `Received events: ${events.map(e => e.type).join(', ')}`
      );
    },

    getLastEvent: (type: string) => {
      const filtered = events.filter(e => e.type === type);
      return filtered[filtered.length - 1];
    },

    clear: () => {
      events.length = 0;
    },
  };
}

/**
 * Fill debate configuration form
 */
export async function fillDebateConfig(
  page: Page,
  config: {
    topic: string;
    rounds: number;
    agent1Model: string;
    agent1Stance: string;
    agent2Model: string;
    agent2Stance: string;
    judgeModel: string;
  }
) {
  // Fill topic
  await page.fill('input[placeholder*="topic" i], textarea[placeholder*="topic" i]', config.topic);

  // Set number of rounds
  const roundsInput = page.locator('input[type="number"]').first();
  await roundsInput.clear();
  await roundsInput.fill(config.rounds.toString());

  // Configure Agent 1
  // Look for the first agent card or section
  const agent1Section = page.locator('[data-testid="agent-config-0"], .agent-config').first();

  // Fill agent 1 model
  await agent1Section.locator('select, [role="combobox"]').first().selectOption({ label: config.agent1Model });

  // Fill agent 1 stance
  const agent1StanceInput = agent1Section.locator('input[placeholder*="stance" i], textarea[placeholder*="stance" i]');
  if (await agent1StanceInput.count() > 0) {
    await agent1StanceInput.fill(config.agent1Stance);
  }

  // Configure Agent 2 - may need to add agent first
  const addAgentButton = page.locator('button:has-text("Add Agent"), button:has-text("+ Agent")');
  if (await addAgentButton.count() > 0) {
    await addAgentButton.click();
  }

  const agent2Section = page.locator('[data-testid="agent-config-1"], .agent-config').nth(1);

  // Fill agent 2 model
  await agent2Section.locator('select, [role="combobox"]').first().selectOption({ label: config.agent2Model });

  // Fill agent 2 stance
  const agent2StanceInput = agent2Section.locator('input[placeholder*="stance" i], textarea[placeholder*="stance" i]');
  if (await agent2StanceInput.count() > 0) {
    await agent2StanceInput.fill(config.agent2Stance);
  }

  // Configure Judge
  const judgeSection = page.locator('[data-testid="judge-config"], .judge-config, .judge-selection');
  await judgeSection.locator('select, [role="combobox"]').selectOption({ label: config.judgeModel });
}

/**
 * Wait for debate to complete
 */
export async function waitForDebateComplete(
  page: Page,
  timeoutMs: number = 120000
): Promise<void> {
  // Wait for "Debate Complete" status or similar indicator
  await page.waitForSelector(
    'text=/debate complete/i, [data-status="completed"], .status-completed',
    { timeout: timeoutMs }
  );
}

/**
 * Verify participant status
 */
export async function verifyParticipantStatus(
  page: Page,
  agentName: string,
  expectedStatus: string
): Promise<void> {
  const participantCard = page.locator(`[data-testid="participant-${agentName}"], .participant-card:has-text("${agentName}")`);
  await expect(participantCard).toContainText(expectedStatus, { ignoreCase: true });
}

/**
 * Get message count from UI
 */
export async function getMessageCount(page: Page): Promise<number> {
  const messages = await page.locator('[data-testid="message"], .message-bubble, .debate-message').count();
  return messages;
}

/**
 * Verify round indicator
 */
export async function verifyRoundIndicator(
  page: Page,
  currentRound: number,
  totalRounds: number
): Promise<void> {
  const roundIndicator = page.locator('[data-testid="round-indicator"], .round-indicator');

  // Should show something like "Round 1 of 2" or "1 / 2"
  const text = await roundIndicator.textContent();
  expect(text).toContain(`${currentRound}`);
  expect(text).toContain(`${totalRounds}`);
}

/**
 * Verify winner is declared
 */
export async function verifyWinnerDeclared(page: Page): Promise<string> {
  const winnerElement = page.locator('[data-testid="winner"], .winner, text=/winner/i').first();
  await expect(winnerElement).toBeVisible();

  const winnerText = await winnerElement.textContent();
  return winnerText || '';
}

/**
 * Verify export button is available
 */
export async function verifyExportAvailable(page: Page): Promise<void> {
  const exportButton = page.locator('button:has-text("Export"), [data-testid="export-button"]');
  await expect(exportButton).toBeVisible();
  await expect(exportButton).toBeEnabled();
}

/**
 * Wait for specific text to appear in debate messages
 */
export async function waitForDebateMessage(
  page: Page,
  searchText: string,
  timeoutMs: number = 30000
): Promise<void> {
  await page.waitForSelector(
    `[data-testid="message"]:has-text("${searchText}"), .message-bubble:has-text("${searchText}")`,
    { timeout: timeoutMs }
  );
}

/**
 * Capture all console logs for debugging
 */
export function captureConsoleLogs(page: Page): string[] {
  const logs: string[] = [];

  page.on('console', (msg) => {
    logs.push(`[${msg.type()}] ${msg.text()}`);
  });

  page.on('pageerror', (error) => {
    logs.push(`[ERROR] ${error.message}`);
  });

  return logs;
}

/**
 * Verify WebSocket connection is established
 */
export async function verifyWebSocketConnected(page: Page): Promise<void> {
  // Look for connection indicator
  const connectionStatus = page.locator('[data-testid="connection-status"], .connection-status');

  if (await connectionStatus.count() > 0) {
    await expect(connectionStatus).toContainText(/connected/i, { timeout: 10000 });
  }

  // Alternative: check for absence of disconnected state
  await expect(page.locator('text=/disconnected|connection failed/i')).not.toBeVisible();
}
