// @ts-check

/**
 * AiTutorPage class representing the AI Tutor interface and functionality
 */
class AiTutorPage {
  /**
   * @param {import('@playwright/test').Page} page 
   */
  constructor(page) {
    this.page = page;
    this.chatContainer = page.locator('.chat-container, .ai-tutor-chat');
    this.messageInput = page.locator('textarea[name="message"], .message-input');
    this.sendButton = page.locator('button[type="submit"], button:has-text("Send"), .send-message-btn');
    this.messages = page.locator('.message, .chat-message');
    this.userMessages = page.locator('.message.user, .user-message');
    this.tutorMessages = page.locator('.message.tutor, .ai-message, .assistant-message');
    this.sessionList = page.locator('.session-list, .ai-sessions');
    this.newSessionButton = page.locator('a:has-text("New Session"), button:has-text("New Session"), a:has-text("Create Session")');
    this.sessionTitle = page.locator('.session-title, h1:has-text("AI Tutor")');
    this.contextSelector = page.locator('select[name="context_type"], .context-selector');
    this.courseSelector = page.locator('select[name="course"], .course-selector');
    this.moduleSelector = page.locator('select[name="module"], .module-selector');
    this.loadingIndicator = page.locator('.loading-indicator, .typing-indicator, .ai-typing');
    this.contextBadge = page.locator('.context-badge, .session-context');
    this.aiTutorButton = page.locator('a:has-text("AI Tutor"), .ai-tutor-button, [href*="ai-tutor"]');
    this.errorMessage = page.locator('.error-message, .alert-error');
  }

  /**
   * Navigate to AI Tutor page
   */
  async goto() {
    await this.page.goto('/ai-tutor/');
    await this.page.waitForLoadState('networkidle');
  }

  /**
   * Navigate to AI Tutor session list
   */
  async gotoSessionList() {
    await this.page.goto('/ai-tutor/sessions/');
    await this.page.waitForLoadState('networkidle');
  }

  /**
   * Create a new AI Tutor session
   * @param {Object} options
   * @param {string} options.contextType - 'general', 'course', 'module', or 'content'
   * @param {string} [options.courseId] - Required if contextType is 'course', 'module', or 'content'
   * @param {string} [options.moduleId] - Required if contextType is 'module' or 'content'
   * @param {string} [options.contentId] - Required if contextType is 'content'
   */
  async createNewSession(options) {
    // Navigate to create session page
    await this.page.goto('/ai-tutor/create-session/');
    await this.page.waitForLoadState('networkidle');
    
    // Select context type
    try {
      await this.contextSelector.selectOption(options.contextType);
      console.log(`Selected context type: ${options.contextType}`);
    } catch (error) {
      console.log(`Error selecting context type: ${error.message}`);
      
      // Try clicking a radio button or other selection method if dropdown fails
      const contextTypeOptions = this.page.locator(`input[name="context_type"][value="${options.contextType}"], .context-option:has-text("${options.contextType}")`);
      const count = await contextTypeOptions.count();
      
      if (count > 0) {
        await contextTypeOptions.first().click();
        console.log(`Clicked context type option: ${options.contextType}`);
      }
    }
    
    // If course context is needed, select a course
    if (options.contextType !== 'general' && options.courseId) {
      try {
        await this.courseSelector.selectOption(options.courseId);
        console.log(`Selected course ID: ${options.courseId}`);
      } catch (error) {
        console.log(`Error selecting course: ${error.message}`);
        
        // Try clicking a course option if dropdown fails
        const courseOptions = this.page.locator(`input[name="course"][value="${options.courseId}"], .course-option:has-text("${options.courseId}")`);
        const count = await courseOptions.count();
        
        if (count > 0) {
          await courseOptions.first().click();
          console.log(`Clicked course option: ${options.courseId}`);
        }
      }
    }
    
    // If module context is needed, select a module
    if ((options.contextType === 'module' || options.contextType === 'content') && options.moduleId) {
      try {
        await this.moduleSelector.selectOption(options.moduleId);
        console.log(`Selected module ID: ${options.moduleId}`);
      } catch (error) {
        console.log(`Error selecting module: ${error.message}`);
        
        // Try clicking a module option if dropdown fails
        const moduleOptions = this.page.locator(`input[name="module"][value="${options.moduleId}"], .module-option:has-text("${options.moduleId}")`);
        const count = await moduleOptions.count();
        
        if (count > 0) {
          await moduleOptions.first().click();
          console.log(`Clicked module option: ${options.moduleId}`);
        }
      }
    }
    
    // If content context is needed, select a content item
    if (options.contextType === 'content' && options.contentId) {
      try {
        const contentSelector = this.page.locator('select[name="content"], .content-selector');
        await contentSelector.selectOption(options.contentId);
        console.log(`Selected content ID: ${options.contentId}`);
      } catch (error) {
        console.log(`Error selecting content: ${error.message}`);
        
        // Try clicking a content option if dropdown fails
        const contentOptions = this.page.locator(`input[name="content"][value="${options.contentId}"], .content-option:has-text("${options.contentId}")`);
        const count = await contentOptions.count();
        
        if (count > 0) {
          await contentOptions.first().click();
          console.log(`Clicked content option: ${options.contentId}`);
        }
      }
    }
    
    // Submit the form
    const submitButton = this.page.locator('button[type="submit"], input[type="submit"], button:has-text("Create")');
    await submitButton.click();
    await this.page.waitForLoadState('networkidle');
    
    // Check if we're now in a chat session
    const isChatPage = await this.chatContainer.isVisible().catch(() => false);
    return isChatPage;
  }

