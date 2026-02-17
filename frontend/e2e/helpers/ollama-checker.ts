/**
 * Ollama availability checker
 * Verifies that Ollama is running and required models are available
 */

export interface OllamaModel {
  name: string;
  modified_at: string;
  size: number;
}

export interface OllamaListResponse {
  models: OllamaModel[];
}

/**
 * Check if Ollama is running
 */
export async function isOllamaRunning(): Promise<boolean> {
  try {
    const response = await fetch('http://localhost:11434/api/tags');
    return response.ok;
  } catch (error) {
    return false;
  }
}

/**
 * Get list of available Ollama models
 */
export async function getAvailableModels(): Promise<string[]> {
  try {
    const response = await fetch('http://localhost:11434/api/tags');
    if (!response.ok) {
      throw new Error(`Ollama API returned ${response.status}`);
    }

    const data: OllamaListResponse = await response.json();
    return data.models.map(m => m.name);
  } catch (error) {
    console.error('Failed to get Ollama models:', error);
    return [];
  }
}

/**
 * Check if a specific model is available
 */
export async function isModelAvailable(modelName: string): Promise<boolean> {
  const models = await getAvailableModels();
  // Handle both "mistral:7b" and "mistral" formats
  return models.some(m => m === modelName || m.startsWith(`${modelName}:`));
}

/**
 * Wait for Ollama to be ready
 */
export async function waitForOllama(
  timeoutMs: number = 10000,
  intervalMs: number = 1000
): Promise<void> {
  const startTime = Date.now();

  while (Date.now() - startTime < timeoutMs) {
    if (await isOllamaRunning()) {
      return;
    }
    await new Promise(resolve => setTimeout(resolve, intervalMs));
  }

  throw new Error(`Ollama did not become ready within ${timeoutMs}ms`);
}

/**
 * Verify test prerequisites
 * Throws an error with helpful message if prerequisites are not met
 */
export async function verifyTestPrerequisites(requiredModel: string = 'mistral'): Promise<void> {
  // Check if Ollama is running
  const ollamaRunning = await isOllamaRunning();
  if (!ollamaRunning) {
    throw new Error(
      'Ollama is not running. Please start Ollama before running E2E tests.\n' +
      'Install: https://ollama.ai\n' +
      'Start: Run "ollama serve" in terminal'
    );
  }

  // Check if required model is available
  const modelAvailable = await isModelAvailable(requiredModel);
  if (!modelAvailable) {
    const availableModels = await getAvailableModels();
    throw new Error(
      `Required model "${requiredModel}" is not available.\n` +
      `Available models: ${availableModels.join(', ')}\n` +
      `To install: ollama pull ${requiredModel}`
    );
  }

  console.log(`✓ Ollama is running with model "${requiredModel}"`);
}
