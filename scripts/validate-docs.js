#!/usr/bin/env node

/**
 * Documentation Validation Script
 * 
 * This script validates that all markdown documentation files:
 * 1. Have the required AI assistant instruction header
 * 2. Don't have broken internal links
 * 3. Are referenced in the documentation index
 * 
 * Usage: node scripts/validate-docs.js
 */

const fs = require('fs');
const path = require('path');

// ANSI color codes for terminal output
const colors = {
    reset: '\x1b[0m',
    bright: '\x1b[1m',
    red: '\x1b[31m',
    green: '\x1b[32m',
    yellow: '\x1b[33m',
    blue: '\x1b[34m',
    cyan: '\x1b[36m'
};

// Required AI assistant header (first line comment)
const REQUIRED_HEADER_START = '<!-- AI ASSISTANT INSTRUCTION:';

// Configuration
const DOCS_DIR = path.join(__dirname, '..', 'docs');
const INDEX_FILE = path.join(DOCS_DIR, 'index.md');
const EXEMPTED_FILES = ['index.md']; // Files that don't need the header (CHANGELOG is a log file)

// Validation results
let errors = [];
let warnings = [];
let checked = 0;

/**
 * Log utilities
 */
function log(message, color = 'reset') {
    console.log(`${colors[color]}${message}${colors.reset}`);
}

function logHeader(message) {
    log(`\n${'='.repeat(60)}`, 'cyan');
    log(`  ${message}`, 'bright');
    log('='.repeat(60), 'cyan');
}

function logSuccess(message) {
    log(`✓ ${message}`, 'green');
}

function logError(message) {
    log(`✗ ${message}`, 'red');
    errors.push(message);
}

function logWarning(message) {
    log(`⚠ ${message}`, 'yellow');
    warnings.push(message);
}

function logInfo(message) {
    log(`ℹ ${message}`, 'blue');
}

/**
 * Get all markdown files recursively
 */
function getMarkdownFiles(dir, fileList = []) {
    const files = fs.readdirSync(dir);
    
    files.forEach(file => {
        const filePath = path.join(dir, file);
        const stat = fs.statSync(filePath);
        
        if (stat.isDirectory()) {
            getMarkdownFiles(filePath, fileList);
        } else if (file.endsWith('.md')) {
            fileList.push(filePath);
        }
    });
    
    return fileList;
}

/**
 * Check if file has the required AI assistant header
 */
function validateHeader(filePath) {
    const relativePath = path.relative(DOCS_DIR, filePath);
    const fileName = path.basename(filePath);
    
    // Check if file is exempted
    if (EXEMPTED_FILES.includes(fileName)) {
        logInfo(`Skipping header check for exempted file: ${relativePath}`);
        return true;
    }
    
    const content = fs.readFileSync(filePath, 'utf8');
    const lines = content.split('\n');
    
    if (lines.length === 0 || !lines[0].startsWith(REQUIRED_HEADER_START)) {
        logError(`Missing AI assistant header: ${relativePath}`);
        return false;
    }
    
    checked++;
    return true;
}

/**
 * Check for broken internal links
 */
function validateLinks(filePath) {
    const relativePath = path.relative(DOCS_DIR, filePath);
    const content = fs.readFileSync(filePath, 'utf8');
    const dir = path.dirname(filePath);
    
    // Match markdown links: [text](url)
    const linkRegex = /\[([^\]]+)\]\(([^)]+)\)/g;
    let match;
    let brokenLinks = [];
    
    while ((match = linkRegex.exec(content)) !== null) {
        const linkText = match[1];
        const linkUrl = match[2];
        
        // Skip external links (http/https) and anchors
        if (linkUrl.startsWith('http://') || 
            linkUrl.startsWith('https://') || 
            linkUrl.startsWith('#')) {
            continue;
        }
        
        // Check if the linked file exists
        const linkedPath = path.resolve(dir, linkUrl);
        
        if (!fs.existsSync(linkedPath)) {
            brokenLinks.push(`"${linkText}" -> ${linkUrl}`);
        }
    }
    
    if (brokenLinks.length > 0) {
        logError(`Broken links in ${relativePath}:`);
        brokenLinks.forEach(link => logError(`  ${link}`));
        return false;
    }
    
    return true;
}

