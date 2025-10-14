#!/usr/bin/env node

/**
 * Documentation Smoke Test
 * 
 * Quick smoke tests to ensure documentation is accessible and valid.
 * This is a lightweight test that can be run as part of the test suite.
 * 
 * Usage: node test/docs-smoke.js
 */

const fs = require('fs');
const path = require('path');
const assert = require('assert');

// Test configuration
const DOCS_DIR = path.join(__dirname, '..', 'docs');

// Test utilities
let testCount = 0;
let passCount = 0;
let failCount = 0;

function test(description, testFn) {
    testCount++;
    try {
        testFn();
        passCount++;
        console.log(`✓ ${description}`);
    } catch (error) {
        failCount++;
        console.error(`✗ ${description}`);
        console.error(`  ${error.message}`);
    }
}

function fileExists(filePath, description) {
    assert(fs.existsSync(filePath), `File not found: ${description || filePath}`);
}

function fileContains(filePath, searchString, description) {
    assert(fs.existsSync(filePath), `File not found: ${filePath}`);
    const content = fs.readFileSync(filePath, 'utf8');
    assert(content.includes(searchString), 
           `File does not contain expected content: ${description || searchString}`);
}

// Smoke Tests
console.log('\n🔥 Running Documentation Smoke Tests\n');

// Test 1: Critical files exist
test('AI_INSTRUCTIONS.md exists', () => {
    fileExists(path.join(DOCS_DIR, 'AI_INSTRUCTIONS.md'));
});

test('project-rules.md exists', () => {
    fileExists(path.join(DOCS_DIR, 'project-rules.md'));
});

test('general-guidelines.md exists', () => {
    fileExists(path.join(DOCS_DIR, 'general-guidelines.md'));
});

test('index.md exists', () => {
    fileExists(path.join(DOCS_DIR, 'index.md'));
});

// Test 2: AI_INSTRUCTIONS.md content
test('AI_INSTRUCTIONS.md contains mandatory protocol', () => {
    const filePath = path.join(DOCS_DIR, 'AI_INSTRUCTIONS.md');
    fileContains(filePath, 'Mandatory Reading Protocol');
    fileContains(filePath, 'Step-by-Step Enforcement Process');
    fileContains(filePath, 'Priority order');
});

test('AI_INSTRUCTIONS.md references all key documentation', () => {
    const filePath = path.join(DOCS_DIR, 'AI_INSTRUCTIONS.md');
    fileContains(filePath, 'project-rules.md');
    fileContains(filePath, 'general-guidelines.md');
    fileContains(filePath, 'backend-rules.md');
    fileContains(filePath, 'frontend-rules.md');
});

// Test 3: Module documentation exists
test('Backend module documentation exists', () => {
    fileExists(path.join(DOCS_DIR, 'modules/backend/backend-rules.md'));
    fileExists(path.join(DOCS_DIR, 'modules/backend/backend-memories.md'));
    fileExists(path.join(DOCS_DIR, 'modules/backend/backend-checklist.md'));
});

test('Frontend module documentation exists', () => {
    fileExists(path.join(DOCS_DIR, 'modules/frontend/frontend-rules.md'));
    fileExists(path.join(DOCS_DIR, 'modules/frontend/frontend-memories.md'));
    fileExists(path.join(DOCS_DIR, 'modules/frontend/frontend-checklist.md'));
});

test('Testing module documentation exists', () => {
    fileExists(path.join(DOCS_DIR, 'modules/testing/testing-rules.md'));
    fileExists(path.join(DOCS_DIR, 'modules/testing/testing-memories.md'));
    fileExists(path.join(DOCS_DIR, 'modules/testing/testing-checklist.md'));
});

test('Legacy scripts module documentation exists', () => {
    fileExists(path.join(DOCS_DIR, 'modules/legacy-scripts/legacy-scripts-rules.md'));
    fileExists(path.join(DOCS_DIR, 'modules/legacy-scripts/legacy-scripts-memories.md'));
    fileExists(path.join(DOCS_DIR, 'modules/legacy-scripts/legacy-scripts-checklist.md'));
});

