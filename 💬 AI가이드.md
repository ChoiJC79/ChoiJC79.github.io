## 워드·PDF를 클로드가 읽는 글로 바꾸는 5단계 | 2026-09-20 | AI·문서변환·MarkItDown
slug: claude-and-markitdown
repo: microsoft/markitdown
minutes: 14
steps: 5
sections: 8
excerpt: 공문 PDF를 클로드 창에 넣으면 깨지거나 중간에 잘립니다. 마이크로소프트 MarkItDown으로 그 파일을 마크다운으로 바꾼 다음, 클로드에 넘기는 다섯 단계입니다.

클로드 창에 공문 PDF를 그대로 올리면 글자가 빠지거나, 표가 한 줄로 뭉개지거나, 용량 제한에 걸려 중간부터 잘리곤 합니다. 이 자료는 마이크로소프트가 공개한 MarkItDown으로 워드·엑셀·PDF를 마크다운 파일로 바꾼 뒤, 그 파일을 클로드에 넘기는 다섯 단계를 담았습니다. 준비물은 파이썬이 돌아가는 컴퓨터와 클로드(또는 커서) 화면 하나입니다.

복사해서 바로 시작하는 프롬프트. 샘플 HTML 변환부터 결과 파일 확인까지 AI에게 맡기기.

터미널을 쓸 수 있는 AI(클로드 코드·커서 등)의 첫 메시지로 붙여넣으세요. 꺾쇠로 표시된 '내 파일' 한 곳만 내 경로로 바꾸면 됩니다. 웹 클로드만 쓰신다면 이 토글은 건너뛰고 STEP 1부터 직접 따라 하세요.

```prompt
역할: 이 컴퓨터에 MarkItDown을 설치하고, 지정한 문서를 마크다운으로 변환하는 담당
맥락: 이 컴퓨터에는 MarkItDown이 아직 없을 수 있고, 저는 개발 경험이 적은 편이라 설치가 됐는지 스스로 판단하기 어렵습니다. 한글(HWP) 파일은 이 도구가 직접 열지 못합니다.
입력: 내 파일 = <변환할 파일의 전체 경로, 예: /Users/나/Desktop/공문.pdf> (운영체제·셸·파이썬 경로는 저에게 묻지 말고 직접 확인하세요)
작업: ① 제 환경을 직접 확인하세요. Python 버전을 알아보고 3.10 미만이면 설치 방법을 초보자 눈높이로 안내한 뒤 여기서 멈추세요. ② 작업 폴더가 있는지 확인하고 없으면 `mkdir -p ~/markitdown-work` 로 만드세요. ③ 그 폴더 안에 가상환경을 만들고 `pip install 'markitdown[all]'` 로 설치하세요. ④ 내 파일이 .hwp 또는 .hwpx 이면 변환하지 말고, 한글에서 PDF로 다시 저장하라고 안내하세요. 그 외 형식이면 `markitdown "<내 파일>" -o ~/markitdown-work/output.md` 로 변환하세요. ⑤ 결과 파일의 앞 40줄과 글자 수를 보여 주고, 이 파일을 클로드 대화에 어떻게 붙이는지 안내하세요.
제약: sudo·전역 설치·시스템 파이썬을 바꾸는 명령은 먼저 물어보세요. API 키나 비밀번호를 화면에 출력하지 마세요. 이미 있는 파일을 덮어쓰지 마세요. Azure Document Intelligence 같은 유료 클라우드 변환은 켜지 마세요.
출력: 실행한 명령, 확인된 Python 버전, MarkItDown 버전, 결과 파일 경로와 글자 수, 남은 오류
검증: `python -c "from importlib.metadata import version; print(version('markitdown'))"` 가 버전 문자열을 출력해야 하고, 변환을 했다면 `~/markitdown-work/output.md` 크기가 0보다 커야 합니다. 하나라도 실패하면 완료로 보고하지 말고 실패한 명령과 원인, 다음 조치를 알려주세요.
```

## Quick Start

