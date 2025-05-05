// @ts-check

/**
 * LoginPage class representing the login page actions and elements
 */
class LoginPage {
  /**
   * @param {import('@playwright/test').Page} page 
   */
  constructor(page) {
    this.page = page;
    this.usernameInput = page.locator('input[name="username"]');
    this.passwordInput = page.locator('input[name="password"]');
    this.loginButton = page.locator('button[type="submit"]');
    this.errorMessage = page.locator('.alert-error, .error-message');
    this.forgotPasswordLink = page.locator('a:has-text("Forgot password?")');
    this.registerLink = page.locator('a:has-text("Register")');
  }

  /**
   * Navigate to the login page
   */
  async goto() {
    // The actual login URL is configured in the Django URLs 
    await this.page.goto('/login/');
    // If login page doesn't load, try the default Django auth URL as fallback
    if (!await this.usernameInput.isVisible({ timeout: 2000 }).catch(() => false)) {
      console.log('Could not find login form at /login/, trying /accounts/login/');
      await this.page.goto('/accounts/login/');
    }
  }

  /**
   * Login with the provided credentials
   * @param {string} username 
   * @param {string} password 
   */
  async login(username, password) {
    await this.usernameInput.fill(username);
    await this.passwordInput.fill(password);
    await this.loginButton.click();
  }

  /**
   * Click on the register link
   */
  async clickRegister() {
    await this.registerLink.click();
  }

  /**
   * Click on the forgot password link
   */
  async clickForgotPassword() {
    await this.forgotPasswordLink.click();
  }
}

module.exports = { LoginPage };