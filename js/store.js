/* ============================================
   STORE.JS — localStorage Abstraction Layer
   ============================================ */

const Store = (() => {
  const PREFIX = 'sa_';

  const get = (key, defaultValue = null) => {
    try {
      const raw = localStorage.getItem(PREFIX + key);
      return raw !== null ? JSON.parse(raw) : defaultValue;
    } catch (e) {
      console.warn('Store.get error:', key, e);
      return defaultValue;
    }
  };

  const set = (key, value) => {
    try {
      localStorage.setItem(PREFIX + key, JSON.stringify(value));
      return true;
    } catch (e) {
      console.warn('Store.set error:', key, e);
      return false;
    }
  };

  const remove = (key) => {
    localStorage.removeItem(PREFIX + key);
  };

  const clear = () => {
    const keys = Object.keys(localStorage).filter(k => k.startsWith(PREFIX));
    keys.forEach(k => localStorage.removeItem(k));
  };

  const exportAll = () => {
    const data = {};
    const keys = Object.keys(localStorage).filter(k => k.startsWith(PREFIX));
    keys.forEach(k => {
      try { data[k.slice(PREFIX.length)] = JSON.parse(localStorage.getItem(k)); }
      catch (e) { data[k.slice(PREFIX.length)] = localStorage.getItem(k); }
    });
    return data;
  };

  const importAll = (data) => {
    Object.entries(data).forEach(([key, value]) => set(key, value));
  };

  // ── ID Generation ──────────────────────────
  const genId = () => '_' + Math.random().toString(36).slice(2, 11) + Date.now().toString(36);

  // ── Date Helpers ───────────────────────────
  const todayStr = () => new Date().toISOString().slice(0, 10);

  const formatDate = (dateStr) => {
    if (!dateStr) return '';
    const d = new Date(dateStr + 'T00:00:00');
    return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
  };

  const daysUntil = (dateStr) => {
    if (!dateStr) return null;
    const today = new Date(); today.setHours(0, 0, 0, 0);
    const target = new Date(dateStr + 'T00:00:00');
    return Math.ceil((target - today) / 86400000);
  };

  const isToday = (dateStr) => dateStr === todayStr();
  const isPast = (dateStr) => dateStr && dateStr < todayStr();

  // ── TODOS ──────────────────────────────────
  const getTodos = () => get('todos', []);
  const saveTodos = (todos) => set('todos', todos);

  const addTodo = (todo) => {
    const todos = getTodos();
    const newTodo = {
      id: genId(),
      title: todo.title || '',
      description: todo.description || '',
      subject: todo.subject || '',
      priority: todo.priority || 'medium',
      dueDate: todo.dueDate || '',
      completed: false,
      pinned: false,
      createdAt: new Date().toISOString(),
      completedAt: null,
      tags: todo.tags || [],
    };
    todos.unshift(newTodo);
    saveTodos(todos);
    return newTodo;
  };

  const updateTodo = (id, updates) => {
    const todos = getTodos().map(t => t.id === id ? { ...t, ...updates } : t);
    saveTodos(todos);
  };

  const deleteTodo = (id) => {
    saveTodos(getTodos().filter(t => t.id !== id));
  };

  const toggleTodo = (id) => {
    const todos = getTodos();
    const todo = todos.find(t => t.id === id);
    if (!todo) return;
    todo.completed = !todo.completed;
    todo.completedAt = todo.completed ? new Date().toISOString() : null;
    saveTodos(todos);
    return todo;
  };

  // ── SUBJECTS ───────────────────────────────
  const getSubjects = () => get('subjects', []);
  const saveSubjects = (s) => set('subjects', s);

  const addSubject = (sub) => {
    const subjects = getSubjects();
    const credits = sub.credits !== undefined ? parseInt(sub.credits) : 3;
    const newSub = {
      id: genId(),
      name: sub.name || 'New Subject',
      code: sub.code || '',
      teacher: sub.teacher || '',
      credits: credits,
      totalClasses: sub.totalClasses !== undefined ? parseInt(sub.totalClasses) : (credits * 15),
      attended: sub.attended !== undefined ? parseInt(sub.attended) : 0,
      bunked: sub.bunked !== undefined ? parseInt(sub.bunked) : 0,
      room: sub.room || '',
      color: sub.color || '#6366f1',
      emoji: sub.emoji || '📚',
      grade: sub.grade || '',
      maxGrade: sub.maxGrade || 100,
      createdAt: new Date().toISOString(),
    };
    subjects.push(newSub);
    saveSubjects(subjects);
    return newSub;
  };

  const updateSubject = (id, updates) => {
    saveSubjects(getSubjects().map(s => s.id === id ? { ...s, ...updates } : s));
  };

  const deleteSubject = (id) => {
    saveSubjects(getSubjects().filter(s => s.id !== id));
  };

  // ── ASSIGNMENTS ────────────────────────────
  const getAssignments = () => get('assignments', []);
  const saveAssignments = (a) => set('assignments', a);

  const addAssignment = (asgn) => {
    const items = getAssignments();
    const newItem = {
      id: genId(),
      title: asgn.title || '',
      subject: asgn.subject || '',
      subjectId: asgn.subjectId || '',
      dueDate: asgn.dueDate || '',
      priority: asgn.priority || 'medium',
      status: asgn.status || 'not_started',
      progress: asgn.progress || 0,
      description: asgn.description || '',
      grade: asgn.grade || '',
      createdAt: new Date().toISOString(),
    };
    items.unshift(newItem);
    saveAssignments(items);
    return newItem;
  };

  const updateAssignment = (id, updates) => {
    saveAssignments(getAssignments().map(a => a.id === id ? { ...a, ...updates } : a));
  };

  const deleteAssignment = (id) => {
    saveAssignments(getAssignments().filter(a => a.id !== id));
  };

  // ── NOTES ──────────────────────────────────
  const getNotes = () => get('notes', []);
  const saveNotes = (n) => set('notes', n);

  const addNote = (note) => {
    const notes = getNotes();
    const newNote = {
      id: genId(),
      title: note.title || 'Untitled Note',
      content: note.content || '',
      subject: note.subject || '',
      tags: note.tags || [],
      color: note.color || '',
      pinned: false,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    };
    notes.unshift(newNote);
    saveNotes(notes);
    return newNote;
  };

  const updateNote = (id, updates) => {
    saveNotes(getNotes().map(n => n.id === id ? { ...n, ...updates, updatedAt: new Date().toISOString() } : n));
  };

  const deleteNote = (id) => {
    saveNotes(getNotes().filter(n => n.id !== id));
  };

  // ── ATTENDANCE ─────────────────────────────
  const getAttendance = () => get('attendance', {});
  const saveAttendance = (a) => set('attendance', a);

  const markAttendance = (subjectId, date, status) => {
    const att = getAttendance();
    if (!att[subjectId]) att[subjectId] = {};
    const oldStatus = att[subjectId][date];
    att[subjectId][date] = status; // 'present' | 'absent' | 'late'
    saveAttendance(att);

    // Sync to subject object counts
    const subjects = getSubjects();
    const s = subjects.find(sub => sub.id === subjectId);
    if (s) {
      if (s.attended === undefined) s.attended = 0;
      if (s.bunked === undefined) s.bunked = 0;
      
      const logValues = Object.values(att[subjectId]);
      s.attended = logValues.filter(v => v === 'present' || v === 'late').length;
      s.bunked = logValues.filter(v => v === 'absent').length;
      saveSubjects(subjects);
    }
  };

  const getSubjectAttendance = (subjectId) => {
    const att = getAttendance();
    return att[subjectId] || {};
  };

  const getAttendanceStats = (subjectId) => {
    const subjects = getSubjects();
    const s = subjects.find(sub => sub.id === subjectId || sub.name === subjectId);
    if (s && s.attended !== undefined && s.bunked !== undefined) {
      const attended = s.attended || 0;
      const bunked = s.bunked || 0;
      const conducted = attended + bunked;
      const pct = conducted > 0 ? Math.round((attended / conducted) * 100) : 100;
      return { total: conducted, present: attended, absent: bunked, pct };
    }
    const records = getSubjectAttendance(subjectId);
    const values = Object.values(records);
    const total = values.length;
    const present = values.filter(v => v === 'present' || v === 'late').length;
    const pct = total > 0 ? Math.round((present / total) * 100) : 100;
    return { total, present, absent: total - present, pct };
  };

  // ── HABITS ─────────────────────────────────
  const getHabits = () => get('habits', []);
  const saveHabits = (h) => set('habits', h);

  const addHabit = (habit) => {
    const habits = getHabits();
    const newHabit = {
      id: genId(),
      name: habit.name || '',
      icon: habit.icon || '⭐',
      color: habit.color || '#6366f1',
      target: habit.target || 'daily',
      completions: {},
      streak: 0,
      createdAt: new Date().toISOString(),
    };
    habits.push(newHabit);
    saveHabits(habits);
    return newHabit;
  };

  const toggleHabit = (id, date) => {
    const habits = getHabits();
    const h = habits.find(h => h.id === id);
    if (!h) return;
    h.completions[date] = !h.completions[date];
    h.streak = calcStreak(h.completions);
    saveHabits(habits);
    return h;
  };

  const calcStreak = (completions) => {
    let streak = 0;
    const d = new Date();
    while (true) {
      const key = d.toISOString().slice(0, 10);
      if (completions[key]) { streak++; d.setDate(d.getDate() - 1); }
      else break;
    }
    return streak;
  };

  // ── PLANNER ────────────────────────────────
  const getPlannerEvents = () => get('planner', []);
  const savePlannerEvents = (e) => set('planner', e);

  const addPlannerEvent = (ev) => {
    const events = getPlannerEvents();
    const newEv = {
      id: genId(),
      title: ev.title || '',
      day: ev.day, // 0-6 (Mon-Sun)
      startTime: ev.startTime || '09:00',
      endTime: ev.endTime || '10:00',
      subjectId: ev.subjectId || '',
      color: ev.color || '#6366f1',
      room: ev.room || '',
      type: ev.type || 'class', // class | event | study
    };
    events.push(newEv);
    savePlannerEvents(events);
    return newEv;
  };

  const deletePlannerEvent = (id) => {
    savePlannerEvents(getPlannerEvents().filter(e => e.id !== id));
  };

  // ── SLEEP ──────────────────────────────────
  const getSleepLogs = () => get('sleep', []);
  const saveSleepLogs = (s) => set('sleep', s);

  const addSleepLog = (log) => {
    const logs = getSleepLogs();
    const newLog = {
      id: genId(),
      date: log.date || todayStr(),
      bedtime: log.bedtime || '',
      wakeTime: log.wakeTime || '',
      duration: log.duration || 0,
      quality: log.quality || 3, // 1-5
      notes: log.notes || '',
    };
    logs.unshift(newLog);
    saveSleepLogs(logs);
    return newLog;
  };

  const deleteSleepLog = (id) => {
    saveSleepLogs(getSleepLogs().filter(l => l.id !== id));
  };

  // ── DIET ───────────────────────────────────
  const getDietLogs = () => get('diet', []);
  const saveDietLogs = (d) => set('diet', d);

  const addDietEntry = (entry) => {
    const logs = getDietLogs();
    const newEntry = {
      id: genId(),
      date: entry.date || todayStr(),
      meal: entry.meal || 'breakfast', // breakfast|lunch|dinner|snack
      name: entry.name || '',
      calories: entry.calories || 0,
      protein: entry.protein || 0,
      carbs: entry.carbs || 0,
      fat: entry.fat || 0,
    };
    logs.unshift(newEntry);
    saveDietLogs(logs);
    return newEntry;
  };

  const deleteDietEntry = (id) => {
    saveDietLogs(getDietLogs().filter(e => e.id !== id));
  };

  // ── WORKOUT ────────────────────────────────
  const getWorkouts = () => get('workouts', []);
  const saveWorkouts = (w) => set('workouts', w);

  const addWorkout = (w) => {
    const workouts = getWorkouts();
    const newW = {
      id: genId(),
      date: w.date || todayStr(),
      type: w.type || 'strength', // strength|cardio|yoga|sports|other
      name: w.name || '',
      duration: w.duration || 0,
      calories: w.calories || 0,
      exercises: w.exercises || [],
      notes: w.notes || '',
    };
    workouts.unshift(newW);
    saveWorkouts(workouts);
    return newW;
  };

  const deleteWorkout = (id) => {
    saveWorkouts(getWorkouts().filter(w => w.id !== id));
  };

  // ── EXPENSES ───────────────────────────────
  const getExpenses = () => get('expenses', []);
  const saveExpenses = (e) => set('expenses', e);

  const addExpense = (exp) => {
    const expenses = getExpenses();
    const newExp = {
      id: genId(),
      date: exp.date || todayStr(),
      type: exp.type || 'expense', // income|expense
      category: exp.category || 'other',
      description: exp.description || '',
      amount: parseFloat(exp.amount) || 0,
    };
    expenses.unshift(newExp);
    saveExpenses(expenses);
    return newExp;
  };

  const deleteExpense = (id) => {
    saveExpenses(getExpenses().filter(e => e.id !== id));
  };

  // ── SETTINGS ───────────────────────────────
  const getSettings = () => get('settings', {
    name: 'Student',
    college: '',
    theme: 'dark',
    accentColor: '#6366f1',
    gpaScale: 10,
    semesterStart: '',
    dailyGoalHours: 6,
    calorieGoal: 2000,
    sleepGoal: 8,
    budgetMonthly: 5000,
  });

  const saveSettings = (s) => set('settings', s);
  const updateSettings = (updates) => saveSettings({ ...getSettings(), ...updates });

  // ── STREAK ─────────────────────────────────
  const getStreak = () => {
    const data = get('streak', { count: 0, lastDate: '' });
    const today = todayStr();
    const yesterday = new Date(); yesterday.setDate(yesterday.getDate() - 1);
    const yStr = yesterday.toISOString().slice(0, 10);
    if (data.lastDate === today) return data.count;
    if (data.lastDate === yStr) return data.count;
    return 0;
  };

  const updateStreak = () => {
    const today = todayStr();
    const data = get('streak', { count: 0, lastDate: '' });
    const yesterday = new Date(); yesterday.setDate(yesterday.getDate() - 1);
    const yStr = yesterday.toISOString().slice(0, 10);

    if (data.lastDate === today) return data.count;
    if (data.lastDate === yStr) {
      const newCount = data.count + 1;
      set('streak', { count: newCount, lastDate: today });
      return newCount;
    }
    set('streak', { count: 1, lastDate: today });
    return 1;
  };

  // ── DAILY GOALS ────────────────────────────
  const getDailyGoals = () => get('daily_goals', []);
  const saveDailyGoals = (g) => set('daily_goals', g);

  const addDailyGoal = (goal) => {
    const goals = getDailyGoals();
    goals.push({ id: genId(), text: goal, completed: false, date: todayStr() });
    saveDailyGoals(goals);
  };

  const toggleDailyGoal = (id) => {
    const goals = getDailyGoals().map(g => g.id === id ? { ...g, completed: !g.completed } : g);
    saveDailyGoals(goals);
  };

  const getTodayGoals = () => getDailyGoals().filter(g => g.date === todayStr());

  return {
    get, set, remove, clear, exportAll, importAll,
    genId, todayStr, formatDate, daysUntil, isToday, isPast,
    // Todos
    getTodos, addTodo, updateTodo, deleteTodo, toggleTodo,
    // Subjects
    getSubjects, addSubject, updateSubject, deleteSubject,
    // Assignments
    getAssignments, addAssignment, updateAssignment, deleteAssignment,
    // Notes
    getNotes, addNote, updateNote, deleteNote,
    // Attendance
    getAttendance, markAttendance, getSubjectAttendance, getAttendanceStats,
    // Habits
    getHabits, addHabit, toggleHabit, saveHabits,
    // Planner
    getPlannerEvents, addPlannerEvent, deletePlannerEvent,
    // Sleep
    getSleepLogs, addSleepLog, deleteSleepLog,
    // Diet
    getDietLogs, addDietEntry, deleteDietEntry,
    // Workout
    getWorkouts, addWorkout, deleteWorkout,
    // Expenses
    getExpenses, addExpense, deleteExpense,
    // Settings
    getSettings, saveSettings, updateSettings,
    // Streak
    getStreak, updateStreak,
    // Daily Goals
    getDailyGoals, addDailyGoal, toggleDailyGoal, getTodayGoals, saveDailyGoals,
  };
})();
