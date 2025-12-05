// ABOUTME: Particles visualization renderer.
// ABOUTME: Floating dots with subtle drift and twinkle effect.

import type { Palette, SlideConfig, VisualizationRenderer, VisualizationMetadata } from './types';
import { createShader, createProgram, hexToRgb, FULLSCREEN_QUAD_VERTICES, DEFAULT_VERTEX_SHADER } from './base';

export const metadata: VisualizationMetadata = {
  id: 'particles',
  name: 'Particles',
  description: 'Floating dots with subtle drift and twinkle like stars',
  bestFor: ['celebratory', 'reflective', 'dreamy', 'peaceful'],
};

const FRAGMENT_SHADER = `
  precision mediump float;
  varying vec2 v_uv;
  uniform float u_time;
  uniform float u_intensity;
  uniform vec3 u_color1;
  uniform vec3 u_color2;
  uniform vec3 u_bg;

  float random(vec2 st) {
    return fract(sin(dot(st.xy, vec2(12.9898, 78.233))) * 43758.5453123);
  }

  void main() {
    vec2 uv = v_uv;
    vec3 color = u_bg;
    float t = u_time * 0.05 * u_intensity;

    for (int i = 0; i < 50; i++) {
      float fi = float(i);
      vec2 pos = vec2(
        fract(random(vec2(fi, 0.0)) + t * (0.02 + random(vec2(fi, 1.0)) * 0.03)),
        fract(random(vec2(fi, 2.0)) + t * (0.01 + random(vec2(fi, 3.0)) * 0.02))
      );

      float size = 0.003 + random(vec2(fi, 4.0)) * 0.005;
      float d = length(uv - pos);
      float brightness = smoothstep(size, size * 0.3, d);
      brightness *= 0.5 + 0.5 * sin(t * 2.0 + fi);

      vec3 particleColor = mix(u_color1, u_color2, random(vec2(fi, 5.0)));
      color = mix(color, particleColor, brightness * 0.8);
    }

    gl_FragColor = vec4(color, 1.0);
  }
`;

export const ParticlesRenderer: VisualizationRenderer = {
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
    gl.uniform3fv(gl.getUniformLocation(program, 'u_color2'), hexToRgb(this.palette.accent));
    gl.uniform3fv(gl.getUniformLocation(program, 'u_bg'), hexToRgb(this.palette.background));

    gl.drawArrays(gl.TRIANGLES, 0, 6);
  },

  transition(toConfig: SlideConfig, progress: number) {},

  destroy() {
    if (this.gl && this.program) this.gl.deleteProgram(this.program);
    if (this.gl && this.buffer) this.gl.deleteBuffer(this.buffer);
  },
} as VisualizationRenderer & { gl: WebGLRenderingContext | null; program: WebGLProgram | null; buffer: WebGLBuffer | null; startTime: number; palette: Palette | null };
