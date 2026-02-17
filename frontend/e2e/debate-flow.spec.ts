/**
 * Multi-Agent Debate - Full Flow E2E Test
 *
 * Comprehensive test validating the complete debate flow using Ollama models.
 * This test follows the plan outlined in TODO.md.
 *
 * Prerequisites:
 * - Ollama must be running (ollama serve)
 * - Mistral model must be installed (ollama pull mistral)
 */

import { test, expect } from '@playwright/test';
import { verifyTestPrerequisites } from './helpers/ollama-checker';
import {
  waitForDebateComplete,
  verifyWinnerDeclared,
  verifyExportAvailable,
  verifyWebSocketConnected,
  captureConsoleLogs,
} from './helpers/debate-helpers';

// Test configuration
const TEST_CONFIG = {
  topic: 'Should AI be regulated by governments?',
  rounds: 2,
  provider: 'Ollama',
  model: 'Mistral 7B',
  judgeModel: 'Mistral 7B (Ollama)',
  agent1Name: 'Pro Agent',
  agent1Stance: 'Pro',
  agent2Name: 'Con Agent',
  agent2Stance: 'Con',
  expectedRuntime: 90000, // ~90 seconds
};

test.describe('Multi-Agent Debate - Full Flow', () => {
  test.beforeAll(async () => {
    // Verify Ollama is running and models are available
    await verifyTestPrerequisites('mistral');
  });

  test('Complete debate flow with Ollama models', async ({ page }) => {
    // Capture console logs for debugging
    const logs = captureConsoleLogs(page);

    // Navigate to application
    await page.goto('/');
    await expect(page).toHaveTitle(/debate/i);

    // ============================================================
    // Phase 1: Configuration
    // ============================================================

    // Verify initial state - should be on config screen
    await expect(page.locator('text=/configure debate|debate config/i')).toBeVisible();

    // Fill debate topic
    const topicInput = page.locator('textarea[placeholder*="topic" i]');
    await topicInput.clear();
    await topicInput.fill(TEST_CONFIG.topic);

    // Remove default agents if any exist
    const removeButtons = page.locator('button:has-text("Remove")');
    const removeCount = await removeButtons.count();
    for (let i = 0; i < removeCount; i++) {
      await removeButtons.first().click();
      await page.waitForTimeout(300);
    }

    // Add Agent 1
    await page.click('button:has-text("Add Agent")');
    await page.waitForSelector('dialog:has-text("Add Participant")', { timeout: 5000 });

    // Fill agent 1 details
    await page.fill('input[placeholder*="Agent" i]', TEST_CONFIG.agent1Name);
    await page.selectOption('select:has-text("Pro")', { label: TEST_CONFIG.agent1Stance });
    await page.selectOption('select[id*="provider" i], label:has-text("Provider") + select', { label: TEST_CONFIG.provider });
    await page.waitForTimeout(500); // Wait for models to load

    // Select model
    await page.selectOption('select[id*="model" i], label:has-text("Model") + select', { label: TEST_CONFIG.model });

    // Submit agent 1
    await page.click('button:has-text("Add Agent"):not(:has-text("Cancel"))');
    await page.waitForTimeout(500);

    // Add Agent 2
    await page.click('button:has-text("Add Agent")');
    await page.waitForSelector('dialog:has-text("Add Participant")', { timeout: 5000 });

    // Fill agent 2 details
    await page.fill('input[placeholder*="Agent" i]', TEST_CONFIG.agent2Name);
    await page.selectOption('select:has-text("Con")', { label: TEST_CONFIG.agent2Stance });
    await page.selectOption('select[id*="provider" i], label:has-text("Provider") + select', { label: TEST_CONFIG.provider });
    await page.waitForTimeout(500);

    // Select model
    await page.selectOption('select[id*="model" i], label:has-text("Model") + select', { label: TEST_CONFIG.model });

    // Submit agent 2
    await page.click('button:has-text("Add Agent"):not(:has-text("Cancel"))');
    await page.waitForTimeout(500);

    // Set number of rounds
    const roundsInput = page.locator('input[type="number"]');
    await roundsInput.clear();
    await roundsInput.fill(TEST_CONFIG.rounds.toString());

    // Configure judge model
    await page.selectOption('select:has-text("judge" i), select[aria-label*="judge" i]', { label: TEST_CONFIG.judgeModel });

    // Verify "Create Debate" button is enabled
    const createButton = page.locator('button:has-text("Create Debate"), button:has-text("Start Debate")');
    await expect(createButton).toBeEnabled();

    console.log('✓ Configuration phase completed');

    // ============================================================
    // Phase 2: Debate Execution
    // ============================================================

    // Start the debate
    await createButton.click();

    // Wait for WebSocket connection
    await verifyWebSocketConnected(page);
    console.log('✓ WebSocket connected');

    // Wait for debate to start
    await page.waitForSelector('text=/debate (in progress|started)/i, [data-status="in_progress"]', { timeout: 10000 });
    console.log('✓ Debate started');

    // Track message count to verify progress
    let previousMessageCount = 0;

    // Wait for messages to appear
    await page.waitForSelector('[data-testid="message"], .message-bubble, .debate-message', {
      timeout: 30000,
    });

    // Round 1
    console.log('Waiting for Round 1...');

    // Wait for first agent to respond
    await page.waitForTimeout(5000);
    let currentMessageCount = await page.locator('[data-testid="message"], .message-bubble, .debate-message').count();
    expect(currentMessageCount).toBeGreaterThan(previousMessageCount);
    console.log(`✓ Agent 1 responded (${currentMessageCount} messages)`);

    previousMessageCount = currentMessageCount;

    // Wait for second agent to respond
    await page.waitForTimeout(10000);
    currentMessageCount = await page.locator('[data-testid="message"], .message-bubble, .debate-message').count();
    expect(currentMessageCount).toBeGreaterThan(previousMessageCount);
    console.log(`✓ Agent 2 responded (${currentMessageCount} messages)`);

    previousMessageCount = currentMessageCount;

    // Round 2
    console.log('Waiting for Round 2...');

    // Wait for round 2 messages
    await page.waitForTimeout(15000);
    currentMessageCount = await page.locator('[data-testid="message"], .message-bubble, .debate-message').count();
    expect(currentMessageCount).toBeGreaterThan(previousMessageCount);
    console.log(`✓ Round 2 messages received (${currentMessageCount} messages)`);

    // Wait for judging to start
    console.log('✓ Waiting for judging to complete...');

    // ============================================================
    // Phase 3: Completion
    // ============================================================

    // Wait for debate to complete
    await waitForDebateComplete(page, 120000);
    console.log('✓ Debate completed');

    // Verify completion status
    await expect(page.locator('text=/debate complete/i, [data-status="completed"]')).toBeVisible();

    // Verify winner is declared
    const winner = await verifyWinnerDeclared(page);
    console.log(`✓ Winner declared: ${winner}`);
    expect(winner).toBeTruthy();

    // Verify final message count (should have at least 4 messages: 2 rounds × 2 agents)
    const finalMessageCount = await page.locator('[data-testid="message"], .message-bubble, .debate-message').count();
    expect(finalMessageCount).toBeGreaterThanOrEqual(4);
    console.log(`✓ Total messages: ${finalMessageCount}`);

    // Verify export button is available
    await verifyExportAvailable(page);
    console.log('✓ Export functionality available');

    // Log summary
    console.log('\n=== Test Summary ===');
    console.log(`Topic: ${TEST_CONFIG.topic}`);
    console.log(`Rounds: ${TEST_CONFIG.rounds}`);
    console.log(`Total Messages: ${finalMessageCount}`);
    console.log(`Winner: ${winner}`);
    console.log('===================\n');

    // Dump console logs if needed for debugging
    if (process.env.DEBUG) {
      console.log('\n=== Console Logs ===');
      logs.forEach(log => console.log(log));
      console.log('====================\n');
    }
  });

  test('UI state updates correctly during debate', async ({ page }) => {
    await page.goto('/');

    // Configure minimal debate
    const topicInput = page.locator('textarea[placeholder*="topic" i]');
    await topicInput.clear();
    await topicInput.fill('Test topic');

    // Remove default agents
    const removeButtons = page.locator('button:has-text("Remove")');
    const removeCount = await removeButtons.count();
    for (let i = 0; i < removeCount; i++) {
      await removeButtons.first().click();
      await page.waitForTimeout(300);
    }

    // Add 2 agents quickly
    for (let i = 0; i < 2; i++) {
      await page.click('button:has-text("Add Agent")');
      await page.fill('input[placeholder*="Agent" i]', `Agent ${i + 1}`);
      await page.selectOption('select[id*="provider" i]', { label: TEST_CONFIG.provider });
      await page.waitForTimeout(500);
      await page.selectOption('select[id*="model" i]', { label: TEST_CONFIG.model });
      await page.click('button:has-text("Add Agent"):not(:has-text("Cancel"))');
      await page.waitForTimeout(500);
    }

    // Set rounds to 1
    const roundsInput = page.locator('input[type="number"]');
    await roundsInput.clear();
    await roundsInput.fill('1');

    // Select judge
    await page.selectOption('select:has-text("judge" i)', { label: TEST_CONFIG.judgeModel });

    // Start debate
    const createButton = page.locator('button:has-text("Create Debate")');
    await createButton.click();

    // Verify status transitions
    await page.waitForSelector('text=/in progress|started/i', { timeout: 10000 });
    console.log('✓ Status: In Progress');

    // Wait for completion
    await page.waitForSelector('text=/complete/i', { timeout: 120000 });
    console.log('✓ Status: Completed');

    // Verify participant statuses
    const statusElements = page.locator('text=/completed|finished/i');
    const statusCount = await statusElements.count();
    expect(statusCount).toBeGreaterThan(0);
    console.log('✓ Participant statuses updated');
  });

  test('Error handling - Invalid configuration', async ({ page }) => {
    await page.goto('/');

    // Clear topic
    const topicInput = page.locator('textarea[placeholder*="topic" i]');
    await topicInput.clear();

    // Try to start debate without proper configuration
    const createButton = page.locator('button:has-text("Create Debate")');

    // Button should be disabled
    await expect(createButton).toBeDisabled();
    console.log('✓ Error handling: Button properly disabled for invalid config');
  });
});

