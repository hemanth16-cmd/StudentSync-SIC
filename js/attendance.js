/* ============================================
   ATTENDANCE.JS — Advanced Intelligence System
   Features: 75% calculator, bunk advisor,
   timetable marking, per-subject analytics
   ============================================ */

const Attendance = (() => {
  let activeTab = 'overview';
  let selectedSubjectId = null;

  // Constants
  const THRESHOLD = 75;
  const DAYS = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'];
  const DAY_SHORT = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun'];

  const render = () => {
    const subjects = Store.getSubjects();
    UI.setHTML('#page-attendance', buildLayout(subjects));
    renderTab();
    attachTabListeners();
  };

  const buildLayout = (subjects) => `
    <div class="page-header flex-between">
      <div>
        <h2 class="page-title">Attendance <span class="gradient-text-green">Intelligence</span></h2>
        <p class="page-subtitle">Track your attendance, calculate bunks, and stay above ${THRESHOLD}%</p>
      </div>
      <div class="flex gap-10">
        <button class="btn btn-secondary btn-sm" onclick="Attendance.openMarkTodayModal()">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 11-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
          Mark Today
        </button>
        <button class="btn btn-primary btn-sm" onclick="App.navigate('subjects')">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
          Add Subject
        </button>
      </div>
    </div>

    <!-- Tabs -->
    <div class="tabs mb-20">
      <button class="tab ${activeTab==='overview'?'active':''}" data-tab="overview">📋 Overview</button>
      <button class="tab ${activeTab==='timetable'?'active':''}" data-tab="timetable">🗓️ Timetable</button>
      <button class="tab ${activeTab==='calculator'?'active':''}" data-tab="calculator">🤔 Bunk Calculator</button>
      <button class="tab ${activeTab==='analytics'?'active':''}" data-tab="analytics">📊 Analytics</button>
    </div>

    <div id="att-tab-content"></div>
  `;

  const attachTabListeners = () => {
    document.querySelectorAll('[data-tab]').forEach(btn => {
      btn.addEventListener('click', () => {
        activeTab = btn.dataset.tab;
        render();
      });
    });
  };

  const renderTab = () => {
    const subjects = Store.getSubjects();
    switch(activeTab) {
      case 'overview':    renderOverview(subjects); break;
      case 'timetable':   renderTimetable(subjects); break;
      case 'calculator':  renderBunkCalculator(subjects); break;
      case 'analytics':   renderAnalytics(subjects); break;
    }
  };

  // ════════════════════════════════════════════
  // TAB 1: OVERVIEW
  // ════════════════════════════════════════════
  const renderOverview = (subjects) => {
    const overall = calcOverall(subjects);
    UI.setHTML('#att-tab-content', `
      ${overall.total > 0 ? `
        <!-- Overall Summary Card -->
        <div class="card mb-20" style="padding:24px;background:var(--green-50);border-color:var(--green-100);">
          <div style="display:flex;align-items:center;gap:24px;flex-wrap:wrap;">
            <div class="ring-wrap" style="flex-shrink:0;">
              <svg width="100" height="100" viewBox="0 0 100 100">
                <circle cx="50" cy="50" r="42" class="ring-track" stroke="var(--border)" stroke-width="8"/>
                <circle cx="50" cy="50" r="42" class="ring-fill" stroke-width="8"
                  stroke="${overall.pct >= THRESHOLD ? 'var(--green)' : 'var(--rose)'}"
                  stroke-dasharray="${2*Math.PI*42}"
                  stroke-dashoffset="${2*Math.PI*42*(1 - overall.pct/100)}"/>
              </svg>
              <div class="ring-center">
                <span style="font-size:1.3rem;font-weight:800;font-family:var(--font-display);color:${overall.pct >= THRESHOLD ? 'var(--green)' : 'var(--rose)'};">${overall.pct}%</span>
              </div>
            </div>
            <div style="flex:1;min-width:200px;">
              <h3 style="font-size:1.2rem;font-weight:700;color:var(--text-primary);margin-bottom:4px;">
                ${overall.pct >= THRESHOLD ? '🎉 Safe Zone' : '🚨 Warning Zone'}
              </h3>
              <p style="color:var(--text-secondary);font-size:0.875rem;margin-bottom:12px;">
                Overall attendance is ${overall.pct}% across all subjects.
              </p>
              <div style="display:flex;gap:16px;flex-wrap:wrap;">
                <div><span style="font-weight:700;color:var(--text-primary);">${overall.attended}</span><span style="font-size:0.75rem;color:var(--text-secondary);"> Attended</span></div>
                <div><span style="font-weight:700;color:var(--rose);">${overall.missed}</span><span style="font-size:0.75rem;color:var(--text-secondary);"> Bunked</span></div>
                <div><span style="font-weight:700;color:var(--text-primary);">${overall.total}</span><span style="font-size:0.75rem;color:var(--text-secondary);"> Conducted</span></div>
              </div>
            </div>
          </div>
        </div>
      ` : ''}

      ${subjects.length === 0 ? `
        <div class="empty-state">
          <div class="empty-state-icon"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"/><circle cx="9" cy="7" r="4"/></svg></div>
          <h3>No subjects yet</h3>
          <p>Add subjects to calculate credits and track attendance</p>
          <button class="btn btn-primary btn-sm mt-12" onclick="App.navigate('subjects')">+ Add Subject</button>
        </div>
      ` : `
        <div class="grid-2 stagger">
          ${subjects.map(s => subjectCard(s)).join('')}
        </div>
      `}
    `);
  };

  const subjectCard = (s) => {
    const stats = calcSubjectStats(s);
    const advice = getAdvice(stats);
    const today = Store.todayStr();
    const todayStatus = (s.attendanceLog || {})[today];

    return `
      <div class="card ${advice.zone==='good'?'att-health-good':advice.zone==='warn'?'att-health-warn':'att-health-danger'}" style="padding:20px;cursor:pointer;" onclick="Attendance.openSubjectDetail('${s.id}')">
        <div style="display:flex;align-items:start;justify-content:space-between;margin-bottom:12px;">
          <div class="flex gap-10 items-center">
            <div style="width:40px;height:40px;border-radius:var(--r-md);background:${s.color}15;color:${s.color};display:flex;align-items:center;justify-content:center;font-size:1.3rem;">${s.emoji}</div>
            <div>
              <div style="font-weight:700;color:var(--text-primary);font-size:0.95rem;">${s.name}</div>
              <div class="text-xs text-dimmed">${s.code || 'No code'} · ${s.credits} Credits</div>
            </div>
          </div>
          <div class="ring-wrap" style="flex-shrink:0;">
            <svg width="56" height="56" viewBox="0 0 56 56">
              <circle cx="28" cy="28" r="23" class="ring-track" stroke="var(--border)" stroke-width="5"/>
              <circle cx="28" cy="28" r="23" class="ring-fill" stroke-width="5"
                stroke="${advice.zone==='good'?'var(--green)':advice.zone==='warn'?'var(--amber)':'var(--rose)'}"
                stroke-dasharray="${2*Math.PI*23}"
                stroke-dashoffset="${2*Math.PI*23*(1 - stats.pct/100)}"/>
            </svg>
            <div class="ring-center">
              <span style="font-size:0.78rem;font-weight:800;color:${advice.zone==='good'?'var(--green)':advice.zone==='warn'?'var(--amber)':'var(--rose)'};">${stats.pct}%</span>
            </div>
          </div>
        </div>

        <div style="margin-bottom:10px;">
          <div class="progress-bar sm"><div class="progress-fill ${advice.zone==='good'?'green':advice.zone==='warn'?'amber':'rose'}" style="width:${stats.pct}%;"></div></div>
        </div>

        <div class="flex-between text-xs text-secondary mb-12">
          <span>${stats.attended} Attended · ${stats.absent} Bunked</span>
          <span>Semester limit: ${s.totalClasses || (s.credits*15)} classes</span>
        </div>

        <!-- Smart Calculator Panel -->
        <div class="bunk-calc ${advice.zone==='good'?'':advice.zone==='warn'?'warning-zone':'danger-zone'} mb-14" style="padding:10px 12px;border-radius:var(--r-md);">
          <div style="font-size:0.8rem;font-weight:700;color:var(--text-primary);">${advice.message}</div>
          <div style="font-size:0.72rem;color:var(--text-secondary);margin-top:2px;">${advice.detail}</div>
        </div>

        <!-- Today log buttons -->
        <div style="display:flex;align-items:center;justify-content:space-between;border-top:1px solid var(--border-light);padding-top:10px;" onclick="event.stopPropagation()">
          <span style="font-size:0.75rem;color:var(--text-secondary);">Today's Class:</span>
          <div style="display:flex;gap:6px;">
            <button class="btn btn-xs ${todayStatus==='present'?'btn-green':'btn-secondary'}" onclick="Attendance.markDay('${s.id}','${today}','present')">✓ Attended</button>
            <button class="btn btn-xs ${todayStatus==='absent'?'btn-danger':'btn-secondary'}" onclick="Attendance.markDay('${s.id}','${today}','absent')">✗ Bunked</button>
          </div>
        </div>
      </div>
    `;
  };

  // ════════════════════════════════════════════
  // TAB 2: TIMETABLE
  // ════════════════════════════════════════════
  const renderTimetable = (subjects) => {
    const events = Store.getPlannerEvents();
    const today = (new Date().getDay() + 6) % 7; // 0=Mon
    const todayStr = Store.todayStr();

    UI.setHTML('#att-tab-content', `
      <div class="section-header mb-12">
        <span class="section-title">🗓️ Timetable Tracker</span>
        <button class="btn btn-primary btn-xs" onclick="Planner.openAddModal()">Add Class</button>
      </div>

      ${(() => {
        const todayEvents = events.filter(e => e.day === today).sort((a,b) => a.startTime.localeCompare(b.startTime));
        if (todayEvents.length === 0) {
          return `
            <div class="card text-center" style="padding:28px 16px;margin-bottom:20px;">
              <span style="font-size:2rem;">📭</span>
              <h3 style="font-size:0.95rem;font-weight:700;margin-top:8px;">No classes today</h3>
              <p class="text-xs text-dimmed">Use Timetable page to schedule classes</p>
            </div>
          `;
        }
        return `
          <div class="flex-col gap-8 mb-20 stagger">
            ${todayEvents.map(ev => {
              const subject = subjects.find(s => s.id === ev.subjectId || s.name === ev.title);
              const subId = subject?.id;
              const todayStatus = subId ? (subject.attendanceLog || {})[todayStr] : null;
              return `
                <div class="card timetable-slot" style="border-left-color:${ev.color};padding:12px 14px;">
                  <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px;">
                    <div>
                      <div style="font-size:0.75rem;font-weight:700;color:${ev.color};">${ev.startTime} — ${ev.endTime}</div>
                      <div style="font-size:0.875rem;font-weight:600;margin-top:2px;">${ev.title}</div>
                      ${ev.room ? `<div style="font-size:0.68rem;color:var(--text-tertiary);">📍 ${ev.room}</div>` : ''}
                    </div>
                    <div style="display:flex;gap:6px;">
                      ${subId ? `
                        <button class="btn btn-xs ${todayStatus==='present'?'btn-green':'btn-secondary'}" onclick="Attendance.markDay('${subId}','${todayStr}','present')">✓ Attended</button>
                        <button class="btn btn-xs ${todayStatus==='absent'?'btn-danger':'btn-secondary'}" onclick="Attendance.markDay('${subId}','${todayStr}','absent')">✗ Bunked</button>
                      ` : '<span style="font-size:0.72rem;color:var(--text-tertiary);">No linked subject</span>'}
                    </div>
                  </div>
                </div>
              `;
            }).join('')}
          </div>
        `;
      })()}
    `);
  };

  // ════════════════════════════════════════════
  // TAB 3: BUNK CALCULATOR
  // ════════════════════════════════════════════
  const renderBunkCalculator = (subjects) => {
    if (subjects.length === 0) {
      UI.setHTML('#att-tab-content', `<div class="empty-state"><h3>No subjects to calculate</h3></div>`);
      return;
    }

    UI.setHTML('#att-tab-content', `
      <div class="card mb-20" style="background:var(--blue-50);border-color:var(--blue-100);">
        <div style="display:flex;gap:12px;align-items:flex-start;">
          <span style="font-size:1.8rem;">🤔</span>
          <div>
            <h3 style="font-size:0.95rem;font-weight:700;color:var(--blue);">Semester Bunk Calculator</h3>
            <p style="font-size:0.82rem;color:var(--text-secondary);margin-top:2px;line-height:1.4;">
              Ensure you maintain at least ${THRESHOLD}% attendance overall. Calculates limit based on semester credit classes.
            </p>
          </div>
        </div>
      </div>

      <div class="flex-col gap-10 stagger">
        ${subjects.map(s => {
          const stats = calcSubjectStats(s);
          const advice = getAdvice(stats);
          const semTotal = s.totalClasses || (s.credits * 15);
          return `
            <div class="card" style="padding:16px;">
              <div style="display:flex;justify-content:space-between;align-items:start;margin-bottom:12px;">
                <div class="flex gap-8 items-center">
                  <span style="font-size:1.2rem;">${s.emoji}</span>
                  <div>
                    <span style="font-weight:700;font-size:0.92rem;">${s.name}</span>
                    <span class="badge badge-muted" style="margin-left:6px;font-size:0.65rem;">${s.credits} Credits</span>
                  </div>
                </div>
                <span class="badge ${advice.zone==='good'?'badge-green':advice.zone==='warn'?'badge-amber':'badge-rose'}" style="font-size:0.78rem;font-weight:700;">${stats.pct}%</span>
              </div>

              <div class="grid-3 gap-8">
                <div style="background:var(--bg-hover);border-radius:var(--r-md);padding:10px;text-align:center;">
                  <span style="font-size:1.2rem;font-weight:800;color:var(--green);">${advice.canBunk}</span>
                  <div style="font-size:0.62rem;color:var(--text-tertiary);text-transform:uppercase;margin-top:2px;">Safe Bunks</div>
                </div>
                <div style="background:var(--bg-hover);border-radius:var(--r-md);padding:10px;text-align:center;">
                  <span style="font-size:1.2rem;font-weight:800;color:${advice.needToAttend>0?'var(--orange)':'var(--text-secondary)'};">${advice.needToAttend}</span>
                  <div style="font-size:0.62rem;color:var(--text-tertiary);text-transform:uppercase;margin-top:2px;">Classes to Attend</div>
                </div>
                <div style="background:var(--bg-hover);border-radius:var(--r-md);padding:10px;text-align:center;">
                  <span style="font-size:1.2rem;font-weight:800;color:var(--text-primary);">${semTotal}</span>
                  <div style="font-size:0.62rem;color:var(--text-tertiary);text-transform:uppercase;margin-top:2px;">Total Limit</div>
                </div>
              </div>

              <!-- Manual update override -->
              <div style="display:flex;align-items:center;justify-content:space-between;margin-top:12px;border-top:1px solid var(--border-light);padding-top:10px;">
                <span style="font-size:0.7rem;color:var(--text-secondary);">Manual Log:</span>
                <div class="flex gap-4">
                  <button class="btn btn-xs btn-success" onclick="Attendance.addQuickClass('${s.id}','present')">+ Attended</button>
                  <button class="btn btn-xs btn-danger" onclick="Attendance.addQuickClass('${s.id}','absent')">+ Bunked</button>
                </div>
              </div>
            </div>
          `;
        }).join('')}
      </div>
    `);
  };

  // ════════════════════════════════════════════
  // TAB 4: ANALYTICS
  // ════════════════════════════════════════════
  const renderAnalytics = (subjects) => {
    UI.setHTML('#att-tab-content', `
      <div class="grid-2 gap-16 mb-16">
        <div class="card" style="padding:16px;">
          <div class="section-header" style="margin-bottom:10px;"><span class="section-title">Subject Standings</span></div>
          <div class="chart-container" style="height:180px;"><canvas id="att-bar-chart"></canvas></div>
        </div>
        <div class="card" style="padding:16px;">
          <div class="section-header" style="margin-bottom:10px;"><span class="section-title">Distribution</span></div>
          <div class="chart-container" style="height:180px;"><canvas id="att-pie-chart"></canvas></div>
        </div>
      </div>

      <div class="card mb-20" style="padding:16px;">
        <div class="section-header" style="margin-bottom:10px;"><span class="section-title">Last 30 Days History</span></div>
        ${subjects.map(s => renderCalendar(s)).join('<div class="divider"></div>')}
      </div>
    `);
    if (subjects.length > 0) setTimeout(() => renderCharts(subjects), 100);
  };

  const renderCalendar = (s) => {
    const log = s.attendanceLog || {};
    const last30 = [];
    for(let i=29;i>=0;i--){const d=new Date();d.setDate(d.getDate()-i);last30.push(d.toISOString().slice(0,10));}
    const stats = calcSubjectStats(s);

    return `
      <div style="padding:4px 0;">
        <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px;">
          <span style="font-size:1.1rem;">${s.emoji}</span>
          <span style="font-weight:600;font-size:0.875rem;">${s.name}</span>
          <span class="badge ${stats.pct>=THRESHOLD?'badge-green':'badge-rose'}">${stats.pct}%</span>
        </div>
        <div class="att-calendar">
          ${['M','T','W','T','F','S','S'].map(d=>`<div class="text-xs text-dimmed text-center" style="font-weight:600;">${d}</div>`).join('')}
          ${last30.map(day => {
            const status = log[day];
            const isToday = day === Store.todayStr();
            return `
              <div class="att-day ${status||'empty'} ${isToday?'today':''}"
                onclick="Attendance.cycleDay('${s.id}','${day}')"
                title="${day}">
                ${new Date(day+'T00:00:00').getDate()}
              </div>
            `;
          }).join('')}
        </div>
      </div>
    `;
  };

  const renderCharts = (subjects) => {
    if (typeof Chart === 'undefined') return;
    const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
    const gridColor = isDark ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.06)';
    const tickColor = isDark ? '#94a3b8' : '#334155';

    // Bar chart
    const barCanvas = document.getElementById('att-bar-chart');
    if (barCanvas) {
      if (barCanvas._chart) barCanvas._chart.destroy();
      barCanvas._chart = new Chart(barCanvas.getContext('2d'), {
        type: 'bar',
        data: {
          labels: subjects.map(s => s.name.slice(0,8)),
          datasets: [{
            label: 'Attendance %',
            data: subjects.map(s => calcSubjectStats(s).pct),
            backgroundColor: subjects.map(s => s.color + '80'),
            borderColor: subjects.map(s => s.color),
            borderWidth: 2, borderRadius: 6
          }]
        },
        options: {
          responsive: true, maintainAspectRatio: false,
          plugins: { legend: { display: false } },
          scales: {
            x: { grid: { color: gridColor }, ticks: { color: tickColor, font: { size: 10 } } },
            y: { grid: { color: gridColor }, ticks: { color: tickColor, font: { size: 10 } }, min:0, max:100 }
          }
        }
      });
    }

    // Pie chart
    const pieCanvas = document.getElementById('att-pie-chart');
    if (pieCanvas) {
      if (pieCanvas._chart) pieCanvas._chart.destroy();
      const good = subjects.filter(s => calcSubjectStats(s).pct >= THRESHOLD).length;
      const bad = subjects.length - good;
      pieCanvas._chart = new Chart(pieCanvas.getContext('2d'), {
        type: 'doughnut',
        data: {
          labels: ['Safe (≥75%)', 'Below 75%'],
          datasets: [{
            data: [good, bad],
            backgroundColor: ['rgba(22,163,74,0.7)','rgba(225,29,72,0.7)'],
            borderColor: ['#16a34a','#e11d48'],
            borderWidth: 2
          }]
        },
        options: {
          responsive: true, maintainAspectRatio: false,
          plugins: { legend: { labels: { color: tickColor, font: { size: 10 } } } },
          cutout: '70%'
        }
      });
    }
  };

  // ════════════════════════════════════════════
  // MATH LOGIC
  // ════════════════════════════════════════════
  const calcSubjectStats = (s) => {
    // Priority: use subject manual counts if set
    if (s.attended !== undefined && s.bunked !== undefined) {
      const attended = s.attended || 0;
      const absent = s.bunked || 0;
      const total = attended + absent;
      const pct = total > 0 ? Math.round((attended / total) * 100) : 100;
      return { attended, absent, total, pct };
    }
    // Fallback: calculate from logs
    const log = s.attendanceLog || {};
    const logValues = Object.values(log);
    const attended = logValues.filter(v => v === 'present').length;
    const absent = logValues.filter(v => v === 'absent').length;
    const total = attended + absent;
    const pct = total > 0 ? Math.round((attended / total) * 100) : 100;
    return { attended, absent, total, pct };
  };

  const calcOverall = (subjects) => {
    const totals = subjects.map(s => calcSubjectStats(s));
    const attended = totals.reduce((sum,s) => sum + s.attended, 0);
    const missed = totals.reduce((sum,s) => sum + s.absent, 0);
    const total = attended + missed;
    const pct = total > 0 ? Math.round((attended/total)*100) : 100;
    return { attended, missed, total, pct };
  };

  const getAdvice = (stats) => {
    const { attended, absent, total, pct } = stats;

    // Safe bunks consecutive: floor((attended - 0.75 * total) / 0.75)
    const canBunk = pct >= THRESHOLD && total > 0
      ? Math.max(0, Math.floor((attended - 0.75 * total) / 0.75))
      : 0;

    // Consecutive needed: ceil((0.75 * total - attended) / 0.25)
    const needToAttend = pct < THRESHOLD && total > 0
      ? Math.max(0, Math.ceil((0.75 * total - attended) / 0.25))
      : 0;

    let zone, label, message, detail;

    if (pct >= 85) {
      zone = 'good'; label = '🟢 Safe';
      message = `You can bunk ${canBunk} more classes`;
      detail = `Maintain status. Current: ${attended}/${total} classes`;
    } else if (pct >= THRESHOLD) {
      zone = 'warn'; label = '🟡 Warning';
      message = canBunk > 0 ? `${canBunk} more bunk${canBunk>1?'s':''} allowed` : 'Borderline safe — attend next class!';
      detail = `Close to dropping below ${THRESHOLD}% threshold`;
    } else {
      zone = 'danger'; label = '🔴 Critical';
      message = `Must attend next ${needToAttend} classes`;
      detail = `Recovery mode: attend continuously to reach ${THRESHOLD}%`;
    }

    return { zone, label, message, detail, canBunk, needToAttend };
  };

  // ════════════════════════════════════════════
  // ACTIONS & MODALS
  // ════════════════════════════════════════════
  const markDay = (subjectId, date, status) => {
    const subjects = Store.getSubjects();
    const subject = subjects.find(s => s.id === subjectId);
    if (!subject) return;

    if (!subject.attendanceLog) subject.attendanceLog = {};
    subject.attendanceLog[date] = status;

    // Recalculate counts
    const logValues = Object.values(subject.attendanceLog);
    subject.attended = logValues.filter(v => v === 'present').length;
    subject.bunked = logValues.filter(v => v === 'absent').length;

    Store.updateSubject(subjectId, {
      attendanceLog: subject.attendanceLog,
      attended: subject.attended,
      bunked: subject.bunked
    });

    UI.toast(`Logged ${status} for ${subject.name}`, status === 'present' ? 'success' : 'info', 1500);
    render();
  };

  const cycleDay = (subjectId, date) => {
    const subjects = Store.getSubjects();
    const subject = subjects.find(s => s.id === subjectId);
    if (!subject) return;

    if (!subject.attendanceLog) subject.attendanceLog = {};
    const cur = subject.attendanceLog[date];
    const cycle = { undefined: 'present', present: 'absent', absent: undefined };
    const next = cycle[cur];

    if (next) subject.attendanceLog[date] = next;
    else delete subject.attendanceLog[date];

    // Recalculate counts
    const logValues = Object.values(subject.attendanceLog);
    subject.attended = logValues.filter(v => v === 'present').length;
    subject.bunked = logValues.filter(v => v === 'absent').length;

    Store.updateSubject(subjectId, {
      attendanceLog: subject.attendanceLog,
      attended: subject.attended,
      bunked: subject.bunked
    });

    render();
  };

  const addQuickClass = (subjectId, status) => {
    const subjects = Store.getSubjects();
    const s = subjects.find(sub => sub.id === subjectId);
    if (!s) return;

    const attended = s.attended || 0;
    const bunked = s.bunked || 0;

    Store.updateSubject(subjectId, {
      attended: status === 'present' ? attended + 1 : attended,
      bunked: status === 'absent' ? bunked + 1 : bunked
    });

    UI.toast('Manual log updated!', 'success', 1500);
    render();
  };

  const openMarkTodayModal = () => {
    const subjects = Store.getSubjects();
    const today = Store.todayStr();
    if (subjects.length === 0) return UI.toast('Add subjects first', 'warning');

    UI.openModal(`
      <div class="modal-header">
        <span class="modal-title">Mark Today's Attendance</span>
        <button class="modal-close" onclick="UI.closeModal()"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg></button>
      </div>
      <p class="text-xs text-muted mb-16">${new Date().toLocaleDateString('en-IN',{weekday:'long',month:'long',day:'numeric'})}</p>
      <div class="flex-col gap-10">
        ${subjects.map(s => {
          const log = s.attendanceLog || {};
          const cur = log[today];
          return `
            <div class="card flex-between" style="padding:12px 14px;background:var(--bg-hover);">
              <div class="flex gap-8 items-center">
                <span style="font-size:1.1rem;">${s.emoji}</span>
                <span style="font-weight:600;font-size:0.875rem;">${s.name}</span>
              </div>
              <div class="flex gap-6">
                <button class="btn btn-xs ${cur==='present'?'btn-green':'btn-secondary'}" onclick="Attendance.markDay('${s.id}','${today}','present');UI.closeModal();Attendance.openMarkTodayModal();">✓ Attended</button>
                <button class="btn btn-xs ${cur==='absent'?'btn-danger':'btn-secondary'}" onclick="Attendance.markDay('${s.id}','${today}','absent');UI.closeModal();Attendance.openMarkTodayModal();">✗ Bunked</button>
              </div>
            </div>
          `;
        }).join('')}
      </div>
      <div class="modal-footer">
        <button class="btn btn-primary" onclick="UI.closeModal();Attendance.render()">Done</button>
      </div>
    `, { size: 'sm' });
  };

  const openSubjectDetail = (id) => {
    const s = Store.getSubjects().find(s => s.id === id);
    if (!s) return;
    const stats = calcSubjectStats(s);
    const advice = getAdvice(stats);
    const log = s.attendanceLog || {};
    const last30 = [];
    for(let i=29;i>=0;i--){const d=new Date();d.setDate(d.getDate()-i);last30.push(d.toISOString().slice(0,10));}

    UI.openModal(`
      <div class="modal-header">
        <span class="modal-title">${s.emoji} ${s.name} Details</span>
        <button class="modal-close" onclick="UI.closeModal()"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg></button>
      </div>
      
      <div class="flex gap-16 items-center mb-20 flex-wrap">
        <div class="ring-wrap" style="flex-shrink:0;">
          <svg width="76" height="76" viewBox="0 0 76 76">
            <circle cx="38" cy="38" r="32" class="ring-track" stroke="var(--border)" stroke-width="6"/>
            <circle cx="38" cy="38" r="32" class="ring-fill" stroke-width="6"
              stroke="${advice.zone==='good'?'var(--green)':advice.zone==='warn'?'var(--amber)':'var(--rose)'}"
              stroke-dasharray="${2*Math.PI*32}"
              stroke-dashoffset="${2*Math.PI*32*(1 - stats.pct/100)}"/>
          </svg>
          <div class="ring-center">
            <span style="font-size:0.95rem;font-weight:800;color:${advice.zone==='good'?'var(--green)':advice.zone==='warn'?'var(--amber)':'var(--rose)'};">${stats.pct}%</span>
          </div>
        </div>
        <div>
          <div class="badge ${advice.zone==='good'?'badge-green':advice.zone==='warn'?'badge-amber':'badge-rose'} mb-6">${advice.label}</div>
          <div style="font-size:0.875rem;font-weight:700;">${advice.message}</div>
          <div class="text-xs text-muted mt-2">${advice.detail}</div>
        </div>
      </div>

      <!-- Quick Manual Override Counts -->
      <div class="card mb-16" style="padding:14px;background:var(--bg-hover);">
        <div style="font-size:0.75rem;font-weight:700;color:var(--text-secondary);text-transform:uppercase;margin-bottom:10px;">Update Attendance Manually</div>
        <div class="grid-3 gap-8">
          <div class="input-group">
            <label class="input-label" style="font-size:0.7rem;">Attended</label>
            <input type="number" class="input" id="override-attended" value="${stats.attended}" min="0">
          </div>
          <div class="input-group">
            <label class="input-label" style="font-size:0.7rem;">Bunked</label>
            <input type="number" class="input" id="override-bunked" value="${stats.absent}" min="0">
          </div>
          <div class="input-group">
            <label class="input-label" style="font-size:0.7rem;">Total Classes</label>
            <input type="number" class="input" id="override-total" value="${s.totalClasses || (s.credits*15)}" min="0">
          </div>
        </div>
        <button class="btn btn-secondary btn-xs mt-10" style="width:100%;" onclick="Attendance.saveManualOverride('${s.id}')">Save Manual Updates</button>
      </div>

      <div class="section-header mb-8"><span class="section-title" style="font-size:0.75rem;">30-Day Check-in History</span></div>
      <div class="att-calendar mb-16">
        ${['M','T','W','T','F','S','S'].map(d=>`<div class="text-xs text-dimmed text-center">${d}</div>`).join('')}
        ${last30.map(day => {
          const status = log[day];
          const isToday = day === Store.todayStr();
          return `<div class="att-day ${status||'empty'} ${isToday?'today':''}" onclick="Attendance.cycleDay('${s.id}','${day}');UI.closeModal();Attendance.openSubjectDetail('${s.id}');" title="${day}">
            ${new Date(day+'T00:00:00').getDate()}
          </div>`;
        }).join('')}
      </div>

      <div class="modal-footer">
        <button class="btn btn-primary" onclick="UI.closeModal();Attendance.render()">Done</button>
      </div>
    `, { size: 'sm' });
  };

  const saveManualOverride = (id) => {
    const attended = parseInt(document.getElementById('override-attended')?.value) || 0;
    const bunked = parseInt(document.getElementById('override-bunked')?.value) || 0;
    const total = parseInt(document.getElementById('override-total')?.value) || 45;

    Store.updateSubject(id, {
      attended,
      bunked,
      totalClasses: total
    });

    UI.toast('Attendance stats updated!', 'success', 1500);
    UI.closeModal();
    render();
  };

  const focusSubject = (id) => {
    selectedSubjectId = id;
    activeTab = 'calculator';
    render();
  };

  return {
    render, markDay, cycleDay, addQuickClass,
    openMarkTodayModal, openSubjectDetail, saveManualOverride, focusSubject
  };
})();
