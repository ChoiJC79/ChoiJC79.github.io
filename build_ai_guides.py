# ai_guides.json 데이터로 ai-guide.html(목록)과 ai/*.html(개별 가이드)을 생성하는 스크립트
import html
import json
import os
import re
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "ai_guides.json")
OUT_DIR = os.path.join(BASE_DIR, "ai")
LIST_PATH = os.path.join(BASE_DIR, "ai-guide.html")
SITE = "https://choijc79.github.io"
CATS = ["기초", "업무", "연구", "코딩", "자동화"]
REQUIRED = ["slug", "date", "cat", "icon", "title", "summary", "when", "steps", "prompt", "cautions", "takeaway"]

e = html.escape

HEAD = """<!DOCTYPE html>
<html lang="ko" data-theme="dark">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:type" content="{og_type}">
<meta property="og:url" content="{url}">
<meta property="og:site_name" content="최승환 · Jecheon">
<meta name="twitter:card" content="summary">
<link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600;700&family=Rajdhani:wght@400;500;600;700&family=Share+Tech+Mono&family=Noto+Sans+KR:wght@300;400;500;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/css/synthwave.css">
<link rel="stylesheet" href="/css/pages.css">
<style>
*{{box-sizing:border-box;margin:0;padding:0;}}
body{{font-family:var(--font-body);font-weight:400;background:var(--bg);color:var(--text);word-break:keep-all;overflow-wrap:anywhere;}}
a{{color:var(--accent);text-decoration:none;}}
.site-header{{position:sticky;top:0;z-index:100;background:var(--bg);border-bottom:1px solid var(--border);padding:0 2rem;display:flex;align-items:center;justify-content:space-between;height:52px;}}
.logo{{font-family:var(--font-display);font-size:15px;color:var(--accent);letter-spacing:0.04em;}}
.nav-links{{display:flex;gap:1.5rem;font-size:12px;}}
.nav-links a{{color:var(--muted);transition:color 0.15s;}}
.nav-links a:hover{{color:var(--accent);}}
#theme-toggle{{background:none;border:1px solid var(--border);color:var(--muted);font-size:11px;padding:3px 11px;border-radius:20px;cursor:pointer;font-family:var(--font-body);margin-left:1rem;}}
#theme-toggle:hover{{border-color:var(--accent);color:var(--accent);}}
.hero{{max-width:760px;margin:0 auto;padding:4rem 2rem 2rem;border-bottom:1px solid var(--border);}}
.hero-label{{font-size:11px;letter-spacing:0.12em;color:var(--accent);text-transform:uppercase;margin-bottom:0.8rem;}}
.hero h1{{font-family:var(--font-display);font-size:clamp(22px,3.6vw,32px);font-weight:700;line-height:1.35;margin-bottom:0.9rem;text-transform:none;letter-spacing:0.01em;}}
.hero p{{color:var(--muted);font-size:14px;line-height:1.8;}}
.hero-meta{{font-size:11px;color:var(--muted);margin-top:0.8rem;letter-spacing:0.04em;opacity:0.8;}}
footer{{border-top:1px solid var(--border);padding:2rem;text-align:center;font-size:11px;color:var(--muted);letter-spacing:0.04em;margin-top:2rem;}}
@media(max-width:600px){{.site-header{{padding:0 1rem;gap:0.6rem;}}.logo{{font-size:12px;white-space:nowrap;}}.nav-links{{gap:0.8rem;font-size:11px;}}.nav-links a{{white-space:nowrap;letter-spacing:0;}}.nav-links a:nth-child(3){{display:none;}}#theme-toggle{{margin-left:0.3rem;white-space:nowrap;}}}}
{extra_css}
</style>
</head>
<body>
<header class="site-header">
  <div class="logo">최승환 · AI 가이드</div>
  <nav class="nav-links">
    <a href="/">← 홈으로</a>
    <a href="/ai-guide.html">가이드 목록</a>
    <a href="/column.html">칼럼</a>
  </nav>
  <button id="theme-toggle" onclick="toggleTheme()">&#9790; 다크</button>
</header>
"""

