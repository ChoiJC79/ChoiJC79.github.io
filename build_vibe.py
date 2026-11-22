# vibe_course.json으로 바이브 코딩 단계별 과정 목록(vibe.html)과 레슨(vibe/*.html)을 만드는 빌더
"""
사용법:
  python3 build_vibe.py          # vibe.html + vibe/*.html 생성
  python3 build_vibe.py --check  # 데이터 검증만
"""
import json
import re
import sys
from pathlib import Path

from build_practice import e, foot, head as practice_head, SITE

BASE = Path(__file__).parent
DATA = BASE / "vibe_course.json"
OUT = BASE / "vibe"
KEYS = "slug title goal why concepts bad good diff mission done cards".split()


def t(s):
    """이스케이프 후 `백틱`을 <code>로."""
    return re.sub(r"`([^`]+)`", r"<code>\1</code>", e(s))


def lv_label(lv):
    return "도구" if lv["lv"] == "T" else f"Lv.{lv['lv']}"


def head(title, desc, url, og_type):
    return practice_head(title, desc, url, og_type).replace(
        "</head>", '<link rel="stylesheet" href="/css/vibe.css">\n</head>')


def page_foot():
    return foot().replace("</body>", '<script src="/js/vibe.js" defer></script>\n</body>')


def load():
    d = json.loads(DATA.read_text(encoding="utf-8"))
    errs = []
    for x in d["lessons"]:
        errs += [f"{x.get('slug')}: '{k}' 누락" for k in KEYS if not x.get(k)]
        if any(not (c.get("q") and c.get("a")) for c in x.get("cards", [])):
            errs.append(f"{x['slug']}: 카드마다 q·a 필요")
    if errs:
        sys.exit("데이터 오류:\n  " + "\n  ".join(errs))
    return d


def tutor_prompt(x):
    cs = ", ".join(f"「{h}」" for h, _ in x["concepts"])
    return f"""너는 내 바이브 코딩 튜터다. 나는 「{x['title']}」 단계를 공부하고 있다.
이 단계의 목표는 「{x['goal']}」
다룰 개념은 {cs}이다.

규칙
1. 설명부터 하지 말고, 내가 지금 만드는 프로젝트가 무엇인지 먼저 한 가지만 묻는다.
2. 질문은 한 번에 하나씩. 내 프로젝트 상황에 맞춘 문제를 낸다.
3. 내가 틀리면 정답을 바로 말하지 말고 힌트를 하나 준 뒤 다시 묻는다.
4. 개념마다 내가 실제로 보낼 프롬프트를 직접 써 보게 하고, 부족한 점을 고쳐 준다.
5. 서로 다른 상황 문제 세 개를 연속으로 맞히면 「통과」라고 말하고, 아직 약한 부분을 한 줄로 알려 준다.
6. 통과하기 전에는 다음 단계로 넘어가지 않는다."""


