// 바이브 코딩 과정: 확인 문제 채점·통과 기록(localStorage)·목록 진행 표시·프롬프트 복사
(function () {
  var KEY = 'vibe-cleared';
  function load() { try { return JSON.parse(localStorage.getItem(KEY)) || []; } catch (_) { return []; } }
  function save(list) { try { localStorage.setItem(KEY, JSON.stringify(list)); } catch (_) {} }
  var cleared = load();

  document.querySelectorAll('.pr-copy').forEach(function (b) {
    b.addEventListener('click', function () {
      var t = b.parentNode.querySelector('pre').textContent;
      if (navigator.clipboard) navigator.clipboard.writeText(t).then(function () {
        b.textContent = '복사됨'; setTimeout(function () { b.textContent = '복사'; }, 1400);
      });
    });
  });

  // 목록 페이지
  var home = document.querySelector('.vb-home');
  if (home) {
    var next = null, total = 0, rank = 2;
    document.querySelectorAll('.vb-row').forEach(function (r) {
      var ok = cleared.indexOf(r.dataset.slug) > -1;
      if (ok) total++;
      else if (!next) next = r;
      r.classList.toggle('done', ok);
      r.querySelector('.vb-state').textContent = ok ? '통과' : '아직';
    });
    if (next) { next.classList.add('now'); next.querySelector('.vb-state').textContent = '지금 할 차례'; }
    document.querySelectorAll('.vb-level').forEach(function (s) {
      var rows = s.querySelectorAll('.vb-row'), n = s.querySelectorAll('.vb-row.done').length;
      s.querySelector('.vb-count').textContent = n;
      if (n === rows.length && rank === +s.dataset.lv - 1) rank = +s.dataset.lv;
    });
    document.querySelector('.vb-total').textContent = total;
    document.querySelector('.vb-rank').textContent = 'Lv.' + rank + (rank === 6 ? ' 과정 수료' : ' 단계');
    return;
  }

  // 레슨 페이지
  var main = document.querySelector('.vb-lesson');
  if (!main) return;
  var slug = main.dataset.slug, prev = main.dataset.prev;
  if (prev && cleared.indexOf(prev) < 0) {
    var lock = main.querySelector('.vb-lock');
    lock.innerHTML = '앞 단계 「<a href="/vibe/' + prev + '.html"></a>」을 아직 통과하지 않았습니다. 읽는 것은 괜찮지만, 앞 단계를 통과한 뒤 풀면 더 잘 남습니다.';
    lock.querySelector('a').textContent = main.dataset.prevTitle;
    lock.hidden = false;
  }

  var data = JSON.parse(main.querySelector('.vb-data').textContent);
  var box = main.querySelector('.vb-quiz');
  function shuffle(a) { a = a.slice(); for (var i = a.length - 1; i > 0; i--) { var j = Math.floor(Math.random() * (i + 1)); var t = a[i]; a[i] = a[j]; a[j] = t; } return a; }
  function el(tag, cls, text) { var n = document.createElement(tag); if (cls) n.className = cls; if (text != null) n.textContent = text; return n; }

  function render() {
    box.innerHTML = '';
    if (cleared.indexOf(slug) > -1) box.appendChild(el('p', 'vb-passed', '이미 통과한 단계입니다. 다시 풀어 보며 복습해도 됩니다.'));
    var form = el('form', 'vb-form');
    shuffle(data.map(function (q, i) { return i; })).forEach(function (qi, n) {
      var q = data[qi], fs = el('fieldset', 'vb-q');
      fs.dataset.qi = qi;
      fs.appendChild(el('legend', null, (n + 1) + '. ' + q.q));
      shuffle([0, 1, 2, 3]).forEach(function (oi) {
        var lab = el('label', 'vb-opt'), inp = el('input');
        inp.type = 'radio'; inp.name = 'q' + qi; inp.value = oi;
        lab.dataset.oi = oi;
        lab.appendChild(inp); lab.appendChild(el('span', null, q.options[oi]));
        fs.appendChild(lab);
      });
      form.appendChild(fs);
    });
    var btn = el('button', 'vb-submit', '채점하기'), msg = el('p', 'vb-msg');
    btn.type = 'submit';
    form.appendChild(btn); form.appendChild(msg);
    form.addEventListener('submit', function (ev) {
      ev.preventDefault();
      var left = data.length - form.querySelectorAll('input:checked').length;
      if (left) { msg.textContent = '아직 고르지 않은 문제가 ' + left + '개 있습니다.'; return; }
      var right = 0;
      form.querySelectorAll('.vb-q').forEach(function (fs) {
        var q = data[+fs.dataset.qi], sel = +fs.querySelector('input:checked').value, ok = sel === q.answer;
        if (ok) right++;
        fs.classList.add(ok ? 'right' : 'wrong');
        fs.querySelectorAll('input').forEach(function (i) { i.disabled = true; });
        fs.querySelector('[data-oi="' + q.answer + '"]').classList.add('answer');
        var ex = el('div', 'vb-ex-why');
        ex.appendChild(el('p', null, (ok ? '맞았습니다. ' : '틀렸습니다. ') + q.why[sel]));
        if (!ok) ex.appendChild(el('p', null, '정답 「' + q.options[q.answer] + '」 ' + q.why[q.answer]));
        fs.appendChild(ex);
      });
      btn.remove();
      if (right === data.length) {
        if (cleared.indexOf(slug) < 0) { cleared.push(slug); save(cleared); }
        msg.className = 'vb-msg pass';
        msg.textContent = data.length + '문제를 모두 맞혀 이 단계를 통과했습니다. 아래 튜터 프롬프트로 내 프로젝트에 적용해 본 뒤 다음 단계로 넘어가세요.';
      } else {
        msg.className = 'vb-msg fail';
        msg.textContent = data.length + '문제 중 ' + right + '개 맞혔습니다. 틀린 문제의 해설을 읽고 다시 풀어 보세요.';
        var again = el('button', 'vb-submit', '다시 풀기');
        again.type = 'button';
        again.addEventListener('click', function () { render(); box.scrollIntoView({ block: 'start' }); });
        form.appendChild(again);
      }
    });
    box.appendChild(form);
  }
  render();
})();