FOOT = """<footer>
  © 2026 최승환 · choijc79.github.io
</footer>
<script>
(function(){
  var t=localStorage.getItem('choijc-theme')||'dark';
  document.documentElement.setAttribute('data-theme',t);
  var btn=document.getElementById('theme-toggle');
  if(btn) btn.textContent=t==='dark'?'☀ 라이트':'☾ 다크';
})();
function toggleTheme(){
  var next=document.documentElement.getAttribute('data-theme')==='dark'?'light':'dark';
  document.documentElement.setAttribute('data-theme',next);
  localStorage.setItem('choijc-theme',next);
  var btn=document.getElementById('theme-toggle');
  if(btn) btn.textContent=next==='dark'?'☀ 라이트':'☾ 다크';
}
%s
</script>
</body>
</html>
"""

LIST_CSS = """.tab-nav{max-width:760px;margin:0 auto;padding:1.4rem 2rem 0;display:flex;flex-wrap:wrap;gap:0.5rem;}
.tab-btn{background:none;border:1px solid var(--border);color:var(--muted);font-size:12px;padding:5px 14px;border-radius:20px;cursor:pointer;font-family:var(--font-body);}
.tab-btn .cnt{opacity:0.6;margin-left:4px;font-size:11px;}
.tab-btn:hover{color:var(--accent);border-color:var(--accent);}
.tab-btn.active{background:var(--accent);border-color:var(--accent);color:var(--bg);}
.col-list{max-width:760px;margin:0 auto;padding:1.4rem 2rem 2rem;display:flex;flex-direction:column;gap:1.2rem;}
.col-card{background:var(--surface);border:1px solid var(--border);border-radius:4px;padding:1.5rem 1.8rem;color:inherit;display:flex;gap:1.2rem;align-items:flex-start;transition:border-color 0.2s,transform 0.15s;}
.col-card:hover{border-color:var(--accent);transform:translateY(-2px);}
.col-icon{font-size:1.8rem;line-height:1;flex-shrink:0;width:2.4rem;text-align:center;}
.col-meta{display:flex;gap:0.8rem;align-items:center;margin-bottom:0.5rem;}
.col-date{font-size:11px;color:var(--muted);letter-spacing:0.04em;}
.col-tag{font-size:10px;color:var(--accent);border:1px solid var(--border);padding:1px 8px;border-radius:10px;}
.col-title{font-family:var(--font-display);font-size:1.05rem;font-weight:600;margin-bottom:0.45rem;line-height:1.45;}
.col-excerpt{font-size:13px;color:var(--muted);line-height:1.7;margin-bottom:0.6rem;}
.col-more{font-size:11px;color:var(--accent);letter-spacing:0.04em;}
.col-card[hidden]{display:none;}
@media(max-width:600px){.tab-nav{padding:1rem 1rem 0;}.col-list{padding:1rem;}.col-card{padding:1.1rem 1.1rem;gap:0.8rem;}.col-icon{font-size:1.4rem;width:1.8rem;}}"""

LIST_JS = """document.querySelectorAll('.tab-btn').forEach(function(b){
  b.addEventListener('click',function(){
    document.querySelectorAll('.tab-btn').forEach(function(x){x.classList.remove('active');x.setAttribute('aria-selected','false');});
    b.classList.add('active');b.setAttribute('aria-selected','true');
    var c=b.getAttribute('data-cat');
    document.querySelectorAll('.col-card').forEach(function(card){
      card.hidden=!(c==='전체'||card.getAttribute('data-cat')===c);
    });
  });
});"""

