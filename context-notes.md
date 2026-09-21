# AI 가이드 섹션 — 결정 기록

## 왜 별도 섹션인가
기존 `column.html`은 행정·에세이 칼럼이다. lazyowen 형식은 복사 프롬프트, 터미널 명령, Quick Start 팩트박스, STEP, 한계 고백이 본문이다. 기존 `build_columns.py`의 마크다운 변환기는 코드펜스·표를 지원하지 않는다. 섞으면 목록도 톤도 깨진다.

URL은 참고 사이트와 같이 `/guides/{슬러그}.html`로 둔다. 예: `/guides/claude-and-markitdown.html`.

## 이번 주 주제
2026-09-20 GitHub Trending (This week)에서 `microsoft/markitdown`을 골랐다.
- 주간 스타 +2,767, 누적 약 185,737
- 공문·PDF·워드를 다루는 독자(운영자 본인 포함)에게 바로 쓸 수 있다
- 클로드와 짝이 분명하다. 파일을 마크다운으로 바꿔 모델에 넘긴다
- HWP 미지원은 한계로 솔직히 적는다. 한글에서 PDF로 저장한 뒤 변환

후보에서 뺀 것:
- `anthropics/knowledge-work-plugins`: Cowork 전용 색이 강하고, 초보 실습 경로가 길다
- `alibaba/open-code-review`: 개발자 코드리뷰 도구라 이 사이트 독자와 거리가 있다
- `bilawalsidhu/gods-eye-view`: 시각화 데모에 가깝고 "클로드로 N단계" 형식이 안 맞는다

## 같은 주 추가 3편 (2026-09-20)
운영자가 “github트렌드에서 내가 사용하기 유용한 것들 3개만 더 올려줘”라고 해서, 같은 주간 트렌드에서 본인 작업(칼럼, 커서, 이 사이트)에 바로 붙는 것만 골랐다.

1. `blader/humanizer` — 칼럼 초안의 AI 티. 스타 50,352, 주간 +3,024, MIT, 스킬 3.0.0. 설치는 `npx skills add blader/humanizer --global`.
2. `ayghri/i-have-adhd` — 커서 답을 행동부터. 스타 48,858, 주간 +5,589, MIT. 설치는 `npx skills add ayghri/i-have-adhd -g`. 이름은 브랜드이지 진단이 아니다. 글쓰기 채팅에는 끄라고 적었다.
3. `addyosmani/agent-skills` — 이 저장소 코딩 절차. 스타 97,217, 주간 +3,445, MIT. 25개 전체가 아니라 `spec-driven-development` / `documentation-and-adrs` / `code-review-and-quality` 세 개만. 단건 설치 때 `references/` 누락은 업스트림 #361.

추가로 뺀 것:
- `Panniantong/Agent-Reach`: 연구·트렌드 조사에는 맞지만, 쿠키·로그인 채널이 공직 계정과 겹치면 위험이 크다. 제로컨피그(웹·유튜브·GitHub·RSS)만 쓰라는 가이드로도 쓸 수 있으나, 이번 3편에서는 제외했다.

슬러그:
- `guides/claude-and-humanizer.html`
- `guides/claude-and-i-have-adhd.html`
- `guides/claude-and-agent-skills.html`

원문은 `💬 AI가이드.md`에 이어 붙이고 `python3 build_guides.py`로 HTML을 다시 만들었다. 라이브 배포는 BAT.

## 주간 운영
매주 채팅에서 "이번 주 AI 가이드"라고 하면 같은 절차를 반복한다.
이미 `💬 AI가이드.md`에 있는 `repo:`는 다시 고르지 않는다.
초안 확인 후 원문 추가 → `python3 build_guides.py` → BAT 배포.
로컬 세션이 일주일 동안 열려 있지 않으므로 타이머 루프는 걸지 않는다.

## 팩트 출처 (2026-09-20)
- PyPI markitdown 0.1.7, MIT, Python >=3.10
- GitHub microsoft/markitdown README (지원 포맷, CLI, 설치)
- packages/markitdown-mcp README (convert_to_markdown, pip install markitdown-mcp)
- GitHub Trending weekly 페이지의 스타 수
