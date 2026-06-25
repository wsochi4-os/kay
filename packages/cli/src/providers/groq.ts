import { BaseProvider } from './base.js';
import type { ConversationMessage } from '../types/index.js';

/**
 * Groq provider - OpenAI-compatible API
 */
export class GroqProvider extends BaseProvider {
  id = 'groq';
  name = 'Groq';
  endpoint = 'https://api.groq.com/openai/v1';
  defaultModel = 'llama-3.3-70b-versatile';

  async chat(messages: ConversationMessage[], options: any = {}): Promise<string> {
    const url = `${this.endpoint}/chat/completions`;
    const model = options.model || this.getModel();
    const maxTokens = options.maxTokens || this.getMaxTokens();
    const temperature = options.temperature || this.getTemperature();

    const response = await this.fetchWithAuth(url, {
      method: 'POST',
      body: JSON.stringify({
        model,
        messages: this.formatMessages(messages),
        max_tokens: maxTokens,
        temperature,
        stream: false,
      }),
    });

    const data = await response.json();
    return data.choices[0].message.content;
  }

  async complete(prompt: string, options: any = {}): Promise<string> {
    const url = `${this.endpoint}/completions`;
    const model = options.model || this.getModel();
    const maxTokens = options.maxTokens || this.getMaxTokens();
    const temperature = options.temperature || this.getTemperature();

    const response = await this.fetchWithAuth(url, {
      method: 'POST',
      body: JSON.stringify({
        model,
        prompt,
        max_tokens: maxTokens,
        temperature,
        stream: false,
      }),
    });

    const data = await response.json();
    return data.choices[0].text;
  }

  async listModels(): Promise<string[]> {
    const url = `${this.endpoint}/models`;
    const response = await this.fetchWithAuth(url);
    const data = await response.json();
    return data.data.map((model: any) => model.id);
  }
}

export const groqProvider = new GroqProvider();
