<!-- ABOUTME: Countdown-style reveal of top 5 tracks with dramatic animations. -->
<!-- ABOUTME: Shows tracks one by one with play counts and album art. -->

<script lang="ts">
  import { fly, scale } from 'svelte/transition';
  import SlideContainer from '../common/SlideContainer.svelte';
  import AnimatedNumber from '../common/AnimatedNumber.svelte';

  export let tracks: Array<{
    name: string;
    artist: string;
    plays: number;
    album_art?: string;
  }>;
  export let visible = true;

  let revealed = 0;
  $: if (visible && revealed < tracks.length) {
    const timer = setInterval(() => {
      revealed++;
      if (revealed >= tracks.length) clearInterval(timer);
    }, 800);
  }
</script>

<SlideContainer {visible}>
  <h2 class="text-4xl font-black mb-12 text-wrapped-accent">Your Top 5 Tracks</h2>

  <div class="space-y-6 max-w-2xl w-full">
    {#each tracks.slice(0, revealed) as track, i (track.name + track.artist)}
      <div
        class="flex items-center gap-4 bg-wrapped-secondary/20 rounded-lg p-4 backdrop-blur"
        in:fly={{ x: -50, duration: 500 }}
      >
        <div class="text-4xl font-black text-wrapped-accent w-12 text-center">
          #{i + 1}
        </div>

        {#if track.album_art}
          <img
            src={track.album_art}
            alt={track.name}
            class="w-16 h-16 rounded shadow-lg object-cover"
            in:scale={{ duration: 400, delay: 200 }}
          />
        {/if}

        <div class="flex-1 text-left">
          <div class="font-bold text-lg">{track.name}</div>
          <div class="text-wrapped-muted text-sm">{track.artist}</div>
        </div>

        <div class="text-right">
          <div class="text-2xl font-bold text-wrapped-accent">
            <AnimatedNumber value={track.plays} />
          </div>
          <div class="text-wrapped-muted text-sm">plays</div>
        </div>
      </div>
    {/each}
  </div>
</SlideContainer>
