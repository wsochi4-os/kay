import { Command } from 'commander';
import chalk from 'chalk';
import { createAgentLoop } from '../agent/loop.js';
import { initializePlugins } from '../plugins/loader.js';
import { initializeSkills, skillsManager } from '../skills/manager.js';
import { initializeMCP } from '../mcp/host.js';
import { authManager } from '../auth/manager.js';
import { configManager } from '../utils/config.js';
import { logger } from '../utils/logger.js';

/**
 * Create chat commands
 */
export function createChatCommands(program: Command) {
  // kutti chat
  program
    .command('chat')
    .description('Start an interactive chat session')
    .option('--provider <provider>', 'Provider to use for this session')
    .option('--model <model>', 'Model to use for this session')
    .option('--skill <skills...>', 'Skills to enable for this session')
    .option('--no-skills', 'Disable all skills for this session')
    .action(async (options) => {
      try {
        // Initialize systems
        await initializePlugins();
        await initializeSkills();
        await initializeMCP();

        // Set provider if specified
        if (options.provider) {
          configManager.setProvider(options.provider);
        }

        // Set model if specified
        if (options.model) {
          configManager.setModel(options.model);
        }

        // Check authentication
        if (!authManager.isAuthenticated()) {
          console.log(chalk.yellow('Warning: Not authenticated. Some providers may not work.'));
          console.log(chalk.yellow('Run: kutti auth login\n'));
        }

        // Enable specified skills
        if (options.skill) {
          for (const skillName of options.skill) {
            await initializeSkills();
            const skill = skillsManager.get(skillName);
            if (skill) {
              skillsManager.enable(skillName);
            }
          }
        }

        // Disable skills if requested
        if (options.noSkills) {
          skillsManager.disableAll();
        }

        // Start interactive chat
        console.log(chalk.cyan('\nKutti Chat - Interactive Mode'));
        console.log(chalk.cyan('Type your message and press Enter. Type "exit" or "quit" to end the session.\n'));

        const agentLoop = createAgentLoop();
        
        // Show active configuration
        const config = configManager.getConfig();
        console.log(chalk.gray(`Provider: ${config.provider}, Model: ${config.model}`));
        const activeSkills = skillsManager.getActiveSkillNames();
        if (activeSkills.length > 0) {
          console.log(chalk.gray(`Active Skills: ${activeSkills.join(', ')}`));
        }
        console.log('');

        const readline = require('readline');
        const rl = readline.createInterface({
          input: process.stdin,
          output: process.stdout,
          prompt: chalk.cyan('kutti> '),
        });

        // Keep conversation history
        const history: { role: string; content: string }[] = [];

        rl.prompt();

        rl.on('line', async (line: string) => {
          const trimmed = line.trim();

          if (trimmed === 'exit' || trimmed === 'quit' || trimmed === 'q') {
            rl.close();
            return;
          }

          if (trimmed) {
            try {
              // Add user message to history
              history.push({ role: 'user', content: trimmed });
              agentLoop.addMessage({ role: 'user', content: trimmed });

              console.log(chalk.cyan('\nThinking...\n'));
              
              const response = await agentLoop.runOnce(trimmed);
              
              // Add assistant response to history
              history.push({ role: 'assistant', content: response });
              agentLoop.addMessage({ role: 'assistant', content: response });

              console.log(chalk.green('\n' + response + '\n'));
            } catch (error: any) {
              console.error(chalk.red(`\nError: ${error.message}\n`));
            }
          }

          rl.prompt();
        }).on('close', () => {
          console.log(chalk.cyan('\nChat session ended. Goodbye!\n'));
          process.exit(0);
        });
      } catch (error: any) {
        console.error(chalk.red(`Error: ${error.message}`));
        if (options.debug) {
          console.error(error.stack);
        }
      }
    });

  // kutti chat --one-shot
  program
    .command('chat:once')
    .description('Run a one-shot chat (no conversation history)')
    .arguments('<prompt>')
    .option('--provider <provider>', 'Provider to use')
    .option('--model <model>', 'Model to use')
    .action(async (prompt: string, options: { provider?: string; model?: string }) => {
      try {
        // Initialize systems
        await initializePlugins();
        await initializeSkills();
        await initializeMCP();

        // Set provider if specified
        if (options.provider) {
          configManager.setProvider(options.provider);
        }

        // Set model if specified
        if (options.model) {
          configManager.setModel(options.model);
        }

        // Check authentication
        if (!authManager.isAuthenticated()) {
          console.log(chalk.yellow('Warning: Not authenticated. Some providers may not work.'));
        }

        const agentLoop = createAgentLoop();
        console.log(chalk.cyan('\nThinking...\n'));
        
        const response = await agentLoop.runOnce(prompt);
        console.log(chalk.green('\n' + response + '\n'));
      } catch (error: any) {
        console.error(chalk.red(`Error: ${error.message}`));
      }
    });
}

// Export for use in other modules
export { createChatCommands };
