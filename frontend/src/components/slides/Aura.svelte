<!-- ABOUTME: Displays the user's musical aura with gradient visualization. -->
<!-- ABOUTME: Shows personality vibe with animated gradient background. -->

<script lang="ts">
  import { onMount } from 'svelte';
  import { fly } from 'svelte/transition';
  import SlideContainer from '../common/SlideContainer.svelte';

  export let aura: {
    primary_color: string;
    secondary_color: string;
    vibe: string;
    description: string;
  };
  export let visible = true;

  let mounted = false;

  onMount(() => {
    mounted = true;
  });

  $: gradientStyle = `background: linear-gradient(135deg, ${aura.primary_color}, ${aura.secondary_color})`;
</script>

<SlideContainer {visible}>
  <div class="max-w-2xl mx-auto">
    <h2 class="text-4xl font-black mb-8 text-wrapped-accent">Your Musical Aura</h2>

    <div class="relative mb-12">
      <div
        class="w-64 h-64 mx-auto rounded-full shadow-2xl animate-pulse"
        style={gradientStyle}
        in:fly={{ scale: 0.5, duration: 800, delay: 200 }}
      >
        <div
          class="absolute inset-0 rounded-full"
          style="background: radial-gradient(circle, transparent 40%, rgba(0,0,0,0.3) 100%)"
        />
      </div>

      {#if mounted && visible}
        <div
          class="absolute inset-0 flex items-center justify-center"
          in:fly={{ y: 20, duration: 600, delay: 600 }}
        >
          <div class="text-6xl font-black drop-shadow-lg text-white mix-blend-overlay">
            {aura.vibe}
          </div>
        </div>
      {/if}
    </div>

    <div
      class="bg-wrapped-secondary/20 rounded-xl p-8 backdrop-blur"
      in:fly={{ y: 30, duration: 500, delay: 1000 }}
    >
      <p class="text-xl leading-relaxed">{aura.description}</p>
    </div>

    <div class="flex gap-4 justify-center mt-8">
      <div
        class="w-16 h-16 rounded-full shadow-lg"
        style="background: {aura.primary_color}"
        in:fly={{ x: -20, duration: 400, delay: 1200 }}
      />
      <div
        class="w-16 h-16 rounded-full shadow-lg"
        style="background: {aura.secondary_color}"
        in:fly={{ x: 20, duration: 400, delay: 1200 }}
      />
    </div>
  </div>
</SlideContainer>
