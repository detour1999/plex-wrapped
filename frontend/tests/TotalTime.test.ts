// ABOUTME: Tests that the TotalTime slide converts minutes into hours and days correctly.
// ABOUTME: The animated counter itself is covered by AnimatedNumber.test.ts.

import { describe, expect, it } from 'vitest';
import { render, screen } from '@testing-library/svelte';
import { tick } from 'svelte';
import TotalTime from '../src/components/slides/TotalTime.svelte';

describe('TotalTime slide', () => {
  it('converts minutes to rounded hours and days with one decimal', async () => {
    render(TotalTime, { totalMinutes: 12345, visible: true });
    await tick();

    // 12345 / 60 = 205.75 -> rounds to 206 hours
    expect(screen.getByText(/206 hours/)).toBeTruthy();
    // 12345 / 60 / 24 = 8.5729... -> 8.6 days
    expect(screen.getByText(/8\.6 days/)).toBeTruthy();
  });

  it('handles zero minutes without error', async () => {
    render(TotalTime, { totalMinutes: 0, visible: true });
    await tick();

    expect(screen.getByText(/0 hours/)).toBeTruthy();
    expect(screen.getByText(/0\.0 days/)).toBeTruthy();
  });
});
