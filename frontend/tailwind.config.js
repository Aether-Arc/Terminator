/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx}",
    "./components/**/*.{js,ts,jsx,tsx}",
    "./pages/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: "#2563eb",
        secondary: "#9333ea",
        darkbg: "#0f172a"
      },
      boxShadow: {
        glow: "0 0 15px rgba(59,130,246,0.5)"
      }
    },
  },
  plugins: [],
}