def build_lesson(x, lv, n, prev_x, next_x):
    concepts = "\n".join(f"    <li><div><b>{t(h)}</b><span>{t(b)}</span></div></li>" for h, b in x["concepts"])
    mission = "\n".join(f"    <li><div><span>{t(m)}</span></div></li>" for m in x["mission"])
    done = "\n".join(f"    <li>{t(d)}</li>" for d in x["done"])
    cards = "\n".join(
        f'      <li class="vb-card"><details><summary>{t(c["q"])}</summary><p>{t(c["a"])}</p></details>'
        f'<label class="vb-know"><input type="checkbox" data-i="{i}"> 안다</label></li>'
        for i, c in enumerate(x["cards"]))
    snippet = f"""
  <section class="pr-sec">
    <h2>자주 쓰는 코드</h2>
    <div class="pr-prompt"><button type="button" class="pr-copy">복사</button><pre>{e(x["snippet"])}</pre></div>
  </section>
""" if x.get("snippet") else ""
    pager = ""
    if prev_x:
        pager += f'<a class="prev" href="/vibe/{prev_x["slug"]}.html"><small>← 이전</small>{e(prev_x["title"])}</a>'
    if next_x:
        pager += f'<a class="next" href="/vibe/{next_x["slug"]}.html"><small>다음 →</small>{e(next_x["title"])}</a>'
    locked = prev_x and lv["lv"] != "T"
    prev_attr = f' data-prev="{prev_x["slug"]}" data-prev-title="{e(prev_x["title"])}"' if locked else ""
    return head(f"{x['title']} | 바이브 코딩 단계별 과정", x["goal"], f"{SITE}/vibe/{x['slug']}.html", "article") + f"""
<section class="hero pr-hero">
  <div class="hero-label"><a href="/vibe.html">바이브 코딩 단계별 과정</a> · {lv_label(lv)} {e(lv['name'])}</div>
  <h1>{n:02d}. {e(x["title"])}</h1>
  <p>{e(x["goal"])}</p>
  <div class="hero-meta">개념 읽기 → 실습 → 요점 카드 모두 「안다」 → 튜터와 대화로 다지기</div>
</section>
<main class="pr-wrap vb-lesson" data-slug="{x['slug']}"{prev_attr}>
  <p class="vb-lock" hidden></p>

  <section class="pr-sec">
    <h2>왜 여기서 막히나</h2>
    <p class="vb-why">{e(x["why"])}</p>
  </section>

  <section class="pr-sec">
    <h2>핵심 개념 세 가지</h2>
    <ol class="pr-steps">
{concepts}
    </ol>
  </section>
{snippet}
  <section class="pr-sec">
    <h2>같은 일, 다른 요청</h2>
    <div class="vb-compare">
      <div class="vb-ex bad"><h3>이렇게 요청하면</h3><pre>{e(x["bad"])}</pre></div>
      <div class="vb-ex good"><h3>이렇게 요청한다</h3><div class="pr-prompt"><button type="button" class="pr-copy">복사</button><pre>{e(x["good"])}</pre></div></div>
    </div>
    <p class="vb-diff">{e(x["diff"])}</p>
  </section>

  <section class="pr-sec">
    <h2>30분 실습</h2>
    <ol class="pr-steps">
{mission}
    </ol>
    <h3 class="vb-sub">통과 기준</h3>
    <ul class="pr-checks">
{done}
    </ul>
  </section>

  <section class="pr-sec" id="cards">
    <h2>요점 카드</h2>
    <p class="vb-note">질문을 보고 답을 먼저 떠올린 뒤 눌러서 확인합니다. 답을 보지 않고 말할 수 있는 카드에만 「안다」를 표시하고, 모든 카드에 표시하면 이 단계를 통과합니다.</p>
    <button type="button" class="vb-open">모두 펼치기</button>
    <ol class="vb-cards">
{cards}
    </ol>
    <p class="vb-msg"></p>
  </section>

  <section class="pr-sec">
    <h2>튜터와 다지기</h2>
    <p class="vb-note">문제를 맞혔어도 내 프로젝트에서 바로 쓰지 못하면 아직 아는 것이 아닙니다. 아래 프롬프트를 Claude에 붙여 넣으면 「통과」라고 할 때까지 내 상황에 맞춘 질문을 계속 받습니다.</p>
    <div class="pr-prompt"><button type="button" class="pr-copy">복사</button><pre>{e(tutor_prompt(x))}</pre></div>
  </section>

  <nav class="pr-pager">{pager}</nav>
</main>
""" + page_foot()


