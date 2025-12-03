<!-- ABOUTME: Shows total listening time with animated counter. -->
<!-- ABOUTME: Converts minutes to hours/days for impact. -->

<script lang="ts">
  import SlideContainer from '../common/SlideContainer.svelte';
  import AnimatedNumber from '../common/AnimatedNumber.svelte';

  export let totalMinutes: number;
  export let visible = true;

  $: hours = Math.round(totalMinutes / 60);
  $: days = (totalMinutes / 60 / 24).toFixed(1);
</script>

<SlideContainer {visible}>
  <p class="text-wrapped-muted text-xl mb-4">You listened for</p>

  <div class="text-8xl font-black text-wrapped-accent mb-2">
    <AnimatedNumber value={totalMinutes} />
  </div>
  <p class="text-2xl mb-8">minutes</p>

  <p class="text-wrapped-muted text-lg">
    That's <span class="text-wrapped-text font-semibold">{hours.toLocaleString()} hours</span>
  </p>
  <p class="text-wrapped-muted text-lg">
    or <span class="text-wrapped-text font-semibold">{days} days</span> of music
  </p>
</SlideContainer>
