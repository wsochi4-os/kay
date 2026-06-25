# Kutti Architecture

This document describes the architecture of Kutti, a personal AI CLI agent for Android.

## Overview

Kutti is designed with a modular, extensible architecture that allows it to run on Android devices with a bundled Ubuntu environment, while also supporting traditional desktop environments.

```
┌─────────────────────────────────────────────────────────────┐
│                      KUTTI ARCHITECTURE                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                    ANDROID APP                          │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │   │
│  │  │ MainActivity │  │AuthActivity  │  │Settings      │ │   │
│  │  └──────────────┘  └──────────────┘  │Activity      │ │   │
│  │        │               │               └──────────────┘ │   │
│  │        └───────────────┼───────────────────────────────┘   │
│  │                            │                               │   │
│  │                    ┌───────────────┐                       │   │
│  │                    │ UbuntuManager │                       │   │
│  │                    └───────────────┘                       │   │
│  │                            │                               │   │
│  │                    ┌───────────────┐                       │   │
│  │                    │  ProotRunner  │                       │   │
│  │                    └───────────────┘                       │   │
│  └──────────────────────────────────────────────────────────┘   │
│                            │                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │               BUNDLED UBUNTU (proot)                    │   │
│  │                                                          │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │   │
│  │  │   /bin       │  │   /usr       │  │   /home      │   │   │
│  │  │   /lib       │  │   /etc       │  │   /kutti     │   │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘   │   │
│  │                                                          │   │
│  │  ┌──────────────────────────────────────────────────┐   │   │
│  │  │               KUTTI CLI (Node.js)                  │   │   │
│  │  │                                                      │   │   │
│  │  │  ┌──────────────┐  ┌──────────────┐                │   │   │
│  │  │  │   Commands   │  │   Agent      │                │   │   │
│  │  │  │              │  │   Loop       │                │   │   │
│  │  │  └──────────────┘  └──────────────┘                │   │   │
│  │  │                                                      │   │   │
│  │  │  ┌──────────────┐  ┌──────────────┐                │   │   │
│  │  │  │  Providers   │  │   Auth       │                │   │   │
│  │  │  │              │  │  Manager     │                │   │   │
│  │  │  └──────────────┘  └──────────────┘                │   │   │
│  │  │                                                      │   │   │
│  │  │  ┌──────────────┐  ┌──────────────┐                │   │   │
│  │  │  │   MCP Host   │  │  Plugin      │                │   │   │
│  │  │  │              │  │  Loader      │                │   │   │
│  │  │  └──────────────┘  └──────────────┘                │   │   │
│  │  │                                                      │   │   │
│  │  │  ┌──────────────┐  ┌──────────────┐                │   │   │
│  │  │  │  Skills      │  │   Config     │                │   │   │
│  │  │  │  Manager     │  │  Manager     │                │   │   │
│  │  │  └──────────────┘  └──────────────┘                │   │   │
│  │  └──────────────────────────────────────────────────┘   │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                            │
└─────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Android App Layer

The Android app provides the native container for Kutti on mobile devices.

#### Main Components:

- **MainActivity**: Entry point that checks Ubuntu setup and launches the terminal
- **TerminalActivity**: Full-screen terminal emulator using Termux libraries
- **AuthActivity**: Web-based authentication flow for AI providers
- **SettingsActivity**: Configuration UI for Kutti settings
- **UbuntuManager**: Manages the bundled Ubuntu environment
- **ProotRunner**: Handles proot execution for running Ubuntu without root

#### Key Features:

- Bundled Ubuntu 22.04 rootfs via proot
- Terminal emulator with xterm-256color support
- Encrypted credential storage using Android Keystore
- Background service for long-running operations

### 2. CLI Layer (Node.js/TypeScript)

The core Kutti functionality is implemented as a CLI application that can run both on Android (inside the Ubuntu environment) and on traditional desktop environments.

#### Main Modules:

- **index.ts**: Main entry point and CLI parser
- **commands/**: CLI command implementations
  - auth.ts: Authentication commands
  - config.ts: Configuration commands
  - mcp.ts: MCP server management
  - plugin.ts: Plugin management
  - skills.ts: Skills management
  - agent.ts: Agent loop commands
  - chat.ts: Chat interface

- **agent/**: Agent loop implementation
  - loop.ts: Main agent loop (THINK -> ACT -> OBSERVE -> EVALUATE)
  - tools.ts: Built-in tools for the agent

- **providers/**: AI provider adapters
  - base.ts: Base provider interface
  - groq.ts: Groq provider
  - gemini.ts: Google Gemini provider
  - ollama.ts: Ollama (local) provider
  - openrouter.ts: OpenRouter provider

- **mcp/**: Model Context Protocol support
  - host.ts: MCP host implementation
  - client.ts: MCP client connections

- **plugins/**: Plugin system
  - loader.ts: Plugin loading and management

- **skills/**: Skills system
  - manager.ts: Skills loading and management

- **auth/**: Authentication
  - manager.ts: Auth flow management
  - keystore.ts: Encrypted credential storage

- **utils/**: Utilities
  - config.ts: Configuration management
  - logger.ts: Logging
  - constants.ts: Constants and defaults

### 3. Plugin System

Plugins extend Kutti's core capabilities with new commands, tools, and hooks.

#### Plugin Structure:

```
plugin-name/
├── package.json          # Plugin manifest
├── src/
│   └── index.js          # Plugin entry point
├── commands/             # New CLI commands
│   └── my-command.js
├── tools/                # New agent tools
│   └── my-tool.js
└── README.md
```

#### Built-in Plugins:

- **kutti-plugin-shell**: Shell command execution
- **kutti-plugin-files**: File operations
- **kutti-plugin-web**: Web fetching and scraping
- **kutti-plugin-git**: Git operations
- **kutti-plugin-android**: Android-specific tools

### 4. Skills System

Skills are markdown files that teach Kutti how to approach specific tasks by shaping its system prompt.

#### Skill Structure:

```
skill-name/
└── SKILL.md              # Skill definition
```

#### Built-in Skills:

- **kutti-core**: Core capabilities and guidelines
- **android-dev**: Android development best practices
- **python-dev**: Python development guidelines
- **code-review**: Code review checklist and patterns

### 5. MCP Support

Kutti is a full MCP host that can discover, launch, and communicate with MCP servers.

#### MCP Architecture:

```
Kutti MCP Host
    │
    ├── MCP Server Discovery
    ├── Server Lifecycle Management
    │   ├── Start/Stop
    │   └── Health Checks
    ├── Tool Registry
    │   ├── List Tools
    │   └── Call Tools
    └── Resource Access
        ├── List Resources
        └── Read Resources
