/* ============================================================
   script.js — choijc79.github.io
   기능: 모달, 탭, 일기 CRUD, 리뷰 CRUD, 아카이브, 로컬스토리지
   ============================================================ */

/* ============================================================
   1. 공통 유틸리티
   ============================================================ */

/**
 * 로컬스토리지 래퍼: 안전한 읽기/쓰기
 */
const Storage = {
  get(key) {
    try {
      return JSON.parse(localStorage.getItem(key)) || [];
    } catch {
      return [];
    }
  },
  set(key, data) {
    try {
      localStorage.setItem(key, JSON.stringify(data));
    } catch (e) {
      console.warn('Storage 저장 실패:', e);
    }
  }
};

const DIARY_KEY  = 'choi_diaries';
const REVIEW_KEY = 'choi_reviews';

/**
 * 오늘 날짜를 YYYY-MM-DD 형식으로 반환
 */
function todayStr() {
  return new Date().toISOString().slice(0, 10);
}

/**
 * YYYY-MM-DD를 한국식 날짜로 변환
 */
function fmtDate(str) {
  if (!str) return '';
  const [y, m, d] = str.split('-');
  return `${y}년 ${parseInt(m)}월 ${parseInt(d)}일`;
}

/**
 * HTML 특수문자 이스케이프 (XSS 방지)
 */
function esc(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

/* ============================================================
   2. 모달 시스템 (index.html)
   ============================================================ */

function initModals() {
  // 카드 클릭 → 모달 열기
  document.querySelectorAll('[data-modal]').forEach(card => {
    card.addEventListener('click', () => openModal(card.dataset.modal));
    // 키보드 접근성
    card.addEventListener('keydown', e => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        openModal(card.dataset.modal);
      }
    });
  });

  // 닫기 버튼
  document.querySelectorAll('.modal-close').forEach(btn => {
    btn.addEventListener('click', () => closeModal(btn.closest('.modal-overlay')));
  });

  // 바깥 클릭으로 닫기
  document.querySelectorAll('.modal-overlay').forEach(overlay => {
    overlay.addEventListener('click', e => {
      if (e.target === overlay) closeModal(overlay);
    });
  });

  // ESC 키로 닫기
  document.addEventListener('keydown', e => {
    if (e.key === 'Escape') {
      document.querySelectorAll('.modal-overlay.active').forEach(closeModal);
    }
  });
}

function openModal(id) {
  const modal = document.getElementById(id);
  if (!modal) return;
  modal.classList.add('active');
  document.body.style.overflow = 'hidden';
  // 닫기 버튼에 포커스
  const closeBtn = modal.querySelector('.modal-close');
  if (closeBtn) closeBtn.focus();
}

function closeModal(overlay) {
  if (!overlay) return;
  overlay.classList.remove('active');
  document.body.style.overflow = '';
}

/* ============================================================
   3. 탭 시스템 (writings.html)
   ============================================================ */

function initTabs() {
  const tabBtns = document.querySelectorAll('.tab-btn');
  if (!tabBtns.length) return;

  tabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      // 버튼 상태 전환
      tabBtns.forEach(b => { b.classList.remove('active'); b.setAttribute('aria-selected','false'); });
      btn.classList.add('active');
      btn.setAttribute('aria-selected','true');

      // 패널 전환
      document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));
      const target = document.getElementById(btn.dataset.tab);
      if (target) target.classList.add('active');

      // 아카이브 탭 진입 시 렌더
      if (btn.dataset.tab === 'tab-archive') renderArchive();
    });
  });
}

/* ============================================================
   4. 일기 기능
   ============================================================ */

let editingDiaryId = null; // 수정 중인 일기 ID

function initDiary() {
  const dateInput = document.getElementById('diary-date');
  if (dateInput) dateInput.value = todayStr();

  const saveBtn   = document.getElementById('diary-save-btn');
  const updateBtn = document.getElementById('diary-update-btn');
  const cancelBtn = document.getElementById('diary-cancel-btn');

  if (saveBtn)   saveBtn.addEventListener('click', saveDiary);
  if (updateBtn) updateBtn.addEventListener('click', updateDiary);
  if (cancelBtn) cancelBtn.addEventListener('click', cancelEditDiary);

  renderDiaries();
}

