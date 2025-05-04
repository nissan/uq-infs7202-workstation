// @ts-check
const { test, expect } = require('@playwright/test');

/**
 * Instructor demo journey test
 * This test simulates the typical instructor user flow
 * User: dr.smith / dr.smith123
 */
test.describe('Instructor Demo Journey', () => {
  // Use the same context for all tests to maintain session
  let instructorContext;
  
  test.beforeAll(async ({ browser }) => {
    // Create a new context for the instructor
    instructorContext = await browser.newContext();
    
    // Login as instructor
    const page = await instructorContext.newPage();
    await page.goto('/login/');
    await page.fill('input[name="username"]', 'dr.smith');
    await page.fill('input[name="password"]', 'dr.smith123');
    await page.click('button[type="submit"]');
    
    // Verify login was successful by checking for dashboard
    await expect(page).toHaveURL(/dashboard|home/);
    await page.close();
  });
  
  test.afterAll(async () => {
    // Close the context after all tests
    await instructorContext.close();
  });
  
  test('should access instructor dashboard', async () => {
    const page = await instructorContext.newPage();
    await page.goto('/courses/instructor/dashboard/');
    
    // Verify instructor dashboard is loaded
    await expect(page.locator('h1')).toContainText('Instructor Dashboard');
    
    // Verify courses taught are shown
    await expect(page.locator('.instructor-courses, .teaching-courses')).toBeVisible();
    
    await page.close();
  });
  
  test('should view course management for first course', async () => {
    const page = await instructorContext.newPage();
    await page.goto('/courses/instructor/dashboard/');
    
    // Click on first course
    await page.click('.instructor-courses a, .course-card, tr td a');
    
    // Verify course management page loaded
    await expect(page.locator('h1, h2, .course-title')).toBeVisible();
    
    // Check for course management options
    await expect(page.locator('a:has-text("Manage Content"), a:has-text("Edit Course"), a:has-text("Analytics")')).toBeVisible();
    
    await page.close();
  });
  
  test('should check course analytics', async () => {
    const page = await instructorContext.newPage();
    await page.goto('/courses/instructor/dashboard/');
    
    // Click on first course
    await page.click('.instructor-courses a, .course-card, tr td a');
    
    // Click on analytics
    const analyticsLink = page.locator('a:has-text("Analytics")');
    if (await analyticsLink.isVisible()) {
      await analyticsLink.click();
      
      // Verify analytics page loaded
      await expect(page.locator('.analytics-container, .statistics, .chart-container')).toBeVisible();
    }
    
    await page.close();
  });
  
  test('should manage course content', async () => {
    const page = await instructorContext.newPage();
    await page.goto('/courses/instructor/dashboard/');
    
    // Click on first course
    await page.click('.instructor-courses a, .course-card, tr td a');
    
    // Click on manage content
    const manageContentLink = page.locator('a:has-text("Manage Content")');
    if (await manageContentLink.isVisible()) {
      await manageContentLink.click();
      
      // Verify content management page loaded
      await expect(page.locator('.modules-container, .module-list')).toBeVisible();
      
      // Check for add module/content buttons
      await expect(page.locator('a:has-text("Add Module"), button:has-text("Add Module")')).toBeVisible();
    }
    
    await page.close();
  });
  
  test('should check quiz manager', async () => {
    const page = await instructorContext.newPage();
    await page.goto('/courses/instructor/dashboard/');
    
    // Click on first course
    await page.click('.instructor-courses a, .course-card, tr td a');
    
    // Click on manage content
    const manageContentLink = page.locator('a:has-text("Manage Content")');
    if (await manageContentLink.isVisible()) {
      await manageContentLink.click();
      
      // Try to find a quiz to edit
      const quizLinks = page.locator('a:has-text("Edit Quiz"), a:has-text("Manage Quiz")');
      
      if (await quizLinks.count() > 0) {
        await quizLinks.first().click();
        
        // Verify quiz edit page loaded
        await expect(page.locator('form, .quiz-editor')).toBeVisible();
        
        // Check for question editor
        await expect(page.locator('.question-editor, .questions-container, .quiz-questions')).toBeVisible();
      } else {
        // Try to find a module to potentially add a quiz to
        const moduleEditLinks = page.locator('a:has-text("Edit Module"), a:has-text("Manage Module")');
        
        if (await moduleEditLinks.count() > 0) {
          await moduleEditLinks.first().click();
          
          // Look for an "Add Quiz" button
          const addQuizButton = page.locator('a:has-text("Add Quiz"), button:has-text("Add Quiz")');
          
          if (await addQuizButton.isVisible()) {
            console.log('Found "Add Quiz" button but not testing quiz creation to avoid test data pollution');
          }
        }
      }
    }
    
    await page.close();
  });
  
  test('should check QR code functionality', async () => {
    const page = await instructorContext.newPage();
    await page.goto('/courses/instructor/dashboard/');
    
    // Go to QR code section if available
    await page.goto('/qr/');
    
    // Verify QR code page loaded
    await expect(page.locator('h1')).toContainText('QR Codes');
    
    // Check if there are QR codes displayed
    const qrCodes = page.locator('.qr-code-container, .qr-code-card, img[alt*="QR Code"]');
    const qrCodesVisible = await qrCodes.isVisible();
    
    if (qrCodesVisible) {
      // Click on a QR code detail if available
      await qrCodes.first().click();
      
      // Check for QR code details
      await expect(page.locator('img[alt*="QR Code"]')).toBeVisible();
    }
    
    // Check for QR code statistics if available
    const statsLink = page.locator('a:has-text("Statistics")');
    if (await statsLink.isVisible()) {
      await statsLink.click();
      
      // Verify statistics page loaded
      await expect(page.locator('.statistics-container, .stats-card, .chart-container')).toBeVisible();
    }
    
    await page.close();
  });
  
  test('should use AI tutor as instructor', async () => {
    const page = await instructorContext.newPage();
    
    // Go to AI tutor sessions
    await page.goto('/tutor/');
    
    // Check if there are existing sessions or create a new one
    const newSessionButton = page.locator('a:has-text("New Session"), button:has-text("New Session")');
    const existingSession = page.locator('.session-item, .ai-session-card').first();
    
    if (await newSessionButton.isVisible()) {
      await newSessionButton.click();
      
      // Fill session creation form if it appears
      if (await page.locator('form input[name="title"], form input[name="session_name"]').isVisible()) {
        await page.fill('input[name="title"], input[name="session_name"]', 'Instructor AI Session');
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
      await messageInput.fill('How can I make my course more engaging?');
      await page.click('button:has-text("Send"), button[type="submit"]');
      
      // Wait for AI response
      await page.waitForSelector('.ai-message, .bot-message', { timeout: 30000 });
      
      // Verify AI responded
      await expect(page.locator('.ai-message, .bot-message')).toBeVisible();
    }
    
    await page.close();
  });
});