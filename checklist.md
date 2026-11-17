# 홈페이지 J-Card 개편 (2026-11-17)

범위: 홈(index.html)만. 다른 페이지의 이모지·팔레트는 건드리지 않음.

- [x] 상단 텍스트 메뉴·조감도 아래 칩 줄·모바일 하단 탭바 제거, 얇은 헤더(로고+토글)만 남김
- [x] 홈의 이모지 전부 제거(링크·푸터·날씨 아이콘·BGM 글자)
- [x] 제목 명조(Noto Serif KR), 번호·시간·날짜·삐삐 숫자 고정폭(JetBrains Mono)
- [x] A/B면 트랙리스트를 속지(#F5F2EB 종이, 1px #2C2A29 잉크, 점선)로. 둥근 테두리·그림자 없음
- [x] 날씨·노을, 오늘 뭐 먹지를 모달로 분리(푸터 버튼으로 열기, ESC·바깥 클릭 닫기)
- [x] 즐겨찾기를 푸터 텍스트 링크로
- [x] 하단 BGM 바 제거, 본문 데크 하나만 sticky로 작동
- [x] 팔레트: 종이 #F5F2EB / 월넛 #1C1B1A, 먹 #22201E, 오렌지 #C85A32, 올리브 #3D4B3E
- [x] 라이트·다크, 데스크톱·모바일 스크린샷 확인, 콘솔 오류 없음, 모달 열림 확인
- [x] 커밋·푸시·실서비스 확인

# 이번 주 AI 가이드: anthropics/skills (2026-11-16)

- [x] 트렌드에서 후보 선정(기존 repo 제외), README·라이선스·스킬 원본 확인
- [x] 초안을 채팅창에서 운영자 승인
- [x] 임시 폴더에 설치(`--scope local`) 후 docx·xlsx·pdf 직접 실행·결과 파일 검증, 시험용 설치 제거
- [x] 그림 4장 `img/guides/skills-*.svg`
- [x] `💬 AI가이드.md` 추가, `build_guides.py` 실행, `sitemap.xml` 추가
- [ ] 미시험(pptx·예시 스킬·이름 없는 요청·한국식 서식)은 본문에 밝힘 — 운영자가 써 보고 알려주면 갱신

# kordoc AI 가이드 발행 (2026-11-16)

- [x] kordoc 공식 README·npm·GitHub API로 버전(4.24.80)·스타(2,995)·라이선스(MIT)·Node 20+ 확인
- [x] PDF 변환, HWPX 생성·재읽기, json·chunks, lint를 직접 실행해 실제 출력 확보
- [x] 그림 5장(`img/guides/kordoc-*.svg`): 개요·설치·PDF 예시·HWPX 왕복 예시·MCP 흐름
- [x] `build_guides.py`에 `![설명](경로)` 그림 처리, `css/guides.css`에 `.g-fig` 추가
- [x] `💬 AI가이드.md`에 `claude-and-kordoc` 추가, `python3 build_guides.py` 실행
- [x] `sitemap.xml`에 항목 추가
- [x] 데스크톱 1100px·모바일 390px 확인(가로 넘침 없음)
- [x] '터미널을 못 쓰는 분을 위한 길' 절과 그림(`kordoc-no-terminal.svg`) 추가 (2026-11-16)
- [ ] 미실행 항목(.hwp 원본·OCR·setup)은 본문에 '직접 돌리지 않음'으로 밝힘 — 운영자가 실제 HWP로 확인하면 본문 갱신

# 항공권 검색 (`flights.html`) + 백엔드 배포 (2026-11-13)

- [x] GitHub에서 API 키 없는 오픈소스 조사 → `AWeirdDev/flights`(fast-flights, 구글 플라이츠 스크래핑) 선정
- [x] fast-flights 3.1.0 파서 버그 발견(가격 미확정 itinerary에서 `IndexError`) → `app.py`에 한 줄 패치한 `parse_js` 몽키패치로 우회
- [x] FastAPI 백엔드(`flight-search-api`) 작성, 로컬에서 국내선·국제선·왕복 실제 조회 확인
- [x] 새 저장소 `ChoiJC79/flight-search-api` 생성·푸시, Render 무료 배포 안내(README.md)
- [x] `flights.html` 작성(편도/왕복 폼, 결과 카드, 라이트/다크 테마), `index.html` B7·`tour.html` 내비·`sitemap.xml`·`publish.py` 연결
- [ ] Render에 실제 배포하고 `flights.html`의 `API_BASE`를 배포 URL로 교체
- [ ] 배포 후 실제 브라우저에서 라이트/다크·모바일 확인, git push로 배포

# 제10대 제천시의회 의정분석 대시보드 (`council.html`) 및 일일 자동화 구축 (2026-11-10)

- [x] 제천시의회 유튜브 채널(`UCg3R1CAEaA2VjeXZHQdCSSg`) 2026년 7월 이후 전체 영상 80편 메타데이터·자막 전수 추출
- [x] 의원 14명 성향(2x2 매트릭스·5축 레이더), 5대 회차 간 인과 흐름도, 15건 발언 5단계 해부도(`data/council_data.js`) 생성
- [x] 인터랙티브 의정분석 대시보드 `council.html` 작성 (타임스탬프 즉시 재생 모달·유기적 관계망 포함)
- [x] `index.html` 상단 내비게이션, 카세트 테이프 A면 트랙(`A7 시의회 분석`), 모바일 하단 `#mqb`에 `의회` 탭 연결
- [x] `sitemap.xml` 및 `publish.py` 배포 목록 갱신
- [x] 매일 신규 영상 업로드 감지·자막 분석·자동 배포 스크립트(`daily_council_sync.py`) 및 스케줄러 등록

# 카세트테이프·삐삐·공중전화 컨셉 개편 (2026-10-14)

- [x] `css/theme.css` 색 토큰을 테이프 톤(밤의 방 / 낮의 방)으로 교체
- [x] `css/tape.css` 작성 (카세트·데크·트랙 목록·모토로라 삐삐·속지·공중전화 부품, 레트로 글꼴)
- [x] `index.html` 첫 화면: 지구본 → 카세트 + 트랙 목록(A면·B면) + 모토로라 삐삐, 페이지 카드 그리드 제거
- [x] 삐삐 액정에 최신 글 자동 표시, 데크 버튼 연결(▶ 최신 칼럼 · ▶▶ 칼럼 목록 · ◀◀ 연대기 · ■ 소개)
- [x] `column.html` 목록을 테이프 속지(SIDE A 행정·정책 / SIDE B 삶의 기록)로
- [x] `guestbook.html`을 공중전화·음성사서함으로 (Supabase 입력·목록 기능 유지)
- [x] 지구본 제거로 쓰지 않게 된 `js/globe.js`·`img/earth.jpg`·배포 목록 정리
- [x] CLAUDE.md 파일 구조·디자인 시스템 갱신, `publish.py`에 `css/tape.css`
- [x] 브라우저로 데스크톱·모바일·라이트 모드·동작 줄이기 확인
- [x] 단계별 커밋, PR·병합·배포 확인

# 진로 나침반 공개 진로검사 (`career-compass.html`) + 구글 시트 수집 (2026-11-11)

- [x] `career-compass.html` 작성: 한 화면 한 문항 모션 진행(흥미 36·성격 50·적응력 16·가치 상위 5·이야기 4), 즉시 결과(육각형·막대·해석·계열/과목)
- [x] 결과 전송: 익명 별칭·학년만 받고, 동의 체크(만 14세 미만 보호자 동의 포함) 후 Apps Script로 전송. 미설정·실패 시 결과 코드 복사
- [x] `scripts/career-compass-sheet.gs` 작성: 시트 자동 머리행, 크기·형식 검사, 수식 주입 방지, 분당 전송 상한
- [x] 채점 검증: 역문항 18개·유형별 문항 수·결과 코드 계산을 node로 확인, 스크립트 구문 검사
- [x] `index.html` B면 트랙·`sitemap.xml`·`publish.py` 배포 목록 연결
- [x] Apps Script 웹 앱 배포(시트 "진로나침반 응답", 프로젝트 "진로나침반 수집", 실행: 운영자 / 액세스: 모든 사용자) 후 URL을 `ENDPOINT`에 넣고 배포

# 홈 첫 화면 배경 교체 (2026-11-17)

- [x] `#lounge-hero` 평면 배경을 1번 호수 아침 사진(`img/hero-lake-mist.jpg`) + 38초 천천히 흐르는 드리프트로 교체
- [x] 글자 가독용 어두운 그라디언트 오버레이, 동작 줄이기 설정 시 정지
- [x] `publish.py`에 `css/lounge-hero.css` 업로드 추가
- [ ] 운영자가 채팅에 올린 1번 사진을 `img/hero-lake-mist.jpg`로 저장 후 배포 확인
