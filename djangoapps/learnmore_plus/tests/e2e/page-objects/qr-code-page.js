// @ts-check

/**
 * QRCodePage class representing the QR code related functionality
 */
class QRCodePage {
  /**
   * @param {import('@playwright/test').Page} page 
   */
  constructor(page) {
    this.page = page;
    
    // QR Code Modal selectors
    this.qrCodeModal = page.locator('#qrCodeModal');
    this.viewQrCodeBtn = page.locator('#viewQrCodeBtn');
    this.closeQrModalBtn = page.locator('#closeQrModal');
    this.courseQrCodeImage = page.locator('#qrCodeModal img[alt*="QR Code for"]').first();
    this.downloadQrCodeBtn = page.locator('#qrCodeModal a[download]').first();
    this.viewStatisticsBtn = page.locator('#qrCodeModal a:has-text("View Statistics")').first();
    this.printableSheetBtn = page.locator('#qrCodeModal a:has-text("Generate Printable Sheet")');
    
    // Module QR Code selectors
    this.moduleItems = page.locator('.qr-module-item');
    this.moduleQrDisplay = page.locator('#moduleQrDisplay');
    this.selectedModuleTitle = page.locator('#selectedModuleTitle');
    this.selectedModuleQr = page.locator('#selectedModuleQr');
    this.downloadModuleQrBtn = page.locator('#downloadModuleQr');
    this.viewModuleStatsBtn = page.locator('#viewModuleStats');
    
    // QR Code detail page selectors
    this.qrCodeDetail = {
      title: page.locator('h4:has-text("QR Code Details")'),
      image: page.locator('img[alt="QR Code"]'),
      downloadBtn: page.locator('a:has-text("Download QR Code")'),
      totalScans: page.locator('text=Total Scans:'),
      uniqueIPs: page.locator('text=Unique IP Addresses:')
    };
    
    // QR Code statistics page selectors
    this.statisticsPage = {
      title: page.locator('h2:has-text("QR Code Statistics")'),
      totalScans: page.locator('text=Total Scans'),
      activeQrCodes: page.locator('text=Active QR Codes'),
      averageScans: page.locator('text=Average Scans per Code'),
      scansChart: page.locator('#scansChart'),
      topQrCodesTable: page.locator('table')
    };
  }

  /**
   * Navigate to QR code statistics page
   */
  async gotoStatistics() {
    await this.page.goto('/qr/statistics/');
  }

  /**
   * Navigate to specific QR code detail page
   * @param {string} id - QR code ID 
   */
  async gotoQrCodeDetail(id) {
    await this.page.goto(`/qr/detail/${id}/`);
  }

  /**
   * Open QR code modal from course detail page
   */
  async openQrCodeModal() {
    await this.viewQrCodeBtn.click();
    await this.qrCodeModal.waitFor({ state: 'visible' });
  }

  /**
   * Close QR code modal
   */
  async closeQrCodeModal() {
    await this.closeQrModalBtn.click();
    await this.qrCodeModal.waitFor({ state: 'hidden' });
  }

  /**
   * Close QR code modal by pressing Escape key
   */
  async closeQrCodeModalWithEscape() {
    await this.page.keyboard.press('Escape');
    await this.qrCodeModal.waitFor({ state: 'hidden' });
  }

  /**
   * Close QR code modal by clicking outside
   */
  async closeQrCodeModalByClickingOutside() {
    // Click on the modal backdrop (the outer div)
    await this.qrCodeModal.click({ position: { x: 10, y: 10 } });
    await this.qrCodeModal.waitFor({ state: 'hidden' });
  }

  /**
   * Download course QR code and verify download
   * @returns {Promise<string>} Path to downloaded file
   */
  async downloadCourseQrCode() {
    // Setup download listener
    const downloadPromise = this.page.waitForEvent('download');
    
    // Click download button
    await this.downloadQrCodeBtn.click();
    
    // Wait for download to start
    const download = await downloadPromise;
    
    // Wait for download to complete
    const path = await download.path();
    return path;
  }

  /**
   * View QR code statistics
   */
  async viewQrCodeStatistics() {
    await this.viewStatisticsBtn.click();
  }

  /**
   * Generate printable QR code sheet
   */
  async generatePrintableSheet() {
    await this.printableSheetBtn.click();
  }

  /**
   * Select module QR code by index
   * @param {number} index 
   */
  async selectModuleQrCode(index) {
    await this.moduleItems.nth(index).click();
    await this.moduleQrDisplay.waitFor({ state: 'visible' });
  }

  /**
   * Get selected module title
   * @returns {Promise<string>}
   */
  async getSelectedModuleTitle() {
    return await this.selectedModuleTitle.innerText();
  }

  /**
   * Download selected module QR code
   * @returns {Promise<string>} Path to downloaded file
   */
  async downloadModuleQrCode() {
    // Setup download listener
    const downloadPromise = this.page.waitForEvent('download');
    
    // Click download button
    await this.downloadModuleQrBtn.click();
    
    // Wait for download to start
    const download = await downloadPromise;
    
    // Wait for download to complete
    const path = await download.path();
    return path;
  }

  /**
   * View module QR code statistics
   */
  async viewModuleQrCodeStatistics() {
    await this.viewModuleStatsBtn.click();
  }

  /**
   * Verify QR code statistics page has loaded correctly
   * @returns {Promise<boolean>}
   */
  async verifyStatisticsPageLoaded() {
    await this.statisticsPage.title.waitFor({ state: 'visible' });
    
    const chartVisible = await this.statisticsPage.scansChart.isVisible();
    const tableVisible = await this.statisticsPage.topQrCodesTable.isVisible();
    
    return chartVisible && tableVisible;
  }

  /**
   * Check if dark mode styling is correctly applied to QR code modal
   * @returns {Promise<boolean>}
   */
  async verifyDarkModeStyle() {
    // Get computed style of the modal
    const modalBgColor = await this.page.evaluate(() => {
      const modal = document.querySelector('#qrCodeModal > div');
      if (!modal) return null;
      return window.getComputedStyle(modal).backgroundColor;
    });
    
    // In dark mode, background should not be white
    // This is a simplified check - in a real test you'd verify the exact color values
    const isDarkMode = await this.page.evaluate(() => {
      return document.documentElement.classList.contains('dark');
    });
    
    if (isDarkMode) {
      // Dark mode - should have a dark background (not white)
      return modalBgColor !== 'rgb(255, 255, 255)';
    } else {
      // Light mode - should have a light background (white or close to white)
      return modalBgColor === 'rgb(255, 255, 255)';
    }
  }
}

module.exports = { QRCodePage };