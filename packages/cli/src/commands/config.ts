import { Command } from 'commander';
import chalk from 'chalk';
import { configManager } from '../utils/config.js';
import { logger } from '../utils/logger.js';

/**
 * Create config commands
 */
export function createConfigCommands(program: Command) {
  const config = new Command('config');
  config.description('Manage Kutti configuration');

  // kutti config (no args - show config)
  config
    .action(() => {
      try {
        const config = configManager.getConfig();
        console.log(chalk.cyan('\nKutti Configuration:\n'));
        console.log(JSON.stringify(config, null, 2));
        console.log('');
      } catch (error: any) {
        console.error(chalk.red(`Error: ${error.message}`));
      }
    });

  // kutti config set
  config
    .command('set <key> <value>')
    .description('Set a configuration value')
    .action((key: string, value: string) => {
      try {
        // Try to parse value as JSON
        let parsedValue: any = value;
        try {
          parsedValue = JSON.parse(value);
        } catch (e) {
          // Not JSON, use as string
        }

        // Handle special cases
        if (key === 'provider') {
          configManager.setProvider(value);
          console.log(chalk.green(`Provider set to: ${value}`));
          return;
        }

        if (key === 'model') {
          configManager.setModel(value);
          console.log(chalk.green(`Model set to: ${value}`));
          return;
        }

        configManager.set(key, parsedValue);
        console.log(chalk.green(`Configuration set: ${key} = ${JSON.stringify(parsedValue)}`));
      } catch (error: any) {
        console.error(chalk.red(`Error: ${error.message}`));
      }
    });

  // kutti config get
  config
    .command('get <key>')
    .description('Get a configuration value')
    .action((key: string) => {
      try {
        const value = configManager.get(key);
        if (value !== undefined) {
          console.log(JSON.stringify(value, null, 2));
        } else {
          console.log(chalk.gray(`Configuration key '${key}' not found`));
        }
      } catch (error: any) {
        console.error(chalk.red(`Error: ${error.message}`));
      }
    });

  // kutti config list
  config
    .command('list')
    .description('List all configuration values')
    .action(() => {
      try {
        const config = configManager.getConfig();
        console.log(chalk.cyan('\nConfiguration Values:\n'));
        
        for (const [key, value] of Object.entries(config)) {
          console.log(`${chalk.yellow(key)}: ${JSON.stringify(value)}`);
        }
        console.log('');
      } catch (error: any) {
        console.error(chalk.red(`Error: ${error.message}`));
      }
    });

  // kutti config reset
  config
    .command('reset')
    .description('Reset configuration to defaults')
    .option('-f, --force', 'Force reset without confirmation')
    .action((options: { force: boolean }) => {
      try {
        if (!options.force) {
          console.log(chalk.yellow('This will reset all configuration to defaults.'));
          console.log(chalk.yellow('Run with --force to confirm.'));
          return;
        }

        configManager.reset();
        console.log(chalk.green('Configuration reset to defaults'));
      } catch (error: any) {
        console.error(chalk.red(`Error: ${error.message}`));
      }
    });

  // kutti config edit
  config
    .command('edit')
    .description('Open configuration file in editor')
    .action(() => {
      try {
        // This would open the config file in the user's editor
        // For now, just show the path
        console.log(chalk.cyan('Configuration file location:'));
        console.log(process.env.KUTTI_CONFIG_DIR || '~/.kutti/config.json');
        console.log('');
        console.log(chalk.yellow('Edit this file manually or use `kutti config set` to modify values.'));
      } catch (error: any) {
        console.error(chalk.red(`Error: ${error.message}`));
      }
    });

  program.addCommand(config);
}
