// @ts-check
const { test, expect } = require('@playwright/test');

/**
 * Admin demo journey test
 * This test simulates the typical admin user flow
 * User: admin / admin123
 */
test.describe('Admin Demo Journey', () => {
  // Use the same context for all tests to maintain session
  let adminContext;
  
  test.beforeAll(async ({ browser }) => {
    // Create a new context for the admin
    adminContext = await browser.newContext();
    
    // Login as admin
    const page = await adminContext.newPage();
    await page.goto('/login/');
    await page.fill('input[name="username"]', 'admin');
    await page.fill('input[name="password"]', 'admin123');
    await page.click('button[type="submit"]');
    
    // Verify login was successful by checking for dashboard
    await expect(page).toHaveURL(/dashboard|home/);
    await page.close();
  });
  
  test.afterAll(async () => {
    // Close the context after all tests
    await adminContext.close();
  });
  
  test('should access admin dashboard', async () => {
    const page = await adminContext.newPage();
    await page.goto('/courses/admin/dashboard/');
    
    // Verify admin dashboard is loaded
    await expect(page.locator('h1')).toContainText('Admin Dashboard');
    
    // Verify key admin sections are available
    await expect(page.locator('.admin-statistics, .admin-panel, .system-stats')).toBeVisible();
    
    await page.close();
  });
  
  test('should access system admin and activity log', async () => {
    const page = await adminContext.newPage();
    
    // Try to access the system admin dashboard
    await page.goto('/dashboard/home');
    
    // Verify system admin dashboard is loaded
    await expect(page.locator('h1')).toContainText('System Dashboard');
    
    // Check activity log
    const activityLogLink = page.locator('a:has-text("Activity Log")');
    if (await activityLogLink.isVisible()) {
      await activityLogLink.click();
      
      // Verify activity log page
      await expect(page.locator('h1')).toContainText('Activity Log');
      await expect(page.locator('.activity-table, .activity-log')).toBeVisible();
    }
    
    await page.close();
  });
  
  test('should access system health dashboard', async () => {
    const page = await adminContext.newPage();
    
    // Try to access the system health dashboard
    await page.goto('/dashboard/system-health');
    
    // Verify system health dashboard is loaded
    await expect(page.locator('h1')).toContainText('System Health');
    
    // Check for health metrics
    await expect(page.locator('.health-metrics, .system-metrics, .health-cards')).toBeVisible();
    
    await page.close();
  });
  
  test('should access user management', async () => {
    const page = await adminContext.newPage();
    
    // Try to access the users dashboard
    await page.goto('/dashboard/users');
    
    // Verify users dashboard is loaded
    await expect(page.locator('h1')).toContainText('Users');
    
    // Check for user list
    await expect(page.locator('.user-list, .users-table, table')).toBeVisible();
    
    await page.close();
  });
  
  test('should check course management as admin', async () => {
    const page = await adminContext.newPage();
    await page.goto('/courses/admin/dashboard/');
    
    // Look for course list
    const courses = page.locator('.course-list, .course-table, tr td a');
    
    if (await courses.count() > 0) {
      // Click on first course
      await courses.first().click();
      
      // Verify course management page
      await expect(page.locator('h1, h2, .course-title')).toBeVisible();
      
      // Check for admin-specific actions
      await expect(page.locator('a:has-text("Delete Course"), button:has-text("Delete"), a:has-text("Edit Permissions")')).toBeVisible();
    }
    
    await page.close();
  });
  
  test('should check course creation capability', async () => {
    const page = await adminContext.newPage();
    await page.goto('/courses/admin/dashboard/');
    
    // Look for create course button
    const createButton = page.locator('a:has-text("Create Course"), button:has-text("New Course")');
    
    if (await createButton.isVisible()) {
      await createButton.click();
      
      // Verify course creation form
      await expect(page.locator('form, .course-form')).toBeVisible();
      await expect(page.locator('input[name="title"]')).toBeVisible();
      
      // Don't submit the form to avoid creating test data
    }
    
    await page.close();
  });
  
  test('should check group management', async () => {
    const page = await adminContext.newPage();
    
    // Try to access group management
    await page.goto('/accounts/groups/');
    
    // Verify groups page
    if (await page.locator('h1, h2').filter({ hasText: 'Groups' }).isVisible()) {
      await expect(page.locator('.group-list, table')).toBeVisible();
      
      // Click on first group
      const groups = page.locator('.group-item a, tr td a');
      
      if (await groups.count() > 0) {
        await groups.first().click();
        
        // Verify group detail page
        await expect(page.locator('.group-details, .group-info')).toBeVisible();
        
        // Check for edit permission link
        await expect(page.locator('a:has-text("Edit Permissions"), a:has-text("Manage Permissions")')).toBeVisible();
      }
    }
    
    await page.close();
  });
  
  test('should check QR code management', async () => {
    const page = await adminContext.newPage();
    
    // Go to QR code section
    await page.goto('/qr/');
    
    // Verify QR code page
    await expect(page.locator('h1')).toContainText('QR Codes');
    
    // Check for admin-specific QR features
    await expect(page.locator('a:has-text("Statistics"), a:has-text("Print QR Codes")')).toBeVisible();
    
    // Check QR code statistics
    const statsLink = page.locator('a:has-text("Statistics")');
    if (await statsLink.isVisible()) {
      await statsLink.click();
      
      // Verify statistics page
      await expect(page.locator('.statistics, .stats-container, .chart-container')).toBeVisible();
    }
    
    await page.close();
  });
  
  test('should create and use AI tutor session', async () => {
    const page = await adminContext.newPage();
    
    // Go to AI tutor sessions
    await page.goto('/tutor/');
    
    // Check if there are existing sessions or create a new one
    const newSessionButton = page.locator('a:has-text("New Session"), button:has-text("New Session")');
    
    if (await newSessionButton.isVisible()) {
      await newSessionButton.click();
      
      // Fill session creation form if it appears
      if (await page.locator('form input[name="title"], form input[name="session_name"]').isVisible()) {
        await page.fill('input[name="title"], input[name="session_name"]', 'Admin AI Session');
        await page.click('button[type="submit"]');
      }
      
      // Verify chat interface loaded
      await expect(page.locator('.chat-container, .message-list')).toBeVisible();
      
      // Send a test message
      const messageInput = page.locator('textarea, input[type="text"]').filter({ hasText: '' });
      if (await messageInput.isVisible()) {
        await messageInput.fill('What admin features are available in the system?');
        await page.click('button:has-text("Send"), button[type="submit"]');
        
        // Wait for AI response
        await page.waitForSelector('.ai-message, .bot-message', { timeout: 30000 });
        
        // Verify AI responded
        await expect(page.locator('.ai-message, .bot-message')).toBeVisible();
      }
    }
    
    await page.close();
  });
});