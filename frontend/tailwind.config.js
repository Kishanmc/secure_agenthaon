/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        cyber: {
          bg: "#0B0F19",
          card: "#161B2A",
          border: "#2A364F",
          accent: "#3B82F6",
          green: "#10B981",
          purple: "#8B5CF6",
          red: "#EF4444",
          text: "#E2E8F0",
          muted: "#94A3B8"
        }
      },
      boxShadow: {
        neon: "0 0 15px rgba(59, 130, 246, 0.4)",
        neonGreen: "0 0 15px rgba(16, 185, 129, 0.4)",
        neonRed: "0 0 15px rgba(239, 68, 68, 0.4)",
        neonPurple: "0 0 15px rgba(139, 92, 246, 0.4)",
      },
      fontFamily: {
        mono: ['Courier New', 'Courier', 'monospace'],
        sans: ['Inter', 'sans-serif'],
      }
    },
  },
  plugins: [],
}
