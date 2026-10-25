/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: ["Poppins", "ui-sans-serif", "system-ui", "sans-serif"],
      },
      colors: {
        navy: {
          950: "#0b1220",
          900: "#0f1a2e",
          800: "#152238",
          700: "#1c2d48",
        },
        teal: {
          500: "#0f9b8e",
          600: "#0c7f75",
        },
        wind: {
          actual: "#2f8f4e",
          forecast: "#0f9b8e",
        },
      },
      boxShadow: {
        card: "0 1px 2px 0 rgb(15 23 42 / 0.06), 0 1px 1px 0 rgb(15 23 42 / 0.04)",
      },
    },
  },
  plugins: [],
};
