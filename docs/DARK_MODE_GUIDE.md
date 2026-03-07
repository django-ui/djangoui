# Dark Mode Implementation Guide

## Overview
Your Django UI project now supports dark mode with automatic theme detection and persistence. The implementation uses CSS variables and JavaScript to provide a seamless theme-switching experience.

## Features

✅ **Automatic Theme Detection** - Detects system preference (dark/light mode)  
✅ **Theme Persistence** - Saves user preference in localStorage  
✅ **Smooth Transitions** - CSS variables enable instant theme switching  
✅ **System Sync** - Automatically updates when system theme changes  
✅ **Easy API** - Simple JavaScript functions to control themes  

## How It Works

### 1. CSS Variables (styles.css)

The theme system uses CSS custom properties (variables) defined in three scopes:

```css
:root {
  /* Default theme variables */
  --bg-color: #ffffff;
  --text-color: #1a1a1a;
  --link-color: #007bff;
  /* ... more variables */
}

[data-theme="dark"] {
  /* Dark theme overrides */
  --bg-color: #1a1a1a;
  --text-color: #e8e8e8;
  --link-color: #4da3ff;
  /* ... more variables */
}

[data-theme="light"] {
  /* Light theme overrides */
  --bg-color: #ffffff;
  --text-color: #000000;
  /* ... more variables */
}
```

### 2. JavaScript API (common.html)

Three global functions are available:

#### `window.toggleTheme()`
Toggles between light and dark mode.
```javascript
// Toggle theme
const newTheme = window.toggleTheme();
console.log('Switched to:', newTheme); // 'dark' or 'light'
```

#### `window.setTheme(theme)`
Sets a specific theme.
```javascript
// Set dark theme
window.setTheme('dark');

// Set light theme
window.setTheme('light');
```

#### `window.getCurrentTheme()`
Gets the current theme.
```javascript
const currentTheme = window.getCurrentTheme();
console.log('Current theme:', currentTheme); // 'dark' or 'light'
```

## Usage Examples

### Example 1: Add a Toggle Button to Your Page

Add this HTML to any template that extends common.html:

```html
<button onclick="window.toggleTheme()" class="btn btn-secondary" id="theme-toggle">
    <i class="fas fa-moon"></i> Toggle Theme
</button>
```

### Example 2: Dynamic Button with Icon Update

```html
<button onclick="toggleThemeWithIcon()" class="btn btn-sm btn-outline-secondary" id="theme-btn">
    <i class="fas fa-moon"></i>
</button>

<script>
function toggleThemeWithIcon() {
    const newTheme = window.toggleTheme();
    const btn = document.getElementById('theme-btn');
    
    if (newTheme === 'dark') {
        btn.innerHTML = '<i class="fas fa-sun"></i>';
        btn.title = 'Switch to Light Mode';
    } else {
        btn.innerHTML = '<i class="fas fa-moon"></i>';
        btn.title = 'Switch to Dark Mode';
    }
}

// Set initial icon
document.addEventListener('DOMContentLoaded', function() {
    const theme = window.getCurrentTheme();
    const btn = document.getElementById('theme-btn');
    if (theme === 'dark') {
        btn.innerHTML = '<i class="fas fa-sun"></i>';
    }
});
</script>
```

### Example 3: Theme-Aware Component

```javascript
// Listen for theme changes
window.addEventListener('themeChanged', function(event) {
    const newTheme = event.detail.theme;
    console.log('Theme changed to:', newTheme);
    
    // Update your component based on theme
    if (newTheme === 'dark') {
        // Apply dark mode specific logic
        document.getElementById('myChart').updateColors('dark');
    } else {
        // Apply light mode specific logic
        document.getElementById('myChart').updateColors('light');
    }
});
```

### Example 4: Dropdown Theme Selector

