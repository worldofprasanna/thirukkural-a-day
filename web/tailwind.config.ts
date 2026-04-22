import type { Config } from "tailwindcss";

export default {
  content: ["./app/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        cream: "#F6EAD0",
        turmeric: "#E4A32A",
        indigo: "#263468",
        terracotta: "#B25037",
        forest: "#3E5E3A",
        ink: "#1C1816",
      },
      fontFamily: {
        serif: ['"Source Serif 4"', '"Georgia"', "serif"],
        sans: ['"Inter"', "ui-sans-serif", "system-ui", "sans-serif"],
      },
    },
  },
  plugins: [],
} satisfies Config;
