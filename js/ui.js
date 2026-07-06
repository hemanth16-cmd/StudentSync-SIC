/* ============================================
   UI.JS — DOM Helpers, Toasts, Modals
   ============================================ */

const UI = (() => {

  // ── Toast Notifications ─────────────────────
  const toastContainer = () => {
    let el = document.getElementById('toast-container');
    if (!el) {
      el = document.createElement('div');
      el.id = 'toast-container';
      el.className = 'toast-container';
      document.body.appendChild(el);
    }
    return el;
  };

  const ICONS = {
    success: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>`,
    error: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>`,
    info: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>`,
    warning: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>`,
  };

  const toast = (message, type = 'info', duration = 3000) => {
    const container = toastContainer();
    const el = document.createElement('div');
    el.className = `toast ${type}`;
    el.innerHTML = `
      <div class="toast-icon">${ICONS[type] || ICONS.info}</div>
      <span>${message}</span>
    `;
    container.appendChild(el);

    setTimeout(() => {
      el.classList.add('removing');
      setTimeout(() => el.remove(), 220);
    }, duration);

    return el;
  };

  // ── Modal ──────────────────────────────────
  let activeModal = null;

  const openModal = (html, opts = {}) => {
    closeModal();
    const backdrop = document.createElement('div');
    backdrop.className = 'modal-backdrop';
    backdrop.id = 'modal-backdrop';
    backdrop.innerHTML = `<div class="modal ${opts.size === 'sm' ? 'modal-sm' : opts.size === 'lg' ? 'modal-lg' : ''}">${html}</div>`;

    backdrop.addEventListener('click', (e) => {
      if (e.target === backdrop && !opts.persistent) closeModal();
    });

    document.body.appendChild(backdrop);
    activeModal = backdrop;

    const firstInput = backdrop.querySelector('input, textarea, select');
    if (firstInput) setTimeout(() => firstInput.focus(), 100);

    return backdrop;
  };

  const closeModal = () => {
    if (activeModal) {
      activeModal.remove();
      activeModal = null;
    }
    const existing = document.getElementById('modal-backdrop');
    if (existing) existing.remove();
  };

  // ── Confirm Dialog ─────────────────────────
  const confirm = (message, title = 'Are you sure?') => {
    return new Promise((resolve) => {
      const modal = openModal(`
        <div class="modal-header">
          <span class="modal-title">${title}</span>
          <button class="modal-close" onclick="UI.closeModal()">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
          </button>
        </div>
        <p style="color:var(--text-2);margin-bottom:24px;">${message}</p>
        <div class="modal-footer">
          <button class="btn btn-secondary" id="confirm-cancel">Cancel</button>
          <button class="btn btn-danger" id="confirm-ok">Delete</button>
        </div>
      `, { size: 'sm' });

      modal.querySelector('#confirm-cancel').addEventListener('click', () => {
        closeModal(); resolve(false);
      });
      modal.querySelector('#confirm-ok').addEventListener('click', () => {
        closeModal(); resolve(true);
      });
    });
  };

  // ── DOM Helpers ─────────────────────────────
  const $ = (sel, ctx = document) => ctx.querySelector(sel);
  const $$ = (sel, ctx = document) => [...ctx.querySelectorAll(sel)];
  const el = (tag, cls = '', html = '') => {
    const e = document.createElement(tag);
    if (cls) e.className = cls;
    if (html) e.innerHTML = html;
    return e;
  };

  const setHTML = (sel, html) => {
    const el = typeof sel === 'string' ? $(sel) : sel;
    if (el) el.innerHTML = html;
  };

  const show = (sel) => {
    const e = typeof sel === 'string' ? $(sel) : sel;
    if (e) e.style.display = '';
  };

  const hide = (sel) => {
    const e = typeof sel === 'string' ? $(sel) : sel;
    if (e) e.style.display = 'none';
  };

  // ── Priority Badge HTML ─────────────────────
  const priorityBadge = (priority) => {
    const map = { high: ['danger', '↑ High'], medium: ['warning', '→ Medium'], low: ['success', '↓ Low'] };
    const [type, label] = map[priority] || ['muted', priority];
    return `<span class="badge badge-${type}">${label}</span>`;
  };

  const statusBadge = (status) => {
    const map = {
      not_started: ['muted', 'Not Started'],
      in_progress: ['warning', 'In Progress'],
      submitted: ['accent', 'Submitted'],
      graded: ['success', 'Graded'],
      completed: ['success', 'Completed'],
    };
    const [type, label] = map[status] || ['muted', status];
    return `<span class="badge badge-${type}">${label}</span>`;
  };

  // ── Time Greeting ────────────────────────────
  const greeting = () => {
    const h = new Date().getHours();
    if (h < 12) return 'Good morning';
    if (h < 17) return 'Good afternoon';
    if (h < 21) return 'Good evening';
    return 'Good night';
  };

  // ── Format Helpers ────────────────────────────
  const formatDate = (str) => {
    if (!str) return '—';
    const d = new Date(str + 'T00:00:00');
    return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  };

  const formatDateTime = (isoStr) => {
    if (!isoStr) return '';
    const d = new Date(isoStr);
    return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
  };

  const relativeTime = (isoStr) => {
    if (!isoStr) return '';
    const diff = Date.now() - new Date(isoStr).getTime();
    const m = Math.floor(diff / 60000);
    if (m < 1) return 'just now';
    if (m < 60) return `${m}m ago`;
    const h = Math.floor(m / 60);
    if (h < 24) return `${h}h ago`;
    return `${Math.floor(h / 24)}d ago`;
  };

  const daysUntilLabel = (dateStr) => {
    const days = Store.daysUntil(dateStr);
    if (days === null) return '';
    if (days < 0) return `<span class="text-danger">${Math.abs(days)}d overdue</span>`;
    if (days === 0) return `<span class="text-warning">Due today</span>`;
    if (days === 1) return `<span class="text-warning">Due tomorrow</span>`;
    if (days <= 3) return `<span class="text-warning">Due in ${days}d</span>`;
    return `<span class="text-muted">Due ${formatDate(dateStr)}</span>`;
  };

  const subjectColor = (subjectId) => {
    const subjects = Store.getSubjects();
    const s = subjects.find(s => s.id === subjectId || s.name === subjectId);
    return s ? s.color : '#6366f1';
  };

  const subjectName = (subjectId) => {
    const subjects = Store.getSubjects();
    const s = subjects.find(s => s.id === subjectId || s.name === subjectId);
    return s ? s.name : subjectId || '';
  };

  // ── Chevron SVG ──────────────────────────────
  const chevron = (dir = 'right') => {
    const rotMap = { right: 0, down: 90, left: 180, up: 270 };
    return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="transform:rotate(${rotMap[dir]}deg)"><polyline points="9 18 15 12 9 6"/></svg>`;
  };

  // ── Animate Numbers ──────────────────────────
  const animateNumber = (el, from, to, duration = 800) => {
    const start = performance.now();
    const update = (now) => {
      const progress = Math.min((now - start) / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      el.textContent = Math.round(from + (to - from) * eased);
      if (progress < 1) requestAnimationFrame(update);
    };
    requestAnimationFrame(update);
  };

  // ── Subject color dot ─────────────────────────
  const subjectDot = (color) =>
    `<span class="color-dot" style="background:${color || '#6366f1'}"></span>`;

  return {
    toast, openModal, closeModal, confirm,
    $, $$, el, setHTML, show, hide,
    priorityBadge, statusBadge,
    greeting, formatDate, formatDateTime, relativeTime, daysUntilLabel,
    subjectColor, subjectName, subjectDot,
    chevron, animateNumber, ICONS,
  };
})();

// Escape key closes modals
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') UI.closeModal();
});
