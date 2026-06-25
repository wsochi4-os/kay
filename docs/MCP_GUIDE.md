# Kutti MCP Guide

This document explains how to use the Model Context Protocol (MCP) with Kutti. MCP allows Kutti to interact with external tools, APIs, and resources, giving it access to a vast ecosystem of capabilities.

## Overview

MCP (Model Context Protocol) is an open protocol that enables AI models to interact with external systems. Kutti is a full MCP host, meaning it can:

- **Discover** MCP servers
- **Launch** MCP servers
- **Communicate** with MCP servers over stdio or SSE
- **Use Tools** exposed by MCP servers
- **Access Resources** exposed by MCP servers

```
┌─────────────────────────────────────────────────────────────┐
│                    KUTTI MCP ARCHITECTURE                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                    KUTTI MCP HOST                       │   │
│  │                                                          │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │   │
│  │  │  Server      │  │  Client      │  │  Registry    │ │   │
│  │  │  Manager     │  │  Manager     │  │              │ │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘ │   │
│  │                                                          │   │
│  │  ┌──────────────────────────────────────────────────┐   │   │
│  │  │                  MCP SERVERS                       │   │   │
│  │  │                                                      │   │   │
│  │  │  ┌──────────────┐  ┌──────────────┐                │   │   │
│  │  │  │ Filesystem   │  │  GitHub      │                │   │   │
│  │  │  │ Server       │  │  Server      │                │   │   │
│  │  │  └──────────────┘  └──────────────┘                │   │   │
│  │  │                                                      │   │   │
│  │  │  ┌──────────────┐  ┌──────────────┐                │   │   │
│  │  │  │ PostgreSQL   │  │  Brave       │                │   │   │
│  │  │  │ Server       │  │  Search      │                │   │   │
│  │  │  └──────────────┘  └──────────────┘                │   │   │
│  │  │                                                      │   │   │
│  │  │  ┌──────────────┐                                  │   │   │
│  │  │  │  Custom      │                                  │   │   │
│  │  │  │  Server      │                                  │   │   │
│  │  │  └──────────────┘                                  │   │   │
│  │  └──────────────────────────────────────────────────┘   │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                            │
└─────────────────────────────────────────────────────────────┘
```

## Quick Start

### 1. List Available MCP Servers

```bash
kutti mcp list
```

### 2. Add an MCP Server

```bash
kutti mcp add filesystem --command npx --args -y @modelcontextprotocol/server-filesystem /home/kutti
```

### 3. Start the Server

```bash
kutti mcp start filesystem
```

### 4. List Tools from the Server

```bash
kutti mcp tools filesystem
```

### 5. Use the Tools in Agent Mode

```bash
kutti agent --prompt "List all files in the current directory using the filesystem MCP server"
```

## MCP Concepts

### MCP Servers

An MCP server is a program that implements the MCP protocol. It exposes:

- **Tools**: Functions that can be called by the LLM
- **Resources**: Data that can be read by the LLM
- **Prompts**: Pre-defined prompts for specific tasks

### Transports

MCP servers communicate with Kutti using:

- **stdio**: Standard input/output (most common)
- **sse**: Server-Sent Events (for web-based servers)

### Tool Calling

When Kutti calls a tool:

1. The LLM decides which tool to use
2. Kutti sends the tool call to the MCP server
3. The server executes the tool
4. The server returns the result
5. Kutti passes the result back to the LLM

## Built-in MCP Servers

Kutti comes with support for several MCP servers out of the box:

### 1. Filesystem Server

Provides access to the file system.

**Installation:**
```bash
kutti mcp add filesystem --command npx --args -y @modelcontextprotocol/server-filesystem /home/kutti
```

**Tools:**
- `read_resource`: Read a file
- `list_resources`: List files in a directory

**Example Usage:**
```bash
# List files
kutti agent --prompt "List all Python files in the current directory"

# Read a file
kutti agent --prompt "Read the README.md file"
```

### 2. GitHub Server

Provides access to GitHub repositories.

**Installation:**
```bash
kutti mcp add github --command npx --args -y @modelcontextprotocol/server-github
```

**Requires:** `GITHUB_PERSONAL_ACCESS_TOKEN` environment variable

**Tools:**
- `get_issue`: Get a GitHub issue
- `list_issues`: List issues in a repository
- `create_issue`: Create a new issue

