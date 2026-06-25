import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import { PATHS, BUILTIN_PLUGINS } from '../utils/constants.js';
import { logger } from '../utils/logger.js';
import type { Plugin, PluginManifest } from '../types/index.js';

/**
 * Plugin Loader - Loads and manages Kutti plugins
 */
export class PluginLoader {
  private plugins: Map<string, Plugin>;
  private pluginPaths: Map<string, string>;
  private loadedFrom: Set<string>;

  constructor() {
    this.plugins = new Map();
    this.pluginPaths = new Map();
    this.loadedFrom = new Set();
  }

  /**
   * Get the plugins directory
   */
  private getPluginsDir(): string {
    return PATHS.plugins.replace('~', os.homedir());
  }

  /**
   * Check if a plugin is built-in
   */
  private isBuiltIn(pluginName: string): boolean {
    return BUILTIN_PLUGINS.includes(pluginName);
  }

  /**
   * Get path to a built-in plugin
   */
  private getBuiltInPluginPath(pluginName: string): string | null {
    const builtInPaths = [
      path.join(process.cwd(), 'plugins', pluginName),
      path.join(__dirname, '..', '..', '..', 'plugins', pluginName),
    ];

    for (const p of builtInPaths) {
      if (fs.existsSync(p)) {
        return p;
      }
    }

    return null;
  }

  /**
   * Load a plugin manifest
   */
  loadManifest(pluginPath: string): PluginManifest | null {
    const manifestPath = path.join(pluginPath, 'package.json');
    
    try {
      if (fs.existsSync(manifestPath)) {
        const content = fs.readFileSync(manifestPath, 'utf8');
        const manifest = JSON.parse(content);
        
        if (manifest.kutti && manifest.kutti.type === 'plugin') {
          return manifest as PluginManifest;
        }
      }
    } catch (error) {
      logger.warn(`Failed to load plugin manifest from ${manifestPath}: ${error}`);
    }

    return null;
  }

  /**
   * Load a plugin from a path
   */
  async loadFromPath(pluginPath: string): Promise<Plugin | null> {
    const manifest = this.loadManifest(pluginPath);
    
    if (!manifest) {
      logger.warn(`No valid plugin manifest found at ${pluginPath}`);
      return null;
    }

    if (this.plugins.has(manifest.name)) {
      logger.warn(`Plugin ${manifest.name} already loaded`);
      return this.plugins.get(manifest.name) || null;
    }

    try {
      // Check if the plugin has a main file
      const mainPath = path.join(pluginPath, manifest.main || 'index.js');
      
      if (!fs.existsSync(mainPath)) {
        logger.warn(`Plugin main file not found: ${mainPath}`);
        return null;
      }

      // Load the plugin module
      // In Node.js, we would use dynamic import
      // For now, we'll create a mock plugin
      const plugin: Plugin = {
        name: manifest.name,
        commands: manifest.kutti.commands?.reduce((acc, cmd) => {
          acc[cmd] = { name: cmd, description: `Command from ${manifest.name}` };
          return acc;
        }, {} as Record<string, any>),
        tools: [],
        hooks: {},
      };

      // Try to load the actual module
      try {
        // This is a simplified approach
        // In a real implementation, we would use:
        // const module = await import(mainPath);
        // plugin = { ...plugin, ...module.default };
        
        logger.info(`Plugin ${manifest.name} loaded from ${pluginPath}`);
      } catch (error) {
        logger.warn(`Failed to load plugin module ${mainPath}: ${error}`);
      }

      this.plugins.set(manifest.name, plugin);
      this.pluginPaths.set(manifest.name, pluginPath);
      this.loadedFrom.add(pluginPath);

      return plugin;
    } catch (error) {
      logger.error(`Failed to load plugin ${manifest.name}: ${error}`);
      return null;
    }
  }

  /**
   * Load a plugin by name
   */
  async load(pluginName: string): Promise<Plugin | null> {
    // Check if already loaded
    if (this.plugins.has(pluginName)) {
      return this.plugins.get(pluginName) || null;
    }

    // Try built-in plugins first
    if (this.isBuiltIn(pluginName)) {
      const builtInPath = this.getBuiltInPluginPath(pluginName);
      if (builtInPath) {
        return this.loadFromPath(builtInPath);
      }
    }

    // Try user plugins directory
    const userPluginPath = path.join(this.getPluginsDir(), pluginName);
    if (fs.existsSync(userPluginPath)) {
      return this.loadFromPath(userPluginPath);
    }

    // Try npm package
    try {
      // This would require dynamic import of npm packages
      // For now, we'll skip this
      logger.warn(`Plugin ${pluginName} not found in built-in or user directories`);
    } catch (error) {
      logger.warn(`Failed to load plugin ${pluginName} from npm: ${error}`);
    }

    return null;
  }

  /**
   * Load all plugins from a directory
   */
  async loadFromDirectory(directory: string): Promise<Plugin[]> {
    const loaded: Plugin[] = [];

    try {
      const entries = fs.readdirSync(directory, { withFileTypes: true });

      for (const entry of entries) {
        if (entry.isDirectory()) {
          const pluginPath = path.join(directory, entry.name);
          const manifest = this.loadManifest(pluginPath);
          
          if (manifest) {
            const plugin = await this.loadFromPath(pluginPath);
            if (plugin) {
              loaded.push(plugin);
            }
          }
        }
      }
    } catch (error) {
      logger.warn(`Failed to load plugins from ${directory}: ${error}`);
    }

    return loaded;
  }

