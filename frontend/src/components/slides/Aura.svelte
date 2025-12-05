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
    <h2 class="text-4xl font-black mb-4 text-wrapped-accent">Your Musical Aura</h2>

    <div
      class="w-48 h-48 mx-auto rounded-full shadow-2xl mb-6"
      style="{gradientStyle}; animation: pulse 3s ease-in-out infinite;"
      in:fly={{ scale: 0.5, duration: 800, delay: 200 }}
    />

    {#if mounted && visible}
      <h3
        class="text-5xl font-black mb-8"
        style="color: {aura.primary_color}"
        in:fly={{ y: 20, duration: 600, delay: 600 }}
      >
        {aura.vibe}
      </h3>
    {/if}

    <div
      class="bg-wrapped-secondary/20 rounded-xl p-6 backdrop-blur"
      in:fly={{ y: 30, duration: 500, delay: 1000 }}
    >
      <p class="text-lg text-left leading-relaxed">{aura.description}</p>
    </div>
  </div>
</SlideContainer>

<style>
  @keyframes pulse {
    0%, 100% { transform: scale(1); opacity: 1; }
    50% { transform: scale(1.05); opacity: 0.9; }
  }
</style>
