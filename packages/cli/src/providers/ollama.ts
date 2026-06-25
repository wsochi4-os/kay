import { BaseProvider } from './base.js';
import type { ConversationMessage } from '../types/index.js';

/**
 * Ollama provider - Local LLM inference
 */
export class OllamaProvider extends BaseProvider {
  id = 'ollama';
  name = 'Ollama';
  endpoint = 'http://localhost:11434/v1';
  defaultModel = 'llama3.3';

  constructor() {
    super();
    // Ollama doesn't require authentication
    this.endpoint = process.env.OLLAMA_HOST || this.endpoint;
  }

  async chat(messages: ConversationMessage[], options: any = {}): Promise<string> {
    const model = options.model || this.getModel();
    const maxTokens = options.maxTokens || this.getMaxTokens();
    const temperature = options.temperature || this.getTemperature();

    const url = `${this.endpoint}/chat/completions`;

    // Ollama uses OpenAI-compatible API
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        model,
        messages: this.formatMessages(messages),
        max_tokens: maxTokens,
        temperature,
        stream: false,
      }),
    });

    if (!response.ok) {
      const error = await response.text();
      throw new Error(`Ollama error: ${response.status} - ${error}`);
    }

    const data = await response.json();
    return data.choices[0].message.content;
  }

  async complete(prompt: string, options: any = {}): Promise<string> {
    const model = options.model || this.getModel();
    const maxTokens = options.maxTokens || this.getMaxTokens();
    const temperature = options.temperature || this.getTemperature();

    const url = `${this.endpoint}/completions`;

    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        model,
        prompt,
        max_tokens: maxTokens,
        temperature,
        stream: false,
      }),
    });

    if (!response.ok) {
      const error = await response.text();
      throw new Error(`Ollama error: ${response.status} - ${error}`);
    }

    const data = await response.json();
    return data.choices[0].text;
  }

  async listModels(): Promise<string[]> {
    const url = `${this.endpoint}/models`;
    
    try {
      const response = await fetch(url);
      if (!response.ok) {
        // If Ollama isn't running, return default models
        return [
          'llama3.3',
          'llama3.2',
          'llama3.1',
          'llama3',
          'mistral',
          'mixtral',
        ];
      }
      
      const data = await response.json();
      return data.data.map((model: any) => model.id);
    } catch (error) {
      // Return default models if we can't connect
      return [
        'llama3.3',
        'llama3.2',
        'llama3.1',
        'llama3',
        'mistral',
        'mixtral',
      ];
    }
  }

  /**
   * Check if Ollama is running
   */
  async isRunning(): Promise<boolean> {
    try {
      const response = await fetch(`${this.endpoint}/models`);
      return response.ok;
    } catch (error) {
      return false;
    }
  }

  /**
   * Pull a model from Ollama registry
   */
  async pullModel(modelName: string): Promise<string> {
    const url = `${this.endpoint.replace('/v1', '')}/api/pull`;
    
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        name: modelName,
      }),
    });

    if (!response.ok) {
      const error = await response.text();
      throw new Error(`Failed to pull model: ${error}`);
    }

    return `Model ${modelName} pulled successfully`;
  }
}

export const ollamaProvider = new OllamaProvider();
