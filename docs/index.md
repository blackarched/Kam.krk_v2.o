# CYBER-MATRIX v8.0 - Documentation Index

## 🎯 Start Here

**Before making any code changes, read:** [`AI_INSTRUCTIONS.md`](./AI_INSTRUCTIONS.md)

This file contains mandatory protocols that all AI assistants must follow before executing any task.

---

## 📚 Core Documentation

### Essential Files
| File | Description | Priority |
|------|-------------|----------|
| [`AI_INSTRUCTIONS.md`](./AI_INSTRUCTIONS.md) | Mandatory AI assistant enforcement protocol | **CRITICAL** |
| [`project-rules.md`](./project-rules.md) | Global project rules (highest authority) | **HIGH** |
| [`general-guidelines.md`](./general-guidelines.md) | Fallback guidelines for all areas | **MEDIUM** |
| [`CHANGELOG.md`](./CHANGELOG.md) | Documentation integration changelog | **INFO** |

### Project Context
| File | Description |
|------|-------------|
| [`project-memories.md`](./project-memories.md) | Important facts about the project |

### Documentation Guidelines
| File | Description |
|------|-------------|
| [`documentation-rules.md`](./documentation-rules.md) | Rules for maintaining documentation |
| [`documentation-memories.md`](./documentation-memories.md) | Documentation structure information |
| [`documentation-checklist.md`](./documentation-checklist.md) | Documentation verification items |

---

## 🔧 Module-Specific Documentation

### Backend Module
**Location:** `docs/modules/backend/`

| File | Description |
|------|-------------|
| [`backend-rules.md`](./modules/backend/backend-rules.md) | Backend development rules |
| [`backend-memories.md`](./modules/backend/backend-memories.md) | Backend architecture facts |
| [`backend-checklist.md`](./modules/backend/backend-checklist.md) | Backend verification checklist |

**When to use:** Making changes to `app.py`, API endpoints, database operations, or backend logic.

---

### Frontend Module
**Location:** `docs/modules/frontend/`

| File | Description |
|------|-------------|
| [`frontend-rules.md`](./modules/frontend/frontend-rules.md) | Frontend development rules |
| [`frontend-memories.md`](./modules/frontend/frontend-memories.md) | Frontend architecture facts |
| [`frontend-checklist.md`](./modules/frontend/frontend-checklist.md) | Frontend verification checklist |

**When to use:** Making changes to `kamkrk_v2.html`, UI components, charts, or frontend JavaScript.

---

### Testing Module
**Location:** `docs/modules/testing/`

| File | Description |
|------|-------------|
| [`testing-rules.md`](./modules/testing/testing-rules.md) | Testing requirements and rules |
| [`testing-memories.md`](./modules/testing/testing-memories.md) | Testing framework information |
| [`testing-checklist.md`](./modules/testing/testing-checklist.md) | Testing verification checklist |

**When to use:** Writing tests, modifying `test_security.py`, or working with the test suite.

---

### Legacy Scripts Module
**Location:** `docs/modules/legacy-scripts/`

| File | Description |
|------|-------------|
| [`legacy-scripts-rules.md`](./modules/legacy-scripts/legacy-scripts-rules.md) | Rules for handling legacy code |
| [`legacy-scripts-memories.md`](./modules/legacy-scripts/legacy-scripts-memories.md) | Information about insecure legacy scripts |
| [`legacy-scripts-checklist.md`](./modules/legacy-scripts/legacy-scripts-checklist.md) | Legacy code verification checklist |

**When to use:** Dealing with `kamkrk_v2.py`, `detect.py`, `networks.py`, or other legacy files.

---

## 🏗️ Infrastructure Documentation

### Configuration Management
**Location:** `docs/infra/`

| File | Description |
|------|-------------|
| [`config-rules.md`](./infra/config-rules.md) | Configuration management rules |
| [`config-checklist.md`](./infra/config-checklist.md) | Configuration verification checklist |

**When to use:** Modifying `requirements.txt`, managing dependencies, or changing configuration files.

