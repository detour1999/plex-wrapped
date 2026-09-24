// ABOUTME: Tests that the SummaryCard (used for the downloadable share image) renders
// ABOUTME: all wrapped stats, and omits the top-artist block when there isn't one.

import { describe, expect, it } from 'vitest';
import { render, screen } from '@testing-library/svelte';
import { tick } from 'svelte';
import SummaryCard from '../src/components/common/SummaryCard.svelte';

describe('SummaryCard', () => {
  it('renders name, year, hours, top artist, personality, and aura', async () => {
    render(SummaryCard, {
      userName: 'Dylan',
      year: 2025,
      totalMinutes: 6000,
      topArtist: { name: 'The Beatles', plays: 321 },
      personalityType: 'The Nostalgic Wanderer',
      auraColor: '#9B59B6',
      auraVibe: 'Mysterious and moody',
    });
    await tick();

    expect(screen.getByText("Dylan's")).toBeTruthy();
    expect(screen.getByText('2025')).toBeTruthy();
    // 6000 minutes / 60 = 100 hours
    expect(screen.getByText('100')).toBeTruthy();
    expect(screen.getByText('The Beatles')).toBeTruthy();
    expect(screen.getByText('321 plays')).toBeTruthy();
    expect(screen.getByText('The Nostalgic Wanderer')).toBeTruthy();
    expect(screen.getByText('Mysterious and moody')).toBeTruthy();
  });

  it('omits the top artist block when topArtist is null', async () => {
    render(SummaryCard, {
      userName: 'Dylan',
      year: 2025,
      totalMinutes: 6000,
      topArtist: null,
      personalityType: 'The Nostalgic Wanderer',
      auraColor: '#9B59B6',
      auraVibe: 'Mysterious and moody',
    });
    await tick();

    expect(screen.queryByText('Top Artist')).toBeNull();
  });
});
