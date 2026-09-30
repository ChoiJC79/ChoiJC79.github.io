// toggleTheme()를 따로 정의하지 않은 페이지용 다크/라이트 전환 (저장 키 choijc-theme)
(function(){
  var t = localStorage.getItem('choijc-theme');
  if (t) document.documentElement.setAttribute('data-theme', t);
  themeBtnLabel();
})();
function themeBtnLabel(){
  var btn = document.getElementById('theme-toggle');
  if (btn) btn.textContent = document.documentElement.getAttribute('data-theme') === 'dark' ? '☀ 라이트' : '☾ 다크';
}
function toggleTheme(){
  var next = document.documentElement.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
  document.documentElement.setAttribute('data-theme', next);
  localStorage.setItem('choijc-theme', next);
  themeBtnLabel();
}
