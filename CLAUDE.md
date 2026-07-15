CLAUDE.md
Behavioral guidelines to reduce common LLM coding mistakes. Merge with project-specific instructions as needed.
Tradeoff: These guidelines bias toward caution over speed. For trivial tasks, use judgment.
1. Think Before Coding
Don't assume. Don't hide confusion. Surface tradeoffs.
Before implementing:
State your assumptions explicitly. If uncertain, ask.
If multiple interpretations exist, present them - don't pick silently.
If a simpler approach exists, say so. Push back when warranted.
If something is unclear, stop. Name what's confusing. Ask.
2. Simplicity First
Minimum code that solves the problem. Nothing speculative.
No features beyond what was asked.
No abstractions for single-use code.
No "flexibility" or "configurability" that wasn't requested.
No error handling for impossible scenarios.
If you write 200 lines and it could be 50, rewrite it.
Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.
3. Surgical Changes
Touch only what you must. Clean up only your own mess.
When editing existing code:
Don't "improve" adjacent code, comments, or formatting.
Don't refactor things that aren't broken.
Match existing style, even if you'd do it differently.
If you notice unrelated dead code, mention it - don't delete it.
When your changes create orphans:
Remove imports/variables/functions that YOUR changes made unused.
Don't remove pre-existing dead code unless asked.
The test: Every changed line should trace directly to the user's request.
4. Goal-Driven Execution
Define success criteria. Loop until verified.
Transform tasks into verifiable goals:
"Add validation" → "Write tests for invalid inputs, then make them pass"
"Fix the bug" → "Write a test that reproduces it, then make it pass"
"Refactor X" → "Ensure tests pass before and after"
For multi-step tasks, state a brief plan:
```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```
Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.
5. No Closing Colons (Korean Output)
End Korean sentences with a period, not a colon.
When the user writes in Korean, your output is also Korean:
Don't end sentences with `:` even if the next line is a list or example.
LLMs trained on English docs leak the colon habit into Korean. Catch it.
The test: every Korean sentence terminator should be `.`, `?`, or `!` — not `:`.
Colons are fine inside code, key-value pairs, or labels. Not as sentence enders.
6. File Header Comments in Korean
First line of every new source file: a one-line Korean comment stating its role.
When creating a new file:
TypeScript/JavaScript: `// 사용자 인증 상태를 관리하는 Context Provider`
Python: `# KIS API 호출을 비동기로 래핑하는 클라이언트`
SQL: `-- 일별 집계 결과를 저장하는 머티리얼라이즈드 뷰`
Place it directly under required directives (`'use client'`, `'use server'`, shebang).
Skip config files (`*.config.ts`, `package.json`, etc.).
Why: agents read files selectively, not whole codebases. A one-line Korean header gives instant context so the next session (human or agent) can navigate without re-reading the entire file.
7. Plan + Checklist + Context Notes
Before any non-trivial task, produce three artifacts. Don't start coding without them.
Plan — what we're building and why.
Checklist (`checklist.md`) — concrete tasks as checkboxes. Tick as you go.
Context Notes (`context-notes.md`) — decisions made during the work and the reasoning behind them. Append continuously.
If the user gives only a plan and asks you to start coding, stop and ask: "Should I create the checklist and context notes first?" The next session — yours or someone else's — needs the notes to pick up where you left off without re-deriving every decision.
8. Run Tests Before Marking Complete
If you touched code, run the tests before saying "done".
`npm test`, `pytest`, `cargo test`, whatever the project uses — run it.
If tests pass, report results. If they fail, fix and re-run.
No test setup? At minimum, verify the project builds/compiles.
Run tests proactively, before the user signals "끝", "완료", "다 됐어" — not after.
This is the step LLMs skip most often. Treat it as non-negotiable.
9. Semantic Commits
Commit when one logical change is complete. Don't wait for the user to ask.
The test: "Can I describe this commit in one sentence?" If yes, commit. If no, the changes are still mixed — split them.
Good: "auth 미들웨어 추가". Bad: "auth 추가하고 UI도 고치고 버그도 수정" (split into 3).
Don't accumulate 20 unrelated edits and lose the ability to roll back individually.
Don't commit just to commit — meaningful units only.
Note: For solo prototypes or throwaway scripts, group commits loosely if it slows you down. The point is reversibility, not ceremony.
10. Read Errors, Don't Guess
Read the actual error/log line. Don't pattern-match from memory.
When something fails:
Read the full error message and stack trace.
Check the actual log output, not what you assume it should say.
Don't apply a "common fix" before confirming the cause.
If unclear, add a print/log to verify state — then fix.
This is the step LLMs skip most often after "run tests". They guess from error keywords and apply the most-recent-pattern fix. That's how a one-line bug becomes a three-file refactor.
---
These guidelines are working if: fewer unnecessary changes in diffs, fewer rewrites due to overcomplication, and clarifying questions come before implementation rather than after mistakes.