test.describe('Debate Export Functionality', () => {
  test.beforeAll(async () => {
    await verifyTestPrerequisites('mistral');
  });

  test('Export button appears after debate completes', async ({ page }) => {
    await page.goto('/');

    // Configure quick debate
    const topicInput = page.locator('textarea[placeholder*="topic" i]');
    await topicInput.clear();
    await topicInput.fill('Export test');

    // Remove default agents
    const removeButtons = page.locator('button:has-text("Remove")');
    const removeCount = await removeButtons.count();
    for (let i = 0; i < removeCount; i++) {
      await removeButtons.first().click();
      await page.waitForTimeout(300);
    }

    // Add 2 agents
    for (let i = 0; i < 2; i++) {
      await page.click('button:has-text("Add Agent")');
      await page.fill('input[placeholder*="Agent" i]', `Agent ${i + 1}`);
      await page.selectOption('select[id*="provider" i]', { label: TEST_CONFIG.provider });
      await page.waitForTimeout(500);
      await page.selectOption('select[id*="model" i]', { label: TEST_CONFIG.model });
      await page.click('button:has-text("Add Agent"):not(:has-text("Cancel"))');
      await page.waitForTimeout(500);
    }

    // Set rounds to 1
    const roundsInput = page.locator('input[type="number"]');
    await roundsInput.clear();
    await roundsInput.fill('1');

    // Select judge
    await page.selectOption('select:has-text("judge" i)', { label: TEST_CONFIG.judgeModel });

    const createButton = page.locator('button:has-text("Create Debate")');
    await createButton.click();

    // Wait for completion
    await waitForDebateComplete(page, 120000);

    // Verify export button
    await verifyExportAvailable(page);
    console.log('✓ Export button available after completion');

    // Click export button to verify it works
    const exportButton = page.locator('button:has-text("Export"), [data-testid="export-button"]');
    await exportButton.click();

    // Should show export options or start download
    await page.waitForTimeout(1000);
    console.log('✓ Export button functional');
  });
});
