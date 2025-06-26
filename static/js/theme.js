// Theme handling
document.addEventListener('DOMContentLoaded', function() {
    const themeProvider = document.querySelector('.theme-provider');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    
    if (prefersDark) {
        themeProvider.setAttribute('data-theme', 'dark');
        document.documentElement.classList.add('dark');
    }
    
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', e => {
        const newTheme = e.matches ? 'dark' : 'light';
        themeProvider.setAttribute('data-theme', newTheme);
        document.documentElement.classList.toggle('dark', e.matches);
    });
});