# 나를 정리하는 프로젝트 — Claude 작업 지침

## 프로젝트 개요

GitHub Pages 기반 개인 사이트 (`choijc79.github.io`) 관리 및 콘텐츠 발행 자동화 프로젝트.
운영자: 최승환 (충청북도 제천시청 팀장, 도시경영학 박사과정)

---

## 파일 구조

| 파일 | 역할 |
|------|------|
| `publish.py` | GitHub API로 전체 사이트 배포. `build_memo_html()` 포함 (memo.html 자동 생성). `build_column_html()`은 더 이상 사용하지 않는 레거시 함수 — column.html은 로컬 파일을 그대로 업로드함 |
| `💬 칼럼·기고.md` | 칼럼 원본. `---` 구분자, `## 제목 \| YYYY-MM-DD \| 태그` 헤더 형식 |
| `build_columns.py` | `columns/*.html` (개별 칼럼 전문 페이지) 생성 스크립트. 칼럼 추가/수정 후 수동 실행 필요 |
| `columns/` | 개별 칼럼 전문 페이지 (`build_columns.py`가 생성, publish.py가 그대로 업로드) |
| `📝 정리노트.md` | 정리노트 원본 |
| `index.html` | 홈페이지 (hero + cat-grid 6칸). CSS/JS는 외부 파일로 분리됨 — 아래 `css/`, `js/` 참고 |
| `css/index.css`, `css/jc-picker.css` | index.html 스타일 (전체 페이지 / 맛집 뽑기 위젯 전용) |
| `js/site.js` | index.html 공통 스크립트: 테마 토글·내비 스크롤·검색창·위젯 열기닫기·날씨·홈 통계 |
| `js/globe.js` | index.html 3D 지구본 렌더링 (Three.js) |
| `js/jc-picker.js` | index.html 맛집 뽑기 로직 |
| `about.html` | 소개 페이지 |
| `research.html` | 연구·논문 포트폴리오 |
| `column.html` | 칼럼 목록. 카드마다 `/columns/{슬러그}.html`로 링크. 직접 수정하는 정본 파일 (더 이상 자동 생성 안 됨) |
| `tour.html` | 투어 기사 목록 |
| `whisky.html` | 위스키 가이드 목록 |
| `memo.html` | 정리노트 (publish.py가 자동 생성) |

배포는 항상 `🚀 사이트에 올리기.bat` 실행으로만 가능 (샌드박스에서 GitHub API 직접 호출 불가).

---

## 디자인 시스템

```
--bg:#0d1117  --surface:#161b22  --border:#30363d
--text:#e6edf3  --muted:#8b949e  --accent:#58a6ff
--amber:#d29922  --green:#3fb950  --lake:#5cbcd4  --purple:#bc8cff
```

폰트: Noto Serif KR (제목) + Noto Sans KR (본문, weight:300)

---

## 글쓰기·문서 작성 기준

### 공통 원칙
- **결과물은 항상 완성형**으로. 초안·1차안 제출 금지. 바로 사용 가능한 수준으로 작성
- **"에스파냐"** 사용 (스페인 X)
- 불필요한 사족 없이 본론 중심으로 정리
- 상투적 표현("의의가 있다", "매우 중요하다" 등) 배제
- 문장이 끊기지 않고 흐름이 자연스럽게 이어지게
- **칼럼 말투**: 단정적 서술 지양. "~이다", "~한다" 대신 "~라고 생각한다", "~느껴진다", "~그럴 수 있다" 처럼 여지를 남기는 표현을 선호. 독자에게 결론을 강요하지 않고 함께 생각하는 어조 유지

### 카테고리별 톤 & 스타일

**에세이 (개인 서사·일상·여행·성찰)**
- 겸손하고 자상한 어조. 자랑이나 과시 없이 독자와 같은 눈높이에서
- 경험을 통해 배운 것을 조용히 나누는 방식. "나는 이랬다"보다 "그 경험이 이것을 가르쳐줬다"
- 따뜻하고 인간적인 문장. 어렵지 않게, 하지만 가볍지 않게
- 결말은 열린 여운으로. 교훈을 강요하지 않고 독자가 스스로 느끼게

