#!/usr/bin/env node

import { Command } from 'commander';
import chalk from 'chalk';
import { KUTTI_VERSION } from './utils/constants.js';
import { logger } from './utils/logger.js';
import { configManager } from './utils/config.js';
import { authManager } from './auth/manager.js';
import { pluginLoader } from './plugins/loader.js';
import { skillsManager } from './skills/manager.js';
import { mcpHost, initializeMCP } from './mcp/host.js';
import { createAgentLoop } from './agent/loop.js';
import { getProvider } from './providers/index.js';
import { initializePlugins } from './plugins/loader.js';
import { initializeSkills } from './skills/manager.js';

// Import commands
import { createAuthCommands } from './commands/auth.js';
import { createConfigCommands } from './commands/config.js';
import { createMcpCommands } from './commands/mcp.js';
import { createPluginCommands } from './commands/plugin.js';
import { createSkillsCommands } from './commands/skills.js';
import { createAgentCommands } from './commands/agent.js';
import { createChatCommands } from './commands/chat.js';

/**
 * Main CLI entry point
 */
async function main() {
  const program = new Command();

  // Set up global options
  program
    .name('kutti')
    .description('Kutti - Your Personal AI CLI Agent')
    .version(KUTTI_VERSION)
    .option('-v, --verbose', 'Enable verbose logging')
    .option('-d, --debug', 'Enable debug mode')
    .option('--provider <provider>', 'Set the AI provider for this command')
    .option('--model <model>', 'Set the model for this command')
    .option('--skill <skills...>', 'Enable specific skills for this command')
    .option('--no-skills', 'Disable all skills for this command')
    .option('--yes, -y', 'Auto-confirm all actions')
    .hook('preAction', (thisCommand) => {
      // Set up logging level
      if (thisCommand.opts().verbose) {
        logger.setLevel('info');
      }
      if (thisCommand.opts().debug) {
        logger.setLevel('debug');
      }

      // Set provider if specified
      if (thisCommand.opts().provider) {
        configManager.setProvider(thisCommand.opts().provider);
      }

      // Set model if specified
      if (thisCommand.opts().model) {
        configManager.setModel(thisCommand.opts().model);
      }

      // Set auto-confirm if specified
      if (thisCommand.opts().yes) {
        configManager.set('agent.autoConfirm', true);
        configManager.set('agent.autoConfirmShell', true);
      }
    });

  // Add commands
  createAuthCommands(program);
  createConfigCommands(program);
  createMcpCommands(program);
  createPluginCommands(program);
  createSkillsCommands(program);
  createAgentCommands(program);
  createChatCommands(program);

  // Default action - treat as a prompt
  program
    .arguments('[prompt...]')
    .action(async (prompt: string[]) => {
      if (prompt.length === 0) {
        // No prompt, show help
        program.help();
        return;
      }

      const promptText = prompt.join(' ');

      // Initialize systems
      await initializePlugins();
      await initializeSkills();
      await initializeMCP();

      // Check authentication
      if (!authManager.isAuthenticated()) {
        console.log(chalk.yellow('Warning: Not authenticated. Some providers may not work.'));
        console.log(chalk.yellow('Run: kutti auth login'));
      }

      // Create agent loop
      const agent = createAgentLoop();

      // Enable specified skills
      if (program.opts().skill) {
        for (const skillName of program.opts().skill) {
          skillsManager.enable(skillName);
        }
      }

      // Disable skills if requested
      if (program.opts().noSkills) {
        skillsManager.disableAll();
      }

      // Run the prompt
      try {
        console.log(chalk.cyan('\nKutti is thinking...\n'));
        
        const response = await agent.runOnce(promptText);
        console.log(chalk.green('\n' + response + '\n'));
      } catch (error: any) {
        console.error(chalk.red(`\nError: ${error.message}\n`));
        if (program.opts().debug) {
          console.error(error.stack);
        }
      }
    });

  // Parse arguments
  try {
    await program.parseAsync(process.argv);
  } catch (error: any) {
    console.error(chalk.red(`\nError: ${error.message}\n`));
    if (program.opts().debug) {
      console.error(error.stack);
    }
    process.exit(1);
  }

  // If no arguments, show help
  if (process.argv.length === 2) {
    program.help();
  }
}

// Run the CLI
main().catch(error => {
  console.error(chalk.red(`\nFatal error: ${error}\n`));
  process.exit(1);
});

export { main };
