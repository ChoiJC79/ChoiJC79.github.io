#!/usr/bin/env python3
# 칼럼·AI 가이드 추가, 지식·의회·민선9기 자동 갱신 실행, 퇴직이후 탭 자료 추가를 맡는 사이트 전용 MCP 서버(stdio)
"""
실행:  python3 site_mcp.py            # MCP 서버(stdio)
검사:  python3 site_mcp.py --selftest # 임시 사본에서 칼럼·가이드 추가를 시험(push 없음)
추가:  python3 site_mcp.py --add column|guide 초안.json  # 스킬에서 호출, 바로 배포
"""

import html, re, shutil, subprocess, sys, tempfile
from pathlib import Path

BASE = Path(__file__).resolve().parent
SITE = "https://choijc79.github.io"
COL_MD = "💬 칼럼·기고.md"
GUIDE_MD = "💬 AI가이드.md"
TYPE_COLOR = {"life": "#9870C8", "policy": "#58a6ff"}
CO_AUTHOR = "\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"


# ─── 공통 ────────────────────────────────────────────────────

def run(cmd, cwd):
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError(f"{' '.join(cmd)} 실패\n{p.stdout[-1500:]}\n{p.stderr[-1500:]}")
    return p.stdout


def read(base, name):
    return (base / name).read_text(encoding="utf-8")


def write(base, name, text):
    (base / name).write_text(text, encoding="utf-8")


def git_sync(base):
    run(["git", "pull", "--rebase", "--autostash"], base)


def commit_push(base, paths, message):
    run(["git", "add", "--", *paths], base)
    if not run(["git", "diff", "--cached", "--name-only"], base).strip():
        return "바뀐 파일이 없어 커밋하지 않았습니다."
    run(["git", "commit", "-m", message + CO_AUTHOR], base)
    run(["git", "push"], base)
    return "커밋하고 push했습니다. GitHub Pages 반영까지 1~2분 걸립니다."


def add_sitemap(base, path, date, freq, prio):
    sm = read(base, "sitemap.xml")
    loc = f"{SITE}/{path}"
    if loc in sm:
        return
    entry = (f"  <url>\n    <loc>{loc}</loc>\n    <lastmod>{date}</lastmod>\n"
             f"    <changefreq>{freq}</changefreq>\n    <priority>{prio}</priority>\n  </url>\n")
    write(base, "sitemap.xml", sm.replace("</urlset>", entry + "</urlset>", 1))


def check_date(date):
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", date):
        raise ValueError("date는 YYYY-MM-DD 형식이어야 합니다.")


# ─── 칼럼 ────────────────────────────────────────────────────

def column_rows(c):
    return re.findall(r"<li class=\"idx-row\"[^>]*/columns/([^']+)\.html'.*?idx-date\">([^<]*)<.*?idx-title\">([^<]*)<", c)


def insert_sorted(block, items_re, new_item, new_date, date_re):
    """block 안의 items_re 항목 중 날짜가 new_date보다 이른 첫 항목 앞에 넣는다(목록은 최신순)."""
    for m in re.finditer(items_re, block, re.S):
        if re.search(date_re, m.group(0)).group(1) < new_date:
            return block[:m.start()] + new_item + "\n" + block[m.start():]
    last = list(re.finditer(items_re, block, re.S))[-1]
    return block[:last.end()] + "\n" + new_item + block[last.end():]


def renumber_cards(block):
    i = 0
    def one(m):
        nonlocal i
        a = m.group(0)
        num = str(i + 1).zfill(2)
        cls = "col-item col-item-rev" if i % 2 else "col-item"
        a = re.sub(r'class="col-item[^"]*"', f'class="{cls}"', a, count=1)
        a = re.sub(r'(col-visual-num">)\d+', rf"\g<1>{num}", a)
        a = re.sub(r'(class="col-num">)\d+', rf"\g<1>{num}", a)
        i += 1
        return a
    return re.sub(r"<article class=\"col-item.*?</article>", one, block, flags=re.S)


def excerpt_of(body, n=60):
    text = re.sub(r"[#>*_`\[\]]|\(http[^)]*\)", "", body)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:n] + "…" if len(text) > n else text


