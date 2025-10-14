# MCP Integration with Documentation System

## Overview

This document explains how MCP servers integrate with the CYBER-MATRIX v8.0 documentation system to ensure AI assistants follow project standards.

---

## 🔗 Documentation-First Workflow

When MCP servers are active, the AI assistant can automatically:

1. **Read documentation before making changes**
2. **Verify compliance with project rules**
3. **Check module-specific guidelines**
4. **Validate security requirements**
5. **Run documentation validation**

---

## 🎯 Automatic Documentation Enforcement

### Standard Workflow Integration

When you ask the AI to make changes, it should:

```
User: "Add a new API endpoint for network statistics"

AI Internal Process:
1. Use filesystem MCP to read docs/AI_INSTRUCTIONS.md
2. Identify affected module: Backend
3. Read docs/modules/backend/backend-rules.md
4. Read docs/modules/backend/backend-checklist.md
5. Plan implementation following rules
6. Use sequential-thinking to break down task
7. Remember key decisions with memory server
8. Implement changes
9. Verify against checklist
```

---

## 📚 MCP Commands for Documentation

### Essential Documentation Commands

**Before any code change:**
```
Read docs/AI_INSTRUCTIONS.md and confirm the enforcement protocol
```

**For backend changes:**
```
Read docs/modules/backend/backend-rules.md and list all security requirements
```

**For frontend changes:**
```
Read docs/modules/frontend/frontend-rules.md and verify UI standards
```

**For testing:**
```
Read docs/modules/testing/testing-rules.md and confirm test requirements
```

**Global rules:**
```
Read docs/project-rules.md and list all mandatory requirements
```

---

## 🔄 Workflow Templates

### Template 1: Adding New Feature

```
Step 1: Documentation Review
- Read docs/AI_INSTRUCTIONS.md
- Read relevant module documentation
- Use memory to store key requirements

Step 2: Planning
- Use sequential-thinking to plan implementation
- Search codebase for similar patterns
- Verify against project rules

Step 3: Implementation
- Follow documented standards
- Use secure_network_tools.py for system commands
- Add tests for new functionality

Step 4: Validation
- Run documentation validation
- Run security tests
- Check against module checklist
```

### Template 2: Refactoring Code

```
Step 1: Understand Current State
- Read affected files
- Check git history for context
- Review module documentation

Step 2: Plan Changes
- Use sequential-thinking for refactoring plan
- Remember refactoring decisions
- Verify against security guidelines

Step 3: Execute Refactoring
- Follow project rules
- Maintain documentation alignment
- Update docs if needed

Step 4: Verify
- Run tests
- Validate documentation
- Check git diff
```

### Template 3: Fixing Security Issue

```
Step 1: Analyze Issue
- Search for security vulnerability pattern
- Check git log for how it was introduced
- Review security documentation

Step 2: Plan Fix
- Read security guidelines
- Use sequential-thinking to plan fix
- Search for secure alternatives

Step 3: Implement Fix
- Apply secure coding patterns
- Update affected files
- Add security tests

Step 4: Validate
- Run security_validation.py
- Run test_security.py
- Update SECURITY_REPORT.md if needed
```

---

## 🤖 AI Assistant Prompts

### Comprehensive Project Understanding

```
Use MCP to:
1. Read docs/AI_INSTRUCTIONS.md
2. Read docs/project-rules.md
3. Read docs/project-memories.md
4. Remember all key facts about this project
5. Summarize the mandatory protocol for code changes
```

### Pre-Change Verification

```
Before modifying [filename]:
1. Read relevant module documentation
2. Search for similar code patterns
3. Verify against security guidelines
4. List all requirements that must be followed
```

### Post-Change Validation

```
After making changes:
1. Show git diff for modified files
2. Run node scripts/validate-docs.js if docs changed
3. Run python3 test_security.py if code changed
4. Verify changes against module checklist
```

---

## 📋 Integration Checklist

### Setup Integration

- [ ] MCP servers installed
- [ ] Documentation system in place
- [ ] Memory server configured
- [ ] Filesystem server has access to docs/
- [ ] Git server connected to repository

### Verify Integration

- [ ] AI can read docs/AI_INSTRUCTIONS.md
- [ ] AI can search documentation files
- [ ] AI can remember project rules
- [ ] AI can use sequential thinking for planning
- [ ] AI references docs before changes

### Test Integration

- [ ] Ask AI to read project rules
- [ ] Ask AI to plan a feature following docs
- [ ] Ask AI to verify changes against checklist
- [ ] Confirm AI remembers project context

---

## 🎓 Training the AI Assistant

### Initial Context Loading

When starting a new session, run:

```
Please use MCP to:

1. Read and understand docs/AI_INSTRUCTIONS.md
   This file contains the mandatory protocol you must follow.

2. Read docs/project-rules.md
   These are global rules that always apply.

3. Read docs/general-guidelines.md
   These are fallback guidelines for undefined cases.

4. Remember key facts from docs/project-memories.md
   Store important project context.

5. Summarize the enforcement protocol
   Confirm you understand the priority order.
```

