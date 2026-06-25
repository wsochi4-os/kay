import fetch from 'node-fetch';
import { authManager } from '../auth/manager.js';
import { configManager } from '../utils/config.js';
import { logger } from '../utils/logger.js';
import type { ConversationMessage } from '../types/index.js';

/**
 * Base provider interface
 */
export interface Provider {
  id: string;
  name: string;
  endpoint: string;
  defaultModel: string;
  
  chat(messages: ConversationMessage[], options?: any): Promise<string>;
  complete(prompt: string, options?: any): Promise<string>;
  listModels(): Promise<string[]>;
}

/**
 * Base provider class with common functionality
 */
export abstract class BaseProvider implements Provider {
  abstract id: string;
  abstract name: string;
  abstract endpoint: string;
  abstract defaultModel: string;

  protected getApiKey(): string | undefined {
    return authManager.getApiKeyForProvider(this.id);
  }

  protected getModel(): string {
    const providerConfig = configManager.getProvider(this.id);
    return providerConfig?.model || this.defaultModel;
  }

  protected getMaxTokens(): number {
    const providerConfig = configManager.getProvider(this.id);
    return providerConfig?.maxTokens || 4096;
  }

  protected getTemperature(): number {
    const providerConfig = configManager.getProvider(this.id);
    return providerConfig?.temperature || 0.2;
  }

  protected async fetchWithAuth(
    url: string,
    options: RequestInit = {},
    apiKey?: string
  ): Promise<Response> {
    const key = apiKey || this.getApiKey();
    
    if (!key && this.id !== 'ollama') {
      throw new Error(`No API key for provider ${this.name}. Run: kutti auth login --provider ${this.id}`);
    }

    const headers = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    // Add authorization header based on provider
    if (this.id === 'groq' || this.id === 'openai' || this.id === 'anthropic' || 
        this.id === 'mistral' || this.id === 'together' || this.id === 'deepseek' ||
        this.id === 'fireworks' || this.id === 'cohere' || this.id === 'openrouter') {
      headers['Authorization'] = `Bearer ${key}`;
    } else if (this.id === 'gemini') {
      headers['x-goog-api-key'] = key;
    } else if (this.id === 'huggingface') {
      headers['Authorization'] = `Bearer ${key}`;
    }

    const response = await fetch(url, {
      ...options,
      headers,
    });

    if (!response.ok) {
      const error = await response.text();
      logger.error(`${this.name} API error: ${response.status} - ${error}`);
      throw new Error(`${this.name} API error: ${response.status} - ${error}`);
    }

    return response;
  }

  abstract chat(messages: ConversationMessage[], options?: any): Promise<string>;
  abstract complete(prompt: string, options?: any): Promise<string>;
  abstract listModels(): Promise<string[]>;

  /**
   * Format messages for the provider's API
   */
  protected formatMessages(messages: ConversationMessage[]): any {
    // Default implementation for OpenAI-compatible APIs
    return messages.map(msg => ({
      role: msg.role,
      content: msg.content,
      name: msg.name,
    }));
  }
}
