# choijc79.github.io — 사이트 완전 복제 프롬프트

> 이 문서 하나로 사이트 전체를 처음부터 재현하거나 새 페이지·칼럼을 추가할 수 있도록 작성됨.  
> 운영자: 최승환 (충청북도 제천시청 팀장, 도시경영학 박사과정)  
> 저장소: `choijc79/choijc79.github.io` (GitHub Pages, main 브랜치)

---

## 1. 사이트 개요

- **성격**: 지방행정 실무자의 개인 포트폴리오·칼럼 사이트
- **기술**: 순수 HTML/CSS/JS (프레임워크 없음) + Python 자동 배포 스크립트
- **배포**: `publish.py` → GitHub API → GitHub Pages (BAT 파일로만 실행)
- **URL**: `https://choijc79.github.io/`
- **주요 콘텐츠**: 칼럼, 행정 제안 기록, 논문 포트폴리오, 투어·위스키 가이드, 정리노트

---

## 2. 디자인 시스템

### 2-1. CSS 변수 (라이트 / 다크 양립)

```css
/* 라이트 모드 (기본) */
:root {
  --bg:      #F4F0E8;   /* 페이지 배경 — 크림 */
  --surface: #ECE8DE;   /* 카드·패널 배경 */
  --border:  #D4CEBC;   /* 선, 구분자 */
  --text:    #1A1410;   /* 본문 텍스트 */
  --ink:     #2A2018;   /* 제목·강조 텍스트 */
  --muted:   #7A6A56;   /* 보조 텍스트, 날짜 */
  --accent:  #E07828;   /* 주요 포인트 색 (주황) */
  --red:     #D96820;   /* 호버 강조 */
  --light:   #FDFAF4;   /* 가장 밝은 면 */
}

/* 다크 모드 */
[data-theme="dark"] {
  --bg:      #0d1117;
  --surface: #161b22;
  --border:  #2c3240;
  --text:    #E8E0D0;
  --ink:     #F0E8D8;
  --muted:   #8b8070;
  --accent:  #F08840;
  --red:     #E07830;
  --light:   #161b22;
}
```

> **다크 모드 전용 페이지** (column.html, memo.html 등 publish.py가 생성하는 페이지)는  
> 아래 별도 팔레트를 사용:
> ```
> --bg:#0d1117  --surface:#161b22  --border:#30363d
> --text:#e6edf3  --muted:#8b949e  --accent:#58a6ff
> --amber:#d29922  --green:#3fb950  --lake:#5cbcd4  --purple:#bc8cff
> ```

### 2-2. 폰트

```html
<link href="https://fonts.googleapis.com/css2?family=Noto+Serif+KR:wght@300;400;600;700&family=Noto+Sans+KR:wght@300;400;500;700&display=swap" rel="stylesheet">
```

| 용도 | 폰트 | weight |
|------|------|--------|
| 제목, 로고, 강조 | Noto Serif KR | 700 |
| 본문 | Noto Sans KR | 300 (기본) |
| 카드 설명, 날짜 | Noto Sans KR | 300~400 |

### 2-3. 주요 UI 패턴

#### 네비게이션
```html
<nav id="nav">
  <a class="nav-logo" href="/">CHOI SEUNG-HWAN</a>
  <ul class="nav-links">
    <li><a href="/about.html">소개</a></li>
    <li><a href="/research.html">연구</a></li>
    <li><a href="/column.html">칼럼</a></li>
    <li><a href="/tour.html">투어</a></li>
    <li><a href="/whisky.html">위스키</a></li>
    <li><a href="/memo.html">정리노트</a></li>
  </ul>
  <button id="theme-btn" onclick="toggleTheme()">DARK</button>
</nav>
```
- 스크롤 전: 투명 + 흰 글씨
- 스크롤 후: `nav.light-nav` 클래스 추가 → `var(--bg)` 배경 + 포인트 색 로고

#### 카드 그리드 (cat-grid)
```html
<div class="cat-grid">  <!-- 3열 grid, gap:1px, background:var(--border) -->
  <a class="cat-card" href="...">
    <span class="cat-icon">🗂️</span>
    <div class="cat-title">제목</div>
    <div class="cat-desc">설명</div>
    <div class="cat-arrow">→ 바로가기</div>
  </a>
  <a class="cat-card wide" href="..."> <!-- wide: grid-column:span 2 -->
    ...
  </a>
</div>
```
- 호버 시: 상단 2px 주황 바(`::before`) 애니메이션

#### 섹션 구분선 레이블
```html
<div class="cat-section-label">
  COLUMNS  <!-- font-size:10px, letter-spacing:0.2em, ::after로 1px 선 -->
</div>
```

