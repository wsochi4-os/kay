// Constants for Kutti CLI

export const KUTTI_VERSION = '1.0.0';

export const DEFAULT_CONFIG: any = {
  version: '1',
  provider: 'groq',
  model: 'llama-3.3-70b-versatile',
  temperature: 0.2,
  maxTokens: 8192,
  agent: {
    maxIterations: 20,
    autoConfirm: false,
    autoConfirmShell: false,
    contextLines: 5,
  },
  terminal: {
    theme: 'gruvbox-dark',
    fontSize: 14,
    fontFamily: 'JetBrains Mono',
    cursorStyle: 'block',
    scrollback: 10000,
  },
  skills: {
    autoDetect: true,
    alwaysLoad: ['kutti-core'],
  },
  mcp: {
    timeout: 30000,
    autoRestart: true,
  },
  log: {
    level: 'info',
    file: '~/.kutti/kutti.log',
  },
};

export const DEFAULT_PROVIDERS: Record<string, any> = {
  groq: {
    endpoint: 'https://api.groq.com/openai/v1',
    model: 'llama-3.3-70b-versatile',
    maxTokens: 8192,
    temperature: 0.2,
  },
  gemini: {
    endpoint: 'https://generativelanguage.googleapis.com/v1beta',
    model: 'gemini-2.0-flash',
    maxTokens: 8192,
  },
  openrouter: {
    endpoint: 'https://openrouter.ai/api/v1',
    model: 'meta-llama/llama-3.1-70b-instruct:free',
    maxTokens: 4096,
  },
  mistral: {
    endpoint: 'https://api.mistral.ai/v1',
    model: 'open-mistral-7b',
    maxTokens: 4096,
  },
  cerebras: {
    endpoint: 'https://api.cerebras.net/v1',
    model: 'llama3.1-70b',
    maxTokens: 4096,
  },
  cohere: {
    endpoint: 'https://api.cohere.ai/v1',
    model: 'command-r',
    maxTokens: 4096,
  },
  together: {
    endpoint: 'https://api.together.xyz/v1',
    model: 'Meta-Llama-3.1-70B',
    maxTokens: 4096,
  },
  ollama: {
    endpoint: 'http://localhost:11434/v1',
    model: 'llama3.3',
    maxTokens: 4096,
    local: true,
  },
  openai: {
    endpoint: 'https://api.openai.com/v1',
    model: 'gpt-4o',
    maxTokens: 8192,
  },
  anthropic: {
    endpoint: 'https://api.anthropic.com/v1',
    model: 'claude-3-5-sonnet-20250620',
    maxTokens: 8192,
  },
  huggingface: {
    endpoint: 'https://api-inference.huggingface.co/models',
    model: 'mistralai/Mistral-7B-Instruct-v0.2',
    maxTokens: 4096,
  },
  deepseek: {
    endpoint: 'https://api.deepseek.com/v1',
    model: 'deepseek-chat',
    maxTokens: 8192,
  },
  fireworks: {
    endpoint: 'https://api.fireworks.ai/inference/v1',
    model: 'accounts/fireworks/models/llama-v3p1-70b-instruct',
    maxTokens: 4096,
  },
};

export const PROVIDER_LIST = [
  { id: 'groq', name: 'Groq', free: true, description: 'Fastest inference' },
  { id: 'gemini', name: 'Google Gemini', free: true, description: 'Strong tool use' },
  { id: 'openrouter', name: 'OpenRouter', free: true, description: '100+ free models' },
  { id: 'mistral', name: 'Mistral', free: true, description: 'Good code tasks' },
  { id: 'cerebras', name: 'Cerebras', free: true, description: 'Ultra fast' },
  { id: 'cohere', name: 'Cohere', free: true, description: 'Strong RAG' },
  { id: 'together', name: 'Together AI', free: true, description: 'Many open models' },
  { id: 'ollama', name: 'Ollama', free: true, description: 'Fully local, no key needed' },
  { id: 'huggingface', name: 'Hugging Face', free: true, description: 'Rate limited' },
  { id: 'deepseek', name: 'DeepSeek', free: false, description: 'Excellent coding' },
  { id: 'fireworks', name: 'Fireworks AI', free: true, description: 'Fast open models' },
  { id: 'openai', name: 'OpenAI', free: false, description: 'Paid' },
  { id: 'anthropic', name: 'Anthropic', free: false, description: 'Paid' },
];

export const KUTTI_DIR = process.env.KUTTI_CONFIG_DIR || 
  (process.platform === 'android' ? '/data/data/dev.kutti.app/files/.kutti' : '~/.kutti');

export const PATHS = {
  config: `${KUTTI_DIR}/config.json`,
  providers: `${KUTTI_DIR}/providers.json`,
  auth: {
    credentials: `${KUTTI_DIR}/auth/credentials.enc`,
    providers: `${KUTTI_DIR}/auth/providers.json`,
    active: `${KUTTI_DIR}/auth/active`,
  },
  mcp: `${KUTTI_DIR}/mcp.json`,
  plugins: `${KUTTI_DIR}/plugins`,
  skills: `${KUTTI_DIR}/skills`,
  logs: `${KUTTI_DIR}/kutti.log`,
};

export const BUILTIN_PLUGINS = [
  'kutti-plugin-shell',
  'kutti-plugin-files',
  'kutti-plugin-web',
  'kutti-plugin-git',
  'kutti-plugin-android',
];

export const BUILTIN_SKILLS = [
  'kutti-core',
  'android-dev',
  'python-dev',
  'code-review',
];
