<!-- ABOUTME: Displays AI-generated narrative story about listening year. -->
<!-- ABOUTME: Uses typewriter effect for dramatic text reveal. -->

<script lang="ts">
  import { onMount } from 'svelte';
  import { fly } from 'svelte/transition';
  import { writable } from 'svelte/store';
  import SlideContainer from '../common/SlideContainer.svelte';

  export let narrative: string;
  export let visible = true;

  const displayedText = writable('');
  const currentIndex = writable(0);
  let mounted = false;
  let intervalId: ReturnType<typeof setInterval> | null = null;

  onMount(() => {
    mounted = true;
    return () => {
      if (intervalId) clearInterval(intervalId);
    };
  });

  $: if (visible && mounted && narrative) {
    if (intervalId) clearInterval(intervalId);
    displayedText.set('');
    currentIndex.set(0);

    intervalId = setInterval(() => {
      currentIndex.update(idx => {
        if (idx < narrative.length) {
          displayedText.update(text => text + narrative[idx]);
          return idx + 1;
        } else {
          if (intervalId) clearInterval(intervalId);
          return idx;
        }
      });
    }, 30);
  }
</script>

<SlideContainer {visible}>
  <div class="max-w-3xl mx-auto">
    <h2 class="text-4xl font-black mb-12 text-wrapped-accent">Your Year in Music</h2>

    <div
      class="bg-wrapped-secondary/20 rounded-xl p-10 backdrop-blur"
      in:fly={{ y: 30, duration: 500, delay: 200 }}
    >
      {#if narrative}
        <div class="text-lg leading-relaxed space-y-6">
          {#each $displayedText.split('\n\n') as paragraph, i}
            <p class="text-left {i === 0 ? 'text-xl font-medium' : i % 2 === 1 ? 'text-wrapped-muted' : ''}">
              {paragraph}
            </p>
          {/each}
          {#if $currentIndex < narrative.length}
            <span class="inline-block w-2 h-5 bg-wrapped-accent animate-pulse ml-1" />
          {/if}
        </div>
      {:else}
        <p class="text-xl text-wrapped-muted italic text-center">
          Your musical story is still being written...
        </p>
      {/if}
    </div>

    {#if narrative && $currentIndex >= narrative.length}
      <div
        class="mt-8 text-wrapped-muted text-sm italic"
        in:fly={{ y: 20, duration: 400, delay: 300 }}
      >
        <p>- Written by AI, inspired by your listening</p>
      </div>
    {/if}
  </div>
</SlideContainer>
