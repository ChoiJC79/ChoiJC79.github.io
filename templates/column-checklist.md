# 칼럼 신규 발행 체크리스트

CLAUDE.md의 "칼럼 추가 방법" 절차를 항목별 체크박스로 재구성한 것. 칼럼 1편을 발행할 때마다 이 파일을 복사해 진행 상황을 체크한다.

## 준비
- [ ] 칼럼 제목: {{제목}} / 날짜: {{YYYY-MM-DD}} / 태그: {{태그1}}·{{태그2}}
- [ ] 카테고리 톤 결정 (에세이 / 행정·정책 / 아이디어·제안) — CLAUDE.md "카테고리별 톤 & 스타일" 참고
- [ ] 슬러그 결정: `{{슬러그}}`

## 원고
- [ ] 초안 작성 후 **채팅창에 먼저 출력해 운영자 확인 요청**
- [ ] 수정·승인 완료

## 파일 반영
- [ ] `💬 칼럼·기고.md` 끝에 아래 형식으로 추가
  ```markdown
  ## {{제목}} | {{YYYY-MM-DD}} | {{태그1}}·{{태그2}}

  {{본문}}

  ---
  ```
- [ ] null 바이트 오염 여부 확인 (`raw.replace(b'\x00', b'')`)
- [ ] `column.html`의 idx-list(`<li class="idx-row" ... data-tag="...">`)에 항목 추가
- [ ] `column.html`의 카드 목록(`<article class="col-item" ...>`)에 슬러그·사진 경로와 함께 항목 추가

## 페이지 생성
- [ ] `python build_columns.py --check`로 매칭 여부 확인
- [ ] `python build_columns.py` 실행 → `columns/{{슬러그}}.html` 생성 확인

## 배포
- [ ] `🚀 사이트에 올리기.bat` 실행 (column.html + columns/*.html + img/ 사진 함께 업로드)
- [ ] 배포 후 `https://choijc79.github.io/columns/{{슬러그}}.html` 접속 확인

## 메모
- (진행 중 발견한 특이사항, 판단 이유를 여기 기록)
