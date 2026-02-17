/**
 * LLM provider models - mirrors backend/models/llm.py
 */

export enum ModelProvider {
  ANTHROPIC = 'anthropic',
  OPENAI = 'openai',
}

export interface LLMConfig {
  provider: ModelProvider;
  model_name: string;
  api_key_env_var: string;
}
