# 반복 작업 템플릿

이 저장소에서 자주 반복되는 콘텐츠 발행 흐름을 템플릿으로 뽑아둔 폴더. 새 항목을 추가할 때는 아래 템플릿을 복사해서 주제·데이터만 갈아 끼우고, 함께 있는 체크리스트로 절차를 따라가면 된다.

## 목록

| 템플릿 | 대상 작업 | 사용법 |
|---|---|---|
| `whisky-review.html` | 위스키 리뷰 페이지 (`ardbeg10.html`, `balvenie12.html` 등과 동일 구조) | 파일을 루트에 새 이름으로 복사 → `{{ }}` 플레이스홀더 치환 → `whisky-review-checklist.md`로 등록까지 마무리 |
| `whisky-review-checklist.md` | 위스키 페이지 신규 등록 | 체크박스를 순서대로 처리 |
| `column-checklist.md` | 칼럼 신규 발행 | CLAUDE.md의 "칼럼 추가 방법" 절차를 항목별 체크박스로 재구성한 것 |
| `new-page-checklist.md` | 위스키·칼럼이 아닌 일반 HTML 페이지 신규 추가 | tour.html/whisky.html 계열 패턴 참고 |

## 원칙

- 템플릿의 CSS 클래스 구조(`.hero`, `.section`, `.card`, `.timeline`, `.step-list`, `.tasting-grid` 등)는 그대로 두고 내용만 바꾼다. 구조를 바꾸면 디자인 시스템(`css/synthwave.css`, `css/pages.css`)과 어긋난다.
- 위스키 페이지는 자체 인라인 `<style>`(템플릿에 포함)을 쓴다. `css/synthwave.css`·`css/pages.css`만 링크하면 위스키 전용 색상(`--deep`, `--gold` 등)이 없어 배경이 투명해지고 첫 화면이 760px로 줄어든다. 색은 `:root`의 `--gold` 3개 값만 바꿔 위스키별로 구분한다.
- 체크리스트는 항목을 지우지 말고 `[x]`로 체크하며 진행. 작업 중 판단·이유는 각 파일 하단의 "메모" 섹션에 남긴다.