```

## Data Flow

### Command Execution Flow:

```
User Input
    │
    ▼
CLI Parser (commander)
    │
    ▼
Command Handler
    │
    ▼
┌─────────────────────────────┐
│ Initialize Systems:          │
│ - Load plugins              │
│ - Load skills               │
│ - Start MCP servers         │
└─────────────────────────────┘
    │
    ▼
┌─────────────────────────────┐
│ Execute Command:            │
│ - auth login                │
│ - agent run                 │
│ - chat                      │
│ - config set                │
└─────────────────────────────┘
    │
    ▼
Output Result
```

### Agent Loop Flow:

```
User Prompt
    │
    ▼
THINK Phase
    │
    ▼
Generate Plan (using LLM)
    │
    ▼
ACT Phase
    │
    ▼
Execute Actions
    │
    ├── Call Tools
    ├── Run Shell Commands
    ├── Read/Write Files
    └── Call MCP Tools
    │
    ▼
OBSERVE Phase
    │
    ▼
Collect Observations
    │
    ├── Tool Results
    ├── Command Output
    ├── File Contents
    └── Test Results
    │
    ▼
EVALUATE Phase
    │
    ▼
Check Completion (using LLM)
    │
    ├── Task Complete? → Return Result
    └── Not Complete? → Back to THINK
