#!/usr/bin/env python3
"""
build_columns.py — columns/ 개별 칼럼 페이지 재생성 스크립트

사용법:
  python build_columns.py          # columns/ 전체 재생성
  python build_columns.py --check  # 생성 예정 목록만 출력

column.html의 idx-list를 기준으로 슬러그/타입을 읽고,
💬 칼럼·기고.md에서 본문을 매칭해 개별 HTML 페이지를 만든다.
새 칼럼 추가 시: 칼럼·기고.md에 내용 추가 → column.html idx-list에 항목 추가 → 이 스크립트 실행
"""

import re, os, html as hl, sys
from pathlib import Path

BASE_DIR = Path(__file__).parent
COLS_DIR = BASE_DIR / 'columns'
COLS_DIR.mkdir(exist_ok=True)

# ─── 데이터 로드 ─────────────────────────────────────────────

def load_md_cols():
    md_path = BASE_DIR / '💬 칼럼·기고.md'
    with open(md_path, 'r', encoding='utf-8') as f:
        md = f.read()
    parts = re.split(r'\n---\n', md.strip())
    cols = []
    for part in parts:
        part = part.strip()
        if not part:
            continue
        m = re.match(r'^## (.+?)\s*\|\s*(\d{4}-\d{2}-\d{2})\s*\|\s*(.+?)$', part, re.MULTILINE)
        if m:
            cols.append({
                'title': m.group(1).strip(),
                'date': m.group(2).strip(),
                'tags': m.group(3).strip(),
                'body': part[m.end():].strip()
            })
    return cols

def load_column_index():
    """column.html idx-list에서 슬러그/타입/태그/날짜/제목 추출"""
    with open(BASE_DIR / 'column.html', 'r', encoding='utf-8') as f:
        c = f.read()
    html_part = c[:c.find('</html>') + 7] if '</html>' in c else c
    return re.findall(
        r"<li[^>]*data-type=\"([^\"]*)\"\s+onclick=\"location\.href='/columns/([^']+)\.html'\""
        r"[^>]*data-tag=\"([^\"]*)\">.*?"
        r"<span class=\"idx-date\">([^<]*)</span>"
        r"<span class=\"idx-title\">([^<]*)</span>",
        html_part, re.DOTALL
    )

def load_card_images():
    """기존 article 카드에서 이미지 URL 추출"""
    with open(BASE_DIR / 'column.html', 'r', encoding='utf-8') as f:
        c = f.read()
    cards = re.findall(
        r'<article[^>]*data-slug="([^"]*)">'
        r'<div class="col-visual"><img src="([^"]*)"',
        c
    )
    return {slug: img for slug, img in cards}

# ─── 매칭 ────────────────────────────────────────────────────

def title_key(t):
    t = t.split('—')[0].split('...')[0]
    return re.sub(r'[^가-힣a-zA-Z0-9]', '', t).lower()

IMG_POOL = {
    'policy': [
        'https://images.unsplash.com/photo-1477959858617-67f85cf4f1df?w=800&h=520&fit=crop&auto=format&q=80',
        'https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=800&h=520&fit=crop&auto=format&q=80',
        'https://images.unsplash.com/photo-1519501025264-65ba15a82390?w=800&h=520&fit=crop&auto=format&q=80',
        'https://images.unsplash.com/photo-1448375240586-882707db888b?w=800&h=520&fit=crop&auto=format&q=80',
        'https://images.unsplash.com/photo-1461896836934-ffe607ba8211?w=800&h=520&fit=crop&auto=format&q=80',
        'https://images.unsplash.com/photo-1456513080510-7bf3a84b82f8?w=800&h=520&fit=crop&auto=format&q=80',
    ],
    'life': [
        'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800&h=520&fit=crop&auto=format&q=80',
        'https://images.unsplash.com/photo-1476231682828-37e571bc172f?w=800&h=520&fit=crop&auto=format&q=80',
        'https://images.unsplash.com/photo-1508002366005-75a695ee81f1?w=800&h=520&fit=crop&auto=format&q=80',
    ]
}
_img_idx = {'policy': 0, 'life': 0}