### Ongoing Context Maintenance

Throughout the session:

```
Remember: [important decision or pattern]

Example:
- Remember: All API endpoints must use @require_api_key decorator
- Remember: Network operations use secure_network_tools.py
- Remember: Tests must pass before committing
```

### Session Continuity

In future sessions:

```
What do you remember about:
- Security requirements
- API endpoint patterns
- Testing procedures
- Documentation rules
```

---

## 🔐 Security Integration

### Security-First Prompts

**Before implementing security-sensitive code:**
```
1. Read docs/modules/backend/backend-rules.md
2. Search codebase for "shell=True"
3. Verify secure_network_tools.py usage
4. List all security requirements
5. Use sequential thinking to plan secure implementation
```

**After implementing:**
```
1. Run python3 security_validation.py
2. Search for potential security issues
3. Verify against security checklist
4. Check if SECURITY_REPORT.md needs update
```

---

## 📊 Monitoring Compliance

### Compliance Checks

**Daily:**
```
1. Review git log for recent changes
2. Verify all changes followed documentation
3. Run validation scripts
4. Check for security violations
```

**Before PR/Release:**
```
1. Run complete test suite
2. Validate all documentation
3. Verify security requirements
4. Check documentation is up to date
```

---

## 🚀 Advanced Integration

### Custom MCP Workflows

**Documentation-Aware Code Generation:**
```javascript
// Pseudo-code for custom MCP workflow
async function generateCode(feature) {
  // Read documentation
  const rules = await mcp.filesystem.read('docs/project-rules.md');
  const moduleRules = await mcp.filesystem.read(`docs/modules/${module}/rules.md`);
  
  // Plan with sequential thinking
  const plan = await mcp.sequentialThinking.create({
    task: `Implement ${feature}`,
    constraints: [rules, moduleRules]
  });
  
  // Remember decisions
  await mcp.memory.create({
    context: feature,
    decisions: plan.decisions
  });
  
  // Generate code following plan
  return generateFromPlan(plan);
}
```

### Automated Documentation Updates

```
When code changes affect documentation:
1. Detect affected documentation files
2. Read current documentation
3. Generate updated documentation
4. Run validation
5. Ask for user review
```

---

## 📈 Measuring Effectiveness

### Metrics to Track

- **Documentation reads per code change** (should be ≥1)
- **Rule violations detected** (should decrease over time)
- **Test failures** (should decrease over time)
- **Security issues** (should approach zero)
- **Documentation drift** (should stay minimal)

### Success Indicators

✅ AI consistently reads docs before changes
✅ All code follows documented standards
✅ Security requirements never violated
✅ Tests pass on first attempt
✅ Documentation stays synchronized

---

## 🛠️ Troubleshooting Integration

### AI Not Reading Documentation

**Symptoms:**
- Changes don't follow project rules
- Security standards ignored
- Documentation not referenced

**Solutions:**
1. Explicitly prompt: "Read docs/AI_INSTRUCTIONS.md first"
2. Verify filesystem MCP server is active
3. Check file paths are correct
4. Restart IDE and reload servers

### AI Forgetting Context

**Symptoms:**
- Repeating same questions
- Not remembering decisions
- Ignoring previous guidance

**Solutions:**
1. Use memory server explicitly: "Remember this..."
2. Check .mcp/memory/ directory exists
3. Verify memory server is active
4. Store important context explicitly

### Documentation Conflicts

**Symptoms:**
- AI confused about priorities
- Conflicting instructions
- Unclear which rule applies

**Solutions:**
1. Reference priority order in AI_INSTRUCTIONS.md
2. Use specific file names in prompts
3. Make priority explicit: "Follow project-rules.md first"
4. Resolve conflicts in documentation

---

## 🎯 Best Practices

### For Users

1. **Always start with documentation**
   - Ask AI to read relevant docs first
   - Explicitly reference rule files
   - Confirm AI understands requirements

2. **Use memory effectively**
   - Store important decisions
   - Reference stored memories
   - Keep context across sessions

3. **Validate changes**
   - Run validation scripts
   - Check against checklists
   - Review git diff before committing

### For AI Assistants

1. **Documentation-first approach**
   - Read docs before any change
   - Follow priority order
   - Reference specific rules

2. **Context awareness**
   - Use memory to persist context
   - Reference project patterns
   - Follow established conventions

3. **Validation-driven**
   - Run tests after changes
   - Validate documentation
   - Check security requirements

---

## 📞 Support

If integration issues persist:

1. Check `.mcp/setup-guide.md` for configuration
2. Run `.mcp/verify-mcp.sh` to diagnose issues
3. Review `.mcp/test-mcp-servers.md` for testing
4. Verify documentation system with `node scripts/validate-docs.js`

---

*Integration Guide v1.0 - Ensures documentation control is absolute*
