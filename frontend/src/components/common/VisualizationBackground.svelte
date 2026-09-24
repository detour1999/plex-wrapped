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
    if (!canvas) return;
    gl = canvas.getContext('webgl');
    if (!gl) {
      console.error('WebGL not supported');
      return;
    }
    /* v8 ignore next -- only reached with a real WebGL context, unavailable in jsdom */
    resizeCanvas();
  }

  function resizeCanvas() {
    if (!canvas || !gl || typeof window === 'undefined') return;
    /* v8 ignore start -- only reached with a real WebGL context, unavailable in jsdom */
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    gl.viewport(0, 0, canvas.width, canvas.height);
    /* v8 ignore stop */
  }

  function switchRenderer(vizType: string) {
    if (currentRenderer) {
      /* v8 ignore next -- only reached once a prior renderer was init()'d against real WebGL */
      currentRenderer.destroy();
    }
    currentRenderer = getRenderer(vizType);
    if (currentRenderer && gl) {
      /* v8 ignore next -- only reached with a real WebGL context, unavailable in jsdom */
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

    if (gl && currentRenderer) {
      /* v8 ignore start -- only reached with a real WebGL context, unavailable in jsdom */
      gl.clearColor(0, 0, 0, 1);
      gl.clear(gl.COLOR_BUFFER_BIT);
      currentRenderer.update(deltaTime, slideConfig.mood, slideConfig.intensity);
      /* v8 ignore stop */
    }

    animationId = requestAnimationFrame(animate);
  }

  $: if (gl && currentSlide !== previousSlide) {
    /* v8 ignore next -- gl is never truthy in jsdom, which has no real WebGL context */
    transitionToSlide(currentSlide);
  }

  onMount(() => {
    initWebGL();
    switchRenderer(slideConfig.visualization);
    animationId = requestAnimationFrame(animate);
    window.addEventListener('resize', resizeCanvas);
  });

  onDestroy(() => {
    if (animationId) cancelAnimationFrame(animationId);
    if (currentRenderer) currentRenderer.destroy();
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
