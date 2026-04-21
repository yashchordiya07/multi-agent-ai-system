/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: ["'DM Sans'", "system-ui", "sans-serif"],
        mono: ["'JetBrains Mono'", "Menlo", "monospace"],
      },
      colors: {
        surface: {
          DEFAULT: "#0f1117",
          card:    "#161b27",
          raised:  "#1c2333",
          border:  "#252e42",
        },
        brand: {
          DEFAULT: "#7c6af7",
          dim:     "#7c6af720",
          border:  "#7c6af740",
        },
      },
      animation: {
        "fade-in":  "fadeIn 0.35s ease-out both",
        "slide-up": "slideUp 0.4s ease-out both",
        "pulse-slow": "pulse 2.5s cubic-bezier(0.4,0,0.6,1) infinite",
      },
      keyframes: {
        fadeIn:  { from: { opacity: 0 }                                 , to: { opacity: 1 } },
        slideUp: { from: { opacity: 0, transform: "translateY(10px)" }  , to: { opacity: 1, transform: "translateY(0)" } },
      },
    },
  },
  plugins: [],
};