def match_cols(li_data, md_cols):
    used = set()
    result = []
    for typ, slug, tag, date, title in li_data:
        tkey = title_key(title)
        best, best_score = None, 0
        for i, col in enumerate(md_cols):
            if i in used or col['date'] != date:
                continue
            ckey = title_key(col['title'])
            score = sum(1 for ch in tkey if ch in ckey) / max(len(tkey), len(ckey), 1)
            if score > best_score:
                best_score, best = score, i
        body = md_cols[best]['body'] if best is not None else ''
        if best is not None:
            used.add(best)
        result.append({'typ': typ, 'slug': slug, 'tag': tag, 'date': date,
                       'title': title, 'body': body})
    return result

# ─── 마크다운 → HTML ─────────────────────────────────────────

def md_to_html(text):
    if not text:
        return '<p>내용을 준비 중입니다.</p>'
    def inline(s):
        s = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', s)
        s = re.sub(r'\*(.+?)\*', r'<em>\1</em>', s)
        return s
    paras = re.split(r'\n{2,}', text.strip())
    result = []
    ul_buf = []
    def flush_ul():
        if ul_buf:
            result.append('<ul>' + ''.join(f'<li>{li}</li>' for li in ul_buf) + '</ul>')
            ul_buf.clear()
    for para in paras:
        para = para.strip()
        if not para:
            continue
        if para.startswith(('- ', '• ')):
            for line in para.split('\n'):
                line = line.lstrip('-• ').strip()
                if line:
                    ul_buf.append(inline(hl.escape(line)))
        elif para.startswith('### '):
            flush_ul()
            result.append(f'<h3>{inline(hl.escape(para[4:]))}</h3>')
        elif para.startswith('## '):
            flush_ul()
            result.append(f'<h2>{inline(hl.escape(para[3:]))}</h2>')
        else:
            flush_ul()
            escaped = inline(hl.escape(para))
            result.append('<p>' + escaped.replace('\n', '<br>') + '</p>')
    flush_ul()
    return '\n'.join(result)

# ─── HTML 페이지 생성 ─────────────────────────────────────────