PAGE_CSS = """.wrap{max-width:760px;margin:0 auto;padding:0 2rem;}
.sec{padding:2.2rem 0 0.4rem;}
.sec h2{font-family:var(--font-display);font-size:13px;letter-spacing:0.12em;color:var(--accent);text-transform:uppercase;margin-bottom:1rem;}
.sec h2 span{color:var(--text);font-family:var(--font-body);font-size:15px;letter-spacing:0;text-transform:none;margin-left:0.5rem;font-weight:600;}
.when li,.caution li{list-style:none;position:relative;padding-left:1.2rem;font-size:14.5px;line-height:1.8;margin-bottom:0.35rem;}
.when li::before{content:'▸';position:absolute;left:0;color:var(--accent);}
.caution li::before{content:'!';position:absolute;left:0.2rem;color:var(--accent2);font-weight:700;}
.steps{counter-reset:s;}
.step{counter-increment:s;display:grid;grid-template-columns:2.4rem 1fr;gap:1rem;margin-bottom:1.3rem;}
.step::before{content:counter(s,decimal-leading-zero);font-family:var(--font-display);font-size:1.2rem;color:var(--accent);opacity:0.7;line-height:1.5;}
.step-title{font-weight:600;font-size:15px;margin-bottom:0.25rem;}
.step-body{font-size:14px;color:var(--muted);line-height:1.8;}
.prompt-box{position:relative;background:var(--surface);border:1px solid var(--border);border-radius:4px;}
.prompt-box pre{font-family:var(--font-mono);font-size:13px;line-height:1.75;white-space:pre-wrap;word-break:keep-all;overflow-wrap:anywhere;padding:2.6rem 1.4rem 1.3rem;color:var(--text);}
.copy-btn{position:absolute;top:0.6rem;right:0.6rem;background:var(--bg);border:1px solid var(--border);color:var(--muted);font-size:11px;padding:3px 10px;border-radius:12px;cursor:pointer;font-family:var(--font-body);}
.copy-btn:hover{color:var(--accent);border-color:var(--accent);}
.takeaway{margin:2.4rem 0 0;padding:1.3rem 1.5rem;border-left:3px solid var(--accent2);background:var(--surface);font-size:16px;font-weight:600;line-height:1.7;}
.pager{display:grid;grid-template-columns:1fr 1fr;gap:1rem;margin:2.6rem 0 0;}
.pager a{display:block;border:1px solid var(--border);border-radius:4px;padding:0.9rem 1.1rem;color:inherit;font-size:13px;line-height:1.5;transition:border-color 0.2s;}
.pager a:hover{border-color:var(--accent);}
.pager small{display:block;font-size:10px;color:var(--muted);letter-spacing:0.08em;margin-bottom:0.2rem;}
.pager .next{text-align:right;grid-column:2;}
@media(max-width:600px){.wrap{padding:0 1.1rem;}.hero{padding:2.6rem 1.1rem 1.6rem;}.pager{grid-template-columns:1fr;}.pager .next{grid-column:1;}}"""

PAGE_JS = """document.querySelectorAll('.copy-btn').forEach(function(b){
  b.addEventListener('click',function(){
    var t=b.parentNode.querySelector('pre').innerText;
    navigator.clipboard.writeText(t).then(function(){b.textContent='복사됨';setTimeout(function(){b.textContent='복사';},1500);});
  });
});"""


def load():
    with open(DATA_PATH, "rb") as f:
        raw = f.read().replace(b"\x00", b"")
    guides = json.loads(raw.decode("utf-8"))
    errors = []
    seen_slug, seen_date = set(), set()
    for i, g in enumerate(guides):
        tag = g.get("slug", f"#{i}")
        for k in REQUIRED:
            if not g.get(k):
                errors.append(f"{tag}: '{k}' 누락")
        if not re.fullmatch(r"[a-z0-9-]+", g.get("slug", "")):
            errors.append(f"{tag}: 슬러그는 영소문자·숫자·하이픈만 허용")
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", g.get("date", "")):
            errors.append(f"{tag}: 날짜 형식은 YYYY-MM-DD")
        if g.get("cat") not in CATS:
            errors.append(f"{tag}: 분류는 {CATS} 중 하나")
        if g.get("slug") in seen_slug:
            errors.append(f"{tag}: 슬러그 중복")
        if g.get("date") in seen_date:
            errors.append(f"{tag}: 날짜 중복 ({g.get('date')})")
        seen_slug.add(g.get("slug"))
        seen_date.add(g.get("date"))
    if errors:
        sys.exit("데이터 오류:\n  " + "\n  ".join(errors))
    return sorted(guides, key=lambda g: g["date"], reverse=True)


