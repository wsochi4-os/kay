import { BaseProvider } from './base.js';
import type { ConversationMessage } from '../types/index.js';

/**
 * OpenRouter provider - Aggregator with many free models
 */
export class OpenRouterProvider extends BaseProvider {
  id = 'openrouter';
  name = 'OpenRouter';
  endpoint = 'https://openrouter.ai/api/v1';
  defaultModel = 'meta-llama/llama-3.1-70b-instruct:free';

  async chat(messages: ConversationMessage[], options: any = {}): Promise<string> {
    const model = options.model || this.getModel();
    const maxTokens = options.maxTokens || this.getMaxTokens();
    const temperature = options.temperature || this.getTemperature();

    const url = `${this.endpoint}/chat/completions`;

    // OpenRouter uses OpenAI-compatible API
    const response = await this.fetchWithAuth(url, {
      method: 'POST',
      body: JSON.stringify({
        model,
        messages: this.formatMessages(messages),
        max_tokens: maxTokens,
        temperature,
        stream: false,
      }),
      headers: {
        'HTTP-Referer': 'https://github.com/wsochi4-os/kay',
        'X-Title': 'Kutti CLI',
      },
    });

    const data = await response.json();
    return data.choices[0].message.content;
  }

  async complete(prompt: string, options: any = {}): Promise<string> {
    const model = options.model || this.getModel();
    const maxTokens = options.maxTokens || this.getMaxTokens();
    const temperature = options.temperature || this.getTemperature();

    const url = `${this.endpoint}/completions`;

    const response = await this.fetchWithAuth(url, {
      method: 'POST',
      body: JSON.stringify({
        model,
        prompt,
        max_tokens: maxTokens,
        temperature,
        stream: false,
      }),
      headers: {
        'HTTP-Referer': 'https://github.com/wsochi4-os/kay',
        'X-Title': 'Kutti CLI',
      },
    });

    const data = await response.json();
    return data.choices[0].text;
  }

  async listModels(): Promise<string[]> {
    const url = `${this.endpoint}/models`;
    
    try {
      const response = await this.fetchWithAuth(url);
      const data = await response.json();
      return data.data.map((model: any) => model.id);
    } catch (error) {
      // Return some known free models
      return [
        'meta-llama/llama-3.1-70b-instruct:free',
        'meta-llama/llama-3.1-8b-instruct:free',
        'mistralai/mistral-7b-instruct:free',
        'mistralai/mixtral-8x7b-instruct:free',
        'openchat/openchat-7b:free',
        'gryphe/mythomax-l2-13b:free',
      ];
    }
  }

  /**
   * Get information about a specific model
   */
  async getModelInfo(modelId: string): Promise<any> {
    const url = `${this.endpoint}/models/${encodeURIComponent(modelId)}`;
    
    try {
      const response = await this.fetchWithAuth(url);
      return await response.json();
    } catch (error) {
      return null;
    }
  }
}

export const openrouterProvider = new OpenRouterProvider();
