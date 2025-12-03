<!-- ABOUTME: Main Wrapped experience controller. -->
<!-- ABOUTME: Manages slide navigation and user interaction. -->

<script lang="ts">
  import Intro from './slides/Intro.svelte';
  import TotalTime from './slides/TotalTime.svelte';
  import TopArtist from './slides/TopArtist.svelte';
  import TopTracks from './slides/TopTracks.svelte';
  import ListeningClock from './slides/ListeningClock.svelte';
  import QuirkyStats from './slides/QuirkyStats.svelte';
  import Personality from './slides/Personality.svelte';
  import Aura from './slides/Aura.svelte';
  import Roasts from './slides/Roasts.svelte';
  import Narrative from './slides/Narrative.svelte';
  import Share from './slides/Share.svelte';

  export let data: {
    user: { name: string; year: number };
    stats: { total_minutes: number };
    top: {
      artists: Array<{ name: string; plays: number; minutes: number; image_url?: string }>;
      tracks: Array<{ name: string; artist: string; plays: number; image_url?: string }>;
    };
    time_patterns: {
      by_hour: number[];
      quirky: any;
    };
    ai_generated: {
      personality: any;
      aura: any;
      roasts: string[];
      narrative: string;
    };
  };

  let currentSlide = 0;

  const slides = [
    'intro',
    'totalTime',
    'topArtist',
    'topTracks',
    'listeningClock',
    'quirkyStats',
    'personality',
    'aura',
    'roasts',
    'narrative',
    'share',
  ];

  function nextSlide() {
    if (currentSlide < slides.length - 1) {
      currentSlide++;
    }
  }

  function prevSlide() {
    if (currentSlide > 0) {
      currentSlide--;
    }
  }

  function handleKeydown(event: KeyboardEvent) {
    if (event.key === 'ArrowRight' || event.key === ' ') {
      nextSlide();
    } else if (event.key === 'ArrowLeft') {
      prevSlide();
    }
  }

  $: peakHour = data.time_patterns.by_hour.indexOf(
    Math.max(...data.time_patterns.by_hour)
  );
</script>

<svelte:window on:keydown={handleKeydown} />

<div
  class="min-h-screen cursor-pointer"
  on:click={nextSlide}
  on:keypress={(e) => e.key === 'Enter' && nextSlide()}
  role="button"
  tabindex="0"
>
  <!-- Progress dots -->
  <div class="fixed top-4 left-1/2 -translate-x-1/2 flex gap-2 z-10">
    {#each slides as _, i}
      <button
        class="w-2 h-2 rounded-full transition-colors {i === currentSlide
          ? 'bg-wrapped-accent'
          : 'bg-wrapped-muted opacity-50'}"
        on:click|stopPropagation={() => (currentSlide = i)}
      />
    {/each}
  </div>

  {#if slides[currentSlide] === 'intro'}
    <Intro userName={data.user.name} year={data.user.year} visible={true} />
  {:else if slides[currentSlide] === 'totalTime'}
    <TotalTime totalMinutes={data.stats.total_minutes} visible={true} />
  {:else if slides[currentSlide] === 'topArtist'}
    <TopArtist artist={data.top.artists[0]} visible={true} />
  {:else if slides[currentSlide] === 'topTracks'}
    <TopTracks tracks={data.top.tracks} visible={true} />
  {:else if slides[currentSlide] === 'listeningClock'}
    <ListeningClock byHour={data.time_patterns.by_hour} {peakHour} visible={true} />
  {:else if slides[currentSlide] === 'quirkyStats'}
    <QuirkyStats quirky={data.time_patterns.quirky} visible={true} />
  {:else if slides[currentSlide] === 'personality'}
    <Personality personality={data.ai_generated.personality} visible={true} />
  {:else if slides[currentSlide] === 'aura'}
    <Aura aura={data.ai_generated.aura} visible={true} />
  {:else if slides[currentSlide] === 'roasts'}
    <Roasts roasts={data.ai_generated.roasts} visible={true} />
  {:else if slides[currentSlide] === 'narrative'}
    <Narrative narrative={data.ai_generated.narrative} visible={true} />
  {:else if slides[currentSlide] === 'share'}
    <Share userName={data.user.name} year={data.user.year} visible={true} />
  {/if}
</div>
