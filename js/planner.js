/* ============================================
   PLANNER.JS — Weekly Timetable
   ============================================ */

const Planner = (() => {
  const DAYS = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'];
  const HOURS = Array.from({length:16}, (_,i) => i + 7); // 7am - 10pm

  const render = () => {
    const events = Store.getPlannerEvents();
    const subjects = Store.getSubjects();
    const todayIdx = (new Date().getDay() + 6) % 7; // 0=Mon

    UI.setHTML('#page-planner', `
      <div class="page-header flex-between">
        <div>
          <h2 class="page-title">Weekly Planner</h2>
          <p class="page-subtitle">Your class schedule & events</p>
        </div>
        <button class="btn btn-primary" onclick="Planner.openAddModal()">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
          Add Event
        </button>
      </div>

      <div class="card" style="padding:0;overflow:hidden;overflow-x:auto;">
        <!-- Day Headers -->
        <div style="display:grid;grid-template-columns:60px repeat(7,1fr);border-bottom:1px solid var(--border);">
          <div style="padding:12px 8px;"></div>
          ${DAYS.map((d,i) => `
            <div style="padding:12px 8px;text-align:center;border-left:1px solid var(--border);background:${i===todayIdx?'var(--accent-dim)':''};">
              <div style="font-size:0.7rem;text-transform:uppercase;letter-spacing:0.06em;color:${i===todayIdx?'var(--accent-light)':'var(--text-3)'};">${d.slice(0,3)}</div>
            </div>
          `).join('')}
        </div>

        <!-- Time Grid -->
        ${HOURS.map(hour => {
          const timeStr = `${hour.toString().padStart(2,'0')}:00`;
          return `
            <div style="display:grid;grid-template-columns:60px repeat(7,1fr);border-bottom:1px solid var(--border);">
              <div style="padding:8px 8px;font-size:0.65rem;color:var(--text-3);text-align:right;padding-right:10px;line-height:1;">${hour > 12 ? (hour-12)+'pm' : hour === 12 ? '12pm' : hour+'am'}</div>
              ${DAYS.map((d,dayIdx) => {
                const slotEvents = events.filter(e => e.day === dayIdx && e.startTime.startsWith(hour.toString().padStart(2,'0')));
                return `
                  <div style="border-left:1px solid var(--border);min-height:48px;padding:3px;background:${dayIdx===todayIdx?'rgba(99,102,241,0.02)':''};position:relative;">
                    ${slotEvents.map(ev => `
                      <div onclick="Planner.deleteEvent('${ev.id}')" style="background:${ev.color}22;border-left:3px solid ${ev.color};border-radius:4px;padding:4px 6px;margin-bottom:2px;cursor:pointer;font-size:0.7rem;font-weight:600;color:${ev.color};" title="${ev.title} (${ev.startTime}-${ev.endTime}) — click to delete">
                        <div style="overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">${ev.title}</div>
                        <div style="font-weight:400;opacity:0.7;">${ev.startTime}-${ev.endTime}${ev.room?' · '+ev.room:''}</div>
                      </div>
                    `).join('')}
                  </div>
                `;
              }).join('')}
            </div>
          `;
        }).join('')}
      </div>
    `);
  };

  const openAddModal = () => {
    const subjects = Store.getSubjects();
    UI.openModal(`
      <div class="modal-header">
        <span class="modal-title">Add Event / Class</span>
        <button class="modal-close" onclick="UI.closeModal()"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg></button>
      </div>
      <div class="modal-form">
        <div class="input-group">
          <label class="input-label">Title *</label>
          <input class="input" id="plan-title" placeholder="e.g. Mathematics Lecture">
        </div>
        <div class="input-group">
          <label class="input-label">Day</label>
          <select class="input" id="plan-day">
            ${DAYS.map((d,i)=>`<option value="${i}">${d}</option>`).join('')}
          </select>
        </div>
        <div class="grid-2">
          <div class="input-group">
            <label class="input-label">Start Time</label>
            <input type="time" class="input" id="plan-start" value="09:00">
          </div>
          <div class="input-group">
            <label class="input-label">End Time</label>
            <input type="time" class="input" id="plan-end" value="10:00">
          </div>
        </div>
        <div class="grid-2">
          <div class="input-group">
            <label class="input-label">Subject (optional)</label>
            <select class="input" id="plan-subject">
              <option value="">None</option>
              ${subjects.map(s=>`<option value="${s.id}" data-color="${s.color}">${s.name}</option>`).join('')}
            </select>
          </div>
          <div class="input-group">
            <label class="input-label">Room</label>
            <input class="input" id="plan-room" placeholder="Room number">
          </div>
        </div>
        <div class="input-group">
          <label class="input-label">Type</label>
          <select class="input" id="plan-type">
            <option value="class">Class</option>
            <option value="study">Study Session</option>
            <option value="event">Event</option>
          </select>
        </div>
      </div>
      <div class="modal-footer">
        <button class="btn btn-secondary" onclick="UI.closeModal()">Cancel</button>
        <button class="btn btn-primary" onclick="Planner.save()">Add to Planner</button>
      </div>
    `);
  };

  const save = () => {
    const title = document.getElementById('plan-title')?.value.trim();
    if (!title) return UI.toast('Title required', 'warning');
    const subjectEl = document.getElementById('plan-subject');
    const subjectId = subjectEl?.value;
    const subjectColor = subjectEl?.options[subjectEl.selectedIndex]?.dataset?.color;
    Store.addPlannerEvent({
      title,
      day: parseInt(document.getElementById('plan-day')?.value),
      startTime: document.getElementById('plan-start')?.value,
      endTime: document.getElementById('plan-end')?.value,
      subjectId,
      color: subjectColor || '#6366f1',
      room: document.getElementById('plan-room')?.value.trim(),
      type: document.getElementById('plan-type')?.value,
    });
    UI.closeModal();
    UI.toast('Event added to planner!', 'success');
    render();
  };

  const deleteEvent = async (id) => {
    const ok = await UI.confirm('Remove this event from the planner?', 'Remove Event');
    if (!ok) return;
    Store.deletePlannerEvent(id);
    render();
  };

  return { render, openAddModal, save, deleteEvent };
})();
