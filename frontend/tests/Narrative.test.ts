// ABOUTME: Tests that the Narrative slide types out its text character by character and
// ABOUTME: only shows the attribution line once the full narrative has been revealed.

import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { render, screen } from '@testing-library/svelte';
import { tick } from 'svelte';
import Narrative from '../src/components/slides/Narrative.svelte';

async function advance(ms: number) {
  await vi.advanceTimersByTimeAsync(ms);
  await tick();
}

describe('Narrative slide', () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it('shows a placeholder when there is no narrative yet', async () => {
    render(Narrative, { narrative: '', visible: true });
    await tick();

    expect(screen.getByText(/still being written/)).toBeTruthy();
  });

  it('reveals the narrative one character at a time', async () => {
    const narrative = 'Hi there';
    render(Narrative, { narrative, visible: true });
    await tick();

    // Nothing revealed yet at time 0.
    expect(screen.queryByText(narrative)).toBeNull();

    await advance(30 * narrative.length);

    expect(screen.getByText(narrative)).toBeTruthy();
  });

  it('shows the attribution line only after the full narrative is revealed', async () => {
    const narrative = 'Short story';
    render(Narrative, { narrative, visible: true });
    await tick();

    expect(screen.queryByText(/Written by AI/)).toBeNull();

    await advance(30 * narrative.length);

    expect(screen.getByText(/Written by AI/)).toBeTruthy();
  });

  it('leaves no timers running once the narrative finishes typing', async () => {
    const narrative = 'Done';
    render(Narrative, { narrative, visible: true });
    await tick();
    // One extra tick past the last character: that's the tick where the
    // interval notices it's done and clears itself.
    await advance(30 * (narrative.length + 1));

    expect(vi.getTimerCount()).toBe(0);
  });

  it('clears its interval when unmounted mid-typing', async () => {
    const narrative = 'A much longer narrative to type out slowly';
    const { unmount } = render(Narrative, { narrative, visible: true });
    await tick();
    await advance(30 * 3);

    unmount();

    expect(vi.getTimerCount()).toBe(0);
  });

  it('renders its content when toggled from hidden to visible after mount', async () => {
    const narrative = 'Short story';
    const { rerender } = render(Narrative, { narrative, visible: false });
    await tick();
    expect(screen.queryByText(/still being written/)).toBeNull();

    await rerender({ narrative, visible: true });
    await tick();
    await advance(30 * narrative.length);

    expect(screen.getByText(narrative)).toBeTruthy();
    expect(screen.getByText(/Written by AI/)).toBeTruthy();
  });
});
