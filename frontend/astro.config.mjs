// ABOUTME: Astro configuration for Last Wrapped frontend.
// ABOUTME: Integrates Svelte for interactive components and Tailwind for styling.

import { defineConfig } from 'astro/config';
import svelte from '@astrojs/svelte';
import tailwind from '@astrojs/tailwind';

export default defineConfig({
  integrations: [svelte(), tailwind()],
  output: 'static',
});
