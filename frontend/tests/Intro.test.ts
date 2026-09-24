// ABOUTME: Tests that the Intro slide displays the user's name and year.
// ABOUTME: Covers both the visible and hidden (SlideContainer-gated) states.

import { describe, expect, it } from 'vitest';
import { render, screen } from '@testing-library/svelte';
import { tick } from 'svelte';
import Intro from '../src/components/slides/Intro.svelte';

describe('Intro slide', () => {
  it('shows the year and user name when visible', async () => {
    render(Intro, { userName: 'Dylan', year: 2025, visible: true });
    await tick();

    expect(screen.getByText('2025')).toBeTruthy();
    expect(screen.getByText('Dylan')).toBeTruthy();
  });

  it('renders nothing when not visible', async () => {
    const { container } = render(Intro, { userName: 'Dylan', year: 2025, visible: false });
    await tick();

    expect(container.textContent?.trim()).toBe('');
  });
});
