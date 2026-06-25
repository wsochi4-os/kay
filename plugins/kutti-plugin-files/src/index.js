import fs from 'node:fs';
import path from 'node:path';

// Kutti Files Plugin
// Provides file operations capabilities

export default {
  name: 'kutti-plugin-files',
  
  commands: {
    files: {
      description: 'File operations',
      subcommands: {
        read: {
          description: 'Read a file',
          action: async (filePath) => {
            const content = fs.readFileSync(filePath, 'utf8');
            console.log(content);
          }
        },
        write: {
          description: 'Write to a file',
          action: async (filePath, content) => {
            fs.writeFileSync(filePath, content);
            console.log(`File written: ${filePath}`);
          }
        },
        list: {
          description: 'List files in a directory',
          action: async (dirPath = '.') => {
            const files = fs.readdirSync(dirPath);
            console.log(files.join('\n'));
          }
        }
      }
    }
  },
  
  tools: [
    {
      name: 'read_file',
      description: 'Read the contents of a file',
      inputSchema: {
        type: 'object',
        properties: {
          path: { type: 'string', description: 'Path to the file' },
          encoding: { type: 'string', description: 'File encoding', default: 'utf8' }
        },
        required: ['path']
      },
      execute: async (args, context) => {
        const filePath = path.resolve(args.path);
        
        if (!fs.existsSync(filePath)) {
          throw new Error(`File not found: ${filePath}`);
        }
        
        const content = fs.readFileSync(filePath, { encoding: args.encoding || 'utf8' });
        return { content, path: filePath };
      }
    },
    {
      name: 'write_file',
      description: 'Write content to a file',
      inputSchema: {
        type: 'object',
        properties: {
          path: { type: 'string', description: 'Path to the file' },
          content: { type: 'string', description: 'Content to write' },
          encoding: { type: 'string', description: 'File encoding', default: 'utf8' }
        },
        required: ['path', 'content']
      },
      execute: async (args, context) => {
        const filePath = path.resolve(args.path);
        const dir = path.dirname(filePath);
        
        // Ensure directory exists
        if (!fs.existsSync(dir)) {
          fs.mkdirSync(dir, { recursive: true });
        }
        
        fs.writeFileSync(filePath, args.content, { encoding: args.encoding || 'utf8' });
        return { success: true, path: filePath };
      }
    },
    {
      name: 'list_files',
      description: 'List files in a directory',
      inputSchema: {
        type: 'object',
        properties: {
          path: { type: 'string', description: 'Path to list', default: '.' },
          recursive: { type: 'boolean', description: 'List recursively', default: false },
          includeHidden: { type: 'boolean', description: 'Include hidden files', default: false }
        },
        required: []
      },
      execute: async (args, context) => {
        const basePath = path.resolve(args.path || '.');
        
        if (!fs.existsSync(basePath)) {
          throw new Error(`Path not found: ${basePath}`);
        }
        
        const entries = fs.readdirSync(basePath, { 
          recursive: args.recursive,
          withFileTypes: true 
        });
        
        const result = [];
        
        for (const entry of entries) {
          const fullPath = path.join(basePath, entry.name);
          const relativePath = path.relative(basePath, fullPath);
          
          if (!args.includeHidden && entry.name.startsWith('.')) {
            continue;
          }
          
          result.push({
            name: entry.name,
            path: relativePath,
            isDirectory: entry.isDirectory(),
            isFile: entry.isFile()
          });
        }
        
        return { files: result, path: basePath };
      }
    },
    {
      name: 'search_files',
      description: 'Search for a pattern in files',
      inputSchema: {
        type: 'object',
        properties: {
          pattern: { type: 'string', description: 'Pattern to search for' },
          path: { type: 'string', description: 'Path to search in', default: '.' },
          recursive: { type: 'boolean', description: 'Search recursively', default: true }
        },
        required: ['pattern']
      },
      execute: async (args, context) => {
        const basePath = path.resolve(args.path || '.');
        const pattern = new RegExp(args.pattern, 'i');
        const results = [];
        
        function searchDirectory(dir) {
          const entries = fs.readdirSync(dir, { withFileTypes: true });
          
          for (const entry of entries) {
            const fullPath = path.join(dir, entry.name);
            
            if (entry.isDirectory()) {
              if (args.recursive) {
                searchDirectory(fullPath);
              }
              continue;
            }
            
            if (entry.name.startsWith('.')) {
              continue;
            }
            
            try {
              const content = fs.readFileSync(fullPath, 'utf8');
              const matches = content.match(pattern);
              
              if (matches) {
                results.push({
                  path: fullPath,
                  matches: matches.map(m => m)
                });
              }
            } catch (error) {
              // Skip binary files
            }
          }
        }
        
        searchDirectory(basePath);
        return { results, pattern: args.pattern };
      }
    }
  ],
  
  hooks: {}
};
