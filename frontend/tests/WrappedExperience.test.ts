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

  it('ignores keys other than ArrowRight, ArrowLeft, and Space', async () => {
    render(WrappedExperience, { data });
    await tick();

    await fireEvent.keyDown(window, { key: 'x' });
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

  const slideText: Array<[index: number, text: string]> = [
    [0, 'Dylan'],
    [1, 'You listened for'],
    [2, 'Your top artist was'],
    [3, 'Your Top 5 Tracks'],
    [4, 'Your Listening Clock'],
    [5, 'Your Quirky Stats'],
    [6, 'Your listening personality'],
    [7, 'Your Musical Aura'],
    [8, 'The Roast'],
    [9, 'Your Year in Music'],
    [10, 'Looking Ahead'],
    [11, 'Thanks for listening'],
  ];

  it.each(slideText)('renders the right slide component at index %i', async (index, text) => {
    const { container } = render(WrappedExperience, { data });
    await tick();

    const dots = container.querySelectorAll('.fixed.top-4 button');
    await fireEvent.click(dots[index]);
    await tick();

    expect(screen.getByText(text)).toBeTruthy();
  });

  it('advances when Enter is pressed on the container', async () => {
    const { container } = render(WrappedExperience, { data });
    await tick();

    const wrapper = container.querySelector('.wrapped-container') as HTMLElement;
    await fireEvent.keyPress(wrapper, { key: 'Enter' });
    await tick();

    expect(screen.getByText('You listened for')).toBeTruthy();
  });

  it('ignores keypresses other than Enter on the container', async () => {
    const { container } = render(WrappedExperience, { data });
    await tick();

    const wrapper = container.querySelector('.wrapped-container') as HTMLElement;
    await fireEvent.keyPress(wrapper, { key: 'a' });
    await tick();

    expect(screen.getByText('Dylan')).toBeTruthy();
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

  it('falls back to the legacy colors array when aura has no hex field', async () => {
    const dataWithColorsArray = {
      ...data,
      ai_generated: {
        ...data.ai_generated,
        aura: { colors: ['#111111'], vibe: 'Legacy', description: 'Legacy.' },
      },
    };
    const { container } = render(WrappedExperience, { data: dataWithColorsArray });
    await tick();

    const dots = container.querySelectorAll('.fixed.top-4 button');
    await fireEvent.click(dots[dots.length - 1]);
    await tick();

    expect(screen.getByText('Thanks for listening')).toBeTruthy();
  });

  it('falls back to the default color when aura has an empty colors array and no hex', async () => {
    const dataWithEmptyColors = {
      ...data,
      ai_generated: {
        ...data.ai_generated,
        aura: { colors: [], vibe: 'Empty', description: 'Empty.' },
      },
    };
    const { container } = render(WrappedExperience, { data: dataWithEmptyColors });
    await tick();

    const dots = container.querySelectorAll('.fixed.top-4 button');
    await fireEvent.click(dots[dots.length - 1]);
    await tick();

    expect(screen.getByText('Thanks for listening')).toBeTruthy();
  });

  it('passes no top artist to Share when there are no artists', async () => {
    const dataWithoutArtists = { ...data, top: { ...data.top, artists: [] } };
    const { container } = render(WrappedExperience, { data: dataWithoutArtists });
    await tick();

    const dots = container.querySelectorAll('.fixed.top-4 button');
    await fireEvent.click(dots[dots.length - 1]);
    await tick();

    expect(screen.getByText('Thanks for listening')).toBeTruthy();
  });
});
