<!-- ABOUTME: Shows AI-generated suggestions for next year's listening. -->
<!-- ABOUTME: Displays artists, genres, or experiences to try based on listening patterns. -->

<script lang="ts">
  import { fly } from 'svelte/transition';
  import SlideContainer from '../common/SlideContainer.svelte';

  export let suggestions: string[];
  export let year: number;
  export let visible = true;
</script>

<SlideContainer {visible}>
  <div class="max-w-2xl mx-auto">
    <h2 class="text-4xl font-black mb-4 text-wrapped-accent">Looking Ahead</h2>
    <p class="text-wrapped-muted text-lg mb-10">
      Based on your listening, here's what to try in {year + 1}
    </p>

    {#if suggestions && suggestions.length > 0}
      <div class="space-y-4">
        {#each suggestions as suggestion, i}
          <div
            class="bg-wrapped-secondary/20 rounded-xl p-5 backdrop-blur text-left"
            in:fly={{ y: 20, duration: 400, delay: 200 + i * 150 }}
          >
            <div class="flex items-start gap-4">
              <div class="w-10 h-10 rounded-full bg-wrapped-accent/20 flex items-center justify-center flex-shrink-0 text-xl">
                {#if i === 0}
                  🎵
                {:else if i === 1}
                  🎧
                {:else if i === 2}
                  🎸
                {:else}
                  ✨
                {/if}
              </div>
              <p class="text-lg leading-relaxed">{suggestion}</p>
            </div>
          </div>
        {/each}
      </div>
    {:else}
      <div class="bg-wrapped-secondary/20 rounded-xl p-8 backdrop-blur">
        <p class="text-wrapped-muted italic">
          Keep listening to get personalized suggestions for next year!
        </p>
      </div>
    {/if}

    <p
      class="text-wrapped-muted text-sm mt-10 italic"
      in:fly={{ y: 10, duration: 300, delay: 800 }}
    >
      Here's to another year of great music
    </p>
  </div>
</SlideContainer>
