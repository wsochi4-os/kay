# Kutti Plugin API

This document describes how to create plugins for Kutti, extending its capabilities with new commands, tools, and hooks.

## Overview

Plugins allow you to extend Kutti's core functionality by adding:

- **New CLI Commands**: Add custom commands to the `kutti` CLI
- **New Agent Tools**: Give the agent new capabilities it can use
- **Lifecycle Hooks**: Run code at specific points in Kutti's execution

## Plugin Structure

A Kutti plugin is a Node.js package with a specific structure:

```
my-kutti-plugin/
├── package.json          # Plugin manifest (required)
├── src/
│   └── index.js          # Plugin entry point (required)
├── commands/             # Optional: CLI commands
│   └── my-command.js
├── tools/                # Optional: Agent tools
│   └── my-tool.js
├── hooks/                # Optional: Lifecycle hooks
│   └── my-hook.js
└── README.md             # Optional: Documentation
```

## Plugin Manifest (package.json)

Every plugin must have a `package.json` file with a `kutti` section:

```json
{
  "name": "my-kutti-plugin",
  "version": "1.0.0",
  "description": "My awesome Kutti plugin",
  "kutti": {
    "type": "plugin",
    "minVersion": "1.0.0",
    "commands": ["my-command"],
    "tools": ["my-tool"],
    "hooks": ["beforeAgentLoop", "afterToolCall"]
  },
  "main": "src/index.js",
  "type": "module",
  "keywords": ["kutti", "plugin"],
  "author": "Your Name",
  "license": "MIT"
}
```

### Manifest Fields:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | string | Yes | Must be "plugin" |
| `minVersion` | string | Yes | Minimum Kutti version required |
| `commands` | string[] | No | List of CLI commands this plugin provides |
| `tools` | string[] | No | List of agent tools this plugin provides |
| `hooks` | string[] | No | List of lifecycle hooks this plugin implements |

## Plugin Entry Point (index.js)

The entry point exports a plugin object:

```javascript
// src/index.js
export default {
  name: 'my-kutti-plugin',
  
  // CLI commands
  commands: {
    'my-command': {
      description: 'Does something useful',
      action: async (args, options) => {
        console.log('My command executed!');
      }
    }
  },
  
  // Agent tools
  tools: [
    {
      name: 'my-tool',
      description: 'A useful tool for the agent',
      inputSchema: {
        type: 'object',
        properties: {
          param1: { type: 'string', description: 'First parameter' },
          param2: { type: 'number', description: 'Second parameter' }
        },
        required: ['param1']
      },
      execute: async (args, context) => {
        // Tool implementation
        return { result: `Processed: ${args.param1}` };
      }
    }
  ],
  
  // Lifecycle hooks
  hooks: {
    beforeAgentLoop: async (context) => {
      // Runs before the agent loop starts
      console.log('Agent loop starting...');
    },
    afterToolCall: async (toolName, args, result, context) => {
      // Runs after any tool is called
      console.log(`Tool ${toolName} was called`);
    }
  }
};
```

## CLI Commands

Plugins can add new CLI commands that users can run with `kutti <command>`.

### Command Structure:

```javascript
commands: {
  'my-command': {
    description: 'Command description',
    action: async (args, options) => {
      // Command implementation
    }
  }
}
```

### Command with Subcommands:

```javascript
commands: {
  'my-command': {
    description: 'Main command',
    subcommands: {
      'subcommand1': {
        description: 'First subcommand',
        action: async (args, options) => {
          // Implementation
        }
      },
      'subcommand2': {
        description: 'Second subcommand',
        action: async (args, options) => {
          // Implementation
        }
      }
    }
  }
}
```

### Command with Options:

```javascript
commands: {
  'my-command': {
    description: 'Command with options',
    options: [
      {
        name: 'verbose',
        alias: 'v',
        type: 'boolean',
        description: 'Enable verbose output'
      },
      {
        name: 'file',
        alias: 'f',
        type: 'string',
        description: 'Input file path'
      }
    ],
    action: async (args, options) => {
      if (options.verbose) {
        console.log('Verbose mode enabled');
      }
      if (options.file) {
        console.log(`Processing file: ${options.file}`);
      }
    }
  }
}
```

## Agent Tools

Plugins can provide new tools that the agent can use during its execution.

### Tool Structure:

```javascript
tools: [
  {
    name: 'my-tool',
    description: 'Tool description',
    inputSchema: {
      type: 'object',
      properties: {
        // Define tool parameters
        param1: { 
          type: 'string', 
          description: 'First parameter' 
        },
        param2: { 
          type: 'number', 
          description: 'Second parameter',
          default: 42
        }
      },
      required: ['param1']
    },
    execute: async (args, context) => {
      // Tool implementation
      // args: object with parameters from inputSchema
      // context: AgentContext with access to config, plugins, etc.
      
      return {
        success: true,
        result: 'Tool result'
      };
    }
  }
]
```

