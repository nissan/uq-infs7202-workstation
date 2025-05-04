// @ts-check
const { test, expect } = require('@playwright/test');
const { LoginPage } = require('../page-objects/login-page');
const { CourseCatalogPage } = require('../page-objects/course-catalog-page');
const { CourseDetailPage } = require('../page-objects/course-detail-page');
const { CourseLearnPage } = require('../page-objects/course-learn-page');

test.describe('Course Functionality', () => {
  test.beforeEach(async ({ page }) => {
    // Login before each test
    const loginPage = new LoginPage(page);
    await loginPage.goto();
    await loginPage.login('student', 'password123');
  });

  test('should display course catalog', async ({ page }) => {
    const catalogPage = new CourseCatalogPage(page);
    
    // Navigate to the course catalog
    await catalogPage.goto();
    
    // Verify page elements
    await expect(catalogPage.pageTitle).toBeVisible();
    await expect(catalogPage.pageTitle).toContainText('Course Catalog');
    
    // Verify courses are displayed
    await expect(catalogPage.courseCards.first()).toBeVisible();
    
    // Test search functionality
    await catalogPage.searchCourses('Python');
    
    // Verify search results
    await expect(page).toHaveURL(/q=Python/);
  });

  test('should display course details', async ({ page }) => {
    const catalogPage = new CourseCatalogPage(page);
    const detailPage = new CourseDetailPage(page);
    
    // Navigate to the course catalog
    await catalogPage.goto();
    
    // Click on first course
    await catalogPage.clickFirstCourse();
    
    // Verify course detail elements
    await expect(detailPage.courseTitle).toBeVisible();
    await expect(detailPage.enrollButton).toBeVisible();
    await expect(detailPage.modulesList).toBeVisible();
  });

  test('should enroll in a course', async ({ page }) => {
    const catalogPage = new CourseCatalogPage(page);
    const detailPage = new CourseDetailPage(page);
    const learnPage = new CourseLearnPage(page);
    
    // Navigate to the course catalog
    await catalogPage.goto();
    
    // Click on first course
    await catalogPage.clickFirstCourse();
    
    // Check if already enrolled
    const isEnrolled = await detailPage.isEnrolled();
    
    if (!isEnrolled) {
      // Enroll in the course
      await detailPage.enroll();
      
      // Verify redirection to learn page
      await expect(learnPage.courseContent).toBeVisible();
    } else {
      // If already enrolled, just navigate to learn
      await detailPage.goToLearn();
      
      // Verify course content
      await expect(learnPage.courseContent).toBeVisible();
    }
  });
});