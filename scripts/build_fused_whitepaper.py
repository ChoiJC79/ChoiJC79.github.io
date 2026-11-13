import re
import subprocess

# 1. Load downloaded file
with open('/Users/aipon/Downloads/민선9기_공약백서.html', 'r', encoding='utf-8') as f:
    down = f.read()

# 2. Load original file from git HEAD to get clean source data
orig = subprocess.check_output(['git', 'show', 'HEAD:jecheon_9th_policy_whitepaper.html']).decode('utf-8')

# Extract Chapters from down
chapters = []
for m in re.finditer(r'<section class="chapter" id="(ch\d+)"([^>]*)>(.*?)</section>', down, re.S):
    cid = m.group(1)
    attrs = m.group(2)
    body = m.group(3)
    chapters.append((cid, attrs, body))

# Extract closing from down
closing = re.search(r'<footer class="closing">(.*?)</footer>', down, re.S).group(1)

# Extract sections from orig
overview_body = re.search(r'<section class="block" id="overview">(.*?)</section>', orig, re.S).group(1)
summary_body = re.search(r'<section class="block" id="summary">(.*?)</section>', orig, re.S).group(1)
insights_body = re.search(r'<section class="block" id="insights">(.*?)</section>', orig, re.S).group(1)

# Extract all 6 department cards from orig
dept_cards = re.findall(r'(<section class="card" id="dept-\d+">.*?</section>)', orig, re.S)

enhanced_dept_cards = []
for card in dept_cards:
    # Add id="pledge-X" and data-no="X" to each tr
    card_enhanced = re.sub(
        r'<tr([^>]*)>\s*<td class="c-no">(\d+)</td>',
        r'<tr\1 id="pledge-\2" data-no="\2">\n          <td class="c-no">\2</td>',
        card
    )
    enhanced_dept_cards.append(card_enhanced)

detail_content = '\n\n'.join(enhanced_dept_cards)

# Extract projects table from orig
proj_sec = re.search(r'<section class="block" id="projects">(.*?)</section>', orig, re.S).group(1)
proj_table = re.search(r'(<table[^>]*>.*?</table>)', proj_sec, re.S).group(1)
proj_table_enhanced = re.sub(
    r'<tr([^>]*)>\s*<td class="c-no">(\d+)</td>',
    r'<tr\1 id="project-\2" data-no="\2">\n              <td class="c-no">\2</td>',
    proj_table
)

# Enhance Chapter 1 core cards with jump functions
core_map = {
    "핵심<br>01": 1,
    "핵심<br>02": 4,
    "핵심<br>03": 5,
    "핵심<br>04": 6,
    "핵심<br>05": 23,
    "핵심<br>06": 27,
    "핵심<br>07": 49,
    "핵심<br>08": 50,
    "핵심<br>09": 51,
    "핵심<br>10": 52
}

def enhance_core_card(match):
    badge = match.group(1).strip()
    content = match.group(2)
    p_no = core_map.get(badge, 1)
    return (
        f'<div class="core-card" onclick="jumpToPledge({p_no})" role="button" tabindex="0" title="클릭하여 상세 검토의견으로 이동">\n'
        f'  <div class="core-card__badge">{badge}</div>\n'
        f'  <div class="core-card__body">\n'
        f'    {content}\n'
        f'    <span class="core-card__link">실무 검토의견 보기 →</span>\n'
        f'  </div>\n'
        f'</div>'
    )

ch1_body = chapters[0][2]
ch1_enhanced = re.sub(
    r'<div class="core-card">\s*<div class="core-card__badge">(.*?)</div>\s*<div>(.*?)</div>\s*</div>',
    enhance_core_card,
    ch1_body,
    flags=re.S
)

# Add jump banners at the end of each chapter in Tab 1
dept_jumps = {
    'ch2': '<div class="chapter-action"><button class="chapter-btn" onclick="jumpToDept(\'dept-3\')">📊 경제산업 분과 11건 세부 실무표 바로가기 →</button></div>',
    'ch3': '<div class="chapter-action"><button class="chapter-btn" onclick="jumpToDept(\'dept-2\')">📊 문화복지 분과 20건 세부 실무표 바로가기 →</button></div>',
    'ch4': '<div class="chapter-action"><button class="chapter-btn" onclick="jumpToDept(\'dept-2\')">📊 문화·관광 관련 세부 실무표 바로가기 →</button></div>',
    'ch5': '<div class="chapter-action"><button class="chapter-btn" onclick="jumpToDept(\'dept-4\')">📊 도시건설 분과 15건 세부 실무표 바로가기 →</button></div>',
    'ch6': '<div class="chapter-action"><button class="chapter-btn" onclick="jumpToDept(\'dept-5\')">📊 청년위원회·여성위원회 분과 실무표 바로가기 →</button></div>',
    'ch7': '<div class="chapter-action"><button class="chapter-btn" onclick="switchMainTab(\'projects\')">📌 도농상생·마을 관련 시책사업 29건 보기 →</button></div>',
    'ch8': '<div class="chapter-action"><button class="chapter-btn" onclick="switchMainTab(\'insights\')">🏛️ 인수위 종합 시사점 및 추진방향 제언 보기 →</button></div>',
}

chapters_rendered = []
for cid, attrs, body in chapters:
    c_body = ch1_enhanced if cid == 'ch1' else body
    if cid in dept_jumps:
        c_body += dept_jumps[cid]
    chapters_rendered.append(f'<section class="chapter" id="{cid}"{attrs}>\n{c_body}\n</section>')

chapters_html = '\n\n'.join(chapters_rendered)

