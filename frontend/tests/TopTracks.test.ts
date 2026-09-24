// ABOUTME: Tests that the TopTracks slide reveals every track over time and shows album art.
// ABOUTME: Uses fake timers so the 800ms reveal interval runs instantly.

import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { render, screen } from '@testing-library/svelte';
import { tick } from 'svelte';
import TopTracks from '../src/components/slides/TopTracks.svelte';

const tracks = [
  { name: 'track one', artist: 'artist one', plays: 10, image_url: '/images/one.jpg' },
  { name: 'track two', artist: 'artist two', plays: 9 },
  { name: 'track three', artist: 'artist three', plays: 8 },
  { name: 'track four', artist: 'artist four', plays: 7 },
  { name: 'track five', artist: 'artist five', plays: 6 },
];

async function advance(ms: number) {
  await vi.advanceTimersByTimeAsync(ms);
  await tick();
}

const shownTracks = () => screen.queryAllByText(/track (one|two|three|four|five)/);

describe('TopTracks slide', () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it('starts with only the first track', async () => {
    render(TopTracks, { tracks, visible: true });
    await tick();

    expect(shownTracks()).toHaveLength(1);
  });

  it('reveals one more track every 800ms until all are shown', async () => {
    render(TopTracks, { tracks, visible: true });
    await tick();

    for (let expected = 2; expected <= tracks.length; expected++) {
      await advance(800);
      expect(shownTracks()).toHaveLength(expected);
    }
  });

  it('keeps every track on screen once revealed', async () => {
    render(TopTracks, { tracks, visible: true });
    await tick();

    await advance(800 * tracks.length * 2);

    expect(shownTracks()).toHaveLength(tracks.length);
  });

  it('leaves no timers running when the slide is removed', async () => {
    const { unmount } = render(TopTracks, { tracks, visible: true });
    await tick();
    await advance(800);

    unmount();

    expect(vi.getTimerCount()).toBe(0);
  });

  it('renders album art from image_url once a track is revealed', async () => {
    render(TopTracks, { tracks, visible: true });
    await tick();

    const image = screen.getByAltText('track one') as HTMLImageElement;
    expect(image.src).toContain('/images/one.jpg');
  });

  it('renders no album art image for a track without image_url', async () => {
    render(TopTracks, { tracks, visible: true });
    await tick();
    await advance(800);

    expect(screen.queryByAltText('track two')).toBeNull();
  });

  it('renders its content when toggled from hidden to visible after mount', async () => {
    const { rerender } = render(TopTracks, { tracks, visible: false });
    await tick();
    expect(shownTracks()).toHaveLength(0);

    await rerender({ tracks, visible: true });
    await tick();

    expect(shownTracks()).toHaveLength(1);
  });

  it('renders album art for a later-revealed track, not just the first one', async () => {
    const tracksWithLaterArt = [
      { name: 'track one', artist: 'artist one', plays: 10 },
      { name: 'track two', artist: 'artist two', plays: 9, image_url: '/images/two.jpg' },
    ];
    render(TopTracks, { tracks: tracksWithLaterArt, visible: true });
    await tick();
    expect(screen.queryByAltText('track two')).toBeNull();

    await advance(800);

    const image = screen.getByAltText('track two') as HTMLImageElement;
    expect(image.src).toContain('/images/two.jpg');
  });
});
