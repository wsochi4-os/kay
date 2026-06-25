import { getProvider } from '../providers/index.js';
import { getBuiltInTools } from './tools.js';
import { configManager } from '../utils/config.js';
import { authManager } from '../auth/manager.js';
import { logger } from '../utils/logger.js';
import type { 
  AgentContext, 
  AgentAction, 
  AgentObservation,
  ConversationMessage,
  Tool 
} from '../types/index.js';

/**
 * Agent Loop - Micro-agent inspired iterative approach
 * THINK -> ACT -> OBSERVE -> EVALUATE -> (refine or done)
 */
export class AgentLoop {
  private context: AgentContext;
  private messages: ConversationMessage[];
  private tools: Tool[];
  private maxIterations: number;
  private iteration: number = 0;

  constructor(context: Partial<AgentContext> = {}) {
    this.context = {
      config: configManager.getConfig(),
      provider: configManager.getProvider(configManager.getActiveProvider()),
      credentials: {},
      plugins: [],
      skills: [],
      mcpClients: {},
      systemPrompt: this.buildSystemPrompt(),
      currentDirectory: process.cwd(),
      ...context,
    };

    this.messages = [];
    this.tools = [...getBuiltInTools()];
    this.maxIterations = context.config?.agent?.maxIterations || 20;
  }

  private buildSystemPrompt(): string {
    const config = configManager.getConfig();
    const provider = configManager.getActiveProvider();
    const model = configManager.getActiveModel();

    return `You are Kutti, a personal AI CLI agent. You are currently using the ${provider} provider with the ${model} model.

Your capabilities:
- Execute shell commands
- Read and write files
- Search and modify code
- Run tests
- Use git commands
- Call external tools via MCP

Guidelines:
- Always think through your actions before executing them
- Be concise and direct
- If you're unsure, ask for clarification
- Follow the user's instructions carefully
- Use tools to gather information before making changes

Current working directory: ${process.cwd()}
`;
  }

  /**
   * Add a message to the conversation
   */
  addMessage(message: ConversationMessage) {
    this.messages.push(message);
  }

  /**
   * Add a tool to the agent
   */
  addTool(tool: Tool) {
    this.tools.push(tool);
  }

  /**
   * Add multiple tools
   */
  addTools(tools: Tool[]) {
    this.tools.push(...tools);
  }

  /**
   * Get available tools as a string description
   */
  getAvailableTools(): string {
    return this.tools
      .map(tool => `${tool.name}: ${tool.description}`)
      .join('\n');
  }

  /**
   * Format tools for the LLM
   */
  formatToolsForLLM(): string {
    return this.tools
      .map(tool => {
        return `Tool: ${tool.name}\nDescription: ${tool.description}\nParameters: ${JSON.stringify(tool.inputSchema.properties, null, 2)}`;
      })
      .join('\n\n');
  }

  /**
   * Execute a tool
   */
  async executeTool(toolName: string, args: any): Promise<any> {
    const tool = this.tools.find(t => t.name === toolName);
    
    if (!tool) {
      throw new Error(`Tool '${toolName}' not found`);
    }

    try {
      const result = await tool.execute(args, this.context);
      return { success: true, result, tool: toolName };
    } catch (error: any) {
      return { success: false, error: error.message, tool: toolName };
    }
  }

  /**
   * THINK phase - Generate a plan
   */
  async think(prompt: string): Promise<AgentAction[]> {
    const provider = getProvider(this.context.config.provider);
    
    const messages: ConversationMessage[] = [
      { role: 'system', content: this.context.systemPrompt },
      ...this.messages,
      {
        role: 'user',
        content: `Task: ${prompt}\n\nAvailable tools:\n${this.formatToolsForLLM()}\n\nGenerate a plan to accomplish this task. Respond with a JSON array of actions to take.`,
      },
    ];

    try {
      const response = await provider.chat(messages, {
        temperature: 0.1, // Low temperature for planning
        maxTokens: 2048,
      });

      // Parse the response as JSON
      try {
        // Try to extract JSON from the response
        const jsonMatch = response.match(/\{[\s\S]*\}/);
        if (jsonMatch) {
          const actions = JSON.parse(jsonMatch[0]);
          if (Array.isArray(actions)) {
            return actions as AgentAction[];
          }
        }
      } catch (e) {
        // If JSON parsing fails, try to parse it differently
        logger.debug('Failed to parse JSON response, trying alternative approach');
      }

      // If we can't parse as JSON, create a default action
      return [
        {
          type: 'shell',
          name: 'echo',
          args: { command: `echo "${prompt}"` },
        },
      ];
    } catch (error) {
      logger.error(`Error in THINK phase: ${error}`);
      throw error;
    }
  }