```

## File System Layout

```
kutti/
├── packages/
│   ├── cli/                          # Main CLI package
│   │   ├── src/
│   │   │   ├── index.ts              # Entry point
│   │   │   ├── commands/             # CLI commands
│   │   │   ├── agent/                # Agent loop
│   │   │   ├── providers/            # AI providers
│   │   │   ├── mcp/                  # MCP support
│   │   │   ├── plugins/              # Plugin loader
│   │   │   ├── skills/               # Skills manager
│   │   │   ├── auth/                 # Authentication
│   │   │   └── utils/                # Utilities
│   │   └── package.json
│   │
│   └── android/                      # Android app
│       ├── app/
│       │   ├── src/main/
│       │   │   ├── java/dev/kutti/app/
│       │   │   │   ├── MainActivity.kt
│       │   │   │   ├── terminal/
│       │   │   │   │   ├── TerminalActivity.kt
│       │   │   │   │   └── TerminalSession.kt
│       │   │   │   ├── ubuntu/
│       │   │   │   │   ├── UbuntuManager.kt
│       │   │   │   │   └── ProotRunner.kt
│       │   │   │   ├── auth/
│       │   │   │   │   ├── AuthActivity.kt
│       │   │   │   │   └── TokenStore.kt
│       │   │   │   └── settings/
│       │   │   │       └── SettingsActivity.kt
│       │   │   └── assets/
│       │   │       ├── bootstrap-aarch64.tar.gz
│       │   │       ├── kutti-bootstrap.sh
│       │   │       └── mcps/
│       │   └── build.gradle.kts
│       └── settings.gradle.kts
│
├── plugins/                          # Built-in plugins
│   ├── kutti-plugin-shell/
│   ├── kutti-plugin-files/
│   ├── kutti-plugin-web/
│   ├── kutti-plugin-git/
│   └── kutti-plugin-android/
│
├── skills/                           # Built-in skills
│   ├── kutti-core/
│   ├── android-dev/
│   ├── python-dev/
│   └── code-review/
│
├── scripts/                          # Utility scripts
│   └── download-bootstrap.sh
│
├── docs/                             # Documentation
│   ├── ARCHITECTURE.md
│   ├── PLUGIN_API.md
│   ├── SKILLS_GUIDE.md
│   └── MCP_GUIDE.md
│
├── package.json                      # Root package.json
├── pnpm-workspace.yaml               # pnpm workspace config
└── README.md                         # Project README
```

## Configuration Files

### Main Configuration (`~/.kutti/config.json`):

```json
{
  "version": "1",
  "provider": "groq",
  "model": "llama-3.3-70b-versatile",
  "temperature": 0.2,
  "maxTokens": 8192,
  "agent": {
    "maxIterations": 20,
    "autoConfirm": false,
    "autoConfirmShell": false,
    "contextLines": 5
  },
  "terminal": {
    "theme": "gruvbox-dark",
    "fontSize": 14,
    "fontFamily": "JetBrains Mono",
    "cursorStyle": "block",
    "scrollback": 10000
  },
  "skills": {
    "autoDetect": true,
    "alwaysLoad": ["kutti-core"]
  },
  "mcp": {
    "timeout": 30000,
    "autoRestart": true
  },
  "log": {
    "level": "info",
    "file": "~/.kutti/kutti.log"
  }
}
```

### Providers Configuration (`~/.kutti/providers.json`):

```json
{
  "groq": {
    "endpoint": "https://api.groq.com/openai/v1",
    "model": "llama-3.3-70b-versatile",
    "maxTokens": 8192,
    "temperature": 0.2
  },
  "gemini": {
    "endpoint": "https://generativelanguage.googleapis.com/v1beta",
    "model": "gemini-2.0-flash",
    "maxTokens": 8192
  }
}
```

### MCP Configuration (`~/.kutti/mcp.json`):

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/home/kutti"],
      "transport": "stdio",
      "autoStart": true
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_TOKEN}"
      }
    }
  }
}
```

## Security Considerations

1. **Credential Storage**: API keys are encrypted using AES-256-GCM with keys stored in:
   - Android Keystore on Android devices
   - OS keyring on desktop environments

2. **Sandboxing**: Ubuntu runs in a proot environment without root access, providing isolation from the host system.

3. **Network Security**: All network requests use HTTPS and proper authentication headers.

4. **Input Validation**: All user input is validated before execution to prevent command injection.

## Performance Considerations

1. **Caching**: Frequently used data is cached to minimize API calls.

2. **Lazy Loading**: Plugins and skills are loaded on-demand.

3. **Streaming**: Large responses are streamed when possible to reduce memory usage.

4. **Background Processing**: Long-running operations are performed in background threads/services.

## Extensibility

Kutti is designed to be easily extensible:

1. **Add a New Provider**: Implement the `Provider` interface in `providers/`
2. **Add a New Plugin**: Create a new package in `plugins/` with a `package.json` manifest
3. **Add a New Skill**: Create a new directory in `skills/` with a `SKILL.md` file
4. **Add a New MCP Server**: Configure it in `mcp.json` or use `kutti mcp add`

## Error Handling

Kutti uses a consistent error handling approach:

1. **User Errors**: Clear, actionable error messages
2. **System Errors**: Logged with full context for debugging
3. **Recovery**: Automatic retry for transient errors
4. **Fallback**: Graceful degradation when features are unavailable

## Logging

Kutti provides comprehensive logging:

- **Levels**: debug, info, warn, error
- **Output**: Console and file (`~/.kutti/kutti.log`)
- **Format**: Timestamped, structured log entries
- **Control**: Configurable log level via config or environment variables

## Testing

Kutti includes:

1. **Unit Tests**: For individual components
2. **Integration Tests**: For system interactions
3. **End-to-End Tests**: For complete workflows
4. **Manual Testing**: For Android-specific features

## Future Architecture Improvements

1. **Plugin Isolation**: Sandbox plugins for security
2. **Skill Versioning**: Support multiple versions of skills
3. **MCP Caching**: Cache MCP server responses
4. **Offline Support**: Better offline functionality
5. **Sync Across Devices**: Cloud sync for configuration and skills
