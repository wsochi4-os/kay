import { Command } from 'commander';
import chalk from 'chalk';
import inquirer from 'inquirer';
import { authManager } from '../auth/manager.js';
import { PROVIDER_LIST } from '../utils/constants.js';
import { logger } from '../utils/logger.js';

/**
 * Create auth commands
 */
export function createAuthCommands(program: Command) {
  const auth = new Command('auth');
  auth.description('Manage authentication with AI providers');

  // kutti auth login
  auth
    .command('login')
    .description('Authenticate with an AI provider')
    .option('--provider <provider>', 'Provider to authenticate with')
    .option('--key <key>', 'API key (for providers that use API keys)')
    .action(async (options) => {
      try {
        if (options.provider) {
          // Specific provider
          const result = await authManager.login(options.provider, options.key);
          if (result.success) {
            console.log(chalk.green(result.message));
          } else {
            console.log(chalk.yellow(result.message));
          }
        } else {
          // Interactive provider selection
          const { provider } = await inquirer.prompt([
            {
              type: 'list',
              name: 'provider',
              message: 'Select a provider to authenticate with:',
              choices: PROVIDER_LIST.map(p => ({
                name: `${p.name} ${p.free ? '(Free)' : '(Paid)'}`,
                value: p.id,
              })),
            },
          ]);

          const selectedProvider = PROVIDER_LIST.find(p => p.id === provider);
          if (!selectedProvider) {
            console.log(chalk.red('Invalid provider selected'));
            return;
          }

          // For Ollama, no key needed
          if (provider === 'ollama') {
            const result = await authManager.login(provider);
            console.log(chalk.green(result.message));
            return;
          }

          // Prompt for API key
          const { apiKey } = await inquirer.prompt([
            {
              type: 'password',
              name: 'apiKey',
              message: `Enter your ${selectedProvider.name} API key:`,
              validate: (input: string) => input.length > 0 || 'API key is required',
            },
          ]);

          const result = await authManager.login(provider, apiKey);
          if (result.success) {
            console.log(chalk.green(result.message));
          } else {
            console.log(chalk.yellow(result.message));
          }
        }
      } catch (error: any) {
        console.error(chalk.red(`Error: ${error.message}`));
        if (options.debug) {
          console.error(error.stack);
        }
      }
    });

  // kutti auth list
  auth
    .command('list')
    .description('List all authenticated providers')
    .action(() => {
      try {
        const { providers } = authManager.list();
        
        console.log(chalk.cyan('\nAuthenticated Providers:\n'));
        
        const authenticated = providers.filter(p => p.authenticated);
        const notAuthenticated = providers.filter(p => !p.authenticated);

        if (authenticated.length > 0) {
          console.log(chalk.green('✓ Authenticated:'));
          for (const provider of authenticated) {
            const active = provider.active ? chalk.yellow(' (active)') : '';
            console.log(`  - ${provider.name}${active}`);
          }
          console.log('');
        }

        if (notAuthenticated.length > 0) {
          console.log(chalk.gray('✗ Not Authenticated:'));
          for (const provider of notAuthenticated) {
            console.log(`  - ${provider.name}`);
          }
          console.log('');
        }

        console.log(chalk.gray(`Total: ${providers.length} providers (${authenticated.length} authenticated)`));
      } catch (error: any) {
        console.error(chalk.red(`Error: ${error.message}`));
      }
    });

  // kutti auth use
  auth
    .command('use <provider>')
    .description('Switch to a specific provider')
    .action((provider: string) => {
      try {
        const result = authManager.use(provider);
        if (result.success) {
          console.log(chalk.green(result.message));
        } else {
          console.log(chalk.red(result.message));
        }
      } catch (error: any) {
        console.error(chalk.red(`Error: ${error.message}`));
      }
    });

  // kutti auth status
  auth
    .command('status')
    .description('Show current authentication status')
    .action(() => {
      try {
        const status = authManager.status();
        
        console.log(chalk.cyan('\nAuthentication Status:\n'));
        
        if (status.activeProvider) {
          console.log(`Active Provider: ${chalk.green(status.activeProvider)}`);
        } else {
          console.log(`Active Provider: ${chalk.gray('None')}`);
        }

        console.log(`Authenticated: ${status.authenticated ? chalk.green('Yes') : chalk.red('No')}`);
        
        if (status.providers.length > 0) {
          console.log(`Authenticated Providers: ${status.providers.join(', ')}`);
        } else {
          console.log(`Authenticated Providers: ${chalk.gray('None')}`);
        }
        
        console.log('');
      } catch (error: any) {
        console.error(chalk.red(`Error: ${error.message}`));
      }
    });

  // kutti auth logout
  auth
    .command('logout [provider]')
    .description('Logout from a provider or all providers')
    .option('--all', 'Logout from all providers')
    .action((provider: string, options: { all: boolean }) => {
      try {
        if (options.all) {
          const result = authManager.logout('all');
          console.log(chalk.green(result.message));
        } else if (provider) {
          const result = authManager.logout(provider);
          if (result.success) {
            console.log(chalk.green(result.message));
          } else {
            console.log(chalk.red(result.message));
          }
        } else {
          console.log(chalk.yellow('Please specify a provider or use --all'));
          console.log(chalk.yellow('Usage: kutti auth logout <provider>'));
          console.log(chalk.yellow('       kutti auth logout --all'));
        }
      } catch (error: any) {
        console.error(chalk.red(`Error: ${error.message}`));
      }
    });

  // kutti auth refresh
  auth
    .command('refresh <provider>')
    .description('Refresh authentication for a provider')
    .action(async (provider: string) => {
      try {
        const result = await authManager.refresh(provider);
        if (result.success) {
          console.log(chalk.green(result.message));
        } else {
          console.log(chalk.red(result.message));
        }
      } catch (error: any) {
        console.error(chalk.red(`Error: ${error.message}`));
      }
    });

  program.addCommand(auth);
}