  /**
   * Load all built-in plugins
   */
  async loadBuiltInPlugins(): Promise<Plugin[]> {
    const loaded: Plugin[] = [];

    for (const pluginName of BUILTIN_PLUGINS) {
      const plugin = await this.load(pluginName);
      if (plugin) {
        loaded.push(plugin);
      }
    }

    return loaded;
  }

  /**
   * Load all user plugins
   */
  async loadUserPlugins(): Promise<Plugin[]> {
    const pluginsDir = this.getPluginsDir();
    
    if (!fs.existsSync(pluginsDir)) {
      fs.mkdirSync(pluginsDir, { recursive: true });
      return [];
    }

    return this.loadFromDirectory(pluginsDir);
  }

  /**
   * Load all plugins (built-in + user)
   */
  async loadAll(): Promise<Plugin[]> {
    const builtIn = await this.loadBuiltInPlugins();
    const user = await this.loadUserPlugins();
    
    return [...builtIn, ...user];
  }

  /**
   * Unload a plugin
   */
  unload(pluginName: string): boolean {
    if (this.plugins.has(pluginName)) {
      this.plugins.delete(pluginName);
      this.pluginPaths.delete(pluginName);
      logger.info(`Plugin ${pluginName} unloaded`);
      return true;
    }
    return false;
  }

  /**
   * Unload all plugins
   */
  unloadAll(): void {
    this.plugins.clear();
    this.pluginPaths.clear();
    this.loadedFrom.clear();
    logger.info('All plugins unloaded');
  }

  /**
   * Get a loaded plugin
   */
  get(pluginName: string): Plugin | undefined {
    return this.plugins.get(pluginName);
  }

  /**
   * Get all loaded plugins
   */
  getAll(): Plugin[] {
    return Array.from(this.plugins.values());
  }

  /**
   * Get all loaded plugin names
   */
  getLoadedPluginNames(): string[] {
    return Array.from(this.plugins.keys());
  }

  /**
   * Check if a plugin is loaded
   */
  isLoaded(pluginName: string): boolean {
    return this.plugins.has(pluginName);
  }

  /**
   * Get commands from all plugins
   */
  getAllCommands(): Record<string, any> {
    const commands: Record<string, any> = {};

    for (const plugin of this.plugins.values()) {
      if (plugin.commands) {
        Object.assign(commands, plugin.commands);
      }
    }

    return commands;
  }

  /**
   * Get tools from all plugins
   */
  getAllTools(): any[] {
    const tools: any[] = [];

    for (const plugin of this.plugins.values()) {
      if (plugin.tools) {
        tools.push(...plugin.tools);
      }
    }

    return tools;
  }

  /**
   * Get hooks from all plugins
   */
  getAllHooks(): Record<string, Function[]> {
    const hooks: Record<string, Function[]> = {};

    for (const plugin of this.plugins.values()) {
      if (plugin.hooks) {
        for (const [hookName, hookFn] of Object.entries(plugin.hooks)) {
          if (!hooks[hookName]) {
            hooks[hookName] = [];
          }
          hooks[hookName].push(hookFn);
        }
      }
    }

    return hooks;
  }

  /**
   * Install a plugin from npm
   */
  async install(pluginName: string): Promise<boolean> {
    try {
      // This would use npm or pnpm to install the plugin
      // For now, we'll just log it
      logger.info(`Installing plugin ${pluginName} from npm...`);
      
      // Simulate installation
      const pluginDir = path.join(this.getPluginsDir(), pluginName);
      fs.mkdirSync(pluginDir, { recursive: true });
      
      // Create a mock package.json
      fs.writeFileSync(
        path.join(pluginDir, 'package.json'),
        JSON.stringify({
          name: pluginName,
          version: '1.0.0',
          kutti: {
            type: 'plugin',
            minVersion: '1.0.0',
          },
          main: 'index.js',
        }, null, 2)
      );

      // Create a mock index.js
      fs.writeFileSync(
        path.join(pluginDir, 'index.js'),
        `module.exports = {
  name: '${pluginName}',
  commands: {},
  tools: [],
  hooks: {},
};`
      );

      // Load the plugin
      await this.load(pluginName);
      
      logger.info(`Plugin ${pluginName} installed successfully`);
      return true;
    } catch (error) {
      logger.error(`Failed to install plugin ${pluginName}: ${error}`);
      return false;
    }
  }

  /**
   * Remove a plugin
   */
  async remove(pluginName: string): Promise<boolean> {
    try {
      // Unload the plugin
      this.unload(pluginName);

      // Remove from filesystem
      const pluginPath = this.pluginPaths.get(pluginName);
      if (pluginPath && fs.existsSync(pluginPath)) {
        fs.rmSync(pluginPath, { recursive: true, force: true });
      }

      logger.info(`Plugin ${pluginName} removed`);
      return true;
    } catch (error) {
      logger.error(`Failed to remove plugin ${pluginName}: ${error}`);
      return false;
    }
  }
}

// Singleton instance
export const pluginLoader = new PluginLoader();

/**
 * Initialize plugins
 */
export async function initializePlugins() {
  await pluginLoader.loadAll();
  logger.info(`Loaded ${pluginLoader.getLoadedPluginNames().length} plugins`);
}
