<!-- ABOUTME: Reveals top artist with album art and play count. -->
<!-- ABOUTME: Dramatic reveal with image and stats. -->

<script lang="ts">
  import { fly } from 'svelte/transition';
  import SlideContainer from '../common/SlideContainer.svelte';
  import AnimatedNumber from '../common/AnimatedNumber.svelte';

  export let artist: {
    name: string;
    plays: number;
    minutes: number;
    image_url?: string;
  };
  export let visible = true;
</script>

<SlideContainer {visible}>
  <p class="text-wrapped-muted text-xl mb-8">Your top artist was</p>

  {#if artist.image_url}
    <img
      src={artist.image_url}
      alt={artist.name}
      class="w-48 h-48 rounded-lg shadow-2xl mb-6 object-cover"
      in:fly={{ y: 30, duration: 600, delay: 200 }}
    />
  {/if}

  <h2 class="text-5xl font-black mb-4">{artist.name}</h2>

  <div class="flex gap-8 text-center">
    <div>
      <div class="text-3xl font-bold text-wrapped-accent">
        <AnimatedNumber value={artist.plays} />
      </div>
      <p class="text-wrapped-muted">plays</p>
    </div>
    <div>
      <div class="text-3xl font-bold text-wrapped-accent">
        <AnimatedNumber value={Math.round(artist.minutes / 60)} />
      </div>
      <p class="text-wrapped-muted">hours</p>
    </div>
  </div>
</SlideContainer>
