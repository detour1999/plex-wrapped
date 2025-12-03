<!-- ABOUTME: Displays quirky listening patterns and fun stats. -->
<!-- ABOUTME: Shows late night anthems, longest sessions, and unique patterns. -->

<script lang="ts">
  import { fly } from 'svelte/transition';
  import SlideContainer from '../common/SlideContainer.svelte';

  export let stats: {
    late_night_anthem?: { name: string; artist: string; count: number };
    longest_session?: { duration_minutes: number; date: string };
    most_repeated?: { name: string; artist: string; streak: number };
    genre_mood?: { morning: string; evening: string };
  };
  export let visible = true;
</script>

<SlideContainer {visible}>
  <h2 class="text-4xl font-black mb-12 text-wrapped-accent">Your Quirky Stats</h2>

  <div class="space-y-8 max-w-xl mx-auto">
    {#if stats.late_night_anthem}
      <div
        class="bg-wrapped-secondary/20 rounded-xl p-6 backdrop-blur"
        in:fly={{ y: 30, duration: 500, delay: 200 }}
      >
        <div class="text-2xl mb-2">🌙</div>
        <h3 class="text-xl font-bold mb-2">Late Night Anthem</h3>
        <p class="text-lg">
          <span class="text-wrapped-accent font-bold">{stats.late_night_anthem.name}</span>
          by {stats.late_night_anthem.artist}
        </p>
        <p class="text-wrapped-muted text-sm mt-2">
          Played {stats.late_night_anthem.count} times after midnight
        </p>
      </div>
    {/if}

    {#if stats.longest_session}
      <div
        class="bg-wrapped-secondary/20 rounded-xl p-6 backdrop-blur"
        in:fly={{ y: 30, duration: 500, delay: 400 }}
      >
        <div class="text-2xl mb-2">⏱️</div>
        <h3 class="text-xl font-bold mb-2">Marathon Session</h3>
        <p class="text-lg">
          <span class="text-wrapped-accent font-bold">
            {Math.floor(stats.longest_session.duration_minutes / 60)}h
            {stats.longest_session.duration_minutes % 60}m
          </span>
          of continuous listening
        </p>
        <p class="text-wrapped-muted text-sm mt-2">
          {new Date(stats.longest_session.date).toLocaleDateString()}
        </p>
      </div>
    {/if}

    {#if stats.most_repeated}
      <div
        class="bg-wrapped-secondary/20 rounded-xl p-6 backdrop-blur"
        in:fly={{ y: 30, duration: 500, delay: 600 }}
      >
        <div class="text-2xl mb-2">🔁</div>
        <h3 class="text-xl font-bold mb-2">Repeat Champion</h3>
        <p class="text-lg">
          <span class="text-wrapped-accent font-bold">{stats.most_repeated.name}</span>
          by {stats.most_repeated.artist}
        </p>
        <p class="text-wrapped-muted text-sm mt-2">
          Played {stats.most_repeated.streak} times in a row
        </p>
      </div>
    {/if}

    {#if stats.genre_mood}
      <div
        class="bg-wrapped-secondary/20 rounded-xl p-6 backdrop-blur"
        in:fly={{ y: 30, duration: 500, delay: 800 }}
      >
        <div class="text-2xl mb-2">🎭</div>
        <h3 class="text-xl font-bold mb-2">Mood Shifts</h3>
        <div class="flex justify-around mt-4">
          <div class="text-center">
            <p class="text-sm text-wrapped-muted mb-1">Morning</p>
            <p class="text-wrapped-accent font-bold">{stats.genre_mood.morning}</p>
          </div>
          <div class="text-center">
            <p class="text-sm text-wrapped-muted mb-1">Evening</p>
            <p class="text-wrapped-accent font-bold">{stats.genre_mood.evening}</p>
          </div>
        </div>
      </div>
    {/if}
  </div>
</SlideContainer>