  /**
   * ACT phase - Execute actions
   */
  async act(actions: AgentAction[]): Promise<AgentObservation[]> {
    const observations: AgentObservation[] = [];

    for (const action of actions) {
      try {
        switch (action.type) {
          case 'tool':
            if (action.name) {
              const result = await this.executeTool(action.name, action.args);
              observations.push({
                type: 'tool_result',
                content: JSON.stringify(result),
                tool: action.name,
                success: result.success,
              });
            }
            break;

          case 'shell':
            if (action.args?.command) {
              const result = await this.executeTool('shell', action.args);
              observations.push({
                type: 'stdout',
                content: result.result?.stdout || '',
                success: result.success,
              });
              if (result.result?.stderr) {
                observations.push({
                  type: 'stderr',
                  content: result.result.stderr,
                  success: false,
                });
              }
            }
            break;

          case 'read_file':
            if (action.path) {
              const result = await this.executeTool('read_file', { path: action.path });
              observations.push({
                type: 'file_read',
                content: result.result?.content || '',
                path: action.path,
                success: true,
              });
            }
            break;

          case 'write_file':
            if (action.path && action.content) {
              const result = await this.executeTool('write_file', {
                path: action.path,
                content: action.content,
              });
              observations.push({
                type: 'file_written',
                content: `File written: ${action.path}`,
                path: action.path,
                success: result.success,
              });
            }
            break;

          case 'patch_file':
            if (action.path && action.diff) {
              const result = await this.executeTool('patch_file', {
                path: action.path,
                diff: action.diff,
              });
              observations.push({
                type: 'file_written',
                content: JSON.stringify(result),
                path: action.path,
                success: result.success,
              });
            }
            break;

          case 'done':
            // Task is complete
            break;

          default:
            logger.warn(`Unknown action type: ${action.type}`);
        }
      } catch (error: any) {
        observations.push({
          type: 'stderr',
          content: error.message,
          success: false,
        });
      }
    }

    return observations;
  }

  /**
   * OBSERVE phase - Collect observations
   */
  observe(observations: AgentObservation[]): string {
    return observations
      .map(obs => {
        if (obs.type === 'file_read') {
          return `[FILE: ${obs.path}]\n${obs.content}`;
        } else if (obs.type === 'file_written') {
          return `[WRITTEN: ${obs.path}] ${obs.success ? 'Success' : 'Failed'}`;
        } else if (obs.type === 'tool_result') {
          return `[TOOL: ${obs.tool}] ${obs.success ? 'Success' : 'Failed'}: ${obs.content}`;
        } else if (obs.type === 'stdout') {
          return `[STDOUT]\n${obs.content}`;
        } else if (obs.type === 'stderr') {
          return `[STDERR]\n${obs.content}`;
        } else if (obs.type === 'test_result') {
          return `[TEST] ${obs.success ? 'Passed' : 'Failed'}: ${obs.content}`;
        }
        return `[OBSERVATION] ${obs.content}`;
      })
      .join('\n\n');
  }

