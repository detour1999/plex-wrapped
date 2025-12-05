// ABOUTME: Aurora visualization renderer.
// ABOUTME: Flowing horizontal bands with wave displacement like northern lights.

import type { Palette, SlideConfig, VisualizationRenderer, VisualizationMetadata } from './types';
import { createShader, createProgram, hexToRgb, FULLSCREEN_QUAD_VERTICES, DEFAULT_VERTEX_SHADER } from './base';

export const metadata: VisualizationMetadata = {
  id: 'aurora',
  name: 'Aurora',
  description: 'Flowing ribbons of color like northern lights',
  bestFor: ['dramatic', 'mystical', 'epic', 'transformative'],
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

  void main() {
    vec2 uv = v_uv;
    float t = u_time * 0.2 * u_intensity;

    float wave1 = sin(uv.x * 3.0 + t) * 0.1 + sin(uv.x * 7.0 - t * 0.5) * 0.05;
    float wave2 = sin(uv.x * 4.0 - t * 0.7) * 0.08 + sin(uv.x * 9.0 + t * 0.3) * 0.04;
    float wave3 = sin(uv.x * 5.0 + t * 0.4) * 0.07 + sin(uv.x * 11.0 - t * 0.6) * 0.03;

    float band1 = smoothstep(0.1, 0.0, abs(uv.y - 0.7 - wave1));
    float band2 = smoothstep(0.15, 0.0, abs(uv.y - 0.5 - wave2));
    float band3 = smoothstep(0.12, 0.0, abs(uv.y - 0.3 - wave3));

    vec3 color = u_bg;
    color = mix(color, u_color1, band1 * 0.7);
    color = mix(color, u_color2, band2 * 0.6);
    color = mix(color, u_color3, band3 * 0.5);

    gl_FragColor = vec4(color, 1.0);
  }
`;

export const AuroraRenderer: VisualizationRenderer = {
  gl: null as WebGLRenderingContext | null,
  program: null as WebGLProgram | null,
  buffer: null as WebGLBuffer | null,
  startTime: 0,
  palette: null as Palette | null,

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

  transition(toConfig: SlideConfig, progress: number) {},

  destroy() {
    if (this.gl && this.program) this.gl.deleteProgram(this.program);
    if (this.gl && this.buffer) this.gl.deleteBuffer(this.buffer);
  },
} as VisualizationRenderer & { gl: WebGLRenderingContext | null; program: WebGLProgram | null; buffer: WebGLBuffer | null; startTime: number; palette: Palette | null };