```html
<select onchange="window.setTheme(this.value)" class="form-control" style="width: auto;">
    <option value="light">☀️ Light</option>
    <option value="dark">🌙 Dark</option>
</select>

<script>
// Set initial selection
document.addEventListener('DOMContentLoaded', function() {
    const select = document.querySelector('select');
    select.value = window.getCurrentTheme();
});
</script>
```

## Adding Theme Support to Custom CSS

When creating new styles, use CSS variables instead of hardcoded colors:

### ❌ Don't Do This:
```css
.my-card {
    background-color: #ffffff;
    color: #000000;
    border: 1px solid #cccccc;
}
```

### ✅ Do This:
```css
.my-card {
    background-color: var(--card-bg);
    color: var(--text-color);
    border: 1px solid var(--border-color);
}
```

## Available CSS Variables

| Variable | Light Mode | Dark Mode | Usage |
|----------|------------|-----------|-------|
| `--bg-color` | #ffffff | #1a1a1a | Main background |
| `--text-color` | #000000 | #e8e8e8 | Main text |
| `--link-color` | #007bff | #4da3ff | Links |
| `--link-hover-color` | #0056b3 | #80bdff | Link hover |
| `--border-color` | #e6e7e9 | #3a3a3a | Borders |
| `--input-bg` | #fefefe | #2a2a2a | Input backgrounds |
| `--input-border` | #ced4da | #4a4a4a | Input borders |
| `--input-disabled-bg` | #ececec | #333333 | Disabled inputs |
| `--card-bg` | #ffffff | #252525 | Card backgrounds |
| `--shadow-color` | rgba(0,0,0,0.1) | rgba(0,0,0,0.5) | Shadows |

## Adding New CSS Variables

To add new theme-aware colors:

1. Add to `:root` (default):
```css
:root {
    --my-new-color: #ff0000;
}
```

2. Add dark mode override:
```css
[data-theme="dark"] {
    --my-new-color: #ff6666;
}
```

3. Add light mode override (optional):
```css
[data-theme="light"] {
    --my-new-color: #cc0000;
}
```

4. Use in your styles:
```css
.my-element {
    color: var(--my-new-color);
}
```

## Browser Compatibility

- ✅ Chrome 49+
- ✅ Firefox 31+
- ✅ Safari 9.1+
- ✅ Edge 15+
- ✅ All modern mobile browsers

## Troubleshooting

### Theme not persisting after page reload
- Check browser localStorage is enabled
- Check browser console for errors

### Colors not changing
- Ensure you're using CSS variables (`var(--variable-name)`)
- Check that `data-theme` attribute is set on `<html>` element
- Clear browser cache

### System preference not detected
- Ensure browser supports `prefers-color-scheme` media query
- Check browser settings allow website theme detection

## Testing

Test your theme implementation:

```javascript
// In browser console:

// Test toggle
window.toggleTheme();

// Test setting specific theme
window.setTheme('dark');
window.setTheme('light');

// Check current theme
console.log(window.getCurrentTheme());

// Check localStorage
console.log(localStorage.getItem('theme'));

// Check HTML attribute
console.log(document.documentElement.getAttribute('data-theme'));
```

## Best Practices

1. **Always use CSS variables** for colors that should change with theme
2. **Test both themes** when adding new UI components
3. **Consider contrast ratios** for accessibility (WCAG 2.1 guidelines)
4. **Provide a visible toggle** so users can easily switch themes
5. **Respect system preferences** by default
6. **Use semantic variable names** (e.g., `--primary-bg` not `--blue-bg`)

## Next Steps

1. Add a theme toggle button to your navigation bar
2. Update any remaining hardcoded colors to use CSS variables
3. Test all pages in both light and dark modes
4. Consider adding a "system" option that always follows OS preference
5. Add smooth transitions for theme changes (optional)

## Example: Adding Smooth Transitions

Add this to your CSS for smooth color transitions:

```css
* {
    transition: background-color 0.3s ease, 
                color 0.3s ease, 
                border-color 0.3s ease;
}
```

⚠️ **Note**: Be careful with universal transitions as they can affect performance on complex pages.
