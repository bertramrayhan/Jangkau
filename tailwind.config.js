/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './webapp/templates/**/*.html',
  ],
  darkMode: "class",
  theme: {
      extend: {
          colors: {
              "primary": "#166434",
              "accent": "#F59E0B",
              "background-light": "#F9FAFB",
              "background-dark": "#122017",
              "dark-charcoal": "#1F2937",
              "medium-gray": "#6B7280",
          },
          fontFamily: {
              "display": ["Inter", "sans-serif"]
          },
          borderRadius: {
              "DEFAULT": "0.5rem", 
              "lg": "0.5rem", 
              "xl": "0.75rem", 
              "full": "9999px"
          },
      },
  },
  plugins: [
    // require('@tailwindcss/forms'),
    // require('@tailwindcss/container-queries'),
  ],
}