# retire_notes.json(퇴직 준비 자료)과 기본정보로 퇴직이후 탭 retire.html을 만든다. 금액은 페이지에 넣지 않는다
import html, json
from datetime import date
from pathlib import Path
from build_practice import head, foot, SITE

BASE = Path(__file__).resolve().parent
BIRTH = (1979, 11)   # 출생 연월
HIRED = (2007, 1)    # 임용 연월


def start_age(year):  # 공무원연금법 부칙 제11조, 1996년 이후 임용자
    return 60 if year <= 2021 else 61 if year <= 2023 else 62 if year <= 2026 else 63 if year <= 2029 else 64 if year <= 2032 else 65


def basics():
    ry, rm = BIRTH[0] + 60, 6 if BIRTH[1] <= 6 else 12
    age = start_age(ry)
    sy, sm = BIRTH[0] + age, BIRTH[1]
    serve = ry * 12 + rm - (HIRED[0] * 12 + HIRED[1]) + 1
    gap = sy * 12 + sm - (ry * 12 + rm) - 1
    t = date.today()
    left = ry * 12 + rm - (t.year * 12 + t.month)
    return [("임용", f"{HIRED[0]}년 {HIRED[1]}월"), ("정년퇴직", f"{ry}년 {rm}월 (만 60세)"),
            ("정년까지", f"{left // 12}년 {left % 12}개월"), ("정년 때 재직기간", f"{serve // 12}년 {serve % 12}개월"),
            ("연금 개시", f"{sy}년 {sm}월 ({age}세)"), ("소득 공백", f"{gap // 12}년 {gap % 12}개월")], gap, age


def e(s):
    return html.escape(str(s))


def note_html(n):
    title = e(n["title"])
    if n.get("url"):
        title = f'<a href="{e(n["url"])}" target="_blank" rel="noopener">{title}</a>'
    return (f'<li class="rt-note-item"><div class="rt-meta">{e(n["date"])} · {e(n["tag"])}</div>'
            f'<h3>{title}</h3><p>{e(n["summary"])}</p></li>')


