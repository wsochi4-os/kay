// Core types for Kutti CLI

export interface KuttiConfig {
  version: string;
  provider: string;
  model: string;
  temperature: number;
  maxTokens: number;
  agent: {
    maxIterations: number;
    autoConfirm: boolean;
    autoConfirmShell: boolean;
    contextLines: number;
  };
  terminal: {
    theme: string;
    fontSize: number;
    fontFamily: string;
    cursorStyle: string;
    scrollback: number;
  };
  skills: {
    autoDetect: boolean;
    alwaysLoad: string[];
    projectSkills?: Record<string, string[]>;
  };
  mcp: {
    timeout: number;
    autoRestart: boolean;
  };
  log: {
    level: 'debug' | 'info' | 'warn' | 'error';
    file: string;
  };
}

export interface ProviderConfig {
  endpoint: string;
  model: string;
  maxTokens?: number;
  temperature?: number;
  local?: boolean;
  apiKey?: string;
}

export interface ProviderConfigMap {
  [key: string]: ProviderConfig;
}

export interface AuthCredentials {
  [provider: string]: {
    apiKey: string;
    token?: string;
    refreshToken?: string;
    expiresAt?: number;
  };
}

export interface MCPServerConfig {
  command: string;
  args: string[];
  env?: Record<string, string>;
  transport?: 'stdio' | 'sse';
}

export interface MCPConfig {
  mcpServers: Record<string, MCPServerConfig>;
}

export interface PluginManifest {
  name: string;
  version: string;
  description: string;
  kutti: {
    type: 'plugin';
    minVersion: string;
    commands?: string[];
    tools?: string[];
    hooks?: string[];
  };
  main: string;
}

export interface Plugin {
  name: string;
  commands?: Record<string, any>;
  tools?: any[];
  hooks?: Record<string, Function>;
}

export interface SkillMetadata {
  name: string;
  description: string;
  triggers?: string[];
  priority?: 'low' | 'medium' | 'high';
}

export interface AgentContext {
  config: KuttiConfig;
  provider: ProviderConfig;
  credentials: AuthCredentials;
  plugins: Plugin[];
  skills: SkillMetadata[];
  mcpClients: Record<string, any>;
  systemPrompt: string;
  currentDirectory: string;
}

export interface Tool {
  name: string;
  description: string;
  inputSchema: any;
  execute: (args: any, context: AgentContext) => Promise<any>;
}

export interface AgentAction {
  type: 'tool' | 'shell' | 'write_file' | 'read_file' | 'patch_file' | 'done';
  name?: string;
  args?: any;
  content?: string;
  path?: string;
  diff?: string;
}

export interface AgentObservation {
  type: 'stdout' | 'stderr' | 'file_read' | 'file_written' | 'tool_result' | 'test_result';
  content: string;
  path?: string;
  tool?: string;
  success?: boolean;
}

export interface ConversationMessage {
  role: 'user' | 'assistant' | 'system' | 'tool';
  content: string;
  name?: string;
  tool_call_id?: string;
}
