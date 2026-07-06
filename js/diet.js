/* ============================================
   DIET.JS — Diet & Nutrition Tracker
   ============================================ */

const Diet = (() => {
  const MEALS = ['breakfast','lunch','dinner','snack'];
  const MEAL_LABELS = { breakfast:'🌅 Breakfast', lunch:'☀️ Lunch', dinner:'🌙 Dinner', snack:'🍎 Snack' };

  const render = () => {
    const settings = Store.getSettings();
    const today = Store.todayStr();
    const logs = Store.getDietLogs();
    const todayLogs = logs.filter(l => l.date === today);
    const totalCal = todayLogs.reduce((s,l) => s + (l.calories||0), 0);
    const totalProtein = todayLogs.reduce((s,l) => s + (l.protein||0), 0);
    const totalCarbs = todayLogs.reduce((s,l) => s + (l.carbs||0), 0);
    const totalFat = todayLogs.reduce((s,l) => s + (l.fat||0), 0);
    const calGoal = settings.calorieGoal || 2000;
    const calPct = Math.min(Math.round((totalCal/calGoal)*100), 100);

    UI.setHTML('#page-diet', `
      <div class="page-header flex-between">
        <div>
          <h2 class="page-title">Diet Tracker</h2>
          <p class="page-subtitle">Today's nutrition overview</p>
        </div>
        <button class="btn btn-primary" onclick="Diet.openAddModal()">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
          Log Food
        </button>
      </div>

      <!-- Calorie Ring Card -->
      <div class="card mb-20" style="padding:24px;">
        <div class="flex gap-32 items-center flex-wrap">
          <div style="position:relative;width:140px;height:140px;flex-shrink:0;">
            <svg width="140" height="140" viewBox="0 0 140 140">
              <circle cx="70" cy="70" r="58" fill="none" stroke="var(--bg-4)" stroke-width="12"/>
              <circle cx="70" cy="70" r="58" fill="none" stroke="url(#calGrad)" stroke-width="12" stroke-linecap="round"
                stroke-dasharray="${2*Math.PI*58}" stroke-dashoffset="${2*Math.PI*58*(1-calPct/100)}"
                transform="rotate(-90 70 70)" style="transition:stroke-dashoffset 0.8s ease;"/>
              <defs><linearGradient id="calGrad" x1="0%" y1="0%" x2="100%" y2="0%"><stop offset="0%" stop-color="#6366f1"/><stop offset="100%" stop-color="#8b5cf6"/></linearGradient></defs>
            </svg>
            <div style="position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;">
              <div style="font-size:1.5rem;font-weight:800;letter-spacing:-0.03em;">${totalCal}</div>
              <div style="font-size:0.65rem;color:var(--text-3);">of ${calGoal} kcal</div>
            </div>
          </div>
          <div style="flex:1;">
            <div class="grid-3 gap-12">
              ${macroBar('Protein', totalProtein, 150, '#6366f1')}
              ${macroBar('Carbs', totalCarbs, 250, '#22c55e')}
              ${macroBar('Fat', totalFat, 65, '#f59e0b')}
            </div>
            <div class="grid-4 gap-10 mt-16">
              ${statPill('Calories', totalCal, 'kcal', calPct >= 100 ? 'danger' : calPct >= 80 ? 'warning' : 'accent')}
              ${statPill('Protein', totalProtein, 'g', 'accent')}
              ${statPill('Carbs', totalCarbs, 'g', 'success')}
              ${statPill('Fat', totalFat, 'g', 'warning')}
            </div>
          </div>
        </div>
      </div>

      <!-- Meals by Category -->
      <div class="grid-2 gap-20">
        ${MEALS.map(meal => {
          const mealLogs = todayLogs.filter(l=>l.meal===meal);
          const mealCal = mealLogs.reduce((s,l)=>s+(l.calories||0),0);
          return `
            <div class="card">
              <div class="section-header mb-12">
                <span class="section-title">${MEAL_LABELS[meal]}</span>
                <div class="flex gap-8 items-center">
                  <span class="text-xs text-muted">${mealCal} kcal</span>
                  <button class="btn-icon" onclick="Diet.openAddModal('${meal}')">
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="width:14px;height:14px;"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
                  </button>
                </div>
              </div>
              ${mealLogs.length === 0 ? `<p class="text-sm text-dimmed">Nothing logged yet</p>` : mealLogs.map(l => `
                <div class="flex-between" style="padding:7px 0;border-bottom:1px solid var(--border);">
                  <span class="text-sm font-medium">${l.name}</span>
                  <div class="flex gap-8 items-center">
                    <span class="badge badge-muted">${l.calories} kcal</span>
                    <button onclick="Diet.delete('${l.id}')" style="background:none;border:none;cursor:pointer;color:var(--danger);font-size:0.75rem;">✕</button>
                  </div>
                </div>
              `).join('')}
            </div>
          `;
        }).join('')}
      </div>

      <!-- Weekly Chart placeholder -->
      <div class="card mt-20">
        <div class="section-header mb-12">
          <span class="section-title">This Week's Calories</span>
        </div>
        <canvas id="diet-chart" height="80"></canvas>
      </div>
    `);

    renderChart(logs);
  };

  const macroBar = (label, val, max, color) => `
    <div>
      <div class="flex-between mb-4">
        <span class="text-xs font-semibold">${label}</span>
        <span class="text-xs text-muted">${val}/${max}g</span>
      </div>
      <div class="progress-bar"><div style="height:100%;border-radius:9999px;background:${color};width:${Math.min(val/max*100,100)}%;transition:width 0.6s ease;"></div></div>
    </div>
  `;

  const statPill = (label, val, unit, type) => `
    <div style="text-align:center;padding:10px;background:var(--bg-3);border-radius:var(--r-md);">
      <div class="font-bold text-${type}" style="font-size:1.1rem;">${val}</div>
      <div class="text-xs text-dimmed">${unit}</div>
      <div class="text-xs text-dimmed">${label}</div>
    </div>
  `;

  const renderChart = (logs) => {
    const canvas = document.getElementById('diet-chart');
    if (!canvas || typeof Chart === 'undefined') return;
    const last7 = [];
    for (let i = 6; i >= 0; i--) {
      const d = new Date(); d.setDate(d.getDate()-i);
      last7.push(d.toISOString().slice(0,10));
    }
    const labels = last7.map(d => { const dd = new Date(d+'T00:00:00'); return ['Sun','Mon','Tue','Wed','Thu','Fri','Sat'][dd.getDay()]; });
    const data = last7.map(d => logs.filter(l=>l.date===d).reduce((s,l)=>s+(l.calories||0),0));

    if (canvas._chart) canvas._chart.destroy();
    canvas._chart = new Chart(canvas.getContext('2d'), {
      type: 'bar',
      data: {
        labels,
        datasets: [{ label: 'Calories', data, backgroundColor: 'rgba(99,102,241,0.5)', borderColor: '#6366f1', borderWidth: 2, borderRadius: 6 }]
      },
      options: {
        responsive: true, maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          x: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#9898bc' } },
          y: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#9898bc' } }
        }
      }
    });
  };

  const openAddModal = (defaultMeal = 'breakfast') => {
    UI.openModal(`
      <div class="modal-header">
        <span class="modal-title">Log Food</span>
        <button class="modal-close" onclick="UI.closeModal()"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg></button>
      </div>
      <div class="modal-form">
        <div class="input-group">
          <label class="input-label">Food Name *</label>
          <input class="input" id="diet-name" placeholder="e.g. Oatmeal, Chicken Rice...">
        </div>
        <div class="grid-2">
          <div class="input-group">
            <label class="input-label">Meal</label>
            <select class="input" id="diet-meal">
              ${MEALS.map(m=>`<option value="${m}" ${m===defaultMeal?'selected':''}>${MEAL_LABELS[m]}</option>`).join('')}
            </select>
          </div>
          <div class="input-group">
            <label class="input-label">Date</label>
            <input type="date" class="input" id="diet-date" value="${Store.todayStr()}">
          </div>
        </div>
        <div class="grid-4">
          <div class="input-group">
            <label class="input-label">Calories</label>
            <input type="number" class="input" id="diet-cal" placeholder="0" min="0">
          </div>
          <div class="input-group">
            <label class="input-label">Protein (g)</label>
            <input type="number" class="input" id="diet-protein" placeholder="0" min="0">
          </div>
          <div class="input-group">
            <label class="input-label">Carbs (g)</label>
            <input type="number" class="input" id="diet-carbs" placeholder="0" min="0">
          </div>
          <div class="input-group">
            <label class="input-label">Fat (g)</label>
            <input type="number" class="input" id="diet-fat" placeholder="0" min="0">
          </div>
        </div>
      </div>
      <div class="modal-footer">
        <button class="btn btn-secondary" onclick="UI.closeModal()">Cancel</button>
        <button class="btn btn-primary" onclick="Diet.save()">Log Food</button>
      </div>
    `);
  };

  const save = () => {
    const name = document.getElementById('diet-name')?.value.trim();
    if (!name) return UI.toast('Food name required', 'warning');
    Store.addDietEntry({
      name,
      meal: document.getElementById('diet-meal')?.value,
      date: document.getElementById('diet-date')?.value || Store.todayStr(),
      calories: parseInt(document.getElementById('diet-cal')?.value)||0,
      protein: parseInt(document.getElementById('diet-protein')?.value)||0,
      carbs: parseInt(document.getElementById('diet-carbs')?.value)||0,
      fat: parseInt(document.getElementById('diet-fat')?.value)||0,
    });
    UI.closeModal();
    UI.toast('Food logged!', 'success');
    render();
  };

  const del = (id) => {
    Store.deleteDietEntry(id);
    render();
  };

  return { render, openAddModal, save, delete: del };
})();
