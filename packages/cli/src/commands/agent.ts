import { Command } from 'commander';
import chalk from 'chalk';
import { createAgentLoop } from '../agent/loop.js';
import { initializePlugins } from '../plugins/loader.js';
import { initializeSkills } from '../skills/manager.js';
import { initializeMCP } from '../mcp/host.js';
import { authManager } from '../auth/manager.js';
import { logger } from '../utils/logger.js';

/**
 * Create agent commands
 */
export function createAgentCommands(program: Command) {
  const agent = new Command('agent');
  agent.description('Run the Kutti agent loop');

  // kutti agent (default - start interactive agent)
  agent
    .description('Start an interactive agent session')
    .option('--prompt <prompt>', 'Initial prompt for the agent')
    .option('--test <command>', 'Test command to run')
    .option('--file <file>', 'File to work on')
    .option('--max-iterations <n>', 'Maximum iterations', '20')
    .option('--watch', 'Watch for file changes and re-run')
    .action(async (options) => {
      try {
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
        const agentLoop = createAgentLoop();

        if (options.prompt) {
          // Run with initial prompt
          console.log(chalk.cyan(`\nStarting agent with prompt: ${options.prompt}\n`));
          
          const result = await agentLoop.run(options.prompt, {
            maxIterations: parseInt(options.maxIterations),
            testCommand: options.test,
            onIteration: (iteration, action, observations) => {
              console.log(chalk.gray(`\n--- Iteration ${iteration} ---`));
              console.log(chalk.blue(`Action: ${JSON.stringify(action)}`));
              console.log(chalk.green(`Observations: ${JSON.stringify(observations)}`));
            },
          });

          console.log(chalk.cyan(`\nAgent finished: ${result.message}`));
          console.log(chalk.gray(`Iterations: ${result.iterations}`));
        } else {
          // Start interactive session
          console.log(chalk.cyan('\nKutti Agent - Interactive Mode'));
          console.log(chalk.cyan('Type your prompt and press Enter. Type "exit" to quit.\n'));

          // Simple interactive loop
          const readline = require('readline');
          const rl = readline.createInterface({
            input: process.stdin,
            output: process.stdout,
            prompt: chalk.cyan('kutti> '),
          });

          rl.prompt();

          rl.on('line', async (line: string) => {
            const trimmed = line.trim();

            if (trimmed === 'exit' || trimmed === 'quit') {
              rl.close();
              return;
            }

            if (trimmed) {
              try {
                console.log(chalk.cyan('\nThinking...\n'));
                const response = await agentLoop.runOnce(trimmed);
                console.log(chalk.green('\n' + response + '\n'));
              } catch (error: any) {
                console.error(chalk.red(`\nError: ${error.message}\n`));
              }
            }

            rl.prompt();
          }).on('close', () => {
            console.log(chalk.cyan('\nAgent session ended. Goodbye!\n'));
            process.exit(0);
          });
        }
      } catch (error: any) {
        console.error(chalk.red(`Error: ${error.message}`));
        if (options.debug) {
          console.error(error.stack);
        }
      }
    });

  // kutti fix
  agent
    .command('fix')
    .description('Fix a failing test')
    .option('--test <command>', 'Test command to run')
    .option('--file <file>', 'File to fix')
    .option('--context <path>', 'Context directory')
    .option('--max-iterations <n>', 'Maximum iterations', '20')
    .action(async (options) => {
      try {
        // Initialize systems
        await initializePlugins();
        await initializeSkills();
        await initializeMCP();

        if (!options.test) {
          console.log(chalk.red('Error: --test option is required'));
          console.log(chalk.yellow('Usage: kutti fix --test "npm test"'));
          return;
        }

        console.log(chalk.cyan(`\nFixing failing test: ${options.test}\n`));

        const agentLoop = createAgentLoop();
        const prompt = `Fix the failing test. Test command: ${options.test}`;

        const result = await agentLoop.run(prompt, {
          maxIterations: parseInt(options.maxIterations),
          testCommand: options.test,
          onIteration: (iteration, action, observations) => {
            console.log(chalk.gray(`\n--- Iteration ${iteration} ---`));
            console.log(chalk.blue(`Action: ${JSON.stringify(action)}`));
          },
        });

        console.log(chalk.cyan(`\nFix attempt finished: ${result.message}`));
        console.log(chalk.gray(`Iterations: ${result.iterations}`));
      } catch (error: any) {
        console.error(chalk.red(`Error: ${error.message}`));
      }
    });

  // kutti build
  agent
    .command('build')
    .description('Generate code from a description')
    .option('--description <desc>', 'Description of what to build')
    .option('--language <lang>', 'Programming language')
    .option('--framework <framework>', 'Framework to use')
    .option('--output <path>', 'Output file or directory')
    .option('--max-iterations <n>', 'Maximum iterations', '20')
    .action(async (options) => {
      try {
        if (!options.description) {
          console.log(chalk.red('Error: --description option is required'));
          console.log(chalk.yellow('Usage: kutti build --description "REST API endpoint"'));
          return;
        }

        // Initialize systems
        await initializePlugins();
        await initializeSkills();
        await initializeMCP();

        console.log(chalk.cyan(`\nBuilding: ${options.description}\n`));

        const agentLoop = createAgentLoop();
        
        let prompt = `Build: ${options.description}`;
        if (options.language) {
          prompt += ` in ${options.language}`;
        }
        if (options.framework) {
          prompt += ` using ${options.framework}`;
        }
        if (options.output) {
          prompt += `. Save to: ${options.output}`;
        }

        const result = await agentLoop.run(prompt, {
          maxIterations: parseInt(options.maxIterations),
          onIteration: (iteration, action, observations) => {
            console.log(chalk.gray(`\n--- Iteration ${iteration} ---`));
            console.log(chalk.blue(`Action: ${JSON.stringify(action)}`));
          },
        });

        console.log(chalk.cyan(`\nBuild finished: ${result.message}`));
        console.log(chalk.gray(`Iterations: ${result.iterations}`));
      } catch (error: any) {
        console.error(chalk.red(`Error: ${error.message}`));
      }
    });

  // kutti review
  agent
    .command('review')
    .description('Review code or a PR')
    .option('--file <file>', 'File to review')
    .option('--diff <diff>', 'Diff to review')
    .option('--pr <number>', 'PR number to review')
    .option('--repo <repo>', 'Repository to review')
    .action(async (options) => {
      try {
        // Initialize systems
        await initializePlugins();
        await initializeSkills();
        await initializeMCP();

        let prompt = 'Review the following code and provide feedback:';

        if (options.file) {
          prompt = `Review the file: ${options.file}`;
        } else if (options.diff) {
          prompt = `Review the diff:\n${options.diff}`;
        } else if (options.pr) {
          prompt = `Review PR #${options.pr}`;
          if (options.repo) {
            prompt += ` in ${options.repo}`;
          }
        }

        console.log(chalk.cyan(`\nReviewing...\n`));

        const agentLoop = createAgentLoop();
        const result = await agentLoop.runOnce(prompt);

        console.log(chalk.cyan('\nReview:\n'));
        console.log(chalk.white(result));
      } catch (error: any) {
        console.error(chalk.red(`Error: ${error.message}`));
      }
    });

  // kutti explain
  agent
    .command('explain')
    .description('Explain code or a concept')
    .option('--file <file>', 'File to explain')
    .option('--code <code>', 'Code snippet to explain')
    .option('--concept <concept>', 'Concept to explain')
    .action(async (options) => {
      try {
        // Initialize systems
        await initializePlugins();
        await initializeSkills();
        await initializeMCP();

        let prompt = '';

        if (options.file) {
          prompt = `Explain the file: ${options.file}`;
        } else if (options.code) {
          prompt = `Explain the following code:\n\n${options.code}`;
        } else if (options.concept) {
          prompt = `Explain the concept: ${options.concept}`;
        } else {
          console.log(chalk.red('Error: Please specify --file, --code, or --concept'));
          return;
        }

        console.log(chalk.cyan(`\nExplaining...\n`));

        const agentLoop = createAgentLoop();
        const result = await agentLoop.runOnce(prompt);

        console.log(chalk.cyan('\nExplanation:\n'));
        console.log(chalk.white(result));
      } catch (error: any) {
        console.error(chalk.red(`Error: ${error.message}`));
      }
    });

  program.addCommand(agent);
}
