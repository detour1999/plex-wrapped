<!-- ABOUTME: Shows AI-generated listening personality type. -->
<!-- ABOUTME: Includes type, tagline, description, and spirit animal. -->

<script lang="ts">
  import { fly } from 'svelte/transition';
  import SlideContainer from '../common/SlideContainer.svelte';

  export let personality: {
    type: string;
    tagline: string;
    description: string;
    spirit_animal: string;
  };
  export let visible = true;
</script>

<SlideContainer {visible}>
  <p class="text-wrapped-muted text-xl mb-4">Your listening personality</p>

  <h2 class="text-5xl font-black text-wrapped-accent mb-4">{personality.type}</h2>

  <p class="text-2xl italic text-wrapped-muted mb-8">"{personality.tagline}"</p>

  <p class="text-lg max-w-md mb-8">{personality.description}</p>

  <div class="bg-wrapped-card rounded-lg px-6 py-4">
    <p class="text-wrapped-muted text-sm mb-1">Spirit Animal</p>
    <p class="text-lg font-semibold">{personality.spirit_animal}</p>
  </div>
</SlideContainer>
