# Kutti Skills Guide

This document explains how to create and use skills in Kutti. Skills are markdown files that teach Kutti how to approach specific tasks by shaping its system prompt.

## Overview

Skills are a powerful way to customize Kutti's behavior without writing code. They allow you to:

- **Teach Kutti** about specific domains or workflows
- **Shape its reasoning** by providing context and guidelines
- **Improve output quality** by setting expectations
- **Auto-load relevant knowledge** based on the task

## How Skills Work

When Kutti processes a prompt:

1. It loads all **always-loaded** skills (from config)
2. It detects the task type and loads **relevant skills** (based on triggers)
3. It appends the skill content to its **system prompt**
4. The LLM uses this enhanced context to generate better responses

```
User Prompt: "Create a new Android activity"
    │
    ▼
Detect triggers: ["android", "activity"]
    │
    ▼
Load matching skills: ["android-dev", "kutti-core"]
    │
    ▼
Build system prompt: 
  - Core instructions
  - Android development guidelines
  - Kotlin best practices
  - Jetpack Compose patterns
    │
    ▼
LLM generates response with enhanced context
```

## Skill Structure

A skill is a directory containing a `SKILL.md` file:

```
my-skill/
└── SKILL.md              # Skill definition
```

The `SKILL.md` file has two parts:

1. **Frontmatter (YAML)**: Metadata about the skill
2. **Content (Markdown)**: The actual skill content

### Example Skill:

```markdown
---
name: android-dev
description: >
  Android development skill for Kutti. Use this for any Android development task
  including Kotlin, Java, Gradle, AndroidManifest, Jetpack Compose, and ADB.
triggers:
  - android
  - kotlin
  - java
  - gradle
  - compose
priority: high
---

# Android Development

You are working inside a Kutti Android project. Always prefer modern Android development practices.

## Language Preferences

- **Kotlin over Java**: Always prefer Kotlin for new code
- **Jetpack Compose for UI**: Use Compose for all new UI development
- **Coroutines + Flow**: Prefer over RxJava or callbacks

## Best Practices

### Architecture
- Use MVVM pattern
- Follow Clean Architecture principles
- Use dependency injection (Hilt)

### Code Quality
- Write unit tests
- Use meaningful names
- Keep functions small
```

## Frontmatter Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Unique identifier for the skill |
| `description` | string | Yes | Human-readable description |
| `triggers` | string[] | No | Keywords that trigger this skill to load |
| `priority` | string | No | Priority level: "low", "medium", or "high" |

### Priority Levels:

- **high**: Always load this skill if triggers match
- **medium**: Load if relevant and not too many skills
- **low**: Load only if very few skills match

## Skill Content

The content after the frontmatter is appended to Kutti's system prompt. Write it as if you're giving instructions to a smart assistant.

### Content Guidelines:

1. **Be Specific**: Provide concrete examples and patterns
2. **Be Concise**: Get to the point quickly
3. **Be Actionable**: Tell Kutti what to do, not just what to know
4. **Use Structure**: Use headings, lists, and code blocks
5. **Prioritize**: Put the most important information first

### What to Include:

✅ **Do Include:**
- Domain-specific knowledge
- Best practices and patterns
- Common pitfalls to avoid
- Preferred tools and libraries
- Code examples
- Decision-making guidelines

❌ **Don't Include:**
- Generic advice (save for kutti-core)
- Outdated information
- Too much detail (keep it focused)
- Personal opinions unrelated to the task

## Built-in Skills

Kutti comes with several built-in skills:

### 1. kutti-core

**Purpose**: Core capabilities and guidelines

**Triggers**: kutti, agent, cli, command

**Priority**: high

**Content**: Fundamental instructions for Kutti, including:
- Core capabilities
- Agent loop behavior
- Tool usage guidelines
- Error handling
- Security considerations

### 2. android-dev

**Purpose**: Android development best practices

**Triggers**: android, kotlin, java, gradle, compose, adb, xml, manifest

**Priority**: high

**Content**: Android-specific guidance, including:
- Language preferences (Kotlin over Java)
- Architecture patterns (MVVM, Clean Architecture)
- UI development (Jetpack Compose)
- Testing strategies
- ADB commands

### 3. python-dev

**Purpose**: Python development guidelines

**Triggers**: python, py, django, flask, fastapi, pandas, numpy, pytest

**Priority**: high

**Content**: Python best practices, including:
- Modern Python features
- Project structure
- Web frameworks (FastAPI, Flask)
- Testing (pytest)
- Code quality tools

