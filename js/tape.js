// 홈 카세트 첫 화면: 모토로라 삐삐에 최신 칼럼을 띄우고 ▶ 버튼·테이프 카운터를 최신 글에 맞춘다
(function () {
  var lcd = document.getElementById('pager-lcd');
  var play = document.getElementById('deck-play');
  var counter = document.getElementById('tape-counter');
  var clock = document.getElementById('pager-clock');
  if (!lcd || !window.fetch || !window.DOMParser) return;

  function two(n) { return (n < 10 ? '0' : '') + n; }
  function tick() {
    var d = new Date();
    if (clock) clock.textContent = two(d.getHours()) + ':' + two(d.getMinutes());
  }
  tick();
  setInterval(tick, 30000);

  fetch('/column.html')
    .then(function (r) { if (!r.ok) throw r.status; return r.text(); })
    .then(function (t) {
      var doc = new DOMParser().parseFromString(t, 'text/html');
      var el = doc.querySelector('article.col-item');
      if (!el) return;
      var title = (el.querySelector('.col-title') || {}).textContent || '';
      var date = ((el.querySelector('.col-date') || {}).textContent || '').trim();
      var more = el.querySelector('a.col-more');
      var href = more ? more.getAttribute('href') : '/column.html';
      var m = date.match(/(\d{4})[.\-](\d{2})[.\-](\d{2})/);
      var mmdd = m ? m[2] + m[3] : '0000';
      document.getElementById('pager-num').textContent = mmdd;
      document.getElementById('pager-text').textContent = '새 글 · ' + title.trim() + ' · 칼럼';
      lcd.href = href;
      lcd.setAttribute('aria-label', '최신 칼럼: ' + title.trim() + ' (' + date + ')');
      if (play) play.href = href;
      if (counter) counter.textContent = mmdd.split('').join(' ');
    })
    .catch(function () {});
})();
