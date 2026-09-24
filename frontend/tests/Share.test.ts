// ABOUTME: Tests the Share slide's caption generation and its share/copy actions.
// ABOUTME: window.open, navigator.clipboard, and window.alert are spied on because jsdom
// ABOUTME: doesn't implement them - this only intercepts the browser boundary, not our logic.

import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/svelte';
import { tick } from 'svelte';
import Share from '../src/components/slides/Share.svelte';

const baseProps = {
  visible: true,
  userName: 'Dylan',
  year: 2025,
  totalMinutes: 6000,
  topArtist: { name: 'The Beatles', plays: 321 },
  personalityType: 'The Nostalgic Wanderer',
  auraColor: '#9B59B6',
  auraVibe: 'Mysterious and moody',
};

describe('Share slide', () => {
  let writeText: ReturnType<typeof vi.fn>;
  let openSpy: ReturnType<typeof vi.spyOn>;
  let alertSpy: ReturnType<typeof vi.spyOn>;

  beforeEach(() => {
    writeText = vi.fn().mockResolvedValue(undefined);
    Object.defineProperty(navigator, 'clipboard', {
      value: { writeText },
      configurable: true,
    });
    openSpy = vi.spyOn(window, 'open').mockImplementation(() => null);
    alertSpy = vi.spyOn(window, 'alert').mockImplementation(() => {});
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
    openSpy.mockRestore();
    alertSpy.mockRestore();
  });

  it('builds a share caption from the provided stats', async () => {
    render(Share, baseProps);
    await tick();

    // 6000 minutes / 60 = 100 hours
    expect(screen.getByText(/100 hours of music/)).toBeTruthy();
    expect(screen.getByText(/Top artist: The Beatles/)).toBeTruthy();
    expect(screen.getByText(/Listening personality: The Nostalgic Wanderer/)).toBeTruthy();
    expect(screen.getByText(/Musical aura: Mysterious and moody/)).toBeTruthy();
  });

  it('omits caption lines for missing optional stats', async () => {
    render(Share, { ...baseProps, topArtist: null, personalityType: '', auraVibe: '' });
    await tick();

    expect(screen.queryByText(/Top artist:/)).toBeNull();
    expect(screen.queryByText(/Listening personality:/)).toBeNull();
    expect(screen.queryByText(/Musical aura:/)).toBeNull();
  });

  it('copies the caption to the clipboard and shows a confirmation that reverts', async () => {
    render(Share, baseProps);
    await tick();

    const button = screen.getByText('Copy caption');
    await fireEvent.click(button);
    await tick();

    expect(writeText).toHaveBeenCalledWith(expect.stringContaining('100 hours of music'));
    expect(screen.getByText('Copied!')).toBeTruthy();

    await vi.advanceTimersByTimeAsync(2000);
    await tick();

    expect(screen.getByText('Copy caption')).toBeTruthy();
  });

  it('opens a Bluesky share intent with the caption and page URL', async () => {
    render(Share, baseProps);
    await tick();

    await fireEvent.click(screen.getByText('Share on Bluesky'));

    expect(openSpy).toHaveBeenCalledTimes(1);
    const [url, target] = openSpy.mock.calls[0];
    expect(url).toContain('https://bsky.app/intent/compose?text=');
    expect(target).toBe('_blank');
  });

  it('copies the caption and link for Instagram and alerts the user', async () => {
    render(Share, baseProps);
    await tick();

    await fireEvent.click(screen.getByText('Share on Instagram'));

    expect(writeText).toHaveBeenCalledWith(expect.stringContaining('100 hours of music'));
    expect(alertSpy).toHaveBeenCalledWith(expect.stringContaining('Caption and link copied'));
  });

  it('copies just the page link and alerts the user', async () => {
    render(Share, baseProps);
    await tick();

    await fireEvent.click(screen.getByText('Copy Link'));

    expect(writeText).toHaveBeenCalledWith(window.location.href);
    expect(alertSpy).toHaveBeenCalledWith(expect.stringContaining('Link copied'));
  });
});