- 공식 저장소: [microsoft/markitdown](https://github.com/microsoft/markitdown)
- 설치 패키지: [PyPI markitdown](https://pypi.org/project/markitdown/)
- 한 줄 정의: MarkItDown은 워드·엑셀·PDF 같은 파일을, 클로드가 잘 읽는 마크다운 글자로 바꿔 주는 명령줄 도구입니다. 클로드가 한글 프로그램을 대신 눌러 주는 것은 아닙니다.
- 인기·만든 곳: 2026년 9월 20일 확인 기준 GitHub 스타 185,737개, 이번 주 트렌드에서 2,767개가 늘었습니다. 만든 곳은 마이크로소프트입니다.
- 라이선스: MIT. 개인 일과 기관 업무에 쓰는 것은 허용됩니다.
- 필요한 환경: Python 3.10 이상. 맥·윈도우·리눅스 모두 됩니다. 클로드 계정은 변환 자체가 아니라, 변환된 글을 읽을 때 필요합니다.
- 비용: MarkItDown 설치와 로컬 변환은 무료입니다. 클로드 요금은 따로 나갑니다. README에 있는 Azure 변환 옵션은 이 자료에서 쓰지 않습니다. 그쪽은 클라우드 과금이 붙습니다.

파이썬이 이미 있고 터미널만 열 수 있다면, 아래 네 줄이면 설치까지 끝입니다.

터미널에서 실행:

```bash
mkdir -p ~/markitdown-work
cd ~/markitdown-work
python3 -m venv .venv
source .venv/bin/activate
pip install 'markitdown[all]'
```

윈도우 명령 프롬프트라면 `python3` 대신 `py -3` 를 쓰고, 가상환경은 `source .venv/bin/activate` 대신 `.venv\Scripts\activate` 입니다.

> 검증: 2026-09-20 기준 (PyPI markitdown 0.1.7, Python >=3.10)

설치가 끝나면 아래 한 줄이 버전을 보여 줘야 합니다.

확인:

```bash
python -c "from importlib.metadata import version; print(version('markitdown'))"
```

`0.1.7` 처럼 숫자가 나오면 성공입니다. `No module named markitdown` 이 뜨면 가상환경을 켜지 않은 상태일 가능성이 큽니다. STEP 2로 가세요.

## STEP 1. 파이썬이 있는지 보기: 2분

이 단계에서는 이 컴퓨터가 MarkItDown을 설치할 수 있는 상태인지 확인합니다.

> 용어: 파이썬은 MarkItDown을 실행하는 바닥 프로그램입니다. 워드가 있어야 한글 문서를 열 수 있듯이, 여기선 파이썬이 있어야 변환 명령을 돌릴 수 있습니다.

터미널(맥은 터미널, 윈도우는 명령 프롬프트 또는 PowerShell)을 열고 한 줄을 입력합니다.

터미널에서 실행:

```bash
python3 --version
```

윈도우에서 `python3` 를 못 찾으면 `py -3 --version` 을 시도하세요.

`Python 3.10` 이상이 나오면 다음 단계로 가면 됩니다. 이 글을 쓰는 컴퓨터에서는 `Python 3.14.6` 이 확인됐습니다.

- `command not found` 또는 `파이썬을 찾을 수 없습니다` 가 나오면 [python.org/downloads](https://www.python.org/downloads/) 에서 설치한 뒤, 설치 화면의 "Add python.exe to PATH" 칸을 체크하세요.
- `Python 3.9` 이하가 나오면 버전이 낮습니다. 3.10 이상을 추가로 설치하세요. 이미 있는 3.9를 지울 필요는 없습니다.

## STEP 2. 가상환경에 설치하기: 3분

이 단계에서는 시스템 파이썬을 건드리지 않고, 이 작업 전용 칸에 MarkItDown만 넣습니다.

> 용어: 가상환경은 이 폴더 안에서만 쓰는 파이썬 상자입니다. 여기 설치한 것은 다른 프로그램을 건드리지 않습니다. 상자를 지으면 설치도 함께 사라집니다.

순서는 이렇습니다.

1. 작업 폴더를 만듭니다. 위치는 집 디렉터리 아래 `markitdown-work` 로 통일합니다.
2. 그 안에서 가상환경을 켭니다.
3. `pip install 'markitdown[all]'` 로 설치합니다. 따옴표와 `[all]` 을 빼면 PDF·워드 변환에 필요한 조각이 빠집니다.

터미널에서 실행:

```bash
mkdir -p ~/markitdown-work
cd ~/markitdown-work
python3 -m venv .venv
source .venv/bin/activate
pip install 'markitdown[all]'
```

프롬프트 앞에 `(.venv)` 가 보이면 상자가 켜진 것입니다. 그 상태에서 버전 확인을 다시 합니다.

확인:

```bash
python -c "from importlib.metadata import version; print(version('markitdown'))"
```

숫자가 나오면 설치는 끝난 것입니다.

- ❌ 이렇게 말고: `pip install markitdown` 만 실행하기
- ✅ 이렇게: `pip install 'markitdown[all]'` 로 PDF·워드·엑셀 변환 조각까지 함께 넣기

`[all]` 없이 설치하면 명령은 살아 있어도 PDF에서 `MissingDependencyException` 이 납니다. README가 선택 설치를 나눠 둔 이유입니다.

## STEP 3. 파일 하나 변환해 보기: 3분

이 단계에서는 실제 공문이 없어도 변환이 되는지부터 봅니다. 그다음 내 파일을 넣습니다.

가상환경이 켜진 상태에서 아래를 그대로 실행합니다.

터미널에서 실행:

```bash
printf '<h1>테스트</h1><p>변환이 되면 이 줄이 보여야 합니다.</p>\n' > ~/markitdown-work/sample.html
markitdown ~/markitdown-work/sample.html -o ~/markitdown-work/sample.md
```

확인:

```bash
cat ~/markitdown-work/sample.md
```

`# 테스트` 와 `변환이 되면 이 줄이 보여야 합니다.` 가 보이면 도구는 정상입니다.

이제 내 파일을 넣습니다. 경로만 바꿉니다.

터미널에서 실행:

```bash
markitdown "/내/파일/경로/공문.pdf" -o ~/markitdown-work/output.md
```

나온 파일은 메모장이나 VS Code, 커서에서 열면 됩니다.

한글(HWP) 파일은 이 도구가 열지 않습니다. 한글 프로그램에서 `다른 이름으로 저장` → `PDF` 를 고른 뒤, 그 PDF를 위 명령에 넣으세요. 스캔만 있는 PDF는 글자가 거의 안 나옵니다. 그 경우는 아래 솔직히 한계를 보세요.

공식 README가 변환을 지원한다고 적은 형식은 PDF, PowerPoint, Word, Excel, 이미지(EXIF·OCR), 오디오(전사), HTML, CSV·JSON·XML, ZIP, 유튜브 URL, EPUB 입니다.

> 용어: 마크다운은 제목·목록·표를 글자만으로 적어 둔 형식입니다. 사람 눈에도 읽을 수 있고, 클로드 같은 모델이 학습 때 많이 본 형식이기도 합니다.

## STEP 4. 나온 글을 클로드에 넘기기: 3분

이 단계에서는 변환된 파일을 실제로 읽게 합니다.

웹 클로드를 쓰는 경우.

1. [claude.ai](https://claude.ai) 에서 새 대화를 엽니다.
2. 입력창의 클립(파일 첨부) 버튼을 누릅니다.
3. `~/markitdown-work/output.md` 를 올립니다. 파인더나 탐색기에서 집 디렉터리 → `markitdown-work` 폴더입니다.
4. 요청은 짧게 적습니다.

```text
첨부한 문서를 읽고, 결정 사항과 내가 해야 할 일만 번호 매겨 정리해 줘.
원문에 없는 숫자는 만들지 마.
```

커서나 클로드 코드를 쓰는 경우, 파일을 프로젝트 폴더로 복사한 뒤 같은 요청을 하면 됩니다.

- ❌ 이렇게 말고: "이 문서 분석해 줘."
- ✅ 이렇게: 무엇을 빼라는지(결정 사항, 해야 할 일)와 하지 말 것(없는 숫자 만들기)을 같이 적기

파일이 클로드 첨부 용량을 넘기면 `output.md` 를 앞부분·뒷부분으로 나눕니다.

터미널에서 실행:

```bash
split -l 400 ~/markitdown-work/output.md ~/markitdown-work/part-
```

`part-aa`, `part-ab` 가 생깁니다. 앞에서부터 하나씩 올리고, "이어서 같은 기준으로 정리해 줘" 라고 하면 됩니다.

## STEP 5. 대화 중에 바로 변환하기 (선택): 5분

이 단계는 건너뛰어도 됩니다. STEP 3~4만으로도 공문 한 건은 처리됩니다.

매번 터미널을 열고 싶지 않다면, 공식 MCP 패키지를 붙일 수 있습니다. 노출되는 도구는 하나뿐입니다. `convert_to_markdown(uri)`. `uri` 에는 `file:` , `http:` , `https:` , `data:` 주소를 넣습니다.

터미널에서 실행:

```bash
pip install markitdown-mcp
```

쓰는 AI 도구의 MCP 설정에 아래를 넣습니다. 클로드 데스크톱 기준으로, 공식 README는 도커를 권합니다. 도커가 없다면 pip로 설치한 명령을 그대로 적어도 됩니다.

```json
{
  "mcpServers": {
    "markitdown": {
      "command": "markitdown-mcp"
    }
  }
}
```

설정 파일을 저장한 뒤 클로드 데스크톱이나 커서를 완전히 종료했다가 다시 켭니다. 도구 목록에 `convert_to_markdown` 이 보이면 연결된 것입니다.

공식 README가 적는 보안 주의는 짧습니다. 이 서버는 인증이 없고, 실행한 사용자 권한으로 파일을 읽습니다. HTTP 모드로 띄울 때는 기본이 `localhost` 입니다. 다른 망에 열어 두지 마세요.

## 자주 막히는 곳

| 증상 | 원인과 해결 |
| --- | --- |
| `No module named markitdown` | 가상환경을 켜지 않은 상태입니다. `source ~/markitdown-work/.venv/bin/activate` (윈도우는 `.venv\Scripts\activate`) 후 다시 시도하세요 |
| PDF에서 `MissingDependencyException` | `[all]` 없이 설치한 경우입니다. 가상환경 안에서 `pip install 'markitdown[all]'` 을 다시 실행하세요 |
| HWP를 넣었더니 실패합니다 | 지원 형식이 아닙니다. 한글에서 PDF로 저장한 다음 그 파일을 넣으세요 |
| 변환은 됐는데 본문이 거의 없습니다 | 스캔 PDF이거나 이미지로만 된 페이지입니다. 로컬 변환은 글자 층을 읽습니다. 그림 속 글자까지 필요하면 유료 Azure 옵션이 있고, 이 자료의 범위 밖입니다 |
| `python3` 를 못 찾습니다 | 윈도우에서는 `py -3 --version` 을 먼저 보세요. 그래도 없으면 python.org 에서 설치하고 PATH 칸을 체크하세요 |
| 클로드에 올리니 잘립니다 | 파일이 큽니다. STEP 4의 `split -l 400` 으로 나눠 올리세요 |

## 솔직히 한계

- 클로드가 한글·워드를 대신 열어 주지는 않습니다. 이 자료로 받는 것은 `.md` 파일 하나이고, 첨부하고 질문하는 일은 사람이 합니다.
- 한글(HWP)은 공식 지원 목록에 없습니다. PDF로 한 번 거치는 품이 남습니다.
- 스캔만 있는 PDF는 글자가 거의 안 나옵니다. README의 Azure Document Intelligence·Content Understanding은 그 구멍을 메우지만 클라우드 과금이 붙고, 공문 파일을 외부로 보내는 문제가 따로 생깁니다. 기관 문서라면 로컬 변환만 쓰는 편이 안전합니다.
- 변환 결과는 "사람이 보기에 예쁜 복원"이 목표가 아닙니다. README가 밝힌 대로, LLM이 읽기 좋은 구조를 남기는 쪽에 가깝습니다. 표가 조금 어색해도 내용은 살아 있는 경우가 많습니다.
- `[all]` 설치는 의존 패키지가 많습니다. 처음 한 번은 몇 분이 걸립니다. 가상환경 폴더를 지우면 `rm -rf ~/markitdown-work` 한 줄로 흔적이 사라집니다.

되돌리기:

```bash
rm -rf ~/markitdown-work
```

아무 메시지도 안 나오면 지워진 것입니다. 이어서 `ls ~/markitdown-work` 를 치면 `No such file or directory` 가 나옵니다. MCP를 등록했다면 설정 JSON에서 `markitdown` 칸만 지우면 됩니다.

## 공식 자료

- 저장소: [microsoft/markitdown](https://github.com/microsoft/markitdown)
- 설치: [PyPI markitdown 0.1.7](https://pypi.org/project/markitdown/)
- MCP 패키지: [packages/markitdown-mcp](https://github.com/microsoft/markitdown/tree/main/packages/markitdown-mcp)
- 라이선스: [MIT](https://github.com/microsoft/markitdown/blob/main/LICENSE)
- 보안 안내: README의 Security Considerations. 로컬 파일과 네트워크 주소를 그대로 열므로, 출처를 모르는 파일은 넣지 마세요.

---

## 클로드 글을 사람 글로 고치는 4단계 | 2026-09-20 | AI·글쓰기·Humanizer
slug: claude-and-humanizer
repo: blader/humanizer
minutes: 12
steps: 4
sections: 8
excerpt: 칼럼 초안이 ‘의의가 있다’ 쪽으로 기울면, 내용이 없어도 AI 티가 납니다. Humanizer 스킬로 그 티를 지우고, 사실과 의견은 그대로 두는 네 단계입니다.

클로드가 써 준 초안은 읽히기는 하는데, 한 문장씩 보면 중요한 척만 하고 사실은 안 늘어나는 경우가 많습니다. 이 자료는 GitHub 트렌드의 Humanizer 스킬을 커서에 넣은 뒤, 내 칼럼 초안에서 AI 티만 걷어 내는 네 단계를 담았습니다. 준비물은 Node가 돌아가는 컴퓨터와 커서 화면 하나입니다.

복사해서 바로 시작하는 프롬프트. 설치부터 샘플 문장 고치기까지 AI에게 맡기기.

터미널을 쓸 수 있는 AI(클로드 코드·커서 등)의 첫 메시지로 붙여넣으세요. 꺾쇠로 표시된 '내 초안' 한 곳만 바꾸면 됩니다. 웹 클로드만 쓰신다면 이 토글은 건너뛰고 STEP 1부터 직접 따라 하세요.

```prompt
역할: 이 컴퓨터에 Humanizer 스킬을 설치하고, 지정한 초안에서 AI 티만 걷어 내는 담당
맥락: 저는 칼럼을 자주 쓰고, 초안은 클로드가 잡는 일이 많습니다. 사실·숫자·인용은 바꾸면 안 됩니다. 없는 일화를 채워 넣으면 안 됩니다.
입력: 내 초안 = <고칠 문단, 또는 프로젝트 안의 .md 경로> (운영체제·셸·Node 경로는 저에게 묻지 말고 직접 확인하세요)
작업: ① Node와 npx가 있는지 확인하세요. 없으면 설치 방법을 초보자 눈높이로 안내한 뒤 여기서 멈추세요. ② `npx skills add blader/humanizer --global` 로 전역 설치하세요. 이미 있으면 덮어쓰기 전에 경로만 보여 주세요. ③ `npx skills list -g` 또는 `~/.cursor/skills/humanizer/SKILL.md` 존재 여부로 설치를 확인하세요. ④ 새 커서 대화를 열라고 안내한 뒤, `/humanizer` 로 내 초안을 고치게 하세요. ⑤ 고친 글에서 원문의 고유명사·숫자·날짜가 그대로인지 대조해 보여 주세요.
제약: sudo·전역 npm 강제 설치·git config 변경은 먼저 물어보세요. 원문에 없는 장소·날짜·감정을 만들지 마세요. 행정 공문 문체를 에세이 문체로 바꾸지 마세요.
출력: 실행한 명령, 확인된 Node 버전, 스킬 파일 경로, 고치기 전후 문단, 바뀐 점과 안 바뀐 사실
검증: `~/.cursor/skills/humanizer/SKILL.md` 또는 프로젝트 `.cursor/skills/humanizer/SKILL.md` 가 있어야 하고, 고친 글에 원문에 없던 고유명사가 없어야 합니다. 하나라도 실패하면 완료로 보고하지 말고 실패한 명령과 원인, 다음 조치를 알려주세요.
```

## Quick Start

- 공식 저장소: [blader/humanizer](https://github.com/blader/humanizer)
- 설치 페이지: [skills.sh/blader/humanizer](https://skills.sh/blader/humanizer)
- 한 줄 정의: Humanizer는 AI가 자주 쓰는 말버릇 25가지를 찾아, 뜻은 유지한 채 사람 글로 다시 쓰는 스킬입니다. 표절 검사기도, 자동 발행기도 아닙니다.
- 인기·만든 곳: 2026년 9월 20일 GitHub API 기준 스타 50,352개. 같은 날 주간 트렌드 스냅샷에서는 한 주 동안 3,024개가 늘었습니다. 만든 곳은 blader입니다.
- 라이선스: MIT. 개인 일과 기관 업무에 쓰는 것은 허용됩니다.
- 필요한 환경: Node.js와 npx. 맥·윈도우·리눅스 모두 됩니다. 커서가 있으면 `/humanizer` 로 바로 부릅니다.
- 비용: 스킬 설치는 무료입니다. 글을 고치는 쪽은 쓰는 모델 요금이 나갑니다.

파이썬이 아니라 Node가 필요합니다. 터미널에서 아래 한 줄이면 전역 설치까지 끝입니다.

터미널에서 실행:

```bash
npx skills add blader/humanizer --global
```

이 프로젝트에만 넣고 싶다면 `--global` 을 빼면 됩니다.

> 검증: 2026-09-20 기준 (README 설치문, 스킬 버전 3.0.0, MIT)

설치가 끝나면 아래가 목록에 보여야 합니다.

확인:

```bash
npx skills list -g
```

`humanizer` 가 보이면 성공입니다. 안 보이면 STEP 2로 가세요. 커서는 새 채팅을 열어야 스킬을 다시 읽습니다.

## STEP 1. Node가 있는지 보기: 2분

이 단계에서는 이 컴퓨터가 스킬 CLI를 돌릴 수 있는지 확인합니다.

> 용어: npx는 Node와 함께 오는 실행기입니다. 패키지를 전역으로 오래 설치하지 않고도, 그때그때 명령을 돌립니다.

터미널을 열고 한 줄을 입력합니다.

터미널에서 실행:

```bash
node --version && npx --version
```

숫자가 두 줄로 나오면 다음 단계로 가면 됩니다. 이 글을 쓰는 컴퓨터에서는 `v26.5.0` 과 `11.17.0` 이 확인됐습니다.

- `command not found` 가 나오면 [nodejs.org](https://nodejs.org/) 에서 LTS를 설치한 뒤 터미널을 다시 여세요.
- 버전이 나와도 `npx skills` 가 없으면 STEP 2의 첫 실행에서 패키지를 받아 옵니다. 그때 `Need to install the following packages` 가 뜨면 확인만 하면 됩니다.

## STEP 2. Humanizer 넣기: 3분

이 단계에서는 커서(또는 클로드 코드)가 읽을 스킬 폴더에 Humanizer를 둡니다.

공식 README가 적는 기본 설치는 한 줄입니다.

터미널에서 실행:

```bash
npx skills add blader/humanizer --global
```

클로드 코드 2.1.142 이상이라면 플러그인으로도 됩니다.

```text
/plugin marketplace add blader/humanizer
/plugin install humanizer@humanizer
```

플러그인 쪽 호출은 `/humanizer:humanizer` 입니다. 스킬 CLI 쪽은 `/humanizer` 입니다.

확인:

```bash
ls ~/.cursor/skills/humanizer/SKILL.md
```

파일이 보이면 커서가 읽을 위치까지 들어간 것입니다. 경로는 에이전트마다 조금 다릅니다. 프로젝트만 설치했다면 `.cursor/skills/humanizer/SKILL.md` 를 보세요.

- ❌ 이렇게 말고: SKILL.md 전문을 사용자 규칙에 붙여 넣기
- ✅ 이렇게: 스킬 폴더에 두고, 대화에서 `/humanizer` 로 부르기

규칙 창에 장문을 넣으면 토큰만 쓰고, 업데이트도 안 따라갑니다.

## STEP 3. 짧은 문단으로 시험하기: 4분

이 단계에서는 설치가 글까지 바꾸는지 봅니다.

커서를 완전히 종료했다가 다시 켠 뒤, 새 채팅을 엽니다. 아래를 그대로 넣습니다.

```text
/humanizer

최근 우리 시는 지역 경제의 새로운 지평을 여는 중대한 전환점에 서 있습니다. 이는 단순한 행사가 아니라, 시민과 행정이 함께 만들어 가는 지속가능한 미래라는 비전을 상징합니다. 전문가들은 이번 시도가 매우 중요한 의미를 갖는다고 평가합니다.
```

잘 되면 첫 줄부터 구체적 문장으로 바뀌고, “전환점” “비전을 상징” “전문가들은” 같은 자리가 빠지거나 평범한 말로 바뀝니다. README의 작업 순서는 티를 센 다음 초안을 잡고, 다시 한번 대조한 뒤 최종본을 내는 쪽입니다.

원문에 없던 행사명·날짜가 생겼다면 실패한 것입니다. 스킬이 밝힌 규칙은 사실·숫자·인용을 만들지 말라는 것입니다. 빠진 정보가 필요하면 지어내지 말고 물어야 합니다.

내 칼럼 말투에 맞추려면 샘플을 같이 줍니다.

```text
/humanizer

아래는 내가 예전에 쓴 문단입니다. 리듬과 어휘를 이것에 맞추세요.
[내 칼럼에서 고른 문단 2~3개]

이제 이 초안을 고치세요.
[고칠 초안]
```

파일 전체를 넘길 수도 있습니다. `docs/초안.md 산문을 Humanize해 줘` 처럼 경로를 주면, README 기준으로 코드·데이터·프론트매터·링크 주소는 건드리지 않고 산문만 고칩니다.

## STEP 4. 칼럼 초안에 쓰기: 3분

이 단계에서는 사이트에 올리는 글에 적용합니다.

이 프로젝트에서는 `💬 칼럼·기고.md` 초안을 커서에 붙여 넣고 `/humanizer` 를 치는 흐름이 맞습니다. 고친 글을 바로 저장하지 말고, 아래만 눈으로 대조하세요.

1. 고유명사, 조례명, 날짜, 금액이 원문과 같은지.
2. 행정 문서의 단정 문체가 에세이 말투로 바뀌지 않았는지.
3. 빼도 되는 상투어만 빠졌는지. 이 사이트의 글쓰기 기준으로는 “의의가 있다” “매우 중요하다” 같은 자리가 후보다.

- ❌ 이렇게 말고: 초안 전체를 한 번에 넣고 저장까지 맡기기
- ✅ 이렇게: 문단 두세 개씩 고치고, 사실 대조 후에만 원문에 반영하기

패턴 목록의 출처는 위키백과 [Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing) 입니다. 영어 표지(em dash, delve, testament)가 앞에 있고, 한국어 상투어는 목록에 덜 나옵니다. 그래서 한국어 칼럼에서는 샘플 문단을 같이 주는 편이 낫습니다.

## 자주 막히는 곳

| 증상 | 원인과 해결 |
| --- | --- |
| `/humanizer` 가 안 뜹니다 | 설치 후 새 채팅을 열지 않은 상태입니다. 커서를 재시작한 뒤 다시 보세요 |
| `npx: command not found` | Node가 없거나 PATH에 없습니다. STEP 1로 돌아가세요 |
| 고친 글에 없던 일화가 생깁니다 | 스킬이 빈칸을 채운 것입니다. “없는 사실은 묻기”를 다시 적고 한 문단만 다시 돌리세요 |
| 공문 문체가 풀어집니다 | 에세이 예시로 학습된 결과입니다. “행정 문체는 유지, AI 상투어만 삭제”를 제약에 넣으세요 |
| 클로드 코드에서 명령이 다릅니다 | 플러그인 설치면 `/humanizer:humanizer` 입니다. 스킬 CLI면 `/humanizer` 입니다 |

## 솔직히 한계

- Humanizer는 “사람이 썼는지”를 증명하지 않습니다. AI 탐지기 점수를 올리는 도구가 아니고, 말버릇을 줄이는 편집 스킬입니다.
- 25개 패턴은 영어 위키 표지를 기준으로 잡혀 있습니다. 한국어 칼럼의 상투어는 샘플을 같이 줘야 잘 잡힙니다.
- 사실을 지어내지 말라는 규칙이 있어도, 모델이 빈칸을 메우려고 할 수는 있습니다. 날짜와 고유명사는 사람이 대조하는 편이 안전합니다.
- 잘 쓴 공식 문장까지 평이하게 만들 수 있습니다. 보도자료·조례 해설은 문단을 나눠 돌리는 편이 낫습니다.
- 전역 설치는 `~/.cursor/skills/humanizer` 에 남습니다. 이 폴더를 지우면 커서가 더 이상 읽지 않습니다.

되돌리기:

```bash
npx skills remove humanizer -g
```

목록에서 사라졌는지는 `npx skills list -g` 로 보면 됩니다. 클로드 코드 플러그인으로 넣었다면 `/plugin uninstall humanizer@humanizer` 쪽이 맞습니다.

## 공식 자료

- 저장소: [blader/humanizer](https://github.com/blader/humanizer)
- 설치: README의 `npx skills add blader/humanizer --global`
- 패턴 출처: [Wikipedia: Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing)
- 라이선스: [MIT](https://github.com/blader/humanizer)
- 버전: README 릴리스 노트 기준 3.0.0 (패턴 35개에서 25개로 정리)

---

## 답이 맨 앞에 나오게 하는 4단계 | 2026-09-20 | AI·커서·답변형식
slug: claude-and-i-have-adhd
repo: ayghri/i-have-adhd
minutes: 10
steps: 4
sections: 8
excerpt: 커서 답이 ‘좋은 질문입니다’로 시작하면 할 일이 뒤로 밀립니다. i-have-adhd 스킬로 다음 행동부터 말하게 하는 네 단계입니다.

코딩 에이전트는 맥락을 길게 말하다 명령을 나중에 붙이는 버릇이 있습니다. 스크롤을 내려야 실행할 줄이 나옵니다. 이 자료는 GitHub 트렌드의 i-have-adhd 스킬을 커서에 넣어, 답의 첫 줄이 명령·경로·다음 행동이 되게 하는 네 단계를 담았습니다. 저장소 이름이 ADHD를 내걸지만, README는 진단이 필요 없다고 적습니다. 출력 형식 스킬입니다.

복사해서 바로 시작하는 프롬프트. 설치부터 한 턴 시험까지 AI에게 맡기기.

터미널을 쓸 수 있는 AI의 첫 메시지로 붙여넣으세요.

```prompt
역할: 이 컴퓨터의 커서에 i-have-adhd 스킬을 설치하고, 답이 행동부터 나오는지 확인하는 담당
맥락: 저는 커서에서 사이트와 칼럼 작업을 합니다. 긴 서론 없이 다음 명령이 먼저 보이면 됩니다. 이 스킬을 모든 대화에 강제로 켜지는 마세요.
입력: 설치 범위 = 전역 (모든 프로젝트). 운영체제·셸·Node 경로는 저에게 묻지 말고 직접 확인하세요.
작업: ① Node와 npx를 확인하세요. 없으면 설치 방법을 안내한 뒤 멈추세요. ② `npx skills add ayghri/i-have-adhd -g` 로 전역 설치하세요. ③ `npx skills ls -g` 와 `~/.cursor/skills/i-have-adhd/SKILL.md` 로 확인하세요. ④ 새 채팅에서 `/i-have-adhd` 를 치라고 안내하세요. ⑤ 시험 질문으로 “빈 Git 저장소를 새 폴더에 만드는 방법”을 쓰고, 첫 줄이 명령인지 아닌지만 판정 기준을 알려 주세요.
제약: 사용자 규칙 파일에 스킬 전문을 붙여 넣지 마세요. always-on 플래그(`~/.claude/.i-have-adhd-always` 등)는 먼저 물어보기 전에는 만들지 마세요. sudo는 묻지 말고 쓰지 마세요.
출력: 실행한 명령, Node 버전, 스킬 경로, 호출 방법, 끄기 문구(stop adhd mode / normal mode)
검증: `~/.cursor/skills/i-have-adhd/SKILL.md` 가 있어야 합니다. 실패하면 완료로 보고하지 마세요.
```

## Quick Start

- 공식 저장소: [ayghri/i-have-adhd](https://github.com/ayghri/i-have-adhd)
- 설치 문서: [INSTALL.md](https://github.com/ayghri/i-have-adhd/blob/main/INSTALL.md)
- 한 줄 정의: 코딩 에이전트가 답을 뒤에 숨기지 않게, 다음 행동·번호 목록·짧은 마침으로 말하게 하는 스킬입니다.
- 인기·만든 곳: 2026년 9월 20일 GitHub API 기준 스타 48,858개. 같은 날 주간 트렌드 스냅샷에서는 한 주 동안 5,589개가 늘었습니다. 만든 곳은 ayghri입니다.
- 라이선스: MIT.
- 필요한 환경: Node.js와 npx, 커서. 클로드 코드는 플러그인 경로가 따로 있습니다.
- 비용: 설치는 무료입니다. 대화 요금은 쓰는 모델 쪽입니다.

커서만 쓴다면 공식 INSTALL.md의 한 줄이면 됩니다.

터미널에서 실행:

```bash
npx skills add ayghri/i-have-adhd -g
```

이 저장소에만 넣으려면 `-g` 를 빼고, 커서만 지정하려면 `-a cursor -y` 를 붙입니다.

> 검증: 2026-09-20 기준 (INSTALL.md Cursor 절, MIT)

확인:

```bash
npx skills ls -g
ls ~/.cursor/skills/i-have-adhd/SKILL.md
```

파일이 보이면 설치는 된 것입니다. 규칙은 새 채팅에서 `/i-have-adhd` 를 치기 전에는 적용되지 않는 경우가 많습니다.

## STEP 1. 어디에 넣을지 정하기: 2분

이 단계에서는 전역과 이 프로젝트만의 차이를 고릅니다.

> 용어: 전역 스킬은 `~/.cursor/skills/` 에 들어가 모든 워크스페이스에서 보입니다. 프로젝트 스킬은 그 폴더의 `.cursor/skills/` 에만 있습니다.

일상 작업 대부분이 커서라면 전역이 맞습니다. 이 사이트 작업에만 짧은 답을 원하면 프로젝트만 설치하세요.

클로드 코드를 주로 쓰면 INSTALL.md의 플러그인 경로가 맞습니다.

```bash
claude plugin marketplace add ayghri/i-have-adhd
claude plugin install i-have-adhd@i-have-adhd
```

이 자료의 본문은 커서 기준입니다.

## STEP 2. 스킬 설치하기: 3분

터미널에서 실행:

```bash
npx skills add ayghri/i-have-adhd -g
```

CLI 없이 수동으로 넣을 수도 있습니다.

```bash
git clone https://github.com/ayghri/i-have-adhd
mkdir -p ~/.cursor/skills
cp -R i-have-adhd/skills/i-have-adhd ~/.cursor/skills/
```

클론한 폴더가 작업 저장소를 더럽히면 지워도 됩니다. 커서가 읽는 것은 복사된 `~/.cursor/skills/i-have-adhd` 입니다.

- ❌ 이렇게 말고: SKILL.md를 사용자 규칙에 통째로 붙여 항상 켜 두기
- ✅ 이렇게: 스킬로 설치하고, 필요할 때만 `/i-have-adhd` 로 켜기

항상 켜고 싶다면 INSTALL.md가 적는 방법은 두 가지입니다. 클로드 코드는 `touch ~/.claude/.i-have-adhd-always`. 커서는 Settings → Rules → User Rules 에 짧은 출력 규칙 10줄을 넣는 쪽입니다. 칼럼·에세이 초안까지 같은 말투가 되면 글이 너무 짧아질 수 있어, 이 자료는 always-on을 기본값으로 두지 않습니다.

## STEP 3. 한 턴으로 확인하기: 3분

커서를 재시작하고 새 채팅을 엽니다.

```text
/i-have-adhd
```

그다음 시험 질문을 합니다. INSTALL.md가 쓰는 예에 가깝습니다.

```text
빈 Git 저장소를 새 폴더에 만드는 방법을 알려 줘.
```

성공이면 첫 줄이 `mkdir` 또는 `git init` 같은 행동입니다. 실패면 “좋은 질문입니다” “몇 가지 방법이 있습니다”로 시작합니다.

README가 적는 규칙 10개는 짧습니다.

1. 다음 행동을 먼저 말하기
2. 여러 단계는 번호
3. 마지막에 실행 가능한 다음 한 가지
4. 옆길로 새지 않기
5. 매 턴 진행 상태 다시 말하기
6. 시간은 “조금”이 아니라 분 단위
7. 바뀐 뒤 무엇이 되는지만 보이기
8. 오류는 위치·원인·수정만
9. 목록은 5개까지
10. 서론·요약·맺음말 금지

끄려면 같은 대화에서 `stop adhd mode` 또는 `normal mode` 라고 하면 됩니다.

## STEP 4. 이 사이트 작업에 쓰기: 2분

이 단계에서는 언제 켜고 언제 끌지를 나눕니다.

켜 두는 편이 나은 작업.

- `build_guides.py` 오류 한 줄 고치기
- `column.html` 에 항목 하나 추가하기
- 배포 전 확인할 명령만 받기

꺼 두는 편이 나은 작업.

- 에세이·칼럼 초안. 여운과 단락 리듬이 잘립니다.
- 제도를 길게 설명해야 하는 메모.

- ❌ 이렇게 말고: 모든 채팅을 always-on으로 고정하기
- ✅ 이렇게: 코딩 채팅에서만 `/i-have-adhd` 를 치고, 글쓰기 채팅은 끄기

이름이 진단명처럼 보여도, 크레딧은 성인 ADHD 도구 키트의 아이디어를 LLM 답변 형식에 옮긴 것이라고 적습니다. 의료 도구가 아닙니다.

## 자주 막히는 곳

| 증상 | 원인과 해결 |
| --- | --- |
| `/i-have-adhd` 가 목록에 없습니다 | 세션이 설치 전에 열린 상태입니다. 새 채팅을 여세요. 폴더 이름과 SKILL.md frontmatter의 `name` 이 같아야 합니다 |
| 설치했는데도 서론이 깁니다 | 스킬을 호출하지 않았습니다. `/i-have-adhd` 를 먼저 치세요 |
| 끄고 싶은데 계속 짧습니다 | `stop adhd mode` 또는 `normal mode`. 그래도 남으면 새 채팅을 여세요 |
| `npx skills add` 후 폴더가 없습니다 | 에이전트 경로가 다릅니다. INSTALL.md는 커서에 `~/.cursor/skills/` 를 적습니다 |
| 클로드 코드 플러그인 설치가 실패합니다 | `owner/repo` 형식을 쓰세요. 로컬 경로는 저장소 루트여야 하고 `.claude-plugin/` 만 가리키면 안 됩니다 |

## 솔직히 한계

- 이 스킬은 모델을 더 똑똑하게 만들지 않습니다. 틀린 답을 짧게 말할 수도 있습니다. 짧다고 맞은 것은 아닙니다.
- 칼럼 문장에는 잘 안 맞습니다. 행정 에세이는 여지를 남기는 어조가 필요한데, 규칙 10번은 맺음말까지 자릅니다.
- 에이전트마다 자동 호출 여부가 다릅니다. INSTALL.md는 클로드 코드·Qwen·Codex·Grok에서 명시 호출 전까지는 꺼져 있다고 적습니다. 커서는 하네스에 따라 설명문만 보고 스스로 켤 수 있습니다.
- always-on은 편하지만, 글쓰기와 코딩이 한 창에서 섞이면 부작용이 큽니다.
- 저장소 이름은 진단명이 아닙니다. 브랜드입니다.

되돌리기:

```bash
npx skills remove i-have-adhd -g
```

수동 복사했다면 `rm -rf ~/.cursor/skills/i-have-adhd` 입니다. 클로드 코드는 `claude plugin uninstall i-have-adhd` 후 `claude plugin marketplace remove i-have-adhd` 입니다.

## 공식 자료

- 저장소: [ayghri/i-have-adhd](https://github.com/ayghri/i-have-adhd)
- 설치: [INSTALL.md](https://github.com/ayghri/i-have-adhd/blob/main/INSTALL.md)
- 규칙 전문: [skills/i-have-adhd/SKILL.md](https://github.com/ayghri/i-have-adhd/blob/main/skills/i-have-adhd/SKILL.md)
- 라이선스: [MIT](https://github.com/ayghri/i-have-adhd/blob/main/LICENSE)

---

## 커서에 실무 스킬 세 개만 넣는 5단계 | 2026-09-20 | AI·커서·AgentSkills
slug: claude-and-agent-skills
repo: addyosmani/agent-skills
minutes: 16
steps: 5
sections: 9
excerpt: 에이전트는 명세 없이 파일부터 고칩니다. Addy Osmani의 agent-skills에서 이 사이트에 필요한 세 개만 커서에 넣는 다섯 단계입니다.

개인 사이트도 파일이 늘면, 커서가 칼럼 HTML과 배포 스크립트를 한 번에 만집니다. 이 자료는 주간 트렌드의 addyosmani/agent-skills에서 스킬 25개를 다 넣지 않고, 명세·기록·리뷰 세 개만 이 프로젝트에 붙이는 다섯 단계를 담았습니다. 구글 규모 제품의 TDD·CI 전부를 이 저장소에 옮기려는 글이 아닙니다.

복사해서 바로 시작하는 프롬프트. 세 스킬 설치와 목록 확인까지 AI에게 맡기기.

```prompt
역할: 이 프로젝트의 커서에 addyosmani/agent-skills 가운데 세 개만 설치하는 담당
맥락: 이 저장소는 GitHub Pages 개인 사이트입니다. 칼럼·가이드 HTML과 publish.py가 핵심입니다. 스킬 25개 전체는 넣지 마세요. CI/CD·관측·출시 스킬은 설치하지 마세요.
입력: 설치할 스킬 = spec-driven-development, documentation-and-adrs, code-review-and-quality. 운영체제·셸·Node는 직접 확인하세요.
작업: ① Node와 npx를 확인하세요. ② `npx skills add addyosmani/agent-skills --list` 로 목록이 보이는지 확인하세요. ③ 위 세 스킬만 `--skill` 옵션으로 이 워크스페이스에 설치하세요. `--global` 과 전체 25개 설치는 하지 마세요. ④ `.cursor/skills/` 아래 세 폴더와 각 `SKILL.md` 를 확인하세요. ⑤ 사용자에게 새 채팅에서 `/spec` `/review` 를 어떻게 쓰는지, 그리고 단건 설치 때 `references/` 가 빠질 수 있다는 점(업스트림 이슈 #361)을 안내하세요.
제약: `.cursor/rules/` 에 SKILL.md 본문을 붙여 넣지 마세요. git config를 바꾸지 마세요. 이 저장소의 칼럼 HTML 본문을 수정하지 마세요.
출력: 실행한 명령, 설치된 경로, 각 SKILL.md 존재 여부, 호출 예, #361 한계 한 줄
검증: `.cursor/skills/spec-driven-development/SKILL.md`, `.cursor/skills/documentation-and-adrs/SKILL.md`, `.cursor/skills/code-review-and-quality/SKILL.md` 세 파일이 있어야 합니다. 다른 22개 스킬 폴더가 생겼으면 완료가 아닙니다. 그 폴더를 나열하고 지우기 전에 물어보세요.
```

## Quick Start

- 공식 저장소: [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills)
- 커서 설치: [docs/cursor-setup.md](https://github.com/addyosmani/agent-skills/blob/main/docs/cursor-setup.md)
- 한 줄 정의: 코딩 에이전트가 명세·구현·검증·리뷰를 건너뛰지 않게, 단계와 증빙을 적어 둔 스킬 묶음입니다. 이 자료는 그중 세 개만 씁니다.
- 인기·만든 곳: 2026년 9월 20일 GitHub API 기준 스타 97,217개. 같은 날 주간 트렌드 스냅샷에서는 한 주 동안 3,445개가 늘었습니다. 만든 곳은 Addy Osmani입니다.
- 라이선스: MIT.
- 필요한 환경: Node.js와 npx, 이 프로젝트를 연 커서.
- 비용: 설치는 무료입니다. 스킬이 켜지면 읽어야 할 마크다운이 늘고, 그만큼 대화 토큰이 늘 수 있습니다.

25개를 한 번에 넣으라는 공식 한 줄은 아래입니다. 이 자료에서는 쓰지 않습니다.

```bash
npx skills add addyosmani/agent-skills
```

대신 목록을 본 뒤 세 개만 고릅니다.

터미널에서 실행:

```bash
npx skills add addyosmani/agent-skills --list
```

> 검증: 2026-09-20 기준 (README Quick Start, cursor-setup.md, MIT, 이슈 #361)

## STEP 1. 왜 세 개만인지 보기: 2분

이 단계에서는 전체 팩이 이 저장소와 안 맞는 지점을 먼저 봅니다.

README는 수명 주기를 `/spec` `/plan` `/build` `/test` `/review` `/ship` 으로 나눕니다. 그 아래 스킬은 25개입니다. 프론트엔드 WCAG, OWASP, OpenTelemetry, 트렁크 기반 배포까지 들어 있습니다.

이 사이트는 정적 HTML과 GitHub API 배포입니다. 테스트 러너가 없고, 프로덕션 관측도 없습니다. 25개를 넣으면 커서가 없는 파이프라인까지 만들려고 할 수 있습니다.

그래서 이 자료가 고르는 세 개는 이렇습니다.

1. `spec-driven-development` — 새 가이드 섹션이나 페이지를 열기 전에 범위부터 적게
2. `documentation-and-adrs` — `context-notes.md` 처럼 “왜 그렇게 했는지”를 남기게
3. `code-review-and-quality` — `build_guides.py` 같은 스크립트를 합치기 전에 다섯 축으로 보게

나머지는 나중에 필요할 때 `--skill` 로 추가하면 됩니다.

## STEP 2. 세 스킬만 설치하기: 4분

프로젝트 루트(이 저장소)에서 실행합니다. `--global` 은 붙이지 않습니다.

터미널에서 실행:

```bash
npx skills add addyosmani/agent-skills --skill spec-driven-development
npx skills add addyosmani/agent-skills --skill documentation-and-adrs
npx skills add addyosmani/agent-skills --skill code-review-and-quality
```

커서만 지정하려면 각 줄 끝에 `-a cursor -y` 를 붙여도 됩니다.

확인:

```bash
ls .cursor/skills/spec-driven-development/SKILL.md
ls .cursor/skills/documentation-and-adrs/SKILL.md
ls .cursor/skills/code-review-and-quality/SKILL.md
```

세 줄 모두 경로가 나오면 성공입니다.

공식 README가 적는 주의가 있습니다. 스킬을 하나씩 설치하면 `skills/<이름>/` 만 복사되고, 저장소 루트의 `references/` 체크리스트는 안 따라옵니다. 스킬 본문은 동작하지만, 공유 체크리스트 경로는 비어 있을 수 있습니다. 추적 이슈는 [#361](https://github.com/addyosmani/agent-skills/issues/361) 입니다. 체크리스트까지 필요하면 저장소를 클론한 뒤 `rsync -a agent-skills/skills/ .cursor/skills/` 를 쓰는 쪽이 맞습니다. 그 경우에도 이 자료는 세 폴더만 남기고 나머지는 지우라고 권합니다.

## STEP 3. 규칙 창에 붙이지 않기: 3분

이 단계에서는 커서가 스킬을 찾는 위치만 맞춥니다.

공식 커서 문서는 역할을 나눕니다. 짧은 정책은 `.cursor/rules/*.mdc`. 긴 절차는 `.cursor/skills/<이름>/SKILL.md`. SKILL.md 전문을 규칙에 복사하지 말라고 적습니다.

필요할 때만 아래처럼 짧은 포인터를 둘 수 있습니다. 없어도 세 스킬은 폴더만으로 동작하는 경우가 많습니다.

```text
---
description: Use agent-skills workflows from .cursor/skills
alwaysApply: true
---

비사소한 코드 작업 전에 `.cursor/skills/` 의 spec-driven-development, documentation-and-adrs, code-review-and-quality 를 읽으세요. SKILL.md 본문을 이 규칙에 붙여 넣지 마세요.
```

파일 위치는 `.cursor/rules/agent-skills.mdc` 입니다. alwaysApply를 켜면 매 채팅에 이 짧은 글이 들어갑니다. 긴 체크리스트는 넣지 마세요.

- ❌ 이렇게 말고: 25개 SKILL.md를 규칙 한 파일에 이어 붙이기
- ✅ 이렇게: `.cursor/skills/` 에 두고, 필요할 때 스킬 이름으로 부르기

`agents/` 폴더의 페르소나 파일은 커서가 자동으로 읽지 않습니다. 코드 리뷰가 필요하면 `code-review-and-quality` 스킬을 쓰면 됩니다.

## STEP 4. 새 채팅에서 한번 불러 보기: 4분

커서를 재시작하고 이 프로젝트를 연 새 채팅에서 시험합니다.

명세부터 필요할 때.

```text
/spec
guides 목록에 검색창을 넣을지 말지, 범위와 하지 말 일부터 적어 줘. 코드는 아직 쓰지 마.
```

리뷰가 필요할 때.

```text
/review
방금 고친 build_guides.py만 다섯 축으로 봐 줘. 칼럼 HTML은 범위 밖이다.
```

기록만 필요할 때.

```text
이번 결정의 이유만 documentation-and-adrs 형식에 맞춰 context-notes.md 끝에 붙여 줄 초안을 보여 줘. 파일은 아직 고치지 마.
```

성공이면 에이전트가 해당 SKILL.md의 절차(범위, 증빙, 건너뛰지 말 것)를 따라 갑니다. 실패면 일반 채팅처럼 바로 코드를 고칩니다. 그때는 스킬 폴더 이름을 한 번 더 말하면 됩니다.

클로드 코드로 전체 팩을 쓰는 사람은 README의 `/plugin marketplace add addyosmani/agent-skills` 경로가 있습니다. SSH 키가 없으면 HTTPS URL을 쓰라고 README가 적습니다. 이 자료의 기본은 커서와 `npx skills add` 입니다.

## STEP 5. 쓰지 말 것: 3분

이 단계는 설치 후에 커서가 욕심부리지 않게 선을 긋습니다.

이 저장소에서 지금 켜지 않는 스킬 예입니다.

- `ci-cd-and-automation`, `shipping-and-launch` — 배포는 `🚀 사이트에 올리기.bat` 한 길입니다.
- `test-driven-development` — 테스트 러너가 아직 없습니다. 테스트 없이 TDD 스킬만 켜면 없는 파일을 만들기 쉽습니다.
- `observability-and-instrumentation` — 정적 페이지에 메트릭 스택이 필요 없습니다.
- `/build auto` — README도 사람이 계획 승인과 실패 중단을 남긴다고 적습니다. 칼럼 원문을 한 번에 맡기기에는 범위가 큽니다.

나중에 사이트에 검색이나 위젯을 붙일 때는 `frontend-ui-engineering` 이나 `browser-testing-with-devtools` 를 그때 추가하면 됩니다.

## 자주 막히는 곳

| 증상 | 원인과 해결 |
| --- | --- |
| 스킬이 목록에 없습니다 | `.cursor/skills/<이름>/SKILL.md` 가 있는지, frontmatter에 `name` 과 `description` 이 있는지 보세요. 새 채팅을 여세요 |
| 25개가 한꺼번에 생겼습니다 | `npx skills add addyosmani/agent-skills` 전체 설치를 탄 것입니다. 쓸 세 폴더만 남기고 나머지는 지우기 전에 목록을 보여 달라고 하세요 |
| 체크리스트 파일을 못 찾습니다 | 단건 `--skill` 설치의 한계입니다. #361. 클론 후 rsync 하거나, 해당 체크리스트만 그 스킬 폴더로 복사하세요 |
| 규칙과 스킬이 겹쳐 말이 깁니다 | SKILL.md를 `.mdc` 에 붙여 넣은 상태입니다. 규칙에서는 포인터만 남기세요 |
| `/spec` 이 코드를 바로 씁니다 | 스킬이 안 읽힌 것입니다. 채팅에 `spec-driven-development 스킬을 먼저 읽고, 코드는 쓰지 마` 라고 한 줄 더 적으세요 |

## 솔직히 한계

- 이 팩은 시니어 엔지니어링 절차를 에이전트에 심는 도구입니다. 칼럼 문장을 다듬어 주지는 않습니다. 글의 AI 티는 Humanizer, 답 형식은 i-have-adhd 쪽이 맞습니다.
- 스킬을 읽는다고 구현이 안전해지지는 않습니다. 검증 항목만 길게 나열하고 테스트를 안 돌릴 수도 있습니다.
- 단건 설치는 `references/` 가 빠집니다. 전체 클론은 반대 문제, 즉 쓰지 않는 22개가 컨텍스트를 차지합니다.
- `/build auto` 는 작업 사이 사람 개입을 줄일 뿐, 실패와 위험한 단계는 멈추라고 README가 적습니다. 이 사이트의 칼럼 원문·배포 토큰이 걸린 작업에는 맞지 않습니다.
- `agents/` 페르소나는 커서 자동 로드 대상이 아닙니다.

되돌리기:

```bash
npx skills remove spec-driven-development
npx skills remove documentation-and-adrs
npx skills remove code-review-and-quality
```

폴더가 남으면 프로젝트의 `.cursor/skills/` 아래 해당 이름만 지우면 됩니다. 이 저장소에 원래 있던 다른 규칙 파일은 건드리지 마세요.

## 공식 자료

- 저장소: [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills)
- 커서 설정: [docs/cursor-setup.md](https://github.com/addyosmani/agent-skills/blob/main/docs/cursor-setup.md)
- 스킬 CLI: [npx skills add addyosmani/agent-skills](https://github.com/addyosmani/agent-skills#quick-start)
- 단건 설치와 references 공백: [이슈 #361](https://github.com/addyosmani/agent-skills/issues/361)
- 라이선스: [MIT](https://github.com/addyosmani/agent-skills/blob/main/LICENSE)
