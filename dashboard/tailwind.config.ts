import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#101418",
        fog: "#eef1ea",
        clay: "#b66239",
        moss: "#415d43"
      }
    }
  },
  plugins: []
};

export default config;
