# MCP Prompt Templates for CYBER-MATRIX v8.0

## 🎯 Purpose

This file contains ready-to-use prompt templates that leverage MCP servers for common development tasks in CYBER-MATRIX v8.0. Copy and customize these prompts to accelerate your workflow.

---

## 📚 Documentation-Driven Development

### Template 1: Start New Feature

```
I need to add a new [FEATURE_NAME]. 

Please use filesystem MCP to:
1. Read docs/AI_INSTRUCTIONS.md
2. Read docs/modules/[MODULE]/[MODULE]-rules.md
3. Search the codebase for similar implementations

Then use sequential-thinking MCP to plan the implementation with security in mind.

Feature requirements:
- [Requirement 1]
- [Requirement 2]
- [Requirement 3]

Module: [backend/frontend/testing/infra]
```

**Example Usage**:
```
I need to add a new network statistics API endpoint.

Please use filesystem MCP to:
1. Read docs/AI_INSTRUCTIONS.md
2. Read docs/modules/backend/backend-rules.md
3. Search the codebase for similar implementations

Then use sequential-thinking MCP to plan the implementation with security in mind.

Feature requirements:
- Track packet counts per interface
- Calculate bandwidth utilization
- Store historical data in database
- Expose via /api/network/statistics endpoint

Module: backend
```

---

### Template 2: Fix Bug Securely

```
I have a bug: [BUG_DESCRIPTION]

Please use MCP to:
1. Use filesystem MCP to search for [ERROR_PATTERN] in the codebase
2. Use git MCP to check recent changes in [FILE_NAME]
3. Use filesystem MCP to read docs/modules/[MODULE]/[MODULE]-rules.md
4. Use sequential-thinking MCP to plan a secure fix

Requirements:
- Fix must not introduce security vulnerabilities
- Follow project security patterns
- Add test to prevent regression
```

**Example Usage**:
```
I have a bug: Network scan crashes when given invalid IP range

Please use MCP to:
1. Use filesystem MCP to search for "network scan" in the codebase
2. Use git MCP to check recent changes in networks_secure.py
3. Use filesystem MCP to read docs/modules/backend/backend-rules.md
4. Use sequential-thinking MCP to plan a secure fix

Requirements:
- Add input validation using ipaddress module
- Return user-friendly error messages
- Add test case for invalid input
- Log invalid attempts for security audit
```

---

### Template 3: Code Review with Security Focus

```
Please review [FILE_NAME] for security issues.

Use filesystem MCP to:
1. Read the file: [FILE_NAME]
2. Search for dangerous patterns:
   - "shell=True"
   - "eval(" or "exec("
   - "subprocess" without validation
3. Read docs/project-rules.md for security requirements

Then provide:
- List of security issues found
- Suggested fixes following secure patterns
- Code examples for remediation
```

**Example Usage**:
```
Please review app.py for security issues.

Use filesystem MCP to:
1. Read the file: app.py
2. Search for dangerous patterns:
   - "shell=True"
   - "eval(" or "exec("
   - "subprocess" without validation
   - Missing @require_api_key decorators
3. Read docs/project-rules.md for security requirements

Then provide:
- List of security issues found
- Suggested fixes following secure patterns from secure_network_tools.py
- Code examples for remediation
```

---

## 🔒 Security-Focused Workflows

### Template 4: Pre-Commit Security Check

```
I'm about to commit changes. Please perform a comprehensive security check.

Use MCP to:
1. Use git MCP: git status - show all changed files
2. Use git MCP: git diff - show all modifications
3. Use filesystem MCP: Search changed files for:
   - "shell=True"
   - "subprocess" usage
   - "eval(" or "exec("
   - Missing authentication decorators
   - Hardcoded credentials
4. Read docs/modules/backend/backend-checklist.md
5. Verify all checklist items are satisfied

Then tell me:
- Is it safe to commit? (Yes/No)
- List any security issues found
- Checklist items that need attention
```

---

### Template 5: Validate Secure Module Usage

```
Please verify that [FILE_NAME] uses only secure modules.

Use filesystem MCP to:
1. Read [FILE_NAME]
2. Check imports - should import from:
   ✅ secure_network_tools.py
   ✅ *_secure.py files
3. Verify LAB_MODE checks for any real network operations
4. Confirm input validation for all user inputs

Report:
- Are secure modules being used correctly?
- Any dangerous imports found?
- Suggested improvements
```

**Example Usage**:
```
Please verify that app.py uses only secure modules for network operations.

Use filesystem MCP to:
1. Read app.py
2. Check imports - should import from:
   ✅ secure_network_tools.py
   ✅ networks_secure.py
   ✅ detect_secure.py
   ❌ networks.py (dangerous)
   ❌ detect.py (dangerous)
3. Verify LAB_MODE checks for any real network operations
4. Confirm input validation for all user inputs

Report:
- Are secure modules being used correctly?
- Any imports from insecure modules?
- Suggested improvements following project patterns
```