/** 일기 저장 */
function saveDiary() {
  const title   = document.getElementById('diary-title')?.value.trim();
  const date    = document.getElementById('diary-date')?.value;
  const mood    = document.getElementById('diary-mood')?.value;
  const content = document.getElementById('diary-content')?.value.trim();
  const tags    = document.getElementById('diary-tags')?.value
                    .split(',').map(t => t.trim()).filter(Boolean);

  if (!title) { alert('제목을 입력해주세요.'); return; }
  if (!date)  { alert('날짜를 선택해주세요.'); return; }
  if (!content){ alert('내용을 입력해주세요.'); return; }

  const diaries = Storage.get(DIARY_KEY);
  diaries.unshift({
    id:      Date.now(),
    title, date, mood, content, tags,
    created: new Date().toISOString()
  });
  Storage.set(DIARY_KEY, diaries);

  clearDiaryForm();
  renderDiaries();
}

/** 일기 수정 완료 */
function updateDiary() {
  const title   = document.getElementById('diary-title')?.value.trim();
  const date    = document.getElementById('diary-date')?.value;
  const mood    = document.getElementById('diary-mood')?.value;
  const content = document.getElementById('diary-content')?.value.trim();
  const tags    = document.getElementById('diary-tags')?.value
                    .split(',').map(t => t.trim()).filter(Boolean);

  if (!title)   { alert('제목을 입력해주세요.'); return; }
  if (!content) { alert('내용을 입력해주세요.'); return; }

  let diaries = Storage.get(DIARY_KEY);
  diaries = diaries.map(d =>
    d.id === editingDiaryId ? { ...d, title, date, mood, content, tags } : d
  );
  Storage.set(DIARY_KEY, diaries);

  cancelEditDiary();
  renderDiaries();
}

/** 일기 수정 모드 진입 */
function editDiary(id) {
  const diaries = Storage.get(DIARY_KEY);
  const entry   = diaries.find(d => d.id === id);
  if (!entry) return;

  editingDiaryId = id;
  document.getElementById('diary-title').value   = entry.title;
  document.getElementById('diary-date').value    = entry.date;
  document.getElementById('diary-mood').value    = entry.mood || '';
  document.getElementById('diary-content').value = entry.content;
  document.getElementById('diary-tags').value    = (entry.tags || []).join(', ');

  // 버튼 교체
  document.getElementById('diary-save-btn').style.display   = 'none';
  document.getElementById('diary-update-btn').style.display = 'inline-block';
  document.getElementById('diary-cancel-btn').style.display = 'inline-block';

  window.scrollTo({ top: 0, behavior: 'smooth' });
}

/** 일기 수정 취소 */
function cancelEditDiary() {
  editingDiaryId = null;
  clearDiaryForm();
  document.getElementById('diary-save-btn').style.display   = 'inline-block';
  document.getElementById('diary-update-btn').style.display = 'none';
  document.getElementById('diary-cancel-btn').style.display = 'none';
}

/** 일기 삭제 */
function deleteDiary(id) {
  if (!confirm('이 일기를 삭제하시겠습니까?')) return;
  let diaries = Storage.get(DIARY_KEY);
  diaries = diaries.filter(d => d.id !== id);
  Storage.set(DIARY_KEY, diaries);
  renderDiaries();
}

/** 일기 폼 초기화 */
function clearDiaryForm() {
  ['diary-title','diary-content','diary-tags'].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.value = '';
  });
  const mood = document.getElementById('diary-mood');
  if (mood) mood.value = '';
  const date = document.getElementById('diary-date');
  if (date) date.value = todayStr();
}

