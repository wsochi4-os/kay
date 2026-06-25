# Kutti Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [v1.0.0] - 2024-XX-XX

### ✅ Added

#### Core Features
- **Complete Kutti project implementation** - Personal AI CLI agent for Android
- **TypeScript CLI package** (`@kutti/cli`) with full feature set
- **Android app** with terminal emulator and Ubuntu environment
- **OpenCode-compatible authentication system** with 9 provider implementations

#### CLI Package (`@kutti/cli`)
- **Core utilities**: constants, logger, config manager
- **Authentication system**: AES-256-GCM encrypted credential storage
- **Multi-provider support**: 14 providers (Groq, Gemini, Ollama, OpenRouter, Mistral, Cerebras, Cohere, Together AI, Hugging Face, DeepSeek, Fireworks AI, OpenAI, Anthropic)
- **Agent loop**: Micro-agent inspired THINK→ACT→OBSERVE→EVALUATE phases
- **Built-in tools**: shell, file operations (read/write/list/search), git (status/diff/commit), test running
- **MCP host**: Model Context Protocol server management
- **Plugin system**: Dynamic loading and lifecycle hooks
- **Skills system**: Markdown-based skills with trigger-based auto-loading
- **CLI commands**: `auth`, `config`, `mcp`, `plugin`, `skills`, `agent`, `chat`

#### Built-in Plugins
- `kutti-plugin-shell`: Shell command execution
- `kutti-plugin-files`: File operations (read, write, list, search)

#### Built-in Skills
- `kutti-core`: Core capabilities, guidelines, and agent loop patterns
- `android-dev`: Android development best practices (Kotlin, Compose, architecture)
- `python-dev`: Python development patterns (type hints, testing, frameworks)
- `code-review`: Code review checklists and patterns

#### Android App
- **Kotlin classes**: `KuttiApplication`, `MainActivity`
- **Terminal emulator**: `TerminalActivity`, `TerminalSession` with Termux libraries
- **Ubuntu environment**: `UbuntuManager`, `ProotRunner` for proot-based Ubuntu
- **Authentication**: `AuthActivity`, `TokenStore` with EncryptedSharedPreferences
- **Settings**: `SettingsActivity` with preferences
- **Complete resource files**: layouts, strings, styles, colors, arrays, drawables
- **AndroidManifest.xml**: All activities, services, and permissions
- **build.gradle.kts**: All dependencies (Termux terminal, proot, coroutines, etc.)

#### OpenCode-Compatible System (Python)
- **Provider Abstraction Layer**:
  - `BaseProvider` interface with common contract
  - 9 provider implementations: OpenAI, Anthropic, Groq, OpenRouter, Mistral, Gemini, Fireworks, Together, DeepSeek
  - Provider capabilities: chat, embeddings, vision, tools, streaming, function calling
  - Dynamic model discovery from provider APIs
  - Plugin system for adding new providers

- **Authentication System**:
  - Multi-provider authentication with secure credential storage
  - Multiple storage backends: Keychain (macOS), Secret Service (Linux), Windows Credential Manager, encrypted file fallback
  - Environment variable detection (OPENAI_API_KEY, ANTHROPIC_API_KEY, GEMINI_API_KEY, etc.)
  - Session management with active provider tracking
  - Token refresh support (stub for OAuth providers)

- **Model System**:
  - Model registry with caching (1 hour TTL)
  - Provider-specific model lists with fallback to known models
  - Model discovery and search capabilities

- **Router System**:
  - Unified request router for provider-agnostic requests
  - Automatic credential loading and session validation
  - Model selection and request dispatching

- **CLI Commands**:
  - `kutti login PROVIDER`: Login with API key
  - `kutti logout PROVIDER`: Logout from providers
  - `kutti providers list`: List all providers
  - `kutti providers use PROVIDER`: Set active provider
  - `kutti models list`: List available models
  - `kutti session`: Show session information

#### Documentation
- **Complete README.md** with usage examples and project structure
- **ARCHITECTURE.md**: Detailed system architecture and component diagrams
- **PLUGIN_API.md**: Complete plugin development guide
- **SKILLS_GUIDE.md**: Skills system documentation
- **MCP_GUIDE.md**: Model Context Protocol usage guide
- **RELEASES.md**: Release and installation documentation

#### Assets & Scripts
- `kutti-bootstrap.sh`: Ubuntu environment setup script
- `download-bootstrap.sh`: Script to download Ubuntu rootfs
- `release.sh`: Automated release creation script

#### Configuration
- **pnpm workspace** with TypeScript and Kotlin support
- **package.json** with build, dev, test, and publish scripts
- **GitHub Actions workflow** for automated builds and releases
- **Signing configuration** templates for Android releases

### 📁 File Structure

