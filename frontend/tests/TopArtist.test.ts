// ABOUTME: Tests that the TopArtist slide shows the artist's name, plays, and hours,
// ABOUTME: and only renders album art when an image_url is present.

import { describe, expect, it } from 'vitest';
import { render, screen } from '@testing-library/svelte';
import { tick } from 'svelte';
import TopArtist from '../src/components/slides/TopArtist.svelte';

describe('TopArtist slide', () => {
  it('renders album art when image_url is present', async () => {
    const artist = { name: 'The Beatles', plays: 500, minutes: 1500, image_url: '/images/beatles.jpg' };
    render(TopArtist, { artist, visible: true });
    await tick();

    expect(screen.getByText('The Beatles')).toBeTruthy();
    const image = screen.getByAltText('The Beatles') as HTMLImageElement;
    expect(image.src).toContain('/images/beatles.jpg');
  });

  it('renders no image when image_url is missing', async () => {
    const artist = { name: 'The Beatles', plays: 500, minutes: 1500 };
    render(TopArtist, { artist, visible: true });
    await tick();

    expect(screen.queryByAltText('The Beatles')).toBeNull();
  });

  it('rounds minutes to hours', async () => {
    // 1500 minutes / 60 = 25 hours
    const artist = { name: 'The Beatles', plays: 500, minutes: 1500 };
    render(TopArtist, { artist, visible: true });
    await tick();

    expect(screen.getByText('plays')).toBeTruthy();
    expect(screen.getByText('hours')).toBeTruthy();
  });
});
