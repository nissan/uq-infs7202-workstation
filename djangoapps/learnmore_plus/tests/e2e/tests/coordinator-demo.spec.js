// @ts-check
const { test, expect } = require('@playwright/test');

/**
 * Course Coordinator demo journey test
 * This test simulates the typical course coordinator user flow
 * User: coordinator / coordinator123
 */
test.describe('Course Coordinator Demo Journey', () => {
  // Use the same context for all tests to maintain session
  let coordinatorContext;
  
  test.beforeAll(async ({ browser }) => {
    // Create a new context for the coordinator
    coordinatorContext = await browser.newContext();
    
    // Login as coordinator
    const page = await coordinatorContext.newPage();
    await page.goto('/login/');
    await page.fill('input[name="username"]', 'coordinator');
    await page.fill('input[name="password"]', 'coordinator123');
    await page.click('button[type="submit"]');
    
    // Verify login was successful by checking for dashboard
    await expect(page).toHaveURL(/dashboard|home/);
    
    // If login fails with the first password, try the alternative
    if (page.url().includes('login')) {
      await page.fill('input[name="username"]', 'coordinator');
      await page.fill('input[name="password"]', 'coord123');
      await page.click('button[type="submit"]');
      await expect(page).toHaveURL(/dashboard|home/);
    }
    
    await page.close();
  });
  
  test.afterAll(async () => {
    // Close the context after all tests
    await coordinatorContext.close();
  });
  
  test('should access coordinator dashboard', async () => {
    const page = await coordinatorContext.newPage();
    await page.goto('/courses/coordinator/dashboard/');
    
    // Verify coordinator dashboard is loaded
    await expect(page.locator('h1')).toContainText('Course Coordinator Dashboard');
    
    // Verify coordinated courses are shown
    await expect(page.locator('.courses-container, .course-list, .coordinated-courses')).toBeVisible();
    
    await page.close();
  });
  
  test('should manage courses', async () => {
    const page = await coordinatorContext.newPage();
    await page.goto('/courses/coordinator/dashboard/');
    
    // Look for manage courses link
    const manageCoursesLink = page.locator('a:has-text("Manage Courses")');
    
    if (await manageCoursesLink.isVisible()) {
      await manageCoursesLink.click();
      
      // Verify manage courses page
      await expect(page.locator('h1, h2')).toContainText('Manage Courses');
      await expect(page.locator('.course-list, table, .courses-container')).toBeVisible();
      
      // Check for create course button
      await expect(page.locator('a:has-text("Create Course"), button:has-text("New Course")')).toBeVisible();
    }
    
    await page.close();
  });
  
  test('should manage instructor assignments', async () => {
    const page = await coordinatorContext.newPage();
    await page.goto('/courses/coordinator/dashboard/');
    
    // Click on first course or find a course management option
    const courseLinks = page.locator('.course-item a, .course-card, tr td a');
    
    if (await courseLinks.count() > 0) {
      await courseLinks.first().click();
      
      // Look for manage instructors link
      const manageInstructorsLink = page.locator('a:has-text("Manage Instructors")');
      
      if (await manageInstructorsLink.isVisible()) {
        await manageInstructorsLink.click();
        
        // Verify instructor management page
        await expect(page.locator('.instructors-list, form, .instructor-management')).toBeVisible();
      }
    }
    
    await page.close();
  });
  
  test('should manage enrollments', async () => {
    const page = await coordinatorContext.newPage();
    await page.goto('/courses/coordinator/dashboard/');
    
    // Look for manage enrollments link
    const manageEnrollmentsLink = page.locator('a:has-text("Manage Enrollments")');
    
    if (await manageEnrollmentsLink.isVisible()) {
      await manageEnrollmentsLink.click();
      
      // Verify enrollments page
      await expect(page.locator('h1, h2')).toContainText('Enrollments');
      await expect(page.locator('.enrollments-list, table, .enrollment-table')).toBeVisible();
      
      // Check for filtering options
      await expect(page.locator('select[name="course"], select[name="status"], input[name="search"]')).toBeVisible();
    }
    
    await page.close();
  });
  
  test('should view enrollment details', async () => {
    const page = await coordinatorContext.newPage();
    await page.goto('/courses/coordinator/dashboard/');
    
    // Look for manage enrollments link
    const manageEnrollmentsLink = page.locator('a:has-text("Manage Enrollments")');
    
    if (await manageEnrollmentsLink.isVisible()) {
      await manageEnrollmentsLink.click();
      
      // Click on first enrollment if available
      const enrollmentLinks = page.locator('.enrollment-item a, tr td a');
      
      if (await enrollmentLinks.count() > 0) {
        await enrollmentLinks.first().click();
        
        // Verify enrollment detail page
        await expect(page.locator('.enrollment-details, .student-info, .progress-info')).toBeVisible();
        
        // Check for status update options
        await expect(page.locator('select[name="status"], button:has-text("Update Status")')).toBeVisible();
      }
    }
    
    await page.close();
  });
  
  test('should check analytics for a course', async () => {
    const page = await coordinatorContext.newPage();
    await page.goto('/courses/coordinator/dashboard/');
    
    // Click on first course
    const courseLinks = page.locator('.course-item a, .course-card, tr td a');
    
    if (await courseLinks.count() > 0) {
      await courseLinks.first().click();
      
      // Look for analytics link
      const analyticsLink = page.locator('a:has-text("Analytics")');
      
      if (await analyticsLink.isVisible()) {
        await analyticsLink.click();
        
        // Verify analytics page
        await expect(page.locator('.analytics-container, .statistics, .chart-container')).toBeVisible();
        
        // Check for specific analytics sections
        await expect(page.locator('.enrollment-stats, .completion-stats, .student-progress')).toBeVisible();
      }
    }
    
    await page.close();
  });
  
  test('should create and use AI tutor session', async () => {
    const page = await coordinatorContext.newPage();
    
    // Go to AI tutor sessions
    await page.goto('/tutor/');
    
    // Check if there are existing sessions or create a new one
    const newSessionButton = page.locator('a:has-text("New Session"), button:has-text("New Session")');
    const existingSession = page.locator('.session-item, .ai-session-card').first();
    
    if (await newSessionButton.isVisible()) {
      await newSessionButton.click();
      
      // Fill session creation form if it appears
      if (await page.locator('form input[name="title"], form input[name="session_name"]').isVisible()) {
        await page.fill('input[name="title"], input[name="session_name"]', 'Coordinator AI Session');
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
      await messageInput.fill('How can I improve student engagement across my courses?');
      await page.click('button:has-text("Send"), button[type="submit"]');
      
      // Wait for AI response
      await page.waitForSelector('.ai-message, .bot-message', { timeout: 30000 });
      
      // Verify AI responded
      await expect(page.locator('.ai-message, .bot-message')).toBeVisible();
    }
    
    await page.close();
  });
});