---

## 3. 파일 구조

```
D:\나를 정리하는 프로젝트\
│
├── index.html          ← 홈페이지 (hero + cat-grid 6칸 + 링크 모음)
├── about.html          ← 소개 페이지
├── research.html       ← 연구·논문 포트폴리오
├── column.html         ← 칼럼 목록 (publish.py가 자동 생성)
├── tour.html           ← 투어 기사 목록
├── whisky.html         ← 위스키 가이드 목록
├── memo.html           ← 정리노트 (publish.py가 자동 생성)
│
├── publish.py          ← GitHub API 자동 배포 스크립트
├── 🚀 사이트에 올리기.bat  ← publish.py 실행 래퍼 (더블클릭으로 배포)
│
├── 💬 칼럼·기고.md     ← 칼럼 원본 마크다운
├── 📝 정리노트.md      ← 정리노트 원본 마크다운
│
├── img/                ← 로컬 이미지 (칼럼 썸네일 등)
│   ├── col_*.jpg       ← 칼럼별 썸네일
│   └── 만남의광장.JPG 등
│
├── CLAUDE.md           ← Claude 작업 지침 (이 파일 상위 지침)
└── SITE_PROMPT.md      ← 이 파일
```

---

## 4. publish.py 구조

### 4-1. 핵심 함수

| 함수 | 역할 |
|------|------|
| `gh_request(method, path, body)` | GitHub API 호출 (GET/PUT) |
| `get_file_sha(path)` | 기존 파일 SHA 조회 (업데이트 시 필요) |
| `push_file(path, content, message)` | 텍스트 파일 GitHub에 업로드 |
| `push_binary_file(remote, local, msg)` | 이미지 등 바이너리 업로드 |
| `parse_columns(md_text)` | 칼럼 마크다운 파싱 |
| `build_column_html()` | column.html 전체 HTML 생성 |
| `build_memo_html()` | memo.html 전체 HTML 생성 |
| `patch_index_html(now_str)` | 로컬 index.html 그대로 업로드 |
| `push_local(filename, remote_path)` | 로컬 파일 → GitHub |
| `main()` | 전체 배포 오케스트레이션 |

### 4-2. PHOTO_MAP 시스템

```python
PHOTO_MAP = [
    # 형식: ([키워드 리스트], 이미지_경로_또는_Unsplash_ID)
    (['청풍랜드','만남의 광장'], '/img/만남의광장.JPG'),   # 로컬 이미지
    (['ENFP','ENTP'], 'photo-1722137148592-e0aa4a8061d8'), # Unsplash ID
]
```

- **로컬 이미지**: `/img/파일명.jpg` 형태, GitHub에 바이너리로 업로드됨
- **Unsplash**: `https://images.unsplash.com/{ID}?w=800&h=520&fit=crop&auto=format&q=80`
- 칼럼 제목 + 태그를 합쳐 키워드 매칭 → 첫 번째 매칭 항목 사용
- 매칭 없으면 카테고리별 폴백 → 최종 폴백은 기본 사진 1장

**새 칼럼에 로컬 사진 추가하는 방법:**
1. `img/` 폴더에 `col_제목키워드.jpg` 저장
2. PHOTO_MAP에 추가: `(['키워드1','키워드2'], '/img/col_제목키워드.jpg'),`
3. BAT 실행 (publish.py가 바이너리로 자동 업로드)

### 4-3. 칼럼 파싱 규칙

```
## 칼럼 제목 | YYYY-MM-DD | 태그1·태그2·태그3

본문 첫 번째 문단...

두 번째 문단...

---
```

- 구분자: `\n---\n`
- 헤더 정규식: `^##\s+(.+?)\s*\|\s*(\d{4}-\d{2}-\d{2})\s*\|\s*(.+)$`
- 태그는 `·`로 구분 (가운뎃점)
- 발행 순서: 파일 내 순서 역순 (최신이 상단)

### 4-4. column.html 생성 구조

```
[필터 바] ← 주요 카테고리 버튼 + 세부 태그 토글
[칼럼 카드 목록] ← 역순, 각 카드에 썸네일·제목·날짜·태그·요약
[전체 본문 모달] ← 카드 클릭 시 슬라이드업 오버레이
```

---

## 5. 칼럼 작성 지침

### 5-1. 파일 위치

`D:\나를 정리하는 프로젝트\💬 칼럼·기고.md`

### 5-2. 형식

```markdown
## 칼럼 제목 | YYYY-MM-DD | 태그1·태그2

본문 단락 1.

본문 단락 2.

---
```

### 5-3. 카테고리 태그 체계

