// @ts-check

/**
 * HomePage class representing the home page actions and elements
 */
class HomePage {
  /**
   * @param {import('@playwright/test').Page} page 
   */
  constructor(page) {
    this.page = page;
    this.loginLink = page.locator('a:has-text("Log In")');
    this.registerLink = page.locator('a:has-text("Sign Up")');
    this.logoutLink = page.locator('button:has-text("Log Out")');
    this.coursesLink = page.locator('a:has-text("Courses")');
    this.featuresSection = page.locator('#features');
    this.howItWorksSection = page.locator('#how-it-works');
    this.ctaButton = page.locator('a:has-text("Get Started")');
  }

  /**
   * Navigate to the home page
   */
  async goto() {
    await this.page.goto('/');
  }

  /**
   * Click on the login link
   */
  async clickLogin() {
    await this.loginLink.click();
  }

  /**
   * Click on the register link
   */
  async clickRegister() {
    await this.registerLink.click();
  }

  /**
   * Click on the logout link
   */
  async logout() {
    await this.logoutLink.click();
  }

  /**
   * Click on the courses link
   */
  async goToCourses() {
    await this.coursesLink.click();
  }

  /**
   * Click on the CTA button
   */
  async clickGetStarted() {
    await this.ctaButton.click();
  }

  /**
   * Scroll to features section
   */
  async scrollToFeatures() {
    await this.featuresSection.scrollIntoViewIfNeeded();
  }

  /**
   * Scroll to how it works section
   */
  async scrollToHowItWorks() {
    await this.howItWorksSection.scrollIntoViewIfNeeded();
  }
}

module.exports = { HomePage };