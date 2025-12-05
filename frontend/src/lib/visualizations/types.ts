// ABOUTME: Type definitions for visualization system.
// ABOUTME: Defines renderer interface and metadata structure.

export interface Palette {
  primary: string;
  secondary: string;
  accent: string;
  background: string;
  text: string;
}

export interface SlideConfig {
  visualization: string;
  mood: string;
  intensity: number;
}

export interface ThemeData {
  palette: Palette;
  slides: Record<string, SlideConfig>;
}

export interface VisualizationMetadata {
  id: string;
  name: string;
  description: string;
  bestFor: string[];
}

export interface VisualizationRenderer {
  init(gl: WebGLRenderingContext, palette: Palette): void;
  update(deltaTime: number, mood: string, intensity: number): void;
  transition(toConfig: SlideConfig, progress: number): void;
  destroy(): void;
}