full_html = f'''<!DOCTYPE html>
<html lang="ko" data-theme="dark">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>민선9기 제천시장 공약백서 — 다시, 제천을 위해</title>
<meta name="description" content="제9회 전국동시지방선거 당선인 이상천 제천시장 핵심공약 10선 및 56건 공약사항·29건 시책사업 분야별 종합 백서.">
<meta property="og:title" content="민선9기 제천시장 공약백서 — 다시, 제천을 위해">
<meta property="og:description" content="제9회 전국동시지방선거 당선인 이상천 제천시장 핵심공약 10선 및 56건 공약사항·29건 시책사업 분야별 종합 백서.">
<meta property="og:type" content="website">
<meta property="og:url" content="https://choijc79.github.io/jecheon_9th_policy_whitepaper.html">
<meta property="og:site_name" content="최승환 · Jecheon">

<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Noto+Serif+KR:wght@400;500;600;700;900&family=Noto+Sans+KR:wght@300;400;500;600;700;900&family=IBM+Plex+Mono:wght@400;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable-dynamic-subset.min.css">
<link rel="stylesheet" href="/css/synthwave.css">
<link rel="stylesheet" href="/css/pages.css">
<link rel="stylesheet" href="/css/motion.css">

<style>
:root {{
  --bg: #F8F9FA;
  --surface: #FFFFFF;
  --surface2: #F0F4F8;
  --surface3: #E7EDF3;
  --ink: #1A202C;
  --ink-soft: #4A5568;
  --ink-muted: #718096;
  --line: #E2E8F0;
  
  --lake: #1565A8;
  --lake-light: #EBF4FF;
  --lake-deep: #0D3B6E;
  
  --ember: #C05621;
  --ember-light: #FFF5EE;
  
  --forest: #276749;
  --forest-light: #F0FFF4;
  
  --slate: #2D4A6F;
  --slate-light: #EDF2F7;
  
  --indigo: #4A3880;
  --indigo-light: #F5F2FF;
  
  --olive: #7B6B2E;
  --olive-light: #FFFFF0;
  
  --seal: #C53030;
  --seal-light: #FDE8E8;
  
  --gold: #B8862E;
  --gold-pale: #F4E9D4;
  
  --navy: #14233D;
  --navy-soft: #1F3759;
  --navy-pale: #E7EAF1;
  
  --font-serif: 'Noto Serif KR', Georgia, serif;
  --font-sans: 'Pretendard', 'Noto Sans KR', -apple-system, BlinkMacSystemFont, sans-serif;
  --font-mono: 'IBM Plex Mono', 'Share Tech Mono', monospace;
}}

html[data-theme="dark"] {{
  --bg: #0d1117;
  --surface: #161b22;
  --surface2: #21262d;
  --surface3: #30363d;
  --ink: #f0f6fc;
  --ink-soft: #c9d1d9;
  --ink-muted: #8b949e;
  --line: #30363d;
  
  --lake: #58a6ff;
  --lake-light: rgba(56, 139, 253, 0.15);
  --lake-deep: #0e2238;
  
  --ember: #f0883e;
  --ember-light: rgba(240, 136, 62, 0.15);
  
  --forest: #3fb950;
  --forest-light: rgba(63, 185, 80, 0.15);
  
  --slate: #79c0ff;
  --slate-light: rgba(121, 192, 255, 0.12);
  
  --indigo: #d2a8ff;
  --indigo-light: rgba(210, 168, 255, 0.15);
  
  --olive: #e3b341;
  --olive-light: rgba(227, 179, 65, 0.15);
  
  --seal: #ff7b72;
  --seal-light: rgba(255, 123, 114, 0.15);
  
  --gold: #d29922;
  --gold-pale: #2a2110;
  
  --navy: #e6edf3;
  --navy-soft: #c9d1d9;
  --navy-pale: #21262d;
}}

* {{ box-sizing: border-box; }}
html {{ scroll-behavior: smooth; }}
body {{
  margin: 0;
  background: var(--bg);
  color: var(--ink);
  font-family: var(--font-sans);
  font-size: 15px;
  line-height: 1.7;
  -webkit-font-smoothing: antialiased;
  transition: background 0.2s, color 0.2s;
}}
::selection {{ background: #BEE3F8; color: #1A365D; }}
html[data-theme="dark"] ::selection {{ background: #1f6feb; color: #ffffff; }}

/* ── Site Header ── */
.site-header {{
  position: sticky;
  top: 0;
  z-index: 1000;
  background: var(--surface);
  border-bottom: 1px solid var(--line);
  padding: 0 2rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 52px;
  transition: background 0.2s, border-color 0.2s;
}}
.site-header .logo a {{
  font-family: var(--font-serif);
  font-weight: 700;
  font-size: 15px;
  color: var(--lake);
  text-decoration: none;
  letter-spacing: 0.02em;
}}
.site-header .nav-links {{
  display: flex;
  gap: 1.4rem;
  font-size: 12.5px;
  list-style: none;
  margin: 0;
  padding: 0;
}}
.site-header .nav-links a {{
  color: var(--ink-muted);
  text-decoration: none;
  transition: color 0.15s;
}}
.site-header .nav-links a:hover {{
  color: var(--lake);
}}
#theme-toggle {{
  background: var(--surface2);
  border: 1px solid var(--line);
  color: var(--ink-soft);
  font-size: 11.5px;
  padding: 4px 12px;
  border-radius: 20px;
  cursor: pointer;
  font-family: var(--font-sans);
  transition: all 0.2s;
}}
#theme-toggle:hover {{
  border-color: var(--lake);
  color: var(--lake);
}}

/* ── Top Letterhead ── */
.letterhead {{
  background: var(--lake-deep);
  color: rgba(255, 255, 255, 0.85);
  font-size: 0.72rem;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  padding: 0.55rem 3.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}}
.letterhead small {{ opacity: 0.8; letter-spacing: 0.05em; }}

/* ── Hero ── */
.hero {{
  position: relative;
  background: var(--surface);
  padding: 3rem 3.5rem 2.4rem;
  border-bottom: 1px solid var(--line);
  overflow: hidden;
}}
.hero__top {{
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 2rem;
  flex-wrap: wrap;
}}
.hero__eyebrow {{
  font-size: 0.82rem;
  color: var(--ember);
  font-weight: 700;
  margin: 0 0 0.5rem;
  letter-spacing: 0.06em;
}}
.hero__title {{
  font-family: var(--font-serif);
  font-weight: 900;
  font-size: clamp(2rem, 3.8vw, 3rem);
  line-height: 1.25;
  margin: 0;
  color: var(--ink);
}}
.hero__desc {{
  max-width: 620px;
  margin-top: 1rem;
  color: var(--ink-soft);
  font-size: 0.93rem;
  line-height: 1.85;
}}
.hero__stamp-wrap {{
  display: flex;
  align-items: center;
  gap: 1.5rem;
}}
.stamp {{
  flex-shrink: 0;
  width: 90px;
  height: 90px;
  border-radius: 50%;
  border: 2.5px solid var(--seal);
  color: var(--seal);
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: var(--font-serif);
  font-weight: 900;
  font-size: 1rem;
  line-height: 1.15;
  text-align: center;
  transform: rotate(-5deg);
  opacity: 0.9;
  letter-spacing: 0.05em;
  position: relative;
}}
.stamp::before {{
  content: '';
  position: absolute;
  inset: -6px;
  border-radius: 50%;
  border: 1px dashed var(--seal);
  opacity: 0.45;
}}
.stamp small {{
  display: block;
  font-size: 0.55rem;
  font-weight: 700;
  letter-spacing: 0.2em;
  margin-top: 0.2rem;
}}

.hero__stats {{
  display: flex;
  gap: 0;
  flex-wrap: wrap;
  margin-top: 2.2rem;
  border: 1px solid var(--line);
  border-radius: 8px;
  overflow: hidden;
  background: var(--surface2);
  width: fit-content;
}}
.stat {{
  padding: 0.9rem 1.6rem;
  border-right: 1px solid var(--line);
}}
.stat:last-child {{ border-right: none; }}
.stat strong {{
  display: block;
  font-family: var(--font-serif);
  font-weight: 900;
  font-size: 1.75rem;
  color: var(--lake);
  line-height: 1;
}}
.stat span {{
  font-size: 0.72rem;
  color: var(--ink-muted);
  margin-top: 0.25rem;
  display: block;
}}

/* ── Tab Navigation Bar ── */
.tab-nav-wrapper {{
  background: var(--surface);
  border-bottom: 1px solid var(--line);
  position: sticky;
  top: 52px;
  z-index: 900;
  backdrop-filter: blur(8px);
}}
.tab-nav-container {{
  max-width: 1360px;
  margin: 0 auto;
  padding: 0.6rem 2rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}}
.tab-nav {{
  display: flex;
  gap: 0.5rem;
  overflow-x: auto;
  padding: 2px 0;
}}
.tab-nav::-webkit-scrollbar {{ height: 3px; }}
.tab-nav::-webkit-scrollbar-thumb {{ background: var(--line); border-radius: 2px; }}

.tab-btn {{
  background: transparent;
  border: 1px solid transparent;
  color: var(--ink-soft);
  padding: 0.55rem 1.15rem;
  border-radius: 8px;
  font-family: var(--font-sans);
  font-size: 0.88rem;
  font-weight: 600;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  white-space: nowrap;
  transition: all 0.15s ease;
}}
.tab-btn:hover {{
  background: var(--surface2);
  color: var(--ink);
}}
.tab-btn.active {{
  background: var(--lake-light);
  border-color: rgba(21, 101, 168, 0.3);
  color: var(--lake);
  font-weight: 700;
}}
html[data-theme="dark"] .tab-btn.active {{
  background: rgba(88, 166, 255, 0.15);
  border-color: rgba(88, 166, 255, 0.35);
  color: #79c0ff;
}}
.tab-btn .tab-badge {{
  font-size: 0.68rem;
  padding: 0.1rem 0.45rem;
  border-radius: 10px;
  background: var(--surface2);
  color: var(--ink-muted);
  font-weight: 500;
}}
.tab-btn.active .tab-badge {{
  background: var(--lake);
  color: #fff;
}}
html[data-theme="dark"] .tab-btn.active .tab-badge {{
  background: #388bfd;
  color: #fff;
}}

/* ── Main Layout ── */
.layout {{
  display: flex;
  align-items: flex-start;
  min-height: calc(100vh - 104px);
}}

/* ── Sidebar ── */
.sidebar {{
  width: 260px;
  flex-shrink: 0;
  position: sticky;
  top: 105px;
  height: calc(100vh - 105px);
  overflow-y: auto;
  background: var(--surface);
  border-right: 1px solid var(--line);
  padding: 1.6rem 1.2rem 2rem;
  display: flex;
  flex-direction: column;
}}
.sidebar::-webkit-scrollbar {{ width: 4px; }}
.sidebar::-webkit-scrollbar-thumb {{ background: var(--line); border-radius: 2px; }}

.brand {{
  margin-bottom: 1.2rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--line);
}}
.brand__eyebrow {{
  display: block;
  font-size: 0.65rem;
  letter-spacing: 0.18em;
  color: var(--ink-muted);
  text-transform: uppercase;
  margin-bottom: 0.35rem;
}}
.brand__title {{
  font-family: var(--font-serif);
  font-weight: 900;
  font-size: 1.05rem;
  line-height: 1.45;
  color: var(--lake-deep);
}}
html[data-theme="dark"] .brand__title {{
  color: #79c0ff;
}}

.sidebar-tabs {{
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 3px;
  background: var(--surface2);
  padding: 3px;
  border-radius: 6px;
  margin-bottom: 1.4rem;
}}
.sb-tab {{
  background: transparent;
  border: none;
  color: var(--ink-muted);
  font-size: 0.75rem;
  padding: 0.35rem 0;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.15s;
}}
.sb-tab:hover {{ color: var(--ink); }}
.sb-tab.active {{
  background: var(--surface);
  color: var(--lake);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
}}

.toc {{ list-style: none; margin: 0; padding: 0; }}
.toc-group {{ margin-bottom: 0.2rem; }}
.toc a {{
  --accent: var(--lake);
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.45rem 0.7rem;
  border-radius: 6px;
  font-size: 0.8rem;
  color: var(--ink-soft);
  text-decoration: none;
  transition: all 0.15s ease;
}}
.toc a:hover {{
  color: var(--ink);
  background: var(--surface2);
}}
.toc a.is-active {{
  color: var(--accent);
  background: var(--lake-light);
  font-weight: 700;
}}
.toc a em {{
  font-style: normal;
  font-family: var(--font-serif);
  font-weight: 700;
  color: var(--accent);
  font-size: 0.72rem;
  min-width: 1.4rem;
  opacity: 0.85;
}}
.sidebar-foot {{
  margin-top: auto;
  padding-top: 1.5rem;
  border-top: 1px solid var(--line);
  font-size: 0.72rem;
  color: var(--ink-muted);
  line-height: 1.6;
}}

/* ── Main Content & Panels ── */
.main {{
  flex: 1;
  min-width: 0;
}}
.main-panel {{
  display: none;
}}
.main-panel.active {{
  display: block;
}}

/* ── Panel 1: Chapters (Editorial) ── */
.chapter {{
  padding: 3.4rem 4rem;
  border-bottom: 1px solid var(--line);
  background: var(--surface);
  opacity: 0;
  transform: translateY(12px);
  transition: opacity 0.5s ease, transform 0.5s ease;
}}
.chapter.is-visible {{
  opacity: 1;
  transform: translateY(0);
}}
.chapter:nth-child(even) {{
  background: var(--bg);
}}

.chapter__kicker {{
  display: inline-block;
  font-size: 0.65rem;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  font-weight: 700;
  color: var(--accent, var(--lake));
  background: var(--accent-bg, var(--lake-light));
  padding: 0.2rem 0.65rem;
  border-radius: 3px;
  margin-bottom: 0.8rem;
}}
.chapter__head {{
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 0.4rem;
}}
.chapter__num {{
  font-family: var(--font-serif);
  font-weight: 900;
  font-size: 2.6rem;
  color: var(--accent, var(--lake));
  opacity: 0.25;
  line-height: 0.9;
  flex-shrink: 0;
}}
.chapter__title {{
  font-family: var(--font-serif);
  font-weight: 700;
  font-size: clamp(1.3rem, 2.1vw, 1.8rem);
  margin: 0;
  color: var(--ink);
}}

.lede {{
  border-left: 3px solid var(--accent, var(--lake));
  padding: 0.8rem 1.2rem;
  margin: 1.4rem 0 2rem;
  max-width: 720px;
  font-size: 0.98rem;
  line-height: 2;
  color: var(--ink-soft);
  font-style: italic;
  background: var(--accent-bg, var(--lake-light));
  border-radius: 0 6px 6px 0;
}}

.section {{ margin-top: 2.2rem; }}
.section__title {{
  font-family: var(--font-serif);
  font-weight: 700;
  font-size: 1.05rem;
  color: var(--accent, var(--lake));
  margin: 0 0 0.85rem;
  padding: 0.55rem 0.9rem;
  background: var(--accent-bg, var(--lake-light));
  border-radius: 4px;
  border-left: 3px solid var(--accent, var(--lake));
}}
.subsection {{ margin-top: 1.4rem; }}
.subsection__title {{
  font-weight: 700;
  font-size: 0.95rem;
  color: var(--ink);
  margin: 0 0 0.45rem;
  padding-left: 0.7rem;
  border-left: 2px solid var(--line);
}}

.prose {{
  font-size: 0.94rem;
  line-height: 1.95;
  color: var(--ink-soft);
  max-width: 760px;
  margin: 0 0 0.85rem;
}}

ul.list {{
  list-style: none;
  margin: 0.6rem 0 1.2rem;
  padding: 0;
  max-width: 760px;
}}
ul.list li {{
  position: relative;
  padding: 0.45rem 0.6rem 0.45rem 1.4rem;
  margin-bottom: 0.35rem;
  font-size: 0.9rem;
  line-height: 1.75;
  color: var(--ink-soft);
  background: var(--surface2);
  border-radius: 4px;
}}
ul.list li::before {{
  content: '';
  position: absolute;
  left: 0.55rem;
  top: 0.72em;
  width: 5px;
  height: 5px;
  background: var(--accent, var(--lake));
  border-radius: 50%;
}}

.tag {{
  display: inline-block;
  font-size: 0.68rem;
  padding: 0.15rem 0.5rem;
  border-radius: 12px;
  background: var(--ember-light);
  color: var(--ember);
  border: 1px solid rgba(192, 86, 33, 0.25);
  margin-left: 0.3rem;
  font-weight: 600;
}}

/* Core pledge grid */
.core-grid {{
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.9rem;
  margin: 1.4rem 0 2rem;
}}
.core-card {{
  background: var(--surface);
  border: 1px solid var(--line);
  padding: 1.1rem 1.2rem;
  border-radius: 8px;
  display: flex;
  gap: 1rem;
  align-items: flex-start;
  transition: all 0.2s ease;
  cursor: pointer;
}}
.core-card:hover {{
  border-color: var(--lake);
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
}}
.core-card__badge {{
  flex-shrink: 0;
  width: 44px;
  height: 44px;
  border-radius: 50%;
  border: 2px solid var(--seal);
  color: var(--seal);
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: var(--font-serif);
  font-weight: 900;
  font-size: 0.66rem;
  line-height: 1.1;
  text-align: center;
  background: var(--surface);
}}
.core-card__body {{ flex: 1; }}
.core-card h4 {{
  margin: 0 0 0.35rem;
  font-size: 0.92rem;
  color: var(--ink);
  font-weight: 700;
  line-height: 1.45;
}}
.core-card .core-card__meta {{
  font-size: 0.74rem;
  color: var(--ink-muted);
  margin-bottom: 0.3rem;
}}
.core-card__link {{
  display: inline-block;
  font-size: 0.72rem;
  color: var(--lake);
  font-weight: 600;
}}

.chapter-action {{
  margin-top: 2rem;
  padding-top: 1.2rem;
  border-top: 1px dashed var(--line);
}}
.chapter-btn {{
  background: var(--surface2);
  border: 1px solid var(--line);
  color: var(--ink-soft);
  padding: 0.55rem 1.1rem;
  border-radius: 6px;
  font-size: 0.84rem;
  font-weight: 600;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  transition: all 0.15s;
}}
.chapter-btn:hover {{
  background: var(--lake-light);
  border-color: var(--lake);
  color: var(--lake);
}}

/* Closing */
.closing {{
  padding: 4.5rem 4rem 4rem;
  background: var(--lake-deep);
  color: #E8F0FB;
}}
.closing__kicker {{
  font-size: 0.72rem;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  color: #90CAF9;
  font-weight: 700;
  display: block;
  margin-bottom: 0.8rem;
}}
.closing__title {{
  font-family: var(--font-serif);
  font-weight: 900;
  font-size: clamp(1.6rem, 2.6vw, 2.2rem);
  margin: 0 0 1.6rem;
  color: #fff;
}}
.closing p {{
  font-size: 0.98rem;
  line-height: 2.1;
  max-width: 700px;
  color: #CBD5E0;
  margin: 0 0 1rem;
}}
.closing__sign {{
  margin-top: 2.4rem;
  text-align: right;
  padding-top: 1.6rem;
  border-top: 1px solid rgba(255, 255, 255, 0.15);
}}
.closing__sign strong {{
  font-family: var(--font-serif);
  font-size: 1.2rem;
  display: block;
  color: #fff;
}}
.closing__sign span {{
  font-size: 0.82rem;
  color: #90A4AE;
}}

/* ── Panel 2, 3, 4: Administrative & Data Tables ── */
.panel-wrap {{
  padding: 3rem 4rem 5rem;
  max-width: 1200px;
}}
.block {{ margin-bottom: 50px; }}
.block-head {{
  display: flex;
  align-items: baseline;
  gap: 12px;
  margin-bottom: 20px;
  padding-bottom: 12px;
  border-bottom: 2px solid var(--lake);
}}
.block-head .num {{
  font-family: var(--font-serif);
  font-weight: 900;
  font-size: 24px;
  color: var(--lake);
}}
.block-head h2 {{
  font-family: var(--font-serif);
  font-size: 22px;
  margin: 0;
  color: var(--ink);
}}
.block-intro {{
  color: var(--ink-soft);
  font-size: 14px;
  margin: -10px 0 22px;
}}

/* Distribution chart in summary */
.dist-wrap {{
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: 8px;
  padding: 18px 24px;
  margin-bottom: 28px;
}}
.dist-row {{
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 12px;
  font-size: 13.5px;
}}
.dist-row:last-child {{ margin-bottom: 0; }}
.dist-label {{ width: 88px; font-weight: 700; color: var(--ink); }}
.dist-track {{ flex: 1; height: 10px; background: var(--surface2); border-radius: 5px; overflow: hidden; }}
.dist-fill {{ height: 100%; background: var(--lake); border-radius: 5px; }}
.dist-value {{ width: 95px; text-align: right; font-family: var(--font-mono); font-weight: 700; color: var(--lake); }}
.dist-value em {{ font-style: normal; font-size: 11px; color: var(--ink-muted); margin-left: 4px; font-weight: 400; }}

/* Core list in summary */
.core-list {{
  list-style: none;
  padding: 0;
  margin: 0;
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: 8px;
  overflow: hidden;
}}
.core-list li {{
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 12px 18px;
  border-bottom: 1px solid var(--line);
  font-size: 13.8px;
}}
.core-list li:last-child {{ border-bottom: none; }}
.core-div {{
  font-family: var(--font-mono);
  font-weight: 700;
  font-size: 11.5px;
  color: var(--lake);
  width: 75px;
}}
.core-title {{ flex: 1; font-weight: 600; color: var(--ink); }}
.core-dept {{ font-size: 12px; color: var(--ink-muted); }}

/* Tables */
.table-wrap {{
  overflow-x: auto;
  margin: 1.2rem 0 1.8rem;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: var(--surface);
}}
table {{
  width: 100%;
  border-collapse: collapse;
  font-size: 0.84rem;
  min-width: 600px;
}}
thead th {{
  background: var(--lake-deep);
  color: #fff;
  text-align: left;
  font-weight: 600;
  padding: 0.75rem 1rem;
  font-family: var(--font-serif);
  white-space: nowrap;
}}
tbody td {{
  padding: 0.7rem 1rem;
  border-bottom: 1px solid var(--line);
  color: var(--ink-soft);
  vertical-align: top;
}}
tbody tr:hover td {{ background: var(--lake-light); }}
tbody tr:last-child td {{ border-bottom: none; }}
td.num, th.num {{ text-align: center; }}
tr.tr-total td {{ font-weight: 700; color: var(--ink); background: var(--surface2) !important; }}

/* Row muted */
tr.row-muted td {{ color: var(--ink-muted); opacity: 0.75; }}
tr.row-muted .c-title {{ text-decoration: line-through; text-decoration-color: var(--line); }}
.tag-out {{ background: var(--seal-light); color: var(--seal); border: 1px solid rgba(197, 48, 48, 0.3); font-size: 11px; padding: 2px 6px; border-radius: 4px; }}
.tag-move {{ background: var(--gold-pale); color: var(--gold); border: 1px solid rgba(184, 134, 46, 0.3); font-size: 11px; padding: 2px 6px; border-radius: 4px; }}
.tag-warn {{ background: var(--ember-light); color: var(--ember); border: 1px solid rgba(192, 86, 33, 0.3); font-size: 11px; padding: 2px 6px; border-radius: 4px; }}

/* Info table */
.info-table {{
  width: 100%;
  border-collapse: collapse;
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: 8px;
  overflow: hidden;
}}
.info-table th, .info-table td {{
  border-bottom: 1px solid var(--line);
  padding: 14px 20px;
  text-align: left;
  vertical-align: top;
  font-size: 14px;
}}
.info-table tr:last-child th, .info-table tr:last-child td {{ border-bottom: none; }}
.info-table th {{
  background: var(--surface2);
  color: var(--ink);
  font-weight: 700;
  width: 150px;
  white-space: nowrap;
}}

/* Summary Table */
.summary-table {{
  width: 100%;
  border-collapse: collapse;
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: 8px;
  overflow: hidden;
  margin-bottom: 1.5rem;
}}
.summary-table th, .summary-table td {{
  padding: 11px 16px;
  border-bottom: 1px solid var(--line);
  text-align: left;
  font-size: 13.5px;
}}
.summary-table thead th {{
  background: var(--lake-deep);
  color: #fff;
  font-family: var(--font-serif);
}}
.summary-table tr:last-child th, .summary-table tr:last-child td {{ border-bottom: none; }}
.summary-table tr.total-row {{
  background: var(--surface2);
  font-weight: 700;
}}

/* Department Cards in Detail */
.card {{
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: 8px;
  margin-bottom: 2.2rem;
  overflow: hidden;
}}
.sec-head {{
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 20px;
  background: var(--surface2);
  border-bottom: 1px solid var(--line);
}}
.sec-no {{
  font-family: var(--font-mono);
  font-weight: 700;
  font-size: 12px;
  color: var(--lake);
  background: var(--surface);
  padding: 2px 8px;
  border-radius: 4px;
  border: 1px solid var(--line);
}}
.sec-head h3 {{
  margin: 0;
  font-size: 16px;
  font-weight: 700;
  color: var(--ink);
  flex: 1;
}}
.sec-meta {{
  font-size: 12px;
  color: var(--ink-muted);
}}

/* Data Table Columns */
.data-table th.c-no, .data-table td.c-no {{ width: 50px; text-align: center; font-weight: 700; font-family: var(--font-mono); }}
.data-table th.c-title, .data-table td.c-title {{ width: 220px; font-weight: 600; color: var(--ink); }}
.data-table th.c-dir, .data-table td.c-dir {{ font-size: 13.5px; line-height: 1.75; }}
.data-table th.c-tag, .data-table td.c-tag {{ width: 110px; text-align: center; }}
.data-table th.c-dept, .data-table td.c-dept {{ width: 120px; font-size: 12.5px; color: var(--ink-muted); white-space: nowrap; }}

.badge-core {{
  display: inline-block;
  background: var(--seal);
  color: #fff;
  font-size: 10px;
  padding: 1px 6px;
  border-radius: 3px;
  font-weight: 700;
  margin-right: 6px;
  vertical-align: middle;
}}
.row-core {{
  background: rgba(197, 48, 48, 0.04);
}}
html[data-theme="dark"] .row-core {{
  background: rgba(255, 123, 114, 0.06);
}}

.pill {{
  display: inline-block;
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 12px;
  font-weight: 500;
}}
.pill-경제-도시 {{ background: var(--lake-light); color: var(--lake); }}
.pill-문화-복지 {{ background: var(--forest-light); color: var(--forest); }}
.pill-기획-재정 {{ background: var(--slate-light); color: var(--slate); }}
.pill-도시-건설 {{ background: var(--ember-light); color: var(--ember); }}
.pill-청년-교육 {{ background: var(--indigo-light); color: var(--indigo); }}
.pill-시책사업 {{ background: var(--olive-light); color: var(--olive); }}
.pill-복지 {{ background: var(--forest-light); color: var(--forest); }}
.pill-일반행정 {{ background: var(--slate-light); color: var(--slate); }}
.pill-도농상생 {{ background: var(--olive-light); color: var(--olive); }}

/* Toolbar & Filters */
.toolbar {{
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 1.2rem;
  flex-wrap: wrap;
}}
.toolbar-left {{
  display: flex;
  align-items: center;
  gap: 0.8rem;
  flex-wrap: wrap;
}}
.btn-filter {{
  background: var(--surface);
  border: 1px solid var(--line);
  color: var(--ink-soft);
  padding: 0.45rem 0.9rem;
  border-radius: 6px;
  font-size: 0.82rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s;
}}
.btn-filter:hover {{ border-color: var(--lake); color: var(--lake); }}
.btn-filter.active {{
  background: var(--seal);
  border-color: var(--seal);
  color: #fff;
}}
.filter-search-input {{
  background: var(--surface);
  border: 1px solid var(--line);
  color: var(--ink);
  padding: 0.45rem 0.85rem;
  border-radius: 6px;
  font-size: 0.84rem;
  font-family: var(--font-sans);
  width: 260px;
  transition: all 0.15s;
}}
.filter-search-input:focus {{
  outline: none;
  border-color: var(--lake);
  box-shadow: 0 0 0 2px var(--lake-light);
}}

.dept-chips {{
  display: flex;
  gap: 0.4rem;
  flex-wrap: wrap;
  margin-bottom: 1.4rem;
}}
.dept-chip {{
  background: var(--surface);
  border: 1px solid var(--line);
  color: var(--ink-soft);
  padding: 0.35rem 0.75rem;
  border-radius: 20px;
  font-size: 0.78rem;
  cursor: pointer;
  transition: all 0.15s;
  text-decoration: none;
}}
.dept-chip:hover {{
  border-color: var(--lake);
  color: var(--lake);
}}

/* Insights callout */
.insight-list {{
  padding-left: 20px;
  margin: 0;
}}
.insight-list li {{
  margin-bottom: 18px;
  font-size: 14.5px;
  line-height: 1.8;
  color: var(--ink-soft);
}}
.insight-list li b {{
  color: var(--ink);
}}
.insight-list .note {{
  display: block;
  font-size: 12px;
  color: var(--ink-muted);
  margin-top: 4px;
}}

.doc-foot {{
  margin-top: 3rem;
  padding: 1.6rem 2rem;
  background: var(--surface2);
  border-radius: 8px;
  font-size: 12.5px;
  color: var(--ink-muted);
  line-height: 1.8;
}}

/* Target highlight animation */
@keyframes pulseHighlight {{
  0% {{ background-color: rgba(240, 136, 62, 0.4); }}
  50% {{ background-color: rgba(240, 136, 62, 0.2); }}
  100% {{ background-color: transparent; }}
}}
.highlight-row {{
  animation: pulseHighlight 2.5s ease-out;
}}

/* ── Mobile Responsive ── */
@media(max-width: 900px) {{
  .site-header {{ padding: 0 1.2rem; }}
  .site-header .nav-links {{ display: none; }}
  .letterhead {{ padding: 0.4rem 1.4rem; font-size: 0.65rem; }}
  .hero {{ padding: 2.2rem 1.4rem 1.8rem; }}
  .hero__stats {{ width: 100%; }}
  .hero__stamp-wrap {{ justify-content: space-between; width: 100%; }}
  .tab-nav-container {{ padding: 0.5rem 1rem; }}
  
  .layout {{ flex-direction: column; }}
  .sidebar {{
    position: sticky;
    top: 96px;
    width: 100%;
    height: auto;
    padding: 0.8rem 1rem;
    z-index: 100;
  }}
  .brand {{ display: none; }}
  .sidebar-tabs {{ margin-bottom: 0.5rem; }}
  .toc {{
    display: flex;
    gap: 0.3rem;
    overflow-x: auto;
    padding-bottom: 0.3rem;
  }}
  .toc-group {{ margin: 0; flex-shrink: 0; }}
  .toc a {{ white-space: nowrap; border-radius: 20px; padding: 0.35rem 0.75rem; }}
  .sidebar-foot {{ display: none; }}
  
  .chapter {{ padding: 2.4rem 1.4rem; }}
  .core-grid {{ grid-template-columns: 1fr; }}
  .closing {{ padding: 3rem 1.4rem; }}
  .panel-wrap {{ padding: 2rem 1.4rem 4rem; }}
}}
</style>
</head>
<body>

<!-- ── Site Header ── -->
<header class="site-header">
  <div class="logo"><a href="/">최승환 · Jecheon</a></div>
  <nav class="nav-links">
    <a href="/">← 홈으로</a>
    <a href="/about.html">소개</a>
    <a href="/research.html">연구</a>
    <a href="/column.html">칼럼</a>
    <a href="/memo.html">정리노트</a>
    <a href="/local.html">제천 소개</a>
  </nav>
  <button id="theme-toggle" onclick="toggleTheme()" aria-label="테마 전환">☀ 라이트</button>
</header>

<div class="letterhead">
  <span>제천시 · 민선9기 공약백서 · 2026</span>
  <small>제9회 전국동시지방선거 당선인 공약 및 시책사업 종합 백서</small>
</div>

<!-- ── Hero ── -->
<header class="hero">
  <div class="hero__top">
    <div>
      <p class="hero__eyebrow">다시, 제천을 위해</p>
      <h1 class="hero__title">민선9기 제천시장<br>공약백서</h1>
      <p class="hero__desc">제9회 전국동시지방선거 이상천 당선인 공약사항 56건 및 시책사업 29건을 체계화한 종합 백서이다. 시민의 삶에서 체감되는 10대 핵심공약을 중심으로 6개 분과별 실행계획과 인수위원회 실무 검토의견을 담았다.</p>
    </div>
    <div class="hero__stamp-wrap">
      <div class="stamp">堤川<small>市長</small></div>
    </div>
  </div>
  <div class="hero__stats">
    <div class="stat"><strong>56</strong><span>공약사업</span></div>
    <div class="stat"><strong>29</strong><span>시책사업</span></div>
    <div class="stat"><strong>10</strong><span>핵심공약</span></div>
    <div class="stat"><strong>6</strong><span>분과위원회</span></div>
  </div>
</header>

<!-- ── Top Tab Bar ("민선 9기 탭") ── -->
<div class="tab-nav-wrapper">
  <div class="tab-nav-container">
    <nav class="tab-nav" role="tablist" aria-label="민선9기 백서 뷰 선택">
      <button class="tab-btn active" role="tab" id="btn-tab-whitepaper" aria-selected="true" onclick="switchMainTab('whitepaper')">
        <span>📖 공약백서 본문</span>
        <span class="tab-badge">8대 분야</span>
      </button>
      <button class="tab-btn" role="tab" id="btn-tab-pledges" aria-selected="false" onclick="switchMainTab('pledges')">
        <span>📋 공약사항 상세표</span>
        <span class="tab-badge">56건 전수</span>
      </button>
      <button class="tab-btn" role="tab" id="btn-tab-projects" aria-selected="false" onclick="switchMainTab('projects')">
        <span>📌 시책사업 현황</span>
        <span class="tab-badge">29건</span>
      </button>
      <button class="tab-btn" role="tab" id="btn-tab-insights" aria-selected="false" onclick="switchMainTab('insights')">
        <span>🏛️ 당선인 개요 &amp; 제언</span>
        <span class="tab-badge">인수위</span>
      </button>
    </nav>
  </div>
</div>

<!-- ── Layout: Sidebar + Main Content ── -->
<div class="layout">

  <!-- ── Sidebar ── -->
  <aside class="sidebar">
    <div class="brand">
      <span class="brand__eyebrow">제천시 · 민선9기</span>
      <span class="brand__title">공약백서<br>2026</span>
    </div>

    <div class="sidebar-tabs" role="tablist" aria-label="사이드바 뷰 전환">
      <button class="sb-tab active" id="sb-btn-whitepaper" onclick="switchMainTab('whitepaper')" title="공약백서 본문">본문</button>
      <button class="sb-tab" id="sb-btn-pledges" onclick="switchMainTab('pledges')" title="공약사항 상세표">공약</button>
      <button class="sb-tab" id="sb-btn-projects" onclick="switchMainTab('projects')" title="시책사업 현황">시책</button>
      <button class="sb-tab" id="sb-btn-insights" onclick="switchMainTab('insights')" title="당선인 개요 및 제언">제언</button>
    </div>

    <!-- TOC: Tab 1 (Whitepaper) -->
    <ul class="toc" id="toc-whitepaper">
      <li class="toc-group"><a href="#ch1" data-accent="lake" style="--accent:var(--lake);--accent-bg:var(--lake-light)"><em>01</em>공약 체계 개관</a></li>
      <li class="toc-group"><a href="#ch2" data-accent="lake" style="--accent:var(--lake);--accent-bg:var(--lake-light)"><em>02</em>경제·산업</a></li>
      <li class="toc-group"><a href="#ch3" data-accent="ember" style="--accent:var(--ember);--accent-bg:var(--ember-light)"><em>03</em>복지</a></li>
      <li class="toc-group"><a href="#ch4" data-accent="forest" style="--accent:var(--forest);--accent-bg:var(--forest-light)"><em>04</em>문화·관광</a></li>
      <li class="toc-group"><a href="#ch5" data-accent="slate" style="--accent:var(--slate);--accent-bg:var(--slate-light)"><em>05</em>도시·건설</a></li>
      <li class="toc-group"><a href="#ch6" data-accent="indigo" style="--accent:var(--indigo);--accent-bg:var(--indigo-light)"><em>06</em>청년·교육</a></li>
      <li class="toc-group"><a href="#ch7" data-accent="olive" style="--accent:var(--olive);--accent-bg:var(--olive-light)"><em>07</em>도농상생·마을</a></li>
      <li class="toc-group"><a href="#ch8" data-accent="lake" style="--accent:var(--lake-deep);--accent-bg:var(--slate-light)"><em>08</em>추진 체계</a></li>
      <li class="toc-group"><a href="#closing-sec" data-accent="lake" style="--accent:var(--lake-deep);--accent-bg:var(--slate-light)"><em>★</em>제천의 굽은 허리</a></li>
    </ul>

    <!-- TOC: Tab 2 (Pledges) -->
    <ul class="toc" id="toc-pledges" style="display:none;">
      <li class="toc-group"><a href="#dept-1"><em>III-1</em>기획재정 (4)</a></li>
      <li class="toc-group"><a href="#dept-2"><em>III-2</em>문화복지 (20)</a></li>
      <li class="toc-group"><a href="#dept-3"><em>III-3</em>경제산업 (11)</a></li>
      <li class="toc-group"><a href="#dept-4"><em>III-4</em>도시건설 (15)</a></li>
      <li class="toc-group"><a href="#dept-5"><em>III-5</em>청년위원회 (3)</a></li>
      <li class="toc-group"><a href="#dept-6"><em>III-6</em>여성위원회 (3)</a></li>
    </ul>

    <!-- TOC: Tab 3 (Projects) -->
    <ul class="toc" id="toc-projects" style="display:none;">
      <li class="toc-group"><a href="#projects"><em>IV</em>시책사업 (29건)</a></li>
    </ul>

    <!-- TOC: Tab 4 (Insights) -->
    <ul class="toc" id="toc-insights" style="display:none;">
      <li class="toc-group"><a href="#overview"><em>I</em>당선인 개요</a></li>
      <li class="toc-group"><a href="#summary"><em>II</em>공약사항 총괄 현황</a></li>
      <li class="toc-group"><a href="#insights"><em>V</em>종합 시사점 및 제언</a></li>
    </ul>

    <div class="sidebar-foot">
      본 백서는 제9회 지방선거 인수위원회 실무자료 및 공문용 당선인 공약사항을 토대로 체계화한 정책 문서입니다.<br>작성 · 2026. 6.
    </div>
  </aside>

  <!-- ── Main Panels ── -->
  <main class="main">

    <!-- ════════ PANEL 1: 공약백서 본문 ════════ -->
    <div id="panel-whitepaper" class="main-panel active">
{chapters_html}

      <footer class="closing" id="closing-sec">
{closing}
      </footer>
    </div>

    <!-- ════════ PANEL 2: 공약사항 상세표 (56건 전수) ════════ -->
    <div id="panel-pledges" class="main-panel">
      <div class="panel-wrap">
        <section class="block" id="detail">
          <div class="block-head"><span class="num">III.</span><h2>분과별 공약사항 상세 (56건)</h2></div>
          <p class="block-intro">인수위원회 실무 검토를 거친 6개 분과 56개 공약사업의 소관부서, 추진방향 및 주요 검토의견 전수 목록입니다.</p>

          <div class="toolbar">
            <div class="toolbar-left">
              <button id="toggleCore" class="btn-filter" onclick="toggleCoreOnly()">★ 핵심공약 10선만 보기</button>
              <button class="btn-filter" onclick="resetPledgeFilter()">전체 56건 보기</button>
            </div>
            <input type="text" id="pledgeSearchInput" class="filter-search-input" placeholder="공약명, 검토내용, 소관부서 검색..." oninput="filterPledges(this.value)">
          </div>

          <div class="dept-chips">
            <a class="dept-chip" onclick="jumpToDept('dept-1')">🏛️ 기획재정 (4)</a>
            <a class="dept-chip" onclick="jumpToDept('dept-2')">🎭 문화복지 (20)</a>
            <a class="dept-chip" onclick="jumpToDept('dept-3')">🏭 경제산업 (11)</a>
            <a class="dept-chip" onclick="jumpToDept('dept-4')">🏗️ 도시건설 (15)</a>
            <a class="dept-chip" onclick="jumpToDept('dept-5')">🌱 청년위원회 (3)</a>
            <a class="dept-chip" onclick="jumpToDept('dept-6')">🌸 여성위원회 (3)</a>
          </div>

{detail_content}
        </section>
      </div>
    </div>

    <!-- ════════ PANEL 3: 시책사업 현황 (29건 전수) ════════ -->
    <div id="panel-projects" class="main-panel">
      <div class="panel-wrap">
        <section class="block" id="projects">
          <div class="block-head"><span class="num">IV.</span><h2>시책사업 현황 (29건)</h2></div>
          <p class="block-intro">마을별 맞춤예산, 생활 인프라, 주민 편익 등 민선9기 시정에서 중점 관리할 29개 주요 시책사업 현황입니다.</p>

          <div class="toolbar">
            <input type="text" id="projectSearchInput" class="filter-search-input" placeholder="시책사업명, 관련부서 검색..." oninput="filterProjects(this.value)">
          </div>

          <div class="table-wrap">
{proj_table_enhanced}
          </div>
        </section>
      </div>
    </div>

    <!-- ════════ PANEL 4: 당선인 개요 & 인수위 제언 ════════ -->
    <div id="panel-insights" class="main-panel">
      <div class="panel-wrap">
        <section class="block" id="overview">
{overview_body}
        </section>

        <section class="block" id="summary">
{summary_body}
        </section>

        <section class="block" id="insights">
{insights_body}
        </section>

        <footer class="doc-foot">
          본 백서는 「민선9기 당선인 공약사항 정리(공문용)」 및 「민선9기 시책사업」 자료를 기초로 재구성한 실무 참고용 문서이며, 각 사업의 최종 추진 여부·규모·일정은 소관부서 검토 및 예산심의 결과에 따라 변경될 수 있습니다.
        </footer>
      </div>
    </div>

  </main>
</div>

<script>
// ── 테마 토글 (Site standard) ──
(function() {{
  var t = localStorage.getItem('choijc-theme') || 'dark';
  document.documentElement.setAttribute('data-theme', t);
  var btn = document.getElementById('theme-toggle');
  if (btn) btn.textContent = t === 'dark' ? '☀ 라이트' : '☾ 다크';
}})();

function toggleTheme() {{
  var html = document.documentElement;
  var now = html.getAttribute('data-theme');
  var next = now === 'dark' ? 'light' : 'dark';
  html.setAttribute('data-theme', next);
  localStorage.setItem('choijc-theme', next);
  var btn = document.getElementById('theme-toggle');
  if (btn) btn.textContent = next === 'dark' ? '☀ 라이트' : '☾ 다크';
}}

// ── 뷰 탭 전환 ──
const TABS = ['whitepaper', 'pledges', 'projects', 'insights'];

function switchMainTab(tabId, scrollToTop = true) {{
  if (!TABS.includes(tabId)) tabId = 'whitepaper';

  // Panel switch
  TABS.forEach(t => {{
    const panel = document.getElementById('panel-' + t);
    const btn = document.getElementById('btn-tab-' + t);
    const sbBtn = document.getElementById('sb-btn-' + t);
    const toc = document.getElementById('toc-' + t);

    const isActive = (t === tabId);
    if (panel) panel.classList.toggle('active', isActive);
    if (btn) {{
      btn.classList.toggle('active', isActive);
      btn.setAttribute('aria-selected', isActive ? 'true' : 'false');
    }}
    if (sbBtn) sbBtn.classList.toggle('active', isActive);
    if (toc) toc.style.display = isActive ? 'block' : 'none';
  }});

  // Update hash
  if (history.replaceState) {{
    history.replaceState(null, null, '#' + tabId);
  }}

  if (scrollToTop) {{
    const nav = document.querySelector('.tab-nav-wrapper');
    if (nav) nav.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
  }}
}}

// ── 핵심 공약 카드 클릭 -> 세부 표로 이동 ──
function jumpToPledge(pNo) {{
  switchMainTab('pledges', false);

  // If core filter was hiding it, reset core filter
  if (document.body.classList.contains('core-only')) {{
    toggleCoreOnly(false);
  }}

  const row = document.getElementById('pledge-' + pNo);
  if (row) {{
    setTimeout(() => {{
      row.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
      row.classList.add('highlight-row');
      setTimeout(() => row.classList.remove('highlight-row'), 2600);
    }}, 100);
  }}
}}

// ── 분과 세부 표로 바로 이동 ──
function jumpToDept(deptId) {{
  switchMainTab('pledges', false);
  const deptSec = document.getElementById(deptId);
  if (deptSec) {{
    setTimeout(() => {{
      deptSec.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
    }}, 100);
  }}
}}

// ── 핵심 공약 필터 ──
function toggleCoreOnly(forceState) {{
  const isCurrentlyOn = document.body.classList.contains('core-only');
  const next = (typeof forceState === 'boolean') ? forceState : !isCurrentlyOn;
  
  document.body.classList.toggle('core-only', next);
  const btn = document.getElementById('toggleCore');
  if (btn) {{
    btn.classList.toggle('active', next);
    btn.textContent = next ? '✓ 핵심공약만 보는 중 (10건)' : '★ 핵심공약 10선만 보기';
  }}
  
  document.querySelectorAll('.data-table tbody tr[data-core]').forEach(tr => {{
    if (next && tr.dataset.core === '0') {{
      tr.style.display = 'none';
    }} else {{
      tr.style.display = '';
    }}
  }});
}}

function resetPledgeFilter() {{
  toggleCoreOnly(false);
  const search = document.getElementById('pledgeSearchInput');
  if (search) {{
    search.value = '';
    filterPledges('');
  }}
}}

// ── 실시간 검색: 공약표 ──
function filterPledges(query) {{
  const q = (query || '').trim().toLowerCase();
  document.querySelectorAll('.data-table tbody tr[data-core]').forEach(tr => {{
    if (!q) {{
      if (document.body.classList.contains('core-only')) {{
        tr.style.display = (tr.dataset.core === '1') ? '' : 'none';
      }} else {{
        tr.style.display = '';
      }}
      return;
    }}
    const text = tr.innerText.toLowerCase();
    tr.style.display = text.includes(q) ? '' : 'none';
  }});
}}

// ── 실시간 검색: 시책사업표 ──
function filterProjects(query) {{
  const q = (query || '').trim().toLowerCase();
  document.querySelectorAll('#projects tbody tr[data-no]').forEach(tr => {{
    if (!q) {{
      tr.style.display = '';
      return;
    }}
    const text = tr.innerText.toLowerCase();
    tr.style.display = text.includes(q) ? '' : 'none';
  }});
}}

// ── Scrollspy for Tab 1 Chapters ──
const tocLinks = Array.from(document.querySelectorAll('#toc-whitepaper a'));
const chapterSections = tocLinks.map(l => document.querySelector(l.getAttribute('href'))).filter(Boolean);

if ('IntersectionObserver' in window && chapterSections.length) {{
  const spy = new IntersectionObserver((entries) => {{
    entries.forEach(entry => {{
      const id = '#' + entry.target.id;
      const link = tocLinks.find(l => l.getAttribute('href') === id);
      if (!link) return;
      if (entry.isIntersecting) {{
        tocLinks.forEach(l => l.classList.remove('is-active'));
        link.classList.add('is-active');
        const accent = entry.target.style.getPropertyValue('--accent');
        if (accent) link.style.setProperty('--accent', accent);
      }}
    }});
  }}, {{ rootMargin: '-30% 0px -55% 0px', threshold: 0 }});
  chapterSections.forEach(s => spy.observe(s));
}}

// ── Chapter Scroll-Reveal Animation ──
if ('IntersectionObserver' in window) {{
  const reveal = new IntersectionObserver((entries) => {{
    entries.forEach(entry => {{
      if (entry.isIntersecting) {{
        entry.target.classList.add('is-visible');
        reveal.unobserve(entry.target);
      }}
    }});
  }}, {{ threshold: 0.05 }});
  document.querySelectorAll('.chapter').forEach(c => reveal.observe(c));
}}

// ── Initial Tab check from URL hash ──
(function() {{
  const hash = window.location.hash.replace('#', '');
  if (['pledges', 'projects', 'insights', 'whitepaper'].includes(hash)) {{
    switchMainTab(hash, false);
  }} else if (hash.startsWith('dept-')) {{
    switchMainTab('pledges', false);
    setTimeout(() => jumpToDept(hash), 200);
  }} else if (hash.startsWith('pledge-')) {{
    const pNo = hash.replace('pledge-', '');
    jumpToPledge(pNo);
  }} else if (hash.startsWith('ch')) {{
    switchMainTab('whitepaper', false);
  }}
}})();
</script>
<script src="https://cdn.jsdelivr.net/npm/motion@13.4.6/dist/motion.js" defer></script>
<script src="/js/motion.js" defer></script>
</body>
</html>
'''

with open('jecheon_9th_policy_whitepaper.html', 'w', encoding='utf-8') as f:
    f.write(full_html)

print('Successfully generated clean jecheon_9th_policy_whitepaper.html!')
print('Total characters:', len(full_html))
print('Total lines:', len(full_html.splitlines()))
