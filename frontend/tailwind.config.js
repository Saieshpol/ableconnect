/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#f0fdfa',
          100: '#ccfbf1',
          200: '#99f6e4',
          300: '#5eead4',
          400: '#2dd4bf',
          500: '#14b8a6',
          600: '#0d9488',
          700: '#0f766e',
          800: '#115e59',
          900: '#134e4a',
        },
        aac: {
          need: '#fef3c7',
          emotion: '#e0f2fe',
          action: '#dcfce7',
          social: '#f3e8ff',
          pronoun: '#e0e7ff',
          help: '#fee2e2'
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
      },
      fontSize: {
        'accessible-sm': ['1rem', '1.5rem'],
        'accessible-base': ['1.125rem', '1.75rem'],
        'accessible-lg': ['1.25rem', '1.875rem'],
        'accessible-xl': ['1.5rem', '2rem'],
        'accessible-2xl': ['1.875rem', '2.25rem'],
        'accessible-3xl': ['2.25rem', '2.625rem'],
      }
    },
  },
  plugins: [],
}