def build_list(d, order):
    lv_rows = []
    for lv in d["levels"]:
        items = [(n, x) for n, (l, x) in enumerate(order, 1) if l is lv]
        lis = "\n".join(
            f'      <li class="pr-row vb-row" data-slug="{x["slug"]}"><a href="/vibe/{x["slug"]}.html">'
            f'<span class="pr-no">{n:02d}</span><span class="pr-title">{e(x["title"])}</span>'
            f'<span class="pr-side vb-state">아직</span><span class="pr-sum">{e(x["goal"])}</span></a></li>'
            for n, x in items)
        lv_rows.append(f"""  <section class="vb-level" data-lv="{lv['lv']}">
    <h2><span class="vb-lv">{lv_label(lv)}</span>{e(lv['name'])}<small>{e(lv['band'])} · <span class="vb-count">0</span>/{len(items)} 통과</small></h2>
    <ol class="pr-index">
{lis}
    </ol>
  </section>""")
    desc = "「만들어줘」 다음 단계로 가는 바이브 코딩 과정. 스펙, 검증, 구조, 에이전트까지 네 단계 12편과, 업무 자동화에 많이 쓰는 언어·라이브러리 도구 상자 10편을 요점 카드로 하나씩 익힙니다."
    return head("바이브 코딩 단계별 과정 | 최승환", desc, f"{SITE}/vibe.html", "website") + f"""
<section class="hero">
  <div class="hero-label">Vibe Coding Course</div>
  <h1>「만들어줘」 다음 단계,<br>바이브 코딩 단계별 과정</h1>
  <p>{e(desc)}</p>
  <div class="hero-meta">지금 <b class="vb-total">0</b>/{len(order)} 통과 · <span class="vb-rank">Lv.2</span> · 진행 기록은 이 브라우저에만 저장됩니다</div>
</section>
<main class="pr-wrap vb-home">
  <section class="pr-sec">
    <h2>이 과정이 시작하는 곳</h2>
    <div class="pr-glance">
      <div class="pr-box"><h2>Lv.1 한 줄 요청</h2><p>「홈페이지 만들어줘」처럼 결과만 말하고 나온 것을 그대로 씁니다.</p></div>
      <div class="pr-box"><h2>Lv.2 고쳐 달라기</h2><p>결과를 보고 「버튼 색 바꿔줘」「안 돼요」로 고쳐 갑니다. 여기서 멈추는 사람이 가장 많습니다.</p></div>
      <div class="pr-box key"><h2>Lv.3부터</h2><p>요청하기 전에 설계하고, 받은 결과를 검증하고, 반복을 도구로 고정합니다. 이 과정은 여기서 시작합니다.</p></div>
    </div>
  </section>
  <section class="pr-sec">
    <h2>한 단계를 통과하는 방법</h2>
    <ol class="pr-steps">
      <li><div><b>읽기</b><span>막히는 이유와 개념 세 가지, 나쁜 요청과 좋은 요청을 비교합니다.</span></div></li>
      <li><div><b>실습</b><span>내 프로젝트에서 30분 안에 해 보고 통과 기준을 스스로 확인합니다.</span></div></li>
      <li><div><b>요점 카드</b><span>명령어, 파일 경로, 판단 기준 같은 구체적인 사실을 카드로 정리했습니다. 답을 떠올린 뒤 확인하고, 모든 카드를 「안다」로 표시하면 통과입니다.</span></div></li>
      <li><div><b>튜터와 다지기</b><span>레슨마다 있는 튜터 프롬프트를 Claude에 붙여 넣으면, 내 프로젝트 상황으로 세 문제를 연속으로 맞힐 때까지 질문이 이어집니다.</span></div></li>
    </ol>
  </section>
{chr(10).join(lv_rows)}
</main>
""" + page_foot()


def main():
    d = load()
    order = [(lv, x) for lv in d["levels"] for x in d["lessons"] if x["level"] == lv["lv"]]
    if "--check" in sys.argv:
        for lv, x in order:
            print(f"  {lv_label(lv)} {x['slug']}  {x['title']}")
        print(f"OK: {len(order)}편")
        return
    OUT.mkdir(exist_ok=True)
    for i, (lv, x) in enumerate(order):
        prev_x = order[i - 1][1] if i else None
        next_x = order[i + 1][1] if i < len(order) - 1 else None
        (OUT / f"{x['slug']}.html").write_text(build_lesson(x, lv, i + 1, prev_x, next_x), encoding="utf-8")
    (BASE / "vibe.html").write_text(build_list(d, order), encoding="utf-8")
    print(f"생성 완료: vibe.html + vibe/ {len(order)}개")


if __name__ == "__main__":
    main()
