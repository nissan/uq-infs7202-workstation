/**
 * Main application JavaScript file for LearnMore Plus
 */

// Document ready function
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips if tooltip elements exist
    const tooltipTriggers = document.querySelectorAll('[data-tooltip]');
    if (tooltipTriggers.length > 0) {
        tooltipTriggers.forEach(tooltip => {
            tooltip.addEventListener('mouseenter', function() {
                const tooltipText = this.getAttribute('data-tooltip');
                const tooltipEl = document.createElement('div');
                tooltipEl.className = 'tooltip';
                tooltipEl.textContent = tooltipText;
                document.body.appendChild(tooltipEl);
                
                const rect = this.getBoundingClientRect();
                tooltipEl.style.top = (rect.top - tooltipEl.offsetHeight - 10) + 'px';
                tooltipEl.style.left = (rect.left + (rect.width / 2) - (tooltipEl.offsetWidth / 2)) + 'px';
                tooltipEl.classList.add('active');
            });
            
            tooltip.addEventListener('mouseleave', function() {
                const tooltips = document.querySelectorAll('.tooltip');
                tooltips.forEach(el => el.remove());
            });
        });
    }
    
    // Handle modal toggles
    const modalToggles = document.querySelectorAll('[data-toggle="modal"]');
    if (modalToggles.length > 0) {
        modalToggles.forEach(toggle => {
            toggle.addEventListener('click', function(e) {
                e.preventDefault();
                const targetId = this.getAttribute('data-target');
                const modal = document.getElementById(targetId);
                if (modal) {
                    modal.classList.add('active');
                    
                    // Add event listeners to close modal
                    const closeButtons = modal.querySelectorAll('[data-dismiss="modal"]');
                    closeButtons.forEach(btn => {
                        btn.addEventListener('click', function() {
                            modal.classList.remove('active');
                        });
                    });
                    
                    // Close when clicking outside
                    modal.addEventListener('click', function(event) {
                        if (event.target === modal) {
                            modal.classList.remove('active');
                        }
                    });
                }
            });
        });
    }
    
    // Handle tab navigation
    const tabNavs = document.querySelectorAll('.tab-nav');
    if (tabNavs.length > 0) {
        tabNavs.forEach(nav => {
            const tabs = nav.querySelectorAll('.tab-link');
            const tabContents = document.querySelectorAll('.tab-content');
            
            tabs.forEach(tab => {
                tab.addEventListener('click', function(e) {
                    e.preventDefault();
                    
                    // Remove active class from all tabs
                    tabs.forEach(t => t.classList.remove('active'));
                    
                    // Add active class to clicked tab
                    this.classList.add('active');
                    
                    // Show corresponding tab content
                    const targetId = this.getAttribute('data-tab');
                    tabContents.forEach(content => {
                        content.classList.remove('active');
                        if (content.id === targetId) {
                            content.classList.add('active');
                        }
                    });
                });
            });
        });
    }
    
    // Handle collapsible sections
    const collapsibles = document.querySelectorAll('.collapsible-toggle');
    if (collapsibles.length > 0) {
        collapsibles.forEach(toggle => {
            toggle.addEventListener('click', function() {
                const targetId = this.getAttribute('data-target');
                const target = document.getElementById(targetId);
                
                if (target) {
                    const isExpanded = target.classList.contains('expanded');
                    
                    if (isExpanded) {
                        target.classList.remove('expanded');
                        this.setAttribute('aria-expanded', 'false');
                    } else {
                        target.classList.add('expanded');
                        this.setAttribute('aria-expanded', 'true');
                    }
                }
            });
        });
    }
    
    // Handle form validation
    const forms = document.querySelectorAll('form[data-validate]');
    if (forms.length > 0) {
        forms.forEach(form => {
            form.addEventListener('submit', function(e) {
                const requiredFields = form.querySelectorAll('[required]');
                let isValid = true;
                
                requiredFields.forEach(field => {
                    // Clear previous error
                    field.classList.remove('error');
                    const errorEl = field.parentElement.querySelector('.error-message');
                    if (errorEl) {
                        errorEl.remove();
                    }
                    
                    // Check if field is empty
                    if (!field.value.trim()) {
                        isValid = false;
                        field.classList.add('error');
                        
                        // Add error message
                        const errorMessage = document.createElement('div');
                        errorMessage.className = 'error-message';
                        errorMessage.textContent = 'This field is required';
                        field.parentElement.appendChild(errorMessage);
                    }
                });
                
                if (!isValid) {
                    e.preventDefault();
                }
            });
        });
    }
    
    // Initialize Lucide icons if available
    if (typeof lucide !== 'undefined') {
        lucide.createIcons();
    }
});