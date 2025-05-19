// @ts-check

/**
 * AssignmentPage class representing assignment-related actions and elements
 */
class AssignmentPage {
  /**
   * @param {import('@playwright/test').Page} page 
   */
  constructor(page) {
    this.page = page;
    this.assignmentTitle = page.locator('.assignment-title, h1:has-text("Assignment")');
    this.assignmentDescription = page.locator('.assignment-description, .description');
    this.submissionForm = page.locator('form.submission-form, form:has([name="submission"])');
    this.fileUploadInput = page.locator('input[type="file"], input[name="file"]');
    this.textSubmissionInput = page.locator('textarea[name="text_submission"], .text-submission');
    this.submitButton = page.locator('button[type="submit"], button:has-text("Submit")');
    this.feedbackSection = page.locator('.feedback, .grading-feedback');
    this.gradeDisplay = page.locator('.grade, .assignment-grade');
    this.statusBadge = page.locator('.status-badge, .assignment-status');
    this.dueDateDisplay = page.locator('.due-date, .deadline');
    this.attachmentsSection = page.locator('.attachments, .assignment-files');
    this.createAssignmentForm = page.locator('form:has(input[name="title"]), form.assignment-form');
    this.assignmentTitleInput = page.locator('input[name="title"], #id_title');
    this.assignmentDescriptionInput = page.locator('textarea[name="description"], #id_description');
    this.dueDateInput = page.locator('input[name="due_date"], #id_due_date');
    this.pointsInput = page.locator('input[name="points"], #id_points');
    this.assignmentList = page.locator('.assignment-list, table:has(.assignment)');
  }

  /**
   * Navigate to a specific assignment
   * @param {string} assignmentId 
   */
  async gotoAssignment(assignmentId) {
    await this.page.goto(`/courses/assignment/${assignmentId}/`);
    await this.page.waitForLoadState('networkidle');
  }

  /**
   * Navigate to assignment creation page for a course
   * @param {string} courseId 
   */
  async gotoCreateAssignment(courseId) {
    await this.page.goto(`/courses/course/${courseId}/assignment/create/`);
    await this.page.waitForLoadState('networkidle');
  }

  /**
   * Navigate to assignment list for a course
   * @param {string} courseId 
   */
  async gotoAssignmentList(courseId) {
    await this.page.goto(`/courses/course/${courseId}/assignments/`);
    await this.page.waitForLoadState('networkidle');
  }

  /**
   * Create a new assignment
   * @param {Object} assignmentData 
   * @param {string} assignmentData.title
   * @param {string} assignmentData.description
   * @param {string} assignmentData.dueDate - In format YYYY-MM-DD
   * @param {number} assignmentData.points
   */
  async createAssignment(assignmentData) {
    await this.assignmentTitleInput.fill(assignmentData.title);
    await this.assignmentDescriptionInput.fill(assignmentData.description);
    
    // Set due date
    await this.dueDateInput.fill(assignmentData.dueDate);
    
    // Set points
    await this.pointsInput.fill(assignmentData.points.toString());
    
    // Submit the form
    await this.submitButton.click();
    await this.page.waitForLoadState('networkidle');
  }

  /**
   * Submit a text assignment
   * @param {string} textSubmission 
   */
  async submitTextAssignment(textSubmission) {
    await this.textSubmissionInput.fill(textSubmission);
    await this.submitButton.click();
    await this.page.waitForLoadState('networkidle');
  }

  /**
   * Submit a file assignment
   * @param {string} filePath - Path to the file to upload
   */
  async submitFileAssignment(filePath) {
    await this.fileUploadInput.setInputFiles(filePath);
    await this.submitButton.click();
    await this.page.waitForLoadState('networkidle');
  }

  /**
   * Get the current assignment status
   * @returns {Promise<string>}
   */
  async getAssignmentStatus() {
    try {
      return await this.statusBadge.innerText();
    } catch (error) {
      console.log(`Error getting assignment status: ${error.message}`);
      return 'Unknown';
    }
  }

  /**
   * Get the assignment grade
   * @returns {Promise<string>}
   */
  async getAssignmentGrade() {
    try {
      return await this.gradeDisplay.innerText();
    } catch (error) {
      console.log(`Error getting assignment grade: ${error.message}`);
      return 'Not graded';
    }
  }

  /**
   * Get feedback for the assignment
   * @returns {Promise<string>}
   */
  async getAssignmentFeedback() {
    try {
      return await this.feedbackSection.innerText();
    } catch (error) {
      console.log(`Error getting assignment feedback: ${error.message}`);
      return '';
    }
  }