**행정·정책 (업무 분석·제도·칼럼)**
- 진중하고 신뢰감 있는 어조. 현장 경험에서 나오는 무게감
- 문제 제기보다 구조 분석 중심. "이것이 문제다"보다 "이 구조가 이렇게 작동한다"
- 감정 없이 사실과 논리로 서술. 비판은 구체적 근거와 함께
- 논문 문장: 학술적, 바로 인용 가능한 수준
- 구조가 문제라는 말 대신 다른 말로 표현

**아이디어·제안 (정책 제안·도시경영·혁신)**
- 긍정적이고 미래지향적인 어조. 현재의 한계보다 가능성을 먼저 말함
- 불평·불만이 아닌 완성형 대안 제시. "문제가 있다"로 끝나지 않고 "이렇게 하면 된다"로
- 자원 배분 효율성, 지속가능성, 실행 가능한 Action Plan을 반드시 포함
- 도시경영학적 관점: 한정된 자원의 효율적 배분 → 지속가능한 성장 → 구체적 실행 3단계
- 희망을 주되 근거 없는 낙관은 지양. 현실적이지만 비전이 있게

---

## 칼럼 추가 방법

1. `💬 칼럼·기고.md` 끝에 아래 형식으로 추가:

```markdown
## 칼럼 제목 | YYYY-MM-DD | 태그1·태그2

본문...

---
```

2. `column.html`의 idx-list(`<li class="idx-row" ... data-tag="...">`)와 카드 목록(`<article class="col-item" ...>`)에 새 항목을 슬러그·사진 경로와 함께 추가
3. `python build_columns.py` 실행 → `columns/{슬러그}.html` 생성 (`--check`로 매칭 여부 미리 확인 가능)
4. `🚀 사이트에 올리기.bat` 실행 → `column.html` + `columns/*.html` + `img/` 사진이 함께 업로드됨

태그는 `·`로 구분. 예: `지방세·행정연구`, `건축·여행·에스파냐`

---

## 자주 쓰는 작업 패턴

**새 칼럼 발행**
1. 칼럼 초안 작성 → **채팅창에 먼저 출력해 운영자 확인 요청**
2. 수정·승인 완료 후에만 `💬 칼럼·기고.md`에 추가
3. null 바이트 오염 여부 확인 (`raw.replace(b'\x00', b'')`)
4. `🚀 사이트에 올리기.bat` 실행

**새 HTML 페이지 추가**
1. 기존 `tour.html` 또는 `whisky.html` 패턴 참고
2. OG 메타태그 반드시 포함 (`og:title`, `og:description`, `og:type`, `og:url`)
3. `publish.py`의 `main()` 함수에 `push_local()` 호출 추가

**publish.py 수정 시 주의사항**
- 수정 후 반드시 `ast.parse()` 또는 `py_compile`로 문법 검사
- 한글이 포함된 문자열 Edit 시 인코딩 잘림 발생 가능 → bash Python 스크립트로 대체
- `str.replace()`는 매칭 실패 시 오류 없이 무시 → 체크리스트로 반드시 검증

---

## 오류 대응 요령

| 증상 | 원인 | 해결 |
|------|------|------|
| `IndentationError: expected an indented block` | 파일 중간 잘림 | 잘린 위치부터 bash 스크립트로 재작성 |
| `UnicodeDecodeError: unexpected end of data` | UTF-8 멀티바이트 경계 잘림 | 바이너리로 읽어 잘린 위치 확인 후 복원 |
| 마크다운 파싱 실패 | null 바이트 오염 | `raw.replace(b'\x00', b'')` 후 재저장 |
| GitHub API 403 | 샌드박스 네트워크 차단 | BAT 파일로만 배포 |

---

## 운영자 맥락 (Claude가 참고할 배경)

- 지방행정 20년 경력, 등록면허세·납세지 불일치·지방세 역외 유출 연구
- 도시경영학 박사과정, 논문 제목: "등록면허세 납세지 불일치가 지방세 세원 역외 유출에 미치는 영향"
- 관심 분야: 지방세, GIS·공간분석, 업무자동화, 바이크투어, 위스키, 글쓰기
- 연락처: 7979@korea.kr
