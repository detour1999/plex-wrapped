<!-- ABOUTME: Full-screen WebGL visualization background. -->
<!-- ABOUTME: Renders animated backgrounds behind slide content. -->

<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import { getRenderer, type ThemeData, type SlideConfig, type Palette } from '../../lib/visualizations';

  export let theme: ThemeData | null = null;
  export let currentSlide: string = 'intro';

  let canvas: HTMLCanvasElement;
  let gl: WebGLRenderingContext | null = null;
  let currentRenderer: ReturnType<typeof getRenderer> = null;
  let animationId: number | null = null;
  let lastTime = 0;
  let opacity = 1;
  let previousSlide = currentSlide;
  let isTransitioning = false;

  const defaultPalette: Palette = {
    primary: '#1DB954',
    secondary: '#191414',
    accent: '#1ed760',
    background: '#121212',
    text: '#ffffff',
  };

  const defaultSlideConfig: SlideConfig = {
    visualization: 'gradient_blob',
    mood: 'calm',
    intensity: 1.0,
  };

  $: palette = theme?.palette || defaultPalette;
  $: slideConfig = theme?.slides?.[currentSlide] || defaultSlideConfig;

  function initWebGL() {
    /* v8 ignore next -- canvas is always bound by the time onMount runs */
    if (!canvas) return;
    gl = canvas.getContext('webgl');
    /* v8 ignore else -- the "gl is truthy" case needs a real WebGL context, unavailable in jsdom */
    if (!gl) {
      console.error('WebGL not supported');
      return;
    }
    /* v8 ignore next -- only reached with a real WebGL context, unavailable in jsdom */
    resizeCanvas();
  }

  function resizeCanvas() {
    /* v8 ignore next -- the true branch (no real WebGL context) is the only one
       reachable in jsdom; the false branch needs a real WebGL context */
    if (!canvas || !gl || typeof window === 'undefined') return;
    /* v8 ignore start -- only reached with a real WebGL context, unavailable in jsdom */
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    gl.viewport(0, 0, canvas.width, canvas.height);
    /* v8 ignore stop */
  }

  function switchRenderer(vizType: string) {
    /* v8 ignore next -- only reached once a prior renderer was init()'d against real WebGL */
    if (currentRenderer) {
      currentRenderer.destroy();
    }
    currentRenderer = getRenderer(vizType);
    /* v8 ignore next -- only reached with a real WebGL context, unavailable in jsdom */
    if (currentRenderer && gl) {
      currentRenderer.init(gl, palette);
    }
  }

  /* v8 ignore start -- only called from the reactive block below, which is gated on a
     real WebGL context (unavailable in jsdom) so this never runs under test */
  function transitionToSlide(newSlide: string) {
    if (isTransitioning || newSlide === previousSlide) return;

    isTransitioning = true;
    opacity = 0;

    // After fade out completes, switch renderer and fade back in
    setTimeout(() => {
      const newConfig = theme?.slides?.[newSlide] || defaultSlideConfig;
      switchRenderer(newConfig.visualization);
      previousSlide = newSlide;

      // Small delay before fading back in
      setTimeout(() => {
        opacity = 1;
        isTransitioning = false;
      }, 50);
    }, 400); // Match CSS transition duration
  }
  /* v8 ignore stop */

  function animate(time: number) {
    const deltaTime = time - lastTime;
    lastTime = time;

    /* v8 ignore next -- only reached with a real WebGL context, unavailable in jsdom */
    if (gl && currentRenderer) {
      gl.clearColor(0, 0, 0, 1);
      gl.clear(gl.COLOR_BUFFER_BIT);
      currentRenderer.update(deltaTime, slideConfig.mood, slideConfig.intensity);
    }

    animationId = requestAnimationFrame(animate);
  }

  /* v8 ignore start -- gl is never truthy in jsdom, which has no real WebGL context */
  $: if (gl && currentSlide !== previousSlide) {
    transitionToSlide(currentSlide);
  }
  /* v8 ignore stop */

  onMount(() => {
    initWebGL();
    switchRenderer(slideConfig.visualization);
    animationId = requestAnimationFrame(animate);
    window.addEventListener('resize', resizeCanvas);
  });

  onDestroy(() => {
    /* v8 ignore else -- onMount always sets animationId before a test can unmount */
    if (animationId) cancelAnimationFrame(animationId);
    /* v8 ignore else -- onMount always sets currentRenderer before a test can unmount */
    if (currentRenderer) currentRenderer.destroy();
    /* v8 ignore else -- jsdom (the only test environment here) always defines window */
    if (typeof window !== 'undefined') {
      window.removeEventListener('resize', resizeCanvas);
    }
  });
</script>

<canvas
  bind:this={canvas}
  class="fixed inset-0 w-full h-full -z-10"
  style="opacity: {opacity}; transition: opacity 400ms ease-in-out"
/>
