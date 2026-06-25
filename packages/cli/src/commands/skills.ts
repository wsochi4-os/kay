import { Command } from 'commander';
import chalk from 'chalk';
import { skillsManager, initializeSkills } from '../skills/manager.js';
import { logger } from '../utils/logger.js';

/**
 * Create skills commands
 */
export function createSkillsCommands(program: Command) {
  const skills = new Command('skills');
  skills.description('Manage Kutti skills');

  // kutti skills list
  skills
    .command('list')
    .description('List all installed skills')
    .action(async () => {
      try {
        await initializeSkills();
        const allSkills = skillsManager.getAll();
        const activeSkills = skillsManager.getActiveSkillNames();
        
        console.log(chalk.cyan('\nInstalled Skills:\n'));
        
        if (allSkills.length === 0) {
          console.log(chalk.gray('No skills installed'));
          console.log('');
          console.log(chalk.yellow('Install skills with: kutti skills install <name>'));
          return;
        }

        for (const skill of allSkills) {
          const active = activeSkills.includes(skill.name) ? chalk.green('✓') : chalk.gray('✗');
          console.log(`- ${active} ${skill.name}: ${skill.description}`);
          if (skill.triggers) {
            console.log(`  Triggers: ${skill.triggers.join(', ')}`);
          }
          if (skill.priority) {
            console.log(`  Priority: ${skill.priority}`);
          }
        }
        console.log('');
      } catch (error: any) {
        console.error(chalk.red(`Error: ${error.message}`));
      }
    });

  // kutti skills install
  skills
    .command('install <name>')
    .description('Install a skill')
    .option('--local <path>', 'Install from a local path')
    .option('--github <repo>', 'Install from GitHub')
    .action(async (name: string, options: { local?: string; github?: string }) => {
      try {
        if (options.local) {
          // Install from local path
          console.log(chalk.yellow(`Installing skill from local path: ${options.local}`));
          console.log(chalk.yellow('Local skill installation not yet implemented'));
        } else if (options.github) {
          // Install from GitHub
          console.log(chalk.yellow(`Installing skill from GitHub: ${options.github}`));
          console.log(chalk.yellow('GitHub skill installation not yet implemented'));
        } else {
          // Install from registry
          console.log(chalk.yellow(`Installing skill: ${name}`));
          console.log(chalk.yellow('Skill installation from registry not yet implemented'));
          console.log(chalk.yellow('For now, you can create skills manually with: kutti skills create'));
        }
      } catch (error: any) {
        console.error(chalk.red(`Error: ${error.message}`));
      }
    });

  // kutti skills enable
  skills
    .command('enable <name>')
    .description('Enable a skill')
    .action(async (name: string) => {
      try {
        await initializeSkills();
        const skill = skillsManager.get(name);
        
        if (!skill) {
          console.log(chalk.red(`Skill '${name}' not found`));
          return;
        }

        if (skillsManager.isActive(name)) {
          console.log(chalk.yellow(`Skill '${name}' is already enabled`));
          return;
        }

        skillsManager.enable(name);
        console.log(chalk.green(`Skill '${name}' enabled`));
      } catch (error: any) {
        console.error(chalk.red(`Error: ${error.message}`));
      }
    });

  // kutti skills disable
  skills
    .command('disable <name>')
    .description('Disable a skill')
    .action((name: string) => {
      try {
        const success = skillsManager.disable(name);
        if (success) {
          console.log(chalk.green(`Skill '${name}' disabled`));
        } else {
          console.log(chalk.red(`Skill '${name}' not found or already disabled`));
        }
      } catch (error: any) {
        console.error(chalk.red(`Error: ${error.message}`));
      }
    });

  // kutti skills active
  skills
    .command('active')
    .description('Show active skills')
    .action(() => {
      try {
        const activeSkills = skillsManager.getActiveSkills();
        
        console.log(chalk.cyan('\nActive Skills:\n'));
        
        if (activeSkills.length === 0) {
          console.log(chalk.gray('No skills active'));
          console.log('');
          console.log(chalk.yellow('Enable skills with: kutti skills enable <name>'));
          return;
        }

        for (const skill of activeSkills) {
          console.log(`- ${chalk.green(skill.name)}: ${skill.description}`);
        }
        console.log('');
      } catch (error: any) {
        console.error(chalk.red(`Error: ${error.message}`));
      }
    });

  // kutti skills create
  skills
    .command('create')
    .description('Create a new skill interactively')
    .action(async () => {
      try {
        console.log(chalk.yellow('Skill creation not yet fully implemented'));
        console.log(chalk.yellow('You can manually create skills by creating a SKILL.md file in:'));
        console.log(chalk.yellow(`  ${process.env.KUTTI_CONFIG_DIR || '~/.kutti'}/skills/user/<skill-name>/SKILL.md`));
        console.log('');
        console.log(chalk.yellow('Example SKILL.md format:'));
        console.log(chalk.gray(`---`));
        console.log(chalk.gray(`name: my-skill`));
        console.log(chalk.gray(`description: My custom skill`));
        console.log(chalk.gray(`triggers: [python, coding]`));
        console.log(chalk.gray(`priority: high`));
        console.log(chalk.gray(`---`));
        console.log(chalk.gray(''));
        console.log(chalk.gray('# My Skill'));
        console.log(chalk.gray(''));
        console.log(chalk.gray('This skill helps with...'));
      } catch (error: any) {
        console.error(chalk.red(`Error: ${error.message}`));
      }
    });

  // kutti skills edit
  skills
    .command('edit <name>')
    .description('Edit a skill')
    .action((name: string) => {
      try {
        console.log(chalk.yellow(`Editing skill: ${name}`));
        console.log(chalk.yellow('Skill editing not yet implemented'));
        console.log(chalk.yellow('You can manually edit skill files in:'));
        console.log(chalk.yellow(`  ${process.env.KUTTI_CONFIG_DIR || '~/.kutti'}/skills/`));
      } catch (error: any) {
        console.error(chalk.red(`Error: ${error.message}`));
      }
    });

  // kutti skills remove
  skills
    .command('remove <name>')
    .description('Remove a skill')
    .action(async (name: string) => {
      try {
        const success = await skillsManager.remove(name);
        if (success) {
          console.log(chalk.green(`Skill '${name}' removed`));
        } else {
          console.log(chalk.red(`Failed to remove skill '${name}'`));
        }
      } catch (error: any) {
        console.error(chalk.red(`Error: ${error.message}`));
      }
    });

  // kutti skills search
  skills
    .command('search <query>')
    .description('Search for skills')
    .action(async (query: string) => {
      try {
        await initializeSkills();
        const matching = skillsManager.findByTriggers(query);
        
        console.log(chalk.cyan(`\nSkills matching "${query}":\n`));
        
        if (matching.length === 0) {
          console.log(chalk.gray('No matching skills found'));
          return;
        }

        for (const skill of matching) {
          const active = skillsManager.isActive(skill.name) ? chalk.green('✓') : chalk.gray('✗');
          console.log(`- ${active} ${skill.name}: ${skill.description}`);
        }
        console.log('');
      } catch (error: any) {
        console.error(chalk.red(`Error: ${error.message}`));
      }
    });

  // kutti skills export
  skills
    .command('export')
    .description('Export skills')
    .option('--output <path>', 'Output directory')
    .action((options: { output?: string }) => {
      try {
        console.log(chalk.yellow('Skill export not yet implemented'));
        console.log(chalk.yellow('Skills are stored in:'));
        console.log(chalk.yellow(`  ${process.env.KUTTI_CONFIG_DIR || '~/.kutti'}/skills/`));
      } catch (error: any) {
        console.error(chalk.red(`Error: ${error.message}`));
      }
    });

  program.addCommand(skills);
}
