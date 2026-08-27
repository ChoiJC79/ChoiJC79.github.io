(function(){var t=localStorage.getItem('choijc-theme')||'dark';document.documentElement.setAttribute('data-theme',t);var tb=document.getElementById('theme-btn');if(tb)tb.textContent=t==='dark'?'☀ 라이트':'☾ 다크';})();
function toggleTheme(){var h=document.documentElement;var n=h.getAttribute('data-theme')==='dark'?'light':'dark';h.setAttribute('data-theme',n);localStorage.setItem('choijc-theme',n);var tb=document.getElementById('theme-btn');if(tb)tb.textContent=n==='dark'?'☀ 라이트':'☾ 다크';}
var navbar=document.getElementById('navbar');var heroEl=document.getElementById('hero');
if(navbar&&heroEl){window.addEventListener('scroll',function(){if(window.scrollY>heroEl.offsetHeight-80)navbar.classList.add('light-nav');else navbar.classList.remove('light-nav');});}
function lkToggle(btn){btn.classList.toggle('lk-open');btn.nextElementSibling.classList.toggle('lk-open');}
function searchNaver(e){e.preventDefault();var q=document.getElementById('naver-q').value.trim();if(q)window.open('https://search.naver.com/search.naver?query='+encodeURIComponent(q),'_blank');}
function searchGoogle(e){e.preventDefault();var q=document.getElementById('google-q').value.trim();if(q)window.open('https://www.google.com/search?q='+encodeURIComponent(q),'_blank');}

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
  var WX={0:'☀️',1:'🌤️',2:'⛅',3:'☁️',
    45:'🌫️',48:'🌫️',
    51:'🌦️',53:'🌦️',55:'🌦️',
    56:'🌨️',57:'🌨️',
    61:'🌧️',63:'🌧️',65:'🌧️',
    71:'❄️',73:'❄️',75:'❄️',77:'🌨️',
    80:'🌦️',81:'🌦️',82:'🌦️',
    85:'🌨️',86:'🌨️',
    95:'⛈️',96:'⛈️',99:'⛈️'};
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
      var icon=WX[days.weather_code[i]]||'🌡️';
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

/* ── 홈 통계 위젯: 연금 D-day / 최근수정 / 방문자수 ── */
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

  /* 1. 공무원연금 개시 D-day (1979년 11월생, 65세 → 2044-11-01) */
  (function(){
    var el = document.getElementById('pension-dday');
    if(!el) return;
    var target = new Date(2044, 10, 1); /* month 0-based */
    var diff = Math.ceil((target - new Date()) / 86400000);
    el.textContent = 'D-' + diff.toLocaleString('ko-KR');
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
