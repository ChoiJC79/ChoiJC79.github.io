# ai_practice.json으로 AI 실무 가이드 목록(practice.html)과 상세(practice/*.html)를 생성하는 빌더
"""
사용법:
  python3 build_practice.py          # practice.html + practice/*.html 생성
  python3 build_practice.py --check  # 데이터 검증만
"""
import html
import json
import re
import sys
from pathlib import Path

BASE = Path(__file__).parent
DATA = BASE / "ai_practice.json"
OUT = BASE / "practice"
SITE = "https://choijc79.github.io"
CATS = ["기초", "업무", "연구", "코딩", "자동화"]
FIELDS = ["slug", "date", "cat", "icon", "title", "summary", "when", "steps", "prompt", "cautions", "takeaway"]
e = html.escape


def head(title, desc, url, og_type):
    return f"""<!DOCTYPE html>
<html lang="ko" data-theme="dark">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:type" content="{og_type}">
<meta property="og:url" content="{url}">
<meta property="og:site_name" content="최승환 · Jecheon">
<link rel="stylesheet" href="/css/synthwave.css">
<link rel="stylesheet" href="/css/pages.css">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable-dynamic-subset.min.css">
<link href="https://fonts.googleapis.com/css2?family=Noto+Serif+KR:wght@600;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/css/theme.css">
<link rel="stylesheet" href="/css/practice.css">
</head>
<body>
<header class="site-header">
  <div class="logo">최승환 · 가이드</div>
  <nav class="nav-links">
    <a href="/">← 홈</a>
    <a href="/about.html">소개</a>
    <a href="/research.html">연구</a>
    <a href="/column.html">칼럼</a>
    <a href="/guides.html">가이드</a>
    <a href="/memo.html">정리노트</a>
  </nav>
  <button id="theme-toggle" onclick="toggleTheme()">&#9728; 라이트</button>
</header>
"""


def foot(extra_js=""):
    return """
<footer>&copy; 2026 최승환 · choijc79.github.io</footer>
<div id="mqb">
  <a href="/">🏠<br>홈</a>
  <a href="/about.html">👤<br>소개</a>
  <a href="/column.html">💬<br>칼럼</a>
  <a href="/guides.html" aria-current="page">⚙️<br>가이드</a>
  <a href="/memo.html">📋<br>노트</a>
</div>
<script>
(function(){
  var t=localStorage.getItem('choijc-theme')||'dark';
  document.documentElement.setAttribute('data-theme',t);
  var btn=document.getElementById('theme-toggle');
  if(btn) btn.textContent=t==='dark'?'\\u2600 라이트':'\\u263e 다크';
})();
function toggleTheme(){
  var next=document.documentElement.getAttribute('data-theme')==='dark'?'light':'dark';
  document.documentElement.setAttribute('data-theme',next);
  localStorage.setItem('choijc-theme',next);
  var btn=document.getElementById('theme-toggle');
  if(btn) btn.textContent=next==='dark'?'\\u2600 라이트':'\\u263e 다크';
}
""" + extra_js + """</script>
<script src="https://cdn.jsdelivr.net/npm/motion@13.4.6/dist/motion.js" defer></script>
<script src="/js/motion.js" defer></script>
</body>
</html>
"""


def first_sentence(text):
    m = re.match(r"(.+?[.!?])(\s|$)", text)
    return m.group(1) if m else text


def minutes(g):
    chars = len(g["summary"]) + len(g["prompt"]) + len(g["takeaway"])
    chars += sum(len(x) for x in g["when"] + g["cautions"]) + sum(len(a) + len(b) for a, b in g["steps"])
    return max(2, round(chars / 450))


def load():
    raw = DATA.read_bytes().replace(b"\x00", b"")
    guides = json.loads(raw.decode("utf-8"))
    errs, slugs, dates = [], set(), set()
    for i, g in enumerate(guides):
        tag = g.get("slug", f"#{i}")
        errs += [f"{tag}: '{k}' 누락" for k in FIELDS if not g.get(k)]
        if not re.fullmatch(r"[a-z0-9-]+", g.get("slug", "")):
            errs.append(f"{tag}: 슬러그는 영소문자·숫자·하이픈만")
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", g.get("date", "")):
            errs.append(f"{tag}: 날짜는 YYYY-MM-DD")
        if g.get("cat") not in CATS:
            errs.append(f"{tag}: 분류는 {CATS} 중 하나")
        if g.get("slug") in slugs:
            errs.append(f"{tag}: 슬러그 중복")
        if g.get("date") in dates:
            errs.append(f"{tag}: 날짜 중복")
        slugs.add(g.get("slug"))
        dates.add(g.get("date"))
    if errs:
        sys.exit("데이터 오류:\n  " + "\n  ".join(errs))
    return sorted(guides, key=lambda g: g["date"])