// Test 4: Infrastructure documentation exists
test('Configuration documentation exists', () => {
    fileExists(path.join(DOCS_DIR, 'infra/config-rules.md'));
    fileExists(path.join(DOCS_DIR, 'infra/config-checklist.md'));
});

test('Deployment documentation exists', () => {
    fileExists(path.join(DOCS_DIR, 'infra/deployment-rules.md'));
    fileExists(path.join(DOCS_DIR, 'infra/deployment-memories.md'));
    fileExists(path.join(DOCS_DIR, 'infra/deployment-checklist.md'));
});

// Test 5: AI assistant headers
test('Backend rules has AI instruction header', () => {
    const filePath = path.join(DOCS_DIR, 'modules/backend/backend-rules.md');
    const content = fs.readFileSync(filePath, 'utf8');
    assert(content.startsWith('<!-- AI ASSISTANT INSTRUCTION:'), 
           'File should start with AI instruction header');
});

test('Frontend rules has AI instruction header', () => {
    const filePath = path.join(DOCS_DIR, 'modules/frontend/frontend-rules.md');
    const content = fs.readFileSync(filePath, 'utf8');
    assert(content.startsWith('<!-- AI ASSISTANT INSTRUCTION:'), 
           'File should start with AI instruction header');
});

test('Testing rules has AI instruction header', () => {
    const filePath = path.join(DOCS_DIR, 'modules/testing/testing-rules.md');
    const content = fs.readFileSync(filePath, 'utf8');
    assert(content.startsWith('<!-- AI ASSISTANT INSTRUCTION:'), 
           'File should start with AI instruction header');
});

// Test 6: Documentation structure
test('Documentation has proper directory structure', () => {
    assert(fs.existsSync(path.join(DOCS_DIR, 'modules')), 'modules directory exists');
    assert(fs.existsSync(path.join(DOCS_DIR, 'modules/backend')), 'backend directory exists');
    assert(fs.existsSync(path.join(DOCS_DIR, 'modules/frontend')), 'frontend directory exists');
    assert(fs.existsSync(path.join(DOCS_DIR, 'modules/testing')), 'testing directory exists');
    assert(fs.existsSync(path.join(DOCS_DIR, 'modules/legacy-scripts')), 'legacy-scripts directory exists');
    assert(fs.existsSync(path.join(DOCS_DIR, 'infra')), 'infra directory exists');
});

test('Index file contains navigation links', () => {
    const filePath = path.join(DOCS_DIR, 'index.md');
    fileContains(filePath, 'AI_INSTRUCTIONS.md');
    fileContains(filePath, 'Backend Module');
    fileContains(filePath, 'Frontend Module');
    fileContains(filePath, 'Testing Module');
});

// Test 7: General guidelines content
test('General guidelines has security section', () => {
    const filePath = path.join(DOCS_DIR, 'general-guidelines.md');
    fileContains(filePath, 'Security Guidelines');
    fileContains(filePath, 'Input Validation');
});

test('General guidelines has code quality section', () => {
    const filePath = path.join(DOCS_DIR, 'general-guidelines.md');
    fileContains(filePath, 'Code Quality Standards');
    fileContains(filePath, 'Development Guidelines');
});

// Test 8: Project rules content
test('Project rules has security requirements', () => {
    const filePath = path.join(DOCS_DIR, 'project-rules.md');
    fileContains(filePath, 'shell=True');
    fileContains(filePath, 'secure_network_tools.py');
});

test('Project rules has testing requirements', () => {
    const filePath = path.join(DOCS_DIR, 'project-rules.md');
    fileContains(filePath, 'security tests');
    fileContains(filePath, 'tests');
});

// Summary
console.log('\n' + '='.repeat(60));
console.log(`Total tests: ${testCount}`);
console.log(`Passed: ${passCount}`);
console.log(`Failed: ${failCount}`);
console.log('='.repeat(60));

if (failCount === 0) {
    console.log('\n✅ All smoke tests passed!\n');
    process.exit(0);
} else {
    console.log('\n❌ Some smoke tests failed!\n');
    process.exit(1);
}