/** 일기 목록 렌더 */
function renderDiaries() {
  const list = document.getElementById('diary-list');
  if (!list) return;

  const diaries = Storage.get(DIARY_KEY);
  if (!diaries.length) {
    list.innerHTML = '<p class="empty-msg">아직 작성된 일기가 없습니다. 첫 번째 일기를 기록해보세요. ✍️</p>';
    return;
  }

  list.innerHTML = diaries.map(d => `
    <div class="entry-card" data-id="${d.id}">
      <div class="entry-header">
        <div>
          <span class="entry-mood">${esc(d.mood || '')}</span>
          <span class="entry-title-main" style="margin-left:6px">${esc(d.title)}</span>
        </div>
        <span class="entry-meta">${fmtDate(d.date)}</span>
      </div>
      <p class="entry-body">${esc(d.content)}</p>
      ${d.tags && d.tags.length ? `
        <div class="entry-tags">
          ${d.tags.map(t => `<span class="tag-chip">${esc(t)}</span>`).join('')}
        </div>` : ''}
      <div class="entry-actions">
        <button class="btn-sm btn-edit"   onclick="editDiary(${d.id})">수정</button>
        <button class="btn-sm btn-delete" onclick="deleteDiary(${d.id})">삭제</button>
      </div>
    </div>
  `).join('');
}

/* ============================================================
   5. 리뷰 기능
   ============================================================ */

let selectedRating = 0;

function initReview() {
  // 별점 클릭
  document.querySelectorAll('.star-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      selectedRating = parseInt(btn.dataset.val);
      updateStars();
    });
    // 호버 미리보기
    btn.addEventListener('mouseenter', () => highlightStars(parseInt(btn.dataset.val)));
    btn.addEventListener('mouseleave', () => updateStars());
  });

  const saveBtn = document.getElementById('review-save-btn');
  if (saveBtn) saveBtn.addEventListener('click', saveReview);

  renderReviews();
}

/** 별점 표시 업데이트 */
function updateStars() {
  document.querySelectorAll('.star-btn').forEach(btn => {
    btn.classList.toggle('active', parseInt(btn.dataset.val) <= selectedRating);
  });
}

function highlightStars(val) {
  document.querySelectorAll('.star-btn').forEach(btn => {
    btn.classList.toggle('active', parseInt(btn.dataset.val) <= val);
  });
}

/** 리뷰 저장 */
function saveReview() {
  const type      = document.getElementById('review-type')?.value;
  const title     = document.getElementById('review-title')?.value.trim();
  const author    = document.getElementById('review-author')?.value.trim();
  const content   = document.getElementById('review-content')?.value.trim();
  const recommend = document.getElementById('review-recommend')?.value;

  if (!title)   { alert('제목을 입력해주세요.'); return; }
  if (!content) { alert('내용을 입력해주세요.'); return; }

  const reviews = Storage.get(REVIEW_KEY);
  reviews.unshift({
    id: Date.now(),
    type, title, author,
    rating: selectedRating,
    content, recommend,
    date:    todayStr(),
    created: new Date().toISOString()
  });
  Storage.set(REVIEW_KEY, reviews);

  // 폼 초기화
  ['review-title','review-author','review-content'].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.value = '';
  });
  selectedRating = 0;
  updateStars();

  renderReviews();
}

/** 리뷰 삭제 */
function deleteReview(id) {
  if (!confirm('이 리뷰를 삭제하시겠습니까?')) return;
  let reviews = Storage.get(REVIEW_KEY);
  reviews = reviews.filter(r => r.id !== id);
  Storage.set(REVIEW_KEY, reviews);
  renderReviews();
}

/** 별점 문자열 생성 */
function starsHtml(n) {
  return '★'.repeat(n || 0) + '☆'.repeat(5 - (n || 0));
}

