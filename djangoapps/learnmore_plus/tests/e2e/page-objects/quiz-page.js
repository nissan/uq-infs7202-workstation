// @ts-check

/**
 * QuizPage class representing the quiz page actions and elements
 */
class QuizPage {
  /**
   * @param {import('@playwright/test').Page} page 
   */
  constructor(page) {
    this.page = page;
    this.quizTitle = page.locator('.quiz-title, h1:has-text("Quiz")');
    this.quizForm = page.locator('form.quiz-form, form');
    this.quizQuestions = page.locator('.quiz-question, .question');
    this.radioOptions = page.locator('input[type="radio"]');
    this.checkboxOptions = page.locator('input[type="checkbox"]');
    this.submitButton = page.locator('button:has-text("Submit"), button[type="submit"]');
    this.scoreElement = page.locator('.score, .result-score');
    this.questionCounter = page.locator('.question-counter, text=/Question \\d+/');
    this.feedbackMessages = page.locator('.feedback, .alert, .notification');
  }

  /**
   * Navigate to a specific quiz
   * @param {string} quizId 
   */
  async goto(quizId) {
    await this.page.goto(`/courses/quiz/${quizId}/take/`);
  }

  /**
   * Get the number of questions in the quiz
   * @returns {Promise<number>}
   */
  async getQuestionCount() {
    return await this.quizQuestions.count();
  }

  /**
   * Check if the page is a quiz page
   * @returns {Promise<boolean>}
   */
  async isQuizPage() {
    try {
      // Try multiple indicators to determine if we're on a quiz page
      const indicators = [
        this.quizForm,
        this.quizQuestions,
        this.radioOptions,
        this.submitButton,
        this.questionCounter,
        this.page.locator('text=Question'),
        this.page.locator('text=Submit'),
        this.page.locator('text=points'),
        this.page.locator('text=quiz')
      ];
      
      for (const indicator of indicators) {
        const visible = await indicator.isVisible();
        if (visible) {
          return true;
        }
      }
      
      return false;
    } catch (error) {
      console.log(`Error checking if page is a quiz: ${error.message}`);
      return false;
    }
  }

  /**
   * Answer all quiz questions randomly
   * Uses a more resilient approach to find and answer questions
   */
  async answerQuestionsRandomly() {
    // First try to identify questions by class
    const questions = this.quizQuestions;
    const questionCount = await questions.count();
    
    if (questionCount > 0) {
      console.log(`Found ${questionCount} questions by class`);
      
      // Answer each question
      for (let i = 0; i < questionCount; i++) {
        await this.answerQuestionByIndex(i);
      }
    } else {
      // Fallback: Try to find radio button groups by name attribute
      console.log('No question elements found by class. Using fallback method.');
      
      // Get unique radio button groups
      const radioGroups = await this.page.evaluate(() => {
        const inputs = document.querySelectorAll('input[type="radio"]');
        const groups = {};
        inputs.forEach(input => {
          if (input.name) {
            groups[input.name] = true;
          }
        });
        return Object.keys(groups);
      });
      
      console.log(`Found ${radioGroups.length} question groups by radio button name`);
      
      // For each group, select a random option
      for (const group of radioGroups) {
        try {
          const radios = this.page.locator(`input[type="radio"][name="${group}"]`);
          const count = await radios.count();
          
          if (count > 0) {
            const randomIndex = Math.floor(Math.random() * count);
            await radios.nth(randomIndex).check();
            console.log(`Selected option ${randomIndex + 1} for question group ${group}`);
          }
        } catch (error) {
          console.log(`Error selecting option for group ${group}: ${error.message}`);
        }
      }
      
      // Also handle checkbox questions if any
      const checkboxGroups = await this.page.evaluate(() => {
        const inputs = document.querySelectorAll('input[type="checkbox"]');
        const groups = {};
        inputs.forEach(input => {
          if (input.name) {
            groups[input.name] = true;
          }
        });
        return Object.keys(groups);
      });
      
      console.log(`Found ${checkboxGroups.length} checkbox question groups`);
      
      // For each checkbox group, randomly select at least one option
      for (const group of checkboxGroups) {
        try {
          const checkboxes = this.page.locator(`input[type="checkbox"][name="${group}"]`);
          const count = await checkboxes.count();
          
          if (count > 0) {
            // Select at least one and up to all options randomly
            const numToSelect = Math.floor(Math.random() * count) + 1; // At least 1
            
            for (let i = 0; i < numToSelect; i++) {
              await checkboxes.nth(i).check();
              console.log(`Selected checkbox ${i + 1} for group ${group}`);
            }
          }
        } catch (error) {
          console.log(`Error selecting checkboxes for group ${group}: ${error.message}`);
        }
      }
    }
  }