/**
 * Check if all markdown files are referenced in the index
 */
function validateIndexReferences() {
    const indexContent = fs.readFileSync(INDEX_FILE, 'utf8');
    const allFiles = getMarkdownFiles(DOCS_DIR);
    const unreferenced = [];
    
    allFiles.forEach(filePath => {
        const relativePath = path.relative(DOCS_DIR, filePath);
        const fileName = path.basename(filePath);
        
        // Skip the index file itself
        if (fileName === 'index.md') {
            return;
        }
        
        // Check if the file is mentioned in the index
        // We look for the filename in markdown links or as plain text
        if (!indexContent.includes(relativePath) && 
            !indexContent.includes(fileName)) {
            unreferenced.push(relativePath);
        }
    });
    
    if (unreferenced.length > 0) {
        logWarning('The following files are not referenced in docs/index.md:');
        unreferenced.forEach(file => logWarning(`  ${file}`));
        return false;
    }
    
    return true;
}

/**
 * Verify that critical files exist
 */
function validateCriticalFiles() {
    const criticalFiles = [
        'AI_INSTRUCTIONS.md',
        'project-rules.md',
        'general-guidelines.md',
        'index.md'
    ];
    
    let allExist = true;
    
    criticalFiles.forEach(file => {
        const filePath = path.join(DOCS_DIR, file);
        if (!fs.existsSync(filePath)) {
            logError(`Critical file missing: ${file}`);
            allExist = false;
        }
    });
    
    return allExist;
}

/**
 * Main validation function
 */
function validateDocumentation() {
    logHeader('Documentation Validation');
    
    // Check if docs directory exists
    if (!fs.existsSync(DOCS_DIR)) {
        logError(`Documentation directory not found: ${DOCS_DIR}`);
        return false;
    }
    
    logInfo(`Scanning documentation directory: ${DOCS_DIR}\n`);
    
    // 1. Validate critical files exist
    logHeader('1. Checking Critical Files');
    const criticalFilesValid = validateCriticalFiles();
    
    if (criticalFilesValid) {
        logSuccess('All critical files exist');
    }
    
    // 2. Validate headers
    logHeader('2. Validating AI Assistant Headers');
    const markdownFiles = getMarkdownFiles(DOCS_DIR);
    logInfo(`Found ${markdownFiles.length} markdown files\n`);
    
    let headersValid = true;
    markdownFiles.forEach(file => {
        if (!validateHeader(file)) {
            headersValid = false;
        }
    });
    
    if (headersValid && checked > 0) {
        logSuccess(`All ${checked} non-exempted files have correct headers`);
    }
    
    // 3. Validate links
    logHeader('3. Checking for Broken Links');
    let linksValid = true;
    markdownFiles.forEach(file => {
        if (!validateLinks(file)) {
            linksValid = false;
        }
    });
    
    if (linksValid) {
        logSuccess('No broken internal links found');
    }
    
    // 4. Validate index references
    logHeader('4. Validating Index References');
    const indexValid = validateIndexReferences();
    
    if (indexValid) {
        logSuccess('All documentation files are properly indexed');
    }
    
    // Summary
    logHeader('Validation Summary');
    
    if (errors.length === 0 && warnings.length === 0) {
        log('\n🎉 All validation checks passed!', 'green');
        log('   Documentation is properly structured and complete.\n', 'green');
        return true;
    }
    
    if (errors.length > 0) {
        log(`\n❌ Found ${errors.length} error(s)`, 'red');
    }
    
    if (warnings.length > 0) {
        log(`⚠️  Found ${warnings.length} warning(s)`, 'yellow');
    }
    
    log('\nPlease fix the issues above before committing.\n', 'yellow');
    return errors.length === 0;
}

// Run validation
const success = validateDocumentation();

// Exit with appropriate code
process.exit(success ? 0 : 1);