def make_page(idx, total, col, matched_list):
    typ = col['typ']
    slug = col['slug']
    tag = col['tag']
    date = col['date']
    title = col['title']
    body = col['body']

    prev_item = matched_list[idx + 1] if idx + 1 < total else None
    next_item = matched_list[idx - 1] if idx > 0 else None

    body_plain = re.sub(r'\*+', '', body).replace('\n', ' ').strip()
    excerpt = body_plain[:110] + '…' if len(body_plain) > 110 else body_plain

    type_label = '삶의 기록' if typ == 'life' else '행정·정책'
    type_color = '#3fb950' if typ == 'life' else '#d29922'
    color = type_color

    tag_chips = ''.join(
        f'<span class="a-tag" style="border-color:{color}44;color:{color}">{t.strip()}</span>'
        for t in tag.split('·') if t.strip()
    )

    def nav_link(item, direction):
        if not item:
            return ''
        s, t = item['slug'], item['title']
        label = (t[:30] + '…') if len(t) > 30 else t
        if direction == 'prev':
            return f'<a class="nav-prev" href="/columns/{s}.html">← {hl.escape(label)}</a>'
        return f'<a class="nav-next" href="/columns/{s}.html">{hl.escape(label)} →</a>'

    return f'''<!DOCTYPE html>
<html lang="ko" data-theme="dark">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{hl.escape(title)} — 최승환</title>
<meta name="description" content="{hl.escape(excerpt)}">
<meta property="og:title" content="{hl.escape(title)}">
<meta property="og:description" content="{hl.escape(excerpt)}">
<meta property="og:type" content="article">
<meta property="og:url" content="https://choijc79.github.io/columns/{slug}.html">
<meta property="og:site_name" content="최승환">
<meta property="article:published_time" content="{date}">
<link rel="canonical" href="https://choijc79.github.io/columns/{slug}.html">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Noto+Serif+KR:wght@400;600;700&family=Noto+Sans+KR:wght@300;400;500&family=IBM+Plex+Mono:wght@400&display=swap" rel="stylesheet">
<style>
:root{{--bg:#0d1117;--surface:#161b22;--border:#30363d;--text:#e6edf3;--ink:#c9d1d9;--muted:#8b949e;--accent:#58a6ff;}}
[data-theme="light"]{{--bg:#ffffff;--surface:#f6f8fa;--border:#d0d7de;--text:#1f2328;--ink:#24292f;--muted:#656d76;--accent:#0969da;}}
*{{margin:0;padding:0;box-sizing:border-box;}}
body{{background:var(--bg);color:var(--text);font-family:'Noto Sans KR',sans-serif;font-weight:300;line-height:1.8;}}
a{{color:inherit;text-decoration:none;}}
header{{position:sticky;top:0;z-index:100;background:var(--bg);border-bottom:1px solid var(--border);}}
.hd-inner{{max-width:1100px;margin:0 auto;padding:0 2rem;height:52px;display:flex;align-items:center;gap:1.5rem;}}
.hd-logo{{font-family:'Noto Serif KR',serif;font-size:15px;font-weight:700;color:var(--text);letter-spacing:0.04em;}}
.hd-nav{{display:flex;gap:1.2rem;flex:1;}}
.hd-nav a{{font-size:12px;color:var(--muted);letter-spacing:0.06em;text-transform:uppercase;transition:color 0.15s;}}
.hd-nav a:hover{{color:var(--accent);}}
.hd-back{{margin-left:auto;font-size:11px;color:var(--muted);letter-spacing:0.06em;border:1px solid var(--border);padding:0.3rem 0.8rem;transition:all 0.15s;}}
.hd-back:hover{{border-color:var(--accent);color:var(--accent);}}
.theme-btn{{background:none;border:1px solid var(--border);color:var(--muted);font-size:11px;font-family:inherit;cursor:pointer;padding:0.3rem 0.7rem;transition:all 0.15s;}}
.theme-btn:hover{{border-color:var(--accent);color:var(--accent);}}
.article-wrap{{max-width:720px;margin:0 auto;padding:3rem 2rem 5rem;}}
.a-type{{font-size:10px;letter-spacing:0.18em;text-transform:uppercase;font-weight:500;color:{type_color};margin-bottom:1rem;}}
.a-title{{font-family:'Noto Serif KR',serif;font-size:2rem;font-weight:700;line-height:1.35;color:var(--ink);margin-bottom:1.2rem;}}
.a-meta{{display:flex;align-items:center;gap:0.8rem;flex-wrap:wrap;margin-bottom:2.5rem;padding-bottom:1.5rem;border-bottom:1px solid var(--border);}}
.a-date{{font-family:'IBM Plex Mono',monospace;font-size:12px;color:var(--muted);}}
.a-tag{{font-size:11px;padding:2px 10px;border:1px solid;}}
.a-body{{font-size:15px;line-height:2;color:var(--ink);}}
.a-body p{{margin-bottom:1.6em;}}
.a-body h2,.a-body h3{{font-family:'Noto Serif KR',serif;font-weight:700;margin:2em 0 0.8em;color:var(--text);}}
.a-body h2{{font-size:1.25rem;}}
.a-body h3{{font-size:1.05rem;}}
.a-body ul{{margin:0 0 1.6em 1.5em;}}
.a-body li{{margin-bottom:0.5em;}}
.a-body strong{{font-weight:500;color:var(--text);}}
.art-nav{{max-width:720px;margin:0 auto;padding:2rem 2rem 4rem;display:flex;gap:1rem;border-top:1px solid var(--border);}}
.nav-prev,.nav-next{{font-size:12px;color:var(--muted);transition:color 0.15s;max-width:45%;}}
.nav-prev:hover,.nav-next:hover{{color:var(--accent);}}
.nav-next{{text-align:right;margin-left:auto;}}
footer{{border-top:1px solid var(--border);text-align:center;padding:1.5rem 1rem;font-size:11px;color:var(--muted);letter-spacing:0.04em;}}
#mqb{{display:none;position:fixed;bottom:0;left:0;right:0;z-index:999;background:var(--surface);border-top:1px solid var(--border);padding:0.45rem 0.6rem;gap:0.4rem;justify-content:space-around;}}
#mqb a{{flex:1;text-align:center;color:var(--muted);font-size:10px;padding:0.4rem 0.2rem;border:1px solid var(--border);line-height:1.4;}}
@media(max-width:900px){{.hd-nav{{display:none;}}#mqb{{display:flex;}}body{{padding-bottom:4rem;}}}}
@media(max-width:600px){{.article-wrap{{padding:2rem 1.2rem 4rem;}}.a-title{{font-size:1.5rem;}}.a-body{{font-size:14px;}}.art-nav{{padding:1.5rem 1.2rem 3rem;}}}}
</style>
</head>
<body>
<header>
<div class="hd-inner">
  <a class="hd-logo" href="/">최승환</a>
  <nav class="hd-nav">
    <a href="/about.html">소개</a>
    <a href="/research.html">연구</a>
    <a href="/column.html">칼럼</a>
    <a href="/local.html">제천</a>
  </nav>
  <a class="hd-back" href="/column.html">← 칼럼 목록</a>
  <button class="theme-btn" id="theme-toggle" onclick="toggleTheme()">☀ 라이트</button>
</div>
</header>
<main>
<div class="article-wrap">
  <div class="a-type">{type_label}</div>
  <h1 class="a-title">{hl.escape(title)}</h1>
  <div class="a-meta">
    <span class="a-date">{date}</span>
    {tag_chips}
  </div>
  <div class="a-body">
    {md_to_html(body)}
  </div>
</div>
<nav class="art-nav">
  {nav_link(prev_item, 'prev')}
  {nav_link(next_item, 'next')}
</nav>
</main>
<footer>© 최승환 · choijc79.github.io</footer>
<div id="mqb">
  <a href="/">🏠 홈</a>
  <a href="/about.html">소개</a>
  <a href="/research.html">연구</a>
  <a href="/column.html">칼럼</a>
  <a href="/local.html">제천</a>
</div>
<script>
function toggleTheme(){{var t=document.documentElement.getAttribute('data-theme')==='dark'?'light':'dark';document.documentElement.setAttribute('data-theme',t);localStorage.setItem('choijc-theme',t);var b=document.getElementById('theme-toggle');if(b)b.textContent=t==='dark'?'☀ 라이트':'🌙 다크';}}
(function(){{var t=localStorage.getItem('choijc-theme')||'dark';document.documentElement.setAttribute('data-theme',t);document.addEventListener('DOMContentLoaded',function(){{var b=document.getElementById('theme-toggle');if(b)b.textContent=t==='dark'?'☀ 라이트':'🌙 다크';}});}}());
</script>
</body>
</html>'''

# ─── 메인 ─────────────────────────────────────────────────────

def main():
    check_only = '--check' in sys.argv

    md_cols = load_md_cols()
    li_data = load_column_index()
    img_map = load_card_images()

    if not li_data:
        print('❌ column.html에서 idx-list를 찾을 수 없습니다.')
        return

    matched = match_cols(li_data, md_cols)
    total = len(matched)

    print(f'칼럼 총 {total}개 처리 예정')
    if check_only:
        for col in matched:
            status = '✅' if col['body'] else '❌ 본문 없음'
            print(f'  {status} [{col["date"]}] {col["title"][:40]}')
        return

    for idx, col in enumerate(matched):
        slug = col['slug']
        out_path = COLS_DIR / f'{slug}.html'
        content = make_page(idx, total, col, matched)
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'  [{idx+1:02d}/{total}] {slug}.html')

    print(f'\n✅ {total}개 페이지 생성 완료 → columns/')

if __name__ == '__main__':
    main()
