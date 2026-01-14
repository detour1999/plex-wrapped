// ABOUTME: Tailwind CSS configuration for Last Wrapped.
// ABOUTME: Custom colors and animations for the wrapped experience.

/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{astro,html,js,jsx,md,mdx,svelte,ts,tsx,vue}'],
  theme: {
    extend: {
      colors: {
        wrapped: {
          bg: '#121212',
          card: '#1a1a1a',
          accent: '#1DB954',
          text: '#ffffff',
          muted: '#b3b3b3',
        },
        landing: {
          black: '#1a1a1a',
          cream: '#faf6f0',
          paper: '#f4e9d8',
          orange: '#e85d04',
          green: '#606c38',
        },
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-out',
        'slide-up': 'slideUp 0.5s ease-out',
        'count-up': 'countUp 2s ease-out',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(20px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
      },
    },
  },
  plugins: [],
};
