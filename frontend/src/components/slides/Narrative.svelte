<!-- ABOUTME: Displays AI-generated narrative story about listening year. -->
<!-- ABOUTME: Uses typewriter effect for dramatic text reveal. -->

<script lang="ts">
  import { onMount } from 'svelte';
  import { fly } from 'svelte/transition';
  import SlideContainer from '../common/SlideContainer.svelte';

  export let narrative: string;
  export let visible = true;

  let displayedText = '';
  let currentIndex = 0;
  let mounted = false;

  onMount(() => {
    mounted = true;
  });

  $: if (visible && mounted && narrative) {
    displayedText = '';
    currentIndex = 0;

    const interval = setInterval(() => {
      if (currentIndex < narrative.length) {
        displayedText += narrative[currentIndex];
        currentIndex++;
      } else {
        clearInterval(interval);
      }
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
      <div class="text-xl leading-relaxed space-y-4">
        {#each displayedText.split('\n\n') as paragraph}
          <p class="text-left">
            {paragraph}
          </p>
        {/each}
        {#if currentIndex < narrative.length}
          <span class="inline-block w-2 h-5 bg-wrapped-accent animate-pulse ml-1" />
        {/if}
      </div>
    </div>

    {#if currentIndex >= narrative.length}
      <div
        class="mt-8 text-wrapped-muted text-sm italic"
        in:fly={{ y: 20, duration: 400, delay: 300 }}
      >
        <p>- Written by AI, inspired by your listening</p>
      </div>
    {/if}
  </div>
</SlideContainer>