  /**
   * EVALUATE phase - Check if task is complete
   */
  async evaluate(
    prompt: string,
    observations: AgentObservation[]
  ): Promise<{ complete: boolean; reason: string; nextPrompt?: string }> {
    const observationText = this.observe(observations);
    
    // Simple evaluation: if there's a 'done' action or tests passed, we're done
    const hasDoneAction = observations.some(obs => obs.type === 'file_written' && obs.success);
    const hasTestPassed = observations.some(obs => obs.type === 'test_result' && obs.success);
    
    if (hasDoneAction || hasTestPassed) {
      return { complete: true, reason: 'Task appears to be complete' };
    }

    // Check if we've reached max iterations
    if (this.iteration >= this.maxIterations) {
      return { 
        complete: true, 
        reason: `Reached maximum iterations (${this.maxIterations})` 
      };
    }

    // Use LLM to evaluate
    const provider = getProvider(this.context.config.provider);
    
    const messages: ConversationMessage[] = [
      { role: 'system', content: this.context.systemPrompt },
      ...this.messages,
      {
        role: 'user',
        content: `Task: ${prompt}\n\nObservations:\n${observationText}\n\nIs the task complete? Respond with JSON: { "complete": boolean, "reason": string, "nextPrompt"?: string }`,
      },
    ];

    try {
      const response = await provider.chat(messages, {
        temperature: 0.1,
        maxTokens: 512,
      });

      try {
        const jsonMatch = response.match(/\{[\s\S]*\}/);
        if (jsonMatch) {
          const evaluation = JSON.parse(jsonMatch[0]);
          return {
            complete: evaluation.complete || false,
            reason: evaluation.reason || 'Unknown',
            nextPrompt: evaluation.nextPrompt,
          };
        }
      } catch (e) {
        // If JSON parsing fails, make a decision based on observations
        logger.debug('Failed to parse evaluation JSON');
      }

      // Default: continue
      return { 
        complete: false, 
        reason: 'Task not yet complete, continuing...' 
      };
    } catch (error) {
      logger.error(`Error in EVALUATE phase: ${error}`);
      // If evaluation fails, assume we need to continue
      return { 
        complete: false, 
        reason: 'Evaluation error, continuing...' 
      };
    }
  }

  /**
   * Run the complete agent loop
   */
  async run(
    prompt: string,
    options: {
      testCommand?: string;
      maxIterations?: number;
      onIteration?: (iteration: number, action: AgentAction, observation: AgentObservation[]) => void;
    } = {}
  ): Promise<{
    success: boolean;
    message: string;
    iterations: number;
    observations: AgentObservation[];
  }> {
    if (options.maxIterations) {
      this.maxIterations = options.maxIterations;
    }

    const allObservations: AgentObservation[] = [];
    
    // Add initial user message
    this.addMessage({ role: 'user', content: prompt });

    while (this.iteration < this.maxIterations) {
      this.iteration++;
      logger.info(`Iteration ${this.iteration}/${this.maxIterations}`);

      // THINK
      logger.debug('Phase: THINK');
      const actions = await this.think(prompt);
      
      if (!actions || actions.length === 0) {
        logger.warn('No actions generated, stopping');
        break;
      }

      // ACT
      logger.debug('Phase: ACT');
      const observations = await this.act(actions);
      allObservations.push(...observations);

      // Call iteration callback if provided
      if (options.onIteration) {
        options.onIteration(this.iteration, actions[0], observations);
      }

      // OBSERVE
      logger.debug('Phase: OBSERVE');
      const observationText = this.observe(observations);
      logger.debug(`Observations: ${observationText}`);

      // EVALUATE
      logger.debug('Phase: EVALUATE');
      const evaluation = await this.evaluate(prompt, observations);
      
      if (evaluation.complete) {
        logger.info(`Task complete: ${evaluation.reason}`);
        return {
          success: true,
          message: evaluation.reason,
          iterations: this.iteration,
          observations: allObservations,
        };
      }

      // Add observations to messages for next iteration
      this.addMessage({
        role: 'assistant',
        content: `Actions taken:\n${actions.map(a => `- ${a.type}: ${JSON.stringify(a)}`).join('\n')}\n\nObservations:\n${observationText}`,
      });
    }

    return {
      success: false,
      message: `Reached maximum iterations (${this.maxIterations})`,
      iterations: this.iteration,
      observations: allObservations,
    };
  }

  /**
   * Run a simple one-shot task (no iteration)
   */
  async runOnce(prompt: string): Promise<string> {
    const provider = getProvider(this.context.config.provider);
    
    const messages: ConversationMessage[] = [
      { role: 'system', content: this.context.systemPrompt },
      ...this.messages,
      { role: 'user', content: prompt },
    ];

    const response = await provider.chat(messages, {
      temperature: this.context.config.temperature,
      maxTokens: this.context.config.maxTokens,
    });

    return response;
  }

  /**
   * Reset the agent state
   */
  reset() {
    this.messages = [];
    this.iteration = 0;
  }
}

/**
 * Create a new agent loop instance
 */
export function createAgentLoop(context?: Partial<AgentContext>) {
  return new AgentLoop(context);
}