---

### Template 6: Input Validation Review

```
Please review input validation for [FUNCTION_NAME] in [FILE_NAME].

Use filesystem MCP to:
1. Read [FILE_NAME] focusing on [FUNCTION_NAME]
2. Read secure_network_tools.py to see validation patterns
3. Search for ipaddress module usage

Check that:
- All user inputs are validated
- IP addresses validated with ipaddress module
- Port numbers checked for valid range (1-65535)
- String inputs sanitized
- Validation errors return appropriate HTTP codes

Provide:
- Current validation status
- Missing validation checks
- Code to add proper validation
```

---

## 🔄 Refactoring Workflows

### Template 7: Migrate to Secure Modules

```
I need to migrate [FILE_NAME] from insecure to secure modules.

Use MCP to:
1. Use filesystem MCP: Read [FILE_NAME]
2. Use filesystem MCP: Read secure_network_tools.py for secure alternatives
3. Use git MCP: Check git log for [FILE_NAME] to understand changes
4. Use sequential-thinking MCP: Plan migration strategy

Create migration plan that:
- Replaces all insecure operations with secure equivalents
- Adds LAB_MODE checks where needed
- Maintains existing functionality
- Adds tests to verify behavior unchanged
```

**Example Usage**:
```
I need to migrate app.py from using networks.py to networks_secure.py.

Use MCP to:
1. Use filesystem MCP: Read app.py
2. Use filesystem MCP: Read networks_secure.py for secure alternatives
3. Use filesystem MCP: Read secure_network_tools.py for patterns
4. Use sequential-thinking MCP: Plan migration strategy

Create migration plan that:
- Replaces all imports from networks.py with networks_secure.py
- Updates function calls to use secure variants
- Adds LAB_MODE environment check
- Maintains existing API contracts
- Adds tests to verify behavior unchanged
```

---

### Template 8: Add Authentication to Endpoint

```
Please add authentication to [ENDPOINT_PATH] in [FILE_NAME].

Use filesystem MCP to:
1. Read [FILE_NAME]
2. Search for "@require_api_key" to find authentication pattern
3. Read docs/modules/backend/backend-rules.md for auth requirements

Implement:
- Add @require_api_key decorator
- Add rate limiting (appropriate limit for endpoint type)
- Add audit logging
- Test authentication with curl commands
- Update API documentation
```

---

## 📊 Analysis and Investigation

### Template 9: Understand Code Pattern

```
Help me understand how [FEATURE] works in this project.

Use filesystem MCP to:
1. Search for "[FEATURE]" across all files
2. Read relevant files that implement this feature
3. Read docs/modules/[MODULE]/[MODULE]-memories.md for context
4. Show git log for files involved

Explain:
- How the feature is currently implemented
- Key files and functions involved
- Security considerations
- Any patterns I should follow for similar features
```

**Example Usage**:
```
Help me understand how network scanning works in this project.

Use filesystem MCP to:
1. Search for "network scan" across all files
2. Read networks_secure.py and secure_network_tools.py
3. Read docs/modules/backend/backend-memories.md for context
4. Show relevant sections of app.py

Explain:
- How network scanning is currently implemented
- Secure vs insecure module differences
- Security considerations and validation
- Pattern I should follow for adding new scan types
```

---

### Template 10: Database Schema Investigation

```
Help me understand the database schema for [TABLE_NAME].

Use MCP to:
1. Use sqlite MCP: list_tables in cyber_matrix.db
2. Use sqlite MCP: describe_table [TABLE_NAME]
3. Use sqlite MCP: query sample data
4. Use filesystem MCP: Search for [TABLE_NAME] usage in code

Provide:
- Table structure and columns
- Example data
- How it's used in the application
- Related tables and relationships
```

**Example Usage**:
```
Help me understand the database schema for the scans table.

Use MCP to:
1. Use sqlite MCP: list_tables in cyber_matrix.db
2. Use sqlite MCP: describe_table scans
3. Use sqlite MCP: query SELECT * FROM scans LIMIT 5
4. Use filesystem MCP: Search for "scans" table usage in code

Provide:
- Table structure and columns
- Example data showing different scan types
- How scan results are stored and retrieved
- Related tables (logs, devices, etc.)
```

---

## 🎨 Frontend Development

### Template 11: Add New UI Component

