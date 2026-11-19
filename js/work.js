// 업무노트(work.html): 할 일·스티커 메모·필드를 localStorage에 저장하고 수첩·달력·진행 현황을 그린다
(function () {
  var KEY = 'jc-worknote-v1';
  var STATUS = [['todo', '예정'], ['doing', '진행 중'], ['done', '완료'], ['later', '연기']];
  var STATUS_NAME = Object.fromEntries(STATUS);
  var WEEK = ['일', '월', '화', '수', '목', '금', '토'];

  var $ = function (id) { return document.getElementById(id); };
  function h(tag, cls, text) {
    var el = document.createElement(tag);
    if (cls) el.className = cls;
    if (text != null) el.textContent = text;
    return el;
  }
  function iso(d) {
    return d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0');
  }
  function parse(s) { var p = s.split('-'); return new Date(+p[0], p[1] - 1, +p[2]); }
  function longDate(s) { var d = parse(s); return d.getFullYear() + '년 ' + (d.getMonth() + 1) + '월 ' + d.getDate() + '일 ' + WEEK[d.getDay()] + '요일'; }
  function uid() { return Date.now().toString(36) + Math.random().toString(36).slice(2, 7); }

  // ── 저장 ──
  function blank() { return { tasks: [], memos: [], fields: ['사무', '공무직급여', '보안'] }; }
  function valid(d) { return d && Array.isArray(d.tasks) && Array.isArray(d.memos) && Array.isArray(d.fields); }
  function load() {
    try { var d = JSON.parse(localStorage.getItem(KEY)); if (valid(d)) return d; } catch (e) {}
    return blank();
  }
  var data = load();
  var saveFailed = false;
  function save() {
    try { localStorage.setItem(KEY, JSON.stringify(data)); saveFailed = false; }
    catch (e) { saveFailed = true; }
  }

  var today = iso(new Date());
  var day = today;                       // 수첩에 펼친 날짜
  var month = parse(today); month.setDate(1); // 달력에 보이는 달

  function tasksOn(date) { return data.tasks.filter(function (t) { return t.date === date; }); }
  function count(list, st) { return list.filter(function (t) { return t.status === st; }).length; }

  // ── 그리기 ──
  function render() {
    renderSide(); renderBook(); renderCalendar(); renderFlow(); renderFields();
    if (saveFailed) $('index-list').prepend(h('li', 'wn-warn', '이 브라우저는 저장을 막고 있어 새로고침하면 사라집니다.'));
  }

  function renderSide() {
    var list = tasksOn(today);
    $('index-date').textContent = longDate(today);
    var ul = $('index-list'); ul.replaceChildren();
    [['오늘 할 일', list.length - count(list, 'done')],
     ['진행 중', count(data.tasks, 'doing')],
     ['오늘 메모', data.memos.filter(function (m) { return m.date === today; }).length]
    ].forEach(function (r) {
      var li = h('li'); li.append(h('span', null, r[0]), h('strong', null, r[1] + '건')); ul.append(li);
    });
  }

  function renderBook() {
    var list = tasksOn(day);
    $('day-label').textContent = longDate(day);
    $('day-input').value = day;
    $('book-stat').textContent = '예정 ' + count(list, 'todo') + ' · 진행 중 ' + count(list, 'doing') + ' · 완료 ' + count(list, 'done');

    var memos = $('memo-list'); memos.replaceChildren();
    data.memos.filter(function (m) { return m.date === day; }).forEach(function (m) {
      var box = h('div', 'wn-memo');
      var ta = h('textarea'); ta.value = m.text; ta.rows = 3; ta.placeholder = '여기에 메모를 적으세요';
      ta.setAttribute('aria-label', '스티커 메모');
      ta.addEventListener('input', function () { m.text = ta.value; save(); });
      var del = h('button', 'wn-memo-del', '×'); del.type = 'button'; del.setAttribute('aria-label', '메모 떼기');
      del.addEventListener('click', function () { data.memos = data.memos.filter(function (x) { return x !== m; }); save(); render(); });
      box.append(ta, del); memos.append(box);
    });
    var addCard = h('button', 'wn-memo-new', '+ 새 메모 붙이기'); addCard.type = 'button';
    addCard.addEventListener('click', addMemo);
    memos.append(addCard);

    var ul = $('today-list'); ul.replaceChildren();
    if (!list.length) ul.append(h('li', 'wn-empty', '이 날짜에 등록된 업무가 없습니다. 업무를 추가하거나 달력에서 날짜를 고르세요.'));
    list.forEach(function (t) {
      var li = h('li', 'wn-task' + (t.status === 'done' ? ' is-done' : ''));
      var cb = h('input'); cb.type = 'checkbox'; cb.checked = t.status === 'done';
      cb.setAttribute('aria-label', t.title + ' 완료');
      cb.addEventListener('change', function () { t.status = cb.checked ? 'done' : 'todo'; save(); render(); });
      var name = h('button', 'wn-task-title', t.title); name.type = 'button';
      name.addEventListener('click', function () { openTask(t); });
      var meta = h('span', 'wn-task-meta', [t.field, STATUS_NAME[t.status]].filter(Boolean).join(' · '));
      li.append(cb, name, meta); ul.append(li);
    });
  }

  function renderCalendar() {
    $('cal-title').textContent = month.getFullYear() + '년 ' + (month.getMonth() + 1) + '월';
    var grid = $('cal-grid'); grid.replaceChildren();
    WEEK.forEach(function (w, i) { grid.append(h('span', 'wn-cal-w' + (i === 0 ? ' is-sun' : ''), w)); });
    for (var i = 0; i < month.getDay(); i++) grid.append(h('span'));
    var last = new Date(month.getFullYear(), month.getMonth() + 1, 0).getDate();
    for (var d = 1; d <= last; d++) {
      var date = iso(new Date(month.getFullYear(), month.getMonth(), d));
      var n = tasksOn(date).length;
      var b = h('button', 'wn-cal-d'); b.type = 'button';
      if (date === today) b.classList.add('is-today');
      if (date === day) b.classList.add('is-sel');
      if (new Date(month.getFullYear(), month.getMonth(), d).getDay() === 0) b.classList.add('is-sun');
      b.append(h('span', null, d));
      if (n) b.append(h('small', null, n + '건'));
      b.setAttribute('aria-label', longDate(date) + ' 업무 ' + n + '건');
      b.addEventListener('click', (function (dt) { return function () { day = dt; render(); }; })(date));
      grid.append(b);
    }
    var list = tasksOn(day);
    var dd = parse(day);
    $('cal-day-label').textContent = (dd.getMonth() + 1) + '월 ' + dd.getDate() + '일 (' + WEEK[dd.getDay()] + ')';
    $('cal-day-count').textContent = list.length + '개의 업무';
    var ul = $('cal-day-list'); ul.replaceChildren();
    if (!list.length) ul.append(h('li', 'wn-empty', '등록된 업무가 없습니다.'));
    list.forEach(function (t) { ul.append(taskChip(t)); });
  }

  function taskChip(t, withStatus) {
    var li = h('li', 'wn-chip' + (t.status === 'done' ? ' is-done' : ''));
    var b = h('button', 'wn-chip-title', t.title); b.type = 'button';
    b.addEventListener('click', function () { openTask(t); });
    li.append(b);
    if (t.date) li.append(h('span', 'wn-chip-date', t.date.slice(5).replace('-', '.')));
    if (withStatus) {
      var sel = h('select'); sel.setAttribute('aria-label', t.title + ' 상태');
      STATUS.forEach(function (s) { var o = h('option', null, s[1]); o.value = s[0]; sel.append(o); });
      sel.value = t.status;
      sel.addEventListener('change', function () { t.status = sel.value; save(); render(); });
      li.append(sel);
    }
    return li;
  }

  function column(title, list, opts) {
    var col = h('div', 'wn-col');
    var head = h('div', 'wn-col-head'); head.append(h('strong', null, title), h('span', null, list.length + '건'));
    if (opts.onRemove) {
      var rm = h('button', 'wn-col-rm', '×'); rm.type = 'button'; rm.setAttribute('aria-label', title + ' 필드 삭제');
      rm.addEventListener('click', opts.onRemove); head.append(rm);
    }
    var ul = h('ul', 'wn-mini');
    if (!list.length) ul.append(h('li', 'wn-empty', '업무 없음'));
    list.forEach(function (t) { ul.append(taskChip(t, opts.withStatus)); });
    col.append(head, ul);
    if (opts.addLabel) {
      var add = h('button', 'wn-btn wn-btn-wide', opts.addLabel); add.type = 'button';
      add.addEventListener('click', opts.onAdd); col.append(add);
    }
    return col;
  }

  function renderFlow() {
    var box = $('flow-cols'); box.replaceChildren();
    STATUS.forEach(function (s) {
      box.append(column(s[1], data.tasks.filter(function (t) { return t.status === s[0]; }), { withStatus: true }));
    });
  }

  function renderFields() {
    var box = $('field-cols'); box.replaceChildren();
    var manage = !$('field-form').hidden;
    data.fields.forEach(function (f) {
      box.append(column(f, data.tasks.filter(function (t) { return t.field === f && t.status !== 'done'; }), {
        addLabel: '+ ' + f + ' 업무 추가',
        onAdd: function () { openTask(null, { field: f }); },
        onRemove: manage ? function () {
          if (!confirm('「' + f + '」 필드를 지울까요? 업무는 남고 필드만 비워집니다.')) return;
          data.fields = data.fields.filter(function (x) { return x !== f; });
          data.tasks.forEach(function (t) { if (t.field === f) t.field = ''; });
          save(); render();
        } : null
      }));
    });
  }

  // ── 업무 추가·수정 창 ──
  var editing = null;
  var dlg = $('task-dialog');
  function openTask(t, preset) {
    editing = t;
    var v = t || Object.assign({ title: '', date: day, status: 'todo', field: '', memo: '' }, preset);
    $('task-dialog-title').textContent = t ? '업무 수정' : '업무 추가';
    $('t-title').value = v.title; $('t-date').value = v.date; $('t-memo').value = v.memo || '';
    var st = $('t-status'); st.replaceChildren();
    STATUS.forEach(function (s) { var o = h('option', null, s[1]); o.value = s[0]; st.append(o); });
    st.value = v.status;
    var fd = $('t-field'); fd.replaceChildren();
    ['', ...data.fields].forEach(function (f) { var o = h('option', null, f || '없음'); o.value = f; fd.append(o); });
    fd.value = data.fields.includes(v.field) ? v.field : '';
    $('t-delete').hidden = !t;
    dlg.showModal();
    $('t-title').focus();
  }
  $('task-form').addEventListener('submit', function () {
    var v = { title: $('t-title').value.trim(), date: $('t-date').value, status: $('t-status').value, field: $('t-field').value, memo: $('t-memo').value.trim() };
    if (!v.title) return;
    if (editing) Object.assign(editing, v);
    else data.tasks.push(Object.assign({ id: uid() }, v));
    save(); render();
  });
  $('t-cancel').addEventListener('click', function () { dlg.close(); });
  $('t-delete').addEventListener('click', function () {
    if (!editing || !confirm('이 업무를 지울까요?')) return;
    data.tasks = data.tasks.filter(function (t) { return t !== editing; });
    save(); dlg.close(); render();
  });

  // ── 메모·날짜·버튼 ──
  function addMemo() {
    data.memos.push({ id: uid(), date: day, text: '' }); save(); render();
    var boxes = document.querySelectorAll('#memo-list textarea');
    if (boxes.length) boxes[boxes.length - 1].focus();
  }
  function moveDay(n) { var d = parse(day); d.setDate(d.getDate() + n); setDay(iso(d)); }
  function setDay(s) { day = s; month = parse(s); month.setDate(1); render(); }

  $('memo-add').addEventListener('click', addMemo);
  $('day-prev').addEventListener('click', function () { moveDay(-1); });
  $('day-next').addEventListener('click', function () { moveDay(1); });
  $('day-today').addEventListener('click', function () { setDay(today); });
  $('day-input').addEventListener('change', function (e) { if (e.target.value) setDay(e.target.value); });
  $('cal-prev').addEventListener('click', function () { month.setMonth(month.getMonth() - 1); renderCalendar(); });
  $('cal-next').addEventListener('click', function () { month.setMonth(month.getMonth() + 1); renderCalendar(); });
  $('btn-add').addEventListener('click', function () { openTask(null); });
  $('today-add').addEventListener('click', function () { openTask(null); });
  $('cal-day-add').addEventListener('click', function () { openTask(null); });
  $('clear-done').addEventListener('click', function () {
    var n = count(data.tasks, 'done');
    if (!n || !confirm('완료한 업무 ' + n + '건을 목록에서 지울까요?')) return;
    data.tasks = data.tasks.filter(function (t) { return t.status !== 'done'; });
    save(); render();
  });
  $('field-manage').addEventListener('click', function () {
    var form = $('field-form'); form.hidden = !form.hidden;
    this.setAttribute('aria-expanded', String(!form.hidden));
    if (!form.hidden) $('field-name').focus();
    renderFields();
  });
  $('field-form').addEventListener('submit', function (e) {
    e.preventDefault();
    var name = $('field-name').value.trim();
    if (name && !data.fields.includes(name)) { data.fields.push(name); save(); }
    $('field-name').value = ''; render();
  });

  // ── 백업·복원 ──
  $('btn-backup').addEventListener('click', function () {
    var url = URL.createObjectURL(new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' }));
    var a = h('a'); a.href = url; a.download = 'worknote-' + today + '.json';
    document.body.append(a); a.click(); a.remove();
    setTimeout(function () { URL.revokeObjectURL(url); }, 1000);
  });
  $('file-restore').addEventListener('change', function (e) {
    var file = e.target.files[0]; e.target.value = '';
    if (!file) return;
    file.text().then(function (txt) {
      var d;
      try { d = JSON.parse(txt); } catch (err) { d = null; }
      if (!valid(d)) { alert('업무노트 백업 파일이 아닙니다.'); return; }
      if (!confirm('지금 기록을 백업 파일 내용으로 바꿀까요?')) return;
      data = d; save(); render();
    });
  });

  // ── 시계 ──
  function tick() {
    var now = new Date();
    $('clock-time').textContent = String(now.getHours()).padStart(2, '0') + ':' + String(now.getMinutes()).padStart(2, '0');
    $('clock-day').textContent = WEEK[now.getDay()] + '요일';
    if (iso(now) !== today) { today = iso(now); render(); } // 자정을 넘기면 오늘을 갱신
  }
  tick(); setInterval(tick, 15000);
  render();
})();
