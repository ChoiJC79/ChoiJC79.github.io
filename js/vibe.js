// 바이브 코딩 과정: 요점 카드 「안다」 표시·통과 기록(localStorage)·목록 진행 표시·프롬프트 복사
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

  var KNOW = 'vibe-known', known = {};
  try { known = JSON.parse(localStorage.getItem(KNOW)) || {}; } catch (_) {}
  var boxes = main.querySelectorAll('.vb-know input'), msg = main.querySelector('.vb-msg');
  var mine = known[slug] || [];
  function update() {
    var n = 0;
    boxes.forEach(function (b) { if (b.checked) n++; });
    if (n === boxes.length) {
      if (cleared.indexOf(slug) < 0) { cleared.push(slug); save(cleared); }
      msg.className = 'vb-msg pass';
      msg.textContent = '모든 카드를 「안다」로 표시해 이 단계를 통과했습니다. 아래 튜터 프롬프트로 내 프로젝트에 적용해 본 뒤 다음 단계로 넘어가세요.';
    } else {
      msg.className = 'vb-msg';
      msg.textContent = boxes.length + '장 중 ' + n + '장을 알고 있습니다.' + (cleared.indexOf(slug) > -1 ? ' 이미 통과한 단계라 복습 중입니다.' : '');
    }
  }
  boxes.forEach(function (b) {
    b.checked = mine.indexOf(+b.dataset.i) > -1;
    b.addEventListener('change', function () {
      known[slug] = [].filter.call(boxes, function (x) { return x.checked; }).map(function (x) { return +x.dataset.i; });
      try { localStorage.setItem(KNOW, JSON.stringify(known)); } catch (_) {}
      update();
    });
  });
  var open = main.querySelector('.vb-open');
  open.addEventListener('click', function () {
    var all = main.querySelectorAll('.vb-card details'), shut = [].some.call(all, function (d) { return !d.open; });
    all.forEach(function (d) { d.open = shut; });
    open.textContent = shut ? '모두 접기' : '모두 펼치기';
  });
  update();
})();
