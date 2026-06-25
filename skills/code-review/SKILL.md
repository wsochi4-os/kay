---
name: code-review
description: >
  Code review skill for Kutti. Use this for reviewing pull requests, commits,
  or any code that needs quality assessment.
triggers:
  - review
  - pr
  - pull request
  - commit
  - code review
  - quality
  - lint
priority: high
---

# Code Review

You are performing a code review. Be thorough, constructive, and helpful. Focus on code quality, maintainability, and correctness.

## Review Process

1. **Understand the Context**: Read the PR description, related issues, and changes
2. **Check Functionality**: Does the code do what it's supposed to do?
3. **Check Code Quality**: Is the code clean, readable, and maintainable?
4. **Check Tests**: Are there adequate tests? Do they pass?
5. **Check Performance**: Are there any obvious performance issues?
6. **Check Security**: Are there any security concerns?
7. **Provide Feedback**: Be specific, actionable, and kind

## What to Look For

### Code Quality
- [ ] Consistent naming conventions
- [ ] Proper error handling
- [ ] Good variable and function names
- [ ] Appropriate comments (not too many, not too few)
- [ ] Consistent code style
- [ ] No duplicated code (DRY principle)
- [ ] Functions are small and focused
- [ ] Classes follow Single Responsibility Principle

### Functionality
- [ ] Code implements the requirements
- [ ] Edge cases are handled
- [ ] Input validation is present
- [ ] Return values are appropriate
- [ ] Side effects are minimized
- [ ] API contracts are respected

### Testing
- [ ] Unit tests cover the new functionality
- [ ] Tests are meaningful (not just testing implementation)
- [ ] Edge cases are tested
- [ ] Tests pass
- [ ] Test coverage is adequate

### Performance
- [ ] No obvious N+1 queries
- [ ] No unnecessary computations
- [ ] Appropriate data structures used
- [ ] No memory leaks
- [ ] Database queries are optimized

### Security
- [ ] No hardcoded secrets or API keys
- [ ] Input is validated and sanitized
- [ ] Authentication/authorization is proper
- [ ] Sensitive data is handled securely
- [ ] No SQL injection vulnerabilities
- [ ] No XSS vulnerabilities

## Review Comments

### Structure Your Feedback

```
## Overall
[General impression of the PR]

## Strengths
- [What's good about this PR]
- [What the author did well]

## Concerns
- [Major issues that need to be addressed]

## Suggestions
- [Minor improvements that would be nice]

## Questions
- [Things you don't understand or need clarification on]
```

### Be Specific

❌ Bad: "This function is too long"
✅ Good: "The `processOrder` function is 80 lines long. Consider breaking it into smaller functions like `validateOrder`, `processPayment`, and `updateInventory`"

❌ Bad: "This is hard to read"
✅ Good: "The nested ternary on line 42 is hard to read. Consider using an if-else statement or extracting to a helper function"

### Be Actionable

❌ Bad: "This could be better"
✅ Good: "Consider using a Set instead of an Array for the `uniqueItems` variable to ensure uniqueness"

### Be Kind

❌ Bad: "Why would you do it this way?"
✅ Good: "I'm curious about the choice to use approach X here. Have you considered approach Y?"

## Common Issues

### Naming
```javascript
// ❌ Bad
function getData(id) { /* ... */ }  // What kind of data?

// ✅ Good
function getUserById(userId) { /* ... */ }
```

### Error Handling
```python
# ❌ Bad
try:
    process_data(data)
except:
    pass  # Silent failure

# ✅ Good
try:
    process_data(data)
except ValueError as e:
    logger.error(f"Invalid data format: {e}")
    raise
```

### Magic Numbers
```javascript
// ❌ Bad
if (status === 2) { /* ... */ }

// ✅ Good
const STATUS_ACTIVE = 2;
if (status === STATUS_ACTIVE) { /* ... */ }
// Or better:
if (status === UserStatus.ACTIVE) { /* ... */ }
```

### Long Functions
```python
# ❌ Bad - 100+ line function
def process_order(order):
    # Validate order
    # Process payment
    # Update inventory
    # Send confirmation
    # Log transaction
    # ...

# ✅ Good - Broken into smaller functions
def process_order(order):
    validate_order(order)
    process_payment(order)
    update_inventory(order)
    send_confirmation(order)
    log_transaction(order)
```

### Comments
```java
// ❌ Bad - Redundant comment
// Increment x by 1
x++;

// ❌ Bad - Outdated comment
// Returns the user's age in years
return user.getAgeInMonths() / 12;

// ✅ Good - Explains why, not what
// We divide by 12 to convert months to years for the age verification
return user.getAgeInMonths() / 12;
```

## Review Checklist

- [ ] **Functionality**: Does the code work as intended?
- [ ] **Tests**: Are there tests? Do they pass?
- [ ] **Naming**: Are names clear and consistent?
- [ ] **Error Handling**: Are errors handled properly?
- [ ] **Edge Cases**: Are edge cases considered?
- [ ] **Performance**: Any obvious performance issues?
- [ ] **Security**: Any security concerns?
- [ ] **Documentation**: Are there appropriate comments/docs?
- [ ] **Style**: Does it follow the project's style guide?
- [ ] **Dependencies**: Are new dependencies appropriate?

## Example Review

```
## Overall
This PR adds a new user authentication endpoint. The implementation looks solid and follows our existing patterns.

## Strengths
- Good use of our existing auth middleware
- Proper error handling with appropriate HTTP status codes
- Input validation is present
- Tests cover the happy path and error cases

## Concerns
- The password hashing algorithm seems weak (MD5). We should use bcrypt or Argon2.
- No rate limiting on the login endpoint. This could be a security concern.

## Suggestions
- Consider adding a `last_login` timestamp to the user model
- The error message for invalid credentials could be more specific
- Consider adding OpenAPI documentation for the new endpoint

## Questions
- Why was MD5 chosen for password hashing?
- Should we add CAPTCHA to prevent brute force attacks?
```

## Final Thoughts

Remember: The goal of code review is to **improve the code**, not to **criticize the author**. Be helpful, be kind, and focus on making the codebase better.
