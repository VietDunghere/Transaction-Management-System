import { useEffect, useRef } from 'react';

const circleSvg =
    '<svg viewBox="0 0 11.4 11.9" width="100%" height="100%"><path fill="#ED412D" d="M5.7,0.1C2.6,0.1,0,2.8,0,6s2.6,5.9,5.7,5.9s5.7-2.7,5.7-5.9S8.9,0.1,5.7,0.1L5.7,0.1z M5.7,8.8 C4.2,8.8,3,7.6,3,6s1.2-2.8,2.7-2.8S8.4,4.4,8.4,6S7.2,8.8,5.7,8.8L5.7,8.8z"/></svg>';

const rhombusSvg =
    '<svg viewBox="0 0 13 14" width="100%" height="100%"><path fill="#2DA94F" stroke="#2DA94F" d="M5.9,1.2L0.7,6.5C0.5,6.7,0.5,7,0.7,7.2l5.2,5.4c0.2,0.2,0.5,0.2,0.7,0l5.2-5.4 C12,7,12,6.7,11.8,6.5L6.6,1.2C6.4,0.9,6.1,0.9,5.9,1.2L5.9,1.2z M3.4,6.5L6,3.9c0.2-0.2,0.5-0.2,0.7,0l2.6,2.6 c0.2,0.2,0.2,0.5,0,0.7L6.6,9.9c-0.2,0.2-0.5,0.2-0.7,0L3.4,7.3C3.2,7.1,3.2,6.8,3.4,6.5L3.4,6.5z"/></svg>';

const pentahedronSvg =
    '<svg viewBox="0 0 561.8 559.4" width="100%" height="100%"><path fill="#3E82F7" d="M383.4,559.4h-204l-2.6-0.2c-51.3-4.4-94-37-108.8-83l-0.2-0.6L6,276.7l-0.2-0.5c-14.5-50,3.1-102.7,43.7-131.4 L212.1,23C252.4-7.9,310.7-7.9,351,23l163.5,122.5l0.4,0.3c39,30.3,56,82.6,42.2,130.3l-0.3,1.1l-61.5,198 C480.4,525.6,435.5,559.4,383.4,559.4z M185.5,439.4h195.2l61.1-196.8c0-0.5-0.3-1.6-0.7-2.1L281.5,120.9L120.9,241.2 c0,0.3,0.1,0.7,0.2,1.2l60.8,195.8C182.5,438.5,183.7,439.1,185.5,439.4z M441,240.3L441,240.3L441,240.3z"/></svg>';

const xSvg =
    '<svg viewBox="0 0 12 12" width="100%" height="100%"><path fill="#FDBD00" d="M10.3,4.3H7.7V1.7C7.7,0.8,7,0,6,0S4.3,0.8,4.3,1.7v2.5H1.7C0.8,4.3,0,5,0,6s0.8,1.7,1.7,1.7h2.5v2.5 C4.3,11.2,5,12,6,12s1.7-0.8,1.7-1.7V7.7h2.5C11.2,7.7,12,7,12,6S11.2,4.3,10.3,4.3z"/></svg>';

const shapes = [circleSvg, rhombusSvg, pentahedronSvg, xSvg];

interface Ball {
    el: HTMLDivElement;
    speed: number;
    vx: number;
    vy: number;
    radius: number;
    x: number;
    y: number;
}

function createBall(container: HTMLDivElement): Ball {
    const w = container.clientWidth;
    const h = container.clientHeight;
    const speed = 2 + Math.random() * 6;
    const vx = Math.random() * speed - Math.random() * speed;
    const vy = Math.random() * speed - Math.random() * speed;
    const radius = 10 + Math.round(Math.random() * 50);
    const x = (w - radius) / 2;
    const y = (h - radius) / 2;

    const el = document.createElement('div');
    el.innerHTML = shapes[Math.floor(Math.random() * shapes.length)];
    el.style.display = 'block';
    el.style.position = 'absolute';
    el.style.width = `${radius}px`;
    el.style.height = `${radius}px`;
    el.style.left = `${x}px`;
    el.style.top = `${y}px`;
    container.appendChild(el);

    return { el, speed, vx, vy, radius, x, y };
}

function moveBall(ball: Ball, w: number, h: number): void {
    ball.x += ball.vx;
    ball.y += ball.vy;

    if (ball.x < 0 || ball.x > w - ball.radius) ball.vx = -ball.vx;
    if (ball.y < 0 || ball.y > h - ball.radius) ball.vy = -ball.vy;

    ball.el.style.left = `${ball.x}px`;
    ball.el.style.top = `${ball.y}px`;
    ball.el.style.transform = `rotate(${ball.y}deg)`;
}

const PARTICLE_COUNT = 60;

export function GeometricBackground() {
    const containerRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        const container = containerRef.current;
        if (!container) return;

        const balls: Ball[] = [];
        for (let i = 0; i < PARTICLE_COUNT; i++) {
            balls.push(createBall(container));
        }

        let w = container.clientWidth;
        let h = container.clientHeight;

        const observer = new ResizeObserver(() => {
            w = container.clientWidth;
            h = container.clientHeight;
        });
        observer.observe(container);

        let frameId: number;
        const animate = () => {
            frameId = requestAnimationFrame(animate);
            for (let i = 0; i < balls.length; i++) {
                moveBall(balls[i], w, h);
            }
        };
        frameId = requestAnimationFrame(animate);

        return () => {
            cancelAnimationFrame(frameId);
            observer.disconnect();
            for (let i = 0; i < balls.length; i++) {
                if (container.contains(balls[i].el)) {
                    container.removeChild(balls[i].el);
                }
            }
        };
    }, []);

    return (
        <div
            ref={containerRef}
            className="absolute inset-0"
            style={{ backgroundColor: '#E4EAF1', overflow: 'hidden' }}
        />
    );
}
