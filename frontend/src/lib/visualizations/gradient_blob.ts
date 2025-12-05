// ABOUTME: Gradient blob visualization renderer.
// ABOUTME: Soft circles with gaussian blur that slowly drift and morph.

import type { Palette, SlideConfig, VisualizationRenderer, VisualizationMetadata } from './types';
import { createShader, createProgram, hexToRgb, FULLSCREEN_QUAD_VERTICES, DEFAULT_VERTEX_SHADER } from './base';

export const metadata: VisualizationMetadata = {
  id: 'gradient_blob',
  name: 'Gradient Blob',
  description: 'Soft circles with gaussian blur that slowly drift and morph like a lava lamp',
  bestFor: ['warm', 'introspective', 'calm', 'reflective'],
};

const FRAGMENT_SHADER = `
  precision mediump float;
  varying vec2 v_uv;
  uniform float u_time;
  uniform float u_intensity;
  uniform vec3 u_color1;
  uniform vec3 u_color2;
  uniform vec3 u_color3;
  uniform vec3 u_bg;

  float blob(vec2 uv, vec2 center, float radius) {
    float d = length(uv - center);
    return smoothstep(radius, radius * 0.3, d);
  }

  void main() {
    vec2 uv = v_uv;
    float t = u_time * 0.1 * u_intensity;

    vec2 c1 = vec2(0.3 + sin(t * 0.7) * 0.2, 0.4 + cos(t * 0.5) * 0.2);
    vec2 c2 = vec2(0.7 + cos(t * 0.6) * 0.2, 0.6 + sin(t * 0.8) * 0.2);
    vec2 c3 = vec2(0.5 + sin(t * 0.9) * 0.2, 0.3 + cos(t * 0.4) * 0.2);

    float b1 = blob(uv, c1, 0.4);
    float b2 = blob(uv, c2, 0.35);
    float b3 = blob(uv, c3, 0.3);

    vec3 color = u_bg;
    color = mix(color, u_color1, b1 * 0.6);
    color = mix(color, u_color2, b2 * 0.5);
    color = mix(color, u_color3, b3 * 0.4);

    gl_FragColor = vec4(color, 1.0);
  }
`;

export const GradientBlobRenderer: VisualizationRenderer = {
  gl: null as WebGLRenderingContext | null,
  program: null as WebGLProgram | null,
  buffer: null as WebGLBuffer | null,
  startTime: 0,
  palette: null as Palette | null,
  currentIntensity: 0.5,

  init(gl: WebGLRenderingContext, palette: Palette) {
    this.gl = gl;
    this.palette = palette;
    this.startTime = performance.now();

    const vertexShader = createShader(gl, gl.VERTEX_SHADER, DEFAULT_VERTEX_SHADER);
    const fragmentShader = createShader(gl, gl.FRAGMENT_SHADER, FRAGMENT_SHADER);
    if (!vertexShader || !fragmentShader) return;

    this.program = createProgram(gl, vertexShader, fragmentShader);
    if (!this.program) return;

    this.buffer = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, this.buffer);
    gl.bufferData(gl.ARRAY_BUFFER, FULLSCREEN_QUAD_VERTICES, gl.STATIC_DRAW);
  },

  update(deltaTime: number, mood: string, intensity: number) {
    const gl = this.gl;
    const program = this.program;
    if (!gl || !program || !this.palette) return;

    this.currentIntensity = intensity;
    const time = (performance.now() - this.startTime) / 1000;

    gl.useProgram(program);

    const posLoc = gl.getAttribLocation(program, 'a_position');
    gl.bindBuffer(gl.ARRAY_BUFFER, this.buffer);
    gl.enableVertexAttribArray(posLoc);
    gl.vertexAttribPointer(posLoc, 2, gl.FLOAT, false, 0, 0);

    gl.uniform1f(gl.getUniformLocation(program, 'u_time'), time);
    gl.uniform1f(gl.getUniformLocation(program, 'u_intensity'), intensity);
    gl.uniform3fv(gl.getUniformLocation(program, 'u_color1'), hexToRgb(this.palette.primary));
    gl.uniform3fv(gl.getUniformLocation(program, 'u_color2'), hexToRgb(this.palette.secondary));
    gl.uniform3fv(gl.getUniformLocation(program, 'u_color3'), hexToRgb(this.palette.accent));
    gl.uniform3fv(gl.getUniformLocation(program, 'u_bg'), hexToRgb(this.palette.background));

    gl.drawArrays(gl.TRIANGLES, 0, 6);
  },

  transition(toConfig: SlideConfig, progress: number) {
    this.currentIntensity = toConfig.intensity;
  },

  destroy() {
    if (this.gl && this.program) {
      this.gl.deleteProgram(this.program);
    }
    if (this.gl && this.buffer) {
      this.gl.deleteBuffer(this.buffer);
    }
  },
} as VisualizationRenderer & { gl: WebGLRenderingContext | null; program: WebGLProgram | null; buffer: WebGLBuffer | null; startTime: number; palette: Palette | null; currentIntensity: number };
