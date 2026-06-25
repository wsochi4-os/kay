import { Command } from 'commander';
import chalk from 'chalk';
import { pluginLoader, initializePlugins } from '../plugins/loader.js';
import { logger } from '../utils/logger.js';

/**
 * Create plugin commands
 */
export function createPluginCommands(program: Command) {
  const plugin = new Command('plugin');
  plugin.description('Manage Kutti plugins');

  // kutti plugin list
  plugin
    .command('list')
    .description('List all installed plugins')
    .action(async () => {
      try {
        await initializePlugins();
        const plugins = pluginLoader.getAll();
        
        console.log(chalk.cyan('\nInstalled Plugins:\n'));
        
        if (plugins.length === 0) {
          console.log(chalk.gray('No plugins installed'));
          console.log('');
          console.log(chalk.yellow('Install plugins with: kutti plugin install <name>'));
          return;
        }

        for (const p of plugins) {
          const loaded = pluginLoader.isLoaded(p.name) ? chalk.green('✓') : chalk.gray('✗');
          console.log(`- ${loaded} ${p.name}`);
          if (p.commands) {
            console.log(`  Commands: ${Object.keys(p.commands).join(', ')}`);
          }
          if (p.tools) {
            console.log(`  Tools: ${p.tools.map(t => t.name).join(', ')}`);
          }
        }
        console.log('');
      } catch (error: any) {
        console.error(chalk.red(`Error: ${error.message}`));
      }
    });

  // kutti plugin install
  plugin
    .command('install <name>')
    .description('Install a plugin')
    .option('--local <path>', 'Install from a local path')
    .option('--github <repo>', 'Install from GitHub')
    .action(async (name: string, options: { local?: string; github?: string }) => {
      try {
        if (options.local) {
          // Install from local path
          console.log(chalk.yellow(`Installing plugin from local path: ${options.local}`));
          // This would copy the plugin to the plugins directory
          console.log(chalk.yellow('Local plugin installation not yet implemented'));
        } else if (options.github) {
          // Install from GitHub
          console.log(chalk.yellow(`Installing plugin from GitHub: ${options.github}`));
          console.log(chalk.yellow('GitHub plugin installation not yet implemented'));
        } else {
          // Install from npm
          const success = await pluginLoader.install(name);
          if (success) {
            console.log(chalk.green(`Plugin '${name}' installed successfully`));
          } else {
            console.log(chalk.red(`Failed to install plugin '${name}'`));
          }
        }
      } catch (error: any) {
        console.error(chalk.red(`Error: ${error.message}`));
      }
    });

  // kutti plugin enable
  plugin
    .command('enable <name>')
    .description('Enable a plugin')
    .action(async (name: string) => {
      try {
        await initializePlugins();
        const plugin = pluginLoader.get(name);
        
        if (!plugin) {
          console.log(chalk.red(`Plugin '${name}' not found`));
          return;
        }

        if (pluginLoader.isLoaded(name)) {
          console.log(chalk.yellow(`Plugin '${name}' is already loaded`));
          return;
        }

        await pluginLoader.load(name);
        console.log(chalk.green(`Plugin '${name}' enabled`));
      } catch (error: any) {
        console.error(chalk.red(`Error: ${error.message}`));
      }
    });

  // kutti plugin disable
  plugin
    .command('disable <name>')
    .description('Disable a plugin')
    .action((name: string) => {
      try {
        const success = pluginLoader.unload(name);
        if (success) {
          console.log(chalk.green(`Plugin '${name}' disabled`));
        } else {
          console.log(chalk.red(`Plugin '${name}' not found or already disabled`));
        }
      } catch (error: any) {
        console.error(chalk.red(`Error: ${error.message}`));
      }
    });

  // kutti plugin remove
  plugin
    .command('remove <name>')
    .description('Remove a plugin')
    .action(async (name: string) => {
      try {
        const success = await pluginLoader.remove(name);
        if (success) {
          console.log(chalk.green(`Plugin '${name}' removed`));
        } else {
          console.log(chalk.red(`Failed to remove plugin '${name}'`));
        }
      } catch (error: any) {
        console.error(chalk.red(`Error: ${error.message}`));
      }
    });

  // kutti plugin info
  plugin
    .command('info <name>')
    .description('Show information about a plugin')
    .action(async (name: string) => {
      try {
        await initializePlugins();
        const plugin = pluginLoader.get(name);
        
        if (!plugin) {
          console.log(chalk.red(`Plugin '${name}' not found`));
          return;
        }

        console.log(chalk.cyan(`\nPlugin: ${name}\n`));
        console.log(`Name: ${plugin.name}`);
        
        if (plugin.commands) {
          console.log(`Commands: ${Object.keys(plugin.commands).join(', ')}`);
        }
        
        if (plugin.tools) {
          console.log(`Tools: ${plugin.tools.map(t => t.name).join(', ')}`);
        }
        
        if (plugin.hooks) {
          console.log(`Hooks: ${Object.keys(plugin.hooks).join(', ')}`);
        }
        
        console.log('');
      } catch (error: any) {
        console.error(chalk.red(`Error: ${error.message}`));
      }
    });

  // kutti plugin update
  plugin
    .command('update')
    .description('Update all plugins')
    .action(async () => {
      try {
        console.log(chalk.yellow('Updating all plugins...'));
        console.log(chalk.yellow('Plugin update not yet implemented'));
        console.log(chalk.yellow('For now, you can manually update plugins by reinstalling them'));
      } catch (error: any) {
        console.error(chalk.red(`Error: ${error.message}`));
      }
    });

  program.addCommand(plugin);
}
