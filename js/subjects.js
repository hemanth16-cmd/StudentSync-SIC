/* ============================================
   SUBJECTS.JS — Subject Management
   ============================================ */

const Subjects = (() => {
  const COLORS = ['#6366f1','#8b5cf6','#06b6d4','#22c55e','#f59e0b','#ef4444','#ec4899','#f97316','#14b8a6','#3b82f6'];
  const EMOJIS = ['📚','🔬','🧮','📐','🎨','💻','📖','⚗️','🌍','🎵','🏋️','📊','🔭','✏️','🧠'];

  let selectedColor = COLORS[0];
  let selectedEmoji = EMOJIS[0];

  const render = () => {
    const subjects = Store.getSubjects();
    UI.setHTML('#page-subjects', `
      <div class="page-header flex-between">
        <div>
          <h2 class="page-title">Subjects</h2>
          <p class="page-subtitle">${subjects.length} subjects this semester</p>
        </div>
        <button class="btn btn-primary" onclick="Subjects.openAddModal()">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
          Add Subject
        </button>
      </div>

      ${subjects.length === 0 ? `
        <div class="empty-state">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M2 3h6a4 4 0 014 4v14a3 3 0 00-3-3H2z"/><path d="M22 3h-6a4 4 0 00-4 4v14a3 3 0 013-3h7z"/></svg>
          <h3>No subjects yet</h3>
          <p>Add your subjects to track attendance, assignments, and grades</p>
          <button class="btn btn-primary mt-12" onclick="Subjects.openAddModal()">+ Add Subject</button>
        </div>
      ` : `
        <div class="grid-auto stagger-children">
          ${subjects.map(s => subjectCard(s)).join('')}
        </div>
      `}
    `);
  };

  const subjectCard = (s) => {
    const attStats = Store.getAttendanceStats(s.id);
    const assignments = Store.getAssignments().filter(a => a.subjectId === s.id || a.subject === s.name);
    const pending = assignments.filter(a => a.status !== 'submitted' && a.status !== 'graded').length;

    return `
      <div class="card card-hover" style="border-top:3px solid ${s.color};padding:20px;" onclick="Subjects.openDetail('${s.id}')">
        <div class="flex-between mb-16">
          <div class="flex gap-12 items-center">
            <div style="width:44px;height:44px;border-radius:var(--r-lg);background:${s.color}22;display:flex;align-items:center;justify-content:center;font-size:1.4rem;">${s.emoji}</div>
            <div>
              <div style="font-weight:700;font-size:1rem;">${s.name}</div>
              ${s.code ? `<div class="text-xs text-dimmed">${s.code}</div>` : ''}
            </div>
          </div>
          <div class="flex gap-6">
            <button class="btn-icon" onclick="event.stopPropagation();Subjects.openEditModal('${s.id}')" title="Edit">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="width:14px;height:14px;"><path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
            </button>
            <button class="btn-icon" onclick="event.stopPropagation();Subjects.delete('${s.id}')" style="color:var(--danger);" title="Delete">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="width:14px;height:14px;"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14H6L5 6"/><path d="M9 6V4h6v2"/></svg>
            </button>
          </div>
        </div>

        <div class="grid-2" style="gap:10px;margin-bottom:14px;">
          ${s.teacher ? `<div class="flex gap-6 items-center"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="width:13px;height:13px;color:var(--text-3);flex-shrink:0;"><path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2"/><circle cx="12" cy="7" r="4"/></svg><span class="text-xs text-muted truncate">${s.teacher}</span></div>` : '<div></div>'}
          ${s.room ? `<div class="flex gap-6 items-center"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="width:13px;height:13px;color:var(--text-3);flex-shrink:0;"><path d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg><span class="text-xs text-muted">${s.room}</span></div>` : '<div></div>'}
        </div>

        <div class="divider" style="margin:12px 0;"></div>

        <div class="flex gap-12">
          <div style="flex:1;text-align:center;">
            <div class="font-bold" style="font-size:1.1rem;color:${attStats.pct >= 75 ? 'var(--success)' : attStats.pct >= 60 ? 'var(--warning)' : 'var(--danger)'};">${attStats.pct}%</div>
            <div class="text-xs text-dimmed">Attendance</div>
          </div>
          <div style="width:1px;background:var(--border);"></div>
          <div style="flex:1;text-align:center;">
            <div class="font-bold" style="font-size:1.1rem;">${pending}</div>
            <div class="text-xs text-dimmed">Pending</div>
          </div>
          <div style="width:1px;background:var(--border);"></div>
          <div style="flex:1;text-align:center;">
            <div class="font-bold" style="font-size:1.1rem;">${s.credits}</div>
            <div class="text-xs text-dimmed">Credits</div>
          </div>
        </div>

        ${s.grade !== undefined && s.grade !== '' ? `
          <div class="progress-bar mt-12">
            <div class="progress-fill ${parseInt(s.grade) >= 75 ? 'success' : parseInt(s.grade) >= 50 ? 'warning' : 'danger'}" style="width:${Math.min(parseInt(s.grade) / parseInt(s.maxGrade || 100) * 100, 100)}%"></div>
          </div>
          <div class="flex-between mt-4">
            <span class="text-xs text-dimmed">Grade</span>
            <span class="text-xs font-semibold">${s.grade}${s.maxGrade ? '/'+s.maxGrade : ''}</span>
          </div>
        ` : ''}
      </div>
    `;
  };

  const openAddModal = () => {
    selectedColor = COLORS[0];
    selectedEmoji = EMOJIS[0];
    UI.openModal(`
      <div class="modal-header">
        <span class="modal-title">Add Subject</span>
        <button class="modal-close" onclick="UI.closeModal()">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
        </button>
      </div>
      <div class="modal-form">
        <div class="input-group">
          <label class="input-label">Subject Name *</label>
          <input class="input" id="sub-name" placeholder="e.g. Mathematics, Physics...">
        </div>
        <div class="grid-2">
          <div class="input-group">
            <label class="input-label">Subject Code</label>
            <input class="input" id="sub-code" placeholder="e.g. MATH101">
          </div>
          <div class="input-group">
            <label class="input-label">Credits</label>
            <input type="number" class="input" id="sub-credits" value="3" min="1" max="10">
          </div>
        </div>
        <div class="grid-2">
          <div class="input-group">
            <label class="input-label">Teacher</label>
            <input class="input" id="sub-teacher" placeholder="Teacher name">
          </div>
          <div class="input-group">
            <label class="input-label">Room</label>
            <input class="input" id="sub-room" placeholder="Room number">
          </div>
        </div>
        <div class="input-group">
          <label class="input-label">Color</label>
          <div class="color-picker-row" id="color-picker">
            ${COLORS.map(c => `<div class="color-swatch ${c===selectedColor?'selected':''}" style="background:${c}" onclick="Subjects.pickColor('${c}')"></div>`).join('')}
          </div>
        </div>
        <div class="input-group">
          <label class="input-label">Emoji</label>
          <div class="flex flex-wrap gap-8" id="emoji-picker">
            ${EMOJIS.map(e => `<button class="btn-icon" style="width:36px;height:36px;font-size:1.1rem;${e===selectedEmoji?'background:var(--accent-dim);border-color:var(--border-accent);':''}" onclick="Subjects.pickEmoji('${e}')">${e}</button>`).join('')}
          </div>
        </div>
      </div>
      <div class="modal-footer">
        <button class="btn btn-secondary" onclick="UI.closeModal()">Cancel</button>
        <button class="btn btn-primary" onclick="Subjects.save()">Add Subject</button>
      </div>
    `);
  };

  const openEditModal = (id) => {
    const s = Store.getSubjects().find(s => s.id === id);
    if (!s) return;
    selectedColor = s.color;
    selectedEmoji = s.emoji;
    UI.openModal(`
      <div class="modal-header">
        <span class="modal-title">Edit Subject</span>
        <button class="modal-close" onclick="UI.closeModal()">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
        </button>
      </div>
      <div class="modal-form">
        <div class="input-group">
          <label class="input-label">Subject Name *</label>
          <input class="input" id="sub-name" value="${s.name}">
        </div>
        <div class="grid-2">
          <div class="input-group">
            <label class="input-label">Subject Code</label>
            <input class="input" id="sub-code" value="${s.code||''}">
          </div>
          <div class="input-group">
            <label class="input-label">Credits</label>
            <input type="number" class="input" id="sub-credits" value="${s.credits||3}">
          </div>
        </div>
        <div class="grid-2">
          <div class="input-group">
            <label class="input-label">Teacher</label>
            <input class="input" id="sub-teacher" value="${s.teacher||''}">
          </div>
          <div class="input-group">
            <label class="input-label">Room</label>
            <input class="input" id="sub-room" value="${s.room||''}">
          </div>
        </div>
        <div class="grid-2">
          <div class="input-group">
            <label class="input-label">Grade Scored</label>
            <input type="number" class="input" id="sub-grade" value="${s.grade||''}" placeholder="e.g. 85">
          </div>
          <div class="input-group">
            <label class="input-label">Max Grade</label>
            <input type="number" class="input" id="sub-max-grade" value="${s.maxGrade||100}">
          </div>
        </div>
        <div class="input-group">
          <label class="input-label">Color</label>
          <div class="color-picker-row" id="color-picker">
            ${COLORS.map(c => `<div class="color-swatch ${c===selectedColor?'selected':''}" style="background:${c}" onclick="Subjects.pickColor('${c}')"></div>`).join('')}
          </div>
        </div>
        <div class="input-group">
          <label class="input-label">Emoji</label>
          <div class="flex flex-wrap gap-8" id="emoji-picker">
            ${EMOJIS.map(e => `<button class="btn-icon" style="width:36px;height:36px;font-size:1.1rem;${e===selectedEmoji?'background:var(--accent-dim);border-color:var(--border-accent);':''}" onclick="Subjects.pickEmoji('${e}')">${e}</button>`).join('')}
          </div>
        </div>
      </div>
      <div class="modal-footer">
        <button class="btn btn-secondary" onclick="UI.closeModal()">Cancel</button>
        <button class="btn btn-primary" onclick="Subjects.update('${id}')">Save Changes</button>
      </div>
    `);
  };

  const openDetail = (id) => {
    const s = Store.getSubjects().find(s => s.id === id);
    if (!s) return;
    App.navigate('attendance');
    setTimeout(() => Attendance.focusSubject(id), 100);
  };

  const pickColor = (color) => {
    selectedColor = color;
    document.querySelectorAll('.color-swatch').forEach(el => {
      el.classList.toggle('selected', el.style.background === color || el.style.backgroundColor === color);
    });
  };

  const pickEmoji = (emoji) => {
    selectedEmoji = emoji;
    document.querySelectorAll('#emoji-picker .btn-icon').forEach(el => {
      const isSelected = el.textContent === emoji;
      el.style.background = isSelected ? 'var(--accent-dim)' : '';
      el.style.borderColor = isSelected ? 'var(--border-accent)' : '';
    });
  };

  const save = () => {
    const name = document.getElementById('sub-name')?.value.trim();
    if (!name) return UI.toast('Subject name is required', 'warning');
    Store.addSubject({
      name,
      code: document.getElementById('sub-code')?.value.trim(),
      credits: parseInt(document.getElementById('sub-credits')?.value) || 3,
      teacher: document.getElementById('sub-teacher')?.value.trim(),
      room: document.getElementById('sub-room')?.value.trim(),
      color: selectedColor,
      emoji: selectedEmoji,
    });
    UI.closeModal();
    UI.toast('Subject added!', 'success');
    render();
  };

  const update = (id) => {
    const name = document.getElementById('sub-name')?.value.trim();
    if (!name) return UI.toast('Subject name is required', 'warning');
    Store.updateSubject(id, {
      name,
      code: document.getElementById('sub-code')?.value.trim(),
      credits: parseInt(document.getElementById('sub-credits')?.value) || 3,
      teacher: document.getElementById('sub-teacher')?.value.trim(),
      room: document.getElementById('sub-room')?.value.trim(),
      grade: document.getElementById('sub-grade')?.value,
      maxGrade: parseInt(document.getElementById('sub-max-grade')?.value) || 100,
      color: selectedColor,
      emoji: selectedEmoji,
    });
    UI.closeModal();
    UI.toast('Subject updated!', 'success');
    render();
  };

  const del = async (id) => {
    const ok = await UI.confirm('Delete this subject? Related data may be affected.', 'Delete Subject');
    if (!ok) return;
    Store.deleteSubject(id);
    UI.toast('Subject deleted', 'info');
    render();
  };

  return { render, openAddModal, openEditModal, openDetail, save, update, delete: del, pickColor, pickEmoji };
})();
