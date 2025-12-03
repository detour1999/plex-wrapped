<!-- ABOUTME: Opening slide for the Wrapped experience. -->
<!-- ABOUTME: Shows user name and year with dramatic reveal. -->

<script lang="ts">
  import SlideContainer from '../common/SlideContainer.svelte';

  export let userName: string;
  export let year: number;
  export let visible = true;
</script>

<SlideContainer {visible}>
  <p class="text-wrapped-muted text-xl mb-4">Your</p>
  <h1 class="text-7xl font-black mb-4">{year}</h1>
  <p class="text-wrapped-muted text-xl mb-8">Wrapped</p>
  <p class="text-2xl font-semibold text-wrapped-accent">{userName}</p>

  <p class="mt-16 text-wrapped-muted animate-pulse">Tap to continue</p>
</SlideContainer>
