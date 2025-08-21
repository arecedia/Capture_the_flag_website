// JavaScript for Dark/Light mode toggle
const toggleSwitch = document.getElementById('theme-toggle');
const body = document.body;

// Load saved theme
const currentTheme = localStorage.getItem('theme');
if (currentTheme === 'dark') {
    body.classList.add('dark-mode');
    toggleSwitch.checked = false;
} else {
    body.classList.remove('dark-mode');
    toggleSwitch.checked = true;
}

// Toggle theme on switch change
toggleSwitch.addEventListener('change', () => {
    if (toggleSwitch.checked) {
        body.classList.add('dark-mode');
        localStorage.setItem('theme', 'light');
    } else {
        body.classList.remove('dark-mode');
        localStorage.setItem('theme', 'dark');
    }
});