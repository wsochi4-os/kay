import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { CallToolRequestSchema, ListToolsRequestSchema } from '@modelcontextprotocol/sdk/types.js';
import { logger } from '../utils/logger.js';
import { PATHS, KUTTI_DIR } from '../utils/constants.js';
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import { spawn } from 'node:child_process';

/**
 * MCP Server Configuration
 */
export interface MCPServerConfig {
  name: string;
  command: string;
  args: string[];
  env?: Record<string, string>;
  transport?: 'stdio' | 'sse';
  autoStart?: boolean;
}

/**
 * MCP Client interface
 */
export interface MCPClient {
  name: string;
  process?: any;
  server?: any;
  tools: any[];
  resources: any[];
  
  start(): Promise<void>;
  stop(): Promise<void>;
  listTools(): Promise<any[]>;
  callTool(name: string, args: any): Promise<any>;
  listResources(): Promise<any[]>;
  readResource(uri: string): Promise<any>;
}

/**
 * MCP Host - Manages MCP servers and their connections
 */
export class MCPHost {
  private servers: Map<string, MCPClient>;
  private configPath: string;

  constructor() {
    this.servers = new Map();
    this.configPath = PATHS.mcp.replace('~', os.homedir());
  }

  /**
   * Load MCP configuration
   */
  loadConfig(): { mcpServers: Record<string, MCPServerConfig> } {
    try {
      if (fs.existsSync(this.configPath)) {
        const config = fs.readFileSync(this.configPath, 'utf8');
        return JSON.parse(config);
      }
    } catch (error) {
      logger.warn(`Failed to load MCP config: ${error}`);
    }

    return { mcpServers: {} };
  }

  /**
   * Save MCP configuration
   */
  saveConfig(config: { mcpServers: Record<string, MCPServerConfig> }) {
    try {
      fs.writeFileSync(this.configPath, JSON.stringify(config, null, 2));
      logger.debug(`MCP config saved to ${this.configPath}`);
    } catch (error) {
      logger.error(`Failed to save MCP config: ${error}`);
    }
  }

  /**
   * Add an MCP server
   */
  addServer(config: MCPServerConfig) {
    const client = this.createClient(config);
    this.servers.set(config.name, client);
    
    // Save to config
    const currentConfig = this.loadConfig();
    currentConfig.mcpServers[config.name] = config;
    this.saveConfig(currentConfig);

    return client;
  }

  /**
   * Remove an MCP server
   */
  removeServer(name: string) {
    this.servers.delete(name);
    
    // Remove from config
    const currentConfig = this.loadConfig();
    delete currentConfig.mcpServers[name];
    this.saveConfig(currentConfig);
  }

  /**
   * Get an MCP server by name
   */
  getServer(name: string): MCPClient | undefined {
    return this.servers.get(name);
  }

  /**
   * List all MCP servers
   */
  listServers(): string[] {
    return Array.from(this.servers.keys());
  }

  /**
   * Start all MCP servers
   */
  async startAll() {
    const promises = Array.from(this.servers.values()).map(server => server.start());
    await Promise.all(promises);
  }

  /**
   * Stop all MCP servers
   */
  async stopAll() {
    const promises = Array.from(this.servers.values()).map(server => server.stop());
    await Promise.all(promises);
  }

  /**
   * Create an MCP client from config
   */
  private createClient(config: MCPServerConfig): MCPClient {
    return new MCPClientImpl(config);
  }

  /**
   * List all tools from all servers
   */
  async listAllTools(): Promise<{ server: string; tools: any[] }[]> {
    const results: { server: string; tools: any[] }[] = [];
    
    for (const [name, client] of this.servers) {
      try {
        const tools = await client.listTools();
        results.push({ server: name, tools });
      } catch (error) {
        logger.warn(`Failed to list tools from server ${name}: ${error}`);
      }
    }

    return results;
  }

  /**
   * Call a tool on a specific server
   */
  async callTool(serverName: string, toolName: string, args: any): Promise<any> {
    const client = this.servers.get(serverName);
    if (!client) {
      throw new Error(`Server '${serverName}' not found`);
    }

    return client.callTool(toolName, args);
  }
}

/**
 * MCP Client Implementation
 */
class MCPClientImpl implements MCPClient {
  name: string;
  private config: MCPServerConfig;
  private process: any;
  private server: any;
  tools: any[] = [];
  resources: any[] = [];