def add_column_core(base, title, date, tags, body, type, image, deploy):
    check_date(date)
    if type not in TYPE_COLOR:
        raise ValueError("type은 policy(행정·정책, A면) 또는 life(삶의 기록, B면)입니다.")
    tag_list = [t.strip() for t in tags.split("·") if t.strip()]
    if not tag_list or not body.strip() or not title.strip():
        raise ValueError("title·tags·body는 비울 수 없습니다.")
    tags = "·".join(tag_list)
    slug = re.sub(r"[^\w]", "", date + title)[:22]

    if deploy:
        git_sync(base)
    c = read(base, "column.html")
    if f"/columns/{slug}.html" in c:
        raise ValueError(f"이미 같은 슬러그({slug})의 칼럼이 있습니다.")

    # 이미지: 로컬 파일이면 img/로 복사, /img/...면 그대로 사용
    paths = [COL_MD, "column.html", "sitemap.xml", "columns"]
    if image.startswith("/img/"):
        if not (base / image.lstrip("/")).exists():
            raise ValueError(f"{image} 파일이 저장소에 없습니다.")
        img_url = image
    else:
        src = Path(image).expanduser()
        if not src.is_file():
            raise ValueError("image는 Mac의 이미지 파일 경로 또는 /img/... 경로여야 합니다.")
        dest = f"img/col_{slug}{src.suffix.lower()}"
        shutil.copyfile(src, base / dest)
        img_url, paths = "/" + dest, paths + [dest]

    # 1) 원본 md
    md = read(base, COL_MD).rstrip("\n") + "\n"
    write(base, COL_MD, md + f"\n## {title} | {date} | {tags}\n\n{body.strip()}\n\n---\n")

    # 2) column.html 목차·태그·개수·카드
    t_txt, t_attr = html.escape(title, quote=False), html.escape(title)
    row = (f'<li class="idx-row" data-type="{type}" onclick="location.href=\'/columns/{slug}.html\'" '
           f'data-tag="{tags}"><span class="idx-date">{date}</span><span class="idx-title">{t_txt}</span>'
           f'<span class="idx-tags">{"".join(f"<span class=\"idx-tag\">{t}</span>" for t in tag_list)}</span></li>')
    same = re.search(rf'col-cat" style="color:(#\w+)">/ {re.escape(tag_list[0])}<', c)
    color = same.group(1) if same else TYPE_COLOR[type]
    card = (f'<article class="col-item" data-tag="{tags}" data-type="{type}" data-slug="{slug}">'
            f'<div class="col-visual"><img src="{img_url}" alt="{t_attr}" loading="lazy">'
            f'<div class="col-visual-overlay"><span class="col-visual-num">00</span></div></div>'
            f'<div class="col-text"><div class="col-num-row"><span class="col-num">00</span>'
            f'<span class="col-cat" style="color:{color}">/ {tag_list[0]}</span></div>'
            f'<h2 class="col-title">{t_txt}</h2><p class="col-excerpt">{html.escape(excerpt_of(body), quote=False)}</p>'
            f'<div class="col-meta-row"><span class="col-date">{date}</span>'
            f'<span class="col-tag-chip" style="color:{color};border-color:{color}44;background:{color}11">'
            f'{" · ".join(tag_list)}</span></div>'
            f'<a class="col-more" href="/columns/{slug}.html">전문 읽기 →</a></div></article>')

    def section(text, name, fn):
        a, b = text.index(f"<!--AUTO:{name}-->"), text.index(f"<!--/AUTO:{name}-->")
        return text[:a] + fn(text[a:b]) + text[b:]

    c = section(c, "INDEX", lambda s: insert_sorted(
        s, r'<li class="idx-row".*?</li>', row, date, r'idx-date">([^<]*)<'))
    c = section(c, "CARDS", lambda s: renumber_cards(insert_sorted(
        s, r'<article class="col-item.*?</article>', card, date, r'col-date">([^<]*)<')))
    def add_tags(s):
        new = "".join(f"<button class=\"tag-btn\" onclick=\"filterCol(this,'{t}')\">{t}</button>"
                      for t in tag_list if f"filterCol(this,'{t}')" not in s)
        k = s.rindex("</button>") + len("</button>")
        return s[:k] + new + s[k:]
    c = section(c, "TAGS", add_tags)
    c = re.sub(r'(idx-count">)\d+', rf"\g<1>{len(column_rows(c))}", c, count=1)
    write(base, "column.html", c)

    # 3) sitemap·개별 페이지
    add_sitemap(base, f"columns/{slug}.html", date, "yearly", "0.6")
    run([sys.executable, "build_columns.py"], base)
    if not (base / "columns" / f"{slug}.html").exists():
        raise RuntimeError("build_columns.py가 새 칼럼 페이지를 만들지 못했습니다. 제목·날짜가 md와 column.html에서 같은지 확인하세요.")

    url = f"{SITE}/columns/{slug}.html"
    if not deploy:
        return url
    return commit_push(base, paths, f"칼럼 '{title}' 발행") + f"\n{url}"


