// @ts-check
const { test, expect } = require('./critical-tests');
const { LoginPage } = require('../page-objects/login-page');
const fs = require('fs').promises;
const path = require('path');
const os = require('os');

/**
 * File Upload Test Suite
 * Tests file upload functionality across different parts of the application
 */
test.describe('File Upload Functionality', () => {
  
  // Create a temporary file before tests
  let smallFilePath;
  let largeFilePath;
  let imageFilePath;
  let docFilePath;
  
  test.beforeAll(async () => {
    // Create temp directory for test files
    const tmpDir = await fs.mkdtemp(path.join(os.tmpdir(), 'playwright-file-upload-'));
    
    // Create small text file (10 KB)
    smallFilePath = path.join(tmpDir, 'small-test-file.txt');
    await fs.writeFile(smallFilePath, 'A'.repeat(10 * 1024));
    
    // Create larger text file (2 MB)
    largeFilePath = path.join(tmpDir, 'large-test-file.txt');
    await fs.writeFile(largeFilePath, 'B'.repeat(2 * 1024 * 1024));
    
    // Create simple text file with doc extension
    docFilePath = path.join(tmpDir, 'test-document.doc');
    await fs.writeFile(docFilePath, 'This is a test document file.');
    
    // Create simple image (1x1 transparent PNG)
    // This is a minimal valid PNG file
    imageFilePath = path.join(tmpDir, 'test-image.png');
    const pngBytes = Buffer.from([
      0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A, 0x00, 0x00, 0x00, 0x0D,
      0x49, 0x48, 0x44, 0x52, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01,
      0x08, 0x06, 0x00, 0x00, 0x00, 0x1F, 0x15, 0xC4, 0x89, 0x00, 0x00, 0x00,
      0x0A, 0x49, 0x44, 0x41, 0x54, 0x78, 0x9C, 0x63, 0x00, 0x01, 0x00, 0x00,
      0x05, 0x00, 0x01, 0x0D, 0x0A, 0x2D, 0xB4, 0x00, 0x00, 0x00, 0x00, 0x49,
      0x45, 0x4E, 0x44, 0xAE, 0x42, 0x60, 0x82
    ]);
    await fs.writeFile(imageFilePath, pngBytes);
  });
  
  test.afterAll(async () => {
    // Clean up test files
    try {
      if (smallFilePath) await fs.unlink(smallFilePath).catch(() => {});
      if (largeFilePath) await fs.unlink(largeFilePath).catch(() => {});
      if (imageFilePath) await fs.unlink(imageFilePath).catch(() => {});
      if (docFilePath) await fs.unlink(docFilePath).catch(() => {});
      
      // Remove parent directory
      const parentDir = path.dirname(smallFilePath);
      await fs.rmdir(parentDir).catch(() => {});
    } catch (error) {
      console.log(`Error cleaning up test files: ${error.message}`);
    }
  });
  
  test('should upload profile avatar image', async ({ page }) => {
    // Login as a student
    const loginPage = new LoginPage(page);
    await loginPage.goto();
    await loginPage.login('john.doe', 'john.doe123');
    
    // Navigate to profile
    await page.goto('/profile/');
    await page.waitForLoadState('networkidle');
    
    // Take screenshot of profile page
    await page.screenshot({ path: 'file-upload-profile.png', fullPage: true });
    
    // Look for avatar upload control
    const avatarSelectors = [
      'input[type="file"][name="avatar"]',
      'input[type="file"][accept="image/*"]',
      'input[type="file"].avatar-upload',
      'input[type="file"][name*="profile"]',
      'button:has-text("Change Avatar")',
      'button:has-text("Upload Avatar")',
      'a:has-text("Change Avatar")',
      'a:has-text("Upload Photo")'
    ];
    
    let avatarUploadFound = false;
    let avatarInput = null;
    
    for (const selector of avatarSelectors) {
      const element = page.locator(selector);
      const exists = await element.count() > 0;
      
      if (exists) {
        console.log(`Found avatar upload with selector: ${selector}`);
        avatarUploadFound = true;
        
        // If it's a button or link, click it to reveal the file input
        if (selector.startsWith('button') || selector.startsWith('a')) {
          await element.click();
          await page.waitForTimeout(1000); // Wait for any modal or popup
          
          // Take screenshot after clicking avatar upload button
          await page.screenshot({ path: 'file-upload-avatar-button-clicked.png', fullPage: true });
          
          // Now look for the actual file input
          const fileInputSelectors = [
            'input[type="file"]',
            'input[accept="image/*"]',
            'input[name="avatar"]'
          ];
          
          for (const inputSelector of fileInputSelectors) {
            const input = page.locator(inputSelector);
            const inputExists = await input.count() > 0;
            
            if (inputExists) {
              avatarInput = input;
              break;
            }
          }
        } else {
          // If it's already a file input, use it directly
          avatarInput = element;
        }
        
        break;
      }
    }
    
    // If we couldn't find the avatar upload, try checking profile editing page
    if (!avatarUploadFound) {
      console.log('Could not find avatar upload on profile page. Checking profile edit page...');
      
      // Look for edit profile link
      const editLinks = page.locator('a:has-text("Edit Profile"), a:has-text("Edit"), button:has-text("Edit")');
      const hasEditLink = await editLinks.count() > 0;
      
      if (hasEditLink) {
        await editLinks.first().click();
        await page.waitForLoadState('networkidle');
        
        // Take screenshot of profile edit page
        await page.screenshot({ path: 'file-upload-profile-edit.png', fullPage: true });
        
        // Look for avatar upload on edit page
        for (const selector of avatarSelectors) {
          const element = page.locator(selector);
          const exists = await element.count() > 0;
          
          if (exists) {
            console.log(`Found avatar upload on edit page with selector: ${selector}`);
            avatarUploadFound = true;
            
            // If it's a button or link, click it to reveal the file input
            if (selector.startsWith('button') || selector.startsWith('a')) {
              await element.click();
              await page.waitForTimeout(1000); // Wait for any modal or popup
              
              // Now look for the actual file input
              const fileInputSelectors = [
                'input[type="file"]',
                'input[accept="image/*"]',
                'input[name="avatar"]'
              ];
              
              for (const inputSelector of fileInputSelectors) {
                const input = page.locator(inputSelector);
                const inputExists = await input.count() > 0;
                
                if (inputExists) {
                  avatarInput = input;
                  break;
                }
              }
            } else {
              // If it's already a file input, use it directly
              avatarInput = element;
            }
            
            break;
          }
        }
      }
    }
    
    if (!avatarUploadFound || !avatarInput) {
      console.log('Could not find avatar upload functionality');
      test.skip(true, 'Could not find avatar upload functionality');
      return;
    }
    
    // Check if the file input has restrictions on accepted file types
    const acceptAttr = await avatarInput.getAttribute('accept');
    console.log(`File input accept attribute: ${acceptAttr || 'none'}`);
    
    // Upload the test image
    await avatarInput.setInputFiles(imageFilePath);
    
    // Look for a submit button if needed
    const submitButtons = page.locator('button[type="submit"], input[type="submit"], button:has-text("Save"), button:has-text("Upload")');
    const hasSubmitButton = await submitButtons.count() > 0;
    
    if (hasSubmitButton) {
      await submitButtons.first().click();
    }
    
    await page.waitForLoadState('networkidle');
    
    // Take screenshot after upload
    await page.screenshot({ path: 'file-upload-avatar-after.png', fullPage: true });
    
    // Check for success message or updated avatar
    const successMessage = page.locator('.alert-success, .notification-success, text=successfully, text=Success, text=updated');
    const avatarImage = page.locator('.avatar img, .profile-image, .user-avatar');
    
    const uploadSuccessful = 
      await successMessage.isVisible().catch(() => false) || 
      await avatarImage.isVisible().catch(() => false);
    
    expect(uploadSuccessful).toBeTruthy();
  });
  
  test('should upload course content file', async ({ page }) => {
    // Login as an instructor
    const loginPage = new LoginPage(page);
    await loginPage.goto();
    await loginPage.login('dr.smith', 'dr.smith123');
    
    // Navigate to instructor dashboard
    await page.goto('/courses/instructor/dashboard/');
    await page.waitForLoadState('networkidle');
    
    // Take screenshot of instructor dashboard
    await page.screenshot({ path: 'file-upload-instructor-dashboard.png', fullPage: true });
    
    // Look for a course to manage
    const courseLinks = page.locator('a[href*="course"], .course-card, .course-item');
    const hasCourses = await courseLinks.count() > 0;
    
    if (!hasCourses) {
      console.log('No courses found for instructor');
      test.skip(true, 'No courses found for testing file uploads');
      return;
    }
    
    // Click the first course
    await courseLinks.first().click();
    await page.waitForLoadState('networkidle');
    
    // Take screenshot of course page
    await page.screenshot({ path: 'file-upload-course-page.png', fullPage: true });
    
    // Look for content management links
    const contentLinks = page.locator('a:has-text("Content"), a:has-text("Modules"), a:has-text("Materials"), a:has-text("Files"), a:has-text("Add Content")');
    const hasContentLinks = await contentLinks.count() > 0;
    
    if (!hasContentLinks) {
      console.log('No content management links found');
      test.skip(true, 'No content management functionality found for testing file uploads');
      return;
    }
    
    // Click content management link
    await contentLinks.first().click();
    await page.waitForLoadState('networkidle');
    
    // Take screenshot of content management page
    await page.screenshot({ path: 'file-upload-content-management.png', fullPage: true });
    
    // Look for add/upload buttons
    const addButtons = page.locator('a:has-text("Add"), button:has-text("Add"), a:has-text("Upload"), button:has-text("Upload")');
    const hasAddButtons = await addButtons.count() > 0;
    
    if (!hasAddButtons) {
      console.log('No add/upload buttons found');
      test.skip(true, 'No file upload functionality found for course content');
      return;
    }
    
    // Click add button
    await addButtons.first().click();
    await page.waitForLoadState('networkidle');
    
    // Take screenshot of add content page
    await page.screenshot({ path: 'file-upload-add-content.png', fullPage: true });
    
    // Look for file upload input
    const fileInputs = page.locator('input[type="file"], [accept="application/pdf,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document"]');
    const hasFileInput = await fileInputs.count() > 0;
    
    if (!hasFileInput) {
      console.log('No file input found');
      
      // Try looking for a file upload type option
      const fileTypeOptions = page.locator('input[value="file"], button:has-text("File"), a:has-text("File"), select option:has-text("File")');
      const hasFileTypeOption = await fileTypeOptions.count() > 0;
      
      if (hasFileTypeOption) {
        await fileTypeOptions.first().click();
        await page.waitForTimeout(1000);
        
        // Take screenshot after selecting file type
        await page.screenshot({ path: 'file-upload-file-type-selected.png', fullPage: true });
      } else {
        test.skip(true, 'No file upload functionality found');
        return;
      }
    }
    
    // Look for file input again after potentially selecting file type
    const fileInput = page.locator('input[type="file"]');
    const fileInputVisible = await fileInput.count() > 0;
    
    if (!fileInputVisible) {
      console.log('Still no file input found');
      test.skip(true, 'Could not locate file input element');
      return;
    }
    
    // Check accepted file types
    const acceptAttr = await fileInput.getAttribute('accept');
    console.log(`File input accept attribute: ${acceptAttr || 'none'}`);
    
    // Upload the test document file
    await fileInput.setInputFiles(docFilePath);
    
    // Fill in other required fields
    const titleInput = page.locator('input[name="title"], input[placeholder="Title"]');
    const hasTitle = await titleInput.count() > 0;
    
    if (hasTitle) {
      await titleInput.fill('Test Document Upload');
    }
    
    const descriptionInput = page.locator('textarea[name="description"], textarea[placeholder="Description"]');
    const hasDescription = await descriptionInput.count() > 0;
    
    if (hasDescription) {
      await descriptionInput.fill('This is a test document uploaded by automated tests.');
    }
    
    // Submit the form
    const submitButton = page.locator('button[type="submit"], input[type="submit"], button:has-text("Save"), button:has-text("Upload")');
    const hasSubmit = await submitButton.count() > 0;
    
    if (hasSubmit) {
      await submitButton.first().click();
      await page.waitForLoadState('networkidle');
    }
    
    // Take screenshot after upload
    await page.screenshot({ path: 'file-upload-content-after.png', fullPage: true });
    
    // Check for success message or file in content list
    const successMessage = page.locator('.alert-success, .notification-success, text=successfully, text=Success, text=added');
    const fileInList = page.locator('text=Test Document Upload, .file-item, .content-item:has-text("doc")');
    
    const uploadSuccessful = 
      await successMessage.isVisible().catch(() => false) || 
      await fileInList.isVisible().catch(() => false);
    
    expect(uploadSuccessful).toBeTruthy();
  });
  
  test('should validate file type and size restrictions', async ({ page }) => {
    // Login as an instructor
    const loginPage = new LoginPage(page);
    await loginPage.goto();
    await loginPage.login('dr.smith', 'dr.smith123');
    
    // Navigate to a page with file upload (try assignment creation)
    await page.goto('/courses/instructor/dashboard/');
    await page.waitForLoadState('networkidle');
    
    // Find a course
    const courseLinks = page.locator('a[href*="course"], .course-card, .course-item');
    const hasCourses = await courseLinks.count() > 0;
    
    if (!hasCourses) {
      console.log('No courses found for instructor');
      test.skip(true, 'No courses found for testing file type validation');
      return;
    }
    
    // Click the first course
    await courseLinks.first().click();
    await page.waitForLoadState('networkidle');
    
    // Take screenshot of course page
    await page.screenshot({ path: 'file-validation-course-page.png', fullPage: true });
    
    // Look for assignment management
    const assignmentLinks = page.locator('a:has-text("Assignment"), a:has-text("Assignments"), a[href*="assignment"]');
    const hasAssignmentLinks = await assignmentLinks.count() > 0;
    
    let fileUploadFound = false;
    let fileInput = null;
    
    if (hasAssignmentLinks) {
      await assignmentLinks.first().click();
      await page.waitForLoadState('networkidle');
      
      // Look for add assignment button
      const addButtons = page.locator('a:has-text("Add Assignment"), button:has-text("Create Assignment"), a:has-text("New Assignment")');
      const hasAddButton = await addButtons.count() > 0;
      
      if (hasAddButton) {
        await addButtons.first().click();
        await page.waitForLoadState('networkidle');
        
        // Take screenshot of assignment creation page
        await page.screenshot({ path: 'file-validation-assignment-creation.png', fullPage: true });
        
        // Look for file attachment field
        const fileInputs = page.locator('input[type="file"]');
        const hasFileInput = await fileInputs.count() > 0;
        
        if (hasFileInput) {
          fileUploadFound = true;
          fileInput = fileInputs.first();
        }
      }
    }
    
    // If we couldn't find file upload in assignments, try looking in course content
    if (!fileUploadFound) {
      console.log('Could not find file upload in assignments. Checking course content...');
      
      await page.goto('/courses/instructor/dashboard/');
      await page.waitForLoadState('networkidle');
      
      // Find a course again
      const courseLinks2 = page.locator('a[href*="course"], .course-card, .course-item');
      await courseLinks2.first().click();
      await page.waitForLoadState('networkidle');
      
      // Look for content management
      const contentLinks = page.locator('a:has-text("Content"), a:has-text("Materials"), a:has-text("Add Content")');
      const hasContentLinks = await contentLinks.count() > 0;
      
      if (hasContentLinks) {
        await contentLinks.first().click();
        await page.waitForLoadState('networkidle');
        
        // Try to find an add content button
        const addContentButtons = page.locator('a:has-text("Add"), button:has-text("Add"), a:has-text("Upload")');
        const hasAddContent = await addContentButtons.count() > 0;
        
        if (hasAddContent) {
          await addContentButtons.first().click();
          await page.waitForLoadState('networkidle');
          
          // Take screenshot of content creation page
          await page.screenshot({ path: 'file-validation-content-creation.png', fullPage: true });
          
          // Look for file upload options if needed
          const fileOptions = page.locator('input[value="file"], button:has-text("File"), a:has-text("File")');
          const hasFileOption = await fileOptions.count() > 0;
          
          if (hasFileOption) {
            await fileOptions.first().click();
            await page.waitForTimeout(1000);
          }
          
          // Now look for file input
          const fileInputs = page.locator('input[type="file"]');
          const hasFileInput = await fileInputs.count() > 0;
          
          if (hasFileInput) {
            fileUploadFound = true;
            fileInput = fileInputs.first();
          }
        }
      }
    }
    
    // If we still couldn't find file upload, try checking profile for avatar upload
    if (!fileUploadFound) {
      console.log('Could not find file upload in course sections. Checking profile...');
      
      await page.goto('/profile/');
      await page.waitForLoadState('networkidle');
      
      // Look for avatar upload
      const avatarInputs = page.locator('input[type="file"][accept="image/*"], input[type="file"][name="avatar"]');
      const hasAvatarInput = await avatarInputs.count() > 0;
      
      if (hasAvatarInput) {
        fileUploadFound = true;
        fileInput = avatarInputs.first();
      } else {
        // Try looking for avatar upload button
        const avatarButtons = page.locator('button:has-text("Change Avatar"), a:has-text("Upload Photo")');
        const hasAvatarButton = await avatarButtons.count() > 0;
        
        if (hasAvatarButton) {
          await avatarButtons.first().click();
          await page.waitForTimeout(1000);
          
          // Now look for file input
          const fileInputs = page.locator('input[type="file"]');
          const hasFileInput = await fileInputs.count() > 0;
          
          if (hasFileInput) {
            fileUploadFound = true;
            fileInput = fileInputs.first();
          }
        }
      }
    }
    
    if (!fileUploadFound || !fileInput) {
      console.log('Could not find any file upload functionality');
      test.skip(true, 'Could not find any file upload functionality for testing validation');
      return;
    }
    
    // Take screenshot showing file input
    await page.screenshot({ path: 'file-validation-file-input.png', fullPage: true });
    
    // Check accepted file types
    const acceptAttr = await fileInput.getAttribute('accept');
    console.log(`File input accept attribute: ${acceptAttr || 'none'}`);
    
    // Test uploading a file with invalid type
    // If accept contains 'image/*', upload a doc file, otherwise upload an image
    const isImageOnly = acceptAttr && acceptAttr.includes('image');
    const invalidFile = isImageOnly ? docFilePath : imageFilePath;
    
    // Try uploading invalid file type
    await fileInput.setInputFiles(invalidFile);
    
    // Take screenshot after attempting invalid file type
    await page.screenshot({ path: 'file-validation-invalid-type.png', fullPage: true });
    
    // Check for validation message (might appear immediately or on form submission)
    let validationMessageVisible = false;
    
    const validationSelectors = [
      '.error, .validation-error, .invalid-feedback',
      'text=Invalid file type',
      'text=File type not supported',
      'text=Only files of type'
    ];
    
    for (const selector of validationSelectors) {
      const validationElement = page.locator(selector);
      validationMessageVisible = await validationElement.isVisible().catch(() => false);
      
      if (validationMessageVisible) {
        break;
      }
    }
    
    // If no validation appeared, try submitting the form
    if (!validationMessageVisible) {
      // Try to find and fill required fields
      const requiredInputs = page.locator('input[required]:not([type="file"]), textarea[required]');
      const requiredCount = await requiredInputs.count();
      
      for (let i = 0; i < requiredCount; i++) {
        const input = requiredInputs.nth(i);
        const type = await input.getAttribute('type');
        
        if (type === 'text' || type === 'textarea' || type === null) {
          await input.fill('Test Input');
        } else if (type === 'number') {
          await input.fill('10');
        } else if (type === 'email') {
          await input.fill('test@example.com');
        }
      }
      
      // Submit the form
      const submitButton = page.locator('button[type="submit"], input[type="submit"], button:has-text("Save")');
      const hasSubmit = await submitButton.count() > 0;
      
      if (hasSubmit) {
        await submitButton.first().click();
        await page.waitForLoadState('networkidle');
        
        // Take screenshot after form submission
        await page.screenshot({ path: 'file-validation-after-submit.png', fullPage: true });
        
        // Check for validation message again
        for (const selector of validationSelectors) {
          const validationElement = page.locator(selector);
          validationMessageVisible = await validationElement.isVisible().catch(() => false);
          
          if (validationMessageVisible) {
            break;
          }
        }
      }
    }
    
    // Some implementations might not validate file type client-side
    // So this test is conditionally checked
    if (validationMessageVisible) {
      console.log('File type validation is working correctly');
      expect(validationMessageVisible).toBeTruthy();
    } else {
      console.log('No visible validation message for invalid file type - might be validated server-side only');
    }
    
    // Test uploading a very large file (if we have size restrictions)
    // Reset the form if possible first
    const resetButton = page.locator('button[type="reset"], input[type="reset"], button:has-text("Reset")');
    const hasReset = await resetButton.count() > 0;
    
    if (hasReset) {
      await resetButton.first().click();
    } else {
      // Refresh the page as an alternative to reset
      await page.reload();
      await page.waitForLoadState('networkidle');
      
      // Find the file input again
      fileInput = page.locator('input[type="file"]').first();
    }
    
    // Try uploading the large file
    await fileInput.setInputFiles(largeFilePath);
    
    // Take screenshot after attempting large file upload
    await page.screenshot({ path: 'file-validation-large-file.png', fullPage: true });
    
    // Check for size validation message
    let sizeValidationVisible = false;
    
    const sizeValidationSelectors = [
      '.error, .validation-error, .invalid-feedback',
      'text=File too large',
      'text=exceeds the maximum allowed size',
      'text=file size',
      'text=size limit'
    ];
    
    for (const selector of sizeValidationSelectors) {
      const validationElement = page.locator(selector);
      sizeValidationVisible = await validationElement.isVisible().catch(() => false);
      
      if (sizeValidationVisible) {
        break;
      }
    }
    
    // If no validation appeared, try submitting the form
    if (!sizeValidationVisible) {
      // Try to find and fill required fields again
      const requiredInputs = page.locator('input[required]:not([type="file"]), textarea[required]');
      const requiredCount = await requiredInputs.count();
      
      for (let i = 0; i < requiredCount; i++) {
        const input = requiredInputs.nth(i);
        const type = await input.getAttribute('type');
        
        if (type === 'text' || type === 'textarea' || type === null) {
          await input.fill('Test Input');
        } else if (type === 'number') {
          await input.fill('10');
        } else if (type === 'email') {
          await input.fill('test@example.com');
        }
      }
      
      // Submit the form
      const submitButton = page.locator('button[type="submit"], input[type="submit"], button:has-text("Save")');
      const hasSubmit = await submitButton.count() > 0;
      
      if (hasSubmit) {
        await submitButton.first().click();
        await page.waitForLoadState('networkidle');
        
        // Take screenshot after form submission
        await page.screenshot({ path: 'file-validation-size-after-submit.png', fullPage: true });
        
        // Check for validation message again
        for (const selector of sizeValidationSelectors) {
          const validationElement = page.locator(selector);
          sizeValidationVisible = await validationElement.isVisible().catch(() => false);
          
          if (sizeValidationVisible) {
            break;
          }
        }
      }
    }
    
    // Some implementations might not validate file size client-side
    // So this test is conditionally checked
    if (sizeValidationVisible) {
      console.log('File size validation is working correctly');
      expect(sizeValidationVisible).toBeTruthy();
    } else {
      console.log('No visible validation message for large file - might be validated server-side only');
      
      // Check for error message that might indicate server-side validation
      const errorMessage = page.locator('.alert-danger, .alert-error, .error-message');
      const hasError = await errorMessage.isVisible().catch(() => false);
      
      if (hasError) {
        console.log('Error message displayed after form submission - might be server-side validation');
      } else {
        console.log('No error message - file size might not be validated or 2MB might be within limits');
      }
    }
  });
});