  /**
   * Grade an assignment (instructor action)
   * @param {Object} gradingData 
   * @param {number} gradingData.score
   * @param {string} gradingData.feedback
   */
  async gradeAssignment(gradingData) {
    // Look for grade input
    const gradeInput = this.page.locator('input[name="grade"], input[name="score"], #id_score');
    await gradeInput.fill(gradingData.score.toString());
    
    // Look for feedback input
    const feedbackInput = this.page.locator('textarea[name="feedback"], #id_feedback');
    await feedbackInput.fill(gradingData.feedback);
    
    // Submit the grading form
    const saveButton = this.page.locator('button:has-text("Save"), button:has-text("Submit Grade")');
    await saveButton.click();
    await this.page.waitForLoadState('networkidle');
  }

  /**
   * Get all assignments for a course
   * @param {string} courseId 
   * @returns {Promise<Array<{id: string, title: string, status: string}>>}
   */
  async getAssignments(courseId) {
    await this.gotoAssignmentList(courseId);
    
    const assignmentLinks = this.page.locator('a[href*="/assignment/"]');
    const count = await assignmentLinks.count();
    
    const assignments = [];
    
    for (let i = 0; i < count; i++) {
      const link = assignmentLinks.nth(i);
      const href = await link.getAttribute('href');
      const title = await link.innerText();
      
      if (href) {
        const match = href.match(/\/assignment\/(\d+)/);
        if (match && match[1]) {
          // Try to get status if available
          let status = 'Unknown';
          try {
            const statusElement = link.locator('xpath=./ancestor::tr/td[contains(@class, "status")]').first();
            if (await statusElement.count() > 0) {
              status = await statusElement.innerText();
            }
          } catch (error) {
            // Ignore errors when trying to get status
          }
          
          assignments.push({
            id: match[1],
            title: title,
            status: status
          });
        }
      }
    }
    
    return assignments;
  }

  /**
   * Check if assignments are available for a course
   * @param {string} courseId 
   * @returns {Promise<boolean>}
   */
  async hasAssignments(courseId) {
    try {
      const assignments = await this.getAssignments(courseId);
      return assignments.length > 0;
    } catch (error) {
      console.log(`Error checking for assignments: ${error.message}`);
      return false;
    }
  }

  /**
   * Find an assignment from the course page
   * @param {string} courseId
   * @returns {Promise<boolean>} - True if found and navigated to an assignment
   */
  async findAssignmentFromCourse(courseId) {
    try {
      // Navigate to course detail page
      await this.page.goto(`/courses/course/${courseId}/`);
      await this.page.waitForLoadState('networkidle');
      
      // Look for assignment links
      const assignmentSelectors = [
        'a:has-text("Assignments")',
        'a:has-text("Assignment")',
        'a[href*="assignment"]',
        '.assignment-link',
        '.nav-item:has-text("Assignment")'
      ];
      
      for (const selector of assignmentSelectors) {
        const links = this.page.locator(selector);
        const count = await links.count();
        
        if (count > 0) {
          await links.first().click();
          await this.page.waitForLoadState('networkidle');
          
          // Check if we're on an assignment list or detail page
          const isAssignmentPage = 
            await this.page.url().includes('assignment') ||
            await this.assignmentList.isVisible().catch(() => false) ||
            await this.assignmentTitle.isVisible().catch(() => false);
          
          if (isAssignmentPage) {
            // If we're on a list page, try to click the first assignment
            if (await this.assignmentList.isVisible().catch(() => false)) {
              const assignmentLinks = this.page.locator('a[href*="/assignment/"]');
              const linkCount = await assignmentLinks.count();
              
              if (linkCount > 0) {
                await assignmentLinks.first().click();
                await this.page.waitForLoadState('networkidle');
              }
            }
            
            return true;
          }
        }
      }
      
      // If we still haven't found assignments, try the assignments URL directly
      await this.gotoAssignmentList(courseId);
      
      // Check if we have assignments listed
      const assignmentLinks = this.page.locator('a[href*="/assignment/"]');
      const count = await assignmentLinks.count();
      
      if (count > 0) {
        await assignmentLinks.first().click();
        await this.page.waitForLoadState('networkidle');
        return true;
      }
      
      console.log('Could not find any assignments for this course');
      return false;
    } catch (error) {
      console.log(`Error finding assignment from course: ${error.message}`);
      return false;
    }
  }
}

module.exports = { AssignmentPage };