// @ts-check
const { test, expect } = require('@playwright/test');
const { HomePage } = require('../page-objects/home-page');

test.describe('Navigation and UI', () => {
  test('should have working navigation links on home page', async ({ page }) => {
    const homePage = new HomePage(page);
    
    // Navigate to home page
    await homePage.goto();
    
    // Check main navigation links
    await expect(homePage.coursesLink).toBeVisible();
    await expect(homePage.loginLink).toBeVisible();
    await expect(homePage.registerLink).toBeVisible();
    
    // Check if sections exist
    await homePage.scrollToFeatures();
    await expect(homePage.featuresSection).toBeVisible();
    
    await homePage.scrollToHowItWorks();
    await expect(homePage.howItWorksSection).toBeVisible();
  });

  test('should navigate between pages', async ({ page }) => {
    const homePage = new HomePage(page);
    
    // Navigate to home page
    await homePage.goto();
    
    // Click on the courses link
    await homePage.goToCourses();
    
    // Verify on catalog page
    await expect(page).toHaveURL(/catalog/);
    await expect(page.locator('h1')).toContainText('Course Catalog');
    
    // Navigate back to home
    await page.goto('/');
    
    // Click login
    await homePage.clickLogin();
    
    // Verify on login page
    await expect(page).toHaveURL(/login/);
    await expect(page.locator('h1, h2')).toContainText('Log In');
  });

  test('should have responsive design', async ({ page }) => {
    // Test on desktop
    await page.setViewportSize({ width: 1280, height: 800 });
    await page.goto('/');
    
    // Desktop menu should be visible
    await expect(page.locator('nav .hidden.md\\:flex')).toBeVisible();
    
    // Mobile menu button should not be visible
    await expect(page.locator('button#mobile-menu-button')).not.toBeVisible();
    
    // Test on mobile
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/');
    
    // Desktop menu should be hidden
    await expect(page.locator('nav .hidden.md\\:flex')).not.toBeVisible();
    
    // Mobile menu button should be visible
    await expect(page.locator('button#mobile-menu-button')).toBeVisible();
    
    // Click mobile menu button
    await page.locator('button#mobile-menu-button').click();
    
    // Mobile menu should be visible
    await expect(page.locator('#mobile-menu')).toBeVisible();
    
    // Should be able to click login link in mobile menu
    await page.locator('#mobile-menu a:has-text("Log In")').click();
    
    // Verify on login page
    await expect(page).toHaveURL(/login/);
  });

  test('should change theme using theme toggle', async ({ page }) => {
    await page.goto('/');
    
    // Get initial theme state
    const initialTheme = await page.evaluate(() => {
      return document.documentElement.classList.contains('dark') ? 'dark' : 'light';
    });
    
    // Click theme toggle
    await page.locator('button[data-theme-toggle]').click();
    
    // Check that theme changed
    const newTheme = await page.evaluate(() => {
      return document.documentElement.classList.contains('dark') ? 'dark' : 'light';
    });
    
    expect(newTheme).not.toEqual(initialTheme);
  });
});