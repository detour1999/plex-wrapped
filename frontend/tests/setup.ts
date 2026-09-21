// ABOUTME: Test setup that gives jsdom the Web Animations API used by Svelte transitions.
// ABOUTME: Transitions finish immediately, which is what these tests need.

if (!Element.prototype.animate) {
  Element.prototype.animate = function () {
    const animation = {
      finished: Promise.resolve(),
      onfinish: null as null | (() => void),
      cancel() {},
      finish() {},
      play() {},
      pause() {},
      currentTime: 0,
    };
    queueMicrotask(() => animation.onfinish?.());
    return animation as unknown as Animation;
  };
}