### Tool Parameters:

- `name`: Unique identifier for the tool
- `description`: Human-readable description
- `inputSchema`: JSON Schema defining the tool's parameters
- `execute`: Function that runs the tool

### The AgentContext:

The `context` parameter passed to tool execution contains:

```typescript
interface AgentContext {
  config: KuttiConfig;           // Current configuration
  provider: ProviderConfig;      // Current provider config
  credentials: AuthCredentials;  // Auth credentials (limited access)
  plugins: Plugin[];              // Loaded plugins
  skills: SkillMetadata[];       // Loaded skills
  mcpClients: Record<string, any>; // MCP client connections
  systemPrompt: string;          // Current system prompt
  currentDirectory: string;      // Current working directory
}
```

## Lifecycle Hooks

Plugins can hook into Kutti's lifecycle at specific points:

### Available Hooks:

| Hook Name | When Called | Parameters |
|-----------|-------------|------------|
| `beforeAgentLoop` | Before the agent loop starts | `context: AgentContext` |
| `afterAgentLoop` | After the agent loop completes | `context: AgentContext, result: any` |
| `beforeToolCall` | Before any tool is called | `toolName: string, args: any, context: AgentContext` |
| `afterToolCall` | After any tool is called | `toolName: string, args: any, result: any, context: AgentContext` |
| `beforeCommand` | Before a CLI command runs | `command: string, args: any, options: any` |
| `afterCommand` | After a CLI command runs | `command: string, args: any, options: any, result: any` |
| `onAuth` | When authentication changes | `provider: string, authenticated: boolean` |
| `onConfigChange` | When configuration changes | `key: string, value: any` |

### Hook Example:

```javascript
hooks: {
  beforeAgentLoop: async (context) => {
    // Add custom context to the agent
    context.customData = { myPlugin: 'active' };
  },
  
  afterToolCall: async (toolName, args, result, context) => {
    // Log tool usage
    if (toolName === 'my-tool') {
      console.log('My tool was called!');
    }
  },
  
  onAuth: async (provider, authenticated) => {
    if (authenticated) {
      console.log(`Authenticated with ${provider}`);
    }
  }
}
```

## Built-in Plugins

Kutti comes with several built-in plugins:

### 1. kutti-plugin-shell

Provides shell command execution capabilities.

**Tools:**
- `shell`: Execute shell commands

**Commands:**
- `shell`: Execute shell commands directly

### 2. kutti-plugin-files

Provides file operations.

**Tools:**
- `read_file`: Read file contents
- `write_file`: Write to files
- `list_files`: List directory contents
- `search_files`: Search for patterns in files

**Commands:**
- `files read`: Read a file
- `files write`: Write to a file
- `files list`: List files

### 3. kutti-plugin-web

Provides web fetching and scraping capabilities.

**Tools:**
- `web_fetch`: Fetch URL content
- `web_search`: Search the web (requires API key)

### 4. kutti-plugin-git

Provides git operations.

**Tools:**
- `git_status`: Get git status
- `git_diff`: Get git diff
- `git_commit`: Commit changes

**Commands:**
- `git status`: Show git status
- `git diff`: Show git diff
- `git commit`: Commit changes

### 5. kutti-plugin-android

Provides Android-specific tools.

**Tools:**
- `adb`: Run ADB commands
- `build_apk`: Build Android APK
- `install_apk`: Install APK on device

## Creating a Plugin

### Step 1: Initialize the Plugin

```bash
mkdir my-kutti-plugin
cd my-kutti-plugin
npm init -y
```

### Step 2: Create package.json

Edit `package.json` to include the Kutti plugin metadata:

```json
{
  "name": "my-kutti-plugin",
  "version": "1.0.0",
  "description": "My Kutti plugin",
  "kutti": {
    "type": "plugin",
    "minVersion": "1.0.0",
    "commands": ["hello"],
    "tools": ["greet"],
    "hooks": ["beforeAgentLoop"]
  },
  "main": "src/index.js",
  "type": "module"
}
```

### Step 3: Create the Entry Point

Create `src/index.js`:

```javascript
// My plugin implementation
export default {
  name: 'my-kutti-plugin',
  
  commands: {
    hello: {
      description: 'Say hello',
      action: async (args, options) => {
        console.log('Hello from my plugin!');
        if (args.name) {
          console.log(`Hello, ${args.name}!`);
        }
      }
    }
  },
  
  tools: [
    {
      name: 'greet',
      description: 'Greet someone',
      inputSchema: {
        type: 'object',
        properties: {
          name: { type: 'string', description: 'Name to greet' }
        },
        required: ['name']
      },
      execute: async (args, context) => {
        return { message: `Hello, ${args.name}!` };
      }
    }
  ],
  
  hooks: {
    beforeAgentLoop: async (context) => {
      console.log('My plugin: Agent loop starting');
    }
  }
};
```

