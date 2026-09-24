// ABOUTME: Tests the visualization registry (getRenderer, metadata) and shared color math.
// ABOUTME: The GL-drawing parts of each renderer (init/update) need a real WebGL context,
// ABOUTME: which jsdom does not implement, and are excluded from coverage for that reason.

import { describe, expect, it } from 'vitest';
import { hexToRgb } from '../../src/lib/visualizations/base';
import {
  getRenderer,
  visualizations,
  visualizationMetadata,
} from '../../src/lib/visualizations';

describe('hexToRgb', () => {
  it('converts a hex color to normalized RGB', () => {
    expect(hexToRgb('#1DB954')).toEqual([0x1d / 255, 0xb9 / 255, 0x54 / 255]);
  });

  it('accepts hex without a leading #', () => {
    expect(hexToRgb('1DB954')).toEqual([0x1d / 255, 0xb9 / 255, 0x54 / 255]);
  });

  it('returns black for an invalid hex string', () => {
    expect(hexToRgb('not-a-color')).toEqual([0, 0, 0]);
  });
});

describe('getRenderer', () => {
  it('returns the gradient_blob renderer by id', () => {
    expect(getRenderer('gradient_blob')).toBe(visualizations.gradient_blob);
  });

  it('returns the particles renderer by id', () => {
    expect(getRenderer('particles')).toBe(visualizations.particles);
  });

  it('returns the aurora renderer by id', () => {
    expect(getRenderer('aurora')).toBe(visualizations.aurora);
  });

  it('returns null for an unknown visualization id', () => {
    expect(getRenderer('does-not-exist')).toBeNull();
  });
});

describe('visualizationMetadata', () => {
  it('describes every registered visualization', () => {
    const ids = visualizationMetadata.map((meta) => meta.id).sort();
    expect(ids).toEqual(['aurora', 'gradient_blob', 'particles'].sort());
  });
});

describe('renderer lifecycle guards without an active GL context', () => {
  for (const id of ['gradient_blob', 'particles', 'aurora'] as const) {
    it(`${id}: transition() and destroy() are safe to call before init()`, () => {
      const renderer = getRenderer(id);
      expect(renderer).not.toBeNull();

      expect(() => renderer!.transition({ visualization: id, mood: 'calm', intensity: 1 }, 0.5)).not.toThrow();
      expect(() => renderer!.destroy()).not.toThrow();
    });
  }
});
