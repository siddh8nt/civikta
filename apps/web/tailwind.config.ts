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
        // Warm citizen-app palette — replaces stark white/cool-slate
        // backgrounds in the citizen-facing surfaces only.
        cream: "#f6f1e7",  // page background
        paper: "#fffdf7",  // card / surface background
      },
    },
  },
  plugins: [],
};

export default config;