  constructor(config: MCPServerConfig) {
    this.name = config.name;
    this.config = config;
  }

  async start(): Promise<void> {
    if (this.process) {
      logger.warn(`Server ${this.name} is already running`);
      return;
    }

    logger.info(`Starting MCP server: ${this.name}`);

    try {
      // Start the server process
      this.process = spawn(this.config.command, this.config.args || [], {
        env: { ...process.env, ...this.config.env },
        stdio: 'pipe',
      });

      // Handle process events
      this.process.stdout.on('data', (data: any) => {
        logger.debug(`[${this.name}] stdout: ${data.toString()}`);
      });

      this.process.stderr.on('data', (data: any) => {
        logger.warn(`[${this.name}] stderr: ${data.toString()}`);
      });

      this.process.on('close', (code: number) => {
        logger.info(`[${this.name}] process exited with code ${code}`);
        this.process = null;
      });

      // Wait for server to be ready
      await new Promise(resolve => setTimeout(resolve, 1000));

      // Initialize the server connection
      this.server = new Server(
        {
          name: this.name,
          version: '1.0.0',
        },
        {
          capabilities: {
            tools: {},
            resources: {},
          },
        }
      );

      // For stdio transport, we would connect here
      // This is a simplified implementation
      
      logger.info(`MCP server ${this.name} started`);
    } catch (error) {
      logger.error(`Failed to start MCP server ${this.name}: ${error}`);
      throw error;
    }
  }

  async stop(): Promise<void> {
    if (!this.process) {
      logger.warn(`Server ${this.name} is not running`);
      return;
    }

    logger.info(`Stopping MCP server: ${this.name}`);

    try {
      this.process.kill();
      this.process = null;
      this.server = null;
      logger.info(`MCP server ${this.name} stopped`);
    } catch (error) {
      logger.error(`Failed to stop MCP server ${this.name}: ${error}`);
      throw error;
    }
  }

  async listTools(): Promise<any[]> {
    // In a real implementation, this would call the server
    // For now, return mock tools
    if (this.name === 'filesystem') {
      return [
        {
          name: 'read_resource',
          description: 'Read a file from the filesystem',
          inputSchema: {
            type: 'object',
            properties: {
              uri: { type: 'string', description: 'File URI' },
            },
            required: ['uri'],
          },
        },
        {
          name: 'list_resources',
          description: 'List files in a directory',
          inputSchema: {
            type: 'object',
            properties: {
              uri: { type: 'string', description: 'Directory URI' },
            },
            required: ['uri'],
          },
        },
      ];
    }

    return [];
  }

  async callTool(name: string, args: any): Promise<any> {
    // In a real implementation, this would call the actual tool
    logger.info(`Calling tool ${name} on server ${this.name} with args: ${JSON.stringify(args)}`);

    // Mock implementation
    if (this.name === 'filesystem' && name === 'read_resource') {
      const filePath = args.uri.replace('file://', '');
      try {
        const content = fs.readFileSync(filePath, 'utf8');
        return { content, path: filePath };
      } catch (error) {
        return { error: `File not found: ${filePath}` };
      }
    }

    return { result: `Tool ${name} called with ${JSON.stringify(args)}` };
  }

  async listResources(): Promise<any[]> {
    // In a real implementation, this would call the server
    return [];
  }

  async readResource(uri: string): Promise<any> {
    // In a real implementation, this would call the server
    return { content: '', uri };
  }
}

// Singleton instance
export const mcpHost = new MCPHost();

/**
 * Initialize MCP with default servers
 */
export async function initializeMCP() {
  const config = mcpHost.loadConfig();
  
  // Add default filesystem server if not present
  if (!config.mcpServers.filesystem) {
    mcpHost.addServer({
      name: 'filesystem',
      command: 'npx',
      args: ['-y', '@modelcontextprotocol/server-filesystem', process.cwd()],
      transport: 'stdio',
      autoStart: true,
    });
  }

  // Start all auto-start servers
  for (const [name, serverConfig] of Object.entries(config.mcpServers)) {
    if (serverConfig.autoStart) {
      try {
        await mcpHost.getServer(name)?.start();
      } catch (error) {
        logger.warn(`Failed to start MCP server ${name}: ${error}`);
      }
    }
  }
}
