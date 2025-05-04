// @ts-check
const { test, expect } = require('@playwright/test');
const { LoginPage } = require('../page-objects/login-page');
const { CourseCatalogPage } = require('../page-objects/course-catalog-page');
const { CourseDetailPage } = require('../page-objects/course-detail-page');
const { QRCodePage } = require('../page-objects/qr-code-page');

/**
 * Tests to verify that all demo scenarios described in the README are working correctly
 */
test.describe('Demo Scenarios', () => {
  // Define user credentials for different roles
  const users = {
    admin: { username: 'admin', password: 'admin123' },
    coordinator: { username: 'coordinator', password: 'coordinator123' },
    instructor: { username: 'dr.smith', password: 'dr.smith123' },
    student: { username: 'john.doe', password: 'john.doe123' }
  };

  // Course Variety Scenarios
  test.describe('Course Variety', () => {
    test('should display published courses with content', async ({ page }) => {
      // Login as student
      const loginPage = new LoginPage(page);
      await loginPage.goto();
      await loginPage.login(users.student.username, users.student.password);
      
      // Go to course catalog
      const catalogPage = new CourseCatalogPage(page);
      await catalogPage.goto();
      
      // Search for Python course
      await catalogPage.searchCourses('Python Programming Fundamentals');
      
      // Verify course exists
      await expect(page.locator('.course-card:has-text("Python Programming Fundamentals")')).toBeVisible();
      
      // Click on the course
      await page.locator('.course-card:has-text("Python Programming Fundamentals")').click();
      
      // Verify it has content (modules)
      const detailPage = new CourseDetailPage(page);
      const moduleCount = await detailPage.getModuleCount();
      expect(moduleCount).toBeGreaterThan(0);
      
      // Verify content types
      const hasContentTypes = await page.locator('.content-type-text, .content-type-video, .content-type-file, .content-type-quiz').count();
      expect(hasContentTypes).toBeGreaterThan(0);
    });
    
    test('should display empty courses with waiting message', async ({ page }) => {
      // Login as student
      const loginPage = new LoginPage(page);
      await loginPage.goto();
      await loginPage.login(users.student.username, users.student.password);
      
      // Go to course catalog
      const catalogPage = new CourseCatalogPage(page);
      await catalogPage.goto();
      
      // Search for empty course
      await catalogPage.searchCourses('Cloud Computing with AWS');
      
      // Verify course exists
      await expect(page.locator('.course-card:has-text("Cloud Computing with AWS")')).toBeVisible();
      
      // Click on the course
      await page.locator('.course-card:has-text("Cloud Computing with AWS")').click();
      
      // Verify empty state message
      await expect(page.locator('text=No modules available yet')).toBeVisible();
    });
    
    test('should display courses in different states (draft, archived)', async ({ page }) => {
      // Login as instructor
      const loginPage = new LoginPage(page);
      await loginPage.goto();
      await loginPage.login(users.instructor.username, users.instructor.password);
      
      // Go to instructor dashboard or course management area
      await page.goto('/courses/instructor/dashboard/');
      
      // Verify draft course is visible in instructor dashboard
      await expect(page.locator('text=Mobile App Development with React Native').first()).toBeVisible();
      
      // Verify draft status indicator
      await expect(page.locator('text=Draft').first()).toBeVisible();
      
      // Verify archived course
      await expect(page.locator('text=Legacy Web Development with PHP').first()).toBeVisible();
      
      // Verify archived status indicator
      await expect(page.locator('text=Archived').first()).toBeVisible();
    });
  });

  // Quiz Types Scenarios
  test.describe('Quiz Types', () => {
    test('should display and complete pre-check survey quiz', async ({ page }) => {
      // Login as student
      const loginPage = new LoginPage(page);
      await loginPage.goto();
      await loginPage.login(users.student.username, users.student.password);
      
      // Navigate to a course with pre-check survey
      // This is just an example, you'll need to adjust to your actual course/module structure
      await page.goto('/courses/catalog/');
      await page.locator('.course-card').first().click();
      await page.locator('text=Continue Learning').click();
      
      // Find and click on a pre-check quiz
      await page.locator('text=Pre-Check Survey').first().click();
      
      // Verify it's a pre-check survey
      await expect(page.locator('text=This survey has no right or wrong answers')).toBeVisible();
      
      // Answer all questions
      const questions = await page.locator('.question-container').count();
      
      for (let i = 0; i < questions; i++) {
        // Select first option for each question
        await page.locator(`.question-container:nth-child(${i + 1}) input[type="radio"]`).first().click();
      }
      
      // Submit the survey
      await page.locator('button:has-text("Submit")').click();
      
      // Verify success message or redirect
      await expect(page.locator('text=Survey completed')).toBeVisible();
    });
    
    test('should complete knowledge check quiz with score feedback', async ({ page }) => {
      // Login as student
      const loginPage = new LoginPage(page);
      await loginPage.goto();
      await loginPage.login(users.student.username, users.student.password);
      
      // Navigate to a course with knowledge check quiz
      await page.goto('/courses/catalog/');
      await page.locator('.course-card').first().click();
      await page.locator('text=Continue Learning').click();
      
      // Find and click on a knowledge check quiz
      await page.locator('text=Knowledge Check').first().click();
      
      // Answer all questions
      const questions = await page.locator('.question-container').count();
      
      for (let i = 0; i < questions; i++) {
        // Select first option for each question
        await page.locator(`.question-container:nth-child(${i + 1}) input[type="radio"]`).first().click();
      }
      
      // Submit the quiz
      await page.locator('button:has-text("Submit")').click();
      
      // Verify score is displayed
      await expect(page.locator('text=Your Score:')).toBeVisible();
      
      // Verify correct/incorrect indicators
      await expect(page.locator('.correct-answer, .incorrect-answer')).toBeVisible();
    });
  });

  // QR Code System Scenarios
  test.describe('QR Code System', () => {
    test('should generate and display course QR code', async ({ page }) => {
      // Login
      const loginPage = new LoginPage(page);
      await loginPage.goto();
      await loginPage.login(users.student.username, users.student.password);
      
      // Navigate to course catalog
      const catalogPage = new CourseCatalogPage(page);
      await catalogPage.goto();
      
      // Click on first course
      await catalogPage.clickFirstCourse();
      
      // Initialize QR code page
      const qrCodePage = new QRCodePage(page);
      
      // Verify QR code button exists
      await expect(qrCodePage.viewQrCodeBtn).toBeVisible();
      
      // Open QR code modal
      await qrCodePage.openQrCodeModal();
      
      // Verify course QR code is visible
      await expect(qrCodePage.courseQrCodeImage).toBeVisible();
      
      // Verify download and module options
      await expect(qrCodePage.downloadQrCodeBtn).toBeVisible();
      await expect(qrCodePage.printableSheetBtn).toBeVisible();
    });
    
    test('should display QR code statistics for instructors', async ({ page }) => {
      // Login as instructor
      const loginPage = new LoginPage(page);
      await loginPage.goto();
      await loginPage.login(users.instructor.username, users.instructor.password);
      
      // Navigate to course catalog
      const catalogPage = new CourseCatalogPage(page);
      await catalogPage.goto();
      
      // Click on first course
      await catalogPage.clickFirstCourse();
      
      // Initialize QR code page
      const qrCodePage = new QRCodePage(page);
      
      // Open QR code modal
      await qrCodePage.openQrCodeModal();
      
      // View statistics
      await qrCodePage.viewQrCodeStatistics();
      
      // Verify we're on the statistics page
      await expect(qrCodePage.qrCodeDetail.title).toBeVisible();
      
      // Verify scan statistics are visible
      await expect(qrCodePage.qrCodeDetail.totalScans).toBeVisible();
    });
    
    test('should generate printable QR code sheet', async ({ page }) => {
      // Login as instructor
      const loginPage = new LoginPage(page);
      await loginPage.goto();
      await loginPage.login(users.instructor.username, users.instructor.password);
      
      // Navigate to course catalog
      const catalogPage = new CourseCatalogPage(page);
      await catalogPage.goto();
      
      // Click on first course
      await catalogPage.clickFirstCourse();
      
      // Initialize QR code page
      const qrCodePage = new QRCodePage(page);
      
      // Open QR code modal
      await qrCodePage.openQrCodeModal();
      
      // Click generate printable sheet
      const newPagePromise = page.context().waitForEvent('page');
      await qrCodePage.generatePrintableSheet();
      
      // Wait for new page/tab
      const newPage = await newPagePromise;
      
      // Verify new page contains the printable sheet
      await newPage.waitForLoadState('domcontentloaded');
      
      // Verify QR code image is present
      const qrImage = newPage.locator('img[src*="qr_code"]').first();
      await expect(qrImage).toBeVisible();
    });
  });

  // Admin System Scenarios
  test.describe('Admin Features', () => {
    test('should access activity log as admin', async ({ page }) => {
      // Login as admin
      const loginPage = new LoginPage(page);
      await loginPage.goto();
      await loginPage.login(users.admin.username, users.admin.password);
      
      // Navigate to activity log
      await page.goto('/dashboard/activity-log/');
      
      // Verify activity log page loads
      await expect(page.locator('h1:has-text("Activity Log")')).toBeVisible();
      
      // Check that activity table is visible
      await expect(page.locator('table')).toBeVisible();
      
      // Verify filter controls exist
      await expect(page.locator('form:has([name="start_date"])')).toBeVisible();
      await expect(page.locator('form:has([name="end_date"])')).toBeVisible();
    });
    
    test('should view system health dashboard as admin', async ({ page }) => {
      // Login as admin
      const loginPage = new LoginPage(page);
      await loginPage.goto();
      await loginPage.login(users.admin.username, users.admin.password);
      
      // Navigate to system health dashboard
      await page.goto('/dashboard/system-health/');
      
      // Verify system health page loads
      await expect(page.locator('h1:has-text("System Health")')).toBeVisible();
      
      // Check that key metrics are visible
      await expect(page.locator('text=User Statistics')).toBeVisible();
      await expect(page.locator('text=Activity Statistics')).toBeVisible();
      
      // Verify system component status section exists
      await expect(page.locator('text=System Component Status')).toBeVisible();
    });
  });

  // Course Management Scenarios
  test.describe('Course Management', () => {
    test('should create a new course as instructor', async ({ page }) => {
      // Login as instructor
      const loginPage = new LoginPage(page);
      await loginPage.goto();
      await loginPage.login(users.instructor.username, users.instructor.password);
      
      // Navigate to instructor dashboard
      await page.goto('/courses/instructor/dashboard/');
      
      // Click create new course
      await page.locator('a:has-text("Create New Course")').click();
      
      // Fill in course details
      await page.locator('[name="title"]').fill('Playwright Testing 101');
      await page.locator('[name="description"]').fill('Learn how to use Playwright for end-to-end testing.');
      
      // Select category
      await page.locator('select[name="category"]').selectOption({value: '1'});
      
      // Set difficulty level
      await page.locator('[name="level"]').selectOption({value: 'beginner'});
      
      // Submit the form
      await page.locator('button:has-text("Create Course")').click();
      
      // Verify success
      await expect(page.locator('text=Course created successfully')).toBeVisible();
    });
    
    test('should manage student enrollments as coordinator', async ({ page }) => {
      // Login as coordinator
      const loginPage = new LoginPage(page);
      await loginPage.goto();
      await loginPage.login(users.coordinator.username, users.coordinator.password);
      
      // Navigate to coordinator dashboard
      await page.goto('/courses/coordinator/dashboard/');
      
      // Click manage enrollments
      await page.locator('a:has-text("Manage Enrollments")').click();
      
      // Verify enrollments page loads
      await expect(page.locator('text=Manage Enrollments')).toBeVisible();
      
      // Verify enrollment table is visible
      await expect(page.locator('table:has(th:has-text("Student"))')).toBeVisible();
    });
  });
  
  // Test that UI framework is working correctly
  test.describe('UI Framework', () => {
    test('should render UI with Tailwind CSS classes', async ({ page }) => {
      await page.goto('/');
      
      // Check that Tailwind CSS classes are used
      const hasTailwindClasses = await page.evaluate(() => {
        const elements = document.querySelectorAll('[class*="bg-"], [class*="text-"], [class*="flex"], [class*="grid"]');
        return elements.length > 0;
      });
      
      expect(hasTailwindClasses).toBeTruthy();
      
      // Check no Bootstrap classes are used
      const hasBootstrapClasses = await page.evaluate(() => {
        const bootstrapElements = document.querySelectorAll('.container-fluid, .row, .col, .btn-primary, .navbar-toggler');
        return bootstrapElements.length === 0;
      });
      
      expect(hasBootstrapClasses).toBeTruthy();
    });
    
    test('should support dark mode correctly', async ({ page }) => {
      await page.goto('/');
      
      // Get initial theme
      const initialTheme = await page.evaluate(() => {
        return document.documentElement.classList.contains('dark') ? 'dark' : 'light';
      });
      
      // Toggle theme
      await page.locator('button[data-theme-toggle]').click();
      await page.waitForTimeout(500); // Small delay for theme to apply
      
      // Verify theme changed
      const newTheme = await page.evaluate(() => {
        return document.documentElement.classList.contains('dark') ? 'dark' : 'light';
      });
      
      expect(newTheme).not.toEqual(initialTheme);
      
      // Verify dark mode utilities are applied to elements
      const hasDarkModeClasses = await page.evaluate(() => {
        const darkModeElements = document.querySelectorAll('[class*="dark:bg-"], [class*="dark:text-"]');
        return darkModeElements.length > 0;
      });
      
      expect(hasDarkModeClasses).toBeTruthy();
    });
  });
});