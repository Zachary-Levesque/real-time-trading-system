/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#07111f",
        signal: "#22c55e",
        caution: "#f59e0b",
        alert: "#ef4444",
        mist: "#d9e6f2",
      },
      fontFamily: {
        sans: ["'Space Grotesk'", "ui-sans-serif", "system-ui", "sans-serif"],
      },
      boxShadow: {
        panel: "0 24px 80px rgba(7, 17, 31, 0.45)",
      },
      backgroundImage: {
        grid: "linear-gradient(rgba(217,230,242,0.06) 1px, transparent 1px), linear-gradient(90deg, rgba(217,230,242,0.06) 1px, transparent 1px)",
      },
      backgroundSize: {
        grid: "40px 40px",
      },
    },
  },
  plugins: [],
};

