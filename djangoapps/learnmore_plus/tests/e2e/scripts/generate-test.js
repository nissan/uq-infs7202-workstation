#!/usr/bin/env node

/**
 * Script to generate a new Playwright test file
 * Usage: node generate-test.js page-name
 * Example: node generate-test.js profile
 */

const fs = require('fs');
const path = require('path');
const readline = require('readline');

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

// Validate arguments
if (process.argv.length < 3) {
  console.error('Please provide a page name. Example: node generate-test.js profile');
  process.exit(1);
}

// Get page name from arguments
const pageName = process.argv[2].toLowerCase();
const pageClassName = pageName.split('-').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join('') + 'Page';
const pageObjectFilename = `${pageName}-page.js`;
const testFilename = `${pageName}.spec.js`;

// Create page object template
const pageObjectTemplate = `// @ts-check

/**
 * ${pageClassName} class representing the ${pageName} page actions and elements
 */
class ${pageClassName} {
  /**
   * @param {import('@playwright/test').Page} page 
   */
  constructor(page) {
    this.page = page;
    // TODO: Add your page elements here
    this.pageTitle = page.locator('h1');
  }

  /**
   * Navigate to the ${pageName} page
   */
  async goto() {
    await this.page.goto('/${pageName.replace('_', '-')}/');
  }

  // TODO: Add your page methods here
}

module.exports = { ${pageClassName} };`;

// Create test file template
const testFileTemplate = `// @ts-check
const { test, expect } = require('@playwright/test');
const { ${pageClassName} } = require('../page-objects/${pageObjectFilename}');

test.describe('${pageName.charAt(0).toUpperCase() + pageName.slice(1)} Page', () => {
  test('should load ${pageName} page', async ({ page }) => {
    const ${pageName}Page = new ${pageClassName}(page);
    
    // Navigate to the ${pageName} page
    await ${pageName}Page.goto();
    
    // Verify page elements
    await expect(${pageName}Page.pageTitle).toBeVisible();
  });

  // TODO: Add your tests here
});`;

// Create directories if they don't exist
const pageObjectsDir = path.join(__dirname, '..', 'page-objects');
const testsDir = path.join(__dirname, '..', 'tests');

if (!fs.existsSync(pageObjectsDir)) {
  fs.mkdirSync(pageObjectsDir, { recursive: true });
}

if (!fs.existsSync(testsDir)) {
  fs.mkdirSync(testsDir, { recursive: true });
}

// Check if files already exist
const pageObjectPath = path.join(pageObjectsDir, pageObjectFilename);
const testFilePath = path.join(testsDir, testFilename);

if (fs.existsSync(pageObjectPath) || fs.existsSync(testFilePath)) {
  rl.question('One or both files already exist. Overwrite? (y/n): ', (answer) => {
    if (answer.toLowerCase() === 'y') {
      writeFiles();
    } else {
      console.log('Operation cancelled.');
      rl.close();
      process.exit(0);
    }
  });
} else {
  writeFiles();
}

function writeFiles() {
  // Write page object file
  fs.writeFileSync(pageObjectPath, pageObjectTemplate);
  console.log(`Page object created: ${pageObjectPath}`);

  // Write test file
  fs.writeFileSync(testFilePath, testFileTemplate);
  console.log(`Test file created: ${testFilePath}`);

  rl.close();
}

rl.on('close', () => {
  console.log('\nTo run your new test:');
  console.log(`npx playwright test ${testFilename}`);
  process.exit(0);
});