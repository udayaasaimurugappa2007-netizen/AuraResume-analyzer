/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        background: {
          dark: '#030014',
          card: 'rgba(13, 9, 31, 0.4)',
          border: 'rgba(255, 255, 255, 0.08)'
        },
        brand: {
          purple: {
            light: '#d8b4fe',
            DEFAULT: '#a855f7',
            dark: '#7e22ce'
          },
          indigo: {
            light: '#c7d2fe',
            DEFAULT: '#6366f1',
            dark: '#4338ca'
          },
          accent: '#c084fc'
        }
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
      },
      animation: {
        'pulse-slow': 'pulse 4s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'float': 'float 6s ease-in-out infinite',
      },
      keyframes: {
        float: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-10px)' },
        }
      }
    },
  },
  plugins: [],
}
