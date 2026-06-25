import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import crypto from 'node:crypto';
import { PATHS } from '../utils/constants.js';
import { logger } from '../utils/logger.js';
import type { AuthCredentials } from '../types/index.js';

/**
 * Keystore for managing encrypted credentials
 * Uses AES-256-GCM encryption with a key derived from the system
 */
export class Keystore {
  private key: Buffer;
  private credentialsPath: string;
  private providersPath: string;
  private activePath: string;

  constructor() {
    this.credentialsPath = PATHS.auth.credentials.replace('~', os.homedir());
    this.providersPath = PATHS.auth.providers.replace('~', os.homedir());
    this.activePath = PATHS.auth.active.replace('~', os.homedir());
    
    // Generate or load encryption key
    this.key = this.loadOrCreateKey();
    
    // Ensure directories exist
    this.ensureDirectories();
  }

  private ensureDirectories() {
    const dir = path.dirname(this.credentialsPath);
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }
  }

  private loadOrCreateKey(): Buffer {
    // On Android, we would use Android Keystore
    // On other platforms, we derive from a system-specific seed
    const isAndroid = process.platform === 'android';
    
    if (isAndroid) {
      // For Android, we'll use a key derived from the app's data directory
      // In a real Android app, this would use Android Keystore API
      const androidKeyPath = '/data/data/dev.kutti.app/files/.kutti/key';
      if (fs.existsSync(androidKeyPath)) {
        return fs.readFileSync(androidKeyPath);
      } else {
        const key = crypto.randomBytes(32);
        fs.writeFileSync(androidKeyPath, key);
        return key;
      }
    } else {
      // For development, derive from a combination of system info
      // In production, this should use the OS keyring
      const seed = `${os.homedir()}:${os.hostname()}:kutti`;
      return crypto.scryptSync(seed, 'kutti-salt', 32);
    }
  }

  private encrypt(data: string): string {
    const iv = crypto.randomBytes(12);
    const cipher = crypto.createCipheriv('aes-256-gcm', this.key, iv);
    
    let encrypted = cipher.update(data, 'utf8', 'base64');
    encrypted += cipher.final('base64');
    
    const authTag = cipher.getAuthTag();
    
    return `${iv.toString('base64')}:${authTag.toString('base64')}:${encrypted}`;
  }

  private decrypt(encryptedData: string): string {
    const parts = encryptedData.split(':');
    if (parts.length !== 3) {
      throw new Error('Invalid encrypted data format');
    }
    
    const iv = Buffer.from(parts[0], 'base64');
    const authTag = Buffer.from(parts[1], 'base64');
    const encrypted = parts[2];
    
    const decipher = crypto.createDecipheriv('aes-256-gcm', this.key, iv);
    decipher.setAuthTag(authTag);
    
    let decrypted = decipher.update(encrypted, 'base64', 'utf8');
    decrypted += decipher.final('utf8');
    
    return decrypted;
  }

  /**
   * Save credentials to encrypted storage
   */
  saveCredentials(credentials: AuthCredentials) {
    try {
      const data = JSON.stringify(credentials);
      const encrypted = this.encrypt(data);
      fs.writeFileSync(this.credentialsPath, encrypted);
      logger.debug('Credentials saved and encrypted');
    } catch (error) {
      logger.error(`Failed to save credentials: ${error}`);
      throw error;
    }
  }

  /**
   * Load credentials from encrypted storage
   */
  loadCredentials(): AuthCredentials {
    try {
      if (!fs.existsSync(this.credentialsPath)) {
        return {};
      }
      
      const encrypted = fs.readFileSync(this.credentialsPath, 'utf8');
      const decrypted = this.decrypt(encrypted);
      return JSON.parse(decrypted);
    } catch (error) {
      logger.warn(`Failed to load credentials: ${error}`);
      return {};
    }
  }

  /**
   * Get API key for a specific provider
   */
  getApiKey(providerId: string): string | undefined {
    const credentials = this.loadCredentials();
    return credentials[providerId]?.apiKey;
  }

  /**
   * Set API key for a specific provider
   */
  setApiKey(providerId: string, apiKey: string) {
    const credentials = this.loadCredentials();
    credentials[providerId] = {
      ...credentials[providerId],
      apiKey,
    };
    this.saveCredentials(credentials);
  }

  /**
   * Remove credentials for a provider
   */
  removeCredentials(providerId: string) {
    const credentials = this.loadCredentials();
    delete credentials[providerId];
    this.saveCredentials(credentials);
  }

  /**
   * Remove all credentials
   */
  removeAllCredentials() {
    this.saveCredentials({});
  }

  /**
   * Check if a provider is authenticated
   */
  isAuthenticated(providerId: string): boolean {
    const credentials = this.loadCredentials();
    return !!(credentials[providerId]?.apiKey);
  }

  /**
   * Get all authenticated providers
   */
  getAuthenticatedProviders(): string[] {
    const credentials = this.loadCredentials();
    return Object.keys(credentials).filter(key => credentials[key]?.apiKey);
  }

  /**
   * Set active provider
   */
  setActiveProvider(providerId: string) {
    fs.writeFileSync(this.activePath, providerId);
  }

  /**
   * Get active provider
   */
  getActiveProvider(): string | undefined {
    try {
      if (fs.existsSync(this.activePath)) {
        return fs.readFileSync(this.activePath, 'utf8').trim();
      }
    } catch (error) {
      logger.warn(`Failed to read active provider: ${error}`);
    }
    return undefined;
  }

  /**
   * Save provider metadata (non-secret)
   */
  saveProviderMetadata(providers: Record<string, any>) {
    try {
      fs.writeFileSync(this.providersPath, JSON.stringify(providers, null, 2));
    } catch (error) {
      logger.error(`Failed to save provider metadata: ${error}`);
    }
  }

  /**
   * Load provider metadata
   */
  loadProviderMetadata(): Record<string, any> {
    try {
      if (fs.existsSync(this.providersPath)) {
        return JSON.parse(fs.readFileSync(this.providersPath, 'utf8'));
      }
    } catch (error) {
      logger.warn(`Failed to load provider metadata: ${error}`);
    }
    return {};
  }
}

// Singleton instance
export const keystore = new Keystore();
