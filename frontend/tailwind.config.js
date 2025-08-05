/** @type {import('tailwindcss').Config} */
/*  <repo-root>/frontend/tailwind.config.js  */
module.exports = {
  /* ———————————————————————————————————————
     1. Core options
  ——————————————————————————————————————— */
  darkMode: ['class'], // toggle via class="dark" on <html> or <body>

  /* ———————————————————————————————————————
     2. Paths Tailwind should scan
  ——————————————————————————————————————— */
  content: [
    './app/**/*.{js,jsx,ts,tsx}',            // every page / component in app router
    './components/**/*.{js,jsx,ts,tsx}',     // shared components folder
    './app/components/**/*.{js,jsx,ts,tsx}', // nested components (optional)
    './app/global.css',                      // global stylesheet (contains @tailwind)
  ],

  /* ———————————————————————————————————————
     3. Theme customisation
  ——————————————————————————————————————— */
  theme: {
    extend: {
      /* ---- border radius tokens ---- */
      borderRadius: {
        lg: 'var(--radius)',
        md: 'calc(var(--radius) - 2px)',
        sm: 'calc(var(--radius) - 4px)',
      },

      /* ---- colour palette (CSS vars) ---- */
      colors: {
        background:  'hsl(var(--background))',
        foreground:  'hsl(var(--foreground))',

        card: {
          DEFAULT:    'hsl(var(--card))',
          foreground: 'hsl(var(--card-foreground))',
        },
        popover: {
          DEFAULT:    'hsl(var(--popover))',
          foreground: 'hsl(var(--popover-foreground))',
        },
        primary: {
          DEFAULT:    'hsl(var(--primary))',
          foreground: 'hsl(var(--primary-foreground))',
        },
        secondary: {
          DEFAULT:    'hsl(var(--secondary))',
          foreground: 'hsl(var(--secondary-foreground))',
        },
        muted: {
          DEFAULT:    'hsl(var(--muted))',
          foreground: 'hsl(var(--muted-foreground))',
        },
        accent: {
          DEFAULT:    'hsl(var(--accent))',
          foreground: 'hsl(var(--accent-foreground))',
        },
        destructive: {
          DEFAULT:    'hsl(var(--destructive))',
          foreground: 'hsl(var(--destructive-foreground))',
        },

        border: 'hsl(var(--border))',
        input:  'hsl(var(--input))',
        ring:   'hsl(var(--ring))',

        /* small categorical palette for charts */
        chart: {
          '1': 'hsl(var(--chart-1))',
          '2': 'hsl(var(--chart-2))',
          '3': 'hsl(var(--chart-3))',
          '4': 'hsl(var(--chart-4))',
          '5': 'hsl(var(--chart-5))',
        },
      },
    },
  },

  /* ———————————————————————————————————————
     4. Plugins
  ——————————————————————————————————————— */
  plugins: [
    require('tailwindcss-animate'),
  ],
};