  /**
   * Answer a specific question by its index
   * @param {number} index 
   */
  async answerQuestionByIndex(index) {
    try {
      const question = this.quizQuestions.nth(index);
      
      // Check if the question has radio buttons or checkboxes
      const radios = question.locator('input[type="radio"]');
      const radioCount = await radios.count();
      
      if (radioCount > 0) {
        // Select a random radio button
        const randomIndex = Math.floor(Math.random() * radioCount);
        await radios.nth(randomIndex).check();
        console.log(`Selected radio option ${randomIndex + 1} for question ${index + 1}`);
        return;
      }
      
      // Check for checkboxes
      const checkboxes = question.locator('input[type="checkbox"]');
      const checkboxCount = await checkboxes.count();
      
      if (checkboxCount > 0) {
        // Select at least one checkbox
        const numToSelect = Math.floor(Math.random() * checkboxCount) + 1; // At least 1
        
        for (let i = 0; i < numToSelect; i++) {
          await checkboxes.nth(i).check();
          console.log(`Selected checkbox option ${i + 1} for question ${index + 1}`);
        }
        return;
      }
      
      // Check for text inputs
      const textInputs = question.locator('input[type="text"], textarea');
      const textInputCount = await textInputs.count();
      
      if (textInputCount > 0) {
        for (let i = 0; i < textInputCount; i++) {
          await textInputs.nth(i).fill('Test answer');
          console.log(`Filled text input ${i + 1} for question ${index + 1}`);
        }
        return;
      }
      
      console.log(`Question ${index + 1} has no answerable inputs`);
    } catch (error) {
      console.log(`Error answering question ${index + 1}: ${error.message}`);
    }
  }

  /**
   * Submit the quiz
   */
  async submitQuiz() {
    await this.submitButton.click();
    await this.page.waitForLoadState('networkidle');
  }

  /**
   * Check if we're on the quiz results page
   * @returns {Promise<boolean>}
   */
  async isResultsPage() {
    const resultIndicators = [
      'text=Results',
      'text=Score',
      'text=Grade',
      'text=Passed',
      'text=Failed',
      'text=Completed',
      'text=Your score:',
      'text=Your answers:',
      '.quiz-result',
      '.quiz-score',
      '.result-summary'
    ];
    
    for (const indicator of resultIndicators) {
      try {
        const element = this.page.locator(indicator);
        const visible = await element.isVisible();
        
        if (visible) {
          return true;
        }
      } catch (error) {
        // Ignore errors and try the next indicator
      }
    }
    
    return false;
  }

  /**
   * Get the quiz score if available
   * @returns {Promise<string>}
   */
  async getScore() {
    try {
      const scoreText = await this.scoreElement.innerText();
      return scoreText;
    } catch (error) {
      console.log(`Error getting score: ${error.message}`);
      return 'Unknown';
    }
  }

  /**
   * Find a quiz to take by navigating from a course
   * @param {string} courseId Optional course ID to start from
   * @returns {Promise<boolean>} True if a quiz was found
   */
  async findQuizFromCourse(courseId = null) {
    try {
      // If courseId is provided, navigate to that course
      if (courseId) {
        await this.page.goto(`/courses/course/${courseId}/`);
      } else {
        // Otherwise start from the course catalog
        await this.page.goto('/courses/catalog/');
        
        // Click on the first course
        const courseLinks = this.page.locator('a[href*="courses"], .course-card, .card');
        const count = await courseLinks.count();
        
        if (count === 0) {
          console.log('No courses found in catalog');
          return false;
        }
        
        await courseLinks.first().click();
      }
      
      await this.page.waitForLoadState('networkidle');
      
      // Look for continue or view course buttons
      const continueSelectors = [
        'text=Continue Learning',
        'text=View Course',
        'text=Start Learning',
        'a:has-text("Learn")',
        'a[href*="learn"]',
        'a.btn-primary',
        'button.btn-primary'
      ];
      
      for (const selector of continueSelectors) {
        const button = this.page.locator(selector);
        if (await button.count() > 0) {
          await button.first().click();
          await this.page.waitForLoadState('networkidle');
          break;
        }
      }
      
      // Now look for quiz links
      const quizSelectors = [
        'text=Quiz',
        'a:has-text("Quiz")',
        'a[href*="quiz"]',
        '.quiz-link'
      ];
      
      for (const selector of quizSelectors) {
        const quizLink = this.page.locator(selector);
        if (await quizLink.count() > 0) {
          await quizLink.first().click();
          await this.page.waitForLoadState('networkidle');
          
          // Check if we're on a quiz page
          if (await this.isQuizPage()) {
            console.log('Successfully found a quiz');
            return true;
          }
        }
      }
      
      console.log('Could not find a quiz in this course');
      return false;
    } catch (error) {
      console.log(`Error finding quiz: ${error.message}`);
      return false;
    }
  }
}

module.exports = { QuizPage };