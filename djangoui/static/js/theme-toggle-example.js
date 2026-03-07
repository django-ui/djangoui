/**
 * Theme Toggle Example
 * 
 * This file demonstrates how to use the theme toggle functionality
 * that's been added to common.html
 */

// Example 1: Create a simple toggle button
function createThemeToggleButton() {
    const button = document.createElement('button');
    button.id = 'theme-toggle-btn';
    button.className = 'btn btn-sm';
    button.style.cssText = 'position: fixed; top: 10px; right: 10px; z-index: 9999;';
    
    // Set initial icon based on current theme
    updateButtonIcon(button);
    
    // Add click handler
    button.addEventListener('click', function() {
        const newTheme = window.toggleTheme();
        updateButtonIcon(button);
        console.log('Theme switched to:', newTheme);
    });
    
    document.body.appendChild(button);
}

function updateButtonIcon(button) {
    const currentTheme = window.getCurrentTheme();
    if (currentTheme === 'dark') {
        button.innerHTML = '<i class="fas fa-sun"></i> Light Mode';
        button.title = 'Switch to Light Mode';
    } else {
        button.innerHTML = '<i class="fas fa-moon"></i> Dark Mode';
        button.title = 'Switch to Dark Mode';
    }
}

// Example 2: Listen for theme changes
window.addEventListener('themeChanged', function(event) {
    console.log('Theme changed to:', event.detail.theme);
    // You can update UI elements here based on the new theme
});

// Example 3: Set theme programmatically
function setLightTheme() {
    window.setTheme('light');
}

function setDarkTheme() {
    window.setTheme('dark');
}

// Example 4: Get current theme
function logCurrentTheme() {
    const theme = window.getCurrentTheme();
    console.log('Current theme:', theme);
}

// Initialize theme toggle button when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', createThemeToggleButton);
} else {
    createThemeToggleButton();
}
