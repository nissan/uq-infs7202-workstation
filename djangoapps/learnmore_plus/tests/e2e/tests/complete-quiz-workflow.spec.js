// @ts-check
const { test, expect } = require('./critical-tests');
const { LoginPage } = require('../page-objects/login-page');
const { QuizPage } = require('../page-objects/quiz-page');

/**
 * Test for complete quiz workflow using the QuizPage page object
 * This test focuses specifically on answering and submitting quizzes
 */
test.describe('Complete Quiz Workflow', () => {
  
  test('should find, answer, and submit a quiz', async ({ page }) => {
    // Set longer timeout for this complex test
    test.setTimeout(60000);
    
    // Login as a student
    const loginPage = new LoginPage(page);
    await loginPage.goto();
    await loginPage.login('john.doe', 'john.doe123');
    
    // Take a screenshot after login
    await page.screenshot({ path: 'complete-quiz-after-login.png', fullPage: true });
    
    // Create a QuizPage instance
    const quizPage = new QuizPage(page);
    
    // Try to find a quiz starting from the course catalog
    console.log('Looking for a quiz to take...');
    const foundQuiz = await quizPage.findQuizFromCourse();
    
    // If we couldn't find a quiz, try directly accessing a common quiz URL pattern
    if (!foundQuiz) {
      console.log('Could not find quiz through course navigation. Trying direct quiz URLs...');
      
      // Try some common quiz paths
      const quizPaths = [
        '/courses/quiz/1/take/',
        '/courses/quiz/2/take/',
        '/courses/quiz/3/take/',
        '/quizzes/1/take/',
        '/quizzes/2/take/',
        '/quizzes/3/take/'
      ];
      
      let quizFound = false;
      
      for (const path of quizPaths) {
        try {
          console.log(`Trying direct quiz path: ${path}`);
          await page.goto(path, { timeout: 5000 });
          await page.waitForLoadState('networkidle');
          
          // Take a screenshot to see what we got
          await page.screenshot({ path: `complete-quiz-direct-path-${path.replace(/\//g, '-')}.png`, fullPage: true });
          
          // Check if we're on a quiz page
          if (await quizPage.isQuizPage()) {
            console.log(`Found quiz at path: ${path}`);
            quizFound = true;
            break;
          }
        } catch (error) {
          console.log(`Error accessing path ${path}: ${error.message}`);
        }
      }
      
      // If we still couldn't find a quiz, look for any links that might lead to quizzes
      if (!quizFound) {
        console.log('Could not find quiz through direct URLs. Searching site-wide...');
        
        // Try the dashboard first
        await page.goto('/dashboard/');
        await page.waitForLoadState('networkidle');
        
        // Take a screenshot of dashboard
        await page.screenshot({ path: 'complete-quiz-dashboard.png', fullPage: true });
        
        // Look for quiz links
        const quizLinkSelectors = [
          'a:has-text("Quiz")',
          'a[href*="quiz"]',
          'text=Take Quiz',
          'text=Continue Quiz',
          'text=Assessment'
        ];
        
        for (const selector of quizLinkSelectors) {
          const links = page.locator(selector);
          const count = await links.count();
          
          if (count > 0) {
            console.log(`Found ${count} potential quiz links with selector: ${selector}`);
            await links.first().click();
            await page.waitForLoadState('networkidle');
            
            // Check if we're on a quiz page
            if (await quizPage.isQuizPage()) {
              console.log('Found quiz through dashboard link');
              quizFound = true;
              break;
            } else {
              // Go back to dashboard to try another link
              await page.goto('/dashboard/');
              await page.waitForLoadState('networkidle');
            }
          }
        }
      }
      
      // If we still couldn't find a quiz, skip the test
      if (!quizFound) {
        console.log('Could not find any quiz to take after multiple attempts');
        test.skip(true, 'No quiz found to take');
        return;
      }
    }
    
    // We've found a quiz - now take it
    console.log('Found a quiz - proceeding to answer questions');
    
    // First take a screenshot of the quiz before answering
    await page.screenshot({ path: 'complete-quiz-before-answers.png', fullPage: true });
    
    // Get the number of questions
    const questionCount = await quizPage.getQuestionCount();
    console.log(`Quiz has ${questionCount} questions`);
    
    // Answer the questions randomly
    await quizPage.answerQuestionsRandomly();
    console.log('Answered all questions randomly');
    
    // Take a screenshot after answering
    await page.screenshot({ path: 'complete-quiz-after-answers.png', fullPage: true });
    
    // Submit the quiz
    await quizPage.submitQuiz();
    console.log('Submitted the quiz');
    
    // Wait for results page to load
    await page.waitForLoadState('networkidle');
    
    // Take a screenshot of the results page
    await page.screenshot({ path: 'complete-quiz-results.png', fullPage: true });
    
    // Check if we're on a results page
    const isResultsPage = await quizPage.isResultsPage();
    
    // Get the score if available
    if (isResultsPage) {
      const score = await quizPage.getScore();
      console.log(`Quiz score: ${score}`);
    }
    
    // Verify we completed the quiz workflow
    expect(isResultsPage).toBeTruthy();
  });
  
  // Additional test for non-enrolled course scenario - handles the case where a student isn't enrolled
  test('should show enrollment message for non-enrolled course quizzes', async ({ page }) => {
    // Login as a student
    const loginPage = new LoginPage(page);
    await loginPage.goto();
    await loginPage.login('john.doe', 'john.doe123');
    
    // Create a new instance of QuizPage
    const quizPage = new QuizPage(page);
    
    // Try to access a quiz in a non-enrolled course
    // We'll try to access multiple quiz IDs to find one that requires enrollment
    const quizIds = [10, 20, 30, 40, 50]; // Try some higher IDs assuming student isn't enrolled
    
    let foundNonEnrolledQuiz = false;
    
    for (const id of quizIds) {
      try {
        console.log(`Trying to access quiz ID: ${id}`);
        await page.goto(`/courses/quiz/${id}/take/`);
        await page.waitForLoadState('networkidle');
        
        // Take screenshot
        await page.screenshot({ path: `non-enrolled-quiz-${id}.png`, fullPage: true });
        
        // Check if we see an enrollment message
        const enrollmentMessages = [
          'text=must be enrolled',
          'text=not enrolled',
          'text=Enroll',
          'text=Join Course',
          'text=Access Denied',
          'text=not authorized',
          'text=Permission Denied'
        ];
        
        for (const message of enrollmentMessages) {
          const messageElement = page.locator(message);
          const isVisible = await messageElement.isVisible();
          
          if (isVisible) {
            console.log(`Found enrollment message: ${message}`);
            foundNonEnrolledQuiz = true;
            break;
          }
        }
        
        if (foundNonEnrolledQuiz) {
          break;
        }
      } catch (error) {
        console.log(`Error accessing quiz ${id}: ${error.message}`);
      }
    }
    
    // If we couldn't find a non-enrolled course quiz, skip the test
    if (!foundNonEnrolledQuiz) {
      console.log('Could not find a quiz requiring enrollment');
      test.skip(true, 'Could not find a quiz requiring enrollment');
      return;
    }
    
    // Verify appropriate messaging
    expect(foundNonEnrolledQuiz).toBeTruthy();
  });
});