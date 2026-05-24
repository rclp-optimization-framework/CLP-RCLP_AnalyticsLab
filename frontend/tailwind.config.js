/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        midnight: "#0b1120",
        slatecore: "#101827",
        steel: "#334155",
        skyglass: "#dbeafe",
        electric: "#2563eb",
        electricSoft: "#60a5fa",
        fog: "#f8fafc",
      },
      boxShadow: {
        glow: "0 24px 80px rgba(37, 99, 235, 0.28)",
        panel: "0 18px 60px rgba(15, 23, 42, 0.14)",
      },
      keyframes: {
        float: {
          "0%, 100%": { transform: "translateY(0px)" },
          "50%": { transform: "translateY(-8px)" },
        },
        sheen: {
          "0%": { backgroundPosition: "0% 50%" },
          "100%": { backgroundPosition: "100% 50%" },
        },
      },
      animation: {
        float: "float 6s ease-in-out infinite",
        sheen: "sheen 10s linear infinite",
      },
    },
  },
  plugins: [],
};
