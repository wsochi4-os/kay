import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import { PATHS, BUILTIN_SKILLS } from '../utils/constants.js';
import { logger } from '../utils/logger.js';
import type { SkillMetadata } from '../types/index.js';

/**
 * Skills Manager - Loads and manages Kutti skills
 */
export class SkillsManager {
  private skills: Map<string, SkillMetadata>;
  private skillContents: Map<string, string>;
  private activeSkills: Set<string>;

  constructor() {
    this.skills = new Map();
    this.skillContents = new Map();
    this.activeSkills = new Set();
  }

  /**
   * Get the skills directory
   */
  private getSkillsDir(): string {
    return PATHS.skills.replace('~', os.homedir());
  }

  /**
   * Parse skill metadata from a skill file
   */
  private parseSkillMetadata(content: string): SkillMetadata {
    const lines = content.split('\n');
    const metadata: Partial<SkillMetadata> = {};
    let inMetadata = false;

    for (const line of lines) {
      if (line.trim() === '---') {
        inMetadata = !inMetadata;
        continue;
      }

      if (inMetadata) {
        const match = line.match(/^(\w+):\s*(.+)$/);
        if (match) {
          const key = match[1];
          const value = match[2].trim();

          if (key === 'name') {
            metadata.name = value;
          } else if (key === 'description') {
            metadata.description = value;
          } else if (key === 'triggers') {
            metadata.triggers = value.split(',').map(t => t.trim());
          } else if (key === 'priority') {
            metadata.priority = value as 'low' | 'medium' | 'high';
          }
        }
      }
    }

    return {
      name: 'unnamed',
      description: '',
      ...metadata,
    } as SkillMetadata;
  }

  /**
   * Load a skill from a file
   */
  loadFromFile(filePath: string): SkillMetadata | null {
    try {
      const content = fs.readFileSync(filePath, 'utf8');
      const metadata = this.parseSkillMetadata(content);
      
      // Use the filename as name if not specified
      if (!metadata.name) {
        const basename = path.basename(filePath, '.md');
        metadata.name = basename;
      }

      this.skillContents.set(metadata.name, content);
      return metadata;
    } catch (error) {
      logger.warn(`Failed to load skill from ${filePath}: ${error}`);
      return null;
    }
  }

  /**
   * Load a skill by name
   */
  async load(skillName: string): Promise<SkillMetadata | null> {
    // Check if already loaded
    if (this.skills.has(skillName)) {
      return this.skills.get(skillName) || null;
    }

    // Try built-in skills first
    if (BUILTIN_SKILLS.includes(skillName)) {
      const builtInPath = this.getBuiltInSkillPath(skillName);
      if (builtInPath) {
        const skill = this.loadFromFile(builtInPath);
        if (skill) {
          this.skills.set(skill.name, skill);
          return skill;
        }
      }
    }

    // Try user skills directory
    const userSkillPath = path.join(this.getSkillsDir(), skillName, 'SKILL.md');
    if (fs.existsSync(userSkillPath)) {
      const skill = this.loadFromFile(userSkillPath);
      if (skill) {
        this.skills.set(skill.name, skill);
        return skill;
      }
    }

    // Try public skills directory
    const publicSkillPath = path.join(this.getSkillsDir(), 'public', skillName, 'SKILL.md');
    if (fs.existsSync(publicSkillPath)) {
      const skill = this.loadFromFile(publicSkillPath);
      if (skill) {
        this.skills.set(skill.name, skill);
        return skill;
      }
    }

    return null;
  }

  /**
   * Get path to a built-in skill
   */
  private getBuiltInSkillPath(skillName: string): string | null {
    const builtInPaths = [
      path.join(process.cwd(), 'skills', skillName, 'SKILL.md'),
      path.join(__dirname, '..', '..', '..', 'skills', skillName, 'SKILL.md'),
    ];

    for (const p of builtInPaths) {
      if (fs.existsSync(p)) {
        return p;
      }
    }

    return null;
  }

  /**
   * Load all skills from a directory
   */
  async loadFromDirectory(directory: string): Promise<SkillMetadata[]> {
    const loaded: SkillMetadata[] = [];

    try {
      const entries = fs.readdirSync(directory, { withFileTypes: true });

      for (const entry of entries) {
        if (entry.isDirectory()) {
          const skillDir = path.join(directory, entry.name);
          const skillFile = path.join(skillDir, 'SKILL.md');
          
          if (fs.existsSync(skillFile)) {
            const skill = this.loadFromFile(skillFile);
            if (skill) {
              loaded.push(skill);
            }
          }
        } else if (entry.isFile() && entry.name === 'SKILL.md') {
          const skill = this.loadFromFile(path.join(directory, entry.name));
          if (skill) {
            loaded.push(skill);
          }
        }
      }
    } catch (error) {
      logger.warn(`Failed to load skills from ${directory}: ${error}`);
    }

    return loaded;
  }

  /**
   * Load all built-in skills
   */
  async loadBuiltInSkills(): Promise<SkillMetadata[]> {
    const loaded: SkillMetadata[] = [];

    for (const skillName of BUILTIN_SKILLS) {
      const skill = await this.load(skillName);
      if (skill) {
        loaded.push(skill);
      }
    }

    return loaded;
  }

  /**
   * Load all user skills
   */
  async loadUserSkills(): Promise<SkillMetadata[]> {
    const skillsDir = this.getSkillsDir();
    
    if (!fs.existsSync(skillsDir)) {
      fs.mkdirSync(skillsDir, { recursive: true });
      return [];
    }

    // Load from user directory
    const userSkills = await this.loadFromDirectory(path.join(skillsDir, 'user'));
    
    // Load from public directory
    const publicSkills = await this.loadFromDirectory(path.join(skillsDir, 'public'));

    return [...userSkills, ...publicSkills];
  }