```
kutti/
├── README.md                          # Comprehensive documentation
├── LICENSE                           # MIT License
├── VERSION                           # Current version
├── CHANGELOG.md                      # This file
├── RELEASES.md                       # Release documentation
├── package.json                      # Root package.json
├── pnpm-workspace.yaml               # pnpm workspace config
├── requirements.txt                  # Python dependencies
├── setup.py                          # Python package setup
├── kutti.py                          # Python CLI entry point
│
├── .github/
│   ├── workflows/
│   │   └── android-build.yml         # GitHub Actions workflow
│   └── release-config.json           # Release configuration
│
├── packages/
│   ├── cli/                          # TypeScript CLI package
│   │   ├── src/
│   │   │   ├── agent/                # Agent loop & tools
│   │   │   ├── auth/                 # Authentication
│   │   │   ├── commands/             # CLI commands
│   │   │   ├── mcp/                  # MCP host
│   │   │   ├── plugins/              # Plugin loader
│   │   │   ├── providers/            # AI provider adapters
│   │   │   └── skills/               # Skills manager
│   │   └── package.json
│   │
│   └── android/                      # Android app
│       ├── app/
│       │   ├── src/main/
│       │   │   ├── java/dev/kutti/app/
│       │   │   │   ├── terminal/      # Terminal emulator
│       │   │   │   ├── ubuntu/        # Ubuntu environment
│       │   │   │   ├── auth/          # Authentication
│       │   │   │   └── settings/      # Settings
│       │   │   └── res/              # Android resources
│       │   └── build.gradle.kts
│       └── settings.gradle.kts
│
├── providers/                        # Python providers
│   ├── base.py                      # Base provider interface
│   ├── registry.py                  # Provider registry
│   ├── openai.py                    # OpenAI provider
│   ├── anthropic.py                 # Anthropic provider
│   ├── groq.py                      # Groq provider
│   ├── openrouter.py                # OpenRouter provider
│   ├── mistral.py                   # Mistral provider
│   ├── gemini.py                    # Google Gemini provider
│   ├── fireworks.py                 # Fireworks AI provider
│   ├── together.py                  # Together AI provider
│   └── deepseek.py                  # DeepSeek provider
│
├── auth/                           # Authentication system
│   ├── manager.py                   # Authentication manager
│   ├── credentials.py               # Credential store
│   ├── storage.py                   # Secure storage backends
│   └── session.py                   # Session manager
│
├── models/                         # Model management
│   ├── registry.py                  # Model registry
│   └── discovery.py                 # Model discovery
│
├── router/                         # Request routing
│   └── chat.py                      # Chat router
│
├── cli/                            # CLI commands
│   ├── main.py                     # Main entry point
│   ├── login.py                    # Login command
│   ├── logout.py                   # Logout command
│   ├── providers.py                # Providers command
│   ├── models.py                   # Models command
│   └── session.py                  # Session command
│
├── config/                         # Configuration
│   └── providers.yaml              # Provider configuration
│
├── docs/                           # Documentation
│   ├── ARCHITECTURE.md              # System architecture
│   ├── PLUGIN_API.md               # Plugin development
│   ├── SKILLS_GUIDE.md              # Skills documentation
│   └── MCP_GUIDE.md                 # MCP documentation
│
├── plugins/                        # Built-in plugins
│   ├── kutti-plugin-shell/          # Shell plugin
│   └── kutti-plugin-files/          # Files plugin
│
├── skills/                         # Built-in skills
│   ├── kutti-core/                  # Core skills
│   ├── android-dev/                 # Android development
│   ├── python-dev/                  # Python development
│   └── code-review/                 # Code review
│
└── scripts/                        # Utility scripts
    ├── download-bootstrap.sh        # Ubuntu setup
    └── release.sh                   # Release script
```

---

## [Unreleased]

### 🚧 In Progress
- GitHub Actions CI/CD pipeline for automated releases
- APK signing and distribution system
- PyPI package publication

### 🎯 Planned
- OAuth support for providers (Google, Microsoft, etc.)
- Additional AI providers (Cohere, Cerebras, Hugging Face, etc.)
- Improved terminal features (tabs, split panes, themes)
- Better error handling and user feedback
- Plugin marketplace for community plugins
- Cloud sync for settings and credentials
- Team collaboration features
- Advanced AI features (multi-turn conversations, memory, etc.)

---

## 📊 Statistics

- **Total Files**: 148+
- **Total Lines of Code**: 17,888+
- **Providers**: 9 fully implemented (Python) + 14 (TypeScript)
- **CLI Commands**: 6 main commands with subcommands
- **Storage Backends**: 4 (Keychain, Secret Service, Windows, Encrypted File)
- **Authentication Methods**: API Key with OAuth support planned
- **Documentation Files**: 6 comprehensive guides

---

## 🏆 Contributors

- **Primary Developer**: Kutti Team
- **Architecture**: Micro-agent inspired design
- **Inspiration**: OpenCode, Cursor, and other AI development tools

---

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) for details.

---

[Unreleased]: https://github.com/wsochi4-os/kay/compare/v1.0.0...HEAD
[v1.0.0]: https://github.com/wsochi4-os/kay/releases/tag/v1.0.0