**Example Usage:**
```bash
# Set your GitHub token
export GITHUB_PERSONAL_ACCESS_TOKEN=your_token

# List issues
kutti agent --prompt "List all open issues in owner/repo"
```

### 3. PostgreSQL Server

Provides access to PostgreSQL databases.

**Installation:**
```bash
kutti mcp add postgres --command npx --args -y @modelcontextprotocol/server-postgres
```

**Requires:** `POSTGRES_CONNECTION_STRING` environment variable

**Tools:**
- `execute_query`: Execute a SQL query
- `list_tables`: List all tables

**Example Usage:**
```bash
# Set your connection string
export POSTGRES_CONNECTION_STRING=postgresql://user:pass@localhost/db

# Query the database
kutti agent --prompt "List all users from the users table"
```

### 4. Brave Search Server

Provides web search capabilities.

**Installation:**
```bash
kutti mcp add brave --command npx --args -y @modelcontextprotocol/server-brave-search
```

**Requires:** `BRAVE_API_KEY` environment variable

**Tools:**
- `search`: Search the web

**Example Usage:**
```bash
# Set your Brave API key
export BRAVE_API_KEY=your_key

# Search the web
kutti agent --prompt "Search for the latest news about AI"
```

## Adding Custom MCP Servers

### From npm

Many MCP servers are available on npm:

```bash
# Add any npm-based MCP server
kutti mcp add server-name --command npx --args -y @modelcontextprotocol/server-name
```

### From a Local Script

You can use any script that implements MCP:

```bash
# Python script
kutti mcp add my-python-server --command python3 --args /path/to/server.py

# Node.js script
kutti mcp add my-node-server --command node --args /path/to/server.js

# Binary
kutti mcp add my-binary-server --command /path/to/server
```

### From GitHub

```bash
# Clone and run from GitHub
kutti mcp add my-github-server --command python3 --args /path/to/cloned/repo/server.py
```

## Writing Your Own MCP Server

### Python Example

Here's a simple MCP server in Python:

```python
# my_server.py
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
import asyncio

app = Server("my-kutti-mcp")

@app.list_tools()
async def list_tools():
    return [
        Tool(
            name="my_tool",
            description="Does something useful",
            inputSchema={
                "type": "object",
                "properties": {
                    "input": {"type": "string"}
                },
                "required": ["input"]
            }
        ),
        Tool(
            name="get_time",
            description="Get the current time",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "my_tool":
        result = f"Processed: {arguments['input']}"
        return [TextContent(type="text", text=result)]
    elif name == "get_time":
        from datetime import datetime
        return [TextContent(type="text", text=datetime.now().isoformat())]
    else:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]

async def main():
    async with stdio_server() as streams:
        await app.run(*streams, app.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())
```

### Node.js Example

```javascript
// my-server.js
import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { CallToolRequestSchema, ListToolsRequestSchema } from '@modelcontextprotocol/sdk/types.js';

const server = new Server(
  {
    name: 'my-kutti-mcp',
    version: '1.0.0',
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: 'my_tool',
        description: 'Does something useful',
        inputSchema: {
          type: 'object',
          properties: {
            input: { type: 'string' },
          },
          required: ['input'],
        },
      },
    ],
  };
});

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  if (request.params.name === 'my_tool') {
    return {
      content: [
        {
          type: 'text',
          text: `Processed: ${request.params.arguments.input}`,
        },
      ],
    };
  }
});

const transport = new StdioServerTransport();
server.connect(transport);
```

## MCP Server Configuration

MCP servers are configured in `~/.kutti/mcp.json`:

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/home/kutti"],
      "env": {},
      "transport": "stdio",
      "autoStart": true
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_TOKEN}"
      },
      "transport": "stdio",
      "autoStart": false
    },
    "my-server": {
      "command": "python3",
      "args": ["/path/to/my_server.py"],
      "env": {},
      "transport": "stdio",
      "autoStart": true
    }
  }
}
```

### Configuration Options:

| Option | Type | Required | Default | Description |
|--------|------|----------|---------|-------------|
| `command` | string | Yes | - | Command to run the server |
| `args` | string[] | No | [] | Arguments for the command |
| `env` | object | No | {} | Environment variables |
| `transport` | string | No | "stdio" | Transport type (stdio/sse) |
| `autoStart` | boolean | No | false | Start server automatically |

## MCP Commands

| Command | Description |
|---------|-------------|
| `kutti mcp list` | List all configured MCP servers |
| `kutti mcp add <name>` | Add a new MCP server |
| `kutti mcp remove <name>` | Remove an MCP server |
| `kutti mcp start <name>` | Start an MCP server |
| `kutti mcp stop <name>` | Stop an MCP server |
| `kutti mcp ping <name>` | Test connection to an MCP server |
| `kutti mcp tools <name>` | List tools from an MCP server |
| `kutti mcp resources <name>` | List resources from an MCP server |
| `kutti mcp install <package>` | Install a community MCP server from npm |

## Using MCP in Agent Mode

Once MCP servers are configured, Kutti's agent can automatically use their tools:

```bash
# With filesystem server
kutti agent --prompt "Read the package.json file and tell me the version"

