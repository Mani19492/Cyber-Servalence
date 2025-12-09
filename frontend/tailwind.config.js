/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./pages/**/*.{js,jsx,ts,tsx}",
    "./components/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        bgDark: "#050816",
        cardDark: "#0f172a",
        accent: "#22c55e",
      },
    },
  },
  plugins: [],
};
