/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['DM Sans', 'sans-serif'],
        display: ['Space Grotesk', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      colors: {
        rillet: {
          navy: '#1A103C',
          deepNavy: '#0F0A28',
          purple: '#53389E',
          purpleLight: '#6E49CB',
          purpleBg: '#F4F0FF',
          bg: '#FFFFFF',
          card: '#FFFFFF',
          border: '#E2E8F0',
          hover: '#F8FAFC',
          muted: '#64748B'
        }
      }
    },
  },
  plugins: [],
}
