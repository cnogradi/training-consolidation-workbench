import typography from '@tailwindcss/typography';

/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          dark: '#0f172a', // Slate 900
          teal: '#0d9488', // Teal 600
          light: '#f8fafc', // Slate 50
        }
      }
    },
  },
  plugins: [
    typography,
  ],
}