### 4. code-review

**Purpose**: Code review checklist and patterns

**Triggers**: review, pr, pull request, commit, code review, quality, lint

**Priority**: high

**Content**: Code review guidance, including:
- Review process
- What to look for
- Common issues
- Feedback structure
- Checklists

## Creating a Skill

### Step 1: Create the Skill Directory

```bash
# Create user skills directory
mkdir -p ~/.kutti/skills/user/my-skill

# Create the skill file
cd ~/.kutti/skills/user/my-skill
touch SKILL.md
```

### Step 2: Write the Skill File

Edit `SKILL.md` with your skill content:

```markdown
---
name: my-skill
description: My custom skill for specific tasks
triggers:
  - my-trigger
  - another-trigger
priority: medium
---

# My Custom Skill

This skill provides guidance for [specific task or domain].

## Key Principles

1. Always do X
2. Never do Y
3. Prefer Z over W

## Examples

### Good Example
```python
def good_function():
    # Well-structured code
    pass
```

### Bad Example
```python
def bad_function():
    # Poorly structured code
    pass
```

## Common Patterns

- Pattern 1: Description
- Pattern 2: Description
- Pattern 3: Description
```

### Step 3: Test the Skill

```bash
# Enable the skill
kutti skills enable my-skill

# Check active skills
kutti skills active

# Test with a matching prompt
kutti "Create a my-trigger implementation"
```

## Skill Management Commands

| Command | Description |
|---------|-------------|
| `kutti skills list` | List all installed skills |
| `kutti skills install <name>` | Install a skill from registry |
| `kutti skills enable <name>` | Enable a skill |
| `kutti skills disable <name>` | Disable a skill |
| `kutti skills active` | Show active skills |
| `kutti skills create` | Create a new skill interactively |
| `kutti skills edit <name>` | Edit a skill |
| `kutti skills remove <name>` | Remove a skill |
| `kutti skills search <query>` | Search for skills by trigger |
| `kutti skills export` | Export skills |

## Skill Auto-Detection

Kutti can automatically load skills based on:

1. **File Types**: Load skills when specific file types are present
2. **Project Structure**: Detect project type and load relevant skills
3. **User Prompts**: Match triggers in user prompts

### Configuration:

```json
// ~/.kutti/config.json
{
  "skills": {
    "autoDetect": true,
    "alwaysLoad": ["kutti-core", "my-skill"],
    "projectSkills": {
      "*.kt": ["android-dev", "kotlin"],
      "*.py": ["python-dev"],
      "Dockerfile": ["docker"],
      "*.rs": ["rust-dev"]
    }
  }
}
```

## Skill Types

### 1. Domain Skills

Focus on a specific domain or technology:

- `android-dev`: Android development
- `python-dev`: Python development
- `web-dev`: Web development
- `data-science`: Data science and analysis
- `devops`: DevOps practices

### 2. Task Skills

Focus on specific tasks:

- `code-review`: Code review guidelines
- `testing`: Testing strategies
- `debugging`: Debugging techniques
- `refactoring`: Code refactoring patterns
- `documentation`: Documentation writing

### 3. Project Skills

Specific to a particular project:

- `my-project-context`: Project-specific patterns
- `my-team-style`: Team coding standards
- `my-api-integration`: API integration guidelines

### 4. Role Skills

For specific roles:

- `tech-lead`: Technical leadership
- `code-reviewer`: Code review expertise
- `architect`: System architecture
- `qa-engineer`: Quality assurance

## Skill Best Practices

### Writing Effective Skills:

1. **Start with a Clear Purpose**: State what the skill is for
2. **Use Concrete Examples**: Show good and bad patterns
3. **Be Specific**: Avoid vague advice
4. **Prioritize Information**: Most important first
5. **Use Consistent Formatting**: Make it easy to read
6. **Keep it Updated**: Remove outdated information

### Example: Good Skill Content

```markdown
# API Design

## REST API Best Practices

### Resource Naming
- Use nouns, not verbs: `/users` not `/getUsers`
- Use plural nouns: `/users` not `/user`
- Use lowercase with hyphens: `/user-profiles` not `/userProfiles`

### HTTP Methods
- GET: Retrieve resources
- POST: Create resources
- PUT: Replace resources
- PATCH: Update resources partially
- DELETE: Remove resources

### Status Codes
- 200 OK: Success
- 201 Created: Resource created
- 400 Bad Request: Client error
- 401 Unauthorized: Authentication failed
- 404 Not Found: Resource not found
- 500 Internal Server Error: Server error

### Example API

```yaml
# Good
GET /users
POST /users
GET /users/{id}
PUT /users/{id}
DELETE /users/{id}