# With GitHub server
kutti agent --prompt "List all open issues in my repo"

# With multiple servers
kutti agent --prompt "Search the web for AI news and save results to a file"
```

The agent will:
1. Detect which tools are available
2. Decide which tools to use
3. Call the tools automatically
4. Incorporate the results into its response

## MCP in Plugins

Plugins can also interact with MCP servers:

```javascript
// In a plugin's hooks
hooks: {
  beforeAgentLoop: async (context) => {
    // Access MCP clients
    const filesystem = context.mcpClients['filesystem'];
    if (filesystem) {
      const files = await filesystem.listResources({ uri: 'file:///home/kutti' });
      console.log('Files:', files);
    }
  }
}
```

## MCP Server Discovery

Kutti can discover MCP servers from:

1. **Configuration File**: `~/.kutti/mcp.json`
2. **npm Packages**: Official MCP servers on npm
3. **Local Files**: Custom servers in specific directories
4. **Environment Variables**: Server configurations from env vars

### Discovery Example:

```bash
# Discover and add all official MCP servers
kutti mcp install @modelcontextprotocol/server-filesystem
kutti mcp install @modelcontextprotocol/server-github
kutti mcp install @modelcontextprotocol/server-postgres
```

## MCP Security

### Authentication

MCP servers often require authentication. Kutti handles this through:

1. **Environment Variables**: Set in the MCP server configuration
2. **Kutti Auth**: Use Kutti's built-in auth system
3. **Plugin Auth**: Plugins can provide custom auth

### Example: Secure MCP Server

```bash
# Add a server with authentication
kutti mcp add github --command npx --args -y @modelcontextprotocol/server-github

# Set the auth token
kutti config set mcp.env.GITHUB_PERSONAL_ACCESS_TOKEN your_token
```

### Sandboxing

MCP servers run in isolated processes. Kutti provides:

- **Process Isolation**: Each server runs in its own process
- **Timeouts**: Prevent hanging servers
- **Resource Limits**: Limit CPU and memory usage
- **Permission Control**: Control what servers can access

## MCP Best Practices

### For Users:

1. **Start with Built-in Servers**: Use the official MCP servers first
2. **Add Gradually**: Don't add too many servers at once
3. **Monitor Performance**: Some servers may be slow
4. **Check Authentication**: Ensure servers have proper auth
5. **Update Regularly**: Keep servers updated

### For Server Developers:

1. **Use stdio Transport**: Most compatible with Kutti
2. **Handle Errors Gracefully**: Provide clear error messages
3. **Document Tools**: Include clear descriptions
4. **Validate Input**: Sanitize tool inputs
5. **Limit Output**: Keep responses concise
6. **Implement Health Checks**: Allow Kutti to verify server status

## MCP Server Examples

### 1. Custom File Server

```python
# file_server.py
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
import os

app = Server("custom-file-server")