  /**
   * Load all skills (built-in + user)
   */
  async loadAll(): Promise<SkillMetadata[]> {
    const builtIn = await this.loadBuiltInSkills();
    const user = await this.loadUserSkills();
    
    return [...builtIn, ...user];
  }

  /**
   * Get a loaded skill
   */
  get(skillName: string): SkillMetadata | undefined {
    return this.skills.get(skillName);
  }

  /**
   * Get all loaded skills
   */
  getAll(): SkillMetadata[] {
    return Array.from(this.skills.values());
  }

  /**
   * Get all loaded skill names
   */
  getLoadedSkillNames(): string[] {
    return Array.from(this.skills.keys());
  }

  /**
   * Get skill content
   */
  getContent(skillName: string): string | undefined {
    return this.skillContents.get(skillName);
  }

  /**
   * Check if a skill is loaded
   */
  isLoaded(skillName: string): boolean {
    return this.skills.has(skillName);
  }

  /**
   * Enable a skill
   */
  enable(skillName: string): boolean {
    if (this.skills.has(skillName)) {
      this.activeSkills.add(skillName);
      logger.info(`Skill ${skillName} enabled`);
      return true;
    }
    return false;
  }

  /**
   * Disable a skill
   */
  disable(skillName: string): boolean {
    if (this.activeSkills.has(skillName)) {
      this.activeSkills.delete(skillName);
      logger.info(`Skill ${skillName} disabled`);
      return true;
    }
    return false;
  }

  /**
   * Get active skills
   */
  getActiveSkills(): SkillMetadata[] {
    return Array.from(this.activeSkills.values())
      .map(name => this.skills.get(name))
      .filter((s): s is SkillMetadata => s !== undefined);
  }

  /**
   * Get active skill names
   */
  getActiveSkillNames(): string[] {
    return Array.from(this.activeSkills.values());
  }

  /**
   * Check if a skill is active
   */
  isActive(skillName: string): boolean {
    return this.activeSkills.has(skillName);
  }

  /**
   * Enable all skills
   */
  enableAll(): void {
    for (const name of this.skills.keys()) {
      this.activeSkills.add(name);
    }
    logger.info(`All ${this.skills.size} skills enabled`);
  }

  /**
   * Disable all skills
   */
  disableAll(): void {
    this.activeSkills.clear();
    logger.info('All skills disabled');
  }

  /**
   * Find skills matching triggers
   */
  findByTriggers(query: string): SkillMetadata[] {
    const matching: SkillMetadata[] = [];

    for (const skill of this.skills.values()) {
      if (skill.triggers) {
        for (const trigger of skill.triggers) {
          if (query.toLowerCase().includes(trigger.toLowerCase())) {
            matching.push(skill);
            break;
          }
        }
      }
    }

    return matching;
  }

  /**
   * Create a new skill
   */
  async create(skillName: string, metadata: Partial<SkillMetadata>, content: string): Promise<boolean> {
    try {
      const userSkillsDir = path.join(this.getSkillsDir(), 'user', skillName);
      fs.mkdirSync(userSkillsDir, { recursive: true });

      // Create SKILL.md
      const skillFile = path.join(userSkillsDir, 'SKILL.md');
      
      const metadataLines = [
        '---',
        `name: ${metadata.name || skillName}`,
        `description: ${metadata.description || ''}`,
      ];

      if (metadata.triggers) {
        metadataLines.push(`triggers: [${metadata.triggers.map(t => `"${t}"`).join(', ')}]`);
      }
      if (metadata.priority) {
        metadataLines.push(`priority: ${metadata.priority}`);
      }
      metadataLines.push('---');
      metadataLines.push('');

      fs.writeFileSync(skillFile, metadataLines.join('\n') + content);

      // Load the skill
      await this.load(skillName);
      
      logger.info(`Skill ${skillName} created`);
      return true;
    } catch (error) {
      logger.error(`Failed to create skill ${skillName}: ${error}`);
      return false;
    }
  }

  /**
   * Remove a skill
   */
  async remove(skillName: string): Promise<boolean> {
    try {
      // Unload the skill
      this.skills.delete(skillName);
      this.skillContents.delete(skillName);
      this.activeSkills.delete(skillName);

      // Remove from filesystem
      const userSkillPath = path.join(this.getSkillsDir(), 'user', skillName);
      if (fs.existsSync(userSkillPath)) {
        fs.rmSync(userSkillPath, { recursive: true, force: true });
      }

      logger.info(`Skill ${skillName} removed`);
      return true;
    } catch (error) {
      logger.error(`Failed to remove skill ${skillName}: ${error}`);
      return false;
    }
  }

  /**
   * Get skills as system prompt additions
   */
  getSystemPromptAdditions(): string {
    const activeSkills = this.getActiveSkills();
    
    if (activeSkills.length === 0) {
      return '';
    }

    const additions = activeSkills.map(skill => {
      const content = this.skillContents.get(skill.name) || '';
      // Extract content after the metadata
      const contentAfterMetadata = content.split('---')[2] || '';
      return `SKILL: ${skill.name}\n${contentAfterMetadata.trim()}`;
    });

    return '\n\n' + additions.join('\n\n');
  }
}

// Singleton instance
export const skillsManager = new SkillsManager();

/**
 * Initialize skills
 */
export async function initializeSkills() {
  await skillsManager.loadAll();
  logger.info(`Loaded ${skillsManager.getLoadedSkillNames().length} skills`);
}
