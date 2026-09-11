/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        studio: {
          bg: "#0B0F19",
          card: "#111827",
          border: "#1F2937",
          accent: "#3B82F6",
          accentHover: "#2563EB",
          emerald: "#10B981",
          gold: "#F59E0B"
        }
      }
    },
  },
  plugins: [],
}