| 주요 카테고리 (필터 버튼) | 세부 태그 예시 |
|--------------------------|---------------|
| 행정혁신 | 제도설계, 디지털행정, 납세편의, 보안, 재산관리 |
| 도시환경 | 도시안전, 스마트행정, 도시경관, 관광정책, 청풍호 |
| 지역공동체 | 마을기업, 사회적경제, 아동문화, 스포츠마케팅 |
| 에세이 | 공직, 가족, 일상, 육아, 건축, 여행, 에스파냐 |

### 5-4. 글쓰기 원칙

**공통**
- 단정적 서술 지양: "~이다" 대신 "~인 것 같다", "~라고 생각한다", "~느껴진다", "~그럴 수 있다"
- 독자에게 결론을 강요하지 않고 함께 생각하는 어조
- 상투적 표현 배제: "의의가 있다", "매우 중요하다" 등 금지
- "에스파냐" 사용 (스페인 ×)

**에세이** (개인 서사·일상·여행·성찰)
- 겸손하고 자상한 어조, 독자와 같은 눈높이
- "나는 이랬다"보다 "그 경험이 이것을 가르쳐줬다"
- 결말은 열린 여운, 교훈 강요 없이

**행정·정책** (업무 분석·제도)
- 진중하고 신뢰감 있는 어조, 현장 경험의 무게감
- 문제 제기보다 구조 분석 중심
- 사실과 논리로 서술, 비판은 구체적 근거와 함께

**아이디어·제안** (정책 제안·도시경영)
- 긍정적이고 미래지향적 어조
- 완성형 대안 제시: "문제가 있다"로 끝내지 않고 "이렇게 하면 된다"로
- 자원 배분 효율성, 지속가능성, 실행 가능한 Action Plan 포함

---

## 6. HTML 페이지 공통 템플릿

### 6-1. 헤드 (필수 포함)

```html
<!DOCTYPE html>
<html lang="ko" data-theme="light">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>페이지 제목 | 최승환</title>
<meta name="description" content="페이지 설명">
<meta property="og:title" content="페이지 제목 | 최승환">
<meta property="og:description" content="페이지 설명">
<meta property="og:type" content="website">
<meta property="og:url" content="https://choijc79.github.io/페이지.html">
<link href="https://fonts.googleapis.com/css2?family=Noto+Serif+KR:wght@300;400;600;700&family=Noto+Sans+KR:wght@300;400;500;700&display=swap" rel="stylesheet">
```

### 6-2. 네비게이션 JS (공통)

```javascript
// 스크롤에 따른 nav 스타일 전환
window.addEventListener('scroll', () => {
  document.getElementById('nav').classList.toggle('light-nav', window.scrollY > 60);
});

// 다크/라이트 토글
function toggleTheme() {
  const html = document.documentElement;
  const isDark = html.getAttribute('data-theme') === 'dark';
  html.setAttribute('data-theme', isDark ? 'light' : 'dark');
  document.getElementById('theme-btn').textContent = isDark ? 'DARK' : 'LIGHT';
  localStorage.setItem('theme', isDark ? 'light' : 'dark');
}
// 초기 테마 적용
(function(){
  const t = localStorage.getItem('theme') || 'light';
  document.documentElement.setAttribute('data-theme', t);
  document.addEventListener('DOMContentLoaded', () => {
    const btn = document.getElementById('theme-btn');
    if (btn) btn.textContent = t === 'dark' ? 'LIGHT' : 'DARK';
  });
})();
```

### 6-3. tour.html / whisky.html 카드 패턴

```html
<article class="article-card" data-tags="태그1 태그2">
  <div class="card-thumb">
    <img src="이미지URL" alt="설명" loading="lazy">
    <div class="card-overlay">
      <span class="card-status">완료</span>  <!-- 또는 진행중 / 예정 -->
    </div>
  </div>
  <div class="card-body">
    <div class="card-meta">
      <span class="card-date">YYYY.MM.DD</span>
      <span class="card-tag">태그</span>
    </div>
    <h2 class="card-title">제목</h2>
    <p class="card-excerpt">요약문...</p>
    <a class="card-link" href="#">자세히 보기 →</a>
  </div>
</article>
```

---

## 7. publish.py에 새 페이지 연동하는 방법

1. 로컬에 `newpage.html` 작성 (OG 메타태그 포함 필수)
2. `publish.py`의 `main()` 함수에 추가:
   ```python
   print("  [4] newpage.html 업로드 중...")
   push_local("newpage.html", "newpage.html")
   ```