/** 리뷰 목록 렌더 */
function renderReviews() {
  const list = document.getElementById('review-list');
  if (!list) return;

  const reviews = Storage.get(REVIEW_KEY);
  if (!reviews.length) {
    list.innerHTML = '<p class="empty-msg">아직 작성된 리뷰가 없습니다. 읽은 책이나 본 영화를 기록해보세요. 📖</p>';
    return;
  }

  list.innerHTML = reviews.map(r => `
    <div class="entry-card" data-id="${r.id}">
      <div class="entry-header">
        <div>
          <span class="tag-chip" style="margin-right:6px">${esc(r.type || '')}</span>
          <span class="entry-title-main">${esc(r.title)}</span>
          ${r.author ? `<span class="entry-meta" style="margin-left:8px">— ${esc(r.author)}</span>` : ''}
        </div>
        <span class="entry-meta">${fmtDate(r.date)}</span>
      </div>
      <div style="color:#f59e0b;font-size:1.05rem;margin:6px 0 4px;">
        ${starsHtml(r.rating)}
        <span class="entry-meta" style="margin-left:8px">${esc(r.recommend || '')}</span>
      </div>
      <p class="entry-body">${esc(r.content)}</p>
      <div class="entry-actions">
        <button class="btn-sm btn-delete" onclick="deleteReview(${r.id})">삭제</button>
      </div>
    </div>
  `).join('');
}

/* ============================================================
   6. 아카이브 기능
   ============================================================ */

function initArchive() {
  const yearSel = document.getElementById('filter-year');
  const typeSel = document.getElementById('filter-type');

  if (yearSel) {
    // 저장된 데이터에서 연도 목록 추출
    const years = new Set();
    [...Storage.get(DIARY_KEY), ...Storage.get(REVIEW_KEY)].forEach(item => {
      if (item.date) years.add(item.date.slice(0, 4));
    });
    // 연도 내림차순 옵션 추가
    [...years].sort((a, b) => b - a).forEach(y => {
      const opt = document.createElement('option');
      opt.value = y; opt.textContent = y + '년';
      yearSel.appendChild(opt);
    });

    yearSel.addEventListener('change', renderArchive);
  }
  if (typeSel) typeSel.addEventListener('change', renderArchive);
}

/** 아카이브 목록 렌더 */
function renderArchive() {
  const list = document.getElementById('archive-list');
  if (!list) return;

  const yearVal = document.getElementById('filter-year')?.value || 'all';
  const typeVal = document.getElementById('filter-type')?.value || 'all';

  const diaries = Storage.get(DIARY_KEY).map(d => ({ ...d, _type: 'diary' }));
  const reviews = Storage.get(REVIEW_KEY).map(r => ({ ...r, _type: 'review' }));

  let all = [...diaries, ...reviews].sort((a, b) =>
    new Date(b.created || 0) - new Date(a.created || 0)
  );

  // 필터 적용
  if (yearVal !== 'all') all = all.filter(i => (i.date || '').startsWith(yearVal));
  if (typeVal !== 'all') all = all.filter(i => i._type === typeVal);

  if (!all.length) {
    list.innerHTML = '<p class="empty-msg">조건에 해당하는 글이 없습니다.</p>';
    return;
  }

  list.innerHTML = all.map(item => {
    const badge = item._type === 'diary' ? '📔 일기' : '⭐ 리뷰';
    const sub   = item._type === 'diary'
      ? (item.mood ? esc(item.mood) : '')
      : (item.type ? esc(item.type) : '');
    return `
      <div class="entry-card">
        <div class="entry-header">
          <div>
            <span class="tag-chip" style="margin-right:6px">${badge}</span>
            ${sub ? `<span class="tag-chip" style="margin-right:6px">${sub}</span>` : ''}
            <span class="entry-title-main">${esc(item.title)}</span>
          </div>
          <span class="entry-meta">${fmtDate(item.date)}</span>
        </div>
        <p class="entry-body">${esc(item.content)}</p>
      </div>
    `;
  }).join('');
}

/* ============================================================
   7. 페이지 초기화 — DOMContentLoaded
   ============================================================ */

document.addEventListener('DOMContentLoaded', () => {
  // index.html: 모달
  if (document.querySelector('.modal-overlay')) {
    initModals();
  }

  // writings.html: 탭, 일기, 리뷰, 아카이브
  if (document.querySelector('.tab-nav')) {
    initTabs();
    initDiary();
    initReview();
    initArchive();
  }
});

/* ============================================================
   8. 전역 노출 (HTML onclick 속성에서 호출)
   ============================================================ */
window.editDiary   = editDiary;
window.deleteDiary = deleteDiary;
window.deleteReview = deleteReview;
