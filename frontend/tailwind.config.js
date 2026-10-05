/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#1F1F1F", muted: "#6B6B6B", canvas: "#FAFAF8", surface: "#FFFFFF",
        sidebar: "#F7F4F1", line: "#E7E2DC", terracotta: "#C96A3D", "terracotta-hover": "#B95D31",
        "terracotta-light": "#F6E7DE", accent: "#E8B89C", success: "#2E7D32", danger: "#C62828",
      },
    },
  },
  plugins: [],
};
