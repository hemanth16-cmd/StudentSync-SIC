/* ============================================
   WORKOUT.JS — Workout Tracker
   ============================================ */

const Workout = (() => {
  const TYPES = { strength:'💪',cardio:'🏃',yoga:'🧘',sports:'⚽',other:'🏋️' };

  const render = () => {
    const workouts = Store.getWorkouts();
    const today = Store.todayStr();
    const todayWorkout = workouts.find(w => w.date === today);

    // Stats
    const thisWeek = workouts.filter(w => {
      const d = new Date(w.date); const now = new Date();
      const diff = (now - d) / 86400000;
      return diff <= 7;
    });
    const totalMinutes = thisWeek.reduce((s,w) => s+(w.duration||0), 0);
    const totalCal = thisWeek.reduce((s,w) => s+(w.calories||0), 0);

    UI.setHTML('#page-workout', `
      <div class="page-header flex-between">
        <div>
          <h2 class="page-title">Workout Tracker</h2>
          <p class="page-subtitle">${thisWeek.length} sessions this week</p>
        </div>
        <button class="btn btn-primary" onclick="Workout.openAddModal()">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
          Log Workout
        </button>
      </div>

      <!-- Stats -->
      <div class="grid-3 mb-20 stagger-children">
        ${statCard('Sessions', thisWeek.length, 'This week')}
        ${statCard('Minutes', totalMinutes, 'This week')}
        ${statCard('Calories', totalCal, 'Burned this week')}
      </div>

      <!-- Today Highlight -->
      ${todayWorkout ? `
        <div class="card mb-20" style="background:var(--accent-grad);border:none;color:white;">
          <div class="flex gap-12 items-center">
            <span style="font-size:2rem;">${TYPES[todayWorkout.type]||'🏋️'}</span>
            <div>
              <div style="font-weight:700;font-size:1.1rem;">Today: ${todayWorkout.name || todayWorkout.type}</div>
              <div style="color:rgba(255,255,255,0.8);font-size:0.85rem;">${todayWorkout.duration} min · ${todayWorkout.calories} kcal</div>
            </div>
          </div>
        </div>
      ` : `
        <div class="card mb-20" style="background:var(--bg-3);border:2px dashed var(--border);">
          <div class="flex gap-12 items-center">
            <span style="font-size:2rem;opacity:0.4;">💪</span>
            <div>
              <div style="font-weight:600;">No workout logged today</div>
              <div class="text-sm text-muted">Stay active! Even a short walk counts.</div>
            </div>
            <button class="btn btn-primary btn-sm" style="margin-left:auto;" onclick="Workout.openAddModal()">Log Now</button>
          </div>
        </div>
      `}

      <!-- History -->
      <div class="section-header mb-16">
        <span class="section-title">Workout History</span>
      </div>
      ${workouts.length === 0 ? `
        <div class="empty-state">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M18 8h1a4 4 0 010 8h-1"/><path d="M2 8h16v9a4 4 0 01-4 4H6a4 4 0 01-4-4V8z"/><line x1="6" y1="1" x2="6" y2="4"/><line x1="10" y1="1" x2="10" y2="4"/><line x1="14" y1="1" x2="14" y2="4"/></svg>
          <h3>No workouts yet</h3>
          <p>Start logging your workouts to track your fitness progress</p>
        </div>
      ` : `
        <div class="flex-col gap-10 stagger-children">
          ${workouts.slice(0,20).map(w => `
            <div class="card flex gap-14 items-center" style="padding:14px 18px;">
              <div style="width:44px;height:44px;border-radius:var(--r-md);background:var(--accent-dim);display:flex;align-items:center;justify-content:center;font-size:1.3rem;flex-shrink:0;">${TYPES[w.type]||'🏋️'}</div>
              <div style="flex:1;">
                <div style="font-weight:600;font-size:0.9rem;">${w.name || (w.type.charAt(0).toUpperCase()+w.type.slice(1))}</div>
                <div class="text-xs text-muted">${UI.formatDate(w.date)} · ${w.duration} min${w.calories?' · '+w.calories+' kcal':''}</div>
                ${w.notes ? `<div class="text-xs text-dimmed mt-2">${w.notes}</div>` : ''}
                ${w.exercises?.length ? `<div class="flex gap-6 flex-wrap mt-4">${w.exercises.map(e=>`<span class="tag">${e}</span>`).join('')}</div>` : ''}
              </div>
              <button onclick="Workout.delete('${w.id}')" class="btn-icon" style="color:var(--danger);">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="width:14px;height:14px;"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14H6L5 6"/><path d="M9 6V4h6v2"/></svg>
              </button>
            </div>
          `).join('')}
        </div>
      `}
    `);
  };

  const statCard = (label, val, sub) => `
    <div class="stat-card">
      <div class="stat-value">${val}</div>
      <div class="stat-label">${label}</div>
      <div class="text-xs text-dimmed">${sub}</div>
    </div>
  `;

  const openAddModal = () => {
    UI.openModal(`
      <div class="modal-header">
        <span class="modal-title">Log Workout</span>
        <button class="modal-close" onclick="UI.closeModal()"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg></button>
      </div>
      <div class="modal-form">
        <div class="grid-2">
          <div class="input-group">
            <label class="input-label">Type</label>
            <select class="input" id="wo-type">
              ${Object.entries(TYPES).map(([k,v])=>`<option value="${k}">${v} ${k.charAt(0).toUpperCase()+k.slice(1)}</option>`).join('')}
            </select>
          </div>
          <div class="input-group">
            <label class="input-label">Session Name</label>
            <input class="input" id="wo-name" placeholder="e.g. Chest Day, Morning Run...">
          </div>
        </div>
        <div class="grid-2">
          <div class="input-group">
            <label class="input-label">Duration (min)</label>
            <input type="number" class="input" id="wo-duration" value="45" min="1">
          </div>
          <div class="input-group">
            <label class="input-label">Calories Burned</label>
            <input type="number" class="input" id="wo-cal" value="0" min="0">
          </div>
        </div>
        <div class="input-group">
          <label class="input-label">Exercises (comma separated)</label>
          <input class="input" id="wo-exercises" placeholder="Push-ups, Squats, Pull-ups...">
        </div>
        <div class="input-group">
          <label class="input-label">Date</label>
          <input type="date" class="input" id="wo-date" value="${Store.todayStr()}">
        </div>
        <div class="input-group">
          <label class="input-label">Notes</label>
          <textarea class="input" id="wo-notes" rows="2" placeholder="How did it go?"></textarea>
        </div>
      </div>
      <div class="modal-footer">
        <button class="btn btn-secondary" onclick="UI.closeModal()">Cancel</button>
        <button class="btn btn-primary" onclick="Workout.save()">Save Workout</button>
      </div>
    `);
  };

  const save = () => {
    const exercises = (document.getElementById('wo-exercises')?.value||'').split(',').map(e=>e.trim()).filter(Boolean);
    Store.addWorkout({
      type: document.getElementById('wo-type')?.value,
      name: document.getElementById('wo-name')?.value.trim(),
      duration: parseInt(document.getElementById('wo-duration')?.value)||0,
      calories: parseInt(document.getElementById('wo-cal')?.value)||0,
      exercises,
      date: document.getElementById('wo-date')?.value||Store.todayStr(),
      notes: document.getElementById('wo-notes')?.value.trim(),
    });
    UI.closeModal();
    UI.toast('Workout logged! 💪', 'success');
    render();
  };

  const del = async (id) => {
    Store.deleteWorkout(id);
    render();
  };

  return { render, openAddModal, save, delete: del };
})();

