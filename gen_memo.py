import os, re, datetime

BASE = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE)

def read_md(filename):
    p = os.path.join(BASE, filename)
    if not os.path.exists(p): return ""
    with open(p, encoding="utf-8") as f: return f.read()

def md_to_html_items(md_text):
    marker = "<!-- 새 항목은 아래에 추가됩니다 -->"
    content = md_text.split(marker, 1)[1].strip() if marker in md_text else md_text.strip()
    if not content:
        return "<p class='empty'>아직 기록이 없습니다.</p>"
    items, current_date, current_text = [], "", []
    for line in content.splitlines():
        line = line.strip()
        if not line:
            if current_text:
                items.append((current_date, " ".join(current_text)))
                current_text = []
            continue
        date_match = re.match(r'^#{1,4}\s*(\d{4}[.\-/]\d{2}[.\-/]\d{2})', line)
        if date_match:
            if current_text:
                items.append((current_date, " ".join(current_text)))
                current_text = []
            current_date = date_match.group(1)
        elif line.startswith("- ") or line.startswith("* "):
            if current_text:
                items.append((current_date, " ".join(current_text)))
                current_text = []
            current_text = [line[2:]]
        else:
            current_text.append(line.lstrip("#").strip())
    if current_text:
        items.append((current_date, " ".join(current_text)))
    if not items:
        return "<p class='empty'>아직 기록이 없습니다.</p>"
    html = ""
    for date, text in reversed(items[-30:]):
        text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
        date_span = "<span class='date'>" + date + "</span>" if date else ""
        html += "\n        <div class='memo-item'>" + date_span + "<span class='text'>" + text + "</span></div>"
    return html

now = datetime.datetime.now().strftime("%Y년 %m월 %d일 %H:%M")
ideas = md_to_html_items(read_md("💡 아이디어·기획.md"))
goals = md_to_html_items(read_md("🎯 목표·계획·다짐.md"))
diary = md_to_html_items(read_md("📖 일상·감정·회고.md"))
work  = md_to_html_items(read_md("📚 업무·논문·공부.md"))

html = """<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>정리노트 | 최승환</title>
<style>
  :root {
    --bg:#0d1117; --surface:#161b22; --border:#30363d;
    --text:#e6edf3; --muted:#8b949e; --accent:#58a6ff;
    --green:#3fb950; --orange:#d29922; --purple:#bc8cff;
  }
  *{box-sizing:border-box;margin:0;padding:0;}
  body{background:var(--bg);color:var(--text);font-family:'Segoe UI',sans-serif;line-height:1.7;padding:2rem 1rem;}
  .container{max-width:900px;margin:0 auto;}
  header{text-align:center;margin-bottom:3rem;padding-bottom:2rem;border-bottom:1px solid var(--border);}
  header h1{font-size:1.8rem;font-weight:700;margin-bottom:0.4rem;}
  header p{color:var(--muted);font-size:0.9rem;}
  .grid{display:grid;grid-template-columns:1fr 1fr;gap:1.5rem;}
  @media(max-width:640px){.grid{grid-template-columns:1fr;}}
  .card{background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:1.5rem;}
  .card-title{font-size:1.1rem;font-weight:700;margin-bottom:1rem;}
  .card.ideas .card-title{color:var(--orange);}
  .card.goals .card-title{color:var(--green);}
  .card.diary .card-title{color:var(--purple);}
  .card.work  .card-title{color:var(--accent);}
  .memo-item{padding:0.6rem 0;border-bottom:1px solid var(--border);}
  .memo-item:last-child{border-bottom:none;}
  .date{display:inline-block;font-size:0.75rem;color:var(--muted);background:rgba(139,148,158,0.1);padding:0.1rem 0.5rem;border-radius:20px;margin-right:0.5rem;}
  .text{font-size:0.92rem;}
  .empty{color:var(--muted);font-size:0.9rem;font-style:italic;}
  footer{text-align:center;margin-top:3rem;padding-top:2rem;border-top:1px solid var(--border);color:var(--muted);font-size:0.82rem;}
  a{color:var(--accent);text-decoration:none;}
</style>
</head>
<body>
<div class="container">
  <header>
    <h1>📋 나를 정리하는 프로젝트</h1>
    <p>최승환 · 지방행정 연구자 · 제천시청 팀장 &nbsp;|&nbsp; 마지막 업데이트: """ + now + """</p>
    <p style="margin-top:0.5rem"><a href="/">← 홈으로</a></p>
  </header>
  <div class="grid">
    <div class="card ideas">
      <div class="card-title">💡 아이디어 · 기획</div>""" + ideas + """
    </div>
    <div class="card goals">
      <div class="card-title">🎯 목표 · 계획 · 다짐</div>""" + goals + """
    </div>
    <div class="card diary">
      <div class="card-title">📖 일상 · 감정 · 회고</div>""" + diary + """
    </div>
    <div class="card work">
      <div class="card-title">📚 업무 · 논문 · 공부</div>""" + work + """
    </div>
  </div>
  <footer>
    <p>Claude와 함께 정리하는 나의 기록 &nbsp;·&nbsp; <a href="https://choijc79.github.io">choijc79.github.io</a></p>
  </footer>
</div>
</body>
</html>"""

out = os.path.join(BASE, "memo_fixed.html")
with open(out, "w", encoding="utf-8") as f:
    f.write(html)
print(f"완료: {out}")
print(f"크기: {len(html):,} bytes")
