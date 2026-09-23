// ABOUTME: Tests that the Aura slide reads the color fields the AI generator actually produces.
// ABOUTME: Covers the "hex" field and the legacy "colors" array fallback.

import { describe, expect, it } from 'vitest';
import { render, screen } from '@testing-library/svelte';
import { tick } from 'svelte';
import Aura from '../src/components/slides/Aura.svelte';

// jsdom normalizes hex colors written into style attributes to rgb(), so
// assertions compare against that normalized form instead of the hex string.
const rgb = (r: number, g: number, b: number) => `rgb(${r}, ${g}, ${b})`;

describe('Aura slide', () => {
  it('uses the "hex" field for the gradient orb and headline color', async () => {
    const aura = {
      color: 'Midnight Purple',
      hex: '#9B59B6',
      vibe: 'Mysterious and moody',
      description: 'Your aura radiates mystery.',
    };

    const { container } = render(Aura, { aura, visible: true });
    await tick();

    const orb = container.querySelector('.rounded-full');
    expect(orb?.getAttribute('style')).toContain(rgb(155, 89, 182));

    const headline = screen.getByText('Mysterious and moody');
    expect(headline.getAttribute('style')).toContain(rgb(155, 89, 182));
  });

  it('falls back to the "colors" array when "hex" is missing', async () => {
    const aura = {
      vibe: 'Chaotic good',
      description: 'You contain multitudes.',
      colors: ['#111111', '#222222'],
    };

    const { container } = render(Aura, { aura, visible: true });
    await tick();

    const orb = container.querySelector('.rounded-full');
    expect(orb?.getAttribute('style')).toContain(rgb(17, 17, 17));
    expect(orb?.getAttribute('style')).toContain(rgb(34, 34, 34));
  });
});