# Bad
GET /getUsers
POST /createUser
GET /getUserById/{id}
POST /updateUser/{id}
POST /deleteUser/{id}
```
```

### Example: Poor Skill Content

```markdown
# API Design

APIs are important. You should design them well.
Use REST. It's good.
Sometimes use GraphQL.
```

## Skill Versioning

Skills can be versioned by including a version in the name:

```
my-skill/
└── SKILL.md              # v1

my-skill-v2/
└── SKILL.md              # v2
```

Or by using git tags if the skill is in a repository.

## Sharing Skills

### With Your Team:

1. **Git Repository**: Store skills in a shared repo
2. **Private npm Package**: Publish as a private package
3. **Shared Directory**: Use a shared network directory

### With the Community:

1. **GitHub**: Publish skills in a public repo
2. **npm**: Publish to the public npm registry
3. **Kutti Registry**: (Future) Official skill registry

### Example: GitHub Skill Installation

```bash
# Clone a skills repository
git clone https://github.com/myorg/kutti-skills.git

# Link to Kutti's skills directory
ln -s ~/kutti-skills/public ~/.kutti/skills/public

# Or install individual skills
kutti skills install gh:myorg/my-skill
```

## Advanced Skill Features

### Conditional Content:

Use markdown comments to include conditional content:

```markdown
<!-- IF provider=groq -->
# Groq-Specific Instructions

When using Groq, prefer these models...
<!-- ENDIF -->
```

*Note: Conditional content requires Kutti v1.1+*

### Skill Dependencies:

Specify that a skill requires another skill:

```yaml
---
name: advanced-android
description: Advanced Android patterns
triggers:
  - android
  - advanced
requires:
  - android-dev
---
```

### Skill Conflicts:

Prevent loading with certain skills:

```yaml
---
name: legacy-android
description: Legacy Android patterns
triggers:
  - android
  - legacy
conflicts:
  - android-dev
---
```

## Skill Testing

Test your skills thoroughly:

1. **Manual Testing**: Try various prompts that should trigger the skill
2. **Trigger Testing**: Verify triggers work correctly
3. **Priority Testing**: Check that high-priority skills load first
4. **Conflict Testing**: Test with conflicting skills
5. **Content Testing**: Verify the content appears in the system prompt

### Test Commands:

```bash
# Check if skill loads
kutti skills active

# Test with a matching prompt
kutti --skill my-skill "Test my skill"

# View the system prompt (debug mode)
KUTTI_DEBUG=true kutti "Test prompt"
```

## Skill Performance

### Optimization Tips:

1. **Keep it Short**: Skills should be concise (aim for < 2000 words)
2. **Use Triggers Wisely**: Don't use too many triggers
3. **Avoid Redundancy**: Don't repeat information from other skills
4. **Use References**: Link to external documentation when possible
5. **Lazy Load**: Use low priority for rarely needed skills

### Performance Impact:

- Each loaded skill adds to the system prompt
- More skills = longer prompts = higher token usage
- Be mindful of the LLM's context window

## Troubleshooting

### Skill Not Loading:

1. Check the skill is in the correct directory
2. Verify the `SKILL.md` file exists
3. Check for syntax errors in the frontmatter
4. Verify triggers match your prompt
5. Check priority settings

### Skill Content Not Appearing:

1. Verify the skill is enabled (`kutti skills active`)
2. Check for errors in the log file (`~/.kutti/kutti.log`)
3. Test with a simple skill to isolate the issue

### Conflicting Skills:

1. Check for skills with overlapping triggers
2. Use priority to control loading order
3. Use conflicts to prevent loading together

## Future Skill Features

Planned enhancements for skills:

1. **Skill Variables**: Dynamic content based on context
2. **Skill Templates**: Reusable skill templates
3. **Skill Inheritance**: Extend existing skills
4. **Skill Validation**: Validate skill content
5. **Skill Marketplace**: Discover and install skills from a registry

## Support

For questions or issues with skills:

1. Check the [Kutti GitHub repository](https://github.com/wsochi4-os/kay)
2. Look at existing skills for examples
3. Open an issue with your question
4. Join the Kutti community discussions

## Changelog

### v1.0.0

- Initial skills system release
- Support for markdown-based skills
- Frontmatter metadata
- Trigger-based auto-loading
- Priority system
- Built-in skills: kutti-core, android-dev, python-dev, code-review
