/* ============================================
   HABITS.JS — Habit Tracker
   ============================================ */

const Habits = (() => {
  const ICONS = ['⭐','💪','📚','🏃','💧','🧘','🥗','😴','🎯','✍️','🎸','🌅','🧹','💻','📖','🚴','🏋️','🤸'];
  const COLORS = ['#6366f1','#8b5cf6','#22c55e','#f59e0b','#06b6d4','#ef4444','#ec4899','#f97316'];

  let selectedIcon = '⭐';
  let selectedColor = '#6366f1';

  const render = () => {
    const habits = Store.getHabits();
    const today = Store.todayStr();

    // Get last 7 days
    const last7 = [];
    for (let i = 6; i >= 0; i--) {
      const d = new Date(); d.setDate(d.getDate() - i);
      last7.push(d.toISOString().slice(0,10));
    }

    UI.setHTML('#page-habits', `
      <div class="page-header flex-between">
        <div>
          <h2 class="page-title">Habit Tracker</h2>
          <p class="page-subtitle">${habits.filter(h=>h.completions[today]).length}/${habits.length} done today</p>
        </div>
        <button class="btn btn-primary" onclick="Habits.openAddModal()">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
          New Habit
        </button>
      </div>

      <!-- Today's check-ins -->
      ${habits.length === 0 ? `
        <div class="empty-state">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="17 1 21 5 17 9"/><path d="M3 11V9a4 4 0 014-4h14"/><polyline points="7 23 3 19 7 15"/><path d="M21 13v2a4 4 0 01-4 4H3"/></svg>
          <h3>No habits yet</h3>
          <p>Build positive routines by tracking daily habits</p>
          <button class="btn btn-primary mt-12" onclick="Habits.openAddModal()">+ Add Habit</button>
        </div>
      ` : `
        <!-- Day header row -->
        <div class="card mb-20" style="padding:16px 20px;">
          <div style="display:grid;grid-template-columns:1fr repeat(7,40px) 80px;gap:6px;align-items:center;margin-bottom:8px;">
            <div class="text-xs text-dimmed font-semibold">HABIT</div>
            ${last7.map(d=>{
              const dd = new Date(d+'T00:00:00');
              const isToday = d === today;
              return `<div class="text-xs text-center ${isToday?'text-accent font-semibold':'text-dimmed'}">${['S','M','T','W','T','F','S'][dd.getDay()]}<br><span style="font-size:0.6rem;">${dd.getDate()}</span></div>`;
            }).join('')}
            <div class="text-xs text-dimmed text-center">STREAK</div>
          </div>
          ${habits.map(h => `
            <div style="display:grid;grid-template-columns:1fr repeat(7,40px) 80px;gap:6px;align-items:center;padding:8px 0;border-top:1px solid var(--border);">
              <div class="flex gap-10 items-center">
                <button class="btn-icon" onclick="Habits.delete('${h.id}')" style="width:28px;height:28px;opacity:0.4;color:var(--danger);" title="Delete">✕</button>
                <span style="font-size:1.2rem;">${h.icon}</span>
                <span style="font-size:0.875rem;font-weight:500;truncate;">${h.name}</span>
              </div>
              ${last7.map(d => {
                const done = h.completions[d];
                const isFuture = d > today;
                return `
                  <div class="flex-center" style="height:34px;">
                    <button onclick="${isFuture ? '' : `Habits.toggle('${h.id}','${d}')`}" style="
                      width:30px;height:30px;border-radius:8px;
                      background:${done ? h.color+'22' : 'var(--bg-4)'};
                      border:2px solid ${done ? h.color : 'transparent'};
                      font-size:0.9rem;cursor:${isFuture?'default':'pointer'};
                      transition:all 0.15s;
                      ${isFuture?'opacity:0.3;':''}
                    ">${done ? '✓' : ''}</button>
                  </div>
                `;
              }).join('')}
              <div class="flex-center">
                <div class="streak-badge" style="font-size:0.75rem;padding:4px 10px;">🔥 ${h.streak || 0}</div>
              </div>
            </div>
          `).join('')}
        </div>

        <!-- Habit Detail Cards -->
        <div class="grid-auto stagger-children">
          ${habits.map(h => {
            const last28 = [];
            for (let i = 27; i >= 0; i--) { const d = new Date(); d.setDate(d.getDate()-i); last28.push(d.toISOString().slice(0,10)); }
            const doneCount = last28.filter(d=>h.completions[d]).length;
            const rate = Math.round((doneCount/28)*100);
            return `
              <div class="card">
                <div class="flex gap-12 items-center mb-12">
                  <div style="width:44px;height:44px;border-radius:var(--r-lg);background:${h.color}22;display:flex;align-items:center;justify-content:center;font-size:1.4rem;">${h.icon}</div>
                  <div style="flex:1;">
                    <div style="font-weight:600;">${h.name}</div>
                    <div class="text-xs text-dimmed">${doneCount}/28 days this month</div>
                  </div>
                  <button onclick="Habits.toggle('${h.id}','${today}')" class="btn ${h.completions[today] ? 'btn-success' : 'btn-primary'} btn-sm">
                    ${h.completions[today] ? '✓ Done' : 'Do it!'}
                  </button>
                </div>
                <div class="progress-bar mb-6"><div class="progress-fill" style="width:${rate}%;background:${h.color};"></div></div>
                <div class="flex-between">
                  <span class="text-xs text-dimmed">${rate}% consistency</span>
                  <span class="streak-badge" style="font-size:0.7rem;padding:3px 8px;">🔥 ${h.streak||0} streak</span>
                </div>
                <!-- 4-week heatmap -->
                <div style="display:grid;grid-template-columns:repeat(7,1fr);gap:3px;margin-top:12px;">
                  ${last28.map(d => `
                    <div onclick="Habits.toggle('${h.id}','${d}')" style="
                      aspect-ratio:1;border-radius:3px;cursor:pointer;
                      background:${h.completions[d] ? h.color : 'var(--bg-4)'};
                      opacity:${h.completions[d]?1:0.3};
                      transition:all 0.15s;
                    " title="${d}"></div>
                  `).join('')}
                </div>
              </div>
            `;
          }).join('')}
        </div>
      `}
    `);
  };

  const toggle = (id, date) => {
    Store.toggleHabit(id, date);
    if (date === Store.todayStr()) {
      const habits = Store.getHabits();
      const allDone = habits.every(h => h.completions[date]);
      if (allDone && habits.length > 0) {
        Confetti.fire(150);
        UI.toast('🎉 All habits done today! Outstanding!', 'success', 3000);
      }
    }
    render();
  };

  const openAddModal = () => {
    selectedIcon = '⭐';
    selectedColor = '#6366f1';
    UI.openModal(`
      <div class="modal-header">
        <span class="modal-title">New Habit</span>
        <button class="modal-close" onclick="UI.closeModal()"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg></button>
      </div>
      <div class="modal-form">
        <div class="input-group">
          <label class="input-label">Habit Name *</label>
          <input class="input" id="habit-name" placeholder="e.g. Read 30 minutes, Exercise...">
        </div>
        <div class="input-group">
          <label class="input-label">Icon</label>
          <div class="flex flex-wrap gap-8" id="icon-picker">
            ${ICONS.map(ic => `<button class="btn-icon" style="width:36px;height:36px;font-size:1.1rem;${ic===selectedIcon?'background:var(--accent-dim);border-color:var(--border-accent);':''}" onclick="Habits.pickIcon('${ic}')">${ic}</button>`).join('')}
          </div>
        </div>
        <div class="input-group">
          <label class="input-label">Color</label>
          <div class="color-picker-row">
            ${COLORS.map(c=>`<div class="color-swatch ${c===selectedColor?'selected':''}" style="background:${c}" onclick="Habits.pickColor('${c}')"></div>`).join('')}
          </div>
        </div>
      </div>
      <div class="modal-footer">
        <button class="btn btn-secondary" onclick="UI.closeModal()">Cancel</button>
        <button class="btn btn-primary" onclick="Habits.save()">Add Habit</button>
      </div>
    `);
  };

  const pickIcon = (icon) => {
    selectedIcon = icon;
    document.querySelectorAll('#icon-picker .btn-icon').forEach(el => {
      const sel = el.textContent === icon;
      el.style.background = sel ? 'var(--accent-dim)' : '';
      el.style.borderColor = sel ? 'var(--border-accent)' : '';
    });
  };

  const pickColor = (color) => {
    selectedColor = color;
    document.querySelectorAll('.color-swatch').forEach(el => {
      el.classList.toggle('selected', el.style.background === color);
    });
  };

  const save = () => {
    const name = document.getElementById('habit-name')?.value.trim();
    if (!name) return UI.toast('Habit name required', 'warning');
    Store.addHabit({ name, icon: selectedIcon, color: selectedColor });
    UI.closeModal();
    UI.toast('Habit added!', 'success');
    render();
  };

  const del = async (id) => {
    const ok = await UI.confirm('Delete this habit and all its history?', 'Delete Habit');
    if (!ok) return;
    Store.saveHabits(Store.getHabits().filter(h=>h.id!==id));
    render();
  };

  return { render, toggle, openAddModal, save, pickIcon, pickColor, delete: del };
})();
