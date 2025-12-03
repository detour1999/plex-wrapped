<!-- ABOUTME: Animated counting number component. -->
<!-- ABOUTME: Counts up from 0 to target value on mount. -->

<script lang="ts">
  import { tweened } from 'svelte/motion';
  import { cubicOut } from 'svelte/easing';
  import { onMount } from 'svelte';

  export let value: number;
  export let duration = 2000;
  export let format: (n: number) => string = (n) => Math.round(n).toLocaleString();

  const displayValue = tweened(0, {
    duration,
    easing: cubicOut,
  });

  onMount(() => {
    displayValue.set(value);
  });
</script>

<span class="tabular-nums">{format($displayValue)}</span>