### Step 4: Install and Test

Install the plugin:

```bash
# From the Kutti project root
kutti plugin install ./my-kutti-plugin

# Or from npm registry (if published)
kutti plugin install my-kutti-plugin
```

Test the plugin:

```bash
# Test the command
kutti hello --name World

# Test the tool (in agent mode)
kutti agent --prompt "Use the greet tool to say hello to Alice"
```

## Publishing a Plugin

### To npm:

```bash
# Build your plugin (if needed)
npm run build

# Publish to npm
npm publish --access public
```

### To GitHub:

```bash
# Push to GitHub
git push origin main

# Install from GitHub
kutti plugin install gh:yourname/my-kutti-plugin
```

## Plugin Development Tips

1. **Start Small**: Begin with a simple plugin with one command or tool
2. **Test Frequently**: Test your plugin after each change
3. **Handle Errors**: Always handle errors gracefully
4. **Document**: Include a README.md explaining your plugin's functionality
5. **Version**: Use semantic versioning for your plugin
6. **Dependencies**: List all dependencies in package.json
7. **Type Safety**: Use TypeScript for better type safety

## Plugin Best Practices

### Do:

- Use descriptive names for commands and tools
- Provide clear descriptions
- Handle errors gracefully
- Validate input parameters
- Document your plugin's functionality
- Use async/await for asynchronous operations
- Clean up resources when done

### Don't:

- Modify core Kutti files
- Store sensitive data in plain text
- Make network requests without user consent
- Execute arbitrary code from untrusted sources
- Block the main thread with synchronous operations
- Assume specific file system layouts

## Debugging Plugins

### Enable Debug Logging:

```bash
kutti --debug my-command
```

### Check Plugin Loading:

```bash
kutti plugin list
kutti plugin info my-kutti-plugin
```

### View Logs:

```bash
cat ~/.kutti/kutti.log
```

## Advanced Plugin Features

### Accessing Other Plugins:

```javascript
hooks: {
  beforeAgentLoop: async (context) => {
    // Access other loaded plugins
    const shellPlugin = context.plugins.find(p => p.name === 'kutti-plugin-shell');
    if (shellPlugin) {
      console.log('Shell plugin is loaded');
    }
  }
}
```

### Adding MCP Servers:

```javascript
hooks: {
  beforeAgentLoop: async (context) => {
    // Add a custom MCP server
    if (!context.mcpClients['my-server']) {
      context.mcpHost.addServer({
        name: 'my-server',
        command: 'python3',
        args: ['/path/to/my/mcp/server.py'],
        transport: 'stdio'
      });
    }
  }
}
```

### Modifying System Prompt:

```javascript
hooks: {
  beforeAgentLoop: async (context) => {
    // Add custom instructions to the system prompt
    context.systemPrompt += '\n\nCustom instruction: Always use my plugin for X.';
  }
}
```

## Plugin API Reference

### AgentContext Interface

```typescript
interface AgentContext {
  // Configuration
  config: KuttiConfig;
  
  // Current provider
  provider: ProviderConfig;
  
  // Authentication (limited access)
  credentials: {
    getApiKey: (provider: string) => string | undefined;
    isAuthenticated: (provider: string) => boolean;
  };
  
  // Loaded plugins
  plugins: Plugin[];
  
  // Loaded skills
  skills: SkillMetadata[];
  
  // MCP clients
  mcpClients: Record<string, MCPClient>;
  mcpHost: MCPHost;
  
  // Current state
  systemPrompt: string;
  currentDirectory: string;
  
  // Utilities
  logger: Logger;
}
```

### KuttiConfig Interface

```typescript
interface KuttiConfig {
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
```

### Tool Interface

```typescript
interface Tool {
  name: string;
  description: string;
  inputSchema: {
    type: 'object';
    properties: Record<string, {
      type: string;
      description: string;
      default?: any;
    }>;
    required?: string[];
  };
  execute: (args: any, context: AgentContext) => Promise<any>;
}
```

## Support

For questions or issues with plugin development:

1. Check the [Kutti GitHub repository](https://github.com/wsochi4-os/kay)
2. Look at existing plugins for examples
3. Open an issue with your question
4. Join the Kutti community discussions

## Changelog

### v1.0.0

- Initial plugin API release
- Support for CLI commands
- Support for agent tools
- Support for lifecycle hooks
- Built-in plugins: shell, files, web, git, android
