/* ============================================
   ANALYTICS.JS — Charts & Insights
   ============================================ */

const Analytics = (() => {
  const render = () => {
    UI.setHTML('#page-analytics', `
      <div class="page-header">
        <h2 class="page-title">Analytics</h2>
        <p class="page-subtitle">Insights into your productivity and health</p>
      </div>

      <div class="grid-2 gap-20 mb-20">
        <!-- Task Completion -->
        <div class="card">
          <div class="section-header mb-16"><span class="section-title">Task Completion (7 days)</span></div>
          <canvas id="chart-tasks" height="180"></canvas>
        </div>
        <!-- Attendance Overview -->
        <div class="card">
          <div class="section-header mb-16"><span class="section-title">Attendance by Subject</span></div>
          <canvas id="chart-attendance" height="180"></canvas>
        </div>
      </div>

      <div class="grid-2 gap-20 mb-20">
        <!-- Sleep Trend -->
        <div class="card">
          <div class="section-header mb-16"><span class="section-title">Sleep Duration (7 days)</span></div>
          <canvas id="chart-sleep" height="180"></canvas>
        </div>
        <!-- Expense Chart -->
        <div class="card">
          <div class="section-header mb-16"><span class="section-title">Spending by Category</span></div>
          <canvas id="chart-expense" height="180"></canvas>
        </div>
      </div>

      <!-- Habit Consistency -->
      <div class="card mb-20">
        <div class="section-header mb-16"><span class="section-title">Habit Consistency (Last 28 Days)</span></div>
        <div id="habit-heatmap"></div>
      </div>

      <!-- Summary Stats -->
      <div class="grid-4 stagger-children">
        ${summaryCard('Total Tasks Done', Store.getTodos().filter(t=>t.completed).length, '✅')}
        ${summaryCard('Notes Created', Store.getNotes().length, '📝')}
        ${summaryCard('Workouts Logged', Store.getWorkouts().length, '💪')}
        ${summaryCard('Sleep Logs', Store.getSleepLogs().length, '😴')}
      </div>
    `);

    setTimeout(renderCharts, 100);
  };

  const summaryCard = (label, val, icon) => `
    <div class="card text-center">
      <div style="font-size:2rem;margin-bottom:8px;">${icon}</div>
      <div class="stat-value">${val}</div>
      <div class="stat-label">${label}</div>
    </div>
  `;

  const renderCharts = () => {
    if (typeof Chart === 'undefined') return;

    const isDark = document.documentElement.getAttribute('data-theme') !== 'light';
    const gridColor = isDark ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.06)';
    const tickColor = isDark ? '#9898bc' : '#50507a';

    Chart.defaults.color = tickColor;
    Chart.defaults.borderColor = gridColor;

    const last7 = [];
    for (let i=6;i>=0;i--) { const d=new Date();d.setDate(d.getDate()-i);last7.push(d.toISOString().slice(0,10)); }
    const dayLabels = last7.map(d => { const dd=new Date(d+'T00:00:00');return ['Sun','Mon','Tue','Wed','Thu','Fri','Sat'][dd.getDay()]; });

    // Tasks Chart
    const todos = Store.getTodos();
    const taskData = last7.map(d => todos.filter(t=>t.dueDate===d&&t.completed).length);
    const taskTotal = last7.map(d => todos.filter(t=>t.dueDate===d).length);
    renderChart('chart-tasks', 'bar', dayLabels, [
      { label:'Completed', data:taskData, backgroundColor:'rgba(99,102,241,0.6)', borderColor:'#6366f1', borderWidth:2, borderRadius:6 },
      { label:'Total', data:taskTotal, backgroundColor:'rgba(139,92,246,0.3)', borderColor:'#8b5cf6', borderWidth:2, borderRadius:6 }
    ]);

    // Attendance Chart
    const subjects = Store.getSubjects();
    if (subjects.length > 0) {
      const attLabels = subjects.map(s=>s.name.slice(0,8));
      const attData = subjects.map(s => Store.getAttendanceStats(s.id).pct);
      const attColors = subjects.map(s => s.color+'99');
      renderChart('chart-attendance', 'bar', attLabels, [
        { label:'Attendance %', data:attData, backgroundColor:attColors, borderColor:subjects.map(s=>s.color), borderWidth:2, borderRadius:6 }
      ], { max:100, suggestedMax:100 });
    } else {
      document.getElementById('chart-attendance').parentElement.innerHTML += '<p class="text-muted text-sm text-center mt-8">Add subjects to see attendance</p>';
    }

    // Sleep Chart
    const sleepLogs = Store.getSleepLogs();
    const sleepData = last7.map(d => { const l=sleepLogs.find(l=>l.date===d); return l?.duration||0; });
    const settings = Store.getSettings();
    renderChart('chart-sleep', 'line', dayLabels, [
      { label:'Hours Slept', data:sleepData, borderColor:'#06b6d4', backgroundColor:'rgba(6,182,212,0.15)', fill:true, tension:0.4, pointRadius:5 }
    ], { annotation: settings.sleepGoal || 8 });

    // Expense Pie
    const expenses = Store.getExpenses();
    const catMap = {};
    expenses.filter(e=>e.type==='expense').forEach(e => { catMap[e.category]=(catMap[e.category]||0)+e.amount; });
    if (Object.keys(catMap).length > 0) {
      const catLabels = Object.keys(catMap);
      const catData = Object.values(catMap);
      const PIE_COLORS = ['#6366f1','#8b5cf6','#06b6d4','#22c55e','#f59e0b','#ef4444','#ec4899','#f97316'];
      renderChart('chart-expense', 'doughnut', catLabels, [
        { data:catData, backgroundColor:PIE_COLORS.slice(0,catLabels.length), borderWidth:0 }
      ]);
    } else {
      document.getElementById('chart-expense').parentElement.innerHTML += '<p class="text-muted text-sm text-center mt-8">No expenses logged yet</p>';
    }

    // Habit Heatmap
    renderHabitHeatmap();
  };

  const renderChart = (id, type, labels, datasets, opts = {}) => {
    const canvas = document.getElementById(id);
    if (!canvas) return;
    if (canvas._chart) canvas._chart.destroy();
    const isDark = document.documentElement.getAttribute('data-theme') !== 'light';
    const gridColor = isDark ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.06)';
    const tickColor = isDark ? '#9898bc' : '#50507a';
    canvas._chart = new Chart(canvas.getContext('2d'), {
      type,
      data: { labels, datasets },
      options: {
        responsive: true, maintainAspectRatio: false,
        plugins: { legend: { labels: { color: tickColor, boxWidth: 12, font: { size: 11 } } } },
        scales: type === 'doughnut' ? {} : {
          x: { grid: { color: gridColor }, ticks: { color: tickColor, font: { size: 11 } } },
          y: { grid: { color: gridColor }, ticks: { color: tickColor, font: { size: 11 } }, ...(opts.max ? { max: opts.max } : {}) }
        }
      }
    });
  };

  const renderHabitHeatmap = () => {
    const container = document.getElementById('habit-heatmap');
    if (!container) return;
    const habits = Store.getHabits();
    const last28 = [];
    for (let i=27;i>=0;i--) { const d=new Date();d.setDate(d.getDate()-i);last28.push(d.toISOString().slice(0,10)); }

    if (habits.length === 0) {
      container.innerHTML = '<p class="text-muted text-sm">No habits to show. Add habits to see consistency.</p>';
      return;
    }

    container.innerHTML = `
      <div style="overflow-x:auto;">
        <div style="min-width:600px;">
          ${habits.map(h => `
            <div class="flex gap-10 items-center mb-8">
              <span style="font-size:1rem;width:24px;text-align:center;">${h.icon}</span>
              <span style="font-size:0.75rem;font-weight:500;width:100px;truncate;">${h.name}</span>
              <div style="display:flex;gap:3px;flex:1;">
                ${last28.map(d => `
                  <div style="width:18px;height:18px;border-radius:3px;background:${h.completions[d]?h.color:'var(--bg-4)'};opacity:${h.completions[d]?1:0.3};flex-shrink:0;" title="${d}"></div>
                `).join('')}
              </div>
              <span class="streak-badge" style="font-size:0.65rem;padding:2px 8px;">🔥${h.streak||0}</span>
            </div>
          `).join('')}
        </div>
      </div>
    `;
  };

  return { render };
})();