  /**
   * Open an AI Tutor session from the session list
   * @param {number} index - Index of the session to open (0-based)
   */
  async openSession(index = 0) {
    await this.gotoSessionList();
    
    const sessionLinks = this.page.locator('.session-item a, .ai-session-link, a[href*="ai-tutor/session"]');
    const count = await sessionLinks.count();
    
    if (count > 0) {
      if (index < count) {
        await sessionLinks.nth(index).click();
        await this.page.waitForLoadState('networkidle');
        return true;
      } else {
        console.log(`Session index ${index} is out of range (found ${count} sessions)`);
        return false;
      }
    } else {
      console.log('No sessions found in the list');
      return false;
    }
  }

  /**
   * Send a message to the AI Tutor
   * @param {string} message 
   * @returns {Promise<boolean>} True if message was sent successfully
   */
  async sendMessage(message) {
    try {
      // Wait for input to be enabled
      await this.messageInput.waitFor({ state: 'visible', timeout: 5000 });
      
      // Fill the message input
      await this.messageInput.fill(message);
      
      // Click the send button
      await this.sendButton.click();
      
      // Wait for the message to appear in the chat
      const messageSent = await this.page.waitForSelector(`:text("${message}")`, { 
        state: 'visible',
        timeout: 10000
      }).then(() => true).catch(() => false);
      
      // Wait for loading indicator to disappear if it's present
      const loadingExists = await this.loadingIndicator.count() > 0;
      if (loadingExists) {
        await this.page.waitForSelector('.loading-indicator, .typing-indicator, .ai-typing', { 
          state: 'hidden',
          timeout: 30000
        }).catch(() => console.log('Loading indicator did not disappear within timeout'));
      }
      
      // Wait a bit for response to complete
      await this.page.waitForTimeout(2000);
      
      return messageSent;
    } catch (error) {
      console.log(`Error sending message: ${error.message}`);
      return false;
    }
  }

  /**
   * Get all messages in the chat
   * @returns {Promise<Array<{role: string, text: string}>>}
   */
  async getMessages() {
    const messages = [];
    
    // Get user messages
    const userMsgs = await this.userMessages.all();
    for (const msg of userMsgs) {
      const text = await msg.innerText();
      messages.push({ role: 'user', text });
    }
    
    // Get tutor messages
    const tutorMsgs = await this.tutorMessages.all();
    for (const msg of tutorMsgs) {
      const text = await msg.innerText();
      messages.push({ role: 'assistant', text });
    }
    
    // Sort messages by their position in the DOM to maintain chronological order
    messages.sort(async (a, b) => {
      const aElement = await this.page.locator(`:text("${a.text}")`).first();
      const bElement = await this.page.locator(`:text("${b.text}")`).first();
      
      const aBox = await aElement.boundingBox();
      const bBox = await bElement.boundingBox();
      
      if (!aBox || !bBox) return 0;
      return aBox.y - bBox.y;
    });
    
    return messages;
  }

