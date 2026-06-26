/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        indigo: {
          50: '#ecfeff',
          100: '#cffafe',
          200: '#a5f3fc',
          300: '#67e8f9',
          400: '#06b6d4', // Cyber Cyan primary
          500: '#0891b2', 
          600: '#0e7490',
          700: '#155e75',
          800: '#164e63',
          900: '#083344',
          950: '#021822',
        },
      },
      boxShadow: {
        soft: "0 18px 55px rgba(15, 23, 42, 0.12)",
      },
    },
  },
  plugins: [],
}
