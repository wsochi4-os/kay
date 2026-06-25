import { PROVIDER_LIST, DEFAULT_PROVIDERS } from '../utils/constants.js';
import { keystore } from './keystore.js';
import { configManager } from '../utils/config.js';
import { logger } from '../utils/logger.js';
import type { AuthCredentials } from '../types/index.js';

/**
 * Auth Manager - Handles authentication flows for all providers
 */
export class AuthManager {
  /**
   * Login to a provider
   */
  async login(providerId: string, apiKey?: string): Promise<{ success: boolean; message: string }> {
    const provider = PROVIDER_LIST.find(p => p.id === providerId);
    
    if (!provider) {
      return { success: false, message: `Provider '${providerId}' not found` };
    }

    // For Ollama, no API key is needed
    if (providerId === 'ollama') {
      keystore.setApiKey(providerId, 'local');
      keystore.setActiveProvider(providerId);
      configManager.setProvider(providerId);
      return { success: true, message: `Authenticated with ${provider.name} (local)` };
    }

    // If API key is provided, use it
    if (apiKey) {
      keystore.setApiKey(providerId, apiKey);
      keystore.setActiveProvider(providerId);
      configManager.setProvider(providerId);
      return { success: true, message: `Authenticated with ${provider.name}` };
    }

    // Otherwise, prompt for API key
    // In a real implementation, this would open a browser for OAuth
    // For CLI, we'll just prompt for the key
    return { 
      success: false, 
      message: `API key required for ${provider.name}. Use: kutti auth login --provider ${providerId} --key YOUR_API_KEY` 
    };
  }

  /**
   * Logout from a provider
   */
  logout(providerId: string): { success: boolean; message: string } {
    if (providerId === 'all') {
      keystore.removeAllCredentials();
      return { success: true, message: 'Logged out from all providers' };
    }

    const provider = PROVIDER_LIST.find(p => p.id === providerId);
    if (!provider) {
      return { success: false, message: `Provider '${providerId}' not found` };
    }

    keystore.removeCredentials(providerId);
    
    // If this was the active provider, switch to a different one
    const active = keystore.getActiveProvider();
    if (active === providerId) {
      const authenticated = keystore.getAuthenticatedProviders();
      if (authenticated.length > 0) {
        keystore.setActiveProvider(authenticated[0]);
        configManager.setProvider(authenticated[0]);
      } else {
        keystore.setActiveProvider('');
        configManager.setProvider('groq'); // Reset to default
      }
    }

    return { success: true, message: `Logged out from ${provider.name}` };
  }

  /**
   * Switch active provider
   */
  use(providerId: string): { success: boolean; message: string } {
    const provider = PROVIDER_LIST.find(p => p.id === providerId);
    if (!provider) {
      return { success: false, message: `Provider '${providerId}' not found` };
    }

    if (!keystore.isAuthenticated(providerId) && providerId !== 'ollama') {
      return { success: false, message: `Not authenticated with ${provider.name}. Run: kutti auth login --provider ${providerId}` };
    }

    keystore.setActiveProvider(providerId);
    configManager.setProvider(providerId);
    
    return { success: true, message: `Switched to ${provider.name}` };
  }

  /**
   * List all authenticated providers
   */
  list(): { providers: Array<{ id: string; name: string; authenticated: boolean; active: boolean }> } {
    const providers = PROVIDER_LIST.map(provider => {
      const authenticated = keystore.isAuthenticated(provider.id);
      const active = keystore.getActiveProvider() === provider.id;
      
      return {
        id: provider.id,
        name: provider.name,
        authenticated,
        active,
      };
    });

    return { providers };
  }

  /**
   * Get current auth status
   */
  status(): {
    activeProvider: string | undefined;
    authenticated: boolean;
    providers: string[];
  } {
    const active = keystore.getActiveProvider();
    const authenticated = active ? keystore.isAuthenticated(active) : false;
    const providers = keystore.getAuthenticatedProviders();

    return {
      activeProvider: active,
      authenticated,
      providers,
    };
  }

  /**
   * Refresh authentication for a provider
   */
  async refresh(providerId: string): Promise<{ success: boolean; message: string }> {
    // For most providers, this just clears the current credentials
    // and prompts for re-authentication
    const provider = PROVIDER_LIST.find(p => p.id === providerId);
    if (!provider) {
      return { success: false, message: `Provider '${providerId}' not found` };
    }

    keystore.removeCredentials(providerId);
    
    return {
      success: true,
      message: `Credentials cleared for ${provider.name}. Run 'kutti auth login --provider ${providerId}' to re-authenticate.`
    };
  }

  /**
   * Get API key for the active provider
   */
  getApiKey(): string | undefined {
    const active = keystore.getActiveProvider();
    if (!active) {
      // Try to get from config
      const configProvider = configManager.getActiveProvider();
      return keystore.getApiKey(configProvider);
    }
    return keystore.getApiKey(active);
  }

  /**
   * Get API key for a specific provider
   */
  getApiKeyForProvider(providerId: string): string | undefined {
    return keystore.getApiKey(providerId);
  }

  /**
   * Check if currently authenticated
   */
  isAuthenticated(): boolean {
    const active = keystore.getActiveProvider();
    if (!active) {
      const configProvider = configManager.getActiveProvider();
      return keystore.isAuthenticated(configProvider);
    }
    return keystore.isAuthenticated(active);
  }

  /**
   * Get all available providers
   */
  getAvailableProviders() {
    return PROVIDER_LIST;
  }

  /**
   * Get provider config by ID
   */
  getProviderConfig(providerId: string) {
    return DEFAULT_PROVIDERS[providerId];
  }
}

// Singleton instance
export const authManager = new AuthManager();
