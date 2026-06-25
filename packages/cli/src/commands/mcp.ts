import { Command } from 'commander';
import chalk from 'chalk';
import { mcpHost, initializeMCP } from '../mcp/host.js';
import { logger } from '../utils/logger.js';

/**
 * Create MCP commands
 */
export function createMcpCommands(program: Command) {
  const mcp = new Command('mcp');
  mcp.description('Manage Model Context Protocol (MCP) servers');

  // kutti mcp list
  mcp
    .command('list')
    .description('List all configured MCP servers')
    .action(async () => {
      try {
        await initializeMCP();
        const servers = mcpHost.listServers();
        
        console.log(chalk.cyan('\nMCP Servers:\n'));
        
        if (servers.length === 0) {
          console.log(chalk.gray('No MCP servers configured'));
          console.log('');
          console.log(chalk.yellow('Add a server with: kutti mcp add <name>'));
          return;
        }

        for (const serverName of servers) {
          const server = mcpHost.getServer(serverName);
          if (server) {
            console.log(`- ${chalk.green(serverName)}`);
          }
        }
        console.log('');
      } catch (error: any) {
        console.error(chalk.red(`Error: ${error.message}`));
      }
    });

  // kutti mcp add
  mcp
    .command('add <name>')
    .description('Add a new MCP server')
    .option('--command <command>', 'Command to run the server')
    .option('--args <args...>', 'Arguments for the command')
    .option('--env <env...>', 'Environment variables')
    .option('--transport <transport>', 'Transport type (stdio or sse)', 'stdio')
    .option('--auto-start', 'Auto-start the server', true)
    .action((name: string, options: any) => {
      try {
        const config = {
          name,
          command: options.command || 'npx',
          args: options.args || [],
          env: options.env ? options.env.reduce((acc: any, val: string) => {
            const [key, value] = val.split('=');
            acc[key] = value;
            return acc;
          }, {}) : {},
          transport: options.transport,
          autoStart: options.autoStart,
        };

        mcpHost.addServer(config);
        console.log(chalk.green(`MCP server '${name}' added`));
      } catch (error: any) {
        console.error(chalk.red(`Error: ${error.message}`));
      }
    });

  // kutti mcp remove
  mcp
    .command('remove <name>')
    .description('Remove an MCP server')
    .action((name: string) => {
      try {
        mcpHost.removeServer(name);
        console.log(chalk.green(`MCP server '${name}' removed`));
      } catch (error: any) {
        console.error(chalk.red(`Error: ${error.message}`));
      }
    });

  // kutti mcp start
  mcp
    .command('start <name>')
    .description('Start an MCP server')
    .action(async (name: string) => {
      try {
        await initializeMCP();
        const server = mcpHost.getServer(name);
        if (server) {
          await server.start();
          console.log(chalk.green(`MCP server '${name}' started`));
        } else {
          console.log(chalk.red(`MCP server '${name}' not found`));
        }
      } catch (error: any) {
        console.error(chalk.red(`Error: ${error.message}`));
      }
    });

  // kutti mcp stop
  mcp
    .command('stop <name>')
    .description('Stop an MCP server')
    .action(async (name: string) => {
      try {
        await initializeMCP();
        const server = mcpHost.getServer(name);
        if (server) {
          await server.stop();
          console.log(chalk.green(`MCP server '${name}' stopped`));
        } else {
          console.log(chalk.red(`MCP server '${name}' not found`));
        }
      } catch (error: any) {
        console.error(chalk.red(`Error: ${error.message}`));
      }
    });

  // kutti mcp tools
  mcp
    .command('tools <name>')
    .description('List tools from an MCP server')
    .action(async (name: string) => {
      try {
        await initializeMCP();
        const server = mcpHost.getServer(name);
        if (server) {
          const tools = await server.listTools();
          
          console.log(chalk.cyan(`\nTools from MCP server '${name}':\n`));
          
          if (tools.length === 0) {
            console.log(chalk.gray('No tools available'));
            return;
          }

          for (const tool of tools) {
            console.log(`- ${chalk.yellow(tool.name)}: ${tool.description}`);
          }
          console.log('');
        } else {
          console.log(chalk.red(`MCP server '${name}' not found`));
        }
      } catch (error: any) {
        console.error(chalk.red(`Error: ${error.message}`));
      }
    });

  // kutti mcp resources
  mcp
    .command('resources <name>')
    .description('List resources from an MCP server')
    .action(async (name: string) => {
      try {
        await initializeMCP();
        const server = mcpHost.getServer(name);
        if (server) {
          const resources = await server.listResources();
          
          console.log(chalk.cyan(`\nResources from MCP server '${name}':\n`));
          
          if (resources.length === 0) {
            console.log(chalk.gray('No resources available'));
            return;
          }

          for (const resource of resources) {
            console.log(`- ${chalk.yellow(resource.uri)}`);
          }
          console.log('');
        } else {
          console.log(chalk.red(`MCP server '${name}' not found`));
        }
      } catch (error: any) {
        console.error(chalk.red(`Error: ${error.message}`));
      }
    });

  // kutti mcp ping
  mcp
    .command('ping <name>')
    .description('Test connection to an MCP server')
    .action(async (name: string) => {
      try {
        await initializeMCP();
        const server = mcpHost.getServer(name);
        if (server) {
          const tools = await server.listTools();
          console.log(chalk.green(`MCP server '${name}' is responding (${tools.length} tools)`));
        } else {
          console.log(chalk.red(`MCP server '${name}' not found`));
        }
      } catch (error: any) {
        console.error(chalk.red(`Error: ${error.message}`));
      }
    });

  // kutti mcp install
  mcp
    .command('install <package>')
    .description('Install a community MCP server from npm')
    .action(async (packageName: string) => {
      try {
        console.log(chalk.yellow(`Installing MCP server package: ${packageName}`));
        console.log(chalk.yellow('This would install the package via npm and configure it.'));
        console.log(chalk.yellow('For now, you can manually add servers with: kutti mcp add <name> --command <command>'));
      } catch (error: any) {
        console.error(chalk.red(`Error: ${error.message}`));
      }
    });

  program.addCommand(mcp);
}
