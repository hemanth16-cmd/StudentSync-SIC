/* ============================================
   ATTENDANCE.JS — Attendance Tracker
   ============================================ */

const Attendance = (() => {
  let selectedSubjectId = null;

  const render = () => {
    const subjects = Store.getSubjects();
    if (!selectedSubjectId && subjects.length > 0) selectedSubjectId = subjects[0].id;

    UI.setHTML('#page-attendance', `
      <div class="page-header flex-between">
        <div>
          <h2 class="page-title">Attendance</h2>
          <p class="page-subtitle">Track your class attendance</p>
        </div>
        <button class="btn btn-primary" onclick="Subjects.openAddModal(); setTimeout(()=>App.navigate('subjects'),50)">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
          Add Subject
        </button>
      </div>

      ${subjects.length === 0 ? `
        <div class="empty-state">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 00-3-3.87"/><path d="M16 3.13a4 4 0 010 7.75"/></svg>
          <h3>No subjects added</h3>
          <p>Add subjects first to track attendance</p>
          <button class="btn btn-primary mt-12" onclick="App.navigate('subjects')">Go to Subjects</button>
        </div>
      ` : `
        <!-- Summary Cards -->
        <div class="grid-auto mb-24 stagger-children">
          ${subjects.map(s => {
            const stats = Store.getAttendanceStats(s.id);
            return `
              <div class="card ${selectedSubjectId===s.id?'glow-border':''}" style="cursor:pointer;border-top:3px solid ${s.color};" onclick="Attendance.selectSubject('${s.id}')">
                <div class="flex gap-10 items-center mb-12">
                  <span style="font-size:1.4rem;">${s.emoji}</span>
                  <div>
                    <div style="font-weight:600;font-size:0.9rem;">${s.name}</div>
                    <div class="text-xs text-dimmed">${stats.present}/${stats.total} classes</div>
                  </div>
                </div>
                <div class="attendance-meter">
                  <span class="attendance-pct ${stats.pct>=75?'good':stats.pct>=60?'okay':'bad'}">${stats.pct}%</span>
                  <div style="flex:1;">
                    <div class="progress-bar">
                      <div class="progress-fill ${stats.pct>=75?'success':stats.pct>=60?'warning':'danger'}" style="width:${stats.pct}%"></div>
                    </div>
                    <div class="text-xs text-dimmed mt-4">${stats.pct>=75?'✓ On track':stats.pct>=60?'⚠ Borderline':'✗ Below minimum'}</div>
                  </div>
                </div>
              </div>
            `;
          }).join('')}
        </div>

        <!-- Mark Attendance -->
        ${selectedSubjectId ? renderMarkAttendance() : ''}
      `}
    `);
  };

  const renderMarkAttendance = () => {
    const subject = Store.getSubjects().find(s=>s.id===selectedSubjectId);
    if (!subject) return '';
    const records = Store.getSubjectAttendance(selectedSubjectId);
    const today = Store.todayStr();

    // Generate last 30 days
    const days = [];
    for (let i = 29; i >= 0; i--) {
      const d = new Date();
      d.setDate(d.getDate() - i);
      days.push(d.toISOString().slice(0,10));
    }

    return `
      <div class="card">
        <div class="section-header mb-20">
          <span class="section-title" style="font-size:1rem;">
            <span style="font-size:1.2rem;">${subject.emoji}</span>
            ${subject.name} — Mark Attendance
          </span>
          <button class="btn btn-primary btn-sm" onclick="Attendance.markToday()">Mark Today</button>
        </div>

        <!-- Mark Today Row -->
        <div class="card mb-20" style="background:var(--bg-3);padding:16px;">
          <div class="flex gap-12 items-center flex-wrap">
            <span style="font-size:0.875rem;font-weight:500;">Today (${today}):</span>
            <button class="btn ${records[today]==='present'?'btn-success':'btn-secondary'} btn-sm" onclick="Attendance.mark('${selectedSubjectId}','${today}','present')">
              ✓ Present
            </button>
            <button class="btn ${records[today]==='absent'?'btn-danger':'btn-secondary'} btn-sm" onclick="Attendance.mark('${selectedSubjectId}','${today}','absent')">
              ✗ Absent
            </button>
            <button class="btn ${records[today]==='late'?'btn-ghost':'btn-secondary'} btn-sm" style="${records[today]==='late'?'background:var(--warning-bg);color:var(--warning);border-color:var(--warning-border);':''}" onclick="Attendance.mark('${selectedSubjectId}','${today}','late')">
              ~ Late
            </button>
          </div>
        </div>

        <!-- Calendar Grid (last 30 days) -->
        <div class="section-header mb-12">
          <span class="section-title" style="font-size:0.85rem;">Last 30 Days</span>
          <div class="flex gap-12 text-xs text-muted">
            <span>🟢 Present</span>
            <span>🔴 Absent</span>
            <span>🟡 Late</span>
          </div>
        </div>
        <div style="display:grid;grid-template-columns:repeat(7,1fr);gap:6px;">
          ${['M','T','W','T','F','S','S'].map(d=>`<div class="text-xs text-dimmed text-center">${d}</div>`).join('')}
          ${days.map(day => {
            const status = records[day];
            const isToday = day === today;
            const colorMap = { present: 'var(--success)', absent: 'var(--danger)', late: 'var(--warning)' };
            return `
              <div onclick="Attendance.cycleDay('${selectedSubjectId}','${day}')" style="
                aspect-ratio:1;border-radius:6px;display:flex;align-items:center;justify-content:center;
                font-size:0.65rem;cursor:pointer;transition:all 0.15s;
                background:${status ? colorMap[status]+'22' : 'var(--bg-4)'};
                border:1.5px solid ${isToday ? 'var(--accent)' : status ? colorMap[status]+'44' : 'transparent'};
                color:${status ? colorMap[status] : 'var(--text-3)'};
                font-weight:${isToday?'700':'400'};
              " title="${day} — ${status || 'not marked'}">
                ${new Date(day+'T00:00:00').getDate()}
              </div>
            `;
          }).join('')}
        </div>
      </div>
    `;
  };

  const selectSubject = (id) => {
    selectedSubjectId = id;
    render();
  };

  const focusSubject = (id) => {
    selectedSubjectId = id;
    render();
  };

  const mark = (subjectId, date, status) => {
    Store.markAttendance(subjectId, date, status);
    UI.toast(`Marked as ${status}`, 'success', 1500);
    render();
  };

  const markToday = () => {
    if (!selectedSubjectId) return;
    const today = Store.todayStr();
    UI.openModal(`
      <div class="modal-header">
        <span class="modal-title">Mark Today's Attendance</span>
        <button class="modal-close" onclick="UI.closeModal()"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg></button>
      </div>
      <p class="text-muted mb-20">Mark your attendance for all subjects today (${today})</p>
      <div class="flex-col gap-12">
        ${Store.getSubjects().map(s => {
          const records = Store.getSubjectAttendance(s.id);
          const current = records[today];
          return `
            <div class="flex-between card" style="padding:12px 16px;background:var(--bg-3);">
              <span style="font-weight:500;">${s.emoji} ${s.name}</span>
              <div class="flex gap-8">
                <button class="btn btn-sm ${current==='present'?'btn-success':'btn-secondary'}" onclick="Store.markAttendance('${s.id}','${today}','present');this.parentElement.querySelectorAll('.btn').forEach(b=>b.className='btn btn-sm btn-secondary');this.className='btn btn-sm btn-success'">✓</button>
                <button class="btn btn-sm ${current==='absent'?'btn-danger':'btn-secondary'}" onclick="Store.markAttendance('${s.id}','${today}','absent');this.parentElement.querySelectorAll('.btn').forEach(b=>b.className='btn btn-sm btn-secondary');this.className='btn btn-sm btn-danger'">✗</button>
                <button class="btn btn-sm ${current==='late'?'':'btn-secondary'}" style="${current==='late'?'background:var(--warning-bg);color:var(--warning);':''}
                " onclick="Store.markAttendance('${s.id}','${today}','late');this.parentElement.querySelectorAll('.btn').forEach(b=>b.className='btn btn-sm btn-secondary');this.style.background='var(--warning-bg)';this.style.color='var(--warning)'">~</button>
              </div>
            </div>
          `;
        }).join('')}
      </div>
      <div class="modal-footer">
        <button class="btn btn-primary" onclick="UI.closeModal();Attendance.render()">Done</button>
      </div>
    `, { size: 'lg' });
  };

  const cycleDay = (subjectId, date) => {
    const records = Store.getSubjectAttendance(subjectId);
    const current = records[date];
    const cycle = { undefined: 'present', present: 'absent', absent: 'late', late: undefined };
    const next = cycle[current];
    if (next) Store.markAttendance(subjectId, date, next);
    else {
      const att = Store.getAttendance();
      if (att[subjectId]) delete att[subjectId][date];
      Store.saveAttendance ? Store.saveAttendance(att) : Store.set('attendance', att);
    }
    render();
  };

  return { render, selectSubject, focusSubject, mark, markToday, cycleDay };
})();