  /**
   * Get the most recent AI Tutor response
   * @returns {Promise<string>}
   */
  async getLatestResponse() {
    const tutorMessages = await this.tutorMessages.all();
    if (tutorMessages.length > 0) {
      const latestMessage = tutorMessages[tutorMessages.length - 1];
      return await latestMessage.innerText();
    }
    return '';
  }

  /**
   * Get the context of the current AI Tutor session
   * @returns {Promise<string>}
   */
  async getSessionContext() {
    try {
      const contextText = await this.contextBadge.innerText();
      return contextText;
    } catch (error) {
      console.log(`Error getting session context: ${error.message}`);
      return 'Unknown';
    }
  }

  /**
   * Check if AI Tutor is available by looking for the AI Tutor button
   * @returns {Promise<boolean>}
   */
  async isAiTutorAvailable() {
    try {
      await this.page.goto('/dashboard/');
      await this.page.waitForLoadState('networkidle');
      
      const buttonExists = await this.aiTutorButton.count() > 0;
      return buttonExists;
    } catch (error) {
      console.log(`Error checking if AI Tutor is available: ${error.message}`);
      return false;
    }
  }

  /**
   * Delete a session from the session list
   * @param {number} index - Index of the session to delete (0-based)
   */
  async deleteSession(index = 0) {
    await this.gotoSessionList();
    
    const deleteButtons = this.page.locator('.delete-session, .delete-button, a:has-text("Delete")');
    const count = await deleteButtons.count();
    
    if (count > 0) {
      if (index < count) {
        await deleteButtons.nth(index).click();
        
        // Handle confirmation dialog if it appears
        try {
          const confirmButton = this.page.locator('button:has-text("Confirm"), button:has-text("Yes"), button:has-text("Delete")');
          const hasConfirm = await confirmButton.count() > 0;
          
          if (hasConfirm) {
            await confirmButton.click();
          }
        } catch (error) {
          console.log(`No confirmation dialog appeared: ${error.message}`);
        }
        
        await this.page.waitForLoadState('networkidle');
        return true;
      } else {
        console.log(`Session index ${index} is out of range (found ${count} sessions)`);
        return false;
      }
    } else {
      console.log('No delete buttons found');
      return false;
    }
  }

  /**
   * Access AI Tutor from a course detail page
   * @param {string} courseSlug - The course slug or ID
   * @returns {Promise<boolean>} - True if successfully accessed AI tutor
   */
  async accessAiTutorFromCourse(courseSlug) {
    try {
      // Navigate to course detail page
      await this.page.goto(`/courses/course/${courseSlug}/`);
      await this.page.waitForLoadState('networkidle');
      
      // Look for AI Tutor button on course page
      const aiTutorButtons = [
        'a:has-text("Get AI Tutor Help")',
        'a:has-text("AI Tutor")',
        '.ai-tutor-link',
        'a[href*="ai-tutor"]',
        '.sidebar a:has-text("Tutor")'
      ];
      
      for (const selector of aiTutorButtons) {
        const button = this.page.locator(selector);
        const exists = await button.count() > 0;
        
        if (exists) {
          await button.click();
          await this.page.waitForLoadState('networkidle');
          
          // Check if we're now in a tutor session
          const isInSession = await this.chatContainer.isVisible().catch(() => false);
          return isInSession;
        }
      }
      
      console.log('Could not find AI Tutor button on course page');
      return false;
    } catch (error) {
      console.log(`Error accessing AI Tutor from course: ${error.message}`);
      return false;
    }
  }

  /**
   * Test if the AI Tutor responds to a course-specific question
   * @param {string} courseSpecificQuestion - A question about the course content
   * @returns {Promise<boolean>} - True if the response appears to be course-specific
   */
  async testCourseSpecificResponse(courseSpecificQuestion) {
    const sent = await this.sendMessage(courseSpecificQuestion);
    if (!sent) {
      return false;
    }
    
    // Wait for response to complete
    await this.page.waitForTimeout(5000);
    
    // Get the response
    const response = await this.getLatestResponse();
    
    // Check if the response mentions course-related terms
    const isCourseSpecific = response.includes('course') || 
                             response.includes('module') || 
                             response.includes('learning') ||
                             response.includes('lesson') ||
                             response.includes('content');
    
    return isCourseSpecific;
  }
}

module.exports = { AiTutorPage };