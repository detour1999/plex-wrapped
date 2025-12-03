<!-- ABOUTME: Radial visualization showing listening patterns by hour of day. -->
<!-- ABOUTME: Creates a clock-like chart with activity levels per hour. -->

<script lang="ts">
  import { onMount } from 'svelte';
  import { fade } from 'svelte/transition';
  import SlideContainer from '../common/SlideContainer.svelte';

  export let hourly_data: Array<{ hour: number; plays: number }>;
  export let visible = true;

  let maxPlays = 0;
  let mounted = false;

  $: if (hourly_data) {
    maxPlays = Math.max(...hourly_data.map((d) => d.plays));
  }

  onMount(() => {
    mounted = true;
  });

  function getBarHeight(plays: number): number {
    return maxPlays > 0 ? (plays / maxPlays) * 100 : 0;
  }

  function getHourLabel(hour: number): string {
    if (hour === 0) return '12am';
    if (hour === 12) return '12pm';
    if (hour > 12) return `${hour - 12}pm`;
    return `${hour}am`;
  }
</script>

<SlideContainer {visible}>
  <h2 class="text-4xl font-black mb-8 text-wrapped-accent">Your Listening Clock</h2>
  <p class="text-wrapped-muted text-lg mb-12">When you pressed play</p>

  <div class="relative w-96 h-96 mx-auto">
    <svg viewBox="0 0 400 400" class="w-full h-full">
      <!-- Clock face circle -->
      <circle
        cx="200"
        cy="200"
        r="180"
        fill="none"
        stroke="currentColor"
        stroke-width="1"
        class="text-wrapped-muted opacity-20"
      />

      <!-- Hour bars -->
      {#each hourly_data as { hour, plays }, i}
        {@const angle = (hour * 15 - 90) * (Math.PI / 180)}
        {@const barLength = 60 + getBarHeight(plays) * 0.8}
        {@const startX = 200 + Math.cos(angle) * 100}
        {@const startY = 200 + Math.sin(angle) * 100}
        {@const endX = 200 + Math.cos(angle) * (100 + barLength)}
        {@const endY = 200 + Math.sin(angle) * (100 + barLength)}

        {#if mounted && visible}
          <line
            x1={startX}
            y1={startY}
            x2={endX}
            y2={endY}
            stroke="currentColor"
            stroke-width="6"
            stroke-linecap="round"
            class="text-wrapped-accent transition-all duration-500"
            style="opacity: {0.3 + (plays / maxPlays) * 0.7}"
            in:fade={{ duration: 400, delay: i * 50 }}
          />
        {/if}

        <!-- Hour labels for key hours -->
        {#if hour % 6 === 0}
          {@const labelX = 200 + Math.cos(angle) * 220}
          {@const labelY = 200 + Math.sin(angle) * 220}
          <text
            x={labelX}
            y={labelY}
            text-anchor="middle"
            dominant-baseline="middle"
            class="text-sm fill-current text-wrapped-muted"
          >
            {getHourLabel(hour)}
          </text>
        {/if}
      {/each}
    </svg>
  </div>

  <p class="text-wrapped-muted text-sm mt-8">
    Most active:
    <span class="text-wrapped-accent font-bold">
      {getHourLabel(
        hourly_data.reduce((max, d) => (d.plays > max.plays ? d : max), hourly_data[0]).hour
      )}
    </span>
  </p>
</SlideContainer>
