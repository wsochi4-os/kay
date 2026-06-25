// Provider registry
export * from './base.js';
export * from './groq.js';
export * from './gemini.js';
export * from './ollama.js';
export * from './openrouter.js';

import { BaseProvider } from './base.js';
import { groqProvider } from './groq.js';
import { geminiProvider } from './gemini.js';
import { ollamaProvider } from './ollama.js';
import { openrouterProvider } from './openrouter.js';
import { DEFAULT_PROVIDERS } from '../utils/constants.js';

// Provider registry
const providers: Record<string, BaseProvider> = {
  groq: groqProvider,
  gemini: geminiProvider,
  ollama: ollamaProvider,
  openrouter: openrouterProvider,
};

/**
 * Get provider by ID
 */
export function getProvider(providerId: string): BaseProvider {
  if (providers[providerId]) {
    return providers[providerId];
  }
  
  // Create a generic provider for unknown providers
  // This allows support for custom providers
  class GenericProvider extends BaseProvider {
    id = providerId;
    name = providerId;
    endpoint = DEFAULT_PROVIDERS[providerId]?.endpoint || '';
    defaultModel = DEFAULT_PROVIDERS[providerId]?.model || '';

    async chat(messages: any[], options: any = {}): Promise<string> {
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
      return this.chat([{ role: 'user', content: prompt }], options);
    }

    async listModels(): Promise<string[]> {
      return [this.defaultModel];
    }
  }

  const genericProvider = new GenericProvider();
  providers[providerId] = genericProvider;
  return genericProvider;
}

/**
 * Get all available providers
 */
export function getAllProviders(): Record<string, BaseProvider> {
  return { ...providers };
}

/**
 * Register a custom provider
 */
export function registerProvider(provider: BaseProvider) {
  providers[provider.id] = provider;
}

/**
 * Get the current active provider
 */
export function getActiveProvider(): BaseProvider {
  const providerId = DEFAULT_PROVIDERS.groq.id; // Default to groq
  return getProvider(providerId);
}
