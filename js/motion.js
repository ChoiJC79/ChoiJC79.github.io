// 사이트 공통 모션: 스크롤 등장·탭/필터 전환 등장·읽기 진행 막대 (Motion 라이브러리, Motion AI Kit 규칙 기준)
(function () {
  if (!window.Motion || !window.matchMedia) return;

  var animate = Motion.animate, inView = Motion.inView, scroll = Motion.scroll;
  var ITEM = '.card,.cat-card,.col-card,.col-item,.kpi-card,.metric-card,.chart-card,.taste-card,' +
             '.pair-item,.tl-item,.step,.insight-item,.info-item,.proposal-item,.diag-item,[data-motion]';
  var PANEL = ITEM + ',section,article,[role=tabpanel],.tab-pane,.lk-body,.detail-wrap,.idx-list';

  function clear(el) {
    el.style.opacity = '';
    el.style.transform = '';
  }
  // Motion은 완료 직후 한 프레임 뒤에 최종값을 인라인으로 기록하므로 두 프레임 뒤에 지운다.
  // 인라인 값을 지워야 기존 CSS의 hover 효과가 그대로 동작한다.
  function clearLater(el) {
    requestAnimationFrame(function () { requestAnimationFrame(function () { clear(el); }); });
  }
  function rise(els, from, duration) {
    var gap = Math.min(0.06, 0.36 / Math.max(els.length - 1, 1));
    for (var i = 0; i < els.length; i++) {
      els[i].__motionDone = true;
      animate(els[i], { opacity: [0, 1], transform: [from, 'translateY(0px)'] },
        { duration: duration, ease: 'easeOut', delay: i * gap })
        .then(clearLater.bind(null, els[i]));
    }
  }

  // 1) 칼럼·가이드 본문 읽기 진행 막대 (스크롤에 직접 연동되므로 '동작 줄이기'와 무관하게 표시)
  if (/^\/(columns|guides)\//.test(location.pathname)) {
    var bar = document.createElement('div');
    bar.setAttribute('aria-hidden', 'true');
    bar.style.cssText = 'position:fixed;top:0;left:0;right:0;height:3px;z-index:10000;pointer-events:none;' +
      'transform-origin:0 50%;transform:scaleX(0);background:linear-gradient(90deg,var(--accent2,#ff2a6d),var(--accent,#05d9e8))';
    document.body.appendChild(bar);
    scroll(animate(bar, { transform: ['scaleX(0)', 'scaleX(1)'] }, { ease: 'linear' }));
  }

  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

  // 2) 스크롤 등장: 첫 화면 아래에 있는 카드·섹션만 대상 (첫 화면은 깜빡임 방지를 위해 그대로 둠)
  var FROM = 'translateY(24px)';
  var fold = window.innerHeight * 0.9;
  function belowFold(el) {
    var r = el.getBoundingClientRect();
    return r.height > 0 && r.top > fold;
  }
  var targets = [];
  var items = document.querySelectorAll(ITEM);
  for (var i = 0; i < items.length; i++) {
    var it = items[i];
    if (it.parentElement && it.parentElement.closest(ITEM)) continue;
    if (belowFold(it)) targets.push(it);
  }
  var blocks = document.querySelectorAll('section,article');
  for (var j = 0; j < blocks.length; j++) {
    var b = blocks[j];
    if (b.querySelector(ITEM) || b.closest(ITEM)) continue;
    var outer = b.parentElement && b.parentElement.closest('section,article');
    if (outer && targets.indexOf(outer) !== -1) continue;
    if (belowFold(b)) targets.push(b);
  }
  for (var k = 0; k < targets.length; k++) {
    targets[k].style.opacity = '0';
    targets[k].style.transform = FROM;
  }
  window.addEventListener('beforeprint', function () {
    for (var p = 0; p < targets.length; p++) clear(targets[p]);
  });

  // 같은 프레임에 화면에 들어온 요소들은 한 묶음으로 순차 등장
  var queue = [], scheduled = false;
  function flush() {
    scheduled = false;
    var batch = queue;
    queue = [];
    rise(batch, FROM, 0.5);
  }
  if (targets.length) {
    inView(targets, function (el) {
      if (el.__motionDone) return;
      queue.push(el);
      if (!scheduled) {
        scheduled = true;
        requestAnimationFrame(flush);
      }
    });
  }

  // 3) 탭·필터·펼침 버튼으로 새로 나타난 요소는 짧게 등장
  function shown(el) {
    return el.getClientRects().length > 0;
  }
  function onScreen(el) {
    var r = el.getBoundingClientRect();
    return r.bottom > 0 && r.top < window.innerHeight;
  }
  document.addEventListener('click', function (e) {
    var trigger = e.target.closest && e.target.closest('button,[onclick],[role=tab]');
    if (!trigger) return;
    var cands = document.querySelectorAll(PANEL);
    var hidden = [];
    for (var n = 0; n < cands.length; n++) if (!shown(cands[n])) hidden.push(cands[n]);
    if (!hidden.length) return;
    setTimeout(function () {
      var now = [];
      for (var m = 0; m < hidden.length; m++) {
        var el = hidden[m];
        if (!shown(el) || !onScreen(el)) continue;
        // 함께 나타난 조상이 있으면 조상만 움직인다
        var anc = el.parentElement && el.parentElement.closest(PANEL);
        if (anc && hidden.indexOf(anc) !== -1 && shown(anc)) continue;
        now.push(el);
      }
      if (now.length) rise(now, 'translateY(8px)', 0.3);
    }, 0);
  }, true);
})();
