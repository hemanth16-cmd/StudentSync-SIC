/* ============================================
   NOTES.JS — Notes Manager
   ============================================ */

const Notes = (() => {
  let searchTimer = null;
  let searchQ = '';

  const NOTE_COLORS = ['', '#6366f122', '#22c55e22', '#f59e0b22', '#ef444422', '#06b6d422', '#8b5cf622'];

  const render = () => {
    let notes = Store.getNotes();
    if (searchQ) {
      const q = searchQ.toLowerCase();
      notes = notes.filter(n => n.title.toLowerCase().includes(q) || (n.content||'').toLowerCase().includes(q) || (n.tags||[]).join(' ').toLowerCase().includes(q));
    }
    const pinned = notes.filter(n => n.pinned);
    const unpinned = notes.filter(n => !n.pinned);

    UI.setHTML('#page-notes', `
      <div class="page-header flex-between">
        <div>
          <h2 class="page-title">Notes</h2>
          <p class="page-subtitle">${Store.getNotes().length} notes</p>
        </div>
        <button class="btn btn-primary" onclick="Notes.openAddModal()">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
          New Note
        </button>
      </div>

      <div class="search-bar mb-20" style="max-width:360px;">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
        <input placeholder="Search notes..." oninput="Notes.onSearch(this.value)" value="${searchQ}">
      </div>

      ${pinned.length > 0 ? `
        <div class="section-header"><span class="section-title" style="font-size:0.78rem;color:var(--text-3);text-transform:uppercase;letter-spacing:0.08em;">📌 Pinned</span></div>
        <div class="grid-auto mb-24 stagger-children">${pinned.map(n => noteCard(n)).join('')}</div>
      ` : ''}

      ${unpinned.length > 0 ? `
        ${pinned.length > 0 ? `<div class="section-header"><span class="section-title" style="font-size:0.78rem;color:var(--text-3);text-transform:uppercase;letter-spacing:0.08em;">All Notes</span></div>` : ''}
        <div class="grid-auto stagger-children">${unpinned.map(n => noteCard(n)).join('')}</div>
      ` : ''}

      ${notes.length === 0 ? `
        <div class="empty-state">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
          <h3>No notes yet</h3>
          <p>Capture your thoughts, lecture notes, and ideas here</p>
          <button class="btn btn-primary mt-12" onclick="Notes.openAddModal()">+ New Note</button>
        </div>
      ` : ''}
    `);
  };

  const noteCard = (n) => `
    <div class="card card-hover" style="${n.color ? 'background:'+n.color+';' : ''}border:1px solid var(--border);cursor:pointer;" onclick="Notes.openEdit('${n.id}')">
      <div class="flex-between mb-8">
        <span style="font-weight:600;font-size:0.9rem;">${n.pinned ? '📌 ' : ''}${n.title}</span>
        <div class="flex gap-4" onclick="event.stopPropagation()">
          <button class="btn-icon" onclick="Notes.togglePin('${n.id}')" style="width:28px;height:28px;" title="${n.pinned?'Unpin':'Pin'}">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="${n.pinned?'currentColor':'none'}" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="width:13px;height:13px;color:${n.pinned?'var(--warning)':'inherit'}"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/></svg>
          </button>
          <button class="btn-icon" onclick="Notes.delete('${n.id}')" style="width:28px;height:28px;color:var(--danger);">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="width:13px;height:13px;"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14H6L5 6"/><path d="M9 6V4h6v2"/></svg>
          </button>
        </div>
      </div>
      <p class="text-sm text-muted" style="overflow:hidden;display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;min-height:40px;">${(n.content||'').replace(/<[^>]*>/g,'').slice(0,150) || 'Empty note'}</p>
      <div class="flex-between mt-12">
        <div class="flex gap-6 flex-wrap">
          ${(n.tags||[]).slice(0,3).map(t=>`<span class="tag">${t}</span>`).join('')}
          ${n.subject ? `<span class="tag" style="color:var(--accent-light);">${n.subject}</span>` : ''}
        </div>
        <span class="text-xs text-dimmed">${UI.relativeTime(n.updatedAt)}</span>
      </div>
    </div>
  `;

  const onSearch = (val) => {
    clearTimeout(searchTimer);
    searchTimer = setTimeout(() => { searchQ = val; render(); }, 200);
  };

  const openAddModal = () => {
    const subjects = Store.getSubjects();
    UI.openModal(`
      <div class="modal-header">
        <span class="modal-title">New Note</span>
        <button class="modal-close" onclick="UI.closeModal()"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg></button>
      </div>
      <div class="modal-form">
        <div class="input-group">
          <label class="input-label">Title *</label>
          <input class="input" id="note-title" placeholder="Note title...">
        </div>
        <div class="input-group">
          <label class="input-label">Content</label>
          <textarea class="input" id="note-content" rows="5" placeholder="Write your note here..."></textarea>
        </div>
        <div class="grid-2">
          <div class="input-group">
            <label class="input-label">Subject</label>
            <select class="input" id="note-subject">
              <option value="">None</option>
              ${subjects.map(s=>`<option value="${s.name}">${s.name}</option>`).join('')}
            </select>
          </div>
          <div class="input-group">
            <label class="input-label">Tags (comma separated)</label>
            <input class="input" id="note-tags" placeholder="lecture, important...">
          </div>
        </div>
        <div class="input-group">
          <label class="input-label">Card Color</label>
          <div class="flex gap-8">
            ${NOTE_COLORS.map((c,i) => `<div onclick="document.getElementById('note-color').value='${c}';document.querySelectorAll('.nc-swatch').forEach(e=>e.style.outline='none');this.style.outline='2px solid var(--accent)'" class="nc-swatch" style="width:26px;height:26px;border-radius:6px;background:${c||'var(--bg-3)'};cursor:pointer;border:1px solid var(--border);${i===0?'outline:2px solid var(--accent)':''}"></div>`).join('')}
            <input type="hidden" id="note-color" value="">
          </div>
        </div>
      </div>
      <div class="modal-footer">
        <button class="btn btn-secondary" onclick="UI.closeModal()">Cancel</button>
        <button class="btn btn-primary" onclick="Notes.save()">Save Note</button>
      </div>
    `, { size: 'lg' });
  };

  const openEdit = (id) => {
    const n = Store.getNotes().find(n=>n.id===id);
    if (!n) return;
    const subjects = Store.getSubjects();
    UI.openModal(`
      <div class="modal-header">
        <span class="modal-title">Edit Note</span>
        <button class="modal-close" onclick="UI.closeModal()"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg></button>
      </div>
      <div class="modal-form">
        <div class="input-group">
          <label class="input-label">Title *</label>
          <input class="input" id="note-title" value="${n.title}">
        </div>
        <div class="input-group">
          <label class="input-label">Content</label>
          <textarea class="input" id="note-content" rows="7">${(n.content||'').replace(/<[^>]*>/g,'')}</textarea>
        </div>
        <div class="grid-2">
          <div class="input-group">
            <label class="input-label">Subject</label>
            <select class="input" id="note-subject">
              <option value="">None</option>
              ${subjects.map(s=>`<option value="${s.name}" ${n.subject===s.name?'selected':''}>${s.name}</option>`).join('')}
            </select>
          </div>
          <div class="input-group">
            <label class="input-label">Tags</label>
            <input class="input" id="note-tags" value="${(n.tags||[]).join(', ')}">
          </div>
        </div>
      </div>
      <div class="modal-footer">
        <button class="btn btn-secondary" onclick="UI.closeModal()">Cancel</button>
        <button class="btn btn-primary" onclick="Notes.update('${id}')">Save Changes</button>
      </div>
    `, { size: 'lg' });
  };

  const save = () => {
    const title = document.getElementById('note-title')?.value.trim();
    if (!title) return UI.toast('Title required', 'warning');
    const tags = (document.getElementById('note-tags')?.value || '').split(',').map(t=>t.trim()).filter(Boolean);
    Store.addNote({
      title,
      content: document.getElementById('note-content')?.value,
      subject: document.getElementById('note-subject')?.value,
      tags,
      color: document.getElementById('note-color')?.value,
    });
    UI.closeModal();
    UI.toast('Note saved!', 'success');
    render();
  };

  const update = (id) => {
    const title = document.getElementById('note-title')?.value.trim();
    if (!title) return UI.toast('Title required', 'warning');
    const tags = (document.getElementById('note-tags')?.value || '').split(',').map(t=>t.trim()).filter(Boolean);
    Store.updateNote(id, {
      title,
      content: document.getElementById('note-content')?.value,
      subject: document.getElementById('note-subject')?.value,
      tags,
    });
    UI.closeModal();
    UI.toast('Note updated!', 'success');
    render();
  };

  const togglePin = (id) => {
    const n = Store.getNotes().find(n=>n.id===id);
    if (n) Store.updateNote(id, { pinned: !n.pinned });
    render();
  };

  const del = async (id) => {
    const ok = await UI.confirm('Delete this note?', 'Delete Note');
    if (!ok) return;
    Store.deleteNote(id);
    UI.toast('Note deleted', 'info');
    render();
  };

  return { render, onSearch, openAddModal, openEdit, save, update, togglePin, delete: del };
})();
