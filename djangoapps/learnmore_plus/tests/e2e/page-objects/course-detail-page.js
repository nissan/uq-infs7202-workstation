// @ts-check

/**
 * CourseDetailPage class representing the course detail page actions and elements
 */
class CourseDetailPage {
  /**
   * @param {import('@playwright/test').Page} page 
   */
  constructor(page) {
    this.page = page;
    this.courseTitle = page.locator('h1.course-title');
    this.courseDescription = page.locator('.course-description');
    this.enrollButton = page.locator('a:has-text("Enroll Now"), button:has-text("Enroll Now")');
    this.continueButton = page.locator('a:has-text("Continue Learning"), button:has-text("Continue Learning")');
    this.modulesList = page.locator('.modules-list');
    this.moduleItems = page.locator('.module-item');
    this.instructorInfo = page.locator('.instructor-info');
  }

  /**
   * Navigate to a specific course detail page
   * @param {string} slug 
   */
  async goto(slug) {
    await this.page.goto(`/courses/course/${slug}/`);
  }

  /**
   * Enroll in the course
   */
  async enroll() {
    await this.enrollButton.click();
  }

  /**
   * Continue learning the course
   */
  async goToLearn() {
    await this.continueButton.click();
  }

  /**
   * Check if already enrolled in the course
   * @returns {Promise<boolean>}
   */
  async isEnrolled() {
    return await this.continueButton.isVisible();
  }

  /**
   * Get the number of modules in the course
   * @returns {Promise<number>}
   */
  async getModuleCount() {
    return await this.moduleItems.count();
  }

  /**
   * Click on a specific module by index
   * @param {number} index 
   */
  async clickModule(index) {
    await this.moduleItems.nth(index).click();
  }

  /**
   * Get course metadata (duration, level, etc.)
   * @returns {Promise<string>}
   */
  async getCourseMetadata() {
    const metadataSection = this.page.locator('.course-metadata');
    return await metadataSection.innerText();
  }
}

module.exports = { CourseDetailPage };