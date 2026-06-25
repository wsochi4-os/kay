import { BaseProvider } from './base.js';
import type { ConversationMessage } from '../types/index.js';

/**
 * Google Gemini provider
 */
export class GeminiProvider extends BaseProvider {
  id = 'gemini';
  name = 'Google Gemini';
  endpoint = 'https://generativelanguage.googleapis.com/v1beta';
  defaultModel = 'gemini-2.0-flash';

  protected formatMessages(messages: ConversationMessage[]): any {
    // Gemini uses a different message format
    return messages.map(msg => ({
      role: msg.role === 'assistant' ? 'model' : msg.role,
      parts: [{ text: msg.content }],
    }));
  }

  async chat(messages: ConversationMessage[], options: any = {}): Promise<string> {
    const model = options.model || this.getModel();
    const maxTokens = options.maxTokens || this.getMaxTokens();
    const temperature = options.temperature || this.getTemperature();

    // Build the URL with model
    const modelPath = model.replace('/', '%2F');
    const url = `${this.endpoint}/models/${modelPath}:generateContent`;

    const response = await this.fetchWithAuth(url, {
      method: 'POST',
      body: JSON.stringify({
        contents: this.formatMessages(messages),
        generationConfig: {
          maxOutputTokens: maxTokens,
          temperature,
        },
      }),
    });

    const data = await response.json();
    
    // Handle potential error responses
    if (data.error) {
      throw new Error(data.error.message);
    }

    // Extract text from the response
    const candidates = data.candidates || [];
    if (candidates.length === 0) {
      throw new Error('No candidates returned from Gemini');
    }

    const parts = candidates[0].content?.parts || [];
    return parts.map((part: any) => part.text).join('');
  }

  async complete(prompt: string, options: any = {}): Promise<string> {
    // For completion, we'll use the chat API
    return this.chat([
      { role: 'user', content: prompt }
    ], options);
  }

  async listModels(): Promise<string[]> {
    // Gemini doesn't have a public models endpoint
    // Return known models
    return [
      'gemini-2.0-flash',
      'gemini-1.5-flash',
      'gemini-1.5-pro',
      'gemini-2.0-pro',
    ];
  }
}

export const geminiProvider = new GeminiProvider();
