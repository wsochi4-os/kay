# Kutti — Your Personal AI CLI Agent

> *Smart. Pluggable. Android-native. Yours.*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Platform: Android](https://img.shields.io/badge/Platform-Android-green)](https://android.com)
[![Terminal: Ubuntu](https://img.shields.io/badge/Terminal-Ubuntu%20Bundled-orange)](https://ubuntu.com)
[![MCP: Supported](https://img.shields.io/badge/MCP-Supported-blue)](https://modelcontextprotocol.io)

---

**Kutti** is a fully autonomous, self-improving AI CLI agent built for Android-first usage. It runs inside a bundled Ubuntu environment (no root required), communicates with multiple free and paid AI providers, supports the Model Context Protocol (MCP), and is extensible through a plugin and skills architecture.

Kutti is inspired by:

- **[micro-agent](https://github.com/BuilderIO/micro-agent)** — iterative test-driven AI coding agent loop
- **[opencode](https://opencode.ai)** — terminal-native AI coding assistant with provider auth
- **[OpenClaw Android](https://github.com/OpenClawAndroid/openclaw-android-assistant)** — Android-native app with bundled Ubuntu and seamless terminal

Think of Kutti as your pocket dev co-pilot that lives on Android, speaks to any AI model you choose, runs real shell commands in a proper Linux environment, and learns from plugins and skills you add to it.

---

## ✨ Features

### 🤖 Core Capabilities

- **Agent Loop**: Micro-agent inspired THINK → ACT → OBSERVE → EVALUATE cycle
- **Multi-Provider**: Support for 12+ AI providers (Groq, Gemini, OpenRouter, Ollama, etc.)
- **MCP Host**: Full Model Context Protocol support with tool and resource access
- **Plugin System**: Extend Kutti with custom commands, tools, and hooks
- **Skills System**: Teach Kutti domain-specific knowledge via markdown files
- **Authentication**: Secure encrypted credential storage with `kutti auth login`

### 📱 Android Features

- **Bundled Ubuntu**: Full Ubuntu 22.04 environment via proot (no root required)
- **Terminal Emulator**: Full xterm-256color terminal with Termux libraries
- **Encrypted Storage**: Android Keystore for secure API key storage
- **Offline Support**: Works without internet for local tasks

### 🔧 Built-in Tools

- **Shell Commands**: Execute bash commands in Ubuntu
- **File Operations**: Read, write, search, modify files
- **Git Integration**: Status, diff, commit, and more
- **Web Access**: Fetch URLs, search the web (with API keys)
- **Test Running**: Execute test commands and verify results

### 🌐 AI Providers

**Free Tier:**
- Groq (Fastest inference)
- Google Gemini (Strong tool use)
- OpenRouter (100+ free models)
- Mistral (Good code tasks)
- Cerebras (Ultra fast)
- Cohere (Strong RAG)
- Together AI (Many open models)
- Ollama (Fully local, no key needed)
- Hugging Face (Rate limited)
- DeepSeek (Excellent coding)
- Fireworks AI (Fast open models)

**Paid:**
- OpenAI
- Anthropic

---

## 🚀 Quick Start

### On Android

1. **Install the APK** (coming soon)
2. **Open Kutti** - It will automatically set up Ubuntu
3. **Authenticate** (optional):
   ```bash
   kutti auth login
   ```
4. **Start using it**:
   ```bash
   kutti "Write a Python script to calculate Fibonacci numbers"
   ```

### On Desktop (Development)

1. **Clone the repository**:
   ```bash
   git clone https://github.com/wsochi4-os/kay.git
   cd kay
   ```

2. **Install dependencies**:
   ```bash
   pnpm install
   ```

3. **Build the CLI**:
   ```bash
   pnpm --filter @kutti/cli build
   ```

4. **Link globally**:
   ```bash
   pnpm --filter @kutti/cli link --global
   ```

5. **Test it**:
   ```bash
   kutti --version
   ```

6. **Authenticate**:
   ```bash
   kutti auth login --provider groq --key YOUR_API_KEY
   ```

7. **Run a task**:
   ```bash
   kutti "Create a REST API endpoint in Node.js"
   ```

---

## 📖 Usage Examples

### Basic Chat

```bash
# Start an interactive chat session
kutti chat

# One-shot question
kutti "Explain how to use React hooks"
```

### Agent Mode (Iterative)

```bash
# Run the agent loop with a task
kutti agent --prompt "Implement a binary search function in Python"

# Fix a failing test
kutti fix --test "npm test" --file src/utils.js

# Build something from a description
kutti build --description "REST API for user authentication" --language typescript
```

### Authentication

```bash
# Interactive login
kutti auth login

# Login to a specific provider
kutti auth login --provider groq --key YOUR_API_KEY

# List authenticated providers
kutti auth list

# Switch provider
kutti auth use gemini

# Logout
kutti auth logout groq
```

### Configuration

```bash
# View current config
kutti config

# Set a configuration value
kutti config set model llama-3.3-70b-versatile
kutti config set temperature 0.5

# Set provider
kutti config set provider openrouter
```

### MCP Servers

```bash
# List configured servers
kutti mcp list

# Add a server
kutti mcp add filesystem --command npx --args -y @modelcontextprotocol/server-filesystem

# Start a server
kutti mcp start filesystem

# List tools from a server
kutti mcp tools filesystem

# Test connection
kutti mcp ping filesystem
```

### Plugins

```bash
# List installed plugins
kutti plugin list

# Install a plugin
kutti plugin install my-plugin

# Enable/disable a plugin
kutti plugin enable my-plugin
kutti plugin disable my-plugin

# Remove a plugin
kutti plugin remove my-plugin
```

### Skills

```bash
# List installed skills
kutti skills list

# Enable a skill
kutti skills enable android-dev

# View active skills
kutti skills active

# Search for skills
kutti skills search python
```

---

## 🏗️ Project Structure

```
kutti/
├── packages/
│   ├── cli/                          # Main CLI package (TypeScript/Node.js)
│   │   ├── src/
│   │   │   ├── index.ts              # Entry point
│   │   │   ├── commands/             # CLI commands
│   │   │   │   ├── auth.ts
│   │   │   │   ├── config.ts
│   │   │   │   ├── mcp.ts
│   │   │   │   ├── plugin.ts
│   │   │   │   ├── skills.ts
│   │   │   │   ├── agent.ts
│   │   │   │   └── chat.ts
│   │   │   ├── agent/                # Agent loop
│   │   │   │   ├── loop.ts
│   │   │   │   └── tools.ts
│   │   │   ├── providers/            # AI providers
│   │   │   │   ├── base.ts
│   │   │   │   ├── groq.ts
│   │   │   │   ├── gemini.ts
│   │   │   │   ├── ollama.ts
│   │   │   │   └── openrouter.ts
│   │   │   ├── mcp/                  # MCP support
│   │   │   │   └── host.ts
│   │   │   ├── plugins/              # Plugin loader
│   │   │   │   └── loader.ts
│   │   │   ├── skills/               # Skills manager
│   │   │   │   └── manager.ts
│   │   │   ├── auth/                 # Authentication
│   │   │   │   ├── manager.ts
│   │   │   │   └── keystore.ts
│   │   │   └── utils/                # Utilities
│   │   │       ├── config.ts
│   │   │       ├── logger.ts
│   │   │       └── constants.ts
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
│   │   └── SKILL.md
│   ├── android-dev/
│   │   └── SKILL.md
│   ├── python-dev/
│   │   └── SKILL.md
│   └── code-review/
│       └── SKILL.md
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
└── README.md
```

---

## 📚 Documentation

- **[Architecture](docs/ARCHITECTURE.md)** - Detailed system architecture
- **[Plugin API](docs/PLUGIN_API.md)** - How to create plugins
- **[Skills Guide](docs/SKILLS_GUIDE.md)** - How to create and use skills
- **[MCP Guide](docs/MCP_GUIDE.md)** - Model Context Protocol usage

---

## 🛠️ Building from Source

### Prerequisites

- Node.js 20+
- pnpm
- Android SDK (for Android build)
- Java 17+ (for Android build)

### Development Build

```bash
# Clone
git clone https://github.com/wsochi4-os/kay.git
cd kay

# Install dependencies
pnpm install

# Build CLI
pnpm --filter @kutti/cli build

# Link globally for development
pnpm --filter @kutti/cli link --global

# Test
kutti --version
```

### Android Build

```bash
# Download Ubuntu arm64 bootstrap (run once)
./scripts/download-bootstrap.sh

# Build debug APK
cd packages/android
./gradlew assembleDebug

# Output: packages/android/app/build/outputs/apk/debug/kutti-debug.apk

# Install on device
adb install app/build/outputs/apk/debug/kutti-debug.apk
```

### Publishing

```bash
# Publish CLI to npm
pnpm --filter @kutti/cli publish --access public

# Build release APK
./scripts/build-android.sh --release

# Tag release
git tag v1.0.0
git push origin v1.0.0
```

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feat/my-feature`)
3. Make your changes
4. Test your changes (`pnpm test`)
5. Commit your changes (`git commit -m 'feat: add my feature'`)
6. Push to the branch (`git push origin feat/my-feature`)
7. Open a Pull Request

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

- **[micro-agent](https://github.com/BuilderIO/micro-agent)** for the iterative agent loop inspiration
- **[opencode](https://opencode.ai)** for the authentication flow and CLI design
- **[OpenClaw Android](https://github.com/OpenClawAndroid/openclaw-android-assistant)** for the Android architecture
- **[Model Context Protocol](https://modelcontextprotocol.io)** for the tool and resource access
- **[Termux](https://termux.com)** for the terminal emulator libraries

---

## 💬 Community

- **GitHub**: [wsochi4-os/kay](https://github.com/wsochi4-os/kay)
- **Issues**: Report bugs and request features
- **Discussions**: Ask questions and share ideas

---

*Built with 🤖 by the Kutti community. Named after the Tamil word for "small one" — because the best tools stay out of your way.*
