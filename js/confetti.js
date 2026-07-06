/* ============================================
   CONFETTI.JS — Canvas Particle System
   ============================================ */

const Confetti = (() => {
  let canvas, ctx, particles = [], animId = null;

  const COLORS = [
    '#6366f1', '#8b5cf6', '#06b6d4', '#22c55e',
    '#f59e0b', '#ec4899', '#3b82f6', '#f97316',
  ];

  const createParticle = () => ({
    x: Math.random() * canvas.width,
    y: -10,
    w: Math.random() * 8 + 4,
    h: Math.random() * 4 + 2,
    color: COLORS[Math.floor(Math.random() * COLORS.length)],
    tilt: Math.random() * 30 - 15,
    tiltVel: Math.random() * 0.3 - 0.15,
    vx: Math.random() * 4 - 2,
    vy: Math.random() * 3 + 2,
    alpha: 1,
    rot: Math.random() * 360,
    rotVel: Math.random() * 6 - 3,
  });

  const setup = () => {
    if (canvas) return;
    canvas = document.createElement('canvas');
    canvas.id = 'confetti-canvas';
    canvas.style.cssText = 'position:fixed;top:0;left:0;width:100%;height:100%;pointer-events:none;z-index:9999;';
    document.body.appendChild(canvas);
    ctx = canvas.getContext('2d');
    resize();
    window.addEventListener('resize', resize);
  };

  const resize = () => {
    if (!canvas) return;
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
  };

  const update = () => {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    for (let i = particles.length - 1; i >= 0; i--) {
      const p = particles[i];
      p.vy += 0.05; // gravity
      p.vx += Math.sin(p.tilt * 0.05) * 0.05;
      p.x += p.vx;
      p.y += p.vy;
      p.rot += p.rotVel;
      p.tilt += p.tiltVel;

      if (p.y > canvas.height * 0.7) {
        p.alpha -= 0.02;
      }

      if (p.alpha <= 0 || p.y > canvas.height) {
        particles.splice(i, 1);
        continue;
      }

      ctx.save();
      ctx.globalAlpha = p.alpha;
      ctx.translate(p.x, p.y);
      ctx.rotate((p.rot * Math.PI) / 180);
      ctx.fillStyle = p.color;
      ctx.beginPath();
      ctx.ellipse(0, 0, p.w, p.h, 0, 0, Math.PI * 2);
      ctx.fill();
      ctx.restore();
    }

    if (particles.length > 0) {
      animId = requestAnimationFrame(update);
    } else {
      stop();
    }
  };

  const stop = () => {
    if (animId) { cancelAnimationFrame(animId); animId = null; }
    if (canvas) { ctx.clearRect(0, 0, canvas.width, canvas.height); }
  };

  const fire = (count = 200) => {
    setup();
    stop();
    particles = [];
    for (let i = 0; i < count; i++) {
      setTimeout(() => {
        particles.push(createParticle());
        if (i === 0) update();
      }, i * 6);
    }
    setTimeout(stop, 5000);
  };

  return { fire, stop };
})();
