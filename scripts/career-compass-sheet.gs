// 진로 나침반(career-compass.html) 응답을 받아 구글 시트에 한 줄씩 쌓는 Apps Script 웹 앱
//
// 설치 (5분)
// 1. 구글 시트를 새로 만든다 (이름 예: 진로나침반 응답). 이 시트는 공유하지 않는다.
// 2. 시트 메뉴 [확장 프로그램] → [Apps Script] → 기본 코드를 지우고 이 파일 내용을 붙여 넣고 저장.
// 3. [배포] → [새 배포] → 유형 '웹 앱' → 실행 사용자: 나 / 액세스 권한: 모든 사용자 → 배포 → 권한 승인.
// 4. 나온 웹 앱 URL(https://script.google.com/macros/s/…/exec)을 career-compass.html의 ENDPOINT에 넣는다.
// 5. 코드를 고치면 [배포] → [배포 관리] → 연필 → 버전 '새 버전'으로 다시 배포해야 반영된다 (URL은 그대로).
//
// 보관: 화면에 '1년 후 삭제'라고 안내했으므로, 매년 1년 지난 행을 지운다 (deleteOlderThanOneYear 실행).

var SHEET_NAME = '응답';
var TK = ['R', 'I', 'A', 'S', 'E', 'C'];
var B5 = ['E', 'A', 'C', 'S', 'O'];
var C4 = ['concern', 'control', 'curiosity', 'confidence'];
var HEAD = ['받은 시각', '별칭', '학년', '흥미 코드']
  .concat(TK.map(function (k) { return '흥미 ' + k; }))
  .concat(['외향성', '친화성', '성실성', '정서 안정성', '개방성'])
  .concat(['관심', '통제', '호기심', '자신감'])
  .concat(['가치 1~5', '롤모델', '즐겨 보는 것', '몰입 활동', '피하고 싶은 일', '원자료(JSON)']);

function doPost(e) {
  try {
    var raw = (e && e.postData && e.postData.contents) || '';
    if (raw.length > 30000) return out_('too_large');
    var d = JSON.parse(raw);
    if (d.hp) return out_('ok'); // 자동 입력 봇: 저장하지 않고 성공처럼 응답
    if (d.v !== 1 || !isNums_(d.interest, 36) || !isNums_(d.big5, 50) || !isNums_(d.adapt, 16)) return out_('bad_format');

    // 분당 전송 상한 (공개 주소이므로 대량 전송 차단)
    var cache = CacheService.getScriptCache();
    var n = Number(cache.get('n') || 0);
    if (n >= 30) return out_('busy');
    cache.put('n', String(n + 1), 60);

    var sc = d.scores || {}, st = d.story || {};
    var vals = Array.isArray(d.values) ? d.values.slice(0, 5).map(function (x) { return clip_(x, 20); }).join(' > ') : '';
    var row = [new Date(), clip_(d.nick, 20), clip_(d.grade, 5), clip_(sc.code, 3)]
      .concat(TK.map(function (k) { return num_(sc.riasec && sc.riasec[k]); }))
      .concat(B5.map(function (k) { return num_(sc.big5 && sc.big5[k]); }))
      .concat(C4.map(function (k) { return num_(sc.adapt && sc.adapt[k]); }))
      .concat([vals, clip_(st.roles, 800), clip_(st.media, 800), clip_(st.flow, 800), clip_(st.avoid, 800), clip_(raw, 30000)]);

    var lock = LockService.getScriptLock();
    lock.waitLock(10000);
    try { sheet_().appendRow(row); } finally { lock.releaseLock(); }
    return out_('ok');
  } catch (err) {
    return out_('error');
  }
}

function sheet_() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sh = ss.getSheetByName(SHEET_NAME) || ss.insertSheet(SHEET_NAME);
  if (sh.getLastRow() === 0) { sh.appendRow(HEAD); sh.setFrozenRows(1); }
  return sh;
}

// 숫자 배열(1~5 또는 비어 있음)인지 확인
function isNums_(a, len) {
  if (!Array.isArray(a) || a.length !== len) return false;
  for (var i = 0; i < a.length; i++) if (a[i] !== null && !(a[i] >= 1 && a[i] <= 5)) return false;
  return true;
}
function num_(x) { return typeof x === 'number' && isFinite(x) ? x : ''; }
// 길이를 자르고, =·+·-·@로 시작하는 값은 수식으로 실행되지 않게 앞에 ' 를 붙인다
function clip_(x, max) {
  var s = String(x == null ? '' : x).slice(0, max);
  return /^[=+\-@]/.test(s) ? "'" + s : s;
}
function out_(status) {
  return ContentService.createTextOutput(JSON.stringify({ status: status })).setMimeType(ContentService.MimeType.JSON);
}

// 1년이 지난 응답 행을 지운다. 매년 한 번 직접 실행하거나 [트리거]에 월 1회로 등록한다.
function deleteOlderThanOneYear() {
  var sh = sheet_(), last = sh.getLastRow();
  if (last < 2) return;
  var limit = new Date(); limit.setFullYear(limit.getFullYear() - 1);
  var times = sh.getRange(2, 1, last - 1, 1).getValues();
  for (var r = times.length - 1; r >= 0; r--) {
    if (times[r][0] instanceof Date && times[r][0] < limit) sh.deleteRow(r + 2);
  }
}
