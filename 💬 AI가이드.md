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