/* ============================================
   SETTINGS.JS — App Settings
   ============================================ */

const Settings = (() => {
  const render = () => {
    const s = Store.getSettings();

    UI.setHTML('#page-settings', `
      <div class="page-header">
        <h2 class="page-title">Settings</h2>
        <p class="page-subtitle">Customize your experience</p>
      </div>

      <div class="grid-2 gap-20">
        <!-- Profile -->
        <div class="card">
          <div class="section-header mb-20">
            <span class="section-title">👤 Profile</span>
          </div>
          <div class="flex-center mb-20" style="flex-direction:column;gap:12px;">
            <div class="avatar" style="width:72px;height:72px;font-size:1.5rem;" id="settings-avatar">${(s.name||'S').slice(0,2).toUpperCase()}</div>
            <div style="text-align:center;">
              <div style="font-weight:700;font-size:1.1rem;" id="settings-name-display">${s.name||'Student'}</div>
              <div class="text-sm text-muted" id="settings-college-display">${s.college||'College not set'}</div>
            </div>
          </div>
          <div class="modal-form">
            <div class="input-group">
              <label class="input-label">Your Name</label>
              <input class="input" id="s-name" value="${s.name||''}" placeholder="Your name" oninput="Settings.liveUpdate()">
            </div>
            <div class="input-group">
              <label class="input-label">College / University</label>
              <input class="input" id="s-college" value="${s.college||''}" placeholder="College name">
            </div>
            <div class="input-group">
              <label class="input-label">Semester Start Date</label>
              <input type="date" class="input" id="s-sem" value="${s.semesterStart||''}">
            </div>
          </div>
        </div>

        <!-- Appearance -->
        <div class="card">
          <div class="section-header mb-20">
            <span class="section-title">🎨 Appearance</span>
          </div>
          <div class="modal-form">
            <div class="input-group">
              <label class="input-label">Theme</label>
              <div class="tabs">
                <button class="tab ${s.theme!=='light'?'active':''}" onclick="Settings.setTheme('dark')">🌙 Dark</button>
                <button class="tab ${s.theme==='light'?'active':''}" onclick="Settings.setTheme('light')">☀️ Light</button>
              </div>
            </div>
          </div>
        </div>

        <!-- Goals -->
        <div class="card">
          <div class="section-header mb-20">
            <span class="section-title">🎯 Daily Goals</span>
          </div>
          <div class="modal-form">
            <div class="input-group">
              <label class="input-label">Study Hours Goal (daily)</label>
              <input type="number" class="input" id="s-study" value="${s.dailyGoalHours||6}" min="1" max="16">
            </div>
            <div class="input-group">
              <label class="input-label">Calorie Goal (daily kcal)</label>
              <input type="number" class="input" id="s-cal" value="${s.calorieGoal||2000}" min="500">
            </div>
            <div class="input-group">
              <label class="input-label">Sleep Goal (hours)</label>
              <input type="number" class="input" id="s-sleep" value="${s.sleepGoal||8}" min="4" max="12">
            </div>
            <div class="input-group">
              <label class="input-label">Monthly Budget (₹)</label>
              <input type="number" class="input" id="s-budget" value="${s.budgetMonthly||5000}" min="0">
            </div>
            <div class="input-group">
              <label class="input-label">GPA Scale</label>
              <select class="input" id="s-gpa">
                <option value="10" ${s.gpaScale===10?'selected':''}>10-point (India)</option>
                <option value="4" ${s.gpaScale===4?'selected':''}>4-point (US)</option>
              </select>
            </div>
          </div>
        </div>

        <!-- Data Management -->
        <div class="card">
          <div class="section-header mb-20">
            <span class="section-title">💾 Data</span>
          </div>
          <div class="flex-col gap-12">
            <button class="btn btn-secondary" onclick="Settings.exportData()">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
              Export All Data (JSON)
            </button>
            <button class="btn btn-secondary" onclick="Settings.importData()">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>
              Import Data
            </button>
            <button class="btn btn-danger" onclick="Settings.clearData()">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14H6L5 6"/><path d="M9 6V4h6v2"/></svg>
              Clear All Data
            </button>
          </div>
          <div class="divider"></div>
          <div class="text-sm text-muted">
            <p>All data is stored locally in your browser.</p>
            <p class="mt-4">Export regularly to back up your data.</p>
          </div>
        </div>
      </div>

      <div class="flex-center mt-24">
        <button class="btn btn-primary btn-lg" onclick="Settings.save()">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 21H5a2 2 0 01-2-2V5a2 2 0 012-2h11l5 5v11a2 2 0 01-2 2z"/><polyline points="17 21 17 13 7 13 7 21"/><polyline points="7 3 7 8 15 8"/></svg>
          Save Settings
        </button>
      </div>
    `);
  };

  const liveUpdate = () => {
    const name = document.getElementById('s-name')?.value.trim() || 'S';
    const avatarEl = document.getElementById('settings-avatar');
    const nameEl = document.getElementById('settings-name-display');
    if (avatarEl) avatarEl.textContent = name.slice(0,2).toUpperCase();
    if (nameEl) nameEl.textContent = name;
  };

  const setTheme = (theme) => {
    Store.updateSettings({ theme });
    document.documentElement.setAttribute('data-theme', theme);
    // Update topbar avatar
    const themeToggle = document.getElementById('theme-toggle-btn');
    if (themeToggle) themeToggle.textContent = theme === 'light' ? '🌙' : '☀️';
    render();
  };

  const save = () => {
    Store.updateSettings({
      name: document.getElementById('s-name')?.value.trim() || 'Student',
      college: document.getElementById('s-college')?.value.trim(),
      semesterStart: document.getElementById('s-sem')?.value,
      dailyGoalHours: parseInt(document.getElementById('s-study')?.value)||6,
      calorieGoal: parseInt(document.getElementById('s-cal')?.value)||2000,
      sleepGoal: parseInt(document.getElementById('s-sleep')?.value)||8,
      budgetMonthly: parseInt(document.getElementById('s-budget')?.value)||5000,
      gpaScale: parseInt(document.getElementById('s-gpa')?.value)||10,
    });
    // Update topbar name
    const topbarName = document.getElementById('topbar-user-name');
    if (topbarName) topbarName.textContent = Store.getSettings().name;
    const topbarAvatar = document.getElementById('topbar-avatar');
    if (topbarAvatar) topbarAvatar.textContent = (Store.getSettings().name||'S').slice(0,2).toUpperCase();
    UI.toast('Settings saved!', 'success');
  };

  const exportData = () => {
    const data = Store.exportAll();
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `student-analyser-backup-${Store.todayStr()}.json`;
    a.click();
    URL.revokeObjectURL(url);
    UI.toast('Data exported!', 'success');
  };

  const importData = () => {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.json';
    input.onchange = (e) => {
      const file = e.target.files[0];
      if (!file) return;
      const reader = new FileReader();
      reader.onload = (ev) => {
        try {
          const data = JSON.parse(ev.target.result);
          Store.importAll(data);
          UI.toast('Data imported! Refreshing...', 'success');
          setTimeout(() => location.reload(), 1000);
        } catch(err) {
          UI.toast('Invalid file format', 'error');
        }
      };
      reader.readAsText(file);
    };
    input.click();
  };

  const clearData = async () => {
    const ok = await UI.confirm('This will permanently delete ALL your data. This cannot be undone!', '⚠️ Clear All Data');
    if (!ok) return;
    Store.clear();
    UI.toast('All data cleared', 'info');
    setTimeout(() => location.reload(), 1000);
  };

  return { render, save, setTheme, liveUpdate, exportData, importData, clearData };
})();
