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

  it('falls back to the default green when neither "hex" nor "colors" is provided', async () => {
    const aura = { vibe: 'Undefined vibes', description: 'A blank canvas.' };

    const { container } = render(Aura, { aura, visible: true });
    await tick();

    const orb = container.querySelector('.rounded-full');
    expect(orb?.getAttribute('style')).toContain(rgb(29, 185, 84));
  });

  it('falls back to the primary color for the secondary gradient stop when "colors" has only one entry', async () => {
    const aura = { colors: ['#9B59B6'], vibe: 'Single tone', description: 'One color only.' };

    const { container } = render(Aura, { aura, visible: true });
    await tick();

    const orb = container.querySelector('.rounded-full');
    // Both gradient stops should be the same primary color.
    expect(orb?.getAttribute('style')).toContain(
      `linear-gradient(135deg, ${rgb(155, 89, 182)}, ${rgb(155, 89, 182)})`
    );
  });

  it('renders its content when toggled from hidden to visible after mount', async () => {
    const aura = { hex: '#9B59B6', vibe: 'Mysterious and moody', description: 'Mystery.' };
    const { rerender } = render(Aura, { aura, visible: false });
    await tick();
    expect(screen.queryByText('Mysterious and moody')).toBeNull();

    await rerender({ aura, visible: true });
    await tick();

    expect(screen.getByText('Mysterious and moody')).toBeTruthy();
  });
});
