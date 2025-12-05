<!-- ABOUTME: Summary card component for downloadable image export. -->
<!-- ABOUTME: Displays key wrapped stats in a shareable card format. -->

<script lang="ts">
  export let userName: string;
  export let year: number;
  export let totalMinutes: number;
  export let topArtist: { name: string; plays: number } | null;
  export let personalityType: string;
  export let auraColor: string;
  export let auraVibe: string;

  $: hours = Math.round(totalMinutes / 60);
</script>

<div
  class="summary-card w-[400px] h-[600px] bg-gradient-to-br from-[#1a1a2e] via-[#16213e] to-[#0f3460] p-6 flex flex-col text-white"
  style="font-family: system-ui, -apple-system, sans-serif;"
>
  <div class="text-center mb-6">
    <p class="text-lg opacity-70 mb-1">{userName}'s</p>
    <h1 class="text-4xl font-black text-[#1DB954] leading-tight">Music Wrapped</h1>
    <p class="text-xl font-bold mt-1">{year}</p>
  </div>

  <div class="flex-1 space-y-3">
    <div class="bg-white/10 rounded-xl p-4 text-center">
      <p class="text-xs opacity-70 uppercase tracking-wider mb-1">Total Time</p>
      <p class="text-4xl font-black text-[#1DB954]">{hours.toLocaleString()}</p>
      <p class="text-sm opacity-70">hours of music</p>
    </div>

    {#if topArtist}
      <div class="bg-white/10 rounded-xl p-4 text-center">
        <p class="text-xs opacity-70 uppercase tracking-wider mb-1">Top Artist</p>
        <p class="text-xl font-bold truncate">{topArtist.name}</p>
        <p class="text-sm opacity-50">{topArtist.plays.toLocaleString()} plays</p>
      </div>
    {/if}

    <div class="bg-white/10 rounded-xl p-4 text-center">
      <p class="text-xs opacity-70 uppercase tracking-wider mb-1">Listening Personality</p>
      <p class="text-base font-bold leading-snug">{personalityType}</p>
    </div>

    <div class="rounded-xl p-4 flex items-center justify-center gap-3" style="background-color: {auraColor}20;">
      <div
        class="w-10 h-10 rounded-full shadow-lg flex-shrink-0"
        style="background-color: {auraColor};"
      />
      <div class="text-center">
        <p class="text-xs opacity-70 uppercase tracking-wider">Aura</p>
        <p class="font-bold text-sm">{auraVibe}</p>
      </div>
    </div>
  </div>

  <div class="text-center mt-4 opacity-40 text-xs">
    <p>Made with Plex listening data</p>
  </div>
</div>
