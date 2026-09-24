// ABOUTME: Tests that the QuirkyStats slide independently renders each optional stat
// ABOUTME: card (late night anthem, longest session, most repeated, genre mood).

import { describe, expect, it } from 'vitest';
import { render, screen } from '@testing-library/svelte';
import { tick } from 'svelte';
import QuirkyStats from '../src/components/slides/QuirkyStats.svelte';

describe('QuirkyStats slide', () => {
  it('renders no stat cards when nothing is provided', async () => {
    render(QuirkyStats, { stats: {}, visible: true });
    await tick();

    expect(screen.queryByText('Late Night Anthem')).toBeNull();
    expect(screen.queryByText('Marathon Session')).toBeNull();
    expect(screen.queryByText('Repeat Champion')).toBeNull();
    expect(screen.queryByText('Mood Shifts')).toBeNull();
  });

  it('renders the late night anthem card', async () => {
    render(QuirkyStats, {
      stats: { late_night_anthem: { name: 'Midnight Song', artist: 'Night Owl', count: 12 } },
      visible: true,
    });
    await tick();

    expect(screen.getByText('Late Night Anthem')).toBeTruthy();
    expect(screen.getByText('Midnight Song')).toBeTruthy();
    expect(screen.getByText(/Night Owl/)).toBeTruthy();
    expect(screen.getByText(/Played 12 times after midnight/)).toBeTruthy();
  });

  it('renders the longest session card with hours and minutes', async () => {
    render(QuirkyStats, {
      stats: { longest_session: { duration_minutes: 125, date: '2025-06-01T00:00:00Z' } },
      visible: true,
    });
    await tick();

    expect(screen.getByText('Marathon Session')).toBeTruthy();
    // 125 minutes = 2h 5m
    expect(screen.getByText(/2h/)).toBeTruthy();
    expect(screen.getByText(/5m/)).toBeTruthy();
  });

  it('renders the most repeated card', async () => {
    render(QuirkyStats, {
      stats: { most_repeated: { name: 'Repeat Song', artist: 'Loop Artist', streak: 7 } },
      visible: true,
    });
    await tick();

    expect(screen.getByText('Repeat Champion')).toBeTruthy();
    expect(screen.getByText('Repeat Song')).toBeTruthy();
    expect(screen.getByText(/Played 7 times in a row/)).toBeTruthy();
  });

  it('renders the genre mood card', async () => {
    render(QuirkyStats, {
      stats: { genre_mood: { morning: 'Chill', evening: 'Energetic' } },
      visible: true,
    });
    await tick();

    expect(screen.getByText('Mood Shifts')).toBeTruthy();
    expect(screen.getByText('Chill')).toBeTruthy();
    expect(screen.getByText('Energetic')).toBeTruthy();
  });

  it('adds each stat card once its data arrives on an already-visible slide', async () => {
    const { rerender } = render(QuirkyStats, { stats: {}, visible: true });
    await tick();

    await rerender({
      stats: { late_night_anthem: { name: 'Midnight Song', artist: 'Night Owl', count: 12 } },
      visible: true,
    });
    await tick();
    expect(screen.getByText('Late Night Anthem')).toBeTruthy();

    await rerender({
      stats: { longest_session: { duration_minutes: 125, date: '2025-06-01T00:00:00Z' } },
      visible: true,
    });
    await tick();
    expect(screen.getByText('Marathon Session')).toBeTruthy();

    await rerender({
      stats: { most_repeated: { name: 'Repeat Song', artist: 'Loop Artist', streak: 7 } },
      visible: true,
    });
    await tick();
    expect(screen.getByText('Repeat Champion')).toBeTruthy();

    await rerender({
      stats: { genre_mood: { morning: 'Chill', evening: 'Energetic' } },
      visible: true,
    });
    await tick();
    expect(screen.getByText('Mood Shifts')).toBeTruthy();
  });

  it('renders its content when toggled from hidden to visible after mount', async () => {
    const stats = {
      late_night_anthem: { name: 'Midnight Song', artist: 'Night Owl', count: 12 },
      longest_session: { duration_minutes: 125, date: '2025-06-01T00:00:00Z' },
      most_repeated: { name: 'Repeat Song', artist: 'Loop Artist', streak: 7 },
      genre_mood: { morning: 'Chill', evening: 'Energetic' },
    };
    const { rerender } = render(QuirkyStats, { stats, visible: false });
    await tick();
    expect(screen.queryByText('Late Night Anthem')).toBeNull();

    await rerender({ stats, visible: true });
    await tick();

    expect(screen.getByText('Late Night Anthem')).toBeTruthy();
    expect(screen.getByText('Marathon Session')).toBeTruthy();
    expect(screen.getByText('Repeat Champion')).toBeTruthy();
    expect(screen.getByText('Mood Shifts')).toBeTruthy();
  });

  it('renders every card at once when all stats are present', async () => {
    render(QuirkyStats, {
      stats: {
        late_night_anthem: { name: 'Midnight Song', artist: 'Night Owl', count: 12 },
        longest_session: { duration_minutes: 125, date: '2025-06-01T00:00:00Z' },
        most_repeated: { name: 'Repeat Song', artist: 'Loop Artist', streak: 7 },
        genre_mood: { morning: 'Chill', evening: 'Energetic' },
      },
      visible: true,
    });
    await tick();

    expect(screen.getByText('Late Night Anthem')).toBeTruthy();
    expect(screen.getByText('Marathon Session')).toBeTruthy();
    expect(screen.getByText('Repeat Champion')).toBeTruthy();
    expect(screen.getByText('Mood Shifts')).toBeTruthy();
  });
});
