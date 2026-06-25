import { PATHS } from './constants.js';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

type LogLevel = 'debug' | 'info' | 'warn' | 'error';

interface LoggerOptions {
  level?: LogLevel;
  file?: string;
}

class Logger {
  private level: LogLevel;
  private filePath: string | null;

  constructor(options: LoggerOptions = {}) {
    this.level = options.level || 'info';
    this.filePath = options.file || null;
    
    // Ensure log directory exists
    if (this.filePath) {
      const dir = path.dirname(this.filePath);
      if (!fs.existsSync(dir)) {
        fs.mkdirSync(dir, { recursive: true });
      }
    }
  }

  private log(level: LogLevel, message: string, ...args: any[]) {
    const timestamp = new Date().toISOString();
    const formattedMessage = `[${timestamp}] [${level.toUpperCase()}] ${message}`;
    
    // Log to console based on level
    const levels: LogLevel[] = ['debug', 'info', 'warn', 'error'];
    const currentLevelIndex = levels.indexOf(this.level);
    const messageLevelIndex = levels.indexOf(level);
    
    if (messageLevelIndex >= currentLevelIndex) {
      const consoleMethod = level === 'warn' ? console.warn : 
                           level === 'error' ? console.error : 
                           console.log;
      consoleMethod(formattedMessage, ...args);
    }
    
    // Log to file if configured
    if (this.filePath) {
      try {
        const logEntry = `${timestamp} [${level.toUpperCase()}] ${message}\n`;
        fs.appendFileSync(this.filePath, logEntry);
      } catch (error) {
        // Silently fail if we can't write to log file
      }
    }
  }

  debug(message: string, ...args: any[]) {
    this.log('debug', message, ...args);
  }

  info(message: string, ...args: any[]) {
    this.log('info', message, ...args);
  }

  warn(message: string, ...args: any[]) {
    this.log('warn', message, ...args);
  }

  error(message: string, ...args: any[]) {
    this.log('error', message, ...args);
  }

  setLevel(level: LogLevel) {
    this.level = level;
  }

  setFile(filePath: string) {
    this.filePath = filePath;
    const dir = path.dirname(filePath);
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }
  }
}

// Create default logger
export const logger = new Logger({
  level: (process.env.KUTTI_LOG_LEVEL as LogLevel) || 'info',
  file: process.env.KUTTI_LOG_FILE || PATHS.logs,
});

export function createLogger(options: LoggerOptions = {}) {
  return new Logger(options);
}

export { Logger, LogLevel };
