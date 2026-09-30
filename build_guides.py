#!/usr/bin/env python3
# GitHub 트렌드 도구를 단계별 AI 가이드 HTML로 만드는 빌더

"""
사용법:
  python3 build_guides.py          # guides.html + guides/*.html 생성
  python3 build_guides.py --check  # 파싱 결과만 출력
"""

import html as hl
import re
import sys
from pathlib import Path

BASE_DIR = Path(__file__).parent
SRC_PATH = BASE_DIR / "💬 AI가이드.md"
OUT_DIR = BASE_DIR / "guides"
SITE = "https://choijc79.github.io"

THEME_JS = """
(function(){
  var t=localStorage.getItem('choijc-theme')||'dark';
  document.documentElement.setAttribute('data-theme',t);
  var btn=document.getElementById('theme-toggle');
  if(btn) btn.textContent=t==='dark'?'\\u2600 라이트':'\\u263e 다크';
})();
function toggleTheme(){
  var html=document.documentElement;
  var next=html.getAttribute('data-theme')==='dark'?'light':'dark';
  html.setAttribute('data-theme',next);
  localStorage.setItem('choijc-theme',next);
  var btn=document.getElementById('theme-toggle');
  if(btn) btn.textContent=next==='dark'?'\\u2600 라이트':'\\u263e 다크';
}
function copyBlock(btn){
  var box=btn.closest('.g-code,.g-prompt');
  if(!box) return;
  var code=box.querySelector('code');
  var text=code?code.textContent:'';
  function done(){
    var old=btn.textContent;
    btn.textContent='복사됨';
    setTimeout(function(){btn.textContent=old;},1400);
  }
  if(navigator.clipboard&&navigator.clipboard.writeText){
    navigator.clipboard.writeText(text).then(done).catch(function(){});
  }
}
"""

HEAD_FONTS = (
    '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
    '<link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600;700'
    '&family=Rajdhani:wght@400;500;600;700&family=Share+Tech+Mono:wght@400'
    '&family=Noto+Sans+KR:wght@300;400;500;700&family=IBM+Plex+Mono:wght@400'
    '&display=swap" rel="stylesheet">\n'
    '<link rel="stylesheet" href="/css/synthwave.css">\n'
    '<link rel="stylesheet" href="/css/pages.css">\n'
    '<link rel="stylesheet" href="/css/guides.css">\n'
    '<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable-dynamic-subset.min.css">\n'
    '<link href="https://fonts.googleapis.com/css2?family=Noto+Serif+KR:wght@600;700&family=IBM+Plex+Mono:wght@400&display=swap" rel="stylesheet">\n'
    '<link rel="stylesheet" href="/css/theme.css">\n'
)


def inline(s):
    s = hl.escape(s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    s = re.sub(r"\[(.+?)\]\((.+?)\)", r'<a href="\2" target="_blank" rel="noopener">\1</a>', s)
    return s


def fence_block(lang, code):
    escaped = hl.escape(code.rstrip("\n"))
    label = {
        "prompt": "복사해서 바로 시작하는 프롬프트",
        "bash": "터미널에서 실행",
        "text": "붙여넣을 글",
        "json": "JSON",
    }.get(lang, lang or "코드")
    klass = "g-prompt" if lang == "prompt" else "g-code"
    return (
        f'<div class="{klass}">'
        f'<div class="g-code-bar"><span>{hl.escape(label)}</span>'
        f'<button type="button" class="g-copy" onclick="copyBlock(this)">복사</button></div>'
        f"<pre><code>{escaped}</code></pre></div>"
    )


def table_html(rows):
    if len(rows) < 2:
        return ""
    head = rows[0]
    body = rows[2:] if len(rows) > 2 and re.match(r"^\s*\|?\s*-+", rows[1]) else rows[1:]
    def cells(line):
        return [c.strip() for c in line.strip().strip("|").split("|")]
    th = "".join(f"<th>{inline(c)}</th>" for c in cells(head))
    trs = []
    for row in body:
        if re.match(r"^\s*\|?\s*-+", row):
            continue
        trs.append("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in cells(row)) + "</tr>")
    return f'<div class="g-table-wrap"><table class="g-table"><thead><tr>{th}</tr></thead><tbody>{"".join(trs)}</tbody></table></div>'


def md_to_html(text):
    lines = text.split("\n")
    out = []
    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]
        if line.startswith("```"):
            lang = line[3:].strip() or "text"
            buf = []
            i += 1
            while i < n and not lines[i].startswith("```"):
                buf.append(lines[i])
                i += 1
            out.append(fence_block(lang, "\n".join(buf)))
            i += 1
            continue
        if line.strip().startswith("|") and i + 1 < n and "|" in lines[i + 1]:
            rows = []
            while i < n and lines[i].strip().startswith("|"):
                rows.append(lines[i])
                i += 1
            out.append(table_html(rows))
            continue
        if line.startswith("> "):
            buf = [line[2:]]
            i += 1
            while i < n and lines[i].startswith("> "):
                buf.append(lines[i][2:])
                i += 1
            joined = " ".join(buf)
            klass = "g-callout"
            if joined.startswith("용어:"):
                klass += " g-term"
            elif joined.startswith("검증:"):
                klass += " g-verify"
            out.append(f'<blockquote class="{klass}">{inline(joined)}</blockquote>')
            continue
        if line.startswith("## "):
            title = line[3:].strip()
            hid = "quick-start" if title.lower().startswith("quick") else re.sub(r"[^가-힣a-zA-Z0-9]+", "-", title).strip("-").lower()
            out.append(f'<h2 id="{hl.escape(hid)}">{inline(title)}</h2>')
            i += 1
            continue
        if line.startswith("### "):
            out.append(f"<h3>{inline(line[4:].strip())}</h3>")
            i += 1
            continue
        if re.match(r"^[-*] ", line) or re.match(r"^\d+\. ", line):
            ordered = bool(re.match(r"^\d+\. ", line))
            tag = "ol" if ordered else "ul"
            items = []
            while i < n and (re.match(r"^[-*] ", lines[i]) or re.match(r"^\d+\. ", lines[i])):
                item = re.sub(r"^([-*]|\d+\.) ", "", lines[i])
                items.append(f"<li>{inline(item)}</li>")
                i += 1
            out.append(f"<{tag}>{''.join(items)}</{tag}>")
            continue
        if not line.strip():
            i += 1
            continue
        para = [line]
        i += 1
        while i < n and lines[i].strip() and not lines[i].startswith(("#", "```", "|", "> ", "- ", "* ")) and not re.match(r"^\d+\. ", lines[i]):
            para.append(lines[i])
            i += 1
        out.append("<p>" + "<br>".join(inline(p) for p in para) + "</p>")
    return "\n".join(out)


META_KEYS = ("slug", "repo", "minutes", "steps", "sections", "excerpt")


def load_guides():
    raw = SRC_PATH.read_bytes().replace(b"\x00", b"").decode("utf-8")
    parts = re.split(r"\n---\n", raw.strip())
    guides = []
    for part in parts:
        part = part.strip()
        if not part:
            continue
        m = re.match(r"^## (.+?)\s*\|\s*(\d{4}-\d{2}-\d{2})\s*\|\s*(.+?)$", part, re.MULTILINE)
        if not m:
            continue
        rest = part[m.end():].lstrip("\n")
        meta = {k: "" for k in META_KEYS}
        body_lines = rest.split("\n")
        consumed = 0
        for line in body_lines:
            kv = re.match(r"^(slug|repo|minutes|steps|sections|excerpt):\s*(.*)$", line)
            if kv:
                meta[kv.group(1)] = kv.group(2).strip()
                consumed += 1
                continue
            if line.strip() == "" and consumed:
                consumed += 1
                break
            break
        body = "\n".join(body_lines[consumed:]).strip()
        body = re.sub(r"\n---\s*$", "", body).strip()
        guides.append({
            "title": m.group(1).strip(),
            "date": m.group(2).strip(),
            "tags": m.group(3).strip(),
            "body": body,
            **meta,
        })
    guides.sort(key=lambda g: g["date"], reverse=True)
    return guides


def page_shell(title, desc, url, body_html, extra_nav=""):
    return f"""<!DOCTYPE html>
<html lang="ko" data-theme="dark">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{hl.escape(title)} | 최승환</title>
<meta name="description" content="{hl.escape(desc)}">
<meta property="og:title" content="{hl.escape(title)}">
<meta property="og:description" content="{hl.escape(desc)}">
<meta property="og:type" content="article">
<meta property="og:url" content="{url}">
<meta property="og:site_name" content="최승환 · Jecheon">
{HEAD_FONTS}</head>
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
{body_html}
{extra_nav}
<footer>&copy; 2026 최승환 · choijc79.github.io</footer>
<div id="mqb">
  <a href="/">🏠<br>홈</a>
  <a href="/about.html">👤<br>소개</a>
  <a href="/column.html">💬<br>칼럼</a>
  <a href="/guides.html" aria-current="page">⚙️<br>가이드</a>
  <a href="/memo.html">📋<br>노트</a>
</div>
<script>{THEME_JS}</script>
</body>
</html>
"""


def make_list_page(guides):
    cards = []
    for g in guides:
        tags = "".join(f'<span class="col-tag">{hl.escape(t)}</span>' for t in g["tags"].split("·") if t)
        cards.append(
            f'<a class="col-card" href="/guides/{hl.escape(g["slug"])}.html">'
            f'<div class="col-meta"><span class="col-date">{hl.escape(g["date"])}</span>{tags}</div>'
            f'<h2 class="col-title">{hl.escape(g["title"])}</h2>'
            f'<p class="col-excerpt">{hl.escape(g["excerpt"] or g["title"])}</p>'
            f'<span class="col-more">가이드 읽기 →</span></a>'
        )
    last = guides[0]["date"] if guides else ""
    body = f"""
<section class="hero">
  <div class="hero-label">AI Guides</div>
  <h1>이번 주 GitHub 트렌드,<br>클로드로 직접 써 보기</h1>
  <p>매주 트렌드에서 도구 하나를 골라, 복사해서 따라 할 수 있는 단계로 정리합니다.</p>
  <div class="hero-meta">마지막 업데이트 · {hl.escape(last)}</div>
</section>
<section class="col-list">
{''.join(cards)}
</section>
"""
    return page_shell(
        "AI 가이드",
        "GitHub 트렌드 도구를 클로드와 함께 쓰는 단계별 가이드.",
        f"{SITE}/guides.html",
        body,
    )


def make_guide_page(g, prev_g, next_g):
    meta = (
        f'<span>읽는 데 {hl.escape(g["minutes"] or "—")}분</span>'
        f'<span>스텝 {hl.escape(g["steps"] or "—")}개</span>'
        f'<span>섹션 {hl.escape(g["sections"] or "—")}개</span>'
        f'<span>{hl.escape(g["date"])} 공개</span>'
    )
    repo = ""
    if g["repo"]:
        repo = (
            f'<p class="g-repo">이번 주 트렌드 · '
            f'<a href="https://github.com/{hl.escape(g["repo"])}" target="_blank" rel="noopener">'
            f'{hl.escape(g["repo"])}</a></p>'
        )
    nav_bits = []
    if prev_g:
        nav_bits.append(
            f'<a class="nav-prev" href="/guides/{hl.escape(prev_g["slug"])}.html">← {hl.escape(prev_g["title"])}</a>'
        )
    if next_g:
        nav_bits.append(
            f'<a class="nav-next" href="/guides/{hl.escape(next_g["slug"])}.html">{hl.escape(next_g["title"])} →</a>'
        )
    extra = f'<nav class="art-nav">{"".join(nav_bits)}</nav>' if nav_bits else ""
    body = f"""
<article class="article-wrap g-article">
  <div class="a-type">AI 가이드</div>
  <h1 class="a-title">{hl.escape(g["title"])}</h1>
  <div class="g-meta">{meta}</div>
  {repo}
  <div class="a-body">
    {md_to_html(g["body"])}
  </div>
</article>
"""
    return page_shell(g["title"], g["excerpt"] or g["title"], f'{SITE}/guides/{g["slug"]}.html', body, extra)


def main():
    check_only = "--check" in sys.argv
    if not SRC_PATH.exists():
        print("원문 파일이 없습니다:", SRC_PATH)
        sys.exit(1)
    guides = load_guides()
    print(f"가이드 {len(guides)}편")
    if check_only:
        for g in guides:
            print(f'  [{g["date"]}] {g["slug"]}  {g["title"]}  repo={g["repo"]}')
        return
    OUT_DIR.mkdir(exist_ok=True)
    (BASE_DIR / "guides.html").write_text(make_list_page(guides), encoding="utf-8")
    print("  guides.html")
    for i, g in enumerate(guides):
        if not g["slug"]:
            print("  skip (slug 없음):", g["title"])
            continue
        prev_g = guides[i + 1] if i + 1 < len(guides) else None
        next_g = guides[i - 1] if i > 0 else None
        path = OUT_DIR / f'{g["slug"]}.html'
        path.write_text(make_guide_page(g, prev_g, next_g), encoding="utf-8")
        print(f'  guides/{g["slug"]}.html')
    print("생성 완료")


if __name__ == "__main__":
    main()
