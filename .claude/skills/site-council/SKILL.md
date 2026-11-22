---
name: site-council
description: 홈페이지 시의회 분석(council.html)을 지금 바로 갱신한다. 「시의회 분석 올려줘」「의회 새 영상 반영해줘」처럼 정해진 시각(09:00·19:00)을 기다리지 않고 동기화하고 싶을 때 쓴다.
---

# 시의회 분석 갱신

시의회 분석은 외장 SSD의 파이프라인이 만든다. 평소에는 launchd(`com.aipon.jecheon-council-sync`)가 09:00·19:00에 자동으로 돌린다. 이 스킬은 그것을 손으로 한 번 돌리는 것이다.

1. **SSD 확인**: `ls "/Volumes/Extreme SSD/제천 시의회/scripts/daily_council_sync.py"`. 없으면 「외장 SSD를 연결해 주세요」라고 알리고 멈춘다.
2. **실행**: 시간이 걸리므로 백그라운드로 돌린다.
   ```bash
   cd "/Volumes/Extreme SSD/제천 시의회" && python3 scripts/daily_council_sync.py
   ```
   새 영상 감지, 자막 추출·교정, council_data.js, 요구자료(council_requests.js) 생성, SSD 안 `site-repo`에서 pull 후 push까지 스크립트가 한다.
3. **결과 확인**: `tail -30 "/Volumes/Extreme SSD/제천 시의회/logs/daily_sync.log"`로 새 영상 수와 push 여부를 본다. 새 영상이 없으면 그대로 알린다.
4. **보고**: 반영된 회의 이름과 https://choijc79.github.io/council.html 주소를 알려 준다. 이 작업 폴더에도 반영하려면 `git pull --rebase --autostash`를 한다.

council.html의 디자인·구조를 고칠 때는 `build_requests.py`·`build_council_data.py`의 출력 형식과 맞아야 한다.
