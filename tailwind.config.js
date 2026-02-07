/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        earth: {
          100: '#F5F5DC', // Beige
          200: '#EDE0D4',
          300: '#E6CCB2',
          400: '#DDB892',
          500: '#B08968',
          600: '#9C6644',
          700: '#7F5539', // Medium Brown
          800: '#8B4513', // Saddle Brown
          900: '#5D4037', // Dark Brown
        },
        vitality: {
          50: '#E8F5E9',
          100: '#C8E6C9',
          500: '#4CAF50',
          600: '#2E8B57', // Sea Green
          700: '#388E3C',
        },
        tech: {
          50: '#E3F2FD',
          500: '#2196F3',
          600: '#4682B4', // Steel Blue
          700: '#1976D2',
        }
      },
      fontFamily: {
        sans: ['"Noto Sans TC"', 'ui-sans-serif', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
