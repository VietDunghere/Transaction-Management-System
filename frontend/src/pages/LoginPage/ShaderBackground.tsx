import { useEffect, useRef } from 'react';
import * as THREE from 'three';

const vertexShader = `void main() { gl_Position = vec4(position, 1.0); }`;

const fragmentShader = `
  uniform vec2 u_resolution;
  uniform vec2 u_mouse;
  uniform float u_time;
  uniform sampler2D u_noise;

  #define PI 3.141592653589793
  #define TAU 6.

  const float multiplier = 15.5;
  const float zoomSpeed = 10.;
  const int layers = 10;
  const int octaves = 5;

  vec2 hash2(vec2 p) {
    vec2 o = texture2D(u_noise, (p + 0.5) / 256.0, -100.0).xy;
    return o;
  }

  mat2 rotate2d(float _angle) {
    return mat2(cos(_angle), sin(_angle), -sin(_angle), cos(_angle));
  }

  vec3 hsb2rgb(in vec3 c) {
    vec3 rgb = clamp(abs(mod(c.x * 6.0 + vec3(0.0, 4.0, 2.0), 6.0) - 3.0) - 1.0, 0.0, 1.0);
    rgb = rgb * rgb * (3.0 - 2.0 * rgb);
    return c.z * mix(vec3(1.0), rgb, c.y);
  }

  float hash(vec2 p) {
    float o = texture2D(u_noise, (p + 0.5) / 256.0, -100.0).x;
    return o;
  }

  float noise(vec2 uv) {
    vec2 id = floor(uv);
    vec2 subuv = fract(uv);
    vec2 u = subuv * subuv * (3.0 - 2.0 * subuv);
    float a = hash(id);
    float b = hash(id + vec2(1.0, 0.0));
    float c = hash(id + vec2(0.0, 1.0));
    float d = hash(id + vec2(1.0, 1.0));
    return mix(mix(a, b, u.x), mix(c, d, u.x), u.y);
  }

  float fbm(in vec2 uv) {
    float s = 0.0;
    float m = 0.0;
    float a = 0.5;
    for (int i = 0; i < octaves; i++) {
      s += a * noise(uv);
      m += a;
      a *= 0.5;
      uv *= 2.0;
    }
    return s / m;
  }

  vec3 render(vec2 uv, float scale, vec3 colour) {
    vec2 id = floor(uv);
    vec2 subuv = fract(uv);
    vec2 rand = hash2(id);
    float bokeh = abs(scale) * 1.0;
    float particle = 0.0;
    if (length(rand) > 1.3) {
      vec2 pos = subuv - 0.5;
      float field = length(pos);
      particle = smoothstep(0.3, 0.0, field);
      particle += smoothstep(0.4 * bokeh, 0.34 * bokeh, field);
    }
    return vec3(particle * 2.0);
  }

  vec3 renderLayer(int layer, int layers, vec2 uv, inout float opacity, vec3 colour, float n) {
    float scale = mod((u_time + zoomSpeed / float(layers) * float(layer)) / zoomSpeed, -1.0);
    uv *= 20.0;
    uv *= scale * scale;
    uv = rotate2d(u_time / 10.0) * uv;
    uv += vec2(25.0 + sin(u_time * 0.1)) * float(layer);
    vec3 pass = render(uv * multiplier, scale, colour) * 0.2;
    opacity = 1.0 + scale;
    float _opacity = opacity;
    float endOpacity = smoothstep(0.0, 0.4, scale * -1.0);
    opacity += endOpacity;
    return pass * _opacity * endOpacity;
  }

  void main() {
    vec2 uv = (gl_FragCoord.xy - 0.5 * u_resolution.xy);
    if (u_resolution.y < u_resolution.x) {
      uv /= u_resolution.y;
    } else {
      uv /= u_resolution.x;
    }
    float n = fbm((uv + vec2(sin(u_time * 0.1), u_time * 0.1)) * 2.0 - 2.0);
    vec3 colour = n * mix(vec3(0.0, 0.5, 1.5) * -1.5, clamp(vec3(1.0, 0.5, 0.25) * 2.0, 0.0, 1.0), n);
    float opacity = 1.0;
    float opacity_sum = 1.0;
    for (int i = 1; i <= layers; i++) {
      colour -= renderLayer(i, layers, uv, opacity, colour, n);
      opacity_sum += opacity;
    }
    colour /= opacity_sum;
    gl_FragColor = vec4(clamp(colour * 20.0, 0.0, 1.0), 1.0);
  }
`;

function createNoiseTexture(): THREE.DataTexture {
    const size = 256;
    const data = new Uint8Array(size * size * 4);
    for (let i = 0; i < data.length; i++) {
        data[i] = Math.random() * 255;
    }
    const texture = new THREE.DataTexture(data, size, size, THREE.RGBAFormat);
    texture.wrapS = THREE.RepeatWrapping;
    texture.wrapT = THREE.RepeatWrapping;
    texture.minFilter = THREE.LinearFilter;
    texture.needsUpdate = true;
    return texture;
}

export function ShaderBackground() {
    const containerRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        const container = containerRef.current;
        if (!container) return;

        const camera = new THREE.Camera();
        camera.position.z = 1;

        const scene = new THREE.Scene();
        const geometry = new THREE.PlaneGeometry(2, 2);
        const noiseTexture = createNoiseTexture();

        const uniforms = {
            u_time: { value: 1.0 },
            u_resolution: { value: new THREE.Vector2() },
            u_noise: { value: noiseTexture },
            u_mouse: { value: new THREE.Vector2() },
        };

        const material = new THREE.ShaderMaterial({
            uniforms,
            vertexShader,
            fragmentShader,
        });

        const mesh = new THREE.Mesh(geometry, material);
        scene.add(mesh);

        const renderer = new THREE.WebGLRenderer({ alpha: false });
        renderer.setPixelRatio(window.devicePixelRatio);
        container.appendChild(renderer.domElement);

        const onResize = () => {
            renderer.setSize(container.clientWidth, container.clientHeight);
            uniforms.u_resolution.value.x = renderer.domElement.width;
            uniforms.u_resolution.value.y = renderer.domElement.height;
        };
        onResize();

        const onPointerMove = (e: PointerEvent) => {
            const ratio = window.innerHeight / window.innerWidth;
            uniforms.u_mouse.value.x = (e.pageX - window.innerWidth / 2) / window.innerWidth / ratio;
            uniforms.u_mouse.value.y = ((e.pageY - window.innerHeight / 2) / window.innerHeight) * -1;
        };

        window.addEventListener('resize', onResize);
        document.addEventListener('pointermove', onPointerMove);

        let frameId: number;
        const animate = (delta: number) => {
            frameId = requestAnimationFrame(animate);
            uniforms.u_time.value = -10000 + delta * 0.0005;
            renderer.render(scene, camera);
        };
        frameId = requestAnimationFrame(animate);

        return () => {
            cancelAnimationFrame(frameId);
            window.removeEventListener('resize', onResize);
            document.removeEventListener('pointermove', onPointerMove);
            renderer.dispose();
            geometry.dispose();
            material.dispose();
            noiseTexture.dispose();
            if (container.contains(renderer.domElement)) {
                container.removeChild(renderer.domElement);
            }
        };
    }, []);

    return <div ref={containerRef} className="absolute inset-0" />;
}
