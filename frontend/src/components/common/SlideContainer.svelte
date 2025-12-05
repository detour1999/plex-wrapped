<!-- ABOUTME: Container for individual slides with transitions. -->
<!-- ABOUTME: Handles entrance animations and consistent styling. -->

<script lang="ts">
  import { fade, fly } from 'svelte/transition';

  export let visible = true;
</script>

{#if visible}
  <div
    class="min-h-screen flex flex-col items-center pt-24 pb-8 px-8 text-center"
    in:fly={{ y: 30, duration: 400 }}
    out:fade={{ duration: 150 }}
  >
    <div class="bg-black/40 backdrop-blur-sm rounded-2xl p-8 w-full max-w-2xl min-h-[500px] flex flex-col justify-center">
      <slot />
    </div>
  </div>
{/if}
