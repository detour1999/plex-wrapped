<!-- ABOUTME: Container for individual slides with transitions. -->
<!-- ABOUTME: Handles entrance animations and consistent styling. -->

<script lang="ts">
  import { fade, fly } from 'svelte/transition';

  export let visible = true;
</script>

{#if visible}
  <div
    class="min-h-screen flex flex-col items-center justify-center p-8 text-center"
    in:fly={{ y: 50, duration: 500 }}
    out:fade={{ duration: 200 }}
  >
    <slot />
  </div>
{/if}
