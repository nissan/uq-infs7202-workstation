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
   * This method is more resilient, and will try multiple selector patterns
   * to find a course card or link
   */
  async clickFirstCourse() {
    // Try multiple selector patterns with a timeout of 5 seconds
    const selectors = [
      '.course-card',
      '.card.course',
      'a[href*="/courses/"]',
      'a:has-text("Python")',
      'a:has-text("Web Development")',
      'a:has-text("Introduction")',
      // Add more potential selectors here
    ];
    
    // Try each selector
    for (const selector of selectors) {
      const elements = this.page.locator(selector);
      const count = await elements.count();
      
      if (count > 0) {
        console.log(`Found ${count} elements with selector: ${selector}`);
        await elements.first().click();
        return;
      }
    }
    
    // If we reach here, no courses were found
    console.log('No course cards or links found on the page. Checking for empty state.');
    
    // Check if we're seeing an empty state or no courses message
    const emptyStateExists = await this.page.locator('text=No courses found, text=No courses available, text=No results').count() > 0;
    
    if (emptyStateExists) {
      console.log('Empty state detected. Test should handle this case appropriately.');
      // Instead of failing, we'll throw a specific error that tests can catch and handle
      throw new Error('NO_COURSES_AVAILABLE');
    } else {
      // If we can't find courses or empty state, take a screenshot for debugging
      await this.page.screenshot({ path: 'debug-no-courses.png' });
      throw new Error('Could not find any course cards or links on the page.');
    }
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