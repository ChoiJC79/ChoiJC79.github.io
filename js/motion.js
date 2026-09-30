// 사이트 공통 스크롤 등장 모션 (Motion 라이브러리 사용, '동작 줄이기' 설정 시 꺼짐)
(function () {
  if (!window.Motion || !window.matchMedia) return;
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

  var animate = Motion.animate, inView = Motion.inView;
  var ITEM = '.card,.cat-card,.col-card,.col-item,.kpi-card,.metric-card,.chart-card,.taste-card,' +
             '.pair-item,.tl-item,.step,.insight-item,.info-item,.proposal-item,.diag-item,[data-motion]';
  var BLOCK = 'section,article';
  var FROM = 'translateY(24px)';

  // 첫 화면에 이미 보이는 요소는 건드리지 않는다 (깜빡임 방지)
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
  var blocks = document.querySelectorAll(BLOCK);
  for (var j = 0; j < blocks.length; j++) {
    var b = blocks[j];
    if (b.querySelector(ITEM) || b.closest(ITEM)) continue;
    if (b.parentElement && b.parentElement.closest(BLOCK) && targets.indexOf(b.parentElement.closest(BLOCK)) !== -1) continue;
    if (belowFold(b)) targets.push(b);
  }
  if (!targets.length) return;

  for (var k = 0; k < targets.length; k++) {
    targets[k].style.opacity = '0';
    targets[k].style.transform = FROM;
  }

  window.addEventListener('beforeprint', function () {
    for (var p = 0; p < targets.length; p++) clear(targets[p]);
  });

  // 같은 프레임에 화면에 들어온 요소들은 한 묶음으로 순차 등장
  var queue = [], scheduled = false;
  function clear(el) {
    el.style.opacity = '';
    el.style.transform = '';
  }
  // Motion은 완료 직후 한 프레임 뒤에 최종값을 인라인으로 기록하므로 두 프레임 뒤에 지운다.
  // 인라인 값을 지워야 기존 CSS의 hover 효과가 그대로 동작한다.
  function clearLater(el) {
    requestAnimationFrame(function () { requestAnimationFrame(function () { clear(el); }); });
  }
  function flush() {
    scheduled = false;
    var batch = queue;
    queue = [];
    var gap = Math.min(0.06, 0.36 / Math.max(batch.length - 1, 1));
    for (var n = 0; n < batch.length; n++) {
      animate(batch[n], { opacity: [0, 1], transform: [FROM, 'translateY(0px)'] },
        { duration: 0.5, ease: 'easeOut', delay: n * gap })
        .then(clearLater.bind(null, batch[n]));
    }
  }

  inView(targets, function (el) {
    queue.push(el);
    if (!scheduled) {
      scheduled = true;
      requestAnimationFrame(flush);
    }
  });
})();
