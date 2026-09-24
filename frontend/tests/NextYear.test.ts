// ABOUTME: Tests that the NextYear slide lists AI suggestions (or a fallback message when
// ABOUTME: there are none) and labels the "year" heading with next year, not this one.

import { describe, expect, it } from 'vitest';
import { render, screen } from '@testing-library/svelte';
import { tick } from 'svelte';
import NextYear from '../src/components/slides/NextYear.svelte';

describe('NextYear slide', () => {
  it('shows the fallback message when there are no suggestions', async () => {
    render(NextYear, { suggestions: [], year: 2025, visible: true });
    await tick();

    expect(screen.getByText(/Keep listening to get personalized suggestions/)).toBeTruthy();
  });

  it('lists every suggestion when provided', async () => {
    const suggestions = ['Try more jazz', 'Explore live albums', 'Branch into ambient', 'Revisit an old favorite'];
    render(NextYear, { suggestions, year: 2025, visible: true });
    await tick();

    for (const suggestion of suggestions) {
      expect(screen.getByText(suggestion)).toBeTruthy();
    }
  });

  it('references next year, not the current one, in the intro copy', async () => {
    render(NextYear, { suggestions: ['Try more jazz'], year: 2025, visible: true });
    await tick();

    expect(screen.getByText(/try in 2026/)).toBeTruthy();
  });

  it('renders its content when toggled from hidden to visible after mount', async () => {
    const { rerender } = render(NextYear, { suggestions: ['Try more jazz'], year: 2025, visible: false });
    await tick();
    expect(screen.queryByText('Try more jazz')).toBeNull();

    await rerender({ suggestions: ['Try more jazz'], year: 2025, visible: true });
    await tick();

    expect(screen.getByText('Try more jazz')).toBeTruthy();
  });

  it('adds a suggestion once it arrives on an already-visible slide', async () => {
    const { rerender } = render(NextYear, { suggestions: [], year: 2025, visible: true });
    await tick();
    expect(screen.queryByText('Try more jazz')).toBeNull();

    await rerender({ suggestions: ['Try more jazz'], year: 2025, visible: true });
    await tick();

    expect(screen.getByText('Try more jazz')).toBeTruthy();
  });
});
