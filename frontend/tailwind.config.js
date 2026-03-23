/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#111111",
        paper: "#f5efe4",
        ember: "#d97706",
        moss: "#2f5d50",
        rose: "#cc5c4c",
      },
      boxShadow: {
        panel: "0 16px 40px rgba(0, 0, 0, 0.18)",
      },
      fontFamily: {
        display: ["Georgia", "Times New Roman", "serif"],
        body: ["Segoe UI", "Helvetica Neue", "Arial", "sans-serif"],
      },
    },
  },
  plugins: [],
};
