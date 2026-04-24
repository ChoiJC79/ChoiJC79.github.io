// ===========================
// 모달 관리
// ===========================

// 모달 요소
const modal = document.getElementById('modal');
const modalOverlay = document.getElementById('modalOverlay');
const modalClose = document.getElementById('modalClose');
const modalBody = document.getElementById('modalBody');

// 모달 콘텐츠 정의
const modalContents = {
    about: {
        emoji: '👋',
        title: '소개',
        content: `
            <p class="modal-text">안녕하세요, 저는 최JC79입니다.</p>
            <p class="modal-text">지방행정과 지역 발전에 관심을 가지고 연구하고 있습니다. 공직 내부자료를 기반한 실증 연구를 통해 지방정부의 정책 효과성과 행정 혁신에 대해 탐구합니다.</p>
            <div class="modal-section">
                <div class="modal-section-title">전문 분야</div>
                <ul class="modal-list">
                    <li>지방행정론</li>
                    <li>지방자치와 주민참여</li>
                    <li>지역 정책 분석</li>
                    <li>지방정부 성과 평가</li>
                </ul>
            </div>
        `
    },
    'writings-link': {
        emoji: '✍️',
        title: '글쓰기',
        content: `
            <p class="modal-text">일상의 생각과 경험, 다양한 자료에 대한 의견을 기록합니다.</p>
            <div class="modal-section">
                <div class="modal-section-title">일기</div>
                <p class="modal-text">매일의 경험과 감정을 기록하는 공간입니다.</p>
            </div>
            <div class="modal-section">
                <div class="modal-section-title">리뷰</div>
                <p class="modal-text">책, 논문, 영화, 팟캐스트 등 다양한 콘텐츠에 대한 의견과 평가를 작성합니다.</p>
            </div>
            <p class="modal-text" style="margin-top: var(--spacing-lg);">
                <a href="writings.html" style="color: var(--primary-blue); text-decoration: none; font-weight: 600;">글쓰기 페이지로 이동 →</a>
            </p>
        `
    },
    research: {
        emoji: '📚',
        title: '연구',
        content: `
            <div class="modal-section">
                <div class="modal-section-title">연구 주제</div>
                <p class="modal-text">자유로운 영혼의 지방행정 연구자</p>
                <ul class="modal-list">
                    <li>지방정부 정책의 실제 효과 분석</li>
                    <li>공직 내부 자료 기반 실증 연구</li>
                    <li>지역사회 발전과 주민참여</li>
                    <li>지방자치제도의 개선 방향</li>
                </ul>
            </div>
            <div class="modal-section">
                <div class="modal-section-title">연구 성과</div>
                <ul class="modal-list">
                    <li>논문 1-2편 발표 중</li>
                    <li>지방정부 정책 자문 참여</li>
                    <li>학술 세미나 발표</li>
                </ul>
            </div>
        `
    },
    contact: {
        emoji: '📞',
        title: '연락하기',
        content: `
            <div class="modal-section">
                <div class="modal-section-title">연락 방법</div>
                <ul class="modal-list">
                    <li><strong>이메일:</strong> 문의하기</li>
                    <li><strong>SNS:</strong> 개인 계정 확인</li>
                    <li><strong>기관:</strong> 소속 기관 참조</li>
                </ul>
            </div>
            <div class="modal-section">
                <div class="modal-section-title">협업 및 제안</div>
                <p class="modal-text">지방행정 관련 연구, 자문, 기고 제안을 환영합니다. 위 연락처를 통해 문의주세요.</p>
            </div>
        `
    },
    timeline: {
        emoji: '📅',
        title: '일정',
        content: `
            <div class="modal-section">
                <div class="modal-section-title">주요 일정</div>
                <ul class="modal-list">
                    <li>논문 발표 및 세미나 참여</li>
                    <li>지방정부 정책 연구 진행</li>
                    <li>학술 저널 투고</li>
                    <li>학술 회의 발표</li>
                </ul>
            </div>
            <div class="modal-section">
                <div class="modal-section-title">진행 중</div>
                <p class="modal-text">현재 지방자치 관련 연구를 진행 중입니다. 관심 있는 분야는 블로그를 통해 공유하겠습니다.</p>
            </div>
        `
    },
    projects: {
        emoji: '🔧',
        title: '프로젝트',
        content: `
            <div class="modal-section">
                <div class="modal-section-title">진행 중인 프로젝트</div>
                <ul class="modal-list">
                    <li><strong>지방정부 정책 효과성 분석:</strong> 공직 내부자료 기반 실증 연구</li>
                    <li><strong>지역 주민참여 연구:</strong> 지방자치와 시민 참여 방식 분석</li>
                    <li><strong>블로그 운영:</strong> 지방행정 관련 글쓰기 및 기록</li>
                </ul>
            </div>
            <div class="modal-section">
                <div class="modal-section-title">향후 계획</div>
                <p class="modal-text">지역 발전을 위한 정책 개선 방안 모색 및 학술 성과 발표를 목표로 합니다.</p>
            </div>
        `
    }
};

// 모달 열기
function openModal(modalType) {
    const content = modalContents[modalType];
    if (!content) return;

    modalBody.innerHTML = `
        <div class="modal-title">
            <span>${content.emoji}</span>
            <span>${content.title}</span>
        </div>
        ${content.content}
    `;

    modal.classList.add('active');
    document.body.style.overflow = 'hidden';
}

// 모달 닫기
function closeModal() {
    modal.classList.remove('active');
    document.body.style.overflow = '';
}

// 모달 이벤트 리스너
modalOverlay.addEventListener('click', closeModal);
modalClose.addEventListener('click', closeModal);

// ESC 키로 모달 닫기
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && modal.classList.contains('active')) {
        closeModal();
    }
});

// ===========================
// 카드 클릭 이벤트
// ===========================

document.querySelectorAll('.card[data-modal]').forEach(card => {
    card.addEventListener('click', (e) => {
        e.preventDefault();
        const modalType = card.dataset.modal;
        openModal(modalType);
    });
});

// ===========================
// 초기화 함수
// ===========================

// 페이지 로드 시 날짜 자동 설정 (writings.js가 로드되기 전에 실행 가능하도록)
function initializeDateInputs() {
    const diaryDateInput = document.getElementById('diary-date');
    const reviewDateInput = document.getElementById('review-date');

    if (diaryDateInput) {
        const today = new Date().toISOString().split('T')[0];
        diaryDateInput.value = today;
    }
}

// DOM이 로드되면 실행
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeDateInputs);
} else {
    initializeDateInputs();
}