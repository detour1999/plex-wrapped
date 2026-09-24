// ABOUTME: Vitest configuration for testing Svelte components in jsdom.
// ABOUTME: Compiles .svelte files with the Svelte plugin and cleans up rendered components.

import { defineConfig } from 'vitest/config';
import { svelte } from '@sveltejs/vite-plugin-svelte';
import { svelteTesting } from '@testing-library/svelte/vite';

export default defineConfig({
  plugins: [svelte(), svelteTesting()],
  test: {
    environment: 'jsdom',
    include: ['tests/**/*.test.ts'],
    setupFiles: ['tests/setup.ts'],
    coverage: {
      provider: 'v8',
      // .astro pages/layouts are server-rendered templates, not component logic
      // Vitest exercises the same way Svelte components are - and config files
      // aren't application code. Both are out of scope for this coverage gate.
      include: ['src/components/**/*.svelte', 'src/lib/**/*.ts'],
      // Floor matches the real current baseline (only 3 of ~15 components have
      // tests yet) - it exists to catch regressions, not to demand the rest of
      // the component library be tested in one pass.
      thresholds: {
        statements: 10,
        branches: 65,
        functions: 30,
        lines: 10,
      },
    },
  },
});
