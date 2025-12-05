// ABOUTME: Visualization registry and exports.
// ABOUTME: Central hub for all visualization renderers and metadata.

export * from './types';
export * from './base';

import { GradientBlobRenderer, metadata as gradientBlobMeta } from './gradient_blob';
import { ParticlesRenderer, metadata as particlesMeta } from './particles';
import { AuroraRenderer, metadata as auroraMeta } from './aurora';
import type { VisualizationRenderer, VisualizationMetadata } from './types';

export const visualizations: Record<string, VisualizationRenderer> = {
  gradient_blob: GradientBlobRenderer,
  particles: ParticlesRenderer,
  aurora: AuroraRenderer,
};

export const visualizationMetadata: VisualizationMetadata[] = [
  gradientBlobMeta,
  particlesMeta,
  auroraMeta,
];

export type VisualizationType = keyof typeof visualizations;

export function getRenderer(type: string): VisualizationRenderer | null {
  return visualizations[type] || null;
}
