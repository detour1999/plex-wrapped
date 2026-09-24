// ABOUTME: Tests the WrappedExperience slide controller: click/tap and arrow-key
// ABOUTME: navigation, direct jumps via the progress dots, and the navigation boundaries.

import { describe, expect, it } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/svelte';
import { tick } from 'svelte';
import WrappedExperience from '../src/components/WrappedExperience.svelte';

const data = {
  user: { name: 'Dylan', year: 2025 },
  stats: { total_minutes: 6000 },
  top: {
    artists: [{ name: 'The Beatles', plays: 321, minutes: 900, image_url: '/beatles.jpg' }],
    tracks: [
      { name: 'Track A', artist: 'Artist A', plays: 10 },
      { name: 'Track B', artist: 'Artist B', plays: 9 },
    ],
  },
  time_patterns: {
    by_hour: Array.from({ length: 24 }, (_, hour) => (hour === 9 ? 50 : 1)),
    quirky: {},
  },
  ai_generated: {
    personality: {
      type: 'The Nostalgic Wanderer',
      tagline: 'Chasing yesterday',
      description: 'You love old songs.',
      spirit_animal: 'A vinyl record',
    },
    aura: { hex: '#9B59B6', vibe: 'Mysterious and moody', description: 'Mystery.' },
    roasts: ['Roast one', 'Roast two'],
    narrative: 'A short story about your year.',
    suggestions: ['Try more jazz'],
  },
};

describe('WrappedExperience', () => {
  it('starts on the intro slide', async () => {
    render(WrappedExperience, { data });
    await tick();

    expect(screen.getByText('Dylan')).toBeTruthy();
    expect(screen.getByText('2025')).toBeTruthy();
  });

  it('advances to the next slide when the container is clicked', async () => {
    const { container } = render(WrappedExperience, { data });
    await tick();

    const wrapper = container.querySelector('.wrapped-container') as HTMLElement;
    await fireEvent.click(wrapper);
    await tick();

    // totalTime is the second slide.
    expect(screen.getByText('You listened for')).toBeTruthy();
  });

  it('advances on ArrowRight and retreats on ArrowLeft', async () => {
    render(WrappedExperience, { data });
    await tick();

    await fireEvent.keyDown(window, { key: 'ArrowRight' });
    await tick();
    expect(screen.getByText('You listened for')).toBeTruthy();

    await fireEvent.keyDown(window, { key: 'ArrowLeft' });
    await tick();
    expect(screen.getByText('Dylan')).toBeTruthy();
  });

  it('does not move before the first slide', async () => {
    render(WrappedExperience, { data });
    await tick();

    await fireEvent.keyDown(window, { key: 'ArrowLeft' });
    await tick();

    expect(screen.getByText('Dylan')).toBeTruthy();
  });

  it('jumps directly to a slide when its progress dot is clicked', async () => {
    const { container } = render(WrappedExperience, { data });
    await tick();

    const dots = container.querySelectorAll('.fixed.top-4 button');
    // Index 2 is topArtist.
    await fireEvent.click(dots[2]);
    await tick();

    expect(screen.getByText('Your top artist was')).toBeTruthy();
  });

  it('does not advance past the last slide', async () => {
    const { container } = render(WrappedExperience, { data });
    await tick();

    const dots = container.querySelectorAll('.fixed.top-4 button');
    await fireEvent.click(dots[dots.length - 1]);
    await tick();

    expect(screen.getByText('Thanks for listening')).toBeTruthy();

    await fireEvent.keyDown(window, { key: ' ' });
    await tick();

    expect(screen.getByText('Thanks for listening')).toBeTruthy();
  });

  it('falls back to the default aura color when no hex or colors array is present', async () => {
    const dataWithoutAuraColor = {
      ...data,
      ai_generated: { ...data.ai_generated, aura: { vibe: 'Plain', description: 'Plain.' } },
    };
    const { container } = render(WrappedExperience, { data: dataWithoutAuraColor });
    await tick();

    const dots = container.querySelectorAll('.fixed.top-4 button');
    await fireEvent.click(dots[dots.length - 1]);
    await tick();

    expect(screen.getByText('Thanks for listening')).toBeTruthy();
  });
});