3. `push_local` 함수 존재 확인 (없으면 추가):
   ```python
   def push_local(filename, remote_path, message=None):
       local_path = os.path.join(BASE_DIR, filename)
       if not os.path.exists(local_path):
           print(f"      {filename} 없음 — 건너뜀")
           return False
       with open(local_path, encoding="utf-8") as f:
           html = f.read()
       msg = message or f"{filename} update ({datetime.datetime.now().strftime('%Y-%m-%d %H:%M')})"
       return push_file(remote_path, html, msg)
   ```
4. BAT 파일 실행

---

## 8. 이미지 관리

### 8-1. 로컬 이미지 추가 흐름

```
폰 촬영 → 카카오톡 나에게 보내기 → PC 저장
→ D:\나를 정리하는 프로젝트\img\col_키워드.jpg
→ publish.py PHOTO_MAP에 추가
→ BAT 실행 (자동으로 GitHub에 업로드됨)
```

### 8-2. 권장 이미지 사양

- **형식**: JPG (80% 품질)
- **크기**: 800×520px (2:1.3 비율)
- **파일명**: `col_[키워드].jpg` (영문 소문자, 언더바)
- **효과 추천**: 밝기 -10, 대비 +15, 채도 -15 (어두운 사이트 배경에 맞게)

### 8-3. PHOTO_MAP 추가 예시

```python
# PHOTO_MAP 리스트 안에 추가 (로컬 이미지)
(['키워드1', '키워드2'], '/img/col_파일명.jpg'),

# Unsplash 폴백
(['키워드'], 'photo-[Unsplash-Photo-ID]'),
```

---

## 9. 배포 규칙

| 항목 | 내용 |
|------|------|
| 배포 명령 | `🚀 사이트에 올리기.bat` 더블클릭 |
| 직접 API 호출 | 불가 (샌드박스 네트워크 차단) |
| publish.py 수정 후 | `ast.parse()` 또는 `py_compile`로 문법 검사 필수 |
| 한글 문자열 Edit | 인코딩 잘림 가능 → bash Python 스크립트로 대체 |
| 이미지 업로드 | `push_binary_file()` 함수 사용 |

---

## 10. 오류 대응

| 증상 | 원인 | 해결 |
|------|------|------|
| `IndentationError` | 파일 중간 잘림 | 잘린 위치부터 bash 스크립트로 재작성 |
| `UnicodeDecodeError` | UTF-8 멀티바이트 경계 잘림 | 바이너리로 읽어 잘린 위치 확인 후 복원 |
| 마크다운 파싱 실패 | null 바이트 오염 | `raw.replace(b'\x00', b'')` 후 재저장 |
| GitHub API 403 | 샌드박스 네트워크 차단 | BAT 파일로만 배포 |
| `str.replace()` 무작동 | 매칭 문자열 불일치 | 체크리스트로 검증, bash로 대체 |

---

## 11. 운영자 맥락

| 항목 | 내용 |
|------|------|
| 이름 | 최승환 |
| 소속 | 충청북도 제천시청 팀장 |
| 경력 | 지방행정 20년 |
| 연구 | 도시경영학 박사과정 |
| 논문 주제 | 등록면허세 납세지 불일치가 지방세 세원 역외 유출에 미치는 영향 |
| 관심 분야 | 지방세, 등록면허세, 납세지·물건지 불일치, GIS·공간분석, 업무자동화, 바이크투어, 위스키, 글쓰기 |
| 연락처 | 7979@korea.kr |
| GitHub | choijc79 |

---

## 12. 새 칼럼 추가 체크리스트

```
□ 1. 칼럼 초안 → 채팅창에 먼저 출력 (운영자 확인 후 파일에 추가)
□ 2. 💬 칼럼·기고.md 끝에 추가 (형식 준수)
□ 3. 말투 확인: 단정형 지양, 여지형 표현 사용
□ 4. PHOTO_MAP에 키워드 추가 (사진 있으면 로컬, 없으면 Unsplash)
□ 5. 사진 있으면 img/ 폴더에 저장
□ 6. null 바이트 오염 여부 확인
□ 7. 🚀 사이트에 올리기.bat 실행
```

---

## 13. 향후 추가 가능한 콘텐츠 아이디어

> 이 섹션은 운영자가 직접 채워 나가는 공간. 아래는 예시.

- [ ] 논문 요약 페이지 (`paper.html`)
- [ ] 제천 데이터 시각화 대시보드 확장
- [ ] 바이크 투어 루트 지도 (KakaoMap API 연동)
- [ ] 위스키 테이스팅 노트 DB화
- [ ] 칼럼 RSS 피드 (`feed.xml`)
- [ ] 방명록 (Supabase 연동, 이미 일부 구현됨)
