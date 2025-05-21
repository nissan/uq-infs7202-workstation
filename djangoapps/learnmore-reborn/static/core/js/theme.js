/**
 * Theme Management JavaScript Module
 * 
 * This file provides functions for managing theme settings and preferences.
 * It handles loading CSS variables and applying theme changes on the client side.
 */

// Theme manager object
const ThemeManager = {
  // Current theme settings
  currentTheme: null,
  
  // User preferences
  userPreferences: null,
  
  /**
   * Initialize the theme manager
   */
  init: function() {
    // Load CSS variables from the API
    this.loadCssVariables();
    
    // Set up theme toggle button
    this.setupThemeToggle();
    
    // Set up preview theme functionality
    this.setupPreviewTheme();
    
    // Set up accessibility controls
    this.setupAccessibilityControls();
    
    // Set system preference detection
    this.setupSystemPreferenceDetection();
  },
  
  /**
   * Load CSS variables from the API
   */
  loadCssVariables: function() {
    fetch('/api/core/css-variables/')
      .then(response => {
        if (!response.ok) {
          throw new Error('Failed to load CSS variables');
        }
        return response.json();
      })
      .then(data => {
        // Apply the CSS variables to the document
        this.applyCssVariables(data.cssVariables);
      })
      .catch(error => {
        console.error('Error loading theme variables:', error);
      });
  },
  
  /**
   * Apply CSS variables to the document
   * @param {Object} variables - CSS variables object
   */
  applyCssVariables: function(variables) {
    const root = document.documentElement;
    
    // Apply each CSS variable to the root element
    for (const [property, value] of Object.entries(variables)) {
      root.style.setProperty(property, value);
    }
    
    // Set data attributes for CSS selectors
    if (variables['--theme-mode']) {
      root.setAttribute('data-theme', variables['--theme-mode']);
    }
    
    if (variables['--high-contrast'] === 'true') {
      root.setAttribute('data-high-contrast', 'true');
    } else {
      root.removeAttribute('data-high-contrast');
    }
    
    if (variables['--increased-spacing'] === 'true') {
      root.setAttribute('data-increased-spacing', 'true');
    } else {
      root.removeAttribute('data-increased-spacing');
    }
    
    if (variables['--text-size']) {
      root.setAttribute('data-text-size', variables['--text-size']);
    }
    
    if (variables['--dyslexia-font'] === 'true') {
      root.setAttribute('data-dyslexia-font', 'true');
    } else {
      root.removeAttribute('data-dyslexia-font');
    }
  },
  
  /**
   * Set up theme toggle button
   */
  setupThemeToggle: function() {
    const themeToggle = document.getElementById('theme-toggle');
    if (themeToggle) {
      themeToggle.addEventListener('click', () => {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        
        // Send the new theme preference to the server
        this.updateThemePreference('theme_mode', newTheme);
      });
    }
  },
  
  /**
   * Set up preview theme functionality
   */
  setupPreviewTheme: function() {
    const previewButtons = document.querySelectorAll('[data-preview-theme]');
    const applyButtons = document.querySelectorAll('[data-apply-theme]');
    const resetButton = document.getElementById('reset-theme');
    
    // Preview theme buttons
    previewButtons.forEach(button => {
      button.addEventListener('click', (e) => {
        const themeId = button.getAttribute('data-preview-theme');
        this.previewTheme(themeId);
      });
    });
    
    // Apply theme buttons
    applyButtons.forEach(button => {
      button.addEventListener('click', (e) => {
        const themeId = button.getAttribute('data-apply-theme');
        this.applyTheme(themeId);
      });
    });
    
    // Reset theme button
    if (resetButton) {
      resetButton.addEventListener('click', () => {
        this.resetTheme();
      });
    }
  },
  
  /**
   * Preview a theme
   * @param {string} themeId - The ID of the theme to preview
   */
  previewTheme: function(themeId) {
    fetch(`/core/preview-theme/${themeId}/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': this.getCsrfToken()
      }
    })
      .then(response => {
        if (!response.ok) {
          throw new Error('Failed to preview theme');
        }
        return response.json();
      })
      .then(data => {
        // Reload the CSS variables
        this.loadCssVariables();
      })
      .catch(error => {
        console.error('Error previewing theme:', error);
      });
  },
  
  /**
   * Apply a theme
   * @param {string} themeId - The ID of the theme to apply
   */
  applyTheme: function(themeId) {
    fetch(`/core/apply-theme/${themeId}/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': this.getCsrfToken()
      }
    })
      .then(response => {
        if (!response.ok) {
          throw new Error('Failed to apply theme');
        }
        return response.json();
      })
      .then(data => {
        // Reload the CSS variables
        this.loadCssVariables();
      })
      .catch(error => {
        console.error('Error applying theme:', error);
      });
  },
  
  /**
   * Reset theme to default
   */
  resetTheme: function() {
    fetch('/core/reset-theme/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': this.getCsrfToken()
      }
    })
      .then(response => {
        if (!response.ok) {
          throw new Error('Failed to reset theme');
        }
        return response.json();
      })
      .then(data => {
        // Reload the CSS variables
        this.loadCssVariables();
      })
      .catch(error => {
        console.error('Error resetting theme:', error);
      });
  },
  
  /**
   * Set up accessibility controls
   */
  setupAccessibilityControls: function() {
    // High contrast toggle
    const contrastToggle = document.getElementById('high-contrast-toggle');
    if (contrastToggle) {
      contrastToggle.addEventListener('change', (e) => {
        this.updateThemePreference('high_contrast', e.target.checked);
      });
    }
    
    // Increased text spacing toggle
    const spacingToggle = document.getElementById('text-spacing-toggle');
    if (spacingToggle) {
      spacingToggle.addEventListener('change', (e) => {
        this.updateThemePreference('increase_text_spacing', e.target.checked);
      });
    }
    
    // Dyslexia friendly font toggle
    const dyslexiaToggle = document.getElementById('dyslexia-font-toggle');
    if (dyslexiaToggle) {
      dyslexiaToggle.addEventListener('change', (e) => {
        this.updateThemePreference('dyslexia_friendly_font', e.target.checked);
      });
    }
    
    // Text size controls
    const textSizeControls = document.querySelectorAll('[name="text_size"]');
    textSizeControls.forEach(control => {
      control.addEventListener('change', (e) => {
        if (e.target.checked) {
          this.updateThemePreference('text_size', e.target.value);
        }
      });
    });
  },
  
  /**
   * Update a theme preference
   * @param {string} preference - The preference to update
   * @param {string|boolean} value - The new value
   */
  updateThemePreference: function(preference, value) {
    const data = {};
    data[preference] = value;
    
    fetch('/api/core/preferences/update_theme/', {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': this.getCsrfToken()
      },
      body: JSON.stringify(data)
    })
      .then(response => {
        if (!response.ok) {
          throw new Error('Failed to update preference');
        }
        return response.json();
      })
      .then(data => {
        // Reload the CSS variables
        this.loadCssVariables();
      })
      .catch(error => {
        console.error('Error updating preference:', error);
      });
  },
  
  /**
   * Set up system preference detection
   */
  setupSystemPreferenceDetection: function() {
    // Detect system color scheme preference
    const darkModeMediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    
    // Set initial value
    if (document.documentElement.getAttribute('data-theme') === 'system') {
      document.documentElement.setAttribute('data-theme', darkModeMediaQuery.matches ? 'dark' : 'light');
    }
    
    // Listen for changes
    darkModeMediaQuery.addEventListener('change', e => {
      if (document.documentElement.getAttribute('data-theme') === 'system') {
        document.documentElement.setAttribute('data-theme', e.matches ? 'dark' : 'light');
      }
    });
    
    // Detect reduced motion preference
    const reducedMotionMediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
    
    // Set initial value
    if (reducedMotionMediaQuery.matches) {
      document.documentElement.setAttribute('data-reduced-motion', 'true');
    }
    
    // Listen for changes
    reducedMotionMediaQuery.addEventListener('change', e => {
      if (e.matches) {
        document.documentElement.setAttribute('data-reduced-motion', 'true');
      } else {
        document.documentElement.removeAttribute('data-reduced-motion');
      }
    });
  },
  
  /**
   * Get CSRF token from cookies
   * @returns {string} - CSRF token
   */
  getCsrfToken: function() {
    const name = 'csrftoken';
    let cookieValue = null;
    
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    
    return cookieValue;
  }
};

// Initialize the theme manager when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  ThemeManager.init();
});