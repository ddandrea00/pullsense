/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        github: {
          primary: "#24292e",
          secondary: "#586069",
          success: "#28a745",
          warning: "#ffd33d",
          danger: "#d73a49",
        },
      },
    },
  },
  plugins: [],
};
