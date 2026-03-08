/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['var(--font-orbitron)', 'sans-serif'],
        mono: ['var(--font-fira-code)', 'monospace'],
      },
      colors: {
        vscode: {
          bg: '#1e1e1e',
          sidebar: '#252526',
          activityBar: '#333333',
          text: '#d4d4d4',
          blue: '#569cd6',
          green: '#6a9955',
          orange: '#ce9178',
          yellow: '#dcdcaa',
          purple: '#c586c0',
          border: '#3c3c3c'
        }
      }
    },
  },
  plugins: [],
}