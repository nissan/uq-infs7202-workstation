// @ts-check
const { test, expect } = require('@playwright/test');
const { LoginPage } = require('../page-objects/login-page');
const { CourseCatalogPage } = require('../page-objects/course-catalog-page');
const { CourseDetailPage } = require('../page-objects/course-detail-page');
const { QRCodePage } = require('../page-objects/qr-code-page');
const fs = require('fs');

test.describe('QR Code System', () => {
  let qrCodePage;
  
  test.beforeEach(async ({ page }) => {
    // Login before each test as student
    const loginPage = new LoginPage(page);
    await loginPage.goto();
    await loginPage.login('john.doe', 'john.doe123');
    
    // Initialize QR code page
    qrCodePage = new QRCodePage(page);
  });

  test('should display and interact with QR code modal on course detail page', async ({ page }) => {
    // Navigate to course catalog
    const catalogPage = new CourseCatalogPage(page);
    await catalogPage.goto();
    
    // Click on first course
    await catalogPage.clickFirstCourse();
    
    // Verify QR code button is visible
    await expect(qrCodePage.viewQrCodeBtn).toBeVisible();
    
    // Open QR code modal
    await qrCodePage.openQrCodeModal();
    
    // Verify modal is visible
    await expect(qrCodePage.qrCodeModal).toBeVisible();
    await expect(qrCodePage.courseQrCodeImage).toBeVisible();
    await expect(qrCodePage.downloadQrCodeBtn).toBeVisible();
    
    // Close modal with close button
    await qrCodePage.closeQrCodeModal();
    await expect(qrCodePage.qrCodeModal).not.toBeVisible();
    
    // Open modal again
    await qrCodePage.openQrCodeModal();
    
    // Close modal with escape key
    await qrCodePage.closeQrCodeModalWithEscape();
    await expect(qrCodePage.qrCodeModal).not.toBeVisible();
    
    // Open modal again
    await qrCodePage.openQrCodeModal();
    
    // Close modal by clicking outside
    await qrCodePage.closeQrCodeModalByClickingOutside();
    await expect(qrCodePage.qrCodeModal).not.toBeVisible();
  });

  test('should select and view module QR codes', async ({ page }) => {
    // Navigate to course catalog
    const catalogPage = new CourseCatalogPage(page);
    await catalogPage.goto();
    
    // Click on first course
    await catalogPage.clickFirstCourse();
    
    // Open QR code modal
    await qrCodePage.openQrCodeModal();
    
    // Check if there are module QR codes
    const moduleCount = await qrCodePage.moduleItems.count();
    
    if (moduleCount > 0) {
      // Select first module
      await qrCodePage.selectModuleQrCode(0);
      
      // Verify module QR code display is visible
      await expect(qrCodePage.moduleQrDisplay).toBeVisible();
      await expect(qrCodePage.selectedModuleQr).toBeVisible();
      
      // Title should not be empty
      const title = await qrCodePage.getSelectedModuleTitle();
      expect(title.length).toBeGreaterThan(0);
      
      // Download buttons should be available
      await expect(qrCodePage.downloadModuleQrBtn).toBeVisible();
      await expect(qrCodePage.viewModuleStatsBtn).toBeVisible();
    }
  });

  test('should handle theme changes correctly for QR code modal', async ({ page }) => {
    // Navigate to course catalog
    const catalogPage = new CourseCatalogPage(page);
    await catalogPage.goto();
    
    // Click on first course
    await catalogPage.clickFirstCourse();
    
    // Open QR code modal
    await qrCodePage.openQrCodeModal();
    
    // Verify initial styling matches current theme
    const initialThemeCorrect = await qrCodePage.verifyDarkModeStyle();
    expect(initialThemeCorrect).toBeTruthy();
    
    // Close modal
    await qrCodePage.closeQrCodeModal();
    
    // Toggle theme
    await page.locator('button[data-theme-toggle]').click();
    await page.waitForTimeout(500); // Small delay for theme to apply
    
    // Open modal again
    await qrCodePage.openQrCodeModal();
    
    // Verify styling has updated
    const updatedThemeCorrect = await qrCodePage.verifyDarkModeStyle();
    expect(updatedThemeCorrect).toBeTruthy();
  });

  test('should display QR code statistics page with dark mode support', async ({ page, browserName }) => {
    // Skip download tests in webkit due to permissions issues
    test.skip(browserName === 'webkit', 'Download verification not supported in WebKit');
    
    // Navigate to course catalog
    const catalogPage = new CourseCatalogPage(page);
    await catalogPage.goto();
    
    // Click on first course
    await catalogPage.clickFirstCourse();
    
    // Open QR code modal
    await qrCodePage.openQrCodeModal();
    
    // Click view statistics
    await qrCodePage.viewQrCodeStatistics();
    
    // Verify statistics page is loaded
    await expect(qrCodePage.qrCodeDetail.title).toBeVisible();
    
    // Go to global statistics page
    await qrCodePage.gotoStatistics();
    
    // Verify statistics page metrics are visible
    await expect(qrCodePage.statisticsPage.title).toBeVisible();
    await expect(qrCodePage.statisticsPage.totalScans).toBeVisible();
    await expect(qrCodePage.statisticsPage.activeQrCodes).toBeVisible();
    await expect(qrCodePage.statisticsPage.averageScans).toBeVisible();
    
    // Toggle dark mode
    await page.locator('button[data-theme-toggle]').click();
    await page.waitForTimeout(500); // Small delay for theme to apply
    
    // Verify chart is visible after theme change
    await expect(qrCodePage.statisticsPage.scansChart).toBeVisible();
    
    // Take a screenshot for visual verification
    await page.screenshot({ path: 'qr-code-statistics-dark-mode.png' });
    
    // Toggle back to light mode
    await page.locator('button[data-theme-toggle]').click();
    await page.waitForTimeout(500); // Small delay for theme to apply
    
    // Take a screenshot for comparison
    await page.screenshot({ path: 'qr-code-statistics-light-mode.png' });
  });

  test('should download QR codes successfully', async ({ page, browserName }) => {
    // Skip download tests in webkit due to permissions issues
    test.skip(browserName === 'webkit', 'Download verification not supported in WebKit');
    
    // Navigate to course catalog
    const catalogPage = new CourseCatalogPage(page);
    await catalogPage.goto();
    
    // Click on first course
    await catalogPage.clickFirstCourse();
    
    // Open QR code modal
    await qrCodePage.openQrCodeModal();
    
    // Download course QR code
    const downloadPath = await qrCodePage.downloadCourseQrCode();
    
    // Verify downloaded file exists and is a PNG
    expect(fs.existsSync(downloadPath)).toBeTruthy();
    expect(downloadPath.endsWith('.png')).toBeTruthy();
    
    // Check file size (should be > 0)
    const stats = fs.statSync(downloadPath);
    expect(stats.size).toBeGreaterThan(0);
    
    // If there are module QR codes, test module download as well
    const moduleCount = await qrCodePage.moduleItems.count();
    
    if (moduleCount > 0) {
      // Select first module
      await qrCodePage.selectModuleQrCode(0);
      
      // Download module QR code
      const moduleDownloadPath = await qrCodePage.downloadModuleQrCode();
      
      // Verify downloaded file exists and is a PNG
      expect(fs.existsSync(moduleDownloadPath)).toBeTruthy();
      expect(moduleDownloadPath.endsWith('.png')).toBeTruthy();
      
      // Check file size (should be > 0)
      const moduleStats = fs.statSync(moduleDownloadPath);
      expect(moduleStats.size).toBeGreaterThan(0);
    }
  });

  test('should generate printable QR code sheet', async ({ page }) => {
    // Navigate to course catalog
    const catalogPage = new CourseCatalogPage(page);
    await catalogPage.goto();
    
    // Click on first course
    await catalogPage.clickFirstCourse();
    
    // Open QR code modal
    await qrCodePage.openQrCodeModal();
    
    // Click generate printable sheet
    const newPagePromise = page.context().waitForEvent('page');
    await qrCodePage.generatePrintableSheet();
    
    // Wait for new page/tab
    const newPage = await newPagePromise;
    
    // Verify new page contains the printable sheet
    await newPage.waitForLoadState('domcontentloaded');
    const pageTitle = await newPage.title();
    expect(pageTitle).toContain('QR Codes for');
    
    // Verify QR code image is present
    const qrImage = newPage.locator('img[src*="qr_code"]').first();
    await expect(qrImage).toBeVisible();
    
    // Check page has proper print styling
    const hasPrintStyles = await newPage.evaluate(() => {
      const styleElements = document.querySelectorAll('style');
      let hasPrintRules = false;
      
      for (const style of styleElements) {
        if (style.textContent.includes('page-break')) {
          hasPrintRules = true;
          break;
        }
      }
      
      return hasPrintRules;
    });
    
    expect(hasPrintStyles).toBeTruthy();
  });
});