def build_list(guides):
    counts = {c: sum(g["cat"] == c for g in guides) for c in CATS}
    tabs = [f'<button class="pr-tab active" data-cat="전체">전체<small>{len(guides)}</small></button>']
    tabs += [f'<button class="pr-tab" data-cat="{c}">{c}<small>{counts[c]}</small></button>' for c in CATS]
    rows = []
    for n, g in enumerate(guides, 1):
        rows.append(
            f'  <li class="pr-row" data-cat="{e(g["cat"])}"><a href="/practice/{g["slug"]}.html">'
            f'<span class="pr-no">{n:02d}</span>'
            f'<span class="pr-title">{g["icon"]} {e(g["title"])}</span>'
            f'<span class="pr-side"><span class="pr-chip">{e(g["cat"])}</span>{g["date"]}</span>'
            f'<span class="pr-sum">{e(first_sentence(g["summary"]))}</span></a></li>'
        )
    desc = "보고서·민원·논문·코딩·자동화까지, 지방행정 실무자가 정리한 생성형 AI 활용 가이드 20편."
    js = """document.querySelectorAll('.pr-tab').forEach(function(b){
  b.addEventListener('click',function(){
    document.querySelectorAll('.pr-tab').forEach(function(x){x.classList.toggle('active',x===b);});
    var c=b.getAttribute('data-cat');
    document.querySelectorAll('.pr-row').forEach(function(r){r.hidden=!(c==='전체'||r.getAttribute('data-cat')===c);});
  });
});
"""
    return (head("AI 실무 가이드 | 최승환", desc, f"{SITE}/practice.html", "website") + f"""
<section class="hero">
  <div class="hero-label">AI Practice</div>
  <h1>일하는 방식에 AI를 더하는<br>실무 가이드</h1>
  <p>{e(desc)} 편마다 세 칸 요약, 단계, 복사용 프롬프트, 주의사항 순서로 한 화면에 정리했습니다.</p>
  <div class="hero-meta">총 {len(guides)}편 · 마지막 업데이트 {guides[-1]["date"]} · <a href="/guides.html">주간 GitHub 도구 가이드 보기 →</a></div>
</section>
<main class="pr-wrap">
  <div class="pr-tabs" role="tablist">
    {chr(10).join("    " + t for t in tabs).strip()}
  </div>
  <ol class="pr-index">
{chr(10).join(rows)}
  </ol>
</main>
""" + foot(js))


def build_page(g, prev_g, next_g):
    when = "".join(f"<li>{e(x)}</li>" for x in g["when"])
    steps = "\n".join(f"    <li><div><b>{e(t)}</b><span>{e(b)}</span></div></li>" for t, b in g["steps"])
    checks = "\n".join(f"    <li>{e(x)}</li>" for x in g["cautions"][1:])
    pager = ""
    if prev_g:
        pager += f'<a class="prev" href="/practice/{prev_g["slug"]}.html"><small>← 이전</small>{e(prev_g["title"])}</a>'
    if next_g:
        pager += f'<a class="next" href="/practice/{next_g["slug"]}.html"><small>다음 →</small>{e(next_g["title"])}</a>'
    caution_sec = f"""
  <section class="pr-sec">
    <h2>함께 챙길 것</h2>
    <ul class="pr-checks">
{checks}
    </ul>
  </section>""" if checks else ""
    js = """document.querySelectorAll('.pr-copy').forEach(function(b){
  b.addEventListener('click',function(){
    var t=b.parentNode.querySelector('pre').textContent;
    if(navigator.clipboard) navigator.clipboard.writeText(t).then(function(){b.textContent='복사됨';setTimeout(function(){b.textContent='복사';},1400);});
  });
});
"""
    return (head(f"{g['title']} | AI 실무 가이드", g["summary"], f"{SITE}/practice/{g['slug']}.html", "article") + f"""
<section class="hero pr-hero">
  <div class="hero-label"><a href="/practice.html">AI 실무 가이드</a> · {e(g["cat"])}</div>
  <h1>{g["icon"]} {e(g["title"])}</h1>
  <p>{e(g["summary"])}</p>
  <div class="hero-meta">{g["date"]} · 약 {minutes(g)}분</div>
</section>
<main class="pr-wrap">
  <div class="pr-glance">
    <div class="pr-box"><h2>이럴 때</h2><ul>{when}</ul></div>
    <div class="pr-box key"><h2>핵심</h2><p>{e(g["takeaway"])}</p></div>
    <div class="pr-box"><h2>꼭 지킬 것</h2><p>{e(g["cautions"][0])}</p></div>
  </div>

  <section class="pr-sec">
    <h2>따라 하기</h2>
    <ol class="pr-steps">
{steps}
    </ol>
  </section>

  <section class="pr-sec">
    <h2>바로 쓰는 프롬프트</h2>
    <div class="pr-prompt"><button type="button" class="pr-copy">복사</button><pre>{e(g["prompt"])}</pre></div>
  </section>
{caution_sec}
  <nav class="pr-pager">{pager}</nav>
</main>
""" + foot(js))


def main():
    guides = load()
    if "--check" in sys.argv:
        for g in guides:
            print(f"  [{g['date']}] {g['cat']:<3} {g['slug']}  {g['title']}")
        print(f"OK: {len(guides)}편")
        return
    OUT.mkdir(exist_ok=True)
    for i, g in enumerate(guides):
        prev_g = guides[i - 1] if i > 0 else None
        next_g = guides[i + 1] if i < len(guides) - 1 else None
        (OUT / f"{g['slug']}.html").write_text(build_page(g, prev_g, next_g), encoding="utf-8")
    (BASE / "practice.html").write_text(build_list(guides), encoding="utf-8")
    print(f"생성 완료: practice.html + practice/ {len(guides)}개")


if __name__ == "__main__":
    main()
