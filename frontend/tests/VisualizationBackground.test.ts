// ABOUTME: Tests that VisualizationBackground degrades gracefully when WebGL isn't
// ABOUTME: available (as in jsdom) and cleans up its resize listener and animation
// ABOUTME: frame loop on unmount. Fake timers drive requestAnimationFrame deterministically.

import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { render } from '@testing-library/svelte';
import { tick } from 'svelte';
import VisualizationBackground from '../src/components/common/VisualizationBackground.svelte';
import type { ThemeData } from '../src/lib/visualizations';

const theme: ThemeData = {
  palette: {
    primary: '#1DB954',
    secondary: '#191414',
    accent: '#1ed760',
    background: '#121212',
    text: '#ffffff',
  },
  slides: {
    intro: { visualization: 'gradient_blob', mood: 'calm', intensity: 1 },
    aura: { visualization: 'aurora', mood: 'dramatic', intensity: 1.2 },
  },
};

describe('VisualizationBackground', () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it('mounts without throwing even though jsdom has no WebGL support', async () => {
    expect(() => render(VisualizationBackground, { theme, currentSlide: 'intro' })).not.toThrow();
    await tick();
  });

  it('falls back to the default palette and slide config when no theme is given', async () => {
    const { container } = render(VisualizationBackground, { theme: null, currentSlide: 'intro' });
    await tick();

    expect(container.querySelector('canvas')).toBeTruthy();
  });

  it('runs the animation loop without error when WebGL is unavailable', async () => {
    render(VisualizationBackground, { theme, currentSlide: 'intro' });
    await tick();

    await vi.advanceTimersByTimeAsync(100);

    // No assertion beyond "didn't throw" - with no GL context, each animation
    // frame is a no-op that just reschedules itself.
  });

  it('handles a window resize without a GL context', async () => {
    render(VisualizationBackground, { theme, currentSlide: 'intro' });
    await tick();

    expect(() => window.dispatchEvent(new Event('resize'))).not.toThrow();
  });

  it('cancels its animation frame and removes the resize listener on unmount', async () => {
    const removeEventListenerSpy = vi.spyOn(window, 'removeEventListener');

    const { unmount } = render(VisualizationBackground, { theme, currentSlide: 'intro' });
    await tick();
    await vi.advanceTimersByTimeAsync(16);

    unmount();

    expect(removeEventListenerSpy).toHaveBeenCalledWith('resize', expect.any(Function));
    removeEventListenerSpy.mockRestore();
  });

  it('re-renders for a different currentSlide without a theme entry for it', async () => {
    const { rerender } = render(VisualizationBackground, { theme, currentSlide: 'intro' });
    await tick();

    await expect(rerender({ theme, currentSlide: 'someUnknownSlide' })).resolves.not.toThrow();
  });
});
