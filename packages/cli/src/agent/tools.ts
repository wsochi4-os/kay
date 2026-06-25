import fs from 'node:fs';
import path from 'node:path';
import { execa } from 'execa';
import { logger } from '../utils/logger.js';
import { configManager } from '../utils/config.js';
import { getProvider } from '../providers/index.js';
import type { AgentContext, Tool, AgentAction, AgentObservation } from '../types/index.js';

/**
 * Built-in tools for the agent
 */

/**
 * Execute a shell command
 */
export const shellTool: Tool = {
  name: 'shell',
  description: 'Execute a shell command and return the output',
  inputSchema: {
    type: 'object',
    properties: {
      command: { type: 'string', description: 'The command to execute' },
      cwd: { type: 'string', description: 'Working directory', default: process.cwd() },
    },
    required: ['command'],
  },
  execute: async (args: { command: string; cwd?: string }, context: AgentContext) => {
    const autoConfirm = configManager.getConfig().agent.autoConfirmShell;
    
    if (!autoConfirm) {
      // In interactive mode, we would prompt for confirmation
      // For now, we'll just log it
      logger.info(`[SHELL] ${args.command}`);
    }

    try {
      const result = await execa({ 
        file: '/bin/sh',
        args: ['-c', args.command],
        cwd: args.cwd || context.currentDirectory,
        timeout: 30000,
      });

      return {
        success: true,
        stdout: result.stdout,
        stderr: result.stderr,
        exitCode: result.exitCode,
      };
    } catch (error: any) {
      return {
        success: false,
        stdout: error.stdout || '',
        stderr: error.stderr || error.message,
        exitCode: error.exitCode || 1,
      };
    }
  },
};

/**
 * Read a file
 */
export const readFileTool: Tool = {
  name: 'read_file',
  description: 'Read the contents of a file',
  inputSchema: {
    type: 'object',
    properties: {
      path: { type: 'string', description: 'Path to the file' },
      encoding: { type: 'string', description: 'File encoding', default: 'utf8' },
    },
    required: ['path'],
  },
  execute: async (args: { path: string; encoding?: string }) => {
    const filePath = path.resolve(args.path);
    
    if (!fs.existsSync(filePath)) {
      throw new Error(`File not found: ${filePath}`);
    }

    const content = fs.readFileSync(filePath, { encoding: args.encoding || 'utf8' });
    return { content, path: filePath };
  },
};

/**
 * Write a file
 */
export const writeFileTool: Tool = {
  name: 'write_file',
  description: 'Write content to a file (creates or overwrites)',
  inputSchema: {
    type: 'object',
    properties: {
      path: { type: 'string', description: 'Path to the file' },
      content: { type: 'string', description: 'Content to write' },
      encoding: { type: 'string', description: 'File encoding', default: 'utf8' },
    },
    required: ['path', 'content'],
  },
  execute: async (args: { path: string; content: string; encoding?: string }, context: AgentContext) => {
    const autoConfirm = configManager.getConfig().agent.autoConfirm;
    
    if (!autoConfirm) {
      logger.info(`[WRITE] ${args.path}`);
    }

    const filePath = path.resolve(args.path);
    const dir = path.dirname(filePath);
    
    // Ensure directory exists
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }

    fs.writeFileSync(filePath, args.content, { encoding: args.encoding || 'utf8' });
    return { success: true, path: filePath };
  },
};

/**
 * Apply a patch to a file
 */
