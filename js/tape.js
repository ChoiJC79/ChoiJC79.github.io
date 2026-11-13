// 홈 카세트 데크 및 1979 라운지 재즈 BGM 플레이어
(function () {
  'use strict';

  /* ── 1. 모토로라 삐삐: 시계 및 최신 칼럼 연동 ── */
  var lcd = document.getElementById('pager-lcd');
  var clock = document.getElementById('pager-clock');
  function two(n) { return (n < 10 ? '0' : '') + n; }
  function tick() {
    var d = new Date();
    if (clock) clock.textContent = two(d.getHours()) + ':' + two(d.getMinutes());
  }
  tick();
  setInterval(tick, 30000);

  if (lcd && window.fetch && window.DOMParser) {
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
        var pNum = document.getElementById('pager-num');
        var pTxt = document.getElementById('pager-text');
        if (pNum) pNum.textContent = mmdd;
        if (pTxt) pTxt.textContent = '새 글 · ' + title.trim() + ' · 칼럼';
        lcd.href = href;
        lcd.setAttribute('aria-label', '최신 칼럼: ' + title.trim() + ' (' + date + ')');
      })
      .catch(function () {});
  }

  /* ── 2. 1979 라운지 재즈 플레이리스트 ── */
  var PLAYLIST = [
    {
      no: 1,
      name: "심야 색소폰 라운지",
      title: "Night on the Docks",
      file: "/audio/night_on_the_docks.mp3",
      tag: "색소폰 & 콘트라베이스"
    },
    {
      no: 2,
      name: "보사노바 카페",
      title: "Bossa Antigua",
      file: "/audio/bossa_antigua.mp3",
      tag: "따뜻한 보사노바 기타"
    },
    {
      no: 3,
      name: "레트로 스윙 그루브",
      title: "Groove Grove",
      file: "/audio/groove_grove.mp3",
      tag: "빈티지 오르간 & 플루트"
    }
  ];

  var currentIndex = 0;
  var isPlaying = false;
  var audio = new Audio();
  audio.preload = "metadata";

  // 기본 볼륨: 35% (부담 없는 배경음악)
  var savedVol = localStorage.getItem('choijc-bgm-vol');
  audio.volume = savedVol !== null ? parseFloat(savedVol) : 0.35;

  // UI 요소 참조
  var tapeDeck = document.querySelector('.deck');
  var heroTape = document.getElementById('hero-tape');
  var tapeCounter = document.getElementById('tape-counter');
  var tapeTrackName = document.getElementById('tape-track-name');

  var deckPlayBtn = document.getElementById('deck-play');
  var deckPlayLabel = document.getElementById('deck-play-label');
  var deckStopBtn = document.getElementById('deck-stop');
  var deckPrevBtn = document.getElementById('deck-prev');
  var deckNextBtn = document.getElementById('deck-next');

  var bgmBar = document.getElementById('lounge-bgm');
  var bgmPlayBtn = document.getElementById('bgm-play-btn');
  var bgmPrevBtn = document.getElementById('bgm-prev-btn');
  var bgmNextBtn = document.getElementById('bgm-next-btn');
  var bgmMuteBtn = document.getElementById('bgm-mute-btn');
  var bgmTrackDisplay = document.getElementById('bgm-track-display');
  var bgmDiscBtn = document.getElementById('bgm-disc-btn');
  var bgmInfoBtn = document.getElementById('bgm-info-btn');

  // 트랙 정보 UI 갱신
  function updateTrackUI() {
    var track = PLAYLIST[currentIndex];
    var labelText = '♪ ' + track.no + '. ' + track.name;
    if (tapeTrackName) tapeTrackName.textContent = labelText;
    if (bgmTrackDisplay) bgmTrackDisplay.textContent = track.no + '. ' + track.name;
  }

  // 곡 로드
  function loadTrack(index, autoplay) {
    currentIndex = (index + PLAYLIST.length) % PLAYLIST.length;
    var track = PLAYLIST[currentIndex];
    audio.src = track.file;
    audio.currentTime = 0;
    updateTrackUI();

    if (autoplay) {
      playAudio();
    } else {
      updatePlaybackUI(false);
    }
  }

  // 재생 상태 UI 동기화
  function updatePlaybackUI(playing) {
    isPlaying = playing;

    // 카세트 본체 및 데크
    if (heroTape) heroTape.classList.toggle('playing', playing);
    if (tapeDeck) tapeDeck.classList.toggle('playing', playing);
    if (deckPlayBtn) {
      deckPlayBtn.classList.toggle('is-playing', playing);
      if (deckPlayLabel) deckPlayLabel.textContent = playing ? '일시정지' : '재생';
      deckPlayBtn.setAttribute('title', playing ? '일시정지 (BGM)' : '재생 (1979 라운지 재즈)');
    }

    // 플로팅 바
    if (bgmBar) bgmBar.classList.toggle('playing', playing);
    if (bgmPlayBtn) {
      bgmPlayBtn.textContent = playing ? '❚❚' : '▶';
      bgmPlayBtn.setAttribute('title', playing ? '일시정지' : '재생');
    }
    if (bgmDiscBtn) {
      bgmDiscBtn.setAttribute('title', playing ? '일시정지' : '재생');
    }
  }

  // 재생 실행
  function playAudio() {
    if (!audio.src) {
      audio.src = PLAYLIST[currentIndex].file;
    }
    audio.play().then(function () {
      updatePlaybackUI(true);
    }).catch(function (err) {
      console.warn('재즈 BGM 재생 대기 (사용자 상호작용 필요):', err);
      updatePlaybackUI(false);
    });
  }

  // 일시정지 실행
  function pauseAudio() {
    audio.pause();
    updatePlaybackUI(false);
  }

  // 정지 실행 (되감기 및 카운터 초기화)
  function stopAudio() {
    audio.pause();
    audio.currentTime = 0;
    updatePlaybackUI(false);
    if (tapeCounter) tapeCounter.textContent = '0 0 0 0';
  }

  // 재생/일시정지 토글
  function togglePlay() {
    if (audio.paused) {
      playAudio();
    } else {
      pauseAudio();
    }
  }

  // 이전 곡
  function prevTrack() {
    if (audio.currentTime > 3) {
      audio.currentTime = 0;
      if (audio.paused) playAudio();
    } else {
      loadTrack(currentIndex - 1, true);
    }
  }

  // 다음 곡
  function nextTrack() {
    loadTrack(currentIndex + 1, true);
  }

  // 음소거 토글
  function toggleMute() {
    audio.muted = !audio.muted;
    if (bgmMuteBtn) {
      bgmMuteBtn.textContent = audio.muted ? '🔇' : '🔊';
      bgmMuteBtn.setAttribute('title', audio.muted ? '소리 켜기' : '음소거');
    }
  }

  // 카세트 카운터 업데이트 (초 단위 디지털 카운트)
  audio.addEventListener('timeupdate', function () {
    if (!tapeCounter) return;
    var s = Math.floor(audio.currentTime);
    var min = Math.floor(s / 60);
    var sec = s % 60;
    var mStr = (min < 10 ? '0' : '') + min;
    var sStr = (sec < 10 ? '0' : '') + sec;
    tapeCounter.textContent = mStr.charAt(0) + ' ' + mStr.charAt(1) + ' ' + sStr.charAt(0) + ' ' + sStr.charAt(1);
  });

  // 한 곡 끝나면 다음 곡 자동 연속 재생
  audio.addEventListener('ended', function () {
    nextTrack();
  });

  // 데크 버튼 이벤트 연결
  if (deckPlayBtn) deckPlayBtn.addEventListener('click', togglePlay);
  if (deckStopBtn) deckStopBtn.addEventListener('click', stopAudio);
  if (deckPrevBtn) deckPrevBtn.addEventListener('click', prevTrack);
  if (deckNextBtn) deckNextBtn.addEventListener('click', nextTrack);

  // 플로팅 바 이벤트 연결
  if (bgmPlayBtn) bgmPlayBtn.addEventListener('click', togglePlay);
  if (bgmDiscBtn) bgmDiscBtn.addEventListener('click', togglePlay);
  if (bgmPrevBtn) bgmPrevBtn.addEventListener('click', prevTrack);
  if (bgmNextBtn) bgmNextBtn.addEventListener('click', nextTrack);
  if (bgmMuteBtn) bgmMuteBtn.addEventListener('click', toggleMute);
  if (bgmInfoBtn) bgmInfoBtn.addEventListener('click', nextTrack);

  // 초기화
  loadTrack(0, false);

})();
