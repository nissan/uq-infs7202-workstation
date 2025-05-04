#!/usr/bin/env node

/**
 * Script to generate performance test stubs for pages or features
 * Usage: node generate-performance-test.js <page-name>
 * Example: node generate-performance-test.js course-catalog
 */

const fs = require('fs');
const path = require('path');

// Get command line arguments
const args = process.argv.slice(2);
const pageName = args[0];

if (!pageName) {
  console.error('Usage: node generate-performance-test.js <page-name>');
  process.exit(1);
}

// Normalize page name
const normalizedPageName = pageName.toLowerCase().replace(/\s+/g, '-');

// Template for performance tests
const performanceTestTemplate = `// @ts-check
const { test, expect } = require('@playwright/test');

/**
 * Performance tests for the ${pageName} page
 */
test.describe('${pageName} Performance', () => {
  test('should load ${pageName} page quickly', async ({ page }) => {
    // Start performance measurement
    const startTime = Date.now();
    
    // Navigate to the page
    // TODO: Update with correct URL
    await page.goto('/relevant-url/');
    
    // Wait for the page to be fully loaded
    await page.waitForLoadState('networkidle');
    
    // Calculate load time
    const loadTime = Date.now() - startTime;
    console.log(\`${pageName} page load time: \${loadTime}ms\`);
    
    // Performance threshold - adjust as needed
    expect(loadTime).toBeLessThan(3000); // 3-second threshold
  });
  
  test('should render critical elements quickly', async ({ page }) => {
    // Navigate to the page
    // TODO: Update with correct URL
    await page.goto('/relevant-url/');
    
    // Define critical elements to measure
    const criticalSelectors = [
      'h1', // Main heading
      '.main-content', // Main content container
      '.critical-ui-element', // TODO: Replace with actual critical UI elements
    ];
    
    // Measure time for each critical element to appear
    for (const selector of criticalSelectors) {
      const startTime = Date.now();
      await page.waitForSelector(selector, { timeout: 5000 }).catch(e => {
        console.error(\`Element not found: \${selector}\`);
        throw e;
      });
      const renderTime = Date.now() - startTime;
      console.log(\`Element \${selector} render time: \${renderTime}ms\`);
      
      // Performance threshold for critical elements - adjust as needed
      expect(renderTime).toBeLessThan(1000); // 1-second threshold
    }
  });
  
  test('should maintain smooth interactions', async ({ page }) => {
    // Navigate to the page
    // TODO: Update with correct URL
    await page.goto('/relevant-url/');
    
    // Wait for the page to be fully loaded
    await page.waitForLoadState('networkidle');
    
    // Define interactions to measure
    const interactions = [
      {
        name: 'button click',
        action: async () => {
          // TODO: Replace with actual interaction
          await page.click('.interaction-button');
        },
        expectation: async () => {
          // TODO: Replace with actual expectation check
          await page.waitForSelector('.interaction-result');
        }
      },
      // TODO: Add more interactions to test
    ];
    
    // Measure time for each interaction
    for (const { name, action, expectation } of interactions) {
      const startTime = Date.now();
      await action();
      await expectation();
      const interactionTime = Date.now() - startTime;
      console.log(\`Interaction "\${name}" response time: \${interactionTime}ms\`);
      
      // Performance threshold for interactions - adjust as needed
      expect(interactionTime).toBeLessThan(500); // 500ms threshold
    }
  });
  
  test('should have optimized network usage', async ({ page, context }) => {
    // Start monitoring network requests
    const requests = [];
    page.on('request', request => {
      requests.push(request);
    });
    
    // Navigate to the page
    // TODO: Update with correct URL
    await page.goto('/relevant-url/');
    
    // Wait for the page to be fully loaded
    await page.waitForLoadState('networkidle');
    
    // Analyze network requests
    const totalRequests = requests.length;
    const imageRequests = requests.filter(r => r.resourceType() === 'image').length;
    const scriptRequests = requests.filter(r => r.resourceType() === 'script').length;
    const cssRequests = requests.filter(r => r.resourceType() === 'stylesheet').length;
    
    console.log(\`Total requests: \${totalRequests}\`);
    console.log(\`Image requests: \${imageRequests}\`);
    console.log(\`Script requests: \${scriptRequests}\`);
    console.log(\`CSS requests: \${cssRequests}\`);
    
    // Performance thresholds - adjust as needed
    expect(totalRequests).toBeLessThan(50); // Maximum number of total requests
    expect(imageRequests).toBeLessThan(15); // Maximum number of image requests
    expect(scriptRequests).toBeLessThan(10); // Maximum number of script requests
    expect(cssRequests).toBeLessThan(5); // Maximum number of CSS requests
  });
  
  test('should maintain responsive layout under load', async ({ page }) => {
    // Navigate to the page
    // TODO: Update with correct URL
    await page.goto('/relevant-url/');
    
    // Wait for the page to be fully loaded
    await page.waitForLoadState('networkidle');
    
    // Simulate high load condition
    // For example, add many items to a list or load large dataset
    // TODO: Customize this to simulate appropriate load for your page
    await page.evaluate(() => {
      // Example: Create many DOM elements
      const container = document.querySelector('.content-container');
      if (container) {
        for (let i = 0; i < 100; i++) {
          const div = document.createElement('div');
          div.textContent = \`Test item \${i}\`;
          div.className = 'test-item';
          container.appendChild(div);
        }
      }
    });
    
    // Verify page still responds properly
    const isResponsive = await page.evaluate(() => {
      // Example check: measure time to perform a simple DOM operation
      const start = performance.now();
      document.querySelector('.test-item')?.getBoundingClientRect();
      const duration = performance.now() - start;
      return duration < 16; // Less than 16ms (60fps) is considered responsive
    });
    
    expect(isResponsive).toBeTruthy();
  });
});`;

// Create the test file
const testsDir = path.join(__dirname, '..', 'tests');
const filename = `${normalizedPageName}-performance.spec.js`;
const filePath = path.join(testsDir, filename);

// Check if file already exists
if (fs.existsSync(filePath)) {
  console.error(`Error: File ${filename} already exists`);
  process.exit(1);
}

// Write the file
fs.writeFileSync(filePath, performanceTestTemplate);

console.log(`Performance test stub created: ${filePath}`);
console.log('Remember to update TODOs and customize the test for your specific page.');
console.log('\nDone!');