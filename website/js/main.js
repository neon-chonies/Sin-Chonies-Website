/* ============================================
   SIN CHONIES — Interactive JavaScript
   ============================================ */

document.addEventListener('DOMContentLoaded', () => {

  // ----- Particle Effect -----
  const particlesEl = document.getElementById('particles');
  if (particlesEl) {
    const canvas = document.createElement('canvas');
    particlesEl.appendChild(canvas);
    const ctx = canvas.getContext('2d');
    let w, h, particles = [];

    function resize() {
      w = canvas.width = particlesEl.offsetWidth;
      h = canvas.height = particlesEl.offsetHeight;
    }

    class Particle {
      constructor() {
        this.reset();
        this.y = Math.random() * h;
      }
      reset() {
        this.x = Math.random() * w;
        this.y = -10;
        this.size = Math.random() * 2 + 0.5;
        this.speed = Math.random() * 0.8 + 0.2;
        this.opacity = Math.random() * 0.5 + 0.1;
        this.hue = Math.random() > 0.5 ? '230,57,70' : '255,184,0';
      }
      update() {
        this.y += this.speed;
        if (this.y > h + 10) this.reset();
      }
      draw() {
        ctx.fillStyle = `rgba(${this.hue},${this.opacity})`;
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
        ctx.fill();
      }
    }

    function initParticles(count) {
      resize();
      particles = Array.from({ length: count }, () => new Particle());
    }

    function animate() {
      ctx.clearRect(0, 0, w, h);
      particles.forEach(p => { p.update(); p.draw(); });
      requestAnimationFrame(animate);
    }

    window.addEventListener('resize', resize);
    initParticles(80);
    animate();
  }

  // ----- Navigation Toggle -----
  const navToggle = document.getElementById('navToggle');
  const nav = document.getElementById('nav');
  if (navToggle && nav) {
    navToggle.addEventListener('click', () => {
      nav.classList.toggle('nav--open');
    });
  }

  // ----- Past Shows Toggle -----
  const pastBtn = document.getElementById('pastShowsBtn');
  const pastShows = document.getElementById('pastShows');
  if (pastBtn && pastShows) {
    pastBtn.addEventListener('click', () => {
      const isHidden = pastShows.style.display === 'none';
      pastShows.style.display = isHidden ? 'flex' : 'none';
      pastBtn.textContent = isHidden ? 'HIDE PAST SHOWS ↑' : 'VIEW PAST SHOWS ↓';
    });
  }

  // ----- Scroll Effects: Nav Highlight -----
  const sections = document.querySelectorAll('section[id]');
  const navLinks = document.querySelectorAll('.nav__link');

  function highlightNav() {
    let scrollY = window.scrollY + 100;
    sections.forEach(section => {
      const top = section.offsetTop;
      const height = section.offsetHeight;
      const id = section.getAttribute('id');
      if (scrollY >= top && scrollY < top + height) {
        navLinks.forEach(link => {
          link.classList.toggle('nav__link--active', link.getAttribute('href') === '#' + id);
        });
      }
    });
  }

  window.addEventListener('scroll', highlightNav);

  // ----- Scroll Reveal Animation -----
  const revealEls = document.querySelectorAll('.show-card, .merch-card, .gallery__item');

  const revealObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.style.opacity = '1';
        entry.target.style.transform = 'translateY(0)';
      }
    });
  }, { threshold: 0.1 });

  revealEls.forEach(el => {
    el.style.opacity = '0';
    el.style.transform = 'translateY(30px)';
    el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
    revealObserver.observe(el);
  });

  // ----- Contact Form -----
  const form = document.getElementById('contactForm');
  if (form) {
    form.addEventListener('submit', (e) => {
      e.preventDefault();
      const btn = form.querySelector('button[type="submit"]');
      const originalText = btn.textContent;
      btn.textContent = 'MESSAGE SENT!';
      btn.style.background = '#ffb800';
      btn.style.color = '#050508';
      setTimeout(() => {
        btn.textContent = originalText;
        btn.style.background = '';
        btn.style.color = '';
        form.reset();
      }, 2500);
    });
  }

  // ----- Smooth scroll for nav links (fallback) -----
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
      const target = document.querySelector(this.getAttribute('href'));
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth' });
        // Close mobile nav if open
        if (nav) nav.classList.remove('nav--open');
      }
    });
  });

});
