// ABOUTME: Astro configuration for Last Wrapped frontend.
// ABOUTME: Integrates Svelte for interactive components; Tailwind v4 runs as a Vite plugin, not an integration.

import { defineConfig } from 'astro/config';
import svelte from '@astrojs/svelte';
import tailwindcss from '@tailwindcss/vite';

export default defineConfig({
  integrations: [svelte()],
  vite: {
    plugins: [tailwindcss()],
  },
  output: 'static',
});
