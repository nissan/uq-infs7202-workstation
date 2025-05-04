// @ts-check
const { test, expect } = require('@playwright/test');
const { LoginPage } = require('../page-objects/login-page');
const { HomePage } = require('../page-objects/home-page');

test.describe('Authentication', () => {
  test('should login with valid credentials', async ({ page }) => {
    const loginPage = new LoginPage(page);
    const homePage = new HomePage(page);
    
    // Navigate to the login page
    await loginPage.goto();
    
    // Verify login page elements
    await expect(loginPage.usernameInput).toBeVisible();
    await expect(loginPage.passwordInput).toBeVisible();
    await expect(loginPage.loginButton).toBeVisible();
    
    // Login with valid credentials
    await loginPage.login('student', 'password123');
    
    // Verify redirection to dashboard or homepage
    await expect(page).toHaveURL(/dashboard|home/);
    
    // Verify logged in state
    await expect(homePage.logoutLink).toBeVisible();
  });

  test('should show error with invalid credentials', async ({ page }) => {
    const loginPage = new LoginPage(page);
    
    // Navigate to the login page
    await loginPage.goto();
    
    // Login with invalid credentials
    await loginPage.login('invaliduser', 'wrongpassword');
    
    // Verify error message
    await expect(loginPage.errorMessage).toBeVisible();
    await expect(loginPage.errorMessage).toContainText('Invalid username or password');
    
    // Verify still on login page
    await expect(page).toHaveURL(/login/);
  });

  test('should logout successfully', async ({ page }) => {
    const loginPage = new LoginPage(page);
    const homePage = new HomePage(page);
    
    // Login first
    await loginPage.goto();
    await loginPage.login('student', 'password123');
    
    // Verify logged in
    await expect(homePage.logoutLink).toBeVisible();
    
    // Logout
    await homePage.logout();
    
    // Verify logged out - should be redirected to home page
    await expect(page).toHaveURL(/home/);
    
    // Verify login link is visible (not logout link)
    await expect(homePage.loginLink).toBeVisible();
  });
});