// ABOUTME: Tests SlideContainer's visibility gate directly, including toggling from
// ABOUTME: hidden to visible after mount so the "intro" transition is actually attached.

import { describe, expect, it } from 'vitest';
import { render } from '@testing-library/svelte';
import { tick } from 'svelte';
import SlideContainer from '../src/components/common/SlideContainer.svelte';

describe('SlideContainer', () => {
  it('renders its slot content when visible', async () => {
    const { container } = render(SlideContainer, { props: { visible: true } });
    await tick();

    expect(container.querySelector('.min-h-screen')).toBeTruthy();
  });

  it('renders nothing when not visible', async () => {
    const { container } = render(SlideContainer, { props: { visible: false } });
    await tick();

    expect(container.querySelector('.min-h-screen')).toBeNull();
  });

  it('mounts the slide wrapper when toggled from hidden to visible after mount', async () => {
    const { container, rerender } = render(SlideContainer, { props: { visible: false } });
    await tick();
    expect(container.querySelector('.min-h-screen')).toBeNull();

    await rerender({ visible: true });
    await tick();

    expect(container.querySelector('.min-h-screen')).toBeTruthy();
  });

  it('removes the slide wrapper when toggled from visible to hidden after mount', async () => {
    const { container, rerender } = render(SlideContainer, { props: { visible: true } });
    await tick();
    expect(container.querySelector('.min-h-screen')).toBeTruthy();

    await rerender({ visible: false });
    await tick();

    expect(container.querySelector('.min-h-screen')).toBeNull();
  });
});
