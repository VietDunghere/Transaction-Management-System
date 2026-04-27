import { useMemo } from 'react';

const COLORS = ['#00b8a9', '#f8f3d4', '#f6416c', '#ffde7d'];
const PARTICLE_COUNT = 60;

function randomRange(min: number, max: number): number {
    return Math.random() * (max - min) + min;
}

function randomStep(min: number, max: number, step: number): number {
    const steps = Math.round((max - min) / step);
    return min + Math.round(Math.random() * steps) * step;
}

function randomColor(): string {
    return COLORS[Math.floor(Math.random() * COLORS.length)];
}

function generateGradient(): string {
    const colorStopCount = Math.floor(randomRange(2, 5)); // 2, 3, or 4
    const colorStops = Array.from({ length: colorStopCount }, () => randomColor());
    const transparentStop = Math.round(randomRange(0, 50));
    return `linear-gradient(to left, ${colorStops.join(', ')}, transparent ${transparentStop}%)`;
}

interface Particle {
    duration: number;
    delay: number;
    rotateX: number;
    rotateY: number;
    rotateZ: number;
    gradient: string;
}

export function CosmicBackground() {
    const particles = useMemo<Particle[]>(() => {
        return Array.from({ length: PARTICLE_COUNT }, () => ({
            duration: randomStep(1.0, 2.0, 0.1),
            delay: -randomRange(0.1, 2.0),
            rotateX: randomRange(-180, 180),
            rotateY: randomRange(-180, 180),
            rotateZ: randomRange(-180, 180),
            gradient: generateGradient(),
        }));
    }, []);

    return (
        <div
            style={{
                position: 'absolute',
                inset: 0,
                background: '#000',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                overflow: 'hidden',
            }}
        >
            <style>{`
        @keyframes cosmic-move {
          20% { opacity: 1; }
          100% { opacity: 0; transform: var(--trans) scale(0); }
        }
      `}</style>
            <div
                style={{
                    width: '40vmin',
                    height: '40vmin',
                    perspective: '10vmin',
                    position: 'relative',
                }}
            >
                {particles.map((p, i) => (
                    <div
                        key={i}
                        style={
                            {
                                '--trans': `translateX(50%) rotateX(${p.rotateX}deg) rotateY(${p.rotateY}deg) rotateZ(${p.rotateZ}deg)`,
                                position: 'absolute',
                                top: '50%',
                                left: '50%',
                                width: '40%',
                                height: '1px',
                                marginTop: '-0.5px',
                                marginLeft: '-20%',
                                background: p.gradient,
                                transformOrigin: '0 center',
                                transformStyle: 'preserve-3d',
                                willChange: 'transform, opacity',
                                transform: 'var(--trans) scale(2)',
                                opacity: 0,
                                animation: `cosmic-move ${p.duration}s linear infinite`,
                                animationDelay: `${p.delay}s`,
                            } as React.CSSProperties
                        }
                    />
                ))}
            </div>
        </div>
    );
}
