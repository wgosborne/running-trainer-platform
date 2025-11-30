/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Soft green spring theme
        spring: {
          50: '#f0fdf4',   // lightest green
          100: '#dcfce7',  // very light green
          200: '#bbf7d0',  // light green
          300: '#86efac',  // soft green
          400: '#4ade80',  // medium green
          500: '#22c55e',  // primary green
          600: '#16a34a',  // darker green
          700: '#15803d',  // deep green
          800: '#166534',  // very deep green
          900: '#14532d',  // darkest green
        },
        // Spring accent colors
        peach: {
          50: '#fff7ed',
          100: '#ffedd5',
          200: '#fed7aa',
          300: '#fdba74',
          400: '#fb923c',
          500: '#f97316',  // primary peach
          600: '#ea580c',
          700: '#c2410c',
        },
        sky: {
          50: '#f0f9ff',
          100: '#e0f2fe',
          200: '#bae6fd',
          300: '#7dd3fc',
          400: '#38bdf8',
          500: '#0ea5e9',  // primary sky
          600: '#0284c7',
          700: '#0369a1',
        },
        coral: {
          50: '#fff1f2',
          100: '#ffe4e6',
          200: '#fecdd3',
          300: '#fda4af',
          400: '#fb7185',
          500: '#f43f5e',  // primary coral
          600: '#e11d48',
          700: '#be123c',
        },
        sunshine: {
          50: '#fefce8',
          100: '#fef9c3',
          200: '#fef08a',
          300: '#fde047',
          400: '#facc15',
          500: '#eab308',  // primary yellow
          600: '#ca8a04',
          700: '#a16207',
        },
      },
    },
  },
  plugins: [],
}
