<!-- ABOUTME: Final slide with sharing options and call to action. -->
<!-- ABOUTME: Provides social media share buttons and export options. -->

<script lang="ts">
  import { fly } from 'svelte/transition';
  import SlideContainer from '../common/SlideContainer.svelte';
  import SummaryCard from '../common/SummaryCard.svelte';

  export let visible = true;
  export let userName: string;
  export let year: number;
  export let totalMinutes: number = 0;
  export let topArtist: { name: string; plays: number } | null = null;
  export let personalityType: string = '';
  export let auraColor: string = '#1DB954';
  export let auraVibe: string = '';

  let captionCopied = false;

  $: hours = Math.round(totalMinutes / 60);
  $: shareCaption = generateCaption();

  function generateCaption(): string {
    const lines = [`My ${year} Music Wrapped:`];
    if (hours > 0) lines.push(`${hours.toLocaleString()} hours of music`);
    if (topArtist) lines.push(`Top artist: ${topArtist.name}`);
    if (personalityType) lines.push(`Listening personality: ${personalityType}`);
    if (auraVibe) lines.push(`Musical aura: ${auraVibe}`);
    lines.push('');
    lines.push('#MusicWrapped #PlexWrapped');
    return lines.join('\n');
  }

  function shareToBluesky() {
    const text = encodeURIComponent(shareCaption);
    const url = encodeURIComponent(window.location.href);
    window.open(`https://bsky.app/intent/compose?text=${text}%0A%0A${url}`, '_blank');
  }

  function shareToInstagram() {
    navigator.clipboard.writeText(`${shareCaption}\n\n${window.location.href}`);
    alert('Caption and link copied! Open Instagram and paste in your story or caption.');
  }

  function copyCaption() {
    navigator.clipboard.writeText(`${shareCaption}\n\n${window.location.href}`);
    captionCopied = true;
    setTimeout(() => captionCopied = false, 2000);
  }

  function copyLink() {
    navigator.clipboard.writeText(window.location.href);
    alert('Link copied to clipboard!');
  }

  async function downloadImage() {
    const { default: html2canvas } = await import('html2canvas');
    const card = document.querySelector('.summary-card');
    if (!card) {
      alert('Could not capture image');
      return;
    }

    const canvas = await html2canvas(card as HTMLElement, {
      backgroundColor: null,
      scale: 2,
    });

    const link = document.createElement('a');
    link.download = `music-wrapped-${year}.png`;
    link.href = canvas.toDataURL('image/png');
    link.click();
  }
</script>

<!-- Hidden summary card for download -->
<div class="fixed -left-[9999px] top-0">
  <SummaryCard
    {userName}
    {year}
    {totalMinutes}
    {topArtist}
    {personalityType}
    {auraColor}
    {auraVibe}
  />
</div>

<SlideContainer {visible}>
  <div class="max-w-2xl mx-auto">
    <div class="mb-12" in:fly={{ y: -30, duration: 600, delay: 200 }}>
      <h2 class="text-5xl font-black mb-4">That's Your</h2>
      <h2 class="text-6xl font-black text-wrapped-accent mb-4">Music Wrapped {year}</h2>
      <p class="text-wrapped-muted text-xl">Thanks for listening</p>
    </div>

    <!-- Caption Preview -->
    <div class="mb-8 bg-wrapped-secondary/20 rounded-xl p-4 backdrop-blur" in:fly={{ y: 20, duration: 500, delay: 300 }}>
      <p class="text-wrapped-muted text-xs uppercase tracking-wider mb-2">Share Caption</p>
      <pre class="text-sm text-left whitespace-pre-wrap font-sans">{shareCaption}</pre>
      <button
        on:click={copyCaption}
        class="mt-3 text-sm text-wrapped-accent hover:underline"
      >
        {captionCopied ? 'Copied!' : 'Copy caption'}
      </button>
    </div>

    <div class="space-y-4 mb-12" in:fly={{ y: 30, duration: 600, delay: 400 }}>
      <button
        on:click={shareToBluesky}
        class="w-full bg-[#0085ff] hover:bg-[#0073e6] text-white font-bold py-4 px-8 rounded-lg transition-all transform hover:scale-105 shadow-lg"
      >
        <span class="flex items-center justify-center gap-3">
          <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 600 530">
            <path d="m135.72 44.03c66.496 49.921 138.02 151.14 164.28 205.46 26.262-54.316 97.782-155.54 164.28-205.46 47.98-36.021 125.72-63.892 125.72 24.795 0 17.712-10.155 148.79-16.111 170.07-20.703 73.984-96.144 92.854-163.25 81.433 117.3 19.964 147.14 86.092 82.697 152.22-122.39 125.59-175.91-31.511-189.63-71.766-2.514-7.3797-3.6904-10.832-3.7077-7.8964-0.0174-2.9357-1.1937 0.51669-3.7077 7.8964-13.714 40.255-67.233 197.36-189.63 71.766-64.444-66.128-34.605-132.26 82.697-152.22-67.108 11.421-142.55-7.4491-163.25-81.433-5.9562-21.282-16.111-152.36-16.111-170.07 0-88.687 77.742-60.816 125.72-24.795z"/>
          </svg>
          Share on Bluesky
        </span>
      </button>

      <button
        on:click={shareToInstagram}
        class="w-full bg-gradient-to-r from-[#833ab4] via-[#fd1d1d] to-[#fcb045] hover:opacity-90 text-white font-bold py-4 px-8 rounded-lg transition-all transform hover:scale-105 shadow-lg"
      >
        <span class="flex items-center justify-center gap-3">
          <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
            <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z"/>
          </svg>
          Share on Instagram
        </span>
      </button>

      <button
        on:click={copyLink}
        class="w-full bg-wrapped-secondary/20 hover:bg-wrapped-secondary/30 backdrop-blur text-white font-bold py-4 px-8 rounded-lg transition-all transform hover:scale-105 border-2 border-wrapped-accent/30"
      >
        <span class="flex items-center justify-center gap-3">
          <svg
            class="w-6 h-6"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            stroke-width="2"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"
            />
          </svg>
          Copy Link
        </span>
      </button>

      <button
        on:click={downloadImage}
        class="w-full bg-wrapped-secondary/20 hover:bg-wrapped-secondary/30 backdrop-blur text-white font-bold py-4 px-8 rounded-lg transition-all transform hover:scale-105 border-2 border-wrapped-accent/30"
      >
        <span class="flex items-center justify-center gap-3">
          <svg
            class="w-6 h-6"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            stroke-width="2"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
            />
          </svg>
          Download Image
        </span>
      </button>
    </div>

    <div class="text-wrapped-muted text-sm" in:fly={{ y: 20, duration: 400, delay: 800 }}>
      <p>Made with your Plex listening data</p>
    </div>
  </div>
</SlideContainer>
