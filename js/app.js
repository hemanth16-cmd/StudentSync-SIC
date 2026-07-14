/* ============================================
   APP.JS — Router, Navigation, App Init
   ============================================ */

const App = (() => {
  const PAGES = {
    dashboard: { label: 'Dashboard', module: Dashboard },
    todos: { label: 'To-Do', module: Todos },
    planner: { label: 'Planner', module: Planner },
    subjects: { label: 'Subjects', module: Subjects },
    assignments: { label: 'Assignments', module: Assignments },
    notes: { label: 'Notes', module: Notes },
    attendance: { label: 'Attendance', module: Attendance },
    habits: { label: 'Habit Tracker', module: Habits },
    diet: { label: 'Diet', module: Diet },
    workout: { label: 'Workout', module: Workout },
    sleep: { label: 'Sleep', module: Sleep },
    expenses: { label: 'Expenses', module: Expenses },
    analytics: { label: 'Analytics', module: Analytics },
    settings: { label: 'Settings', module: Settings },
  };

  let currentPage = 'dashboard';
  let sidebarCollapsed = false;

  const init = () => {
    // Apply saved theme
    const settings = Store.getSettings();
    document.documentElement.setAttribute('data-theme', settings.theme || 'light');

    // Update topbar
    updateTopbar(settings);

    // Set up nav clicks
    document.querySelectorAll('.nav-item[data-page]').forEach(el => {
      el.addEventListener('click', () => navigate(el.dataset.page));
    });

    // Sidebar toggle (desktop)
    document.getElementById('sidebar-toggle')?.addEventListener('click', toggleSidebar);

    // Mobile menu
    document.getElementById('mobile-menu-btn')?.addEventListener('click', openMobileSidebar);
    document.getElementById('sidebar-overlay')?.addEventListener('click', closeMobileSidebar);

    // Theme toggle
    document.getElementById('theme-toggle-btn')?.addEventListener('click', () => {
      const current = document.documentElement.getAttribute('data-theme');
      Settings.setTheme(current === 'light' ? 'dark' : 'light');
    });

    // Search (topbar)
    document.getElementById('topbar-search-input')?.addEventListener('input', (e) => {
      if (currentPage === 'todos') {
        Todos.onSearch(e.target.value);
      }
    });

    // Navigate to hash or default
    const hash = location.hash.slice(1);
    navigate(PAGES[hash] ? hash : 'dashboard');

    // Handle browser back/forward
    window.addEventListener('hashchange', () => {
      const h = location.hash.slice(1);
      if (PAGES[h] && h !== currentPage) navigate(h, false);
    });

    // Keyboard shortcuts
    document.addEventListener('keydown', (e) => {
      if (e.altKey) {
        const shortcuts = { 'd':'dashboard','t':'todos','n':'notes','a':'assignments','s':'subjects' };
        if (shortcuts[e.key]) { e.preventDefault(); navigate(shortcuts[e.key]); }
      }
    });

    console.log('✅ StudentSync initialized');
  };

  const navigate = (page, updateHash = true) => {
    if (!PAGES[page]) return;
    currentPage = page;

    // Update page visibility
    document.querySelectorAll('.page').forEach(el => el.classList.remove('active'));
    const pageEl = document.getElementById(`page-${page}`);
    if (pageEl) pageEl.classList.add('active');

    // Update nav active state
    document.querySelectorAll('.nav-item[data-page]').forEach(el => {
      el.classList.toggle('active', el.dataset.page === page);
    });

    // Update topbar title
    const topbarTitle = document.getElementById('topbar-page-title');
    if (topbarTitle) topbarTitle.textContent = PAGES[page].label;

    // Update hash
    if (updateHash) history.replaceState(null, '', `#${page}`);

    // Render module
    const mod = PAGES[page].module;
    if (mod?.render) {
      try { mod.render(); } catch (e) { console.error(`Error rendering ${page}:`, e); }
    }

    // Close mobile sidebar
    closeMobileSidebar();

    // Scroll to top
    document.querySelector('.main-content')?.scrollTo(0, 0);
  };

  const toggleSidebar = () => {
    sidebarCollapsed = !sidebarCollapsed;
    const sidebar = document.getElementById('sidebar');
    const mainContent = document.querySelector('.main-content');
    sidebar?.classList.toggle('collapsed', sidebarCollapsed);
    mainContent?.classList.toggle('sidebar-collapsed', sidebarCollapsed);
  };

  const openMobileSidebar = () => {
    document.getElementById('sidebar')?.classList.add('mobile-open');
    document.getElementById('sidebar-overlay')?.classList.add('active');
    document.body.style.overflow = 'hidden';
  };

  const closeMobileSidebar = () => {
    document.getElementById('sidebar')?.classList.remove('mobile-open');
    document.getElementById('sidebar-overlay')?.classList.remove('active');
    document.body.style.overflow = '';
  };

  const updateTopbar = (settings) => {
    const name = settings.name || 'Student';
    const avatarEl = document.getElementById('topbar-avatar');
    const nameEl = document.getElementById('topbar-user-name');
    if (avatarEl) avatarEl.textContent = name.slice(0,2).toUpperCase();
    if (nameEl) nameEl.textContent = name;
    const themeBtn = document.getElementById('theme-toggle-btn');
    if (themeBtn) themeBtn.textContent = settings.theme === 'dark' ? '☀️' : '🌙';
  };

  return { init, navigate, toggleSidebar };
})();

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', App.init);
