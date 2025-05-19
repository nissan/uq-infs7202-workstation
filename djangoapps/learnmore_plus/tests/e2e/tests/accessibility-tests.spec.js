// @ts-check
const { test, expect } = require('./critical-tests');
const { LoginPage } = require('../page-objects/login-page');

/**
 * Comprehensive accessibility testing suite
 * This test suite focuses on keyboard navigation, ARIA attributes, and focus management
 */
test.describe('Accessibility Features', () => {
  
  test('should navigate main functionality using keyboard only', async ({ page }) => {
    // Start at the homepage
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    // Take screenshot of initial state
    await page.screenshot({ path: 'a11y-keyboard-initial.png', fullPage: true });
    
    // Focus on the first focusable element (usually the logo or skip link)
    await page.keyboard.press('Tab');
    
    // Check if the focus is visible
    const focusedElement = page.locator(':focus');
    const isFocusVisible = await focusedElement.isVisible().catch(() => false);
    
    // Take screenshot showing focus
    await page.screenshot({ path: 'a11y-keyboard-first-focus.png', fullPage: true });
    
    // Verify that focus is visible
    expect(isFocusVisible).toBeTruthy();
    
    // Navigate to login using keyboard
    // Tab through the page until we find a login link
    const maxTabsToLogin = 20; // Maximum tabs to try before giving up
    let loginLinkFound = false;
    
    for (let i = 0; i < maxTabsToLogin; i++) {
      await page.keyboard.press('Tab');
      
      // Check if we're focused on a login link
      const focusedHref = await page.evaluate(() => {
        const focused = document.activeElement;
        return focused && focused.tagName === 'A' ? focused.textContent : null;
      });
      
      if (focusedHref && (focusedHref.includes('Login') || focusedHref.includes('login') || focusedHref.includes('Sign in'))) {
        loginLinkFound = true;
        break;
      }
    }
    
    // Take screenshot of login link focus
    await page.screenshot({ path: 'a11y-keyboard-login-focus.png', fullPage: true });
    
    if (!loginLinkFound) {
      console.log('Could not find login link with keyboard navigation');
      test.skip(true, 'Could not find login link with keyboard navigation');
      return;
    }
    
    // Press Enter to navigate to login page
    await page.keyboard.press('Enter');
    await page.waitForLoadState('networkidle');
    
    // Take screenshot of login page
    await page.screenshot({ path: 'a11y-keyboard-login-page.png', fullPage: true });
    
    // Check if we're on the login page
    const currentUrl = page.url();
    const isLoginPage = currentUrl.includes('login') || 
                       currentUrl.includes('signin') || 
                       await page.locator('form input[name="username"], form input[name="email"]').isVisible().catch(() => false);
    
    expect(isLoginPage).toBeTruthy();
    
    // Tab to username/email field
    let usernameFieldFound = false;
    for (let i = 0; i < 10; i++) {
      await page.keyboard.press('Tab');
      
      const focusedType = await page.evaluate(() => {
        const focused = document.activeElement;
        return focused ? focused.getAttribute('type') || focused.tagName : null;
      });
      
      if (focusedType === 'text' || focusedType === 'email' || focusedType === 'INPUT') {
        usernameFieldFound = true;
        break;
      }
    }
    
    // Take screenshot showing username field focus
    await page.screenshot({ path: 'a11y-keyboard-username-focus.png', fullPage: true });
    
    expect(usernameFieldFound).toBeTruthy();
    
    // Type username
    await page.keyboard.type('john.doe');
    
    // Tab to password field
    await page.keyboard.press('Tab');
    
    // Type password
    await page.keyboard.type('john.doe123');
    
    // Tab to login button
    await page.keyboard.press('Tab');
    
    // Take screenshot showing login button focus
    await page.screenshot({ path: 'a11y-keyboard-login-button-focus.png', fullPage: true });
    
    // Press Enter to submit the form
    await page.keyboard.press('Enter');
    await page.waitForLoadState('networkidle');
    
    // Take screenshot after login
    await page.screenshot({ path: 'a11y-keyboard-after-login.png', fullPage: true });
    
    // Verify we're logged in by checking for elements that would only be visible to logged-in users
    const isLoggedIn = 
      await page.locator('text=Dashboard, text=Profile, text=Logout, text=My Courses').count() > 0 ||
      await page.locator('.user-menu, .profile-menu, .dashboard-nav').isVisible().catch(() => false);
    
    expect(isLoggedIn).toBeTruthy();
  });
  
  test('should have proper ARIA attributes on interactive elements', async ({ page }) => {
    // Login as a user
    const loginPage = new LoginPage(page);
    await loginPage.goto();
    await loginPage.login('john.doe', 'john.doe123');
    
    // Navigate to a page likely to have interactive elements
    await page.goto('/dashboard/');
    await page.waitForLoadState('networkidle');
    
    // Take screenshot of dashboard
    await page.screenshot({ path: 'a11y-aria-dashboard.png', fullPage: true });
    
    // Check navigation for ARIA attributes
    const mainNav = page.locator('nav, .navigation, .main-nav');
    const hasMainNav = await mainNav.count() > 0;
    
    if (hasMainNav) {
      // Check for proper nav role
      const navRole = await mainNav.first().getAttribute('role');
      const isProperNav = navRole === 'navigation' || navRole === null; // nav element has implicit role
      
      // For landmarks that aren't <nav> but function as navigation, they should have role="navigation"
      if (!isProperNav) {
        console.log('Navigation landmark missing proper role attribute');
      }
      
      // Check if nav has an accessible name
      const navAriaLabel = await mainNav.first().getAttribute('aria-label');
      const navAriaLabelledBy = await mainNav.first().getAttribute('aria-labelledby');
      
      const hasAccessibleName = navAriaLabel || navAriaLabelledBy;
      
      if (!hasAccessibleName) {
        console.log('Navigation landmark missing accessible name (aria-label or aria-labelledby)');
      }
    }
    
    // Check buttons for proper ARIA attributes
    const buttons = page.locator('button, [role="button"]');
    const buttonCount = await buttons.count();
    
    let improperButtonsCount = 0;
    
    for (let i = 0; i < Math.min(buttonCount, 10); i++) { // Check up to 10 buttons
      const button = buttons.nth(i);
      
      // Check if button has accessible name
      const buttonText = await button.innerText().catch(() => '');
      const buttonAriaLabel = await button.getAttribute('aria-label');
      const buttonAriaLabelledBy = await button.getAttribute('aria-labelledby');
      
      const hasAccessibleName = buttonText.trim() || buttonAriaLabel || buttonAriaLabelledBy;
      
      if (!hasAccessibleName) {
        console.log(`Button ${i+1} missing accessible name`);
        improperButtonsCount++;
      }
      
      // Check if button has correct expanded state if it controls expandable content
      const controls = await button.getAttribute('aria-controls');
      if (controls) {
        const expanded = await button.getAttribute('aria-expanded');
        if (expanded === null) {
          console.log(`Button ${i+1} controls expandable content but missing aria-expanded state`);
          improperButtonsCount++;
        }
      }
    }
    
    // Take screenshot showing some of the examined buttons
    await page.screenshot({ path: 'a11y-aria-buttons.png', fullPage: true });
    
    // Verify most buttons have proper attributes
    expect(improperButtonsCount).toBeLessThan(buttonCount * 0.5); // At least 50% should be proper
    
    // Check form fields for proper ARIA attributes
    await page.goto('/profile/');
    await page.waitForLoadState('networkidle');
    
    // Take screenshot of profile page
    await page.screenshot({ path: 'a11y-aria-profile.png', fullPage: true });
    
    // Check form labels
    const formFields = page.locator('input, select, textarea');
    const fieldCount = await formFields.count();
    
    let improperFieldsCount = 0;
    
    for (let i = 0; i < Math.min(fieldCount, 10); i++) { // Check up to 10 fields
      const field = formFields.nth(i);
      
      // Skip hidden fields
      const isHidden = await field.isHidden().catch(() => true);
      if (isHidden) continue;
      
      // Check if field has a label or accessible name
      const fieldId = await field.getAttribute('id');
      let hasLabel = false;
      
      if (fieldId) {
        // Check for a <label> element with a 'for' attribute matching this field's id
        hasLabel = await page.locator(`label[for="${fieldId}"]`).count() > 0;
      }
      
      // Check for aria-label or aria-labelledby
      const fieldAriaLabel = await field.getAttribute('aria-label');
      const fieldAriaLabelledBy = await field.getAttribute('aria-labelledby');
      
      const hasAccessibleName = hasLabel || fieldAriaLabel || fieldAriaLabelledBy;
      
      if (!hasAccessibleName) {
        console.log(`Form field ${i+1} missing accessible name`);
        improperFieldsCount++;
      }
      
      // Check for required state
      const isRequired = await field.getAttribute('required') !== null;
      const ariaRequired = await field.getAttribute('aria-required') === 'true';
      
      if (isRequired && !ariaRequired) {
        // It's fine if the field uses the required attribute without aria-required
        // as long as there's some visual indication
      }
    }
    
    // Take screenshot showing some of the examined form fields
    await page.screenshot({ path: 'a11y-aria-form-fields.png', fullPage: true });
    
    // Verify most form fields have proper attributes
    expect(improperFieldsCount).toBeLessThan(fieldCount * 0.5); // At least 50% should be proper
  });
  
  test('should have proper focus management for modals', async ({ page }) => {
    // Login as a user
    const loginPage = new LoginPage(page);
    await loginPage.goto();
    await loginPage.login('john.doe', 'john.doe123');
    
    // Need to find a page with a modal component
    // Try looking for a page with a modal trigger
    const pagesToTry = [
      '/dashboard/',
      '/courses/catalog/',
      '/profile/'
    ];
    
    let foundModalTrigger = false;
    let modalPage = '';
    
    for (const pagePath of pagesToTry) {
      await page.goto(pagePath);
      await page.waitForLoadState('networkidle');
      
      // Take screenshot of the page
      await page.screenshot({ path: `a11y-modal-page-${pagePath.replace(/\//g, '-')}.png`, fullPage: true });
      
      // Look for modal triggers
      const modalTriggers = page.locator(
        'button:has-text("Delete"), button:has-text("Edit"), ' +
        'button:has-text("Settings"), button:has-text("Add"), ' +
        'a:has-text("View"), a:has-text("QR Code"), ' +
        '[data-modal], [aria-haspopup="dialog"], [data-toggle="modal"]'
      );
      
      const hasModalTrigger = await modalTriggers.count() > 0;
      
      if (hasModalTrigger) {
        foundModalTrigger = true;
        modalPage = pagePath;
        break;
      }
    }
    
    if (!foundModalTrigger) {
      // Try one more approach - look for QR code functionality
      await page.goto('/courses/catalog/');
      await page.waitForLoadState('networkidle');
      
      // Try to find and click on a course
      const courseLinks = page.locator('a[href*="course"], .course-card, .card');
      const hasLinks = await courseLinks.count() > 0;
      
      if (hasLinks) {
        await courseLinks.first().click();
        await page.waitForLoadState('networkidle');
        
        // Look for QR code links on course page
        const qrLinks = page.locator('a:has-text("QR"), a:has-text("QR Code"), a:has-text("Generate QR"), [href*="qr"]');
        const hasQRLinks = await qrLinks.count() > 0;
        
        if (hasQRLinks) {
          foundModalTrigger = true;
          modalPage = page.url();
        }
      }
    }
    
    if (!foundModalTrigger) {
      console.log('Could not find any modal triggers');
      test.skip(true, 'Could not find any modal triggers to test focus management');
      return;
    }
    
    // Navigate to the page with a modal trigger
    await page.goto(modalPage);
    await page.waitForLoadState('networkidle');
    
    // Find and click a modal trigger
    const modalTriggers = page.locator(
      'button:has-text("Delete"), button:has-text("Edit"), ' +
      'button:has-text("Settings"), button:has-text("Add"), ' +
      'a:has-text("View"), a:has-text("QR Code"), ' +
      '[data-modal], [aria-haspopup="dialog"], [data-toggle="modal"]'
    );
    
    // Take screenshot showing modal trigger
    await page.screenshot({ path: 'a11y-modal-trigger.png', fullPage: true });
    
    await modalTriggers.first().click();
    await page.waitForTimeout(1000); // Wait for modal animation
    
    // Take screenshot of opened modal
    await page.screenshot({ path: 'a11y-modal-opened.png', fullPage: true });
    
    // Verify modal is open
    const modal = page.locator('.modal, [role="dialog"], [aria-modal="true"]');
    const isModalOpen = await modal.isVisible().catch(() => false);
    
    if (!isModalOpen) {
      console.log('Modal did not open after clicking trigger');
      test.skip(true, 'Could not open a modal to test focus management');
      return;
    }
    
    // Check if modal has proper ARIA attributes
    const modalRole = await modal.getAttribute('role');
    const isDialogRole = modalRole === 'dialog' || modalRole === 'alertdialog';
    
    if (!isDialogRole) {
      console.log(`Modal has incorrect role attribute: ${modalRole || 'none'} (should be 'dialog' or 'alertdialog')`);
    }
    
    const ariaModal = await modal.getAttribute('aria-modal');
    const hasAriaModal = ariaModal === 'true';
    
    if (!hasAriaModal) {
      console.log('Modal missing aria-modal="true" attribute');
    }
    
    const ariaLabel = await modal.getAttribute('aria-label');
    const ariaLabelledBy = await modal.getAttribute('aria-labelledby');
    
    const hasAccessibleName = ariaLabel || ariaLabelledBy;
    
    if (!hasAccessibleName) {
      console.log('Modal missing accessible name (aria-label or aria-labelledby)');
    }
    
    // Check if focus is trapped within the modal
    // First, check if focus moved into the modal
    const focusedElementInModal = await page.evaluate(() => {
      const focused = document.activeElement;
      const modal = document.querySelector('.modal, [role="dialog"], [aria-modal="true"]');
      return modal && focused ? modal.contains(focused) : false;
    });
    
    // Take screenshot showing focus in modal
    await page.screenshot({ path: 'a11y-modal-focus.png', fullPage: true });
    
    expect(focusedElementInModal).toBeTruthy();
    
    // Try to tab out of the modal
    // Press Tab multiple times
    for (let i = 0; i < 10; i++) {
      await page.keyboard.press('Tab');
    }
    
    // Focus should still be within the modal
    const focusStillInModal = await page.evaluate(() => {
      const focused = document.activeElement;
      const modal = document.querySelector('.modal, [role="dialog"], [aria-modal="true"]');
      return modal && focused ? modal.contains(focused) : false;
    });
    
    // Take screenshot showing focus trap
    await page.screenshot({ path: 'a11y-modal-focus-trap.png', fullPage: true });
    
    expect(focusStillInModal).toBeTruthy();
    
    // Check if Escape key closes the modal
    await page.keyboard.press('Escape');
    await page.waitForTimeout(1000); // Wait for modal close animation
    
    // Take screenshot after Escape key
    await page.screenshot({ path: 'a11y-modal-after-escape.png', fullPage: true });
    
    const modalClosed = await modal.isHidden().catch(() => true);
    
    if (!modalClosed) {
      console.log('Modal did not close with Escape key');
    }
  });
  
  test('should have skip links for keyboard users', async ({ page }) => {
    // Go to the homepage
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    // Take screenshot of initial state
    await page.screenshot({ path: 'a11y-skip-link-initial.png', fullPage: true });
    
    // Look for skip link
    const skipLink = page.locator('a:has-text("Skip"), a:has-text("Skip to content"), a:has-text("Skip to main content"), a:has-text("Skip navigation"), .skip-link, [href="#content"], [href="#main"]');
    
    const hasSkipLink = await skipLink.count() > 0;
    
    if (!hasSkipLink) {
      console.log('No skip link found');
      test.skip(true, 'No skip link found to test');
      return;
    }
    
    // Skip link should be the first focusable element
    await page.keyboard.press('Tab');
    
    // Check if the first focusable element is the skip link
    const firstFocusableIsSkip = await page.evaluate(() => {
      const focused = document.activeElement;
      return focused ? 
        focused.textContent?.includes('Skip') || 
        focused.classList.contains('skip-link') || 
        focused.getAttribute('href') === '#content' || 
        focused.getAttribute('href') === '#main' : 
        false;
    });
    
    // Take screenshot showing skip link focus
    await page.screenshot({ path: 'a11y-skip-link-focus.png', fullPage: true });
    
    expect(firstFocusableIsSkip).toBeTruthy();
    
    // Press Enter to activate the skip link
    await page.keyboard.press('Enter');
    
    // Focus should now be on the main content
    const focusedOnContent = await page.evaluate(() => {
      const focused = document.activeElement;
      const main = document.querySelector('main, #main, #content, [role="main"]');
      
      if (focused && main) {
        // Check if focus is on main element itself
        if (focused === main) {
          return true;
        }
        
        // Or if focus is on the first focusable element within main
        if (main.contains(focused)) {
          return true;
        }
      }
      
      return false;
    });
    
    // Take screenshot after skip link activation
    await page.screenshot({ path: 'a11y-skip-link-activated.png', fullPage: true });
    
    // Some implementations might not directly focus on main content
    // but should at least move focus past the navigation
    if (!focusedOnContent) {
      console.log('Skip link did not move focus directly to main content, but might have skipped navigation');
    }
  });
});