export const patchFileTool: Tool = {
  name: 'patch_file',
  description: 'Apply a unified diff patch to a file',
  inputSchema: {
    type: 'object',
    properties: {
      path: { type: 'string', description: 'Path to the file' },
      diff: { type: 'string', description: 'Unified diff to apply' },
    },
    required: ['path', 'diff'],
  },
  execute: async (args: { path: string; diff: string }) => {
    // Simple patch implementation
    // In production, use a proper diff/patch library
    const filePath = path.resolve(args.path);
    
    if (!fs.existsSync(filePath)) {
      throw new Error(`File not found: ${filePath}`);
    }

    const content = fs.readFileSync(filePath, 'utf8');
    
    // Parse the diff and apply it
    // This is a simplified implementation
    const lines = content.split('\n');
    const diffLines = args.diff.split('\n');
    
    // Find the line to modify
    // This is a placeholder - a real implementation would parse the diff properly
    let modified = content;
    
    // Try to apply simple replacements
    for (const line of diffLines) {
      if (line.startsWith('+') && !line.startsWith('+++')) {
        const newLine = line.substring(1);
        // This is a very naive approach - would need proper diff parsing
      }
    }

    // For now, just return the original content
    // A real implementation would use a library like 'diff' or 'patch-package'
    return { 
      success: false, 
      message: 'Patch application not yet implemented. Use write_file instead.',
      path: filePath 
    };
  },
};

/**
 * List files in a directory
 */
export const listFilesTool: Tool = {
  name: 'list_files',
  description: 'List files and directories in a path',
  inputSchema: {
    type: 'object',
    properties: {
      path: { type: 'string', description: 'Path to list', default: '.' },
      recursive: { type: 'boolean', description: 'List recursively', default: false },
      includeHidden: { type: 'boolean', description: 'Include hidden files', default: false },
    },
    required: [],
  },
  execute: async (args: { path?: string; recursive?: boolean; includeHidden?: boolean }) => {
    const basePath = path.resolve(args.path || '.');
    
    if (!fs.existsSync(basePath)) {
      throw new Error(`Path not found: ${basePath}`);
    }

    const options: { recursive?: boolean; withFileTypes?: boolean } = {
      recursive: args.recursive,
      withFileTypes: true,
    };

    const entries = fs.readdirSync(basePath, options);
    
    const result: any[] = [];
    
    for (const entry of entries) {
      const fullPath = path.join(basePath, entry.name);
      const relativePath = path.relative(basePath, fullPath);
      
      // Skip hidden files unless requested
      if (!args.includeHidden && entry.name.startsWith('.')) {
        continue;
      }

      result.push({
        name: entry.name,
        path: relativePath,
        isDirectory: entry.isDirectory(),
        isFile: entry.isFile(),
      });
    }

    return { files: result, path: basePath };
  },
};

/**
 * Search files for a pattern
 */
export const searchFilesTool: Tool = {
  name: 'search_files',
  description: 'Search for a pattern in files',
  inputSchema: {
    type: 'object',
    properties: {
      pattern: { type: 'string', description: 'Pattern to search for' },
      path: { type: 'string', description: 'Path to search in', default: '.' },
      recursive: { type: 'boolean', description: 'Search recursively', default: true },
      include: { type: 'string', description: 'File patterns to include', default: '**' },
      exclude: { type: 'string', description: 'File patterns to exclude' },
    },
    required: ['pattern'],
  },
  execute: async (args: { pattern: string; path?: string; recursive?: boolean; include?: string; exclude?: string }) => {
    // Simple search implementation
    // In production, use a library like 'glob' or 'ripgrep'
    const basePath = path.resolve(args.path || '.');
    const pattern = new RegExp(args.pattern, 'i');
    
    const results: any[] = [];
    
    function searchDirectory(dir: string) {
      const entries = fs.readdirSync(dir, { withFileTypes: true });
      
      for (const entry of entries) {
        const fullPath = path.join(dir, entry.name);
        
        // Skip directories
        if (entry.isDirectory()) {
          if (args.recursive) {
            searchDirectory(fullPath);
          }
          continue;
        }

        // Skip hidden files
        if (entry.name.startsWith('.')) {
          continue;
        }

        try {
          const content = fs.readFileSync(fullPath, 'utf8');
          const matches = content.match(pattern);
          
          if (matches) {
            results.push({
              path: fullPath,
              matches: matches.map(m => m),
              lineNumbers: [], // Would need line-by-line parsing
            });
          }
        } catch (error) {
          // Skip binary files or unreadable files
        }
      }
    }

    searchDirectory(basePath);
    return { results, pattern: args.pattern };
  },
};

