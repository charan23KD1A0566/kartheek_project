import { useEffect, useRef } from 'react';

export default function VisualEffects() {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');

    let width = window.innerWidth;
    let height = window.innerHeight;

    const mouse = {
      x: width / 2,
      y: height / 2,
      targetX: width / 2,
      targetY: height / 2,
    };

    const particles = [];
    const sparks = [];
    const trails = [];

    const resize = () => {
      width = window.innerWidth;
      height = window.innerHeight;

      canvas.width = width * window.devicePixelRatio;
      canvas.height = height * window.devicePixelRatio;

      canvas.style.width = `${width}px`;
      canvas.style.height = `${height}px`;

      ctx.setTransform(
        window.devicePixelRatio,
        0,
        0,
        window.devicePixelRatio,
        0,
        0
      );
    };

    resize();

    window.addEventListener('resize', resize);

    const handleMouseMove = (event) => {
      mouse.targetX = event.clientX;
      mouse.targetY = event.clientY;

      trails.push({
        x: event.clientX,
        y: event.clientY,
        life: 1,
        size: Math.random() * 3 + 1,
      });

      if (trails.length > 80) {
        trails.shift();
      }
    };

    const createBurst = (x, y) => {
      const count = 45;

      for (let i = 0; i < count; i++) {
        const angle = Math.random() * Math.PI * 2;
        const speed = Math.random() * 6 + 2;

        particles.push({
          x,
          y,
          vx: Math.cos(angle) * speed,
          vy: Math.sin(angle) * speed,
          life: 1,
          size: Math.random() * 4 + 1,
          gravity: 0.08,
        });
      }
    };

    const handleClick = (event) => {
      createBurst(event.clientX, event.clientY);
    };

    window.addEventListener('mousemove', handleMouseMove);
    window.addEventListener('click', handleClick);

    const animate = () => {
      ctx.clearRect(0, 0, width, height);

      mouse.x += (mouse.targetX - mouse.x) * 0.12;
      mouse.y += (mouse.targetY - mouse.y) * 0.12;

      /*
       * Cursor glow
       */
      const gradient = ctx.createRadialGradient(
        mouse.x,
        mouse.y,
        0,
        mouse.x,
        mouse.y,
        110
      );

      gradient.addColorStop(
        0,
        'rgba(59,130,246,0.16)'
      );

      gradient.addColorStop(
        0.4,
        'rgba(59,130,246,0.07)'
      );

      gradient.addColorStop(
        1,
        'rgba(59,130,246,0)'
      );

      ctx.fillStyle = gradient;

      ctx.beginPath();
      ctx.arc(mouse.x, mouse.y, 110, 0, Math.PI * 2);
      ctx.fill();

      /*
       * Cursor trail
       */
      for (let i = trails.length - 1; i >= 0; i--) {
        const trail = trails[i];

        trail.life -= 0.035;

        if (trail.life <= 0) {
          trails.splice(i, 1);
          continue;
        }

        ctx.beginPath();

        ctx.arc(
          trail.x,
          trail.y,
          trail.size * trail.life,
          0,
          Math.PI * 2
        );

        ctx.fillStyle = `rgba(59,130,246,${trail.life * 0.22})`;

        ctx.fill();
      }

      /*
       * Click particles
       */
      for (let i = particles.length - 1; i >= 0; i--) {
        const particle = particles[i];

        particle.x += particle.vx;
        particle.y += particle.vy;

        particle.vy += particle.gravity;

        particle.vx *= 0.985;
        particle.vy *= 0.985;

        particle.life -= 0.018;

        if (particle.life <= 0) {
          particles.splice(i, 1);
          continue;
        }

        ctx.beginPath();

        ctx.arc(
          particle.x,
          particle.y,
          particle.size * particle.life,
          0,
          Math.PI * 2
        );

        ctx.fillStyle = `rgba(37,99,235,${particle.life})`;

        ctx.fill();
      }

      requestAnimationFrame(animate);
    };

    const animationFrame = requestAnimationFrame(animate);

    return () => {
      cancelAnimationFrame(animationFrame);

      window.removeEventListener(
        'resize',
        resize
      );

      window.removeEventListener(
        'mousemove',
        handleMouseMove
      );

      window.removeEventListener(
        'click',
        handleClick
      );
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      className="visual-effects-canvas"
      aria-hidden="true"
    />
  );
}