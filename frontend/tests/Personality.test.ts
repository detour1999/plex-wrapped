// ABOUTME: Tests that the Personality slide displays every field of the AI-generated
// ABOUTME: personality object (type, tagline, description, spirit animal).

import { describe, expect, it } from 'vitest';
import { render, screen } from '@testing-library/svelte';
import { tick } from 'svelte';
import Personality from '../src/components/slides/Personality.svelte';

describe('Personality slide', () => {
  it('displays the personality type, tagline, description, and spirit animal', async () => {
    const personality = {
      type: 'The Nostalgic Wanderer',
      tagline: 'Always chasing yesterday\'s hits',
      description: 'You gravitate toward songs that remind you of simpler times.',
      spirit_animal: 'A vinyl record',
    };

    render(Personality, { personality, visible: true });
    await tick();

    expect(screen.getByText('The Nostalgic Wanderer')).toBeTruthy();
    expect(screen.getByText(/Always chasing yesterday's hits/)).toBeTruthy();
    expect(screen.getByText('You gravitate toward songs that remind you of simpler times.')).toBeTruthy();
    expect(screen.getByText('A vinyl record')).toBeTruthy();
  });
});