@app.list_tools()
async def list_tools():
    return [
        Tool(
            name="read_file",
            description="Read a file from a specific directory",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {"type": "string"}
                },
                "required": ["path"]
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "read_file":
        try:
            with open(arguments['path'], 'r') as f:
                content = f.read()
            return [TextContent(type="text", text=content)]
        except Exception as e:
            return [TextContent(type="text", text=f"Error: {str(e)}")]

async def main():
    async with stdio_server() as streams:
        await app.run(*streams, app.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())
```

### 2. Web API Server

```python
# api_server.py
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
import httpx

app = Server("api-server")

@app.list_tools()
async def list_tools():
    return [
        Tool(
            name="fetch_url",
            description="Fetch content from a URL",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {"type": "string"}
                },
                "required": ["url"]
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "fetch_url":
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(arguments['url'])
                return [TextContent(type="text", text=response.text)]
        except Exception as e:
            return [TextContent(type="text", text=f"Error: {str(e)}")]

async def main():
    async with stdio_server() as streams:
        await app.run(*streams, app.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())
```

## MCP Resources

In addition to tools, MCP servers can expose resources that Kutti can read:

```python
@app.list_resources()
async def list_resources():
    return {
        "resources": [
            {
                "uri": "file:///data/file1.txt",
                "name": "File 1",
                "description": "A sample file",
                "mimeType": "text/plain"
            }
        ]
    }

@app.read_resource()
async def read_resource(uri: str):
    if uri == "file:///data/file1.txt":
        return [TextContent(type="text", text="File content...")]
```

Kutti can access resources using MCP tools or directly in agent mode:

```bash
kutti agent --prompt "Read the resource at file:///data/file1.txt"
```

## MCP in the Agent Loop

When the agent is running, it can use MCP tools just like built-in tools:

```
User: "What's in the README.md file?"

Agent THINK:
- User wants to read README.md
- I can use the filesystem MCP server's read_resource tool
- I'll call read_resource with uri="file:///README.md"

Agent ACT:
- Calls read_resource tool

Agent OBSERVE:
- Receives file content

Agent EVALUATE:
- Task is complete, return the content to user
```

## Troubleshooting MCP

### Server Won't Start:

1. Check the command is correct
2. Verify the server binary exists
3. Check for missing dependencies
4. Look at error logs

```bash
# Check server logs
kutti mcp start my-server --debug

# View Kutti logs
tail -f ~/.kutti/kutti.log
```

### Connection Issues:

1. Verify the server is running
2. Check transport type (stdio vs sse)
3. Test with a simple server first
4. Check for timeouts

### Tool Not Found:

1. Verify the server is started
2. Check the tool name is correct
3. List available tools

```bash
kutti mcp tools my-server
```

### Authentication Errors:

1. Verify environment variables are set
2. Check token permissions
3. Test authentication manually

## MCP Performance Tips

1. **Start Only Needed Servers**: Don't start all servers at once
2. **Use autoStart Wisely**: Only auto-start frequently used servers
3. **Set Timeouts**: Configure appropriate timeouts
4. **Cache Results**: Cache frequent tool calls
5. **Limit Concurrent Calls**: Don't overload servers

## MCP Configuration Tips

### Environment Variables:

```bash
# Set in shell
export GITHUB_TOKEN=your_token

# Or set in MCP config
kutti mcp add github --env GITHUB_TOKEN=your_token
```

### Multiple Servers:

```json
{
  "mcpServers": {
    "github-prod": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {"GITHUB_TOKEN": "${PROD_TOKEN}"}
    },
    "github-test": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {"GITHUB_TOKEN": "${TEST_TOKEN}"}
    }
  }
}
```

### Server Groups:

Organize servers by purpose:

```json
{
  "mcpServers": {
    "dev-github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {"GITHUB_TOKEN": "${DEV_TOKEN}"},
      "group": "development"
    },
    "dev-filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/dev"],
      "group": "development"
    }
  }
}
```

## Future MCP Features

Planned enhancements for MCP in Kutti:

1. **Server Discovery**: Automatic discovery of MCP servers on the network
2. **Server Marketplace**: Browse and install MCP servers from a registry
3. **Server Health Checks**: Automatic monitoring of server status
4. **Server Updates**: Automatic updates for installed servers
5. **Resource Caching**: Cache frequently accessed resources
6. **Tool Chaining**: Chain multiple MCP tool calls together
7. **Parallel Execution**: Execute multiple MCP tools in parallel

## Support

For questions or issues with MCP:

1. Check the [MCP Specification](https://github.com/modelcontextprotocol/specification)
2. Look at the [Kutti GitHub repository](https://github.com/wsochi4-os/kay)
3. Check the [MCP Server Registry](https://github.com/modelcontextprotocol/servers)
4. Open an issue with your question
5. Join the MCP community discussions

## References

- [MCP Specification](https://github.com/modelcontextprotocol/specification)
- [MCP SDK](https://github.com/modelcontextprotocol/sdk)
- [MCP Servers](https://github.com/modelcontextprotocol/servers)
- [Kutti MCP Implementation](https://github.com/wsochi4-os/kay/tree/main/packages/cli/src/mcp)

## Changelog

### v1.0.0

- Initial MCP support in Kutti
- stdio transport support
- Built-in filesystem server
- MCP server management commands
- MCP tool integration in agent loop
- Plugin access to MCP clients
