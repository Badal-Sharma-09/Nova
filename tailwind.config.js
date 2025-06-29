/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class',
  content: [
    "./templates/**/*.html", // recursive match
    "./static/**/*.css",     // recursive match
    "./static/**/*js"
  ],
  theme: {
    extend: {
      colors: {},
      animation: {
        fadeSlideIn: 'fadeSlideIn 0.6s ease-out forwards',
      },
      keyframes: {
        fadeSlideIn: {
          '0%': { opacity: 0, transform: 'translateY(20px)' },
          '100%': { opacity: 1, transform: 'translateY(0)' },
        },
      },
    },
  },
  plugins: [],
};
