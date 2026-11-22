---
name: site-guide
description: 홈페이지 AI 가이드(guides/)를 한 편 만들어 올린다. 「이번 주 AI 가이드」「이 저장소로 AI 가이드 써줘」처럼 GitHub 도구 사용법 가이드를 부탁할 때 쓴다.
---

# AI 가이드 올리기

형식은 프로젝트 CLAUDE.md의 「AI 가이드 추가 방법」과 기존 가이드(`💬 AI가이드.md`)를 따른다.

1. **도구 고르기**: 운영자가 저장소를 주면 그것을 쓴다. 없으면 GitHub Trending(weekly)에서 클로드와 짝지을 수 있고 초보가 따라 할 명령이 있는 것을 고른다. `grep '^repo:' "💬 AI가이드.md"`로 이미 다룬 저장소는 건너뛴다.
2. **자료 확인**: README·릴리스·라이선스를 직접 읽는다. 스타 수·버전은 확인한 날짜와 함께 적는다. 기억에 기대지 않는다.
3. **초안 쓰기**: 복사 프롬프트, Quick Start(저장소·한 줄 정의·스타 수·라이선스·환경·비용), STEP, 자주 막히는 곳, 솔직히 한계, 공식 자료를 넣는다. 긴 줄표와 챗봇 말투는 쓰지 않는다.
4. **채팅에 초안을 보여 승인받는다.** 승인 전에는 파일을 건드리지 않는다.
5. **배포**: 스크래치패드에 JSON을 쓰고 실행한다.
   ```json
   {"title": "...", "date": "2026-11-22", "tags": "AI·자동화", "slug": "claude-and-도구", "repo": "owner/repo",
    "minutes": 14, "steps": 5, "sections": 8, "excerpt": "한 줄 요약", "body": "본문 마크다운"}
   ```
   ```bash
   python3 site_mcp.py --add guide /경로/초안.json
   ```
   slug는 영어 소문자·숫자·하이픈만. md 추가, build_guides.py, sitemap, 커밋·push를 한 번에 한다.
6. **결과 보고**: 출력된 주소를 알려 준다. 커밋 검사에 걸리면 표현을 고치고, md에 들어간 블록은 `git restore`로 되돌린 뒤 다시 실행한다.
