// @ts-check

/**
 * CourseLearnPage class representing the course learning page actions and elements
 */
class CourseLearnPage {
  /**
   * @param {import('@playwright/test').Page} page 
   */
  constructor(page) {
    this.page = page;
    this.courseTitle = page.locator('.course-title');
    this.moduleNavigation = page.locator('.module-navigation');
    this.moduleTitle = page.locator('.module-title');
    this.courseContent = page.locator('.course-content');
    this.contentNavigation = page.locator('.content-navigation');
    this.nextButton = page.locator('button:has-text("Next"), a:has-text("Next")');
    this.prevButton = page.locator('button:has-text("Previous"), a:has-text("Previous")');
    this.progressIndicator = page.locator('.progress-indicator');
    this.quizForm = page.locator('form.quiz-form');
    this.quizSubmitButton = page.locator('button:has-text("Submit Quiz")');
  }

  /**
   * Navigate to a specific course learning page
   * @param {string} slug 
   * @param {number} moduleOrder 
   * @param {number} contentOrder 
   */
  async goto(slug, moduleOrder = 1, contentOrder = null) {
    if (contentOrder) {
      await this.page.goto(`/courses/course/${slug}/learn/${moduleOrder}/${contentOrder}/`);
    } else {
      await this.page.goto(`/courses/course/${slug}/learn/${moduleOrder}/`);
    }
  }

  /**
   * Navigate to the next content item
   */
  async goToNext() {
    await this.nextButton.click();
  }

  /**
   * Navigate to the previous content item
   */
  async goToPrevious() {
    await this.prevButton.click();
  }

  /**
   * Select a specific module from the navigation
   * @param {number} index 
   */
  async selectModule(index) {
    const moduleLinks = this.moduleNavigation.locator('a, button');
    await moduleLinks.nth(index).click();
  }

  /**
   * Check if currently on a quiz
   * @returns {Promise<boolean>}
   */
  async isQuiz() {
    return await this.quizForm.isVisible();
  }

  /**
   * Answer all questions in a quiz with random selections
   */
  async answerQuizRandomly() {
    const questions = this.page.locator('.quiz-question');
    const count = await questions.count();
    
    for (let i = 0; i < count; i++) {
      const question = questions.nth(i);
      const options = question.locator('input[type="radio"]');
      const optionCount = await options.count();
      
      if (optionCount > 0) {
        // Select a random option
        const randomIndex = Math.floor(Math.random() * optionCount);
        await options.nth(randomIndex).check();
      }
    }
  }

  /**
   * Submit the quiz
   */
  async submitQuiz() {
    await this.quizSubmitButton.click();
  }

  /**
   * Get the current progress percentage
   * @returns {Promise<string>}
   */
  async getProgressPercentage() {
    const progressText = await this.progressIndicator.innerText();
    const percentageMatch = progressText.match(/(\d+)%/);
    return percentageMatch ? percentageMatch[1] : '0';
  }
}

module.exports = { CourseLearnPage };