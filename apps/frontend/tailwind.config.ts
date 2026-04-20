import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}", "./lib/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#171717",
        paper: "#fbfaf7",
        basil: "#28635a",
        coral: "#d95d4f",
        gold: "#c99a2e"
      },
      boxShadow: {
        soft: "0 16px 40px rgba(23, 23, 23, 0.08)"
      }
    }
  },
  plugins: []
};

export default config;
