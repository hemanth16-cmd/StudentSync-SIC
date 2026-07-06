/* ============================================
   EXPENSES.JS — Budget & Expense Tracker
   ============================================ */

const Expenses = (() => {
  const CATEGORIES = {
    food:'🍔 Food', transport:'🚌 Transport', books:'📚 Books', entertainment:'🎬 Entertainment',
    clothing:'👕 Clothing', health:'💊 Health', subscription:'📱 Subscription',
    tuition:'🏫 Tuition', income:'💵 Income', other:'💰 Other'
  };

  const render = () => {
    const settings = Store.getSettings();
    const budget = settings.budgetMonthly || 5000;
    const expenses = Store.getExpenses();
    const now = new Date();
    const monthStr = `${now.getFullYear()}-${String(now.getMonth()+1).padStart(2,'0')}`;
    const monthExpenses = expenses.filter(e => e.date.startsWith(monthStr));

    const totalIncome = monthExpenses.filter(e=>e.type==='income').reduce((s,e)=>s+e.amount,0);
    const totalExpense = monthExpenses.filter(e=>e.type==='expense').reduce((s,e)=>s+e.amount,0);
    const balance = totalIncome - totalExpense;
    const budgetUsed = Math.min(Math.round((totalExpense/budget)*100),100);

    // Category breakdown
    const catBreakdown = {};
    monthExpenses.filter(e=>e.type==='expense').forEach(e => {
      catBreakdown[e.category] = (catBreakdown[e.category]||0) + e.amount;
    });

    UI.setHTML('#page-expenses', `
      <div class="page-header flex-between">
        <div>
          <h2 class="page-title">Expenses</h2>
          <p class="page-subtitle">${now.toLocaleDateString('en-US',{month:'long',year:'numeric'})}</p>
        </div>
        <button class="btn btn-primary" onclick="Expenses.openAddModal()">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
          Add Entry
        </button>
      </div>

      <!-- Summary Cards -->
      <div class="grid-3 mb-20 stagger-children">
        <div class="stat-card">
          <div class="stat-value text-success">₹${totalIncome.toLocaleString()}</div>
          <div class="stat-label">Income</div>
          <div class="text-xs text-dimmed">This month</div>
        </div>
        <div class="stat-card">
          <div class="stat-value text-danger">₹${totalExpense.toLocaleString()}</div>
          <div class="stat-label">Spent</div>
          <div class="text-xs text-dimmed">This month</div>
        </div>
        <div class="stat-card">
          <div class="stat-value ${balance>=0?'text-success':'text-danger'}">₹${Math.abs(balance).toLocaleString()}</div>
          <div class="stat-label">${balance>=0?'Balance':'Deficit'}</div>
          <div class="text-xs text-dimmed">${balance>=0?'Surplus':'Overspent'}</div>
        </div>
      </div>

      <!-- Budget Progress -->
      <div class="card mb-20">
        <div class="flex-between mb-8">
          <span class="font-semibold">Monthly Budget</span>
          <span class="text-sm text-muted">₹${totalExpense.toLocaleString()} / ₹${budget.toLocaleString()}</span>
        </div>
        <div class="progress-bar" style="height:10px;"><div class="progress-fill ${budgetUsed>=100?'danger':budgetUsed>=80?'warning':'success'}" style="width:${budgetUsed}%"></div></div>
        <div class="flex-between mt-6">
          <span class="text-xs text-dimmed">${budgetUsed}% used</span>
          <span class="text-xs ${budgetUsed>=100?'text-danger':'text-muted'}">₹${Math.max(budget-totalExpense,0).toLocaleString()} remaining</span>
        </div>
      </div>

      <div class="grid-2 gap-20">
        <!-- Category Breakdown -->
        <div class="card">
          <div class="section-header mb-16"><span class="section-title">By Category</span></div>
          ${Object.entries(catBreakdown).length === 0 ? `<p class="text-muted text-sm">No expenses this month</p>` :
            Object.entries(catBreakdown).sort((a,b)=>b[1]-a[1]).map(([cat,amt]) => {
              const pct = totalExpense > 0 ? Math.round(amt/totalExpense*100) : 0;
              return `
                <div style="margin-bottom:12px;">
                  <div class="flex-between mb-4">
                    <span class="text-sm">${CATEGORIES[cat]||cat}</span>
                    <span class="text-sm font-semibold">₹${amt.toLocaleString()} <span class="text-dimmed text-xs">(${pct}%)</span></span>
                  </div>
                  <div class="progress-bar"><div class="progress-fill" style="width:${pct}%;"></div></div>
                </div>
              `;
            }).join('')
          }
        </div>

        <!-- Recent Transactions -->
        <div class="card">
          <div class="section-header mb-16"><span class="section-title">Recent Transactions</span></div>
          ${expenses.slice(0,10).map(e => `
            <div class="flex-between" style="padding:8px 0;border-bottom:1px solid var(--border);">
              <div style="flex:1;">
                <div class="flex gap-8 items-center">
                  <span style="font-size:0.85rem;font-weight:500;">${e.description || CATEGORIES[e.category]}</span>
                  <span class="badge badge-muted" style="font-size:0.65rem;">${CATEGORIES[e.category]?.split(' ')[0]||'💰'}</span>
                </div>
                <div class="text-xs text-dimmed">${UI.formatDate(e.date)}</div>
              </div>
              <div class="flex gap-8 items-center">
                <span style="font-weight:700;color:${e.type==='income'?'var(--success)':'var(--danger)'};">${e.type==='income'?'+':'-'}₹${e.amount.toLocaleString()}</span>
                <button onclick="Expenses.delete('${e.id}')" class="btn-icon" style="color:var(--danger);width:24px;height:24px;">
                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="width:12px;height:12px;"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14H6L5 6"/><path d="M9 6V4h6v2"/></svg>
                </button>
              </div>
            </div>
          `).join('')}
          ${expenses.length === 0 ? `<p class="text-muted text-sm">No transactions yet</p>` : ''}
        </div>
      </div>
    `);
  };

  const openAddModal = () => {
    UI.openModal(`
      <div class="modal-header">
        <span class="modal-title">Add Transaction</span>
        <button class="modal-close" onclick="UI.closeModal()"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg></button>
      </div>
      <div class="modal-form">
        <div class="input-group">
          <label class="input-label">Type</label>
          <div class="tabs">
            <button class="tab active" id="type-expense" onclick="this.className='tab active';document.getElementById('type-income').className='tab';document.getElementById('exp-type').value='expense'">💸 Expense</button>
            <button class="tab" id="type-income" onclick="this.className='tab active';document.getElementById('type-expense').className='tab';document.getElementById('exp-type').value='income'">💵 Income</button>
          </div>
          <input type="hidden" id="exp-type" value="expense">
        </div>
        <div class="input-group">
          <label class="input-label">Amount (₹) *</label>
          <input type="number" class="input" id="exp-amount" placeholder="0.00" min="0" step="0.01">
        </div>
        <div class="input-group">
          <label class="input-label">Description</label>
          <input class="input" id="exp-desc" placeholder="What was this for?">
        </div>
        <div class="grid-2">
          <div class="input-group">
            <label class="input-label">Category</label>
            <select class="input" id="exp-cat">
              ${Object.entries(CATEGORIES).map(([k,v])=>`<option value="${k}">${v}</option>`).join('')}
            </select>
          </div>
          <div class="input-group">
            <label class="input-label">Date</label>
            <input type="date" class="input" id="exp-date" value="${Store.todayStr()}">
          </div>
        </div>
      </div>
      <div class="modal-footer">
        <button class="btn btn-secondary" onclick="UI.closeModal()">Cancel</button>
        <button class="btn btn-primary" onclick="Expenses.save()">Save</button>
      </div>
    `);
  };

  const save = () => {
    const amount = parseFloat(document.getElementById('exp-amount')?.value);
    if (!amount || amount <= 0) return UI.toast('Enter a valid amount', 'warning');
    Store.addExpense({
      type: document.getElementById('exp-type')?.value,
      amount,
      description: document.getElementById('exp-desc')?.value.trim(),
      category: document.getElementById('exp-cat')?.value,
      date: document.getElementById('exp-date')?.value || Store.todayStr(),
    });
    UI.closeModal();
    UI.toast('Transaction saved!', 'success');
    render();
  };

  const del = (id) => {
    Store.deleteExpense(id);
    render();
  };

  return { render, openAddModal, save, delete: del };
})();
