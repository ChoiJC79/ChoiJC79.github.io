(function(){var t=localStorage.getItem('choijc-theme')||'light';document.documentElement.setAttribute('data-theme',t);var tb=document.getElementById('theme-btn');if(tb)tb.textContent=t==='dark'?'라이트':'다크';})();
function toggleTheme(){var h=document.documentElement;var n=h.getAttribute('data-theme')==='dark'?'light':'dark';h.setAttribute('data-theme',n);localStorage.setItem('choijc-theme',n);var tb=document.getElementById('theme-btn');if(tb)tb.textContent=n==='dark'?'라이트':'다크';}
/* -- 제천 맛집 위젯 열기/닫기 -- */
(function(){
  var corner=document.getElementById('jc-corner');
  var panel=document.getElementById('jc-corner-panel');
  var toggle=document.getElementById('jc-corner-toggle');
  var closeBtn=document.getElementById('jc-corner-close');
  if(!corner||!panel||!toggle||!closeBtn)return;
  function openPanel(){ panel.classList.add('open'); }
  function closePanel(){ panel.classList.remove('open'); }
  toggle.addEventListener('click', function(){
    panel.classList.contains('open') ? closePanel() : openPanel();
  });
  closeBtn.addEventListener('click', closePanel);
  document.addEventListener('click', function(e){
    if (panel.classList.contains('open') && !corner.contains(e.target)) closePanel();
  });
})();

/* 제천 날씨 — Open-Meteo (no API key) */
(function(){
  var WX={0:'맑음',1:'대체로 맑음',2:'구름 조금',3:'흐림',45:'안개',48:'안개',
    51:'이슬비',53:'이슬비',55:'이슬비',56:'어는 비',57:'어는 비',
    61:'비',63:'비',65:'강한 비',71:'눈',73:'눈',75:'강한 눈',77:'눈',
    80:'소나기',81:'소나기',82:'강한 소나기',85:'눈보라',86:'눈보라',
    95:'뇌우',96:'뇌우',99:'뇌우'};
  var DOW=['일','월','화','수','목','금','토'];
  fetch('https://api.open-meteo.com/v1/forecast?latitude=37.13&longitude=128.19' +
    '&daily=weather_code,temperature_2m_max,temperature_2m_min' +
    '&timezone=Asia%2FSeoul&forecast_days=7')
  .then(function(r){return r.json();})
  .then(function(d){
    var days=d.daily, html='';
    var today=new Date().toLocaleDateString('sv-SE');
    for(var i=0;i<7;i++){
      var dt=days.time[i];
      var dow=DOW[new Date(dt+'T12:00:00').getDay()];
      var icon=WX[days.weather_code[i]]||'-';
      var hi=Math.round(days.temperature_2m_max[i]);
      var lo=Math.round(days.temperature_2m_min[i]);
      var cls=dt===today?' today':'';
      html+='<div class="wx-day'+cls+'">'+
        '<div class="wx-dow">'+(dt===today?'오늘':dow)+'</div>'+
        '<div class="wx-icon">'+icon+'</div>'+
        '<div class="wx-temps"><span class="wx-hi">'+hi+'°</span>'+
        '<span class="wx-lo">'+lo+'°</span></div></div>';
    }
    document.getElementById('wx-days').innerHTML=html;
    var n=new Date();
    document.getElementById('wx-updated').textContent=
      n.getHours()+':'+String(n.getMinutes()).padStart(2,'0')+' 기준';
  })
  .catch(function(){
    document.getElementById('wx-days').innerHTML='<div class="wx-err">날씨 정보를 불러올 수 없습니다</div>';
  });
})();

/* ── 홈 통계 위젯: 최근수정 / 방문자수 ── */
(function(){

  /* 0. 시간대별 인사말 */
  (function(){
    var el = document.getElementById('hero-greeting');
    if(!el) return;
    var h = new Date().getHours();
    var msg = h >= 6  && h < 12 ? '좋은 아침입니다' :
              h >= 12 && h < 18 ? '안녕하세요' :
              h >= 18 && h < 22 ? '좋은 저녁입니다' :
              h >= 22            ? '오늘도 수고하셨습니다' :
                                   '이 시간까지 찾아주셨네요';
    el.textContent = msg;
  })();

  /* 2. 웹페이지 최근 수정일 */
  (function(){
    var el = document.getElementById('last-modified');
    if(!el) return;
    var d = new Date(document.lastModified);
    if(d && !isNaN(d.getTime())){
      el.textContent = d.getFullYear() + '.' +
        String(d.getMonth()+1).padStart(2,'0') + '.' +
        String(d.getDate()).padStart(2,'0');
    }
  })();


})();

