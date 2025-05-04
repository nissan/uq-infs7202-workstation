#!/usr/bin/env node

/**
 * Script to generate accessibility test stubs for components or pages
 * Usage: node generate-accessibility-test.js <component-name>
 * Example: node generate-accessibility-test.js qr-modal
 */

const fs = require('fs');
const path = require('path');

// Get command line arguments
const args = process.argv.slice(2);
const componentName = args[0];

if (!componentName) {
  console.error('Usage: node generate-accessibility-test.js <component-name>');
  process.exit(1);
}

// Normalize component name
const normalizedComponentName = componentName.toLowerCase().replace(/\s+/g, '-');

// Template for accessibility tests
const accessibilityTestTemplate = `// @ts-check
const { test, expect } = require('@playwright/test');
const { LoginPage } = require('../page-objects/login-page');

/**
 * Accessibility tests for the ${componentName} component
 */
test.describe('${componentName} Accessibility', () => {
  test('should be keyboard navigable', async ({ page }) => {
    // Login first (if needed)
    const loginPage = new LoginPage(page);
    await loginPage.goto();
    await loginPage.login('john.doe', 'john.doe123');
    
    // Navigate to the page with the ${componentName} component
    // TODO: Update with correct URL
    await page.goto('/relevant-page/');
    
    // TODO: Add steps to interact with the ${componentName} using keyboard
    // Example: Using Tab key to navigate focus
    await page.keyboard.press('Tab');
    await page.keyboard.press('Tab');
    
    // TODO: Verify focus is on the expected element
    const focusedElement = await page.evaluate(() => {
      return document.activeElement.tagName + 
        (document.activeElement.id ? '#' + document.activeElement.id : '') +
        (document.activeElement.className ? '.' + document.activeElement.className.replace(/\\s+/g, '.') : '');
    });
    console.log('Focused element:', focusedElement);
    
    // TODO: Add assertions for keyboard navigation
    // await expect(page.locator('#focus-target')).toBeFocused();
    
    // TODO: Test escape key functionality if applicable
    await page.keyboard.press('Escape');
    
    // TODO: Add assertions for Escape key behavior
  });
  
  test('should have proper ARIA attributes and roles', async ({ page }) => {
    // TODO: Implement this test
    await page.goto('/relevant-page/');
    
    // TODO: Add steps to show/open the ${componentName} if needed
    
    // TODO: Check for required ARIA attributes
    // Examples:
    await expect(page.locator('selector')).toHaveAttribute('aria-label', 'Expected value');
    await expect(page.locator('selector')).toHaveAttribute('role', 'Expected role');
    
    // TODO: Check for proper heading structure
    await expect(page.locator('h1')).toBeVisible();
    
    // TODO: Check for required attributes on interactive elements
    await expect(page.locator('button')).toHaveAttribute('type', 'button');
  });
  
  test('should have sufficient color contrast in light mode', async ({ page }) => {
    // TODO: Implement this test
    await page.goto('/relevant-page/');
    
    // Ensure we're in light mode
    await page.evaluate(() => {
      if (document.documentElement.classList.contains('dark')) {
        // Toggle to light mode if in dark mode
        document.querySelector('button[data-theme-toggle]').click();
      }
    });
    
    // TODO: Add steps to show/open the ${componentName} if needed
    
    // TODO: Add manual checks for color contrast
    // In a real implementation, you would use an accessibility testing library
    // like axe-core to automatically check contrast ratios
    
    // Example of a color contrast check (manual implementation)
    const hasProperContrast = await page.evaluate(() => {
      // This would be replaced with actual calculations or axe-core checks
      return true; // Placeholder
    });
    
    expect(hasProperContrast).toBeTruthy();
  });
  
  test('should have sufficient color contrast in dark mode', async ({ page }) => {
    // TODO: Implement this test
    await page.goto('/relevant-page/');
    
    // Ensure we're in dark mode
    await page.evaluate(() => {
      if (!document.documentElement.classList.contains('dark')) {
        // Toggle to dark mode if in light mode
        document.querySelector('button[data-theme-toggle]').click();
      }
    });
    
    // TODO: Add steps to show/open the ${componentName} if needed
    
    // TODO: Add manual checks for color contrast in dark mode
    // In a real implementation, you would use an accessibility testing library
    
    // Example of a color contrast check (manual implementation)
    const hasProperContrast = await page.evaluate(() => {
      // This would be replaced with actual calculations or axe-core checks
      return true; // Placeholder
    });
    
    expect(hasProperContrast).toBeTruthy();
  });
  
  test('should be screen reader friendly', async ({ page }) => {
    // Note: This test provides a structure for manual testing with screen readers
    // Automated testing with screen readers is complex and often requires
    // specialized tools beyond Playwright
    
    await page.goto('/relevant-page/');
    
    // TODO: Add steps to show/open the ${componentName} if needed
    
    // Check for alt text on images
    const images = await page.locator('img').all();
    for (const img of images) {
      await expect(img).toHaveAttribute('alt');
    }
    
    // Check for form labels
    const formControls = await page.locator('input, select, textarea').all();
    for (const control of formControls) {
      const hasLabelOrAria = await page.evaluate(el => {
        // Check for associated label
        const id = el.id;
        return id ? !!document.querySelector(\`label[for="\${id}"]\`) : false;
      }, control);
      
      // If no label, it should have aria-label or aria-labelledby
      if (!hasLabelOrAria) {
        const hasAriaLabel = await control.evaluate(el => {
          return el.hasAttribute('aria-label') || el.hasAttribute('aria-labelledby');
        });
        
        expect(hasAriaLabel).toBeTruthy();
      }
    }
  });
});`;

// Create the test file
const testsDir = path.join(__dirname, '..', 'tests');
const filename = `${normalizedComponentName}-accessibility.spec.js`;
const filePath = path.join(testsDir, filename);

// Check if file already exists
if (fs.existsSync(filePath)) {
  console.error(`Error: File ${filename} already exists`);
  process.exit(1);
}

// Write the file
fs.writeFileSync(filePath, accessibilityTestTemplate);

console.log(`Accessibility test stub created: ${filePath}`);
console.log('Remember to update TODOs and customize the test for your specific component.');
console.log('\nDone!');