/**
 * Run tests
 */
export const runTestsTool: Tool = {
  name: 'run_tests',
  description: 'Run the configured test command',
  inputSchema: {
    type: 'object',
    properties: {
      command: { type: 'string', description: 'Test command to run' },
      cwd: { type: 'string', description: 'Working directory' },
    },
    required: [],
  },
  execute: async (args: { command?: string; cwd?: string }) => {
    const command = args.command || 'npm test';
    
    try {
      const result = await execa({
        file: '/bin/sh',
        args: ['-c', command],
        cwd: args.cwd || process.cwd(),
        timeout: 60000,
      });

      return {
        success: result.exitCode === 0,
        stdout: result.stdout,
        stderr: result.stderr,
        exitCode: result.exitCode,
      };
    } catch (error: any) {
      return {
        success: false,
        stdout: error.stdout || '',
        stderr: error.stderr || error.message,
        exitCode: error.exitCode || 1,
      };
    }
  },
};

/**
 * Get git status
 */
export const gitStatusTool: Tool = {
  name: 'git_status',
  description: 'Get the current git status',
  inputSchema: {
    type: 'object',
    properties: {
      cwd: { type: 'string', description: 'Working directory' },
    },
    required: [],
  },
  execute: async (args: { cwd?: string }) => {
    try {
      const result = await execa({
        file: 'git',
        args: ['status', '--porcelain'],
        cwd: args.cwd || process.cwd(),
        timeout: 10000,
      });

      return {
        status: result.stdout,
        isClean: result.stdout.trim() === '',
      };
    } catch (error: any) {
      return {
        status: '',
        isClean: true,
        error: error.message,
      };
    }
  },
};

/**
 * Get git diff
 */
export const gitDiffTool: Tool = {
  name: 'git_diff',
  description: 'Get the current git diff',
  inputSchema: {
    type: 'object',
    properties: {
      cwd: { type: 'string', description: 'Working directory' },
      staged: { type: 'boolean', description: 'Show staged changes only', default: false },
    },
    required: [],
  },
  execute: async (args: { cwd?: string; staged?: boolean }) => {
    try {
      const result = await execa({
        file: 'git',
        args: args.staged ? ['diff', '--cached'] : ['diff'],
        cwd: args.cwd || process.cwd(),
        timeout: 10000,
      });

      return {
        diff: result.stdout,
        hasChanges: result.stdout.trim() !== '',
      };
    } catch (error: any) {
      return {
        diff: '',
        hasChanges: false,
        error: error.message,
      };
    }
  },
};

/**
 * Commit changes
 */
export const gitCommitTool: Tool = {
  name: 'git_commit',
  description: 'Commit changes with a message',
  inputSchema: {
    type: 'object',
    properties: {
      message: { type: 'string', description: 'Commit message' },
      cwd: { type: 'string', description: 'Working directory' },
      all: { type: 'boolean', description: 'Commit all changes', default: false },
    },
    required: ['message'],
  },
  execute: async (args: { message: string; cwd?: string; all?: boolean }) => {
    try {
      await execa({
        file: 'git',
        args: ['add', args.all ? '.' : '-A'],
        cwd: args.cwd || process.cwd(),
        timeout: 10000,
      });

      const result = await execa({
        file: 'git',
        args: ['commit', '-m', args.message],
        cwd: args.cwd || process.cwd(),
        timeout: 10000,
      });

      return {
        success: true,
        hash: result.stdout.trim(),
        message: args.message,
      };
    } catch (error: any) {
      return {
        success: false,
        error: error.message,
      };
    }
  },
};

/**
 * Get built-in tools
 */
export function getBuiltInTools(): Tool[] {
  return [
    shellTool,
    readFileTool,
    writeFileTool,
    patchFileTool,
    listFilesTool,
    searchFilesTool,
    runTestsTool,
    gitStatusTool,
    gitDiffTool,
    gitCommitTool,
  ];
}
