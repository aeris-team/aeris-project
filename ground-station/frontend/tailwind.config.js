/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      },
      colors: {
        aeris: {
          light: '#d1fae5',
          DEFAULT: '#059669',
          dark: '#047857',
        },
        danger: {
          light: '#fee2e2',
          DEFAULT: '#dc2626',
          dark: '#b91c1c',
        },
        warning: {
          DEFAULT: '#d97706',
        }
      }
    },
  },
  plugins: [],
}
