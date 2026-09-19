# 신규 HTML 페이지 추가 체크리스트

위스키 리뷰·칼럼이 아닌 일반 페이지(투어 기사, 정책 보고서, 대시보드 등)를 새로 추가할 때 사용. `tour.html` 또는 `whisky.html`, `jecheon_dashboard.html` 등 성격이 비슷한 기존 페이지를 골라 구조를 참고한다.

## 준비
- [ ] 페이지 성격이 비슷한 기존 파일 1개 선정 (참고용)
- [ ] 파일명(슬러그) 결정: `{{파일명}}.html`

## 작성
- [ ] 참고 파일을 복사해 내용 교체 (디자인 토큰은 CLAUDE.md의 `--bg`, `--surface`, `--accent` 등 유지)
- [ ] OG 메타태그 포함 확인 — `og:title`, `og:description`, `og:type`, `og:url`
- [ ] 가능하면 `css/synthwave.css` + `css/pages.css` 링크 방식 사용 (인라인 `<style>` 전체 복제는 지양)

## 목록/내비게이션 연결
- [ ] 관련 목록 페이지(있다면)에 카드·링크 추가
- [ ] 필요 시 `index.html`의 cat-grid에서 연결

## 배포
- [ ] `publish.py`의 `main()` 함수에 `push_local("{{파일명}}.html", "add {{설명}}")` 호출 추가
- [ ] `🚀 사이트에 올리기.bat` 실행
- [ ] 배포 후 `https://choijc79.github.io/{{파일명}}.html` 접속 확인

## 메모
- (진행 중 발견한 특이사항, 판단 이유를 여기 기록)
