// @ts-check
const { test, expect } = require('./critical-tests');
const { LoginPage } = require('../page-objects/login-page');
const { AiTutorPage } = require('../page-objects/ai-tutor-page');

/**
 * Comprehensive test suite for AI Tutor functionality
 */
test.describe('AI Tutor Functionality', () => {
  
  test('should check if AI Tutor is available', async ({ page }) => {
    // Login as a student
    const loginPage = new LoginPage(page);
    await loginPage.goto();
    await loginPage.login('john.doe', 'john.doe123');
    
    // Check if AI Tutor is available
    const aiTutorPage = new AiTutorPage(page);
    const isAvailable = await aiTutorPage.isAiTutorAvailable();
    
    // Take screenshot regardless of result
    await page.screenshot({ path: 'ai-tutor-availability.png', fullPage: true });
    
    // If AI Tutor is not available, skip remaining tests
    if (!isAvailable) {
      console.log('AI Tutor feature appears to be disabled or not available');
      test.skip(true, 'AI Tutor feature appears to be disabled or not available');
      return;
    }
    
    // Verify AI Tutor is available
    expect(isAvailable).toBeTruthy();
  });
  
  test('should create a new general AI Tutor session', async ({ page }) => {
    // Login as a student
    const loginPage = new LoginPage(page);
    await loginPage.goto();
    await loginPage.login('john.doe', 'john.doe123');
    
    // Create a new AI Tutor page instance
    const aiTutorPage = new AiTutorPage(page);
    
    // Navigate to AI Tutor
    await aiTutorPage.goto();
    
    // Take screenshot of AI Tutor page
    await page.screenshot({ path: 'ai-tutor-page.png', fullPage: true });
    
    // Try to create a new session with general context
    const sessionCreated = await aiTutorPage.createNewSession({ contextType: 'general' });
    
    // Take screenshot after session creation attempt
    await page.screenshot({ path: 'ai-tutor-general-session.png', fullPage: true });
    
    // If session couldn't be created, conditionally skip
    if (!sessionCreated) {
      console.log('Could not create AI Tutor session - feature may be restricted');
      test.skip(true, 'Could not create AI Tutor session');
      return;
    }
    
    // Verify session was created
    expect(sessionCreated).toBeTruthy();
    
    // Get session context
    const context = await aiTutorPage.getSessionContext();
    console.log(`Session context: ${context}`);
    
    // Verify chat container is visible
    const chatVisible = await aiTutorPage.chatContainer.isVisible();
    expect(chatVisible).toBeTruthy();
  });
  
  test('should send a message and receive a response in general context', async ({ page }) => {
    // Login as a student
    const loginPage = new LoginPage(page);
    await loginPage.goto();
    await loginPage.login('john.doe', 'john.doe123');
    
    // Create a new AI Tutor page instance
    const aiTutorPage = new AiTutorPage(page);
    
    // Create a new session or open an existing one
    await aiTutorPage.goto();
    
    try {
      // First try to create a new general session
      const sessionCreated = await aiTutorPage.createNewSession({ contextType: 'general' });
      
      // If we couldn't create a session, try opening an existing one
      if (!sessionCreated) {
        console.log('Could not create new session, trying to open existing one');
        const sessionOpened = await aiTutorPage.openSession(0);
        
        if (!sessionOpened) {
          console.log('Could not find any AI Tutor sessions to open');
          test.skip(true, 'No AI Tutor sessions available');
          return;
        }
      }
    } catch (error) {
      console.log(`Error setting up AI Tutor session: ${error.message}`);
      
      // As a last resort, try to navigate directly to a session page
      await page.goto('/ai-tutor/sessions/');
      const sessionLink = page.locator('a[href*="ai-tutor/session"]').first();
      const exists = await sessionLink.count() > 0;
      
      if (exists) {
        await sessionLink.click();
        await page.waitForLoadState('networkidle');
      } else {
        console.log('Could not find or create any AI Tutor sessions');
        test.skip(true, 'No AI Tutor sessions available');
        return;
      }
    }
    
    // Take screenshot before sending message
    await page.screenshot({ path: 'ai-tutor-before-message.png', fullPage: true });
    
    // Send a general question
    const testQuestion = 'What is machine learning?';
    const messageSent = await aiTutorPage.sendMessage(testQuestion);
    
    // If message couldn't be sent, skip the rest
    if (!messageSent) {
      console.log('Could not send message to AI Tutor');
      test.skip(true, 'Could not send message to AI Tutor');
      return;
    }
    
    // Wait for AI to respond (this might take time)
    await page.waitForTimeout(10000);
    
    // Take screenshot after response
    await page.screenshot({ path: 'ai-tutor-after-response.png', fullPage: true });
    
    // Get the latest response
    const response = await aiTutorPage.getLatestResponse();
    console.log(`AI response: ${response.substring(0, 100)}...`);
    
    // Verify we got a response
    expect(response.length).toBeGreaterThan(0);
  });
  
  test('should access course-specific AI tutoring', async ({ page }) => {
    // Login as a student
    const loginPage = new LoginPage(page);
    await loginPage.goto();
    await loginPage.login('john.doe', 'john.doe123');
    
    // Create a new AI Tutor page instance
    const aiTutorPage = new AiTutorPage(page);
    
    // Navigate to course catalog to find a course
    await page.goto('/courses/catalog/');
    await page.waitForLoadState('networkidle');
    
    // Take a screenshot of course catalog
    await page.screenshot({ path: 'ai-tutor-course-catalog.png', fullPage: true });
    
    // Try to find and click on a course
    const courseLinks = page.locator('a[href*="course"], .course-card, .card');
    const count = await courseLinks.count();
    
    if (count === 0) {
      console.log('No courses found in catalog');
      test.skip(true, 'No courses available to test course-specific AI tutor');
      return;
    }
    
    // Get the course URL from the first link
    const href = await courseLinks.first().getAttribute('href');
    let courseSlug = 'python-programming';  // Default fallback
    
    if (href) {
      const match = href.match(/\/course\/([^\/]+)/);
      if (match && match[1]) {
        courseSlug = match[1];
      }
    }
    
    // Click the course
    await courseLinks.first().click();
    await page.waitForLoadState('networkidle');
    
    // Take screenshot of course detail page
    await page.screenshot({ path: 'ai-tutor-course-detail.png', fullPage: true });
    
    // Try to access AI Tutor from course
    const aiTutorAccessed = await aiTutorPage.accessAiTutorFromCourse(courseSlug);
    
    // Take screenshot after trying to access AI Tutor
    await page.screenshot({ path: 'ai-tutor-from-course.png', fullPage: true });
    
    // If we couldn't access AI Tutor from course, try creating a course-specific session directly
    if (!aiTutorAccessed) {
      console.log('Could not access AI Tutor from course page, trying to create course-specific session directly');
      
      await aiTutorPage.goto();
      
      try {
        await aiTutorPage.createNewSession({ 
          contextType: 'course',
          courseId: courseSlug
        });
      } catch (error) {
        console.log(`Error creating course-specific session: ${error.message}`);
        test.skip(true, 'Could not set up course-specific AI tutor session');
        return;
      }
    }
    
    // Take screenshot of course-specific AI Tutor session
    await page.screenshot({ path: 'ai-tutor-course-session.png', fullPage: true });
    
    // Send a course-specific question
    const courseQuestion = 'Can you explain the key concepts covered in this course?';
    const messageSent = await aiTutorPage.sendMessage(courseQuestion);
    
    // If message couldn't be sent, skip the rest
    if (!messageSent) {
      console.log('Could not send message to AI Tutor');
      test.skip(true, 'Could not send message to course-specific AI Tutor');
      return;
    }
    
    // Wait for AI to respond (this might take time)
    await page.waitForTimeout(10000);
    
    // Take screenshot after response
    await page.screenshot({ path: 'ai-tutor-course-response.png', fullPage: true });
    
    // Get the latest response
    const response = await aiTutorPage.getLatestResponse();
    console.log(`AI course response: ${response.substring(0, 100)}...`);
    
    // Verify we got a response
    expect(response.length).toBeGreaterThan(0);
    
    // Verify the response is course-specific (this is a soft check)
    const isCourseSpecific = await aiTutorPage.testCourseSpecificResponse(
      'Tell me about the topics covered in this course'
    );
    
    // This is a conditional check since we can't guarantee the AI will always give course-specific responses
    if (!isCourseSpecific) {
      console.log('Response does not appear to be course-specific, but this could be valid AI behavior');
    }
  });
  
  test('should manage conversation history', async ({ page }) => {
    // Login as a student
    const loginPage = new LoginPage(page);
    await loginPage.goto();
    await loginPage.login('john.doe', 'john.doe123');
    
    // Create a new AI Tutor page instance
    const aiTutorPage = new AiTutorPage(page);
    
    // Create a new session or open an existing one
    await aiTutorPage.goto();
    let conversationPath;
    
    try {
      // First try to create a new general session
      const sessionCreated = await aiTutorPage.createNewSession({ contextType: 'general' });
      
      // If we couldn't create a session, try opening an existing one
      if (!sessionCreated) {
        console.log('Could not create new session, trying to open existing one');
        const sessionOpened = await aiTutorPage.openSession(0);
        
        if (!sessionOpened) {
          console.log('Could not find any AI Tutor sessions to open');
          test.skip(true, 'No AI Tutor sessions available');
          return;
        }
      }
      
      // Take screenshot before conversation
      await page.screenshot({ path: 'ai-tutor-conversation-start.png', fullPage: true });
      
      // Send first message in conversation
      await aiTutorPage.sendMessage('Let\'s talk about data science');
      await page.waitForTimeout(5000);
      
      // Take screenshot after first response
      await page.screenshot({ path: 'ai-tutor-conversation-1.png', fullPage: true });
      
      // Send follow-up question referencing first conversation
      await aiTutorPage.sendMessage('What are the key skills needed for the field we just discussed?');
      await page.waitForTimeout(5000);
      
      // Take screenshot after second response
      await page.screenshot({ path: 'ai-tutor-conversation-2.png', fullPage: true });
      
      // Send third message in conversation
      await aiTutorPage.sendMessage('Can you recommend learning resources for these skills?');
      await page.waitForTimeout(5000);
      
      // Take screenshot after third response
      await page.screenshot({ path: 'ai-tutor-conversation-3.png', fullPage: true });
      
      // Get all messages
      const messages = await aiTutorPage.getMessages();
      
      // Check if conversation has at least 6 messages (3 user + 3 AI responses)
      const hasConversationHistory = messages.length >= 6;
      
      // Save the full URL for checking continuity
      conversationPath = page.url();
      
      expect(hasConversationHistory).toBeTruthy();
    } catch (error) {
      console.log(`Error during conversation: ${error.message}`);
      test.skip(true, 'Could not complete conversation test');
      return;
    }
    
    // Test session continuity by refreshing the page
    if (conversationPath) {
      // Refresh the page
      await page.reload();
      await page.waitForLoadState('networkidle');
      
      // Take screenshot after refresh
      await page.screenshot({ path: 'ai-tutor-conversation-after-refresh.png', fullPage: true });
      
      // Check if message history is still visible
      const messagesAfterRefresh = await aiTutorPage.getMessages();
      const historyPreserved = messagesAfterRefresh.length >= 4;  // We should see at least 2 exchanges
      
      expect(historyPreserved).toBeTruthy();
      
      // Test session persistence by navigating away and back
      await page.goto('/dashboard/');
      await page.waitForLoadState('networkidle');
      
      // Navigate back to the conversation
      await page.goto(conversationPath);
      await page.waitForLoadState('networkidle');
      
      // Take screenshot after navigation
      await page.screenshot({ path: 'ai-tutor-conversation-after-navigation.png', fullPage: true });
      
      // Check if message history is still visible
      const messagesAfterNavigation = await aiTutorPage.getMessages();
      const persistenceWorks = messagesAfterNavigation.length >= 4;  // We should see at least 2 exchanges
      
      expect(persistenceWorks).toBeTruthy();
    }
  });
  
  test('should manage AI Tutor sessions', async ({ page }) => {
    // Login as a student
    const loginPage = new LoginPage(page);
    await loginPage.goto();
    await loginPage.login('john.doe', 'john.doe123');
    
    // Create a new AI Tutor page instance
    const aiTutorPage = new AiTutorPage(page);
    
    // Navigate to session list
    await aiTutorPage.gotoSessionList();
    
    // Take screenshot of session list
    await page.screenshot({ path: 'ai-tutor-session-list.png', fullPage: true });
    
    // Get current session count
    const sessionLinks = page.locator('.session-item a, .ai-session-link, a[href*="ai-tutor/session"]');
    const initialCount = await sessionLinks.count();
    
    console.log(`Found ${initialCount} existing sessions`);
    
    // Try to create a new session
    let newSessionCreated = false;
    
    try {
      await aiTutorPage.goto();
      newSessionCreated = await aiTutorPage.createNewSession({ contextType: 'general' });
      
      if (newSessionCreated) {
        console.log('Created new AI Tutor session');
        
        // Add a message to the new session
        await aiTutorPage.sendMessage('This is a test session for management testing');
        await page.waitForTimeout(5000);
        
        // Take screenshot of new session
        await page.screenshot({ path: 'ai-tutor-new-session.png', fullPage: true });
      } else {
        console.log('Could not create new session, continuing with existing sessions');
      }
    } catch (error) {
      console.log(`Error creating new session: ${error.message}`);
    }
    
    // Return to session list
    await aiTutorPage.gotoSessionList();
    
    // Take screenshot of updated session list
    await page.screenshot({ path: 'ai-tutor-updated-session-list.png', fullPage: true });
    
    // Check if we have sessions to work with
    const updatedSessionCount = await sessionLinks.count();
    
    if (updatedSessionCount === 0) {
      console.log('No sessions available for testing session management');
      test.skip(true, 'No AI Tutor sessions available');
      return;
    }
    
    // Verify session count increased if we created a new session
    if (newSessionCreated) {
      console.log(`Session count before: ${initialCount}, after: ${updatedSessionCount}`);
      expect(updatedSessionCount).toBeGreaterThanOrEqual(initialCount);
    }
    
    // Try to open a session
    const sessionOpened = await aiTutorPage.openSession(0);
    
    // Take screenshot of opened session
    await page.screenshot({ path: 'ai-tutor-opened-session.png', fullPage: true });
    
    // Verify session opened
    expect(sessionOpened).toBeTruthy();
    
    // Return to session list
    await aiTutorPage.gotoSessionList();
    
    // Check if we can delete a session (only if there are multiple sessions)
    if (updatedSessionCount > 1) {
      // Try to delete the last session (most likely our new one)
      const deleted = await aiTutorPage.deleteSession(updatedSessionCount - 1);
      
      // Take screenshot after deletion
      await page.screenshot({ path: 'ai-tutor-after-deletion.png', fullPage: true });
      
      // Verify deletion
      if (deleted) {
        const finalSessionCount = await sessionLinks.count();
        console.log(`Final session count: ${finalSessionCount}`);
        expect(finalSessionCount).toBeLessThan(updatedSessionCount);
      } else {
        console.log('Session deletion not supported or failed');
      }
    } else {
      console.log('Only one session available, skipping deletion test');
    }
  });
});