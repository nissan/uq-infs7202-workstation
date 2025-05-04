// @ts-check
const { test, expect } = require('@playwright/test');
const { LoginPage } = require('../page-objects/login-page');
const { HomePage } = require('../page-objects/home-page');

/**
 * These tests verify visual aspects of the UI including:
 * - Dark mode transitions
 * - Component styling consistency
 * - Responsive layouts
 * - UI framework implementation (Tailwind CSS)
 */
test.describe('Visual UI Verification', () => {
  test('should correctly apply dark mode styling', async ({ page }) => {
    // Go to homepage
    const homePage = new HomePage(page);
    await homePage.goto();
    
    // Get initial theme
    const initialTheme = await page.evaluate(() => {
      return document.documentElement.classList.contains('dark') ? 'dark' : 'light';
    });
    
    // Take screenshot of light mode
    if (initialTheme === 'light') {
      await page.screenshot({ path: 'home-light-mode.png', fullPage: true });
    } else {
      await page.screenshot({ path: 'home-dark-mode.png', fullPage: true });
    }
    
    // Toggle theme
    await page.locator('button[data-theme-toggle]').click();
    await page.waitForTimeout(500); // Small delay for theme to apply
    
    // Verify theme changed
    const newTheme = await page.evaluate(() => {
      return document.documentElement.classList.contains('dark') ? 'dark' : 'light';
    });
    
    expect(newTheme).not.toEqual(initialTheme);
    
    // Take screenshot of toggled theme
    if (newTheme === 'light') {
      await page.screenshot({ path: 'home-light-mode.png', fullPage: true });
    } else {
      await page.screenshot({ path: 'home-dark-mode.png', fullPage: true });
    }
    
    // Verify specific Tailwind dark mode classes are active
    if (newTheme === 'dark') {
      // Check background color of main content area
      const mainBgColor = await page.evaluate(() => {
        const main = document.querySelector('main');
        return window.getComputedStyle(main).backgroundColor;
      });
      
      // Dark mode background should not be white
      expect(mainBgColor).not.toBe('rgb(255, 255, 255)');
      
      // Verify text colors for dark mode
      const bodyTextColor = await page.evaluate(() => {
        return window.getComputedStyle(document.body).color;
      });
      
      // Dark mode text should be light
      expect(bodyTextColor).not.toBe('rgb(0, 0, 0)');
    }
  });

  test('should maintain consistent styling on different pages', async ({ page }) => {
    // Login first
    const loginPage = new LoginPage(page);
    await loginPage.goto();
    await loginPage.login('john.doe', 'john.doe123');
    
    // Array of pages to check
    const pagesToCheck = [
      '/',                        // Home
      '/courses/catalog/',        // Course catalog
      '/dashboard/',              // Dashboard
      '/qr-codes/statistics/',    // QR code statistics
    ];
    
    // Verify common UI elements on each page
    for (const pageUrl of pagesToCheck) {
      await page.goto(pageUrl);
      await page.waitForLoadState('networkidle');
      
      // Verify navigation
      await expect(page.locator('nav')).toBeVisible();
      
      // Verify footer
      await expect(page.locator('footer')).toBeVisible();
      
      // Verify theme toggle
      await expect(page.locator('button[data-theme-toggle]')).toBeVisible();
      
      // Verify page-specific content area
      await expect(page.locator('main')).toBeVisible();
      
      // Take screenshot
      const pageName = pageUrl === '/' ? 'home' : pageUrl.replace(/\//g, '-').replace(/^-|-$/g, '');
      await page.screenshot({ path: `${pageName}-styling.png`, fullPage: true });
      
      // Verify Tailwind CSS classes are being used (not Bootstrap)
      const hasTailwindClasses = await page.evaluate(() => {
        // Look for typical Tailwind utility classes
        const elements = document.querySelectorAll('[class*="bg-"]');
        return elements.length > 0;
      });
      
      expect(hasTailwindClasses).toBeTruthy();
      
      // Verify no Bootstrap classes are being used
      const hasBootstrapClasses = await page.evaluate(() => {
        // Look for typical Bootstrap-specific classes
        const bootstrapElements = document.querySelectorAll('.container-fluid, .row, .col, .btn-primary, .navbar-toggler');
        return bootstrapElements.length > 0;
      });
      
      expect(hasBootstrapClasses).toBeFalsy();
    }
  });

  test('should render correctly on mobile, tablet, and desktop sizes', async ({ browser }) => {
    // Define viewport sizes
    const viewports = [
      { width: 375, height: 667, name: 'mobile' },     // iPhone SE
      { width: 768, height: 1024, name: 'tablet' },    // iPad
      { width: 1280, height: 800, name: 'desktop' },   // Desktop
    ];
    
    // Pages to test
    const pagesToTest = [
      '/',                     // Home
      '/login/',               // Login
      '/courses/catalog/',     // Course catalog
    ];
    
    for (const viewport of viewports) {
      // Create a new context with the viewport size
      const context = await browser.newContext({
        viewport: {
          width: viewport.width,
          height: viewport.height,
        }
      });
      
      const page = await context.newPage();
      
      for (const pageUrl of pagesToTest) {
        await page.goto(pageUrl);
        await page.waitForLoadState('networkidle');
        
        // Take screenshot of the page at this viewport
        const pageName = pageUrl === '/' ? 'home' : pageUrl.replace(/\//g, '-').replace(/^-|-$/g, '');
        await page.screenshot({ path: `${pageName}-${viewport.name}.png`, fullPage: true });
        
        // Verify mobile-specific elements on small screens
        if (viewport.name === 'mobile') {
          // Mobile menu button should be visible
          await expect(page.locator('button#mobile-menu-button')).toBeVisible();
          
          // Desktop menu should be hidden
          await expect(page.locator('nav .hidden.md\\:flex')).not.toBeVisible();
          
          // Click mobile menu button to verify it works
          await page.locator('button#mobile-menu-button').click();
          
          // Mobile menu should appear
          await expect(page.locator('#mobile-menu')).toBeVisible();
        }
        
        // Verify desktop elements on large screens
        if (viewport.name === 'desktop') {
          // Desktop menu should be visible
          await expect(page.locator('nav .hidden.md\\:flex')).toBeVisible();
          
          // Mobile menu button should be hidden
          await expect(page.locator('button#mobile-menu-button')).not.toBeVisible();
        }
      }
      
      await context.close();
    }
  });

  test('should correctly apply Tailwind CSS utility classes for modal', async ({ page }) => {
    // Login first
    const loginPage = new LoginPage(page);
    await loginPage.goto();
    await loginPage.login('john.doe', 'john.doe123');
    
    // Go to course catalog
    await page.goto('/courses/catalog/');
    
    // Click on first course
    await page.locator('.course-card').first().click();
    
    // Open QR code modal
    await page.locator('#viewQrCodeBtn').click();
    
    // Wait for modal to be visible
    await page.locator('#qrCodeModal').waitFor({ state: 'visible' });
    
    // Verify modal uses Tailwind CSS classes for positioning
    const modalClasses = await page.evaluate(() => {
      const modal = document.querySelector('#qrCodeModal');
      return modal ? modal.className : '';
    });
    
    // Should have fixed positioning and flex classes (Tailwind)
    expect(modalClasses).toContain('fixed');
    expect(modalClasses).toContain('flex');
    
    // Should not have Bootstrap modal classes
    expect(modalClasses).not.toContain('modal');
    expect(modalClasses).not.toContain('fade');
    
    // Take screenshot of modal
    await page.screenshot({ path: 'qr-code-modal.png' });
    
    // Toggle dark mode
    await page.locator('button[data-theme-toggle]').click();
    await page.waitForTimeout(500); // Small delay for theme to apply
    
    // Take screenshot in dark mode
    await page.screenshot({ path: 'qr-code-modal-dark.png' });
    
    // Verify dark mode classes are applied to modal content
    const hasModalDarkModeClasses = await page.evaluate(() => {
      const modalContent = document.querySelector('#qrCodeModal > div');
      return modalContent ? modalContent.className.includes('dark:bg-') : false;
    });
    
    expect(hasModalDarkModeClasses).toBeTruthy();
    
    // Close modal with Escape key
    await page.keyboard.press('Escape');
    
    // Verify modal is hidden
    await page.locator('#qrCodeModal').waitFor({ state: 'hidden' });
  });
});