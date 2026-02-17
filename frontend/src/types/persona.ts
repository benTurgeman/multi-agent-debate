/**
 * Persona models - mirrors backend/models/persona.py
 */

export enum PersonaStyle {
  AGGRESSIVE = 'aggressive',
  DIPLOMATIC = 'diplomatic',
  ANALYTICAL = 'analytical',
  SOCRATIC = 'socratic',
}

export interface PersonaTemplate {
  persona_id: string;
  name: string;
  expertise: string;
  debate_style: PersonaStyle;
  description: string;
  system_prompt_template: string;
  suggested_temperature: number;
  suggested_max_tokens: number;
  tags: string[];
}

export interface PersonaCatalogResponse {
  personas: PersonaTemplate[];
  total: number;
}