def build():
    rows, gap, age = basics()
    notes = sorted(json.loads((BASE / "retire_notes.json").read_text("utf-8")), key=lambda n: n["date"], reverse=True)
    info = "".join(f'<div class="rt-stat"><b>{e(v)}</b><span>{e(k)}</span></div>' for k, v in rows)
    items = "".join(note_html(n) for n in notes) or '<li class="rt-note-item">아직 올린 자료가 없습니다.</li>'

    css = """<style>
.rt-wrap{max-width:860px;margin:0 auto;padding:32px 16px 80px}
.rt-wrap h1{font-family:var(--font-display);font-size:clamp(1.6rem,4vw,2.2rem);margin:.2em 0 .3em}
.rt-lead,.rt-small{color:var(--muted);line-height:1.7}
.rt-small{font-size:.85rem}
.rt-card{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:20px;margin:18px 0}
.rt-card h2{font-family:var(--font-display);font-size:1.15rem;margin:0 0 12px}
.rt-stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:12px}
.rt-stat{border-left:3px solid var(--accent);padding:4px 0 4px 12px}
.rt-stat b{display:block;font-family:var(--font-mono);font-size:1.15rem}
.rt-stat span{font-size:.85rem;color:var(--muted)}
.rt-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:12px;margin-bottom:16px}
.rt-grid label{display:flex;flex-direction:column;gap:4px;font-size:.88rem;color:var(--muted)}
.rt-grid input{font:inherit;font-family:var(--font-mono);background:var(--bg);color:var(--text);border:1px solid var(--border);border-radius:8px;padding:8px 10px}
.rt-notes{list-style:none;padding:0;margin:0}
.rt-note-item{border-top:1px solid var(--border);padding:14px 0}
.rt-note-item:first-child{border-top:0;padding-top:0}
.rt-note-item h3{font-size:1.02rem;margin:4px 0}
.rt-note-item a{color:var(--accent)}
.rt-note-item p{margin:0;line-height:1.7}
.rt-meta{font-family:var(--font-mono);font-size:.78rem;color:var(--muted)}
</style>"""

    body = f"""
<main class="rt-wrap">
  <p class="rt-small">LOUNGE · 퇴직이후</p>
  <h1>퇴직 이후를 준비하는 방</h1>
  <p class="rt-lead">정년과 연금 개시까지의 기본 일정, 간단한 계산, 모아 둔 자료를 둡니다.</p>

  <section class="rt-card">
    <h2>기본정보</h2>
    <div class="rt-stats">{info}</div>
    <p class="rt-small">정년은 만 60세가 되는 해의 6월 말 또는 12월 말이고, 연금 개시 연령은 퇴직한 해로 정해집니다(공무원연금법 부칙 제11조).</p>
  </section>

  <section class="rt-card">
    <h2>간단 계산</h2>
    <div class="rt-grid">
      <label>연금 월액(세후, 만 원)<input id="pension" type="number" inputmode="numeric"></label>
      <label>일시금으로 받을 때 총액(만 원)<input id="lump" type="number" inputmode="numeric"></label>
      <label>퇴직수당(만 원)<input id="allowance" type="number" inputmode="numeric"></label>
      <label>한 달 생활비(만 원)<input id="living" type="number" inputmode="numeric"></label>
    </div>
    <div class="rt-stats">
      <div class="rt-stat"><b id="o-gap">-</b><span>공백기 생활비 합계</span></div>
      <div class="rt-stat"><b id="o-month">-</b><span>연금 받을 때 매달 남는 돈</span></div>
      <div class="rt-stat"><b id="o-even">-</b><span>연금이 일시금을 넘는 나이</span></div>
    </div>
    <p class="rt-small">넣은 숫자는 이 브라우저에만 저장됩니다. 퇴직수당은 연금을 골라도 한 번에 받으므로 손익분기에서 뺍니다. 연금의 물가 연동은 넣지 않았습니다.</p>
  </section>

  <section class="rt-card">
    <h2>자료</h2>
    <ul class="rt-notes">{items}</ul>
  </section>
</main>

<script>
(function () {{
  var KEY = "retire-plan", F = ["pension", "lump", "allowance", "living"], GAP = {gap}, AGE = {age};
  var d = {{}};
  try {{ d = JSON.parse(localStorage.getItem(KEY)) || {{}}; }} catch (_) {{}}
  var $ = function (id) {{ return document.getElementById(id); }};
  var man = function (n) {{ return Math.round(n).toLocaleString("ko-KR") + "만 원"; }};
  function calc() {{
    var n = function (k) {{ return +d[k] || 0; }};
    $("o-gap").textContent = n("living") ? man(n("living") * GAP) : "-";
    $("o-month").textContent = n("living") && n("pension") ? man(n("pension") - n("living")) : "-";
    var diff = n("lump") - n("allowance");
    $("o-even").textContent = n("pension") && diff > 0 ? Math.floor(AGE + diff / n("pension") / 12) + "세" : "-";
  }}
  F.forEach(function (k) {{
    $(k).value = d[k] || "";
    $(k).addEventListener("input", function (e) {{
      d[k] = e.target.value;
      try {{ localStorage.setItem(KEY, JSON.stringify(d)); }} catch (_) {{}}
      calc();
    }});
  }});
  calc();
}})();
</script>
"""
    desc = "정년·연금 개시 일정과 소득 공백, 연금과 일시금 손익분기를 간단히 계산하고 퇴직 준비 자료를 모아 두는 페이지"
    page = head("퇴직 이후 준비 | 최승환", desc, f"{SITE}/retire.html", "website").replace("</head>", css + "\n</head>") + body + foot()
    page = page.replace("<!DOCTYPE html>", "<!DOCTYPE html>\n<!-- 퇴직이후 탭: build_retire.py가 retire_notes.json으로 생성. 직접 고치지 않는다 -->", 1)
    page = page.replace("최승환 · 가이드", "최승환 · 라운지").replace('<a href="/guides.html" aria-current="page">', '<a href="/guides.html">')
    (BASE / "retire.html").write_text(page, "utf-8")
    return len(notes)


if __name__ == "__main__":
    print(f"retire.html 생성, 자료 {build()}건")
