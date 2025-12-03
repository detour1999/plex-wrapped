<!-- ABOUTME: Displays AI-generated roasts about listening habits. -->
<!-- ABOUTME: Reveals roasts one by one with dramatic timing. -->

<script lang="ts">
  import { fly } from 'svelte/transition';
  import SlideContainer from '../common/SlideContainer.svelte';

  export let roasts: string[];
  export let visible = true;

  let currentRoast = 0;

  $: if (visible && roasts.length > 0) {
    currentRoast = 0;
    const timer = setInterval(() => {
      currentRoast++;
      if (currentRoast >= roasts.length) clearInterval(timer);
    }, 3000);
  }
</script>

<SlideContainer {visible}>
  <div class="max-w-3xl mx-auto">
    <h2 class="text-4xl font-black mb-4 text-wrapped-accent">The Roast</h2>
    <p class="text-wrapped-muted text-lg mb-12">Your taste, roasted by AI</p>

    <div class="space-y-8">
      {#each roasts.slice(0, currentRoast + 1) as roast, i (i)}
        <div
          class="bg-wrapped-secondary/20 rounded-xl p-8 backdrop-blur border-2 border-wrapped-accent/20"
          in:fly={{ x: -50, duration: 600 }}
        >
          <div class="flex items-start gap-4">
            <div class="text-4xl">🔥</div>
            <div class="flex-1">
              <p class="text-xl leading-relaxed italic">"{roast}"</p>
            </div>
          </div>
        </div>
      {/each}
    </div>

    {#if currentRoast >= roasts.length - 1}
      <div class="mt-12 text-wrapped-muted text-sm" in:fly={{ y: 20, duration: 400, delay: 500 }}>
        <p>Just kidding - your taste is actually pretty good</p>
      </div>
    {/if}
  </div>
</SlideContainer>
