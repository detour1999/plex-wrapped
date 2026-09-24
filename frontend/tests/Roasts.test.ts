// ABOUTME: Tests that the Roasts slide reveals every roast over time.
// ABOUTME: Uses fake timers so the 3 second reveal interval runs instantly.

import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { render, screen } from '@testing-library/svelte';
import { tick } from 'svelte';
import Roasts from '../src/components/slides/Roasts.svelte';

const roasts = ['roast one', 'roast two', 'roast three', 'roast four', 'roast five'];

async function advance(ms: number) {
  await vi.advanceTimersByTimeAsync(ms);
  await tick();
}

const shownRoasts = () => screen.queryAllByText(/roast (one|two|three|four|five)/);

describe('Roasts slide', () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it('starts with only the first roast', async () => {
    render(Roasts, { roasts, visible: true });
    await tick();

    expect(shownRoasts()).toHaveLength(1);
  });

  it('reveals one more roast every 3 seconds until all are shown', async () => {
    render(Roasts, { roasts, visible: true });
    await tick();

    for (let expected = 2; expected <= roasts.length; expected++) {
      await advance(3000);
      expect(shownRoasts()).toHaveLength(expected);
    }
  });

  it('shows the closing line only after the last roast', async () => {
    render(Roasts, { roasts, visible: true });
    await tick();

    await advance(3000 * (roasts.length - 2));
    expect(screen.queryByText(/Just kidding/)).toBeNull();

    await advance(3000);
    expect(screen.getByText(/Just kidding/)).toBeTruthy();
  });

  it('keeps every roast on screen once revealed', async () => {
    render(Roasts, { roasts, visible: true });
    await tick();

    await advance(3000 * roasts.length * 2);

    expect(shownRoasts()).toHaveLength(roasts.length);
  });

  it('leaves no timers running when the slide is removed', async () => {
    const { unmount } = render(Roasts, { roasts, visible: true });
    await tick();
    await advance(3000);

    unmount();

    expect(vi.getTimerCount()).toBe(0);
  });

  it('never starts the reveal timer when mounted with an empty roasts list', async () => {
    render(Roasts, { roasts: [], visible: true });
    await tick();
    await advance(3000);

    expect(shownRoasts()).toHaveLength(0);
    expect(vi.getTimerCount()).toBe(0);
  });

  it('never starts the reveal timer when mounted not visible', async () => {
    render(Roasts, { roasts, visible: false });
    await tick();
    await advance(3000);

    expect(vi.getTimerCount()).toBe(0);
  });
});