# ─── AI 가이드 ───────────────────────────────────────────────

def add_guide_core(base, title, date, tags, slug, repo, minutes, steps, sections, excerpt, body, deploy):
    check_date(date)
    if not re.fullmatch(r"[a-z0-9-]+", slug):
        raise ValueError("slug는 영어 소문자·숫자·하이픈만 씁니다. 예: claude-and-markitdown")
    if deploy:
        git_sync(base)
    md = read(base, GUIDE_MD)
    if re.search(rf"^slug: *{re.escape(slug)}\s*$", md, re.M):
        raise ValueError(f"slug {slug}는 이미 있습니다.")
    if re.search(rf"^repo: *{re.escape(repo)}\s*$", md, re.M):
        raise ValueError(f"{repo}는 이미 다룬 저장소입니다.")
    block = (f"\n## {title} | {date} | {tags}\nslug: {slug}\nrepo: {repo}\nminutes: {minutes}\n"
             f"steps: {steps}\nsections: {sections}\nexcerpt: {excerpt}\n\n{body.strip()}\n\n---\n")
    write(base, GUIDE_MD, md.rstrip("\n") + "\n" + block)
    add_sitemap(base, f"guides/{slug}.html", date, "monthly", "0.7")
    run([sys.executable, "build_guides.py"], base)
    if not (base / "guides" / f"{slug}.html").exists():
        raise RuntimeError("build_guides.py가 새 가이드 페이지를 만들지 못했습니다.")
    url = f"{SITE}/guides/{slug}.html"
    if not deploy:
        return url
    return commit_push(base, [GUIDE_MD, "guides.html", "guides", "sitemap.xml"],
                       f"이번 주 AI 가이드: {title}") + f"\n{url}"


# ─── 자동 갱신 작업(지식·의회·민선9기) ─────────────────────────

H = Path.home()
JOBS = {  # 이름: (스크립트, 인자, 로그)
    "jisik": (H / "jisik-auto/update.py", ["--force"], H / "jisik-auto/logs/update.log"),
    "badq": (H / "badq-auto/update.py", ["--force"], H / "badq-auto/logs/update.log"),
    "lsc": (H / "lsc-auto/update.py", ["--force"], H / "lsc-auto/logs/update.log"),
    "council": (H / "council-auto/work/scripts/daily_council_sync.py", [], H / "council-auto/work/logs/daily_sync.log"),
}
JOB_PATH = f"{H}/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"


def job_running(name):
    return subprocess.run(["pgrep", "-f", str(JOBS[name][0])], capture_output=True).returncode == 0


def start_job(name):
    """작업을 백그라운드로 띄운다. 요약에 수십 분 걸리므로 기다리지 않는다."""
    if name not in JOBS:
        raise ValueError(f"작업 이름은 {', '.join(JOBS)} 중 하나")
    script, args, log = JOBS[name]
    if job_running(name):
        return f"{name}은 이미 실행 중입니다. update_log로 진행을 확인하세요."
    import os
    out = open(H / f"{script.parent.name}-mcp.out", "a")
    subprocess.Popen([sys.executable, str(script), *args], cwd=script.parent, stdout=out, stderr=out,
                     env={**os.environ, "PATH": JOB_PATH}, start_new_session=True)
    return f"{name} 갱신을 시작했습니다. 끝나면 스크립트가 직접 커밋·push합니다. 로그: {log}"


def tail_log(name, lines=30):
    log = JOBS[name][2]
    state = "실행 중" if job_running(name) else "쉬는 중"
    text = log.read_text("utf-8", "replace").splitlines()[-lines:] if log.exists() else ["로그 없음"]
    return f"[{name} · {state}]\n" + "\n".join(text)


# ─── 퇴직이후 탭 자료 ────────────────────────────────────────

