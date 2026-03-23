/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class', // Enable class-based dark mode
  theme: {
    extend: {
      colors: {
        background: 'var(--background)',
        foreground: 'var(--foreground)',
        cyanAccent: '#5227FF', // Antigravity Purple
        copperAccent: '#FF9FFC', // Antigravity Pink
        glassDark: 'rgba(15, 23, 42, 0.65)',
        glassLight: 'rgba(255, 255, 255, 0.75)',
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        mono: ['Roboto Mono', 'monospace'],
      },
      animation: {
        'scanner': 'scanner 2s linear infinite',
        'pulse-glow': 'pulse-glow 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
      keyframes: {
        scanner: {
          '0%': { transform: 'translateY(-100%)', opacity: '0' },
          '10%': { opacity: '1' },
          '90%': { opacity: '1' },
          '100%': { transform: 'translateY(100%)', opacity: '0' },
        },
        'pulse-glow': {
          '0%, 100%': {
            opacity: '1',
            boxShadow: '0 0 15px 0px rgba(82, 39, 255, 0.6)',
          },
          '50%': {
            opacity: '.8',
            boxShadow: '0 0 5px 0px rgba(82, 39, 255, 0.2)',
          },
        }
      }
    },
  },
  plugins: [],
}