def build_list(guides):
    counts = {c: sum(1 for g in guides if g["cat"] == c) for c in CATS}
    tabs = ['<button class="tab-btn active" data-cat="전체" role="tab" aria-selected="true">전체<span class="cnt">%d</span></button>' % len(guides)]
    tabs += ['<button class="tab-btn" data-cat="%s" role="tab" aria-selected="false">%s<span class="cnt">%d</span></button>' % (c, c, counts[c]) for c in CATS]
    cards = []
    for g in guides:
        cards.append(f"""  <a class="col-card" href="/ai/{g['slug']}.html" data-cat="{e(g['cat'])}">
    <div class="col-icon">{g['icon']}</div>
    <div>
      <div class="col-meta"><span class="col-date">{g['date']}</span><span class="col-tag">{e(g['cat'])}</span></div>
      <h2 class="col-title">{e(g['title'])}</h2>
      <p class="col-excerpt">{e(g['summary'])}</p>
      <span class="col-more">가이드 읽기 →</span>
    </div>
  </a>""")
    latest = guides[0]["date"]
    desc = "지방행정 실무자가 정리한 생성형 AI 활용 가이드. 업무·연구·바이브코딩·자동화까지 바로 쓰는 절차와 프롬프트."
    out = HEAD.format(title="AI 가이드 | 최승환", desc=desc, og_type="website", url=f"{SITE}/ai-guide.html", extra_css=LIST_CSS)
    out += f"""
<section class="hero">
  <div class="hero-label">AI Practice Guide</div>
  <h1>일하는 방식에 AI를 더하는<br>실무 가이드</h1>
  <p>보고서·민원·논문·코딩·자동화까지, 행정 현장과 연구실에서 직접 써 본 방식을 절차와 프롬프트로 정리합니다. 입력해도 되는 자료와 안 되는 자료의 경계부터 함께 봅니다.</p>
  <div class="hero-meta">총 {len(guides)}편 · 마지막 업데이트 {latest}</div>
</section>

<nav class="tab-nav" role="tablist">
  {chr(10).join('  ' + t for t in tabs).strip()}
</nav>

<section class="col-list">
{chr(10).join(cards)}
</section>

"""
    out += FOOT % LIST_JS
    return out


def build_page(g, prev_g, next_g):
    when = "\n".join(f"      <li>{e(x)}</li>" for x in g["when"])
    steps = "\n".join(
        f'      <div class="step"><div><div class="step-title">{e(t)}</div><p class="step-body">{e(b)}</p></div></div>'
        for t, b in g["steps"]
    )
    cautions = "\n".join(f"      <li>{e(x)}</li>" for x in g["cautions"])
    pager = ""
    if prev_g:
        pager += f'<a class="prev" href="/ai/{prev_g["slug"]}.html"><small>← 이전 가이드</small>{e(prev_g["title"])}</a>'
    if next_g:
        pager += f'<a class="next" href="/ai/{next_g["slug"]}.html"><small>다음 가이드 →</small>{e(next_g["title"])}</a>'
    out = HEAD.format(
        title=f"{e(g['title'])} | AI 가이드",
        desc=e(g["summary"]),
        og_type="article",
        url=f"{SITE}/ai/{g['slug']}.html",
        extra_css=PAGE_CSS,
    )
    out += f"""
<section class="hero">
  <div class="hero-label">{g['icon']} AI Guide · {e(g['cat'])}</div>
  <h1>{e(g['title'])}</h1>
  <p>{e(g['summary'])}</p>
  <div class="hero-meta">{g['date']} · 최승환</div>
</section>

<main class="wrap">
  <section class="sec">
    <h2>When<span>이럴 때 쓰세요</span></h2>
    <ul class="when">
{when}
    </ul>
  </section>

  <section class="sec">
    <h2>How<span>따라하기</span></h2>
    <div class="steps">
{steps}
    </div>
  </section>

  <section class="sec">
    <h2>Prompt<span>바로 쓰는 프롬프트</span></h2>
    <div class="prompt-box"><button class="copy-btn">복사</button><pre>{e(g['prompt'])}</pre></div>
  </section>

  <section class="sec">
    <h2>Caution<span>주의할 점</span></h2>
    <ul class="caution">
{cautions}
    </ul>
  </section>

  <div class="takeaway">{e(g['takeaway'])}</div>

  <nav class="pager">{pager}</nav>
</main>

"""
    out += FOOT % PAGE_JS
    return out


def main():
    guides = load()
    if "--check" in sys.argv:
        print(f"OK: {len(guides)}편, 데이터 오류 없음")
        return
    os.makedirs(OUT_DIR, exist_ok=True)
    # 목록은 최신순, 이전/다음은 발행 순서(과거→최신) 기준
    chrono = list(reversed(guides))
    for i, g in enumerate(chrono):
        prev_g = chrono[i - 1] if i > 0 else None
        next_g = chrono[i + 1] if i < len(chrono) - 1 else None
        with open(os.path.join(OUT_DIR, f"{g['slug']}.html"), "w", encoding="utf-8") as f:
            f.write(build_page(g, prev_g, next_g))
    with open(LIST_PATH, "w", encoding="utf-8") as f:
        f.write(build_list(guides))
    print(f"생성 완료: ai-guide.html + ai/ {len(guides)}개")


if __name__ == "__main__":
    main()