---

### Deployment & Installation
**Location:** `docs/infra/`

| File | Description |
|------|-------------|
| [`deployment-rules.md`](./infra/deployment-rules.md) | Deployment rules and guidelines |
| [`deployment-memories.md`](./infra/deployment-memories.md) | Deployment script information |
| [`deployment-checklist.md`](./infra/deployment-checklist.md) | Deployment verification checklist |

**When to use:** Modifying installation scripts, deployment processes, or system configuration.

---

## 🗺️ Documentation Navigation Guide

### By Task Type

| Task | Primary Documentation | Secondary Documentation |
|------|----------------------|------------------------|
| **Adding a new API endpoint** | `backend-rules.md` | `backend-checklist.md`, `testing-rules.md` |
| **Modifying the UI** | `frontend-rules.md` | `frontend-checklist.md` |
| **Writing tests** | `testing-rules.md` | `testing-checklist.md` |
| **Managing dependencies** | `config-rules.md` | `config-checklist.md` |
| **Deployment changes** | `deployment-rules.md` | `deployment-checklist.md` |
| **Working with legacy code** | `legacy-scripts-rules.md` | `legacy-scripts-checklist.md` |
| **Updating documentation** | `documentation-rules.md` | `documentation-checklist.md` |
| **General/undefined tasks** | `project-rules.md` | `general-guidelines.md` |

---

## 📋 Quick Reference

### Priority Order for Conflicting Instructions
1. **`project-rules.md`** - Highest priority, global rules
2. **Module-specific rules** - Second priority, area-specific rules
3. **`general-guidelines.md`** - Lowest priority, fallback guidelines

### Documentation Types Explained

- **Rules (`*-rules.md`)**: Mandatory requirements and constraints that must be followed
- **Memories (`*-memories.md`)**: Important facts, context, and architecture information
- **Checklists (`*-checklist.md`)**: Verification items to ensure completeness and quality

---

## 🔍 Search Tips

### Finding the Right Documentation

1. **Identify the file or module** you're working on
2. **Find the corresponding category** in this index
3. **Read the rules file first** for that category
4. **Check the memories file** for context
5. **Use the checklist** to verify your work
6. **Fall back to `general-guidelines.md`** if no specific doc exists

### Common Patterns

- Backend work → `docs/modules/backend/`
- Frontend work → `docs/modules/frontend/`
- Testing → `docs/modules/testing/`
- Dependencies → `docs/infra/config-*.md`
- Installation → `docs/infra/deployment-*.md`

---

## 🚀 Getting Started

### For AI Assistants

1. **Read** [`AI_INSTRUCTIONS.md`](./AI_INSTRUCTIONS.md) first
2. **Identify** which module your task involves
3. **Open** the relevant rules, memories, and checklist files
4. **Follow** the instructions precisely
5. **Verify** your work against the checklist

### For Developers

1. **Familiarize yourself** with [`project-rules.md`](./project-rules.md)
2. **Read** [`general-guidelines.md`](./general-guidelines.md)
3. **Explore** module-specific documentation for your area
4. **Reference** this index when switching between modules
5. **Update** documentation when making significant changes

---

## 📝 Documentation Statistics

- **Total documentation files:** 25
- **Module-specific files:** 15
- **Infrastructure files:** 5
- **Core files:** 5
- **Categories:** 6 (Backend, Frontend, Testing, Legacy Scripts, Infrastructure, General)

---

## 🔄 Maintenance

### Keeping This Index Updated

When adding new documentation:
1. Create the file in the appropriate directory
2. Add the AI instruction header
3. Update this index with the new file
4. Update the relevant category section
5. Commit changes together

### Documentation Lifecycle

- **Active**: Currently used and maintained
- **Deprecated**: Marked with redirect stubs
- **Archived**: Moved to `docs/archive/` if needed

---

**Last Updated:** 2025-10-14  
**Version:** 1.0  
**Maintained by:** CYBER-MATRIX Documentation Team
