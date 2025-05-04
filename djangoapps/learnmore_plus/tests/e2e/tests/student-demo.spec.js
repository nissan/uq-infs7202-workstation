// @ts-check
const { test, expect } = require('@playwright/test');

/**
 * Student demo journey test
 * This test simulates the typical student user flow
 * User: john.doe / john.doe123
 */
test.describe('Student Demo Journey', () => {
  // Use the same context for all tests to maintain session
  let studentContext;
  
  test.beforeAll(async ({ browser }) => {
    // Create a new context for the student
    studentContext = await browser.newContext();
    
    // Login as student
    const page = await studentContext.newPage();
    await page.goto('/login/');
    await page.fill('input[name="username"]', 'john.doe');
    await page.fill('input[name="password"]', 'john.doe123');
    await page.click('button[type="submit"]');
    
    // Verify login was successful by checking for dashboard
    await expect(page).toHaveURL(/dashboard|home/);
    await page.close();
  });
  
  test.afterAll(async () => {
    // Close the context after all tests
    await studentContext.close();
  });
  
  test('should access student dashboard', async () => {
    const page = await studentContext.newPage();
    await page.goto('/courses/student/dashboard/');
    
    // Verify student dashboard is loaded
    await expect(page.locator('h1')).toContainText('Student Dashboard');
    
    // Verify enrolled courses are shown
    await expect(page.locator('.enrolled-courses')).toBeVisible();
    
    await page.close();
  });
  
  test('should browse course catalog', async () => {
    const page = await studentContext.newPage();
    await page.goto('/courses/catalog/');
    
    // Verify catalog page loads
    await expect(page.locator('h1')).toContainText('Course Catalog');
    
    // Test search functionality
    await page.fill('input[name="q"]', 'Python');
    await page.click('button[type="submit"]');
    
    // Verify search results
    await expect(page).toHaveURL(/q=Python/);
    
    // Click on first course
    await page.click('.course-card a, .course-card');
    
    // Verify course detail page loads
    await expect(page.locator('.course-title, h1')).toBeVisible();
    
    await page.close();
  });
  
  test('should access enrolled course and view content', async () => {
    const page = await studentContext.newPage();
    
    // Go to student dashboard
    await page.goto('/courses/student/dashboard/');
    
    // Click on first enrolled course
    await page.click('.enrolled-courses a, .course-card');
    
    // Verify course detail page loads
    await expect(page.locator('.course-title, h1')).toBeVisible();
    
    // Check if already enrolled and click "Continue Learning" or "Learn"
    const continueButton = page.locator('a:has-text("Continue Learning"), a:has-text("Learn"), a:has-text("Start Learning")');
    if (await continueButton.isVisible()) {
      await continueButton.click();
      
      // Verify course content page loads
      await expect(page.locator('.course-content, .module-content')).toBeVisible();
      
      // Attempt to navigate between content items if available
      const nextButton = page.locator('a:has-text("Next"), button:has-text("Next")');
      if (await nextButton.isVisible()) {
        await nextButton.click();
        await expect(page.locator('.course-content, .module-content')).toBeVisible();
      }
    }
    
    await page.close();
  });
  
  test('should view and attempt quiz', async () => {
    const page = await studentContext.newPage();
    
    // Go to student dashboard
    await page.goto('/courses/student/dashboard/');
    
    // Click on first enrolled course
    await page.click('.enrolled-courses a, .course-card');
    
    // Continue to learning page
    const continueButton = page.locator('a:has-text("Continue Learning"), a:has-text("Learn"), a:has-text("Start Learning")');
    if (await continueButton.isVisible()) {
      await continueButton.click();
      
      // Look for a quiz in the module navigation
      const modules = page.locator('.module-navigation a');
      const moduleCount = await modules.count();
      
      let quizFound = false;
      
      // Try to find a quiz by navigating through modules and content
      for (let i = 0; i < moduleCount && !quizFound; i++) {
        await modules.nth(i).click();
        
        // Look for quiz content in this module
        const quizLink = page.locator('a:has-text("Quiz"), .content-item:has-text("Quiz") a');
        
        if (await quizLink.count() > 0) {
          await quizLink.first().click();
          quizFound = true;
          
          // Check if we've loaded a quiz form
          if (await page.locator('form.quiz-form, .quiz-question').isVisible()) {
            console.log('Quiz found, attempting to answer questions');
            
            // Find all questions
            const questions = page.locator('.quiz-question');
            const questionCount = await questions.count();
            
            // Answer each question randomly
            for (let q = 0; q < questionCount; q++) {
              // Find all options for this question
              const options = questions.nth(q).locator('input[type="radio"]');
              const optionCount = await options.count();
              
              if (optionCount > 0) {
                // Choose a random option
                const randomOption = Math.floor(Math.random() * optionCount);
                await options.nth(randomOption).check();
              }
            }
            
            // Submit the quiz
            const submitButton = page.locator('button:has-text("Submit"), button[type="submit"]');
            if (await submitButton.isVisible()) {
              await submitButton.click();
              
              // Verify results page
              await expect(page.locator('.quiz-result, .quiz-score')).toBeVisible();
            }
          }
        }
      }
    }
    
    await page.close();
  });
  
  test('should use AI tutor', async () => {
    const page = await studentContext.newPage();
    
    // Go to AI tutor sessions
    await page.goto('/tutor/');
    
    // Check if there are existing sessions or create a new one
    const newSessionButton = page.locator('a:has-text("New Session"), button:has-text("New Session")');
    const existingSession = page.locator('.session-item, .ai-session-card').first();
    
    if (await newSessionButton.isVisible()) {
      await newSessionButton.click();
      
      // Fill session creation form if it appears
      if (await page.locator('form input[name="title"], form input[name="session_name"]').isVisible()) {
        await page.fill('input[name="title"], input[name="session_name"]', 'Test AI Session');
        await page.click('button[type="submit"]');
      }
    } else if (await existingSession.isVisible()) {
      await existingSession.click();
    }
    
    // Verify chat interface loaded
    await expect(page.locator('.chat-container, .message-list')).toBeVisible();
    
    // Send a test message
    const messageInput = page.locator('textarea, input[type="text"]').filter({ hasText: '' });
    if (await messageInput.isVisible()) {
      await messageInput.fill('What is this course about?');
      await page.click('button:has-text("Send"), button[type="submit"]');
      
      // Wait for AI response
      await page.waitForSelector('.ai-message, .bot-message', { timeout: 30000 });
      
      // Verify AI responded
      await expect(page.locator('.ai-message, .bot-message')).toBeVisible();
    }
    
    await page.close();
  });
});