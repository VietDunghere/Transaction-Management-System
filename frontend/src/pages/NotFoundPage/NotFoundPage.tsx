import { useNavigate } from '@tanstack/react-router';
import { useEffect, useRef } from 'react';
import * as THREE from 'three';
import { Button } from '~/components/ui/Button/Button';

const VERTEX = `void main(){gl_Position=vec4(position,1.);}`;

const FRAGMENT = `
uniform vec2 u_resolution;
uniform vec2 u_mouse;
uniform float u_time;
uniform sampler2D u_noise;

#define PI 3.141592653589793
#define TAU 6.

const float multiplier=15.5;
const float zoomSpeed=10.;
const int layers=10;
const int octaves=5;

vec2 hash2(vec2 p){return texture2D(u_noise,(p+.5)/256.,-100.).xy;}
float hash(vec2 p){return texture2D(u_noise,(p+.5)/256.,-100.).x;}

mat2 rotate2d(float a){return mat2(cos(a),sin(a),-sin(a),cos(a));}

vec3 hsb2rgb(vec3 c){
  vec3 rgb=clamp(abs(mod(c.x*6.+vec3(0.,4.,2.),6.)-3.)-1.,0.,1.);
  rgb=rgb*rgb*(3.-2.*rgb);
  return c.z*mix(vec3(1.),rgb,c.y);
}

float noise(vec2 uv){
  vec2 id=floor(uv);vec2 u=fract(uv);u=u*u*(3.-2.*u);
  float a=hash(id),b=hash(id+vec2(1.,0.)),c=hash(id+vec2(0.,1.)),d=hash(id+vec2(1.,1.));
  return mix(mix(a,b,u.x),mix(c,d,u.x),u.y);
}

float fbm(vec2 uv){
  float s=0.,m=0.,a=.5;
  for(int i=0;i<octaves;i++){s+=a*noise(uv);m+=a;a*=.5;uv*=2.;}
  return s/m;
}

vec3 render(vec2 uv,float scale,vec3 colour){
  vec2 id=floor(uv);vec2 subuv=fract(uv);vec2 rand=hash2(id);
  float bokeh=abs(scale);float particle=0.;
  if(length(rand)>1.3){
    float field=length(subuv-.5);
    particle=smoothstep(.3,0.,field)+smoothstep(.4*bokeh,.34*bokeh,field);
  }
  return vec3(particle*2.);
}

vec3 renderLayer(int layer,int layers,vec2 uv,inout float opacity,vec3 colour,float n){
  float scale=mod((u_time+zoomSpeed/float(layers)*float(layer))/zoomSpeed,-1.);
  uv*=20.;uv*=scale*scale;
  uv=rotate2d(u_time/10.)*uv;
  uv+=vec2(25.+sin(u_time*.1))*float(layer);
  vec3 pass=render(uv*multiplier,scale,colour)*.2;
  opacity=1.+scale;float _opacity=opacity;
  float endOpacity=smoothstep(0.,.4,scale*-1.);
  opacity+=endOpacity;
  return pass*_opacity*endOpacity;
}

void main(){
  vec2 uv=(gl_FragCoord.xy-.5*u_resolution.xy);
  if(u_resolution.y<u_resolution.x)uv/=u_resolution.y;else uv/=u_resolution.x;
  float n=fbm((uv+vec2(sin(u_time*.1),u_time*.1))*2.-2.);
  vec3 colour=n*mix(vec3(0.,.5,1.5)*-1.5,clamp(vec3(1.,.5,.25)*2.,0.,1.),n);
  float opacity=1.,opacity_sum=1.;
  for(int i=1;i<=layers;i++){colour-=renderLayer(i,layers,uv,opacity,colour,n);opacity_sum+=opacity;}
  colour/=opacity_sum;
  gl_FragColor=vec4(clamp(colour*20.,0.,1.),1.);
}`;

const NOISE_URL = 'https://s3-us-west-2.amazonaws.com/s.cdpn.io/982762/noise.png';

function useAshfall(containerRef: React.RefObject<HTMLDivElement | null>) {
    useEffect(() => {
        const el = containerRef.current;
        if (!el) return;

        let disposed = false;
        const renderer = new THREE.WebGLRenderer({ antialias: false });
        renderer.setPixelRatio(window.devicePixelRatio);
        el.appendChild(renderer.domElement);

        const camera = new THREE.Camera();
        camera.position.z = 1;
        const scene = new THREE.Scene();

        const uniforms = {
            u_time: { value: 1.0 },
            u_resolution: { value: new THREE.Vector2() },
            u_mouse: { value: new THREE.Vector2() },
            u_noise: { value: new THREE.Texture() },
        };

        const material = new THREE.ShaderMaterial({
            uniforms,
            vertexShader: VERTEX,
            fragmentShader: FRAGMENT,
        });
        (material.extensions as Record<string, boolean>).derivatives = true;
        scene.add(new THREE.Mesh(new THREE.PlaneGeometry(2, 2), material));

        const loader = new THREE.TextureLoader();
        loader.setCrossOrigin('anonymous');
        loader.load(NOISE_URL, (tex) => {
            tex.wrapS = THREE.RepeatWrapping;
            tex.wrapT = THREE.RepeatWrapping;
            tex.minFilter = THREE.LinearFilter;
            uniforms.u_noise.value = tex;
        });

        function resize() {
            const w = el!.clientWidth;
            const h = el!.clientHeight;
            renderer.setSize(w, h);
            uniforms.u_resolution.value.set(renderer.domElement.width, renderer.domElement.height);
        }
        resize();
        window.addEventListener('resize', resize);

        function onPointer(e: PointerEvent) {
            const ratio = window.innerHeight / window.innerWidth;
            uniforms.u_mouse.value.x = (e.pageX - window.innerWidth / 2) / window.innerWidth / ratio;
            uniforms.u_mouse.value.y = -((e.pageY - window.innerHeight / 2) / window.innerHeight);
        }
        document.addEventListener('pointermove', onPointer);

        let animId: number;
        function loop(delta: number) {
            if (disposed) return;
            uniforms.u_time.value = -10000 + delta * 0.0005;
            renderer.render(scene, camera);
            animId = requestAnimationFrame(loop);
        }
        animId = requestAnimationFrame(loop);

        return () => {
            disposed = true;
            cancelAnimationFrame(animId);
            window.removeEventListener('resize', resize);
            document.removeEventListener('pointermove', onPointer);
            renderer.dispose();
            material.dispose();
            el.removeChild(renderer.domElement);
        };
    }, [containerRef]);
}

export function NotFoundPage() {
    const navigate = useNavigate();
    const bgRef = useRef<HTMLDivElement>(null);
    useAshfall(bgRef);

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center overflow-hidden">
            {/* shader background */}
            <div ref={bgRef} className="absolute inset-0" />

            {/* content */}
            <div className="relative z-10 flex flex-col items-center gap-6 text-center px-6">
                <p className="text-[10rem] leading-none font-black tracking-tighter text-white">404</p>
                <div className="flex flex-col items-center gap-2 -mt-6">
                    <p className="text-2xl font-semibold text-white">Page not found</p>
                    <p className="text-sm text-white/50 max-w-sm">
                        The page you're looking for doesn't exist or has been moved.
                    </p>
                </div>
                <Button
                    variant="ghost"
                    className="border border-white/20 text-white/70 hover:bg-white/10 hover:text-white"
                    onClick={() => navigate({ to: '/' })}
                >
                    Back to Dashboard
                </Button>
            </div>

            <p className="absolute bottom-4 right-4 text-xs text-white/30">BG by Liam Egan</p>
        </div>
    );
}