def add_retire_note_core(base, title, date, tag, summary, url="", deploy=True):
    import json
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", date):
        raise ValueError("date는 YYYY-MM-DD")
    if deploy:
        git_sync(base)
    p = base / "retire_notes.json"
    notes = json.loads(p.read_text("utf-8"))
    if any(n["title"] == title for n in notes):
        raise ValueError(f"같은 제목의 자료가 이미 있습니다: {title}")
    notes.append({k: v for k, v in dict(date=date, tag=tag, title=title, summary=summary, url=url).items() if v})
    p.write_text(json.dumps(notes, ensure_ascii=False, indent=2) + "\n", "utf-8")
    run([sys.executable, "build_retire.py"], base)
    if not deploy:
        return "ok"
    return commit_push(base, ["retire_notes.json", "retire.html"], f"퇴직이후 자료 추가: {title}") + f"\n{SITE}/retire.html"

# ─── MCP 도구 ────────────────────────────────────────────────

def serve():
    from mcp.server.fastmcp import FastMCP
    mcp = FastMCP("jc-site")

    @mcp.tool()
    def site_status() -> str:
        """사이트 저장소의 커밋 안 된 변경과 최근 커밋 5개를 보여준다."""
        return ("[변경]\n" + (run(["git", "status", "--short"], BASE) or "없음\n")
                + "[최근 커밋]\n" + run(["git", "log", "-5", "--format=%h %ad %s", "--date=short"], BASE))

    @mcp.tool()
    def list_columns(limit: int = 15) -> str:
        """최신순 칼럼 목록(날짜·제목·슬러그)."""
        rows = column_rows(read(BASE, "column.html"))[:limit]
        return "\n".join(f"{d} {html.unescape(t)} ({s})" for s, d, t in rows)

    @mcp.tool()
    def add_column(title: str, date: str, tags: str, body: str, type: str, image: str) -> str:
        """칼럼을 추가하고 바로 배포한다(md 추가 → column.html 갱신 → columns/ 생성 → sitemap → 커밋·push).
        운영자가 채팅에서 본문을 승인한 뒤에만 호출한다.
        date: YYYY-MM-DD. tags: 가운뎃점(·) 구분, 예 '에세이·일상'. body: 마크다운 본문(제목 줄 제외).
        type: 'policy'(행정·정책, A면) 또는 'life'(삶의 기록, B면).
        image: Mac의 이미지 파일 절대경로(img/로 복사됨) 또는 저장소의 기존 '/img/파일명'."""
        return add_column_core(BASE, title, date, tags, body, type, image, deploy=True)

    @mcp.tool()
    def add_guide(title: str, date: str, tags: str, slug: str, repo: str, minutes: int,
                  steps: int, sections: int, excerpt: str, body: str) -> str:
        """주간 AI 가이드를 추가하고 바로 배포한다(💬 AI가이드.md → build_guides.py → sitemap → 커밋·push).
        운영자가 초안을 승인한 뒤에만 호출한다. slug 예: claude-and-markitdown, repo 예: owner/repo.
        body에는 복사 프롬프트, Quick Start, STEP, 자주 막히는 곳, 솔직히 한계, 공식 자료가 들어가야 한다."""
        return add_guide_core(BASE, title, date, tags, slug, repo, minutes, steps, sections, excerpt, body, deploy=True)

    @mcp.tool()
    def publish(message: str) -> str:
        """모든 빌드 스크립트(칼럼·가이드·실무 가이드)를 다시 돌린 뒤, 추적 중인 파일 변경과
        columns/·guides/·practice/·img/의 새 파일을 커밋·push한다. 직접 고친 내용을 배포할 때 쓴다."""
        git_sync(BASE)
        for s in ("build_columns.py", "build_guides.py", "build_practice.py"):
            run([sys.executable, s], BASE)
        run(["git", "add", "-u"], BASE)
        return commit_push(BASE, ["columns", "guides", "practice", "img"], message)

    @mcp.tool()
    def run_update(job: str) -> str:
        """자동 갱신 작업을 지금 바로 돌린다(주기 무시). job: 'jisik'(지식인사이드), 'badq'(나쁜질문),
        'lsc'(민선9기), 'council'(제천시의회 회의 분석). 백그라운드로 돌고 끝나면 스스로 push한다."""
        return start_job(job)

    @mcp.tool()
    def update_log(job: str, lines: int = 30) -> str:
        """자동 갱신 작업의 실행 여부와 로그 끝부분. job은 run_update와 같다."""
        return tail_log(job, lines)

    @mcp.tool()
    def add_retire_note(title: str, date: str, tag: str, summary: str, url: str = "") -> str:
        """퇴직이후 탭(retire.html) 자료 목록에 한 건을 추가하고 배포한다(retire_notes.json → build_retire.py → 커밋·push).
        date: YYYY-MM-DD. tag 예: 연금·건강보험·세금·재취업·생활. summary: 2~3문장 요약. url: 원문 주소(선택).
        개인 금액(연금액·퇴직금)은 공개 사이트라 넣지 않는다."""
        return add_retire_note_core(BASE, title, date, tag, summary, url)

    mcp.run()


