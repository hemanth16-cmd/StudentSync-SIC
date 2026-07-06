/* ============================================
   TODOS.JS — Task Manager
   ============================================ */

const Todos = (() => {
  let filter = { status: 'all', priority: 'all', subject: 'all', search: '' };
  let searchTimer = null;

  const render = () => {
    const todos = getFiltered();
    const subjects = Store.getSubjects();
    const pinned = todos.filter(t => t.pinned);
    const unpinned = todos.filter(t => !t.pinned);

    UI.setHTML('#page-todos', `
      <div class="page-header flex-between">
        <div>
          <h2 class="page-title">To-Do List</h2>
          <p class="page-subtitle">${Store.getTodos().filter(t=>!t.completed).length} tasks remaining</p>
        </div>
        <button class="btn btn-primary" onclick="Todos.openAddModal()">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
          New Task
        </button>
      </div>

      <!-- Filters -->
      <div class="card mb-20" style="padding:14px 18px;">
        <div class="flex gap-12 flex-wrap items-center">
          <div class="search-bar" style="flex:1;min-width:200px;">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
            <input id="todo-search" placeholder="Search tasks..." value="${filter.search}" oninput="Todos.onSearch(this.value)">
          </div>
          <select class="input" style="width:auto;" onchange="Todos.setFilter('status',this.value)">
            <option value="all" ${filter.status==='all'?'selected':''}>All Status</option>
            <option value="active" ${filter.status==='active'?'selected':''}>Active</option>
            <option value="completed" ${filter.status==='completed'?'selected':''}>Completed</option>
          </select>
          <select class="input" style="width:auto;" onchange="Todos.setFilter('priority',this.value)">
            <option value="all" ${filter.priority==='all'?'selected':''}>All Priority</option>
            <option value="high" ${filter.priority==='high'?'selected':''}>High</option>
            <option value="medium" ${filter.priority==='medium'?'selected':''}>Medium</option>
            <option value="low" ${filter.priority==='low'?'selected':''}>Low</option>
          </select>
          <select class="input" style="width:auto;" onchange="Todos.setFilter('subject',this.value)">
            <option value="all">All Subjects</option>
            ${subjects.map(s => `<option value="${s.name}" ${filter.subject===s.name?'selected':''}>${s.name}</option>`).join('')}
          </select>
        </div>
      </div>

      <!-- Task List -->
      <div id="todos-list">
        ${pinned.length > 0 ? `
          <div class="section-header"><span class="section-title" style="font-size:0.78rem;color:var(--text-3);text-transform:uppercase;letter-spacing:0.08em;">📌 Pinned</span></div>
          <div class="flex-col gap-8 mb-20 stagger-children">${pinned.map(t => taskCard(t)).join('')}</div>
        ` : ''}
        ${unpinned.length > 0 ? `
          ${pinned.length > 0 ? `<div class="section-header"><span class="section-title" style="font-size:0.78rem;color:var(--text-3);text-transform:uppercase;letter-spacing:0.08em;">Tasks</span></div>` : ''}
          <div class="flex-col gap-8 stagger-children">${unpinned.map(t => taskCard(t)).join('')}</div>
        ` : ''}
        ${todos.length === 0 ? `
          <div class="empty-state">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
            <h3>No tasks found</h3>
            <p>Add a new task to get started</p>
            <button class="btn btn-primary mt-12" onclick="Todos.openAddModal()">+ Add Task</button>
          </div>
        ` : ''}
      </div>
    `);
  };

  const taskCard = (t) => `
    <div class="card flex gap-12 items-center ${t.completed ? 'opacity-60' : ''}" style="padding:14px 16px;" id="todo-${t.id}">
      <button class="checkbox ${t.completed ? 'checked' : ''}" onclick="Todos.toggle('${t.id}')">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>
      </button>
      <div style="flex:1;min-width:0;">
        <div class="flex gap-8 items-center flex-wrap">
          <span style="font-size:0.9rem;font-weight:500;${t.completed ? 'text-decoration:line-through;color:var(--text-3);' : ''}">${t.title}</span>
          ${t.pinned ? '<span style="font-size:0.7rem;color:var(--warning);">📌</span>' : ''}
        </div>
        <div class="flex gap-8 mt-4 flex-wrap items-center">
          ${UI.priorityBadge(t.priority)}
          ${t.subject ? `<span class="badge badge-muted">${t.subject}</span>` : ''}
          ${t.dueDate ? UI.daysUntilLabel(t.dueDate) : ''}
          ${t.description ? `<span class="text-xs text-dimmed truncate" style="max-width:200px;">${t.description}</span>` : ''}
        </div>
      </div>
      <div class="flex gap-6 items-center">
        <button class="btn-icon" onclick="Todos.togglePin('${t.id}')" title="${t.pinned ? 'Unpin' : 'Pin'}">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="${t.pinned ? 'currentColor' : 'none'}" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="width:14px;height:14px;color:${t.pinned ? 'var(--warning)' : 'inherit'}"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/></svg>
        </button>
        <button class="btn-icon" onclick="Todos.openEditModal('${t.id}')" title="Edit">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="width:14px;height:14px;"><path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
        </button>
        <button class="btn-icon" onclick="Todos.delete('${t.id}')" title="Delete" style="color:var(--danger);">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="width:14px;height:14px;"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14H6L5 6"/><path d="M10 11v6"/><path d="M14 11v6"/><path d="M9 6V4h6v2"/></svg>
        </button>
      </div>
    </div>
  `;

  const getFiltered = () => {
    let todos = Store.getTodos();
    if (filter.status === 'active') todos = todos.filter(t => !t.completed);
    if (filter.status === 'completed') todos = todos.filter(t => t.completed);
    if (filter.priority !== 'all') todos = todos.filter(t => t.priority === filter.priority);
    if (filter.subject !== 'all') todos = todos.filter(t => t.subject === filter.subject);
    if (filter.search) {
      const q = filter.search.toLowerCase();
      todos = todos.filter(t =>
        t.title.toLowerCase().includes(q) ||
        (t.description || '').toLowerCase().includes(q) ||
        (t.subject || '').toLowerCase().includes(q)
      );
    }
    // Sort: pinned first, then by priority
    const pOrder = { high: 0, medium: 1, low: 2 };
    todos.sort((a, b) => {
      if (a.pinned !== b.pinned) return a.pinned ? -1 : 1;
      if (a.completed !== b.completed) return a.completed ? 1 : -1;
      return (pOrder[a.priority] || 1) - (pOrder[b.priority] || 1);
    });
    return todos;
  };

  const setFilter = (key, value) => {
    filter[key] = value;
    render();
  };

  const onSearch = (val) => {
    clearTimeout(searchTimer);
    searchTimer = setTimeout(() => {
      filter.search = val;
      render();
    }, 200);
  };

  const toggle = (id) => {
    const todo = Store.toggleTodo(id);
    if (todo?.completed) {
      const todos = Store.getTodos();
      const allDone = todos.filter(t => !t.pinned).every(t => t.completed);
      if (allDone && todos.length > 0) {
        Confetti.fire();
        UI.toast('🎉 All tasks complete! Great job!', 'success', 4000);
      } else {
        UI.toast('Task completed! ✓', 'success', 1500);
      }
    }
    render();
  };

  const togglePin = (id) => {
    const todos = Store.getTodos();
    const t = todos.find(t => t.id === id);
    if (t) Store.updateTodo(id, { pinned: !t.pinned });
    render();
  };

  const openAddModal = () => {
    const subjects = Store.getSubjects();
    UI.openModal(`
      <div class="modal-header">
        <span class="modal-title">New Task</span>
        <button class="modal-close" onclick="UI.closeModal()">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
        </button>
      </div>
      <div class="modal-form">
        <div class="input-group">
          <label class="input-label">Task Title *</label>
          <input class="input" id="todo-title" placeholder="What needs to be done?" required>
        </div>
        <div class="input-group">
          <label class="input-label">Description</label>
          <textarea class="input" id="todo-desc" placeholder="Add details..." rows="2"></textarea>
        </div>
        <div class="grid-2">
          <div class="input-group">
            <label class="input-label">Subject</label>
            <select class="input" id="todo-subject">
              <option value="">None</option>
              ${subjects.map(s => `<option value="${s.name}">${s.name}</option>`).join('')}
            </select>
          </div>
          <div class="input-group">
            <label class="input-label">Priority</label>
            <select class="input" id="todo-priority">
              <option value="low">Low</option>
              <option value="medium" selected>Medium</option>
              <option value="high">High</option>
            </select>
          </div>
        </div>
        <div class="input-group">
          <label class="input-label">Due Date</label>
          <input type="date" class="input" id="todo-due" value="${Store.todayStr()}">
        </div>
      </div>
      <div class="modal-footer">
        <button class="btn btn-secondary" onclick="UI.closeModal()">Cancel</button>
        <button class="btn btn-primary" onclick="Todos.save()">Add Task</button>
      </div>
    `);
    document.getElementById('todo-title').addEventListener('keydown', e => { if (e.key === 'Enter') save(); });
  };

  const openEditModal = (id) => {
    const t = Store.getTodos().find(t => t.id === id);
    if (!t) return;
    const subjects = Store.getSubjects();
    UI.openModal(`
      <div class="modal-header">
        <span class="modal-title">Edit Task</span>
        <button class="modal-close" onclick="UI.closeModal()">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
        </button>
      </div>
      <div class="modal-form">
        <div class="input-group">
          <label class="input-label">Task Title *</label>
          <input class="input" id="todo-title" value="${t.title}" required>
        </div>
        <div class="input-group">
          <label class="input-label">Description</label>
          <textarea class="input" id="todo-desc" rows="2">${t.description || ''}</textarea>
        </div>
        <div class="grid-2">
          <div class="input-group">
            <label class="input-label">Subject</label>
            <select class="input" id="todo-subject">
              <option value="">None</option>
              ${subjects.map(s => `<option value="${s.name}" ${t.subject===s.name?'selected':''}>${s.name}</option>`).join('')}
            </select>
          </div>
          <div class="input-group">
            <label class="input-label">Priority</label>
            <select class="input" id="todo-priority">
              <option value="low" ${t.priority==='low'?'selected':''}>Low</option>
              <option value="medium" ${t.priority==='medium'?'selected':''}>Medium</option>
              <option value="high" ${t.priority==='high'?'selected':''}>High</option>
            </select>
          </div>
        </div>
        <div class="input-group">
          <label class="input-label">Due Date</label>
          <input type="date" class="input" id="todo-due" value="${t.dueDate || ''}">
        </div>
      </div>
      <div class="modal-footer">
        <button class="btn btn-secondary" onclick="UI.closeModal()">Cancel</button>
        <button class="btn btn-primary" onclick="Todos.update('${id}')">Save Changes</button>
      </div>
    `);
  };

  const save = () => {
    const title = document.getElementById('todo-title')?.value.trim();
    if (!title) return UI.toast('Please enter a task title', 'warning');
    Store.addTodo({
      title,
      description: document.getElementById('todo-desc')?.value.trim(),
      subject: document.getElementById('todo-subject')?.value,
      priority: document.getElementById('todo-priority')?.value,
      dueDate: document.getElementById('todo-due')?.value,
    });
    UI.closeModal();
    UI.toast('Task added!', 'success');
    render();
  };

  const update = (id) => {
    const title = document.getElementById('todo-title')?.value.trim();
    if (!title) return UI.toast('Please enter a task title', 'warning');
    Store.updateTodo(id, {
      title,
      description: document.getElementById('todo-desc')?.value.trim(),
      subject: document.getElementById('todo-subject')?.value,
      priority: document.getElementById('todo-priority')?.value,
      dueDate: document.getElementById('todo-due')?.value,
    });
    UI.closeModal();
    UI.toast('Task updated!', 'success');
    render();
  };

  const del = async (id) => {
    const ok = await UI.confirm('Delete this task? This cannot be undone.', 'Delete Task');
    if (!ok) return;
    Store.deleteTodo(id);
    UI.toast('Task deleted', 'info');
    render();
  };

  return { render, toggle, togglePin, openAddModal, openEditModal, save, update, delete: del, setFilter, onSearch };
})();
