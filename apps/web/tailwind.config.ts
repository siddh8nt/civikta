import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}", "./lib/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        brand: {
          DEFAULT: "#0f766e", // teal-700
          dark: "#115e59",
          light: "#5eead4",
        },
      },
    },
  },
  plugins: [],
};

export default config;
