/**
 * Persona Feature E2E Test
 *
 * Tests the complete persona selection and integration flow.
 *
 * Prerequisites:
 * - Backend must be running
 * - Ollama must be running with mistral model
 */

import { test, expect } from '@playwright/test';

test.describe('Persona Feature', () => {
  test('Persona selector loads and populates form', async ({ page }) => {
    // Navigate to application
    await page.goto('/');

    // Remove any existing default agents
    const removeButtons = page.locator('button:has-text("Remove")');
    const removeCount = await removeButtons.count();
    for (let i = 0; i < removeCount; i++) {
      await removeButtons.first().click();
      await page.waitForTimeout(300);
    }

    // Open Add Agent modal
    await page.click('button:has-text("Add Agent")');
    await page.waitForSelector('dialog:has-text("Add Participant")', {
      timeout: 5000,
    });

    // Wait for persona selector to load
    await page.waitForSelector('label:has-text("Persona Template")', {
      timeout: 5000,
    });

    // Verify persona selector is visible and has loaded options
    const personaSelect = page.locator('select', {
      has: page.locator('option:has-text("Socratic Philosopher")'),
    });
    await expect(personaSelect).toBeVisible();

    // Verify "None (Custom)" option exists
    await expect(
      personaSelect.locator('option:has-text("None (Custom)")')
    ).toBeVisible();

    // Verify all expected personas are loaded
    const expectedPersonas = [
      'Socratic Philosopher',
      'Data Scientist',
      'Trial Lawyer',
      'Academic Researcher',
      'Political Strategist',
      'Entrepreneur',
      'Ethicist',
      'Investigative Journalist',
    ];

    for (const personaName of expectedPersonas) {
      await expect(
        personaSelect.locator(`option:has-text("${personaName}")`)
      ).toBeVisible();
    }

    // Select "Socratic Philosopher" persona
    await personaSelect.selectOption({ label: 'Socratic Philosopher' });
    await page.waitForTimeout(500); // Allow form to update

    // Verify persona details card appears
    await expect(
      page.locator('text=Logic and Epistemology')
    ).toBeVisible();
    await expect(
      page.locator('text=Questions assumptions, seeks truth through inquiry')
    ).toBeVisible();

    // Verify form fields are populated
    const agentNameInput = page.locator('input[placeholder*="Agent" i]');
    await expect(agentNameInput).toHaveValue('Socratic Philosopher');

    // Verify system prompt is populated and contains persona-specific content
    const systemPromptTextarea = page.locator('textarea');
    const promptValue = await systemPromptTextarea.inputValue();
    expect(promptValue).toContain('philosopher');
    expect(promptValue).toContain('Socratic');

    // Verify temperature field is set to persona's suggested value (0.7)
    const temperatureInput = page.locator('input[label*="Temperature" i]');
    const tempValue = await temperatureInput.inputValue();
    expect(parseFloat(tempValue)).toBeCloseTo(0.7, 1);

    // Verify max tokens field is set
    const maxTokensInput = page.locator('input[label*="Max Tokens" i]');
    const tokensValue = await maxTokensInput.inputValue();
    expect(parseInt(tokensValue)).toBe(1024);

    // Verify fields are still editable - change agent name
    await agentNameInput.clear();
    await agentNameInput.fill('Custom Philosopher Name');
    await expect(agentNameInput).toHaveValue('Custom Philosopher Name');

    // Close modal
    await page.click('button:has-text("Cancel")');
  });

  test('Persona selection updates prompt when stance changes', async ({
    page,
  }) => {
    // Navigate and open modal
    await page.goto('/');

    const removeButtons = page.locator('button:has-text("Remove")');
    const removeCount = await removeButtons.count();
    for (let i = 0; i < removeCount; i++) {
      await removeButtons.first().click();
      await page.waitForTimeout(300);
    }

    await page.click('button:has-text("Add Agent")');
    await page.waitForSelector('dialog:has-text("Add Participant")');

    // Select a persona
    const personaSelect = page.locator('select', {
      has: page.locator('option:has-text("Trial Lawyer")'),
    });
    await personaSelect.selectOption({ label: 'Trial Lawyer' });
    await page.waitForTimeout(500);

    // Get initial system prompt
    const systemPromptTextarea = page.locator('textarea');
    const initialPrompt = await systemPromptTextarea.inputValue();

    // Change stance from Pro to Con
    const stanceSelect = page.locator('select', {
      has: page.locator('option:has-text("Con")'),
    });
    await stanceSelect.selectOption({ label: 'Con (Against)' });
    await page.waitForTimeout(500);

    // Verify system prompt updated with new stance
    const updatedPrompt = await systemPromptTextarea.inputValue();
    expect(updatedPrompt).toContain('Con');
    expect(updatedPrompt).not.toEqual(initialPrompt);

    await page.click('button:has-text("Cancel")');
  });

  test('Can create agent with persona and run debate', async ({ page }) => {
    // Set a longer timeout for this test since it runs a debate
    test.setTimeout(120000);

    await page.goto('/');

    // Set topic
    const topicInput = page.locator('textarea[placeholder*="topic" i]');
    await topicInput.clear();
    await topicInput.fill('Is philosophy still relevant in modern society?');

    // Remove default agents
    const removeButtons = page.locator('button:has-text("Remove")');
    const removeCount = await removeButtons.count();
    for (let i = 0; i < removeCount; i++) {
      await removeButtons.first().click();
      await page.waitForTimeout(300);
    }

    // Add Agent 1 with Socratic Philosopher persona
    await page.click('button:has-text("Add Agent")');
    await page.waitForSelector('dialog:has-text("Add Participant")');

    // Select Socratic Philosopher
    const personaSelect1 = page.locator('select', {
      has: page.locator('option:has-text("Socratic Philosopher")'),
    });
    await personaSelect1.selectOption({ label: 'Socratic Philosopher' });
    await page.waitForTimeout(500);

    // Select Ollama provider and model
    await page.selectOption(
      'select[id*="provider" i], label:has-text("Provider") + select',
      { label: 'Ollama' }
    );
    await page.waitForTimeout(500);
    await page.selectOption(
      'select[id*="model" i], label:has-text("Model") + select',
      { label: 'Mistral 7B' }
    );

    await page.click('button:has-text("Add Agent"):not(:has-text("Cancel"))');
    await page.waitForTimeout(500);

    // Add Agent 2 with Data Scientist persona
    await page.click('button:has-text("Add Agent")');
    await page.waitForSelector('dialog:has-text("Add Participant")');

    const personaSelect2 = page.locator('select', {
      has: page.locator('option:has-text("Data Scientist")'),
    });
    await personaSelect2.selectOption({ label: 'Data Scientist' });
    await page.waitForTimeout(500);

    // Change stance to Con
    await page.selectOption('select:has-text("Con")', {
      label: 'Con (Against)',
    });

    // Select Ollama provider and model
    await page.selectOption(
      'select[id*="provider" i], label:has-text("Provider") + select',
      { label: 'Ollama' }
    );
    await page.waitForTimeout(500);
    await page.selectOption(
      'select[id*="model" i], label:has-text("Model") + select',
      { label: 'Mistral 7B' }
    );

    await page.click('button:has-text("Add Agent"):not(:has-text("Cancel"))');
    await page.waitForTimeout(500);

    // Verify both agents are added with correct names
    await expect(page.locator('text=Socratic Philosopher')).toBeVisible();
    await expect(page.locator('text=Data Scientist')).toBeVisible();

    // Select judge
    await page.selectOption('select', { label: 'Mistral 7B (Ollama)' });

    // Set rounds to 1 for faster testing
    const roundsInput = page.locator('input[type="number"]');
    await roundsInput.clear();
    await roundsInput.fill('1');

    // Start debate
    await page.click('button:has-text("Start Debate")');

    // Wait for debate to start
    await expect(page.locator('text=/Round 1/i')).toBeVisible({
      timeout: 10000,
    });

    // Wait for first agent response
    await expect(
      page.locator('text=/Socratic Philosopher|Data Scientist/i').first()
    ).toBeVisible({ timeout: 30000 });

    // Wait for debate to complete (with generous timeout)
    await page.waitForSelector('text=/Winner|Debate Complete/i', {
      timeout: 90000,
    });

    // Verify debate completed successfully
    await expect(page.locator('text=/Winner|verdict/i')).toBeVisible();
  });

  test('Custom mode works when no persona selected', async ({ page }) => {
    await page.goto('/');

    const removeButtons = page.locator('button:has-text("Remove")');
    const removeCount = await removeButtons.count();
    for (let i = 0; i < removeCount; i++) {
      await removeButtons.first().click();
      await page.waitForTimeout(300);
    }

    await page.click('button:has-text("Add Agent")');
    await page.waitForSelector('dialog:has-text("Add Participant")');

    // Ensure "None (Custom)" is selected
    const personaSelect = page.locator('select', {
      has: page.locator('option:has-text("None (Custom)")'),
    });
    await personaSelect.selectOption({ label: 'None (Custom)' });
    await page.waitForTimeout(300);

    // Verify no persona details card is shown
    await expect(page.locator('text=Logic and Epistemology')).not.toBeVisible();

    // Manually fill in agent details
    const agentNameInput = page.locator('input[placeholder*="Agent" i]');
    await agentNameInput.fill('Custom Agent');

    // Verify system prompt is empty (using default placeholder behavior)
    const systemPromptTextarea = page.locator('textarea');
    const promptValue = await systemPromptTextarea.inputValue();
    expect(promptValue).toBe('');

    // Verify temperature and max tokens are at default values
    const temperatureInput = page.locator('input[label*="Temperature" i]');
    const tempValue = await temperatureInput.inputValue();
    expect(parseFloat(tempValue)).toBe(1.0);

    const maxTokensInput = page.locator('input[label*="Max Tokens" i]');
    const tokensValue = await maxTokensInput.inputValue();
    expect(parseInt(tokensValue)).toBe(1024);

    await page.click('button:has-text("Cancel")');
  });
});
