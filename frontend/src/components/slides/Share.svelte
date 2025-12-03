<!-- ABOUTME: Final slide with sharing options and call to action. -->
<!-- ABOUTME: Provides social media share buttons and export options. -->

<script lang="ts">
  import { fly } from 'svelte/transition';
  import SlideContainer from '../common/SlideContainer.svelte';

  export let visible = true;
  export let year: number;

  function shareToTwitter() {
    const text = encodeURIComponent(`Check out my Last.fm Wrapped ${year}! #LastWrapped`);
    const url = encodeURIComponent(window.location.href);
    window.open(`https://twitter.com/intent/tweet?text=${text}&url=${url}`, '_blank');
  }

  function copyLink() {
    navigator.clipboard.writeText(window.location.href);
    alert('Link copied to clipboard!');
  }

  function downloadImage() {
    // Placeholder for future screenshot/export functionality
    alert('Screenshot feature coming soon!');
  }
</script>

<SlideContainer {visible}>
  <div class="max-w-2xl mx-auto">
    <div class="mb-12" in:fly={{ y: -30, duration: 600, delay: 200 }}>
      <h2 class="text-5xl font-black mb-4">That's Your</h2>
      <h2 class="text-6xl font-black text-wrapped-accent mb-4">Last Wrapped {year}</h2>
      <p class="text-wrapped-muted text-xl">Thanks for listening</p>
    </div>

    <div class="space-y-4 mb-12" in:fly={{ y: 30, duration: 600, delay: 400 }}>
      <button
        on:click={shareToTwitter}
        class="w-full bg-[#1DA1F2] hover:bg-[#1a8cd8] text-white font-bold py-4 px-8 rounded-lg transition-all transform hover:scale-105 shadow-lg"
      >
        <span class="flex items-center justify-center gap-3">
          <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
            <path
              d="M23 3a10.9 10.9 0 01-3.14 1.53 4.48 4.48 0 00-7.86 3v1A10.66 10.66 0 013 4s-4 9 5 13a11.64 11.64 0 01-7 2c9 5 20 0 20-11.5a4.5 4.5 0 00-.08-.83A7.72 7.72 0 0023 3z"
            />
          </svg>
          Share on Twitter
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
      <p class="mb-2">Made with Last.fm data</p>
      <p>
        <a
          href="https://github.com/yourusername/last-wrapped"
          target="_blank"
          class="text-wrapped-accent hover:underline"
        >
          View on GitHub
        </a>
      </p>
    </div>
  </div>
</SlideContainer>