```
I need to add a new UI component for [COMPONENT_NAME] to kamkrk_v2.html.

Use filesystem MCP to:
1. Read kamkrk_v2.html
2. Read docs/modules/frontend/frontend-rules.md
3. Search for similar UI patterns in kamkrk_v2.html

Requirements:
- Follow cyberpunk design system (purple/blue/cyan colors)
- Use Tailwind CSS classes
- Connect to API endpoint: [ENDPOINT]
- Handle errors gracefully
- Show loading states
- Update real-time (no mock data)

Provide:
- HTML structure following project patterns
- JavaScript for API integration
- Error handling code
- CSS/Tailwind classes for styling
```

---

### Template 12: Fix Frontend-Backend Integration

```
The frontend component [COMPONENT] isn't connecting to backend properly.

Use MCP to:
1. Use filesystem MCP: Read kamkrk_v2.html, focus on [COMPONENT]
2. Use filesystem MCP: Read app.py, find relevant endpoint
3. Use browser dev tools to check network requests
4. Use sequential-thinking MCP: Debug the integration

Check:
- API endpoint path matches between frontend and backend
- Request/response format matches
- Authentication headers included
- CORS configured correctly
- Error handling on both sides

Provide:
- Root cause of integration issue
- Fix for frontend code
- Fix for backend code (if needed)
- Test commands to verify fix
```

---

## 🧪 Testing Workflows

### Template 13: Add Comprehensive Tests

```
I need comprehensive tests for [FUNCTION_NAME] in [FILE_NAME].

Use filesystem MCP to:
1. Read [FILE_NAME] to understand the function
2. Read test_security.py to see test patterns
3. Read docs/modules/testing/testing-rules.md

Create tests for:
- Valid inputs (happy path)
- Invalid inputs (should raise errors)
- Edge cases
- Security constraints
- Integration with other components

Provide:
- Test class with all test methods
- Mock objects if needed
- Test data fixtures
- Instructions to run tests
```

---

### Template 14: Debug Failing Test

```
The test [TEST_NAME] is failing. Help me fix it.

Use MCP to:
1. Use filesystem MCP: Read test_security.py, find [TEST_NAME]
2. Use filesystem MCP: Read the file being tested
3. Use sequential-thinking MCP: Analyze why it's failing
4. Use git MCP: Check if recent changes broke it

Provide:
- Root cause of failure
- Fix for test or code (whichever is wrong)
- Explanation of what was wrong
- Prevention strategy for similar issues
```

---

## 🚀 Deployment Workflows

### Template 15: Review Deployment Configuration

```
Please review deployment configuration for security.

Use filesystem MCP to:
1. Read start.sh
2. Read auto-install.sh
3. Read requirements.txt
4. Read docs/infra/deployment-rules.md

Check:
- DEBUG=False in production scripts
- FLASK_HOST=127.0.0.1 (not 0.0.0.0)
- LAB_MODE=false by default
- Secure dependency versions
- Proper error handling in scripts
- Startup security checks included

Report:
- Security issues found
- Configuration improvements needed
- Fixes for each issue
```

---

### Template 16: Environment Variable Audit

```
Please audit environment variables for security.

Use filesystem MCP to:
1. Search for "os.environ" across all Python files
2. Search for "getenv" across all Python files
3. Read docs/infra/config-rules.md
4. Check for hardcoded secrets

Report:
- All environment variables used
- Any hardcoded secrets found
- Missing validation for env vars
- Recommended .env file structure
- Security improvements
```

---

## 🔍 Code Quality Workflows

### Template 17: Improve Code Quality

```
Please review [FILE_NAME] for code quality improvements.

Use filesystem MCP to:
1. Read [FILE_NAME]
2. Read docs/project-rules.md for coding standards
3. Search for similar patterns in codebase

Check for:
- PEP 8 compliance
- Function documentation
- Complex code that needs comments
- Repeated code that could be DRY'd up
- Error handling completeness
- Logging adequacy

Provide:
- Code quality score (1-10)
- Specific improvements needed
- Refactored code examples
```

---

### Template 18: Add Comprehensive Documentation

```
Please add comprehensive documentation to [FILE_NAME].

Use filesystem MCP to:
1. Read [FILE_NAME]
2. Read docs/documentation-rules.md
3. Find well-documented examples in codebase

Add:
- Module docstring
- Function docstrings with:
  - Description
  - Args with types
  - Returns with type
  - Raises with exception types
  - Usage examples
- Inline comments for complex logic
- Type hints

Format following Google or NumPy docstring style.
```

---

## 📈 Performance Optimization

### Template 19: Performance Analysis

```
Please analyze performance of [FUNCTION_NAME] in [FILE_NAME].

Use MCP to:
1. Use filesystem MCP: Read [FILE_NAME]
2. Use sequential-thinking MCP: Analyze algorithmic complexity
3. Use sqlite MCP: Check for database query efficiency

Analyze:
- Time complexity
- Space complexity
- Database query efficiency
- Network operations overhead
- Potential bottlenecks

Provide:
- Performance assessment
- Optimization opportunities
- Refactored code with improvements
- Expected performance gains
```

