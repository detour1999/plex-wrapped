// ABOUTME: Test setup that gives jsdom the Web Animations API used by Svelte transitions.
// ABOUTME: Transitions finish immediately, and matchMedia is stubbed, which is what these tests need.

if (!window.matchMedia) {
  window.matchMedia = function (query: string) {
    return {
      matches: false,
      media: query,
      onchange: null,
      addListener() {},
      removeListener() {},
      addEventListener() {},
      removeEventListener() {},
      dispatchEvent() {
        return false;
      },
    } as unknown as MediaQueryList;
  };
}

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