/* 홈 최근 글: 칼럼 목록·가이드 목록 페이지에서 최신 글을 읽어 와 카드로 표시 */
(function(){
  var sec = document.getElementById('recent'), list = document.getElementById('recent-list');
  if (!sec || !list || !window.fetch || !window.DOMParser) return;
  function load(url){ return fetch(url).then(function(r){ if(!r.ok) throw r.status; return r.text(); }).then(function(t){ return new DOMParser().parseFromString(t, 'text/html'); }); }
  function txt(root, sel){ var el = root.querySelector(sel); return el ? el.textContent.trim() : ''; }
  function card(o){
    var a = document.createElement('a'); a.className = 'recent-card' + (o.img ? '' : ' recent-card-text'); a.href = o.href;
    if (o.img) { var im = document.createElement('img'); im.src = o.img; im.alt = ''; im.loading = 'lazy'; a.appendChild(im); }
    var body = document.createElement('div'); body.className = 'recent-body';
    var k = document.createElement('span'); k.className = 'recent-kind'; k.textContent = o.kind; body.appendChild(k);
    var h = document.createElement('h3'); h.textContent = o.title; body.appendChild(h);
    if (o.excerpt) { var p = document.createElement('p'); p.textContent = o.excerpt; body.appendChild(p); }
    var d = document.createElement('span'); d.className = 'recent-date'; d.textContent = o.date; body.appendChild(d);
    a.appendChild(body); return a;
  }
  Promise.all([
    load('/column.html').then(function(doc){
      return Array.prototype.slice.call(doc.querySelectorAll('article.col-item'), 0, 3).map(function(el){
        var img = el.querySelector('.col-visual img'), more = el.querySelector('a.col-more');
        return { kind: '칼럼' + txt(el, '.col-cat').replace(/^\/\s*/, ' · '), title: txt(el, '.col-title'),
                 excerpt: txt(el, '.col-excerpt'), date: txt(el, '.col-date'),
                 href: more ? more.getAttribute('href') : '/column.html', img: img ? img.getAttribute('src') : '' };
      });
    }).catch(function(){ return []; }),
    load('/guides.html').then(function(doc){
      var el = doc.querySelector('a.col-card');
      return el ? [{ kind: 'AI 가이드', title: txt(el, '.col-title'), excerpt: txt(el, '.col-excerpt'),
                     date: txt(el, '.col-date'), href: el.getAttribute('href'), img: '' }] : [];
    }).catch(function(){ return []; })
  ]).then(function(r){
    var items = r[0].concat(r[1]);
    if (!items.length) return;
    items.forEach(function(o){ list.appendChild(card(o)); });
    sec.hidden = false;
  });
})();

/* 모달: 푸터 버튼으로 열고, 닫기 버튼·바깥 클릭·ESC로 닫는다 */
(function(){
  var last=null;
  function open(m,from){
    last=from; m.hidden=false; document.body.classList.add('jm-open');
    window.dispatchEvent(new Event('resize')); /* 노을 호 그래프가 숨김 상태에서 폭을 못 재므로 열 때 다시 잰다 */
    var c=m.querySelector('.jmodal-close'); if(c) c.focus();
  }
  function close(m){
    m.hidden=true; document.body.classList.remove('jm-open'); if(last) last.focus();
  }
  document.querySelectorAll('[data-modal]').forEach(function(b){
    b.addEventListener('click',function(){ var m=document.getElementById(b.getAttribute('data-modal')); if(m) open(m,b); });
  });
  document.querySelectorAll('.jmodal').forEach(function(m){
    m.addEventListener('click',function(e){ if(e.target===m||e.target.classList.contains('jmodal-close')) close(m); });
  });
  document.addEventListener('keydown',function(e){
    if(e.key!=='Escape') return;
    document.querySelectorAll('.jmodal:not([hidden])').forEach(close);
  });
})();