---

## 🎓 Learning Workflows

### Template 20: Explain Project Architecture

```
I'm new to this project. Help me understand the architecture.

Use filesystem MCP to:
1. Read .mcp/PROJECT_KNOWLEDGE_BASE.md
2. Read README.md
3. Read PRD.md
4. List directory structure

Explain:
- High-level architecture (frontend, backend, database)
- Key files and their purposes
- Security model (secure vs insecure modules)
- Development workflow
- How to run the project
- Where to find documentation

Create a learning path for me to follow.
```

---

## 🔧 Advanced Workflows

### Template 21: Complex Refactoring Plan

```
I need to refactor [COMPONENT] to [DESIRED_STATE].

Use MCP to:
1. Use filesystem MCP: Read all files in [COMPONENT]
2. Use git MCP: Check history of changes
3. Use sequential-thinking MCP: Create detailed refactoring plan
4. Use memory MCP: Remember refactoring decisions

Create plan with:
- Current state analysis
- Desired state specification
- Step-by-step migration path
- Risk assessment
- Rollback strategy
- Testing strategy
- Estimated effort

Then execute plan incrementally with validation at each step.
```

---

### Template 22: Multi-Module Feature

```
I need to add [FEATURE] that touches backend, frontend, and database.

Use MCP to:
1. Use filesystem MCP: Read relevant documentation
   - docs/modules/backend/backend-rules.md
   - docs/modules/frontend/frontend-rules.md
   - docs/project-rules.md
2. Use sequential-thinking MCP: Plan cross-module implementation
3. Use memory MCP: Track dependencies between modules
4. Use sqlite MCP: Design database changes

Create implementation plan:
- Database schema changes
- Backend API implementation
- Frontend UI implementation
- Testing strategy for each layer
- Integration testing approach
- Deployment considerations

Execute plan module by module with testing after each.
```

---

## 🎯 Quick Command Snippets

### Documentation Commands

```
Read project rules:
filesystem MCP: read_file("docs/project-rules.md")

Read AI instructions:
filesystem MCP: read_file("docs/AI_INSTRUCTIONS.md")

Read backend rules:
filesystem MCP: read_file("docs/modules/backend/backend-rules.md")

Read knowledge base:
filesystem MCP: read_file(".mcp/PROJECT_KNOWLEDGE_BASE.md")
```

### Security Commands

```
Search for shell=True:
filesystem MCP: search_files("shell=True", "**/*.py")

Search for eval/exec:
filesystem MCP: search_files("eval\\(|exec\\(", "**/*.py")

Check authentication:
filesystem MCP: search_files("@require_api_key", "**/*.py")

Find subprocess usage:
filesystem MCP: search_files("subprocess\\.", "**/*.py")
```

### Git Commands

```
Check status:
git MCP: git_status()

Review changes:
git MCP: git_diff()

Check history:
git MCP: git_log(limit=10)

Show specific commit:
git MCP: git_show(commit_hash)
```

### Database Commands

```
List tables:
sqlite MCP: list_tables()

Describe table:
sqlite MCP: describe_table("scans")

Query data:
sqlite MCP: query("SELECT * FROM scans ORDER BY timestamp DESC LIMIT 10")

Check table size:
sqlite MCP: query("SELECT COUNT(*) FROM scans")
```

---

## 💡 Tips for Using Templates

### Customization

1. Replace `[PLACEHOLDERS]` with your specific values
2. Add/remove MCP operations based on your needs
3. Adjust requirements to match your specific case
4. Combine multiple templates for complex tasks

### Best Practices

1. **Always start with documentation reads** - Use filesystem MCP to understand context
2. **Use sequential-thinking for complex tasks** - Plan before implementing
3. **Use memory for cross-session consistency** - Remember decisions and patterns
4. **Verify with git diff** - Review all changes before committing
5. **Run tests after changes** - python3 test_security.py

### Chaining Templates

You can chain templates together for complex workflows:

```
1. Use Template 20 (Explain Architecture) to understand project
2. Use Template 1 (Start New Feature) to plan implementation
3. Use Template 13 (Add Tests) to ensure quality
4. Use Template 4 (Pre-Commit Check) to verify security
5. Use Template 6 (Deployment Review) before releasing
```

---

## 🚀 Next Steps

After using these templates:

1. **Customize for your needs** - Save frequently used variants
2. **Share with team** - Create team-specific templates
3. **Update regularly** - Add new templates as patterns emerge
4. **Contribute back** - Submit useful templates to the project

---

**These templates are designed to maximize the value of MCP servers.**

**Use them to accelerate development while maintaining security and quality.**

**Customize freely, but always prioritize security and follow project rules.**
