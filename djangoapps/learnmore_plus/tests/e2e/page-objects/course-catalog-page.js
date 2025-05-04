// @ts-check

/**
 * CourseCatalogPage class representing the course catalog page actions and elements
 */
class CourseCatalogPage {
  /**
   * @param {import('@playwright/test').Page} page 
   */
  constructor(page) {
    this.page = page;
    this.pageTitle = page.locator('h1:has-text("Course Catalog")');
    this.courseCards = page.locator('.course-card');
    this.searchInput = page.locator('input[name="q"]');
    this.searchButton = page.locator('button:has-text("Search")');
    this.filterOptions = page.locator('.filter-option');
    this.categoryFilter = page.locator('select[name="category"]');
  }

  /**
   * Navigate to the course catalog page
   */
  async goto() {
    await this.page.goto('/courses/catalog/');
  }

  /**
   * Search for courses
   * @param {string} keyword 
   */
  async searchCourses(keyword) {
    await this.searchInput.fill(keyword);
    await this.searchButton.click();
  }

  /**
   * Filter courses by category
   * @param {string} category 
   */
  async filterByCategory(category) {
    await this.categoryFilter.selectOption(category);
  }

  /**
   * Click on the first course in the list
   */
  async clickFirstCourse() {
    await this.courseCards.first().click();
  }

  /**
   * Get the number of courses displayed
   * @returns {Promise<number>}
   */
  async getCourseCount() {
    return await this.courseCards.count();
  }

  /**
   * Check if search results contain a specific text
   * @param {string} text 
   * @returns {Promise<boolean>}
   */
  async resultsContain(text) {
    const cards = await this.courseCards.all();
    for (const card of cards) {
      const cardText = await card.innerText();
      if (cardText.includes(text)) {
        return true;
      }
    }
    return false;
  }
}

module.exports = { CourseCatalogPage };