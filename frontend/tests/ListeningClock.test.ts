// ABOUTME: Tests that the ListeningClock slide identifies the peak listening hour,
// ABOUTME: labels it correctly, and classifies the listener's time-of-day personality.

import { describe, expect, it } from 'vitest';
import { render, screen } from '@testing-library/svelte';
import { tick } from 'svelte';
import ListeningClock from '../src/components/slides/ListeningClock.svelte';

function hourlyData(peakHour: number, peakPlays = 100): Array<{ hour: number; plays: number }> {
  return Array.from({ length: 24 }, (_, hour) => ({
    hour,
    plays: hour === peakHour ? peakPlays : 1,
  }));
}

describe('ListeningClock slide', () => {
  it('labels a night-time peak hour as "Night Owl"', async () => {
    render(ListeningClock, { hourly_data: hourlyData(3), visible: true });
    await tick();

    expect(screen.getByText('3am')).toBeTruthy();
    expect(screen.getByText('Night Owl')).toBeTruthy();
  });

  it('labels a morning peak hour as "Morning Person" and formats hour 0 and 12 specially', async () => {
    render(ListeningClock, { hourly_data: hourlyData(9), visible: true });
    await tick();

    expect(screen.getByText('9am')).toBeTruthy();
    expect(screen.getByText('Morning Person')).toBeTruthy();
    // Hour 0 and hour 12 are rendered as clock emoji labels, not text labels,
    // but 12pm should still appear once it becomes the peak.
  });

  it('labels an afternoon peak hour as "Afternoon Groover"', async () => {
    render(ListeningClock, { hourly_data: hourlyData(14), visible: true });
    await tick();

    expect(screen.getByText('2pm')).toBeTruthy();
    expect(screen.getByText('Afternoon Groover')).toBeTruthy();
  });

  it('labels an evening peak hour as "Evening Listener"', async () => {
    render(ListeningClock, { hourly_data: hourlyData(19), visible: true });
    await tick();

    expect(screen.getByText('7pm')).toBeTruthy();
    expect(screen.getByText('Evening Listener')).toBeTruthy();
  });

  it('formats a noon peak as "12pm"', async () => {
    render(ListeningClock, { hourly_data: hourlyData(12), visible: true });
    await tick();

    expect(screen.getByText('12pm')).toBeTruthy();
  });

  it('formats a midnight peak as "12am"', async () => {
    render(ListeningClock, { hourly_data: hourlyData(0), visible: true });
    await tick();

    expect(screen.getByText('12am')).toBeTruthy();
  });
});
