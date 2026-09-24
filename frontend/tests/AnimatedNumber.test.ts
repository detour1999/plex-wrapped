// ABOUTME: Tests that AnimatedNumber counts from 0 up to its target value on mount.
// ABOUTME: The tween runs on real timers (it's driven by requestAnimationFrame, not
// ABOUTME: setTimeout/setInterval), so tests wait for it with a short real duration.

import { describe, expect, it } from 'vitest';
import { render, screen, waitFor } from '@testing-library/svelte';
import { tick } from 'svelte';
import AnimatedNumber from '../src/components/common/AnimatedNumber.svelte';

describe('AnimatedNumber', () => {
  it('starts at 0 before the tween advances', async () => {
    render(AnimatedNumber, { value: 1234, duration: 200 });
    await tick();

    expect(screen.getByText('0')).toBeTruthy();
  });

  it('reaches the target value, formatted with thousands separators, once the tween finishes', async () => {
    render(AnimatedNumber, { value: 1234, duration: 50 });
    await tick();

    await waitFor(() => expect(screen.getByText('1,234')).toBeTruthy());
  });

  it('uses a custom format function when provided', async () => {
    render(AnimatedNumber, { value: 50, duration: 50, format: (n: number) => `${Math.round(n)}%` });
    await tick();

    await waitFor(() => expect(screen.getByText('50%')).toBeTruthy());
  });
});