/* ============================================
   SLEEP.JS — Sleep Tracker
   ============================================ */

const Sleep = (() => {
  const render = () => {
    const logs = Store.getSleepLogs();
    const settings = Store.getSettings();
    const sleepGoal = settings.sleepGoal || 8;

    // Last 7 days avg
    const last7 = [];
    for (let i=6;i>=0;i--) { const d=new Date();d.setDate(d.getDate()-i);last7.push(d.toISOString().slice(0,10)); }
    const last7Logs = last7.map(d => logs.find(l=>l.date===d));
    const avgSleep = last7Logs.filter(Boolean).length > 0
      ? (last7Logs.filter(Boolean).reduce((s,l)=>s+(l.duration||0),0) / last7Logs.filter(Boolean).length).toFixed(1)
      : 0;

    const todayLog = logs.find(l=>l.date===Store.todayStr());
    const stars = (q) => '★'.repeat(q) + '☆'.repeat(5-q);

    UI.setHTML('#page-sleep', `
      <div class="page-header flex-between">
        <div>
          <h2 class="page-title">Sleep Tracker</h2>
          <p class="page-subtitle">Avg ${avgSleep}h / ${sleepGoal}h goal</p>
        </div>
        <button class="btn btn-primary" onclick="Sleep.openAddModal()">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1111.21 3 7 7 0 0021 12.79z"/></svg>
          Log Sleep
        </button>
      </div>

      <!-- Stats -->
      <div class="grid-3 mb-20 stagger-children">
        <div class="stat-card">
          <div class="stat-value" style="${parseFloat(avgSleep) >= sleepGoal ? 'color:var(--success)' : parseFloat(avgSleep) >= sleepGoal*0.8 ? 'color:var(--warning)' : 'color:var(--danger)'}">${avgSleep}h</div>
          <div class="stat-label">Avg Sleep</div>
          <div class="text-xs text-dimmed">Last 7 days</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">${todayLog ? todayLog.duration + 'h' : '—'}</div>
          <div class="stat-label">Last Night</div>
          <div class="text-xs text-dimmed">${todayLog ? stars(todayLog.quality) : 'Not logged'}</div>
        </div>
        <div class="stat-card">
          <div class="stat-value" style="color:${parseFloat(avgSleep) >= sleepGoal ? 'var(--success)' : 'var(--danger)'}">
            ${parseFloat(avgSleep) >= sleepGoal ? '0' : (sleepGoal - parseFloat(avgSleep)).toFixed(1)}h
          </div>
          <div class="stat-label">Sleep Debt</div>
          <div class="text-xs text-dimmed">${parseFloat(avgSleep) >= sleepGoal ? '🎉 Well rested!' : 'Per night avg'}</div>
        </div>
      </div>

      <!-- Weekly Chart -->
      <div class="card mb-20">
        <div class="section-header mb-12"><span class="section-title">Last 7 Days</span></div>
        <div class="flex gap-8 items-end" style="height:100px;">
          ${last7.map((d,i) => {
            const log = last7Logs[i];
            const dur = log?.duration || 0;
            const pct = Math.min(dur / 12 * 100, 100);
            const dd = new Date(d+'T00:00:00');
            const labels = ['S','M','T','W','T','F','S'];
            return `
              <div class="flex-col items-center gap-4" style="flex:1;">
                <div style="font-size:0.65rem;color:var(--text-3);">${dur > 0 ? dur+'h' : ''}</div>
                <div style="flex:1;display:flex;align-items:flex-end;width:100%;">
                  <div style="width:100%;border-radius:4px 4px 0 0;min-height:4px;height:${Math.max(pct,4)}%;background:${dur>=sleepGoal?'var(--success)':dur>=sleepGoal*0.8?'var(--warning)':'var(--danger)'};transition:height 0.6s ease;opacity:${log?1:0.25}"></div>
                </div>
                <div style="font-size:0.65rem;color:var(--text-3);">${labels[dd.getDay()]}</div>
              </div>
            `;
          }).join('')}
        </div>
        <div style="margin-top:8px;border-top:2px dashed var(--border);position:relative;">
          <span style="position:absolute;right:0;top:-10px;font-size:0.6rem;color:var(--text-3);">Goal: ${sleepGoal}h</span>
        </div>
      </div>

      <!-- Log History -->
      <div class="section-header mb-16"><span class="section-title">Sleep Log</span></div>
      ${logs.length === 0 ? `
        <div class="empty-state">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1111.21 3 7 7 0 0021 12.79z"/></svg>
          <h3>No sleep logged</h3>
          <p>Track your sleep to improve your energy and performance</p>
        </div>
      ` : `
        <div class="flex-col gap-8 stagger-children">
          ${logs.slice(0,14).map(l => `
            <div class="card flex-between" style="padding:14px 18px;">
              <div class="flex gap-12 items-center">
                <div style="font-size:1.5rem;">😴</div>
                <div>
                  <div style="font-weight:600;">${l.date === Store.todayStr() ? 'Today' : UI.formatDate(l.date)}</div>
                  <div class="text-xs text-muted">${l.bedtime} → ${l.wakeTime} · ${l.duration}h</div>
                </div>
              </div>
              <div class="flex gap-12 items-center">
                <div style="color:var(--warning);font-size:0.9rem;">${stars(l.quality||3)}</div>
                <button onclick="Sleep.delete('${l.id}')" class="btn-icon" style="color:var(--danger);">
                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="width:14px;height:14px;"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14H6L5 6"/><path d="M9 6V4h6v2"/></svg>
                </button>
              </div>
            </div>
          `).join('')}
        </div>
      `}
    `);
  };

  const openAddModal = () => {
    UI.openModal(`
      <div class="modal-header">
        <span class="modal-title">Log Sleep</span>
        <button class="modal-close" onclick="UI.closeModal()"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg></button>
      </div>
      <div class="modal-form">
        <div class="input-group">
          <label class="input-label">Date</label>
          <input type="date" class="input" id="sleep-date" value="${Store.todayStr()}">
        </div>
        <div class="grid-2">
          <div class="input-group">
            <label class="input-label">Bedtime</label>
            <input type="time" class="input" id="sleep-bed" value="23:00">
          </div>
          <div class="input-group">
            <label class="input-label">Wake Time</label>
            <input type="time" class="input" id="sleep-wake" value="07:00">
          </div>
        </div>
        <div class="input-group">
          <label class="input-label">Quality (1-5 stars)</label>
          <select class="input" id="sleep-quality">
            <option value="1">⭐ 1 — Terrible</option>
            <option value="2">⭐⭐ 2 — Poor</option>
            <option value="3" selected>⭐⭐⭐ 3 — Okay</option>
            <option value="4">⭐⭐⭐⭐ 4 — Good</option>
            <option value="5">⭐⭐⭐⭐⭐ 5 — Excellent</option>
          </select>
        </div>
        <div class="input-group">
          <label class="input-label">Notes</label>
          <input class="input" id="sleep-notes" placeholder="e.g. Woke up groggy, dreamt a lot...">
        </div>
      </div>
      <div class="modal-footer">
        <button class="btn btn-secondary" onclick="UI.closeModal()">Cancel</button>
        <button class="btn btn-primary" onclick="Sleep.save()">Save Sleep Log</button>
      </div>
    `);
  };

  const calcDuration = (bed, wake) => {
    if (!bed || !wake) return 0;
    const [bh,bm] = bed.split(':').map(Number);
    const [wh,wm] = wake.split(':').map(Number);
    let diff = (wh*60+wm) - (bh*60+bm);
    if (diff < 0) diff += 1440; // next day
    return parseFloat((diff/60).toFixed(1));
  };

  const save = () => {
    const bed = document.getElementById('sleep-bed')?.value;
    const wake = document.getElementById('sleep-wake')?.value;
    Store.addSleepLog({
      date: document.getElementById('sleep-date')?.value || Store.todayStr(),
      bedtime: bed,
      wakeTime: wake,
      duration: calcDuration(bed, wake),
      quality: parseInt(document.getElementById('sleep-quality')?.value)||3,
      notes: document.getElementById('sleep-notes')?.value.trim(),
    });
    UI.closeModal();
    UI.toast('Sleep logged! 😴', 'success');
    render();
  };

  const del = (id) => {
    Store.deleteSleepLog(id);
    render();
  };

  return { render, openAddModal, save, delete: del };
})();
