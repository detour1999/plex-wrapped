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

  function getTimeEmoji(hour: number): string {
    if (hour === 0) return '🌙';
    if (hour === 6) return '🌅';
    if (hour === 12) return '☀️';
    if (hour === 18) return '🌆';
    return '';
  }

  function getTimeOfDayLabel(hour: number): string {
    if (hour >= 22 || hour < 6) return 'Night Owl';
    if (hour >= 6 && hour < 12) return 'Morning Person';
    if (hour >= 12 && hour < 17) return 'Afternoon Groover';
    return 'Evening Listener';
  }
</script>

<SlideContainer {visible}>
  <h2 class="text-4xl font-black mb-8 text-wrapped-accent">Your Listening Clock</h2>
  <p class="text-wrapped-muted text-lg mb-12">When you pressed play</p>

  <div class="relative w-96 h-96 mx-auto">
    <svg viewBox="0 0 500 500" class="w-full h-full overflow-visible">
      <!-- Clock face circle -->
      <circle
        cx="250"
        cy="250"
        r="120"
        fill="none"
        stroke="currentColor"
        stroke-width="1"
        class="text-wrapped-muted opacity-20"
      />

      <!-- Hour bars -->
      {#each hourly_data as { hour, plays }, i}
        {@const angle = (hour * 15 - 90) * (Math.PI / 180)}
        {@const barLength = 30 + getBarHeight(plays) * 0.6}
        {@const startX = 250 + Math.cos(angle) * 70}
        {@const startY = 250 + Math.sin(angle) * 70}
        {@const endX = 250 + Math.cos(angle) * (70 + barLength)}
        {@const endY = 250 + Math.sin(angle) * (70 + barLength)}

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
          {@const labelX = 250 + Math.cos(angle) * 185}
          {@const labelY = 250 + Math.sin(angle) * 185}
          <text
            x={labelX}
            y={labelY}
            text-anchor="middle"
            dominant-baseline="middle"
            class="text-2xl"
          >
            {getTimeEmoji(hour)}
          </text>
        {/if}
      {/each}
    </svg>
  </div>

  {@const peakHour = hourly_data.reduce((max, d) => (d.plays > max.plays ? d : max), hourly_data[0]).hour}
  <div class="mt-8 text-center">
    <p class="text-wrapped-muted text-sm">
      Most active: <span class="text-wrapped-accent font-bold">{getHourLabel(peakHour)}</span>
    </p>
    <p class="text-lg font-semibold mt-2">
      You're a <span class="text-wrapped-accent">{getTimeOfDayLabel(peakHour)}</span>
    </p>
  </div>
</SlideContainer>
