/**
 * Message models - mirrors backend/models/message.py
 */

export interface Message {
  agent_id: string;
  agent_name: string;
  content: string;
  round_number: number;
  turn_number: number;
  timestamp: string; // ISO format datetime
  stance: string;
}

export interface MessageHistory {
  messages: Message[];
}
