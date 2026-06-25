import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import { DEFAULT_CONFIG, PATHS, KUTTI_DIR, DEFAULT_PROVIDERS } from './constants.js';
import { logger } from './logger.js';
import type { KuttiConfig, ProviderConfigMap } from '../types/index.js';

/**
 * Configuration Manager for Kutti
 * Handles loading, saving, and merging configuration from multiple sources
 */
export class ConfigManager {
  private config: KuttiConfig;
  private providers: ProviderConfigMap;
  private configPath: string;
  private providersPath: string;

  constructor() {
    // Expand ~ in paths
    this.configPath = PATHS.config.replace('~', os.homedir());
    this.providersPath = PATHS.providers.replace('~', os.homedir());
    
    // Ensure directories exist
    this.ensureDirectories();
    
    // Load configuration
    this.config = this.loadConfig();
    this.providers = this.loadProviders();
  }

  private ensureDirectories() {
    const dirs = [
      KUTTI_DIR.replace('~', os.homedir()),
      path.dirname(this.configPath),
      path.dirname(this.providersPath),
      PATHS.auth.credentials.replace('~', os.homedir()).split('/').slice(0, -1).join('/'),
      PATHS.plugins.replace('~', os.homedir()),
      PATHS.skills.replace('~', os.homedir()),
    ];
    
    for (const dir of dirs) {
      if (!fs.existsSync(dir)) {
        fs.mkdirSync(dir, { recursive: true });
      }
    }
  }

  private loadConfig(): KuttiConfig {
    try {
      if (fs.existsSync(this.configPath)) {
        const configFile = fs.readFileSync(this.configPath, 'utf-8');
        const config = JSON.parse(configFile);
        return this.mergeWithDefaults(config);
      }
    } catch (error) {
      logger.warn(`Failed to load config from ${this.configPath}: ${error}`);
    }
    
    return { ...DEFAULT_CONFIG };
  }

  private loadProviders(): ProviderConfigMap {
    try {
      if (fs.existsSync(this.providersPath)) {
        const providersFile = fs.readFileSync(this.providersPath, 'utf-8');
        return JSON.parse(providersFile);
      }
    } catch (error) {
      logger.warn(`Failed to load providers from ${this.providersPath}: ${error}`);
    }
    
    return { ...DEFAULT_PROVIDERS };
  }

  private mergeWithDefaults(config: Partial<KuttiConfig>): KuttiConfig {
    return {
      ...DEFAULT_CONFIG,
      ...config,
      agent: { ...DEFAULT_CONFIG.agent, ...config.agent },
      terminal: { ...DEFAULT_CONFIG.terminal, ...config.terminal },
      skills: { ...DEFAULT_CONFIG.skills, ...config.skills },
      mcp: { ...DEFAULT_CONFIG.mcp, ...config.mcp },
      log: { ...DEFAULT_CONFIG.log, ...config.log },
    };
  }

  getConfig(): KuttiConfig {
    return this.config;
  }

  getProviders(): ProviderConfigMap {
    return this.providers;
  }

  getProvider(providerId: string): any {
    return this.providers[providerId] || DEFAULT_PROVIDERS[providerId];
  }

  getActiveProvider(): string {
    return this.config.provider;
  }

  getActiveModel(): string {
    return this.config.model;
  }

  setConfig(config: Partial<KuttiConfig>) {
    this.config = this.mergeWithDefaults({ ...this.config, ...config });
    this.saveConfig();
  }

  setProvider(providerId: string) {
    this.config.provider = providerId;
    // Update model to provider's default if not set
    if (!this.config.model || !DEFAULT_PROVIDERS[providerId]?.model.includes(this.config.model)) {
      this.config.model = DEFAULT_PROVIDERS[providerId]?.model || this.config.model;
    }
    this.saveConfig();
  }

  setModel(model: string) {
    this.config.model = model;
    this.saveConfig();
  }

  setProviders(providers: ProviderConfigMap) {
    this.providers = { ...this.providers, ...providers };
    this.saveProviders();
  }

  addProvider(providerId: string, config: any) {
    this.providers[providerId] = { ...this.providers[providerId], ...config };
    this.saveProviders();
  }

  removeProvider(providerId: string) {
    delete this.providers[providerId];
    this.saveProviders();
  }

  private saveConfig() {
    try {
      fs.writeFileSync(this.configPath, JSON.stringify(this.config, null, 2));
      logger.debug(`Config saved to ${this.configPath}`);
    } catch (error) {
      logger.error(`Failed to save config: ${error}`);
    }
  }

  private saveProviders() {
    try {
      fs.writeFileSync(this.providersPath, JSON.stringify(this.providers, null, 2));
      logger.debug(`Providers saved to ${this.providersPath}`);
    } catch (error) {
      logger.error(`Failed to save providers: ${error}`);
    }
  }

  // Get configuration value by key (supports nested keys with dot notation)
  get<T>(key: string): T | undefined {
    const keys = key.split('.');
    let value: any = this.config;
    
    for (const k of keys) {
      if (value && typeof value === 'object' && k in value) {
        value = value[k];
      } else {
        return undefined;
      }
    }
    
    return value as T;
  }

  // Set configuration value by key (supports nested keys with dot notation)
  set(key: string, value: any) {
    const keys = key.split('.');
    let current: any = this.config;
    
    for (let i = 0; i < keys.length - 1; i++) {
      const k = keys[i];
      if (!current[k] || typeof current[k] !== 'object') {
        current[k] = {};
      }
      current = current[k];
    }
    
    current[keys[keys.length - 1]] = value;
    this.saveConfig();
  }

  // Reset configuration to defaults
  reset() {
    this.config = { ...DEFAULT_CONFIG };
    this.providers = { ...DEFAULT_PROVIDERS };
    this.saveConfig();
    this.saveProviders();
  }

  // Reload configuration from disk
  reload() {
    this.config = this.loadConfig();
    this.providers = this.loadProviders();
  }
}

// Singleton instance
export const configManager = new ConfigManager();

export function getConfig(): KuttiConfig {
  return configManager.getConfig();
}

export function getProvider(providerId: string): any {
  return configManager.getProvider(providerId);
}

export function getActiveProvider(): string {
  return configManager.getActiveProvider();
}

export function getActiveModel(): string {
  return configManager.getActiveModel();
}
