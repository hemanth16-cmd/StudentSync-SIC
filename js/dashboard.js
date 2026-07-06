/* ============================================
   DASHBOARD.JS — Home Dashboard
   ============================================ */

const Dashboard = (() => {

  const DAYS = ['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'];
  const MONTHS = ['January','February','March','April','May','June','July','August','September','October','November','December'];

  const render = () => {
    const settings = Store.getSettings();
    const name = settings.name || 'Student';
    const now = new Date();
    const todayStr = Store.todayStr();

    // Streak
    const streak = Store.updateStreak();

    // Todos stats
    const todos = Store.getTodos();
    const todayTodos = todos.filter(t => t.dueDate === todayStr || (!t.dueDate && !t.completed));
    const completedToday = todayTodos.filter(t => t.completed).length;
    const totalToday = todayTodos.length;
    const score = totalToday > 0 ? Math.round((completedToday / totalToday) * 100) : 0;

    // Upcoming deadlines
    const upcoming = [...Store.getTodos(), ...Store.getAssignments()]
      .filter(i => i.dueDate && !i.completed && i.status !== 'submitted' && i.status !== 'graded')
      .sort((a, b) => a.dueDate.localeCompare(b.dueDate))
      .slice(0, 5);

    // Weekly progress (last 7 days)
    const weekData = getWeekProgress();

    // Today's planner events
    const dayIndex = (now.getDay() + 6) % 7; // 0=Mon...6=Sun
    const plannerEvents = Store.getPlannerEvents().filter(e => e.day === dayIndex);
    plannerEvents.sort((a, b) => a.startTime.localeCompare(b.startTime));

    // Recent notes
    const notes = Store.getNotes().slice(0, 3);

    // Goals
    const goals = Store.getTodayGoals();

    // Habits today
    const habits = Store.getHabits();
    const habitsDoneToday = habits.filter(h => h.completions[todayStr]).length;

    UI.setHTML('#page-dashboard', `
      <!-- Hero Welcome -->
      <div class="dashboard-hero card" style="background:var(--accent-grad);border:none;margin-bottom:24px;position:relative;overflow:hidden;">
        <div style="position:absolute;top:-40px;right:-40px;width:200px;height:200px;background:rgba(255,255,255,0.06);border-radius:50%;"></div>
        <div style="position:absolute;bottom:-60px;right:60px;width:150px;height:150px;background:rgba(255,255,255,0.04);border-radius:50%;"></div>
        <div class="flex-between" style="position:relative;z-index:1;">
          <div>
            <div style="font-size:0.8rem;color:rgba(255,255,255,0.7);margin-bottom:4px;font-weight:500;">${UI.greeting()},</div>
            <h1 style="color:white;font-size:1.8rem;margin-bottom:4px;letter-spacing:-0.02em;">${name} 👋</h1>
            <div style="color:rgba(255,255,255,0.75);font-size:0.875rem;">${DAYS[now.getDay()]}, ${MONTHS[now.getMonth()]} ${now.getDate()}, ${now.getFullYear()}</div>
          </div>
          <div style="text-align:right;">
            <div class="streak-badge" style="background:rgba(255,255,255,0.15);border-color:rgba(255,255,255,0.3);color:white;">
              🔥 ${streak} day streak
            </div>
            <div style="color:rgba(255,255,255,0.7);font-size:0.78rem;margin-top:8px;">${completedToday}/${totalToday} tasks done today</div>
          </div>
        </div>
      </div>

      <!-- Quick Actions -->
      <div class="quick-actions mb-20">
        <button class="quick-action-btn" onclick="App.navigate('todos'); setTimeout(() => Todos.openAddModal(),100)">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
          Add Task
        </button>
        <button class="quick-action-btn" onclick="App.navigate('notes'); setTimeout(() => Notes.openAddModal(),100)">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
          New Note
        </button>
        <button class="quick-action-btn" onclick="App.navigate('assignments'); setTimeout(() => Assignments.openAddModal(),100)">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 11l3 3L22 4"/><path d="M21 12v7a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2h11"/></svg>
          Assignment
        </button>
        <button class="quick-action-btn" onclick="App.navigate('expenses'); setTimeout(() => Expenses.openAddModal(),100)">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 000 7h5a3.5 3.5 0 010 7H6"/></svg>
          Expense
        </button>
      </div>

      <!-- Stats Row -->
      <div class="grid-4 mb-24 stagger-children">
        ${statCard('Productivity', score + '%', 'target', score >= 80 ? 'success' : score >= 50 ? 'warning' : 'accent', 'Today\'s score')}
        ${statCard('Streak', streak + ' days', 'zap', 'warning', 'Current streak')}
        ${statCard('Habits', `${habitsDoneToday}/${habits.length}`, 'repeat', 'accent', 'Done today')}
        ${statCard('Tasks', `${completedToday}/${totalToday}`, 'check-circle', 'success', 'Completed today')}
      </div>

      <!-- Main Grid -->
      <div class="grid-2 gap-24">
        <!-- Left Column -->
        <div class="flex-col gap-20">
          <!-- Today's Tasks -->
          <div class="card">
            <div class="section-header">
              <span class="section-title">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
                Today's Tasks
              </span>
              <button class="btn btn-ghost btn-sm" onclick="App.navigate('todos')">View all</button>
            </div>
            <div id="dashboard-todos">
              ${renderTodayTasks(todayTodos)}
            </div>
            ${totalToday === 0 ? `<button class="btn btn-primary btn-sm mt-12" onclick="App.navigate('todos');setTimeout(()=>Todos.openAddModal(),100)">+ Add your first task</button>` : ''}
          </div>

          <!-- Daily Goals -->
          <div class="card">
            <div class="section-header">
              <span class="section-title">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/></svg>
                Daily Goals
              </span>
              <button class="btn btn-icon" onclick="Dashboard.addGoalPrompt()" title="Add goal">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
              </button>
            </div>
            <div id="dashboard-goals">
              ${renderGoals(goals)}
            </div>
          </div>

          <!-- Weekly Progress -->
          <div class="card">
            <div class="section-header">
              <span class="section-title">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>
                Weekly Progress
              </span>
            </div>
            <div class="flex gap-8 mt-8" style="align-items:flex-end;height:80px;">
              ${weekData.map((d, i) => `
                <div class="flex-col items-center gap-4" style="flex:1;">
                  <div style="flex:1;display:flex;align-items:flex-end;width:100%;">
                    <div style="width:100%;background:${d.today ? 'var(--accent-grad)' : 'var(--bg-4)'};border-radius:4px 4px 0 0;height:${Math.max(d.pct, 4)}%;transition:height 600ms ease;min-height:4px;${d.today?'box-shadow:var(--shadow-glow-sm)':''}"></div>
                  </div>
                  <div style="font-size:0.65rem;color:${d.today ? 'var(--accent-light)' : 'var(--text-3)'};font-weight:${d.today?'600':'400'}">${d.label}</div>
                </div>
              `).join('')}
            </div>
          </div>
        </div>

        <!-- Right Column -->
        <div class="flex-col gap-20">
          <!-- Today's Classes -->
          <div class="card">
            <div class="section-header">
              <span class="section-title">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M2 3h6a4 4 0 014 4v14a3 3 0 00-3-3H2z"/><path d="M22 3h-6a4 4 0 00-4 4v14a3 3 0 013-3h7z"/></svg>
                Today's Classes
              </span>
              <button class="btn btn-ghost btn-sm" onclick="App.navigate('planner')">View planner</button>
            </div>
            ${plannerEvents.length === 0
              ? `<div class="empty-state" style="padding:24px;">
                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
                  <p>No classes today</p>
                </div>`
              : plannerEvents.map(ev => `
                <div class="flex gap-12 items-center" style="padding:10px 0;border-bottom:1px solid var(--border);last-child:border-none;">
                  <div style="width:4px;height:40px;border-radius:2px;background:${ev.color};flex-shrink:0;"></div>
                  <div style="flex:1;">
                    <div style="font-size:0.875rem;font-weight:600;">${ev.title}</div>
                    <div style="font-size:0.75rem;color:var(--text-3);">${ev.startTime} – ${ev.endTime}${ev.room ? ' · ' + ev.room : ''}</div>
                  </div>
                </div>
              `).join('')
            }
          </div>

          <!-- Upcoming Deadlines -->
          <div class="card">
            <div class="section-header">
              <span class="section-title">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
                Upcoming Deadlines
              </span>
            </div>
            ${upcoming.length === 0
              ? `<p class="text-muted text-sm">No upcoming deadlines 🎉</p>`
              : upcoming.map(item => `
                <div class="flex-between" style="padding:10px 0;border-bottom:1px solid var(--border);">
                  <div style="flex:1;min-width:0;">
                    <div style="font-size:0.875rem;font-weight:500;truncate;">${item.title}</div>
                    <div style="font-size:0.75rem;color:var(--text-3);">${item.subject || ''}</div>
                  </div>
                  <div style="text-align:right;flex-shrink:0;margin-left:12px;">
                    ${UI.daysUntilLabel(item.dueDate)}
                    <div style="font-size:0.7rem;color:var(--text-3);margin-top:2px;">${UI.formatDate(item.dueDate)}</div>
                  </div>
                </div>
              `).join('')
            }
          </div>

          <!-- Recent Notes -->
          <div class="card">
            <div class="section-header">
              <span class="section-title">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>
                Recent Notes
              </span>
              <button class="btn btn-ghost btn-sm" onclick="App.navigate('notes')">View all</button>
            </div>
            ${notes.length === 0
              ? `<p class="text-muted text-sm">No notes yet</p>`
              : notes.map(n => `
                <div class="card" style="padding:12px;margin-bottom:8px;cursor:pointer;background:var(--bg-3);" onclick="App.navigate('notes')">
                  <div style="font-size:0.85rem;font-weight:600;margin-bottom:4px;">${n.title}</div>
                  <div style="font-size:0.75rem;color:var(--text-3);">${(n.content || '').replace(/<[^>]*>/g,'').slice(0,60)}${n.content && n.content.length > 60 ? '...' : ''}</div>
                </div>
              `).join('')
            }
          </div>
        </div>
      </div>
    `);
  };

  const statCard = (label, value, icon, type, sub) => {
    const iconSVGs = {
      target: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/></svg>`,
      zap: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>`,
      repeat: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="17 1 21 5 17 9"/><path d="M3 11V9a4 4 0 014-4h14"/><polyline points="7 23 3 19 7 15"/><path d="M21 13v2a4 4 0 01-4 4H3"/></svg>`,
      'check-circle': `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 11-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>`,
    };
    const colorMap = { success: 'var(--success)', warning: 'var(--warning)', accent: 'var(--accent-light)', danger: 'var(--danger)' };
    const bgMap = { success: 'var(--success-bg)', warning: 'var(--warning-bg)', accent: 'var(--accent-dim)', danger: 'var(--danger-bg)' };
    return `
      <div class="stat-card">
        <div class="stat-icon" style="background:${bgMap[type]};color:${colorMap[type]};">${iconSVGs[icon] || ''}</div>
        <div>
          <div class="stat-value">${value}</div>
          <div class="stat-label">${label}</div>
          <div class="text-xs text-dimmed mt-4">${sub}</div>
        </div>
      </div>
    `;
  };

  const renderTodayTasks = (tasks) => {
    if (tasks.length === 0) return `<p class="text-muted text-sm">No tasks for today.</p>`;
    return tasks.slice(0, 5).map(t => `
      <div class="flex gap-12 items-center" style="padding:9px 0;border-bottom:1px solid var(--border);">
        <button class="checkbox ${t.completed ? 'checked' : ''}" onclick="Dashboard.toggleTask('${t.id}')" id="dash-cb-${t.id}">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>
        </button>
        <span style="flex:1;font-size:0.875rem;${t.completed ? 'color:var(--text-3);text-decoration:line-through;' : ''}">${t.title}</span>
        ${UI.priorityBadge(t.priority)}
      </div>
    `).join('');
  };

  const renderGoals = (goals) => {
    if (goals.length === 0) return `<p class="text-muted text-sm">Add your goals for today.</p>`;
    return goals.map(g => `
      <div class="flex gap-10 items-center" style="padding:8px 0;">
        <button class="checkbox ${g.completed ? 'checked' : ''}" onclick="Dashboard.toggleGoal('${g.id}')">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>
        </button>
        <span style="flex:1;font-size:0.875rem;${g.completed ? 'color:var(--text-3);text-decoration:line-through;' : ''}">${g.text}</span>
        <button class="btn-icon" style="width:24px;height:24px;font-size:0.7rem;" onclick="Dashboard.deleteGoal('${g.id}')">✕</button>
      </div>
    `).join('');
  };

  const getWeekProgress = () => {
    const labels = ['M','T','W','T','F','S','S'];
    const todos = Store.getTodos();
    const result = [];
    const today = new Date();
    const todayDay = today.getDay(); // 0=Sun...6=Sat

    for (let i = 0; i < 7; i++) {
      const d = new Date(today);
      // Get Monday of current week
      const diffToMon = (todayDay === 0 ? -6 : 1 - todayDay);
      d.setDate(today.getDate() + diffToMon + i);
      const dStr = d.toISOString().slice(0, 10);
      const dayTodos = todos.filter(t => t.dueDate === dStr);
      const done = dayTodos.filter(t => t.completed).length;
      const total = dayTodos.length;
      result.push({
        label: labels[i],
        pct: total > 0 ? (done / total) * 100 : 0,
        today: dStr === Store.todayStr(),
      });
    }
    return result;
  };

  const toggleTask = (id) => {
    Store.toggleTodo(id);
    // Check if all done
    const todos = Store.getTodos();
    const todayStr = Store.todayStr();
    const todayTodos = todos.filter(t => t.dueDate === todayStr || !t.dueDate);
    if (todayTodos.length > 0 && todayTodos.every(t => t.completed)) {
      Confetti.fire(250);
      UI.toast('🎉 All tasks complete! Amazing work!', 'success', 4000);
    }
    render();
  };

  const toggleGoal = (id) => {
    Store.toggleDailyGoal(id);
    render();
  };

  const deleteGoal = (id) => {
    const goals = Store.getDailyGoals().filter(g => g.id !== id);
    Store.saveDailyGoals(goals);
    render();
  };

  const addGoalPrompt = () => {
    UI.openModal(`
      <div class="modal-header">
        <span class="modal-title">Add Daily Goal</span>
        <button class="modal-close" onclick="UI.closeModal()">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
        </button>
      </div>
      <div class="input-group">
        <label class="input-label">Goal for today</label>
        <input class="input" id="goal-input" placeholder="e.g. Study for 3 hours" maxlength="80">
      </div>
      <div class="modal-footer">
        <button class="btn btn-secondary" onclick="UI.closeModal()">Cancel</button>
        <button class="btn btn-primary" onclick="Dashboard.saveGoal()">Add Goal</button>
      </div>
    `, { size: 'sm' });
    document.getElementById('goal-input').addEventListener('keydown', (e) => {
      if (e.key === 'Enter') saveGoal();
    });
  };

  const saveGoal = () => {
    const input = document.getElementById('goal-input');
    const text = input?.value.trim();
    if (!text) return UI.toast('Please enter a goal', 'warning');
    Store.addDailyGoal(text);
    UI.closeModal();
    UI.toast('Goal added!', 'success');
    render();
  };

  return { render, toggleTask, toggleGoal, deleteGoal, addGoalPrompt, saveGoal };
})();
