/* ============================================
   ASSIGNMENTS.JS — Assignment Tracker
   ============================================ */

const Assignments = (() => {
  let filter = { status: 'all', priority: 'all', subject: 'all' };

  const STATUS_OPTIONS = [
    { value: 'not_started', label: 'Not Started' },
    { value: 'in_progress', label: 'In Progress' },
    { value: 'submitted', label: 'Submitted' },
    { value: 'graded', label: 'Graded' },
  ];

  const render = () => {
    const items = getFiltered();
    const subjects = Store.getSubjects();
    const overdue = Store.getAssignments().filter(a => Store.isPast(a.dueDate) && a.status !== 'submitted' && a.status !== 'graded').length;

    UI.setHTML('#page-assignments', `
      <div class="page-header flex-between">
        <div>
          <h2 class="page-title">Assignments</h2>
          <p class="page-subtitle">${overdue > 0 ? `<span class="text-danger">${overdue} overdue · </span>` : ''}${Store.getAssignments().filter(a=>a.status==='not_started'||a.status==='in_progress').length} pending</p>
        </div>
        <button class="btn btn-primary" onclick="Assignments.openAddModal()">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
          New Assignment
        </button>
      </div>

      <div class="card mb-20" style="padding:14px 18px;">
        <div class="flex gap-12 flex-wrap items-center">
          <select class="input" style="width:auto;" onchange="Assignments.setFilter('status',this.value)">
            <option value="all">All Status</option>
            ${STATUS_OPTIONS.map(s=>`<option value="${s.value}" ${filter.status===s.value?'selected':''}>${s.label}</option>`).join('')}
          </select>
          <select class="input" style="width:auto;" onchange="Assignments.setFilter('priority',this.value)">
            <option value="all">All Priority</option>
            <option value="high" ${filter.priority==='high'?'selected':''}>High</option>
            <option value="medium" ${filter.priority==='medium'?'selected':''}>Medium</option>
            <option value="low" ${filter.priority==='low'?'selected':''}>Low</option>
          </select>
          <select class="input" style="width:auto;" onchange="Assignments.setFilter('subject',this.value)">
            <option value="all">All Subjects</option>
            ${subjects.map(s=>`<option value="${s.name}" ${filter.subject===s.name?'selected':''}>${s.name}</option>`).join('')}
          </select>
        </div>
      </div>

      ${items.length === 0 ? `
        <div class="empty-state">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M9 11l3 3L22 4"/><path d="M21 12v7a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2h11"/></svg>
          <h3>No assignments found</h3>
          <p>Track your assignments to stay on top of your work</p>
          <button class="btn btn-primary mt-12" onclick="Assignments.openAddModal()">+ Add Assignment</button>
        </div>
      ` : `
        <div class="flex-col gap-12 stagger-children">
          ${items.map(a => assignmentCard(a)).join('')}
        </div>
      `}
    `);
  };

  const assignmentCard = (a) => {
    const subjectColor = UI.subjectColor(a.subjectId || a.subject);
    const isOverdue = Store.isPast(a.dueDate) && a.status !== 'submitted' && a.status !== 'graded';
    return `
      <div class="card" style="border-left:3px solid ${isOverdue ? 'var(--danger)' : subjectColor};padding:16px 20px;">
        <div class="flex-between mb-8">
          <div class="flex gap-10 items-center flex-wrap">
            <span style="font-weight:600;font-size:0.95rem;">${a.title}</span>
            ${UI.priorityBadge(a.priority)}
            ${UI.statusBadge(a.status)}
            ${isOverdue ? `<span class="badge badge-danger">Overdue</span>` : ''}
          </div>
          <div class="flex gap-6">
            <button class="btn-icon" onclick="Assignments.openEditModal('${a.id}')">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="width:14px;height:14px;"><path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
            </button>
            <button class="btn-icon" onclick="Assignments.delete('${a.id}')" style="color:var(--danger);">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="width:14px;height:14px;"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14H6L5 6"/><path d="M9 6V4h6v2"/></svg>
            </button>
          </div>
        </div>
        <div class="flex gap-16 items-center flex-wrap text-sm text-muted mb-10">
          ${a.subject ? `<span style="color:${subjectColor};font-weight:500;">📚 ${a.subject}</span>` : ''}
          ${a.dueDate ? `<span>${UI.daysUntilLabel(a.dueDate)}</span>` : ''}
          ${a.grade ? `<span class="text-success font-semibold">Grade: ${a.grade}</span>` : ''}
        </div>
        ${a.description ? `<p class="text-sm text-muted mb-10">${a.description}</p>` : ''}
        ${a.status === 'in_progress' ? `
          <div class="flex gap-10 items-center">
            <div class="progress-bar" style="flex:1;"><div class="progress-fill warning" style="width:${a.progress||0}%"></div></div>
            <span class="text-xs text-muted">${a.progress||0}%</span>
            <input type="range" min="0" max="100" value="${a.progress||0}" style="width:80px;" oninput="Assignments.updateProgress('${a.id}',this.value)" onchange="Assignments.updateProgress('${a.id}',this.value)">
          </div>
        ` : ''}
        <div class="flex gap-8 mt-10 flex-wrap">
          ${STATUS_OPTIONS.filter(s=>s.value!==a.status).map(s=>`
            <button class="btn btn-secondary btn-sm" onclick="Assignments.setStatus('${a.id}','${s.value}')">→ ${s.label}</button>
          `).join('')}
        </div>
      </div>
    `;
  };

  const getFiltered = () => {
    let items = Store.getAssignments();
    if (filter.status !== 'all') items = items.filter(a => a.status === filter.status);
    if (filter.priority !== 'all') items = items.filter(a => a.priority === filter.priority);
    if (filter.subject !== 'all') items = items.filter(a => a.subject === filter.subject);
    items.sort((a, b) => {
      const pOrder = { high: 0, medium: 1, low: 2 };
      if (a.dueDate && b.dueDate) return a.dueDate.localeCompare(b.dueDate);
      return (pOrder[a.priority]||1) - (pOrder[b.priority]||1);
    });
    return items;
  };

  const setFilter = (key, val) => { filter[key] = val; render(); };

  const setStatus = (id, status) => {
    Store.updateAssignment(id, { status });
    render();
    UI.toast(`Status updated to ${status.replace('_',' ')}`, 'success');
  };

  const updateProgress = (id, val) => {
    Store.updateAssignment(id, { progress: parseInt(val) });
    const bar = document.querySelector(`#asgn-prog-${id}`);
    if (bar) bar.style.width = val + '%';
  };

  const openAddModal = () => {
    const subjects = Store.getSubjects();
    UI.openModal(`
      <div class="modal-header">
        <span class="modal-title">New Assignment</span>
        <button class="modal-close" onclick="UI.closeModal()"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg></button>
      </div>
      <div class="modal-form">
        <div class="input-group">
          <label class="input-label">Title *</label>
          <input class="input" id="asgn-title" placeholder="Assignment title">
        </div>
        <div class="grid-2">
          <div class="input-group">
            <label class="input-label">Subject</label>
            <select class="input" id="asgn-subject">
              <option value="">None</option>
              ${subjects.map(s=>`<option value="${s.name}" data-id="${s.id}">${s.name}</option>`).join('')}
            </select>
          </div>
          <div class="input-group">
            <label class="input-label">Priority</label>
            <select class="input" id="asgn-priority">
              <option value="low">Low</option>
              <option value="medium" selected>Medium</option>
              <option value="high">High</option>
            </select>
          </div>
        </div>
        <div class="grid-2">
          <div class="input-group">
            <label class="input-label">Due Date</label>
            <input type="date" class="input" id="asgn-due">
          </div>
          <div class="input-group">
            <label class="input-label">Status</label>
            <select class="input" id="asgn-status">
              ${STATUS_OPTIONS.map(s=>`<option value="${s.value}">${s.label}</option>`).join('')}
            </select>
          </div>
        </div>
        <div class="input-group">
          <label class="input-label">Description</label>
          <textarea class="input" id="asgn-desc" rows="2" placeholder="Details, requirements..."></textarea>
        </div>
      </div>
      <div class="modal-footer">
        <button class="btn btn-secondary" onclick="UI.closeModal()">Cancel</button>
        <button class="btn btn-primary" onclick="Assignments.save()">Add Assignment</button>
      </div>
    `);
  };

  const openEditModal = (id) => {
    const a = Store.getAssignments().find(a=>a.id===id);
    if (!a) return;
    const subjects = Store.getSubjects();
    UI.openModal(`
      <div class="modal-header">
        <span class="modal-title">Edit Assignment</span>
        <button class="modal-close" onclick="UI.closeModal()"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg></button>
      </div>
      <div class="modal-form">
        <div class="input-group">
          <label class="input-label">Title *</label>
          <input class="input" id="asgn-title" value="${a.title}">
        </div>
        <div class="grid-2">
          <div class="input-group">
            <label class="input-label">Subject</label>
            <select class="input" id="asgn-subject">
              <option value="">None</option>
              ${subjects.map(s=>`<option value="${s.name}" ${a.subject===s.name?'selected':''}>${s.name}</option>`).join('')}
            </select>
          </div>
          <div class="input-group">
            <label class="input-label">Priority</label>
            <select class="input" id="asgn-priority">
              <option value="low" ${a.priority==='low'?'selected':''}>Low</option>
              <option value="medium" ${a.priority==='medium'?'selected':''}>Medium</option>
              <option value="high" ${a.priority==='high'?'selected':''}>High</option>
            </select>
          </div>
        </div>
        <div class="grid-2">
          <div class="input-group">
            <label class="input-label">Due Date</label>
            <input type="date" class="input" id="asgn-due" value="${a.dueDate||''}">
          </div>
          <div class="input-group">
            <label class="input-label">Status</label>
            <select class="input" id="asgn-status">
              ${STATUS_OPTIONS.map(s=>`<option value="${s.value}" ${a.status===s.value?'selected':''}>${s.label}</option>`).join('')}
            </select>
          </div>
        </div>
        <div class="grid-2">
          <div class="input-group">
            <label class="input-label">Grade</label>
            <input class="input" id="asgn-grade" value="${a.grade||''}" placeholder="e.g. 92/100">
          </div>
          <div class="input-group">
            <label class="input-label">Progress %</label>
            <input type="number" class="input" id="asgn-progress" value="${a.progress||0}" min="0" max="100">
          </div>
        </div>
        <div class="input-group">
          <label class="input-label">Description</label>
          <textarea class="input" id="asgn-desc" rows="2">${a.description||''}</textarea>
        </div>
      </div>
      <div class="modal-footer">
        <button class="btn btn-secondary" onclick="UI.closeModal()">Cancel</button>
        <button class="btn btn-primary" onclick="Assignments.update('${id}')">Save Changes</button>
      </div>
    `);
  };

  const save = () => {
    const title = document.getElementById('asgn-title')?.value.trim();
    if (!title) return UI.toast('Title required', 'warning');
    const subjectEl = document.getElementById('asgn-subject');
    const subjectName = subjectEl?.value;
    const subjectId = subjectEl?.options[subjectEl.selectedIndex]?.dataset?.id || '';
    Store.addAssignment({
      title,
      subject: subjectName,
      subjectId,
      priority: document.getElementById('asgn-priority')?.value,
      dueDate: document.getElementById('asgn-due')?.value,
      status: document.getElementById('asgn-status')?.value,
      description: document.getElementById('asgn-desc')?.value.trim(),
    });
    UI.closeModal();
    UI.toast('Assignment added!', 'success');
    render();
  };

  const update = (id) => {
    const title = document.getElementById('asgn-title')?.value.trim();
    if (!title) return UI.toast('Title required', 'warning');
    Store.updateAssignment(id, {
      title,
      subject: document.getElementById('asgn-subject')?.value,
      priority: document.getElementById('asgn-priority')?.value,
      dueDate: document.getElementById('asgn-due')?.value,
      status: document.getElementById('asgn-status')?.value,
      grade: document.getElementById('asgn-grade')?.value,
      progress: parseInt(document.getElementById('asgn-progress')?.value)||0,
      description: document.getElementById('asgn-desc')?.value.trim(),
    });
    UI.closeModal();
    UI.toast('Assignment updated!', 'success');
    render();
  };

  const del = async (id) => {
    const ok = await UI.confirm('Delete this assignment?', 'Delete Assignment');
    if (!ok) return;
    Store.deleteAssignment(id);
    UI.toast('Deleted', 'info');
    render();
  };

  return { render, setFilter, setStatus, updateProgress, openAddModal, openEditModal, save, update, delete: del };
})();