# ─── 자체 검사 ───────────────────────────────────────────────

def selftest():
    with tempfile.TemporaryDirectory() as tmp:
        # 필요한 파일만 복사한다. 저장소가 iCloud 데스크탑에 있어 통째로 복사하면 사진을 전부 내려받는다.
        base = Path(tmp) / "site"
        for d in ("columns", "guides"):
            shutil.copytree(BASE / d, base / d)
        for f in ("column.html", "guides.html", "sitemap.xml", COL_MD, GUIDE_MD, "build_columns.py", "build_guides.py"):
            shutil.copy(BASE / f, base / f)
        (base / "img").mkdir()
        (base / "img" / "col_family.jpg").touch()
        before = column_rows(read(base, "column.html"))
        add_column_core(base, "시험 칼럼 '제목'", "2099-01-01", "에세이·시험태그",
                        "첫 문단입니다. **굵게** 쓴 글.\n\n둘째 문단.", "life", "/img/col_family.jpg", deploy=False)
        c = read(base, "column.html")
        rows = column_rows(c)
        slug = re.sub(r"[^\w]", "", "2099-01-01시험 칼럼 '제목'")[:22]
        assert rows[0][0] == slug and len(rows) == len(before) + 1
        nums = re.findall(r'col-visual-num">(\d+)', c)
        assert nums == [str(i).zfill(2) for i in range(1, len(nums) + 1)], nums
        assert f'idx-count">{len(rows)}<' in c
        assert "filterCol(this,'시험태그')" in c and c.count("filterCol(this,'에세이')") == 1
        assert (base / "columns" / f"{slug}.html").exists()
        assert f"columns/{slug}.html" in read(base, "sitemap.xml")

        # 과거 날짜는 목록 중간에 들어가야 한다
        add_column_core(base, "중간 날짜 시험", "2026-10-01", "행정혁신", "본문.", "policy", "/img/col_family.jpg", deploy=False)
        dates = [d for _, d, _ in column_rows(read(base, "column.html"))]
        assert dates == sorted(dates, reverse=True), dates[:5]

        try:
            add_column_core(base, "시험 칼럼 '제목'", "2099-01-01", "에세이", "x", "life", "/img/col_family.jpg", deploy=False)
            raise AssertionError("중복 슬러그가 통과됨")
        except ValueError:
            pass

        add_guide_core(base, "시험 가이드", "2099-01-01", "시험", "claude-and-selftest", "test/selftest",
                       10, 3, 5, "시험 요약", "## STEP 1. 설치\n\n```bash\necho hi\n```", deploy=False)
        assert (base / "guides" / "claude-and-selftest.html").exists()
        assert "claude-and-selftest" in read(base, "guides.html")
    for n in JOBS:
        assert JOBS[n][0].exists(), n
        tail_log(n, 1)
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        for x in ("retire_notes.json", "build_retire.py", "build_practice.py"):
            shutil.copy(BASE / x, base / x)
        add_retire_note_core(base, "시험 자료", "2099-01-01", "시험", "요약.", deploy=False)
        assert "시험 자료" in read(base, "retire.html")
        try:
            add_retire_note_core(base, "시험 자료", "2099-01-02", "시험", "x", deploy=False)
            raise AssertionError("중복 제목이 통과됨")
        except ValueError:
            pass
    try:
        start_job("nope")
        raise AssertionError("없는 작업이 통과됨")
    except ValueError:
        pass
    print("selftest 통과")


def cli_add(kind, path):
    """스킬용: JSON 파일(키는 add_column/add_guide 인자와 같음)로 추가하고 배포한다."""
    import json
    a = json.loads(Path(path).read_text(encoding="utf-8"))
    fn = {"column": add_column_core, "guide": add_guide_core}[kind]
    print(fn(BASE, **a, deploy=True))


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
    elif len(sys.argv) == 4 and sys.argv[1] == "--add":
        cli_add(sys.argv[2], sys.argv[3])
    else:
        serve()
