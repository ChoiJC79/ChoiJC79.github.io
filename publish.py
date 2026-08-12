"""
나를 정리하는 프로젝트 — GitHub 자동 발행 스크립트
더블클릭 한 번으로 사이트에 업로드됩니다.
"""

import json
import base64
import urllib.request
import urllib.error
import urllib.parse
import os
import datetime
import re

# ──────────────────────────────────────────
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
REPO         = "choijc79/choijc79.github.io"
BRANCH       = "main"
BASE_DIR     = os.path.dirname(os.path.abspath(__file__))
# ──────────────────────────────────────────

if not GITHUB_TOKEN:
    print("오류: GITHUB_TOKEN 환경변수가 설정되어 있지 않습니다.")
    print("macOS에서는 🔐 GitHub 토큰 저장.command를 먼저 실행하세요.")
    print("다른 환경에서는 GITHUB_TOKEN 환경변수를 설정한 뒤 다시 실행하세요.")
    raise SystemExit(1)

HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json",
    "User-Agent": "NaeguJeongri-Publisher/1.0",
    "Content-Type": "application/json",
}

def gh_request(method, path, body=None):
    url = "https://api.github.com/repos/" + REPO + "/" + urllib.parse.quote(path, safe="/?=&:@!$'()*+,;#")
    data = json.dumps(body, ensure_ascii=False).encode("utf-8") if body else None
    req = urllib.request.Request(url, data=data, headers=HEADERS, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read()), resp.status
    except urllib.error.HTTPError as e:
        content = e.read().decode("utf-8", errors="replace")
        print(f"      HTTP {e.code}: {content[:200]}")
        try:
            return json.loads(content), e.code
        except Exception:
            return {}, e.code
    except Exception as e:
        print(f"      네트워크 오류: {e}")
        return {}, 0

def get_file_sha(path):
    data, status = gh_request("GET", f"contents/{path}?ref={BRANCH}")
    if status == 200:
        return data.get("sha"), base64.b64decode(data["content"]).decode("utf-8")
    return None, None

def get_binary_sha(path):
    data, status = gh_request("GET", f"contents/{path}?ref={BRANCH}")
    if status == 200:
        return data.get("sha")
    return None

def push_binary_file(remote_path, local_path, message):
    """바이너리 파일(이미지 등)을 GitHub에 업로드"""
    print(f"      SHA 조회 중: {remote_path}")
    sha = get_binary_sha(remote_path)
    with open(local_path, "rb") as f:
        raw = f.read()
    body = {
        "message": message,
        "content": base64.b64encode(raw).decode(),
        "branch": BRANCH,
    }
    if sha:
        body["sha"] = sha
        print(f"      SHA 확인됨 (업데이트 모드)")
    else:
        print(f"      SHA 없음 (신규 생성 모드)")
    data, status = gh_request("PUT", f"contents/{remote_path}", body)
    print(f"      결과: HTTP {status}")
    return status in (200, 201)

def push_file(path, content, message):
    print(f"      SHA 조회 중: {path}")
    sha, _ = get_file_sha(path)
    body = {
        "message": message,
        "content": base64.b64encode(content.encode("utf-8")).decode(),
        "branch": BRANCH,
    }
    if sha:
        body["sha"] = sha
        print(f"      SHA 확인됨 (업데이트 모드)")
    else:
        print(f"      SHA 없음 (신규 생성 모드)")
    data, status = gh_request("PUT", f"contents/{path}", body)
    print(f"      결과: HTTP {status}")
    return status in (200, 201)

def read_md(filename):
    filepath = os.path.join(BASE_DIR, filename)
    if not os.path.exists(filepath):
        return ""
    with open(filepath, encoding="utf-8") as f:
        return f.read()

def md_to_html_items(md_text):
    """마크다운에서 아코디언 카드 HTML 생성 (제목 클릭 시 내용 펼침)"""
    marker = "<!-- 새 항목은 아래에 추가됩니다 -->"
    if marker in md_text:
        content = md_text.split(marker, 1)[1].strip()
    else:
        content = md_text.strip()

    if not content:
        return "<p class='empty'>아직 기록이 없습니다.</p>"

    items = []
    current_date = ""
    current_text = []

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
    for i, (date, text) in enumerate(reversed(items[-30:])):
        # **[태그]** 추출 → 제목으로 사용
        tag_m = re.match(r'\*\*\[(.+?)\]\*\*\s*(.*)', text, re.DOTALL)
        if tag_m:
            tag   = tag_m.group(1)
            body  = tag_m.group(2).strip()
        else:
            tag   = "메모"
            body  = text
        body = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', body)
        date_html = f"<span class='date'>{date}</span>" if date else ""
        html += f"""
        <div class="memo-item accordion-item">
          <div class="acc-header" onclick="toggleAcc(this)">
            {date_html}
            <span class="acc-tag">[{tag}]</span>
            <span class="acc-arrow">▸</span>
          </div>
          <div class="acc-body">{body}</div>
        </div>"""
    return html


def parse_columns(md_text):
    """## 제목 | 날짜 | 태그 형식으로 칼럼 파싱"""
    marker = "<!-- 새 칼럼은 아래에 추가됩니다 -->"
    if marker in md_text:
        body = md_text.split(marker, 1)[1]
    else:
        body = md_text

    columns = []
    blocks = re.split(r'\n---\n', body.strip())
    for block in blocks:
        block = block.strip()
        if not block:
            continue
        lines = block.splitlines()
        header = lines[0].strip()
        m = re.match(r"^##\s+(.+?)\s*\|\s*(\d{4}-\d{2}-\d{2})\s*\|\s*(.+)$", header)
        if not m:
            continue
        title = m.group(1).strip()
        date  = m.group(2).strip()
        tag   = m.group(3).strip()
        paragraphs = [l.strip() for l in lines[1:] if l.strip()]
        excerpt = paragraphs[0][:80] + "…" if paragraphs else ""
        body_html = "".join(f"<p>{p}</p>" for p in paragraphs)
        columns.append({"title": title, "date": date, "tag": tag,
                         "excerpt": excerpt, "body": body_html})
    return columns


def patch_index_html(now_str):
    """로컬 index.html을 그대로 GitHub에 업로드 (로컬 파일이 정본)"""
    local_path = os.path.join(BASE_DIR, "index.html")
    if not os.path.exists(local_path):
        print("      로컬 index.html 없음 — 건너뜀", flush=True)
        return False
    with open(local_path, encoding="utf-8") as f:
        html = f.read()
    print(f"      로컬 index.html 읽기 완료 ({len(html):,} bytes)", flush=True)
    print("      업로드 중...", flush=True)
    ok = push_file("index.html", html, f"index.html update ({now_str})")
    if ok:
        print("      완료!", flush=True)
    return ok


def build_column_html():
    now = datetime.datetime.now().strftime("%Y년 %m월 %d일 %H:%M")
    md = read_md("💬 칼럼·기고.md")
    cols = parse_columns(md)

    MAIN_CATS = ['행정혁신','도시환경','지역공동체','에세이']
    CAT_LABELS = {'행정혁신':'행정·정책','도시환경':'도시·환경','지역공동체':'지역·사람','에세이':'에세이'}

    cat_tags = []
    detail_tags = []
    for c in cols:
        for t in c['tag'].split('·'):
            t = t.strip()
            if not t: continue
            if t in MAIN_CATS:
                if t not in cat_tags: cat_tags.append(t)
            else:
                if t not in detail_tags: detail_tags.append(t)

    cat_btns = ''.join(
        '<button class="cat-btn" onclick="filterCol(this,\'' + t + '\')">' + CAT_LABELS.get(t,t) + '</button>'
        for t in cat_tags
    )
    detail_btns = ''.join(
        '<button class="tag-btn" onclick="filterCol(this,\'' + t + '\')">' + t + '</button>'
        for t in detail_tags
    )
    detail_row = (
        '<div class="detail-wrap" id="detail-wrap">'
        '<div class="detail-bar">' + detail_btns + '</div>'
        '</div>'
        '<button class="tag-toggle" onclick="toggleTagBar()">▸ 태그 더보기</button>'
    ) if detail_tags else ''

    filter_html = (
        '<div class="filter-section">'
        '<div class="cat-bar">'
        '<button class="cat-btn active" onclick="filterCol(this,\'\')">전체</button>'
        + cat_btns +
        '</div>'
        + detail_row +
        '</div>'
    )

    cols_rev = list(reversed(cols))

    # 제목·태그 키워드 → Unsplash 사진 ID 매핑 (600x400 크롭)
    BASE = 'https://images.unsplash.com/'
    PARAMS = '?w=800&h=520&fit=crop&auto=format&q=80'

    PHOTO_MAP = [
        # 로컬 사진 — /img/ 경로로 직접 참조
        (['청풍랜드','만남의 광장'],               '/img/만남의광장.JPG'),         # 청풍랜드·만남의광장
        (['열쇠','당직'],                         '/img/col_duty.jpg'),           # 당직자 열쇠꾸러미
        (['체육관','놀이터'],                      '/img/col_gym.jpg'),            # 체육관이 놀이터
        (['ARS','통합 ARS'],                       '/img/col_ars.jpg'),            # 보이는 ARS
        (['보도블럭','보도블록','스마트 관리'],     '/img/col_sidewalk.jpg'),       # 보도블럭
        (['청전동','가로수'],                      '/img/col_cheongjeondong.jpg'), # 청전동 술집거리
        (['입석','마을기업'],                      '/img/col_ipseok.jpg'),         # 입석마을기업
        (['도심캠핑','광장에 텐트'],               '/img/col_camping.jpg'),        # 도심캠핑
        (['폰토그래퍼','아이들의 폰'],             '/img/col_kids_phone.jpg'),     # 아이들의 폰
        (['빈집'],                                 '/img/col_empty_house.jpg'),    # 청풍호 빈집호텔
        (['CPTED','범죄발생'],                     '/img/col_cpted.jpg'),          # CPTED
        (['박사과정생','낮에는 공무원'],            '/img/col_study.jpg'),          # 주경야독
        (['불꽃대','대장님'],                      '/img/col_scouts.jpg'),         # 제천불꽃대
        (['사그라다','파밀리에'],                  '/img/col_sagrada.jpg'),        # 사그라다 파밀리에
        (['국공유재산','용도폐지'],                '/img/col_survey.jpg'),         # 국공유재산
        (['셔틀콕'],                               '/img/col_badminton.jpg'),      # 셔틀콕
        (['아버지와 나'],                          '/img/col_family.jpg'),         # 아버지와 나
        (['간판'],                                 '/img/col_signboard.jpg'),      # 간판 정비
        # Unsplash 폴백 — 로컬 사진 없는 칼럼
        (['민선9기','이상천'],                     '/img/이상천.jpg'),                    # 민선9기 이상천 시장
        (['나눔가게','골목 가게'],                 '/img/col_nanumgae.jpg'),       # 나눔가게 실제 사진
        (['ENFP','ENTP','논리로 살고'],            'photo-1722137148592-e0aa4a8061d8'),  # MBTI
        (['제안이 살아나','제안제도'],             '/img/col_proposal.jpg'),             # 제안제도
        (['스포츠로 도심','스포츠마케팅'],         '/img/col_sports.jpg'),            # 스포츠
        (['GB350','W230','오토바이'],          '/img/오토바이.jpg'),          # 바이크
        (['수경분수','청풍호 수경'],               '/img/col_cheongpung.jpg'),          # 수경분수 (임시 — 실제 사진으로 교체 필요)
        (['대관람차'],                             'photo-1572182237597-2f97e1ad77f9'),  # 대관람차
        (['지방세','납세지','역외','세원'],         'photo-1554224155-6726b3ff858f'),    # 지방세
        (['GIS','공간분석'],                       'photo-1508739773434-c26b3d09e071'),  # GIS
        (['균형발전'],                             'photo-1477959858617-67f85cf4f1df'),  # 균형발전
        (['삼겹살','아침 삼겹살'],                'photo-1767974756540-a9b4ff92c58b'),  # 삼겹살
        (['결핍','기다림','육아'],                 'photo-1503454537195-1dcabb73ffb9'),
    (['AI', '인공지능', '지방세', '실무', '행정AI'], 'photo-1677442135703-1787eea5ce01'),  # 결핍·아이들
    ]

    CAT_FALLBACK = {
        '행정혁신':  'photo-1486406146926-c627a92ad1ab',   # modern building
        '도시환경':  'photo-1480714378408-67cf0d13bc1b',   # city skyline
        '지역공동체':'photo-1529156069898-49953e39b3ac',   # people community
        '에세이':    'photo-1455390582262-044cdead277a',   # writing
    }

    DEFAULT_PHOTO = 'photo-1477959858617-67f85cf4f1df'

    def get_photo_url(title, tag_str):
        combined = title + ' ' + tag_str
        for keywords, pid in PHOTO_MAP:
            for kw in keywords:
                if kw in combined:
                    # 로컬 경로(/img/...)는 그대로, Unsplash ID는 URL 조합
                    if pid.startswith('/'):
                        return pid
                    return BASE + pid + PARAMS
        for tag in tag_str.split('·'):
            t = tag.strip()
            if t in CAT_FALLBACK:
                return BASE + CAT_FALLBACK[t] + PARAMS
        return BASE + DEFAULT_PHOTO + PARAMS

    CAT_ACCENT = {
        '행정혁신':  '#E07828',
        '도시환경':  '#5AAA70',
        '지역공동체':'#C8A028',
        '에세이':    '#9870C8',
    }

    def get_accent(tag_str):
        for t in tag_str.split('·'):
            t = t.strip()
            if t in CAT_ACCENT:
                return CAT_ACCENT[t]
        return '#E07828'

    if not cols_rev:
        items_html = "<p style='text-align:center;padding:4rem;color:var(--muted)'>아직 칼럼이 없습니다.</p>"
        filter_html = ""
    else:
        items_html = ""
        for i, c in enumerate(cols_rev):
            slug = re.sub(r'[^\w]', '', c['date'] + c['title'])[:22]
            num_str = str(i+1).zfill(2)
            first_tag = c['tag'].split('·')[0].strip()
            cat_label = CAT_LABELS.get(first_tag, first_tag)
            photo_url = get_photo_url(c['title'], c['tag'])
            accent = get_accent(c['tag'])
            is_even = (i % 2 == 1)

            visual_block = (
                '<div class="col-visual">'
                '<img src="' + photo_url + '" alt="' + c['title'] + '" loading="lazy">'
                '<div class="col-visual-overlay">'
                '<span class="col-visual-num">' + num_str + '</span>'
                '</div>'
                '</div>'
            )

            text_block = (
                '<div class="col-text">'
                '<div class="col-num-row">'
                '<span class="col-num">' + num_str + '</span>'
                '<span class="col-cat" style="color:' + accent + '">/ ' + cat_label + '</span>'
                '</div>'
                '<h2 class="col-title">' + c['title'] + '</h2>'
                '<p class="col-excerpt">' + c['excerpt'] + '</p>'
                '<div class="col-meta-row">'
                '<span class="col-date">' + c['date'] + '</span>'
                '<span class="col-tag-chip" style="color:' + accent + ';border-color:' + accent + '44;background:' + accent + '11">' + c['tag'].replace('·',' · ') + '</span>'
                '</div>'
                '<button class="col-more" onclick="openCol(' + str(i) + ',\'' + slug + '\')">전문 읽기 →</button>'
                '</div>'
            )

            rev_cls = ' col-item-rev' if is_even else ''
            left  = text_block if is_even else visual_block
            right = visual_block if is_even else text_block
            items_html += (
                '\n        <article class="col-item' + rev_cls + '" data-tag="' + c['tag'] + '" data-slug="' + slug + '">'
                + left + right +
                '</article>'
            )

    modals_js = "const COL_DATA = " + repr(cols_rev).replace("True","true").replace("False","false").replace("None","null") + ";"

    CSS = """
:root {
  --bg:      #F4F0E8;
  --surface: #ECE8DE;
  --border:  #D4CEBC;
  --text:    #1A1410;
  --ink:     #2A2018;
  --muted:   #7A6A56;
  --accent:  #E07828;
  --light:   #FDFAF4;
}
[data-theme="dark"] {
  --bg:      #0d1117;
  --surface: #161b22;
  --border:  #2c3240;
  --text:    #E8E0D0;
  --ink:     #F0E8D8;
  --muted:   #8b8070;
  --accent:  #F08840;
  --light:   #161b22;
}
*{box-sizing:border-box;margin:0;padding:0;}
body{background:var(--bg);color:var(--text);font-family:'Noto Sans KR',sans-serif;font-weight:300;line-height:1.8;transition:background 0.3s,color 0.3s;}
a{color:var(--accent);text-decoration:none;}
.site-header{position:sticky;top:0;z-index:100;background:var(--bg);border-bottom:1px solid var(--border);padding:0 2rem;display:flex;align-items:center;justify-content:space-between;height:52px;transition:background 0.3s,border-color 0.3s;}
.logo{font-family:'Noto Serif KR',serif;font-size:15px;color:var(--accent);letter-spacing:0.04em;}
.nav-links{display:flex;gap:1.5rem;font-size:12px;}
.nav-links a{color:var(--muted);text-decoration:none;transition:color 0.15s;}
.nav-links a:hover{color:var(--accent);}
#theme-toggle{background:none;border:1px solid var(--border);color:var(--muted);font-size:11px;padding:3px 11px;border-radius:20px;cursor:pointer;font-family:'Noto Sans KR',sans-serif;letter-spacing:0.05em;transition:all 0.2s;margin-left:1rem;}
#theme-toggle:hover{border-color:var(--accent);color:var(--accent);}
.page-header{text-align:center;padding:5rem 2rem 3rem;border-bottom:1px solid var(--border);}
.page-header-eyebrow{font-size:11px;letter-spacing:0.28em;text-transform:uppercase;color:var(--muted);margin-bottom:0.8rem;display:flex;align-items:center;justify-content:center;gap:0.8rem;}
.page-header-eyebrow::before,.page-header-eyebrow::after{content:'';display:block;width:40px;height:1px;background:var(--border);}
.page-header-title{font-family:'Noto Sans KR',sans-serif;font-size:clamp(2rem,5vw,3.8rem);font-weight:700;letter-spacing:0.18em;text-transform:uppercase;color:var(--ink);line-height:1.1;}
.page-header-dot{display:inline-block;width:10px;height:10px;background:var(--accent);border-radius:50%;margin-left:4px;vertical-align:middle;position:relative;top:-6px;}
.page-header-sub{font-size:0.82rem;color:var(--muted);margin-top:1rem;letter-spacing:0.04em;}
.filter-section{max-width:1100px;margin:2rem auto 0;padding:0 2rem;}
.cat-bar{display:flex;gap:0.5rem;flex-wrap:wrap;align-items:center;margin-bottom:0.6rem;}
.cat-btn{padding:0.4rem 1.2rem;background:none;border:1px solid var(--border);color:var(--muted);font-size:12px;font-family:inherit;cursor:pointer;letter-spacing:0.06em;text-transform:uppercase;transition:all 0.15s;}
.cat-btn:hover{border-color:var(--accent);color:var(--accent);}
.cat-btn.active{background:var(--accent);border-color:var(--accent);color:#fff;}
.detail-wrap{display:none;}
.detail-bar{display:flex;flex-wrap:wrap;gap:0.35rem;margin-top:0.5rem;}
.tag-btn{padding:2px 10px;border:1px solid var(--border);background:none;color:var(--muted);font-size:11px;font-family:inherit;cursor:pointer;transition:all 0.15s;}
.tag-btn:hover,.tag-btn.active{border-color:var(--accent);color:var(--accent);}
.tag-toggle{background:none;border:none;color:var(--muted);font-size:11px;font-family:inherit;cursor:pointer;padding:0.4rem 0;letter-spacing:0.04em;transition:color 0.15s;}
.tag-toggle:hover{color:var(--accent);}
.col-list{max-width:1100px;margin:0 auto;padding:3rem 2rem 4rem;display:flex;flex-direction:column;gap:0;}
.col-item{display:grid;grid-template-columns:1fr 1fr;border:1px solid var(--border);border-bottom:none;transition:box-shadow 0.2s;}
.col-item:last-child{border-bottom:1px solid var(--border);}
.col-item:hover{box-shadow:0 4px 28px rgba(0,0,0,0.1);}
.col-visual{min-height:320px;position:relative;overflow:hidden;}
.col-visual img{width:100%;height:100%;object-fit:cover;display:block;transition:transform 0.5s ease;}
.col-item:hover .col-visual img{transform:scale(1.04);}
.col-visual-overlay{position:absolute;inset:0;background:linear-gradient(to top,rgba(0,0,0,0.55) 0%,rgba(0,0,0,0.1) 50%,transparent 100%);pointer-events:none;}
.col-visual-num{position:absolute;bottom:1rem;left:1.2rem;font-size:4.5rem;font-weight:700;color:rgba(255,255,255,0.18);line-height:1;font-family:'Noto Sans KR',sans-serif;letter-spacing:-0.04em;user-select:none;}
.col-text{padding:2.8rem 2.5rem;display:flex;flex-direction:column;background:var(--bg);}
.col-num-row{display:flex;align-items:baseline;gap:0.6rem;margin-bottom:1rem;}
.col-num{font-size:2rem;font-weight:700;color:var(--border);letter-spacing:-0.02em;font-family:'Noto Sans KR',sans-serif;line-height:1;}
.col-cat{font-size:11px;letter-spacing:0.16em;text-transform:uppercase;font-weight:500;}
.col-title{font-family:'Noto Serif KR',serif;font-size:1.2rem;font-weight:700;color:var(--ink);line-height:1.5;margin-bottom:1rem;}
.col-excerpt{font-size:13px;color:var(--muted);line-height:1.9;margin-bottom:1.2rem;flex:1;}
.col-meta-row{display:flex;align-items:center;gap:0.8rem;margin-bottom:1.2rem;flex-wrap:wrap;}
.col-date{font-size:11px;color:var(--muted);letter-spacing:0.04em;}
.col-tag-chip{font-size:10px;padding:1px 8px;letter-spacing:0.03em;border:1px solid;}
.col-more{align-self:flex-start;background:none;border:1px solid var(--border);color:var(--text);font-size:11px;font-family:inherit;letter-spacing:0.1em;text-transform:uppercase;padding:0.5rem 1.2rem;cursor:pointer;transition:all 0.2s;}
.col-more:hover{border-color:var(--accent);color:var(--accent);}
.col-hidden{display:none!important;}
.overlay{display:none;position:fixed;inset:0;background:rgba(0,0,0,0.75);z-index:200;align-items:flex-start;justify-content:center;padding:2rem 1rem;overflow-y:auto;}
.overlay.open{display:flex;}
.modal{background:var(--bg);border:1px solid var(--border);width:100%;max-width:680px;margin:auto;}
.modal-header{padding:2rem 2rem 1.5rem;display:flex;justify-content:space-between;align-items:flex-start;gap:1rem;border-bottom:1px solid var(--border);}
.modal-meta{display:flex;gap:0.6rem;margin-bottom:0.6rem;align-items:center;}
.modal-date{font-size:11px;color:var(--muted);letter-spacing:0.06em;}
.modal-tag-chip{font-size:10px;color:var(--accent);border:1px solid rgba(224,120,40,0.3);padding:1px 8px;background:rgba(224,120,40,0.06);}
.modal-title{font-family:'Noto Serif KR',serif;font-size:1.4rem;font-weight:700;line-height:1.35;color:var(--ink);}
.modal-close{background:none;border:1px solid var(--border);color:var(--muted);font-size:16px;width:32px;height:32px;cursor:pointer;display:flex;align-items:center;justify-content:center;transition:all 0.15s;flex-shrink:0;}
.modal-close:hover{border-color:var(--accent);color:var(--accent);}
.modal-body{padding:2rem;font-family:'Noto Serif KR',serif;font-size:15px;line-height:2.1;color:var(--text);}
.modal-body p{margin-bottom:1.2em;}
footer{border-top:1px solid var(--border);padding:2rem;text-align:center;font-size:11px;color:var(--muted);letter-spacing:0.04em;}
#mqb{display:none;position:fixed;bottom:0;left:0;right:0;z-index:999;background:var(--surface);border-top:1px solid var(--border);padding:0.45rem 0.6rem;gap:0.4rem;justify-content:space-around;}
#mqb a{flex:1;text-align:center;color:var(--muted);font-size:10px;padding:0.4rem 0.2rem;border:1px solid var(--border);line-height:1.4;transition:all 0.15s;}
#mqb a:hover{border-color:var(--accent);color:var(--accent);}
@media(max-width:800px){
  .col-item{grid-template-columns:1fr;}
  .col-visual{min-height:220px;order:-1;}
  .col-visual-num{font-size:3rem;}
  .col-text{padding:1.8rem 1.5rem;}
  .col-num{font-size:1.6rem;}
  .page-header{padding:3rem 1.5rem 2rem;}
  #mqb{display:flex;}
  body{padding-bottom:4rem;}
}
"""

    JS = """
(function(){
  var t=localStorage.getItem('choijc-theme')||'light';
  document.documentElement.setAttribute('data-theme',t);
  var btn=document.getElementById('theme-toggle');
  if(btn) btn.textContent=t==='dark'?'\\u2600 \\ub77c\\uc774\\ud2b8':'\\u263e \\ub2e4\\ud06c';
})();
function toggleTheme(){
  var html=document.documentElement;
  var now=html.getAttribute('data-theme');
  var next=now==='dark'?'light':'dark';
  html.setAttribute('data-theme',next);
  localStorage.setItem('choijc-theme',next);
  var btn=document.getElementById('theme-toggle');
  if(btn) btn.textContent=next==='dark'?'\\u2600 \\ub77c\\uc774\\ud2b8':'\\u263e \\ub2e4\\ud06c';
}
function filterCol(btn,tag){
  document.querySelectorAll('.cat-btn,.tag-btn').forEach(b=>b.classList.remove('active'));
  btn.classList.add('active');
  document.querySelectorAll('.col-item').forEach(a=>{
    if(!tag||a.dataset.tag.includes(tag)) a.classList.remove('col-hidden');
    else a.classList.add('col-hidden');
  });
  var n=1;
  document.querySelectorAll('.col-item:not(.col-hidden)').forEach(a=>{
    var el=a.querySelector('.col-num');
    if(el) el.textContent=String(n).padStart(2,'0');
    n++;
  });
}
function toggleTagBar(){
  var w=document.getElementById('detail-wrap');
  if(w) w.style.display=w.style.display==='block'?'none':'block';
}
function openCol(i,slug){
  var d=COL_DATA[i];
  if(!d) return;
  document.getElementById('modal-title').textContent=d.title;
  document.getElementById('modal-date').textContent=d.date;
  document.getElementById('modal-tag').textContent=d.tag.replace(/\xb7/g,' \xb7 ');
  var body=document.getElementById('modal-body');
  body.innerHTML=d.body.split('\\n\\n').map(p=>p.trim()?'<p>'+p.trim()+'</p>':'').join('');
  document.getElementById('overlay').classList.add('open');
  document.body.style.overflow='hidden';
  history.pushState({col:i},'','#'+slug);
}
function closeCol(){
  document.getElementById('overlay').classList.remove('open');
  document.body.style.overflow='';
  if(history.state&&history.state.col!==undefined) history.back();
}
function closeOnBg(e){if(e.target===document.getElementById('overlay')) closeCol();}
window.addEventListener('keydown',e=>{if(e.key==='Escape') closeCol();});
window.addEventListener('popstate',()=>document.getElementById('overlay').classList.remove('open'));
"""

    return (
        '<!DOCTYPE html>\n'
        '<html lang="ko" data-theme="light">\n'
        '<head>\n'
        '<meta charset="UTF-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
        '<title>칼럼 · 기고 | 최승환</title>\n'
        '<meta name="description" content="지방행정 현장에서 건진 생각들. 공직 경험을 바탕으로 쓴 칼럼과 에세이.">\n'
        '<meta property="og:title" content="칼럼 · 기고 | 최승환">\n'
        '<meta property="og:description" content="지방행정 현장에서 건진 생각들.">\n'
        '<meta property="og:type" content="website">\n'
        '<meta property="og:url" content="https://choijc79.github.io/column.html">\n'
        '<meta property="og:site_name" content="최승환 · Jecheon">\n'
        '<link href="https://fonts.googleapis.com/css2?family=Noto+Serif+KR:wght@400;600;700&family=Noto+Sans+KR:wght@300;400;500;700&display=swap" rel="stylesheet">\n'
        '<style>' + CSS + '</style>\n'
        '</head>\n'
        '<body>\n'
        '<header class="site-header">\n'
        '  <div class="logo">최승환 · 칼럼</div>\n'
        '  <nav class="nav-links">\n'
        '    <a href="/">← 홈</a>\n'
        '    <a href="/about.html">소개</a>\n'
        '    <a href="/research.html">연구</a>\n'
        '    <a href="/memo.html">정리노트</a>\n'
        '  </nav>\n'
        '  <button id="theme-toggle" onclick="toggleTheme()">&#9790; 다크</button>\n'
        '</header>\n'
        '<div class="page-header">\n'
        '  <div class="page-header-eyebrow">최승환 · Jecheon</div>\n'
        '  <h1 class="page-header-title">COLUMN<span class="page-header-dot"></span></h1>\n'
        '  <p class="page-header-sub">지방행정 현장에서 건진 생각들 · 공직 경험을 바탕으로 쓴 칼럼과 에세이</p>\n'
        '</div>\n'
        + filter_html + '\n'
        '<div class="col-list">\n'
        + items_html + '\n'
        '</div>\n'
        '<div class="overlay" id="overlay" onclick="closeOnBg(event)">\n'
        '  <div class="modal" id="modal">\n'
        '    <div class="modal-header">\n'
        '      <div>\n'
        '        <div class="modal-meta">\n'
        '          <span class="modal-date" id="modal-date"></span>\n'
        '          <span class="modal-tag-chip" id="modal-tag"></span>\n'
        '        </div>\n'
        '        <div class="modal-title" id="modal-title"></div>\n'
        '      </div>\n'
        '      <button class="modal-close" onclick="closeCol()">&#x2715;</button>\n'
        '    </div>\n'
        '    <div class="modal-body" id="modal-body"></div>\n'
        '  </div>\n'
        '</div>\n'
        '<footer>&copy; 2026 최승환 · choijc79.github.io · 마지막 업데이트 ' + now + '</footer>\n'
        '<div id="mqb">\n'
        '  <a href="/">🏠<br>홈</a>\n'
        '  <a href="/about.html">👤<br>소개</a>\n'
        '  <a href="/column.html">💬<br>칼럼</a>\n'
        '  <a href="/tour.html">🏍<br>투어</a>\n'
        '  <a href="/whisky.html">🥃<br>위스키</a>\n'
        '</div>\n'
        '<script>\n'
        + modals_js + '\n'
        + JS +
        '</script>\n'
        '</body>\n'
        '</html>'
    )


def build_memo_html():
    now = datetime.datetime.now().strftime("%Y년 %m월 %d일 %H:%M")

    ideas   = md_to_html_items(read_md("💡 아이디어·기획.md"))
    goals   = md_to_html_items(read_md("🎯 목표·계획·다짐.md"))
    diary   = md_to_html_items(read_md("📖 일상·감정·회고.md"))
    work    = md_to_html_items(read_md("📚 업무·논문·공부.md"))

    return f"""<!DOCTYPE html>
<html lang="ko" data-theme="light">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>정리노트 | 최승환</title>
<meta name="description" content="최승환의 아이디어·목표·일상·논문 정리노트.">
<link href="https://fonts.googleapis.com/css2?family=Noto+Serif+KR:wght@400;600;700&family=Noto+Sans+KR:wght@300;400;500&display=swap" rel="stylesheet">
<style>
:root {{
  --bg:#F4F0E8; --surface:#ECE8DE; --border:#D4CEBC;
  --text:#1A1410; --muted:#7A6A56; --accent:#E07828;
  --green:#5A7A3A; --purple:#7A4AB0; --amber:#E07828;
}}
[data-theme="dark"] {{
  --bg:#0d1117; --surface:#161b22; --border:#2c3240;
  --text:#E8E0D0; --muted:#8b8070; --accent:#F08840;
  --green:#3fb950; --purple:#bc8cff; --amber:#F08840;
}}
*{{box-sizing:border-box;margin:0;padding:0;}}
body{{background:var(--bg);color:var(--text);font-family:'Noto Sans KR',sans-serif;font-weight:300;line-height:1.8;}}
a{{color:var(--accent);text-decoration:none;}}
.site-header{{position:sticky;top:0;z-index:100;background:var(--bg);border-bottom:1px solid var(--border);padding:0 2rem;display:flex;align-items:center;justify-content:space-between;height:52px;transition:background 0.3s,border-color 0.3s;}}
.logo{{font-family:'Noto Serif KR',serif;font-size:15px;color:var(--accent);letter-spacing:0.04em;}}
.nav-links{{display:flex;gap:1.5rem;font-size:12px;}}
.nav-links a{{color:var(--muted);transition:color 0.15s;}}
.nav-links a:hover{{color:var(--accent);}}
#theme-toggle{{background:none;border:1px solid var(--border);color:var(--muted);font-size:11px;padding:3px 11px;border-radius:20px;cursor:pointer;font-family:'Noto Sans KR',sans-serif;letter-spacing:0.05em;transition:all 0.2s;margin-left:1rem;}}
#theme-toggle:hover{{border-color:var(--accent);color:var(--accent);}}
.hero{{max-width:900px;margin:0 auto;padding:3rem 2rem 1.5rem;border-bottom:1px solid var(--border);}}
.hero-label{{font-size:11px;letter-spacing:0.12em;color:var(--green);text-transform:uppercase;margin-bottom:0.6rem;}}
.hero h1{{font-family:'Noto Serif KR',serif;font-size:clamp(20px,3vw,28px);font-weight:700;line-height:1.3;margin-bottom:0.5rem;}}
.hero p{{color:var(--muted);font-size:13px;}}
.grid{{display:grid;grid-template-columns:1fr 1fr;gap:1.5rem;max-width:900px;margin:2rem auto;padding:0 2rem 3rem;}}
@media(max-width:640px){{.grid{{grid-template-columns:1fr;}}}}
.card{{background:var(--surface);border:1px solid var(--border);border-radius:8px;padding:1.5rem;}}
.card-title{{font-family:'Noto Serif KR',serif;font-size:1rem;font-weight:700;margin-bottom:1rem;display:flex;align-items:center;gap:0.5rem;}}
.card.ideas .card-title{{color:var(--amber);}}
.card.goals .card-title{{color:var(--green);}}
.card.diary .card-title{{color:var(--purple);}}
.card.work  .card-title{{color:var(--accent);}}
.memo-item{{border-bottom:1px solid var(--border);}}
.memo-item:last-child{{border-bottom:none;}}
.acc-header{{display:flex;align-items:center;gap:0.5rem;padding:0.65rem 0;cursor:pointer;user-select:none;}}
.acc-header:hover .acc-tag{{color:var(--accent);}}
.date{{font-size:0.72rem;color:var(--muted);background:rgba(122,106,86,0.1);padding:0.1rem 0.45rem;border-radius:20px;flex-shrink:0;}}
.acc-tag{{font-size:0.88rem;color:var(--text);font-weight:400;flex:1;}}
.acc-arrow{{font-size:0.7rem;color:var(--muted);margin-left:auto;transition:transform 0.2s;flex-shrink:0;}}
.acc-header.open .acc-arrow{{transform:rotate(90deg);}}
.acc-body{{display:none;font-size:0.9rem;color:var(--muted);line-height:1.75;padding:0 0 0.75rem 0.2rem;}}
.empty{{color:var(--muted);font-size:0.9rem;font-style:italic;}}
footer{{border-top:1px solid var(--border);padding:2rem;text-align:center;font-size:11px;color:var(--muted);letter-spacing:0.04em;}}
#mqb{{display:none;position:fixed;bottom:0;left:0;right:0;z-index:9999;background:var(--bg);border-top:1px solid var(--border);padding:0.45rem 0.6rem;gap:0.4rem;justify-content:space-around;padding-bottom:max(0.45rem,env(safe-area-inset-bottom));}}
#mqb a{{flex:1;text-align:center;color:var(--text);font-size:11px;font-family:sans-serif;padding:0.45rem 0.2rem;border-radius:7px;background:var(--surface);border:1px solid var(--border);line-height:1.4;transition:border-color 0.15s;}}
#mqb a:hover,#mqb a:active{{border-color:var(--accent);color:var(--accent);}}
@media(max-width:768px){{#mqb{{display:flex;}} body{{padding-bottom:4rem;}}}}
</style>
</head>
<body>
<header class="site-header">
  <div class="logo">최승환 · 정리노트</div>
  <nav class="nav-links">
    <a href="/">← 홈으로</a>
    <a href="/column.html">칼럼</a>
    <a href="/research.html">연구</a>
  </nav>
  <button id="theme-toggle" onclick="toggleTheme()">☾ 다크</button>
</header>

<div class="hero">
  <div class="hero-label">Memo · Note</div>
  <h1>나를 정리하는 기록들</h1>
  <p>마지막 업데이트 · {now}</p>
</div>

<div class="grid">
  <div class="card ideas">
    <div class="card-title">💡 아이디어 · 기획</div>
    {ideas}
  </div>
  <div class="card goals">
    <div class="card-title">🎯 목표 · 계획 · 다짐</div>
    {goals}
  </div>
  <div class="card diary">
    <div class="card-title">📖 일상 · 감정 · 회고</div>
    {diary}
  </div>
  <div class="card work">
    <div class="card-title">📚 업무 · 논문 · 공부</div>
    {work}
  </div>
</div>

<footer>© 2026 최승환 · choijc79.github.io</footer>
<div id="mqb">
  <a href="/">🏠<br>홈</a>
  <a href="/memo.html">📋<br>정리노트</a>
  <a href="/column.html">💬<br>칼럼</a>
  <a href="/research.html">🔬<br>연구</a>
</div>
<script>
(function(){{
  var t=localStorage.getItem('choijc-theme')||'light';
  document.documentElement.setAttribute('data-theme',t);
  var btn=document.getElementById('theme-toggle');
  if(btn) btn.textContent=t==='dark'?'☀ 라이트':'☾ 다크';
}})();
function toggleTheme(){{
  var next=document.documentElement.getAttribute('data-theme')==='dark'?'light':'dark';
  document.documentElement.setAttribute('data-theme',next);
  localStorage.setItem('choijc-theme',next);
  var btn=document.getElementById('theme-toggle');
  if(btn) btn.textContent=next==='dark'?'☀ 라이트':'☾ 다크';
}}
function toggleAcc(hdr){{
  hdr.classList.toggle('open');
  var body=hdr.nextElementSibling;
  body.style.display=body.style.display==='block'?'none':'block';
}}
</script>
</body>
</html>"""

def main():
    print("=" * 50)
    print("  나를 정리하는 프로젝트 — GitHub 발행 시작")
    print("=" * 50)

    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    print("\n[1/4] 페이지 HTML 생성 중...")
    memo_html   = build_memo_html()

    print("[2/4] memo.html 업로드 중...")
    ok1 = push_file("memo.html", memo_html, f"📝 정리노트 업데이트 ({now_str})")

    def push_local(filename, label, msg=""):
        fpath = os.path.join(BASE_DIR, filename)
        if not os.path.exists(fpath):
            print(f"      skip: {filename}")
            return True
        with open(fpath, encoding="utf-8") as _f:
            _html = _f.read()
        return push_file(filename, _html, f"{label} ({now_str})")

    # column.html은 더 이상 build_column_html()로 재생성하지 않는다.
    # 개별 칼럼 페이지(columns/*.html, build_columns.py 생성)를 링크하는
    # 로컬 column.html이 정본이므로 그대로 업로드한다.
    print("[3/4] column.html 업로드 중 (로컬 파일 그대로)...")
    ok2 = push_local("column.html", "칼럼 업데이트")

    print("[columns] columns/ (개별 칼럼 페이지) ...")
    cols_dir = os.path.join(BASE_DIR, "columns")
    if os.path.exists(cols_dir):
        for colfile in sorted(os.listdir(cols_dir)):
            colpath = os.path.join(cols_dir, colfile)
            if os.path.isfile(colpath) and colfile.endswith(".html"):
                push_local(f"columns/{colfile}", f"update column page {colfile}")

    print("[4/4] jecheon_moto_guide.html ...")
    ok3 = push_local("jecheon_moto_guide.html", "update jecheon guide")

    print("[img] images/ ...")
    img_dir = os.path.join(BASE_DIR, "images")
    if os.path.exists(img_dir):
        for imgfile in sorted(os.listdir(img_dir)):
            imgpath = os.path.join(img_dir, imgfile)
            if os.path.isfile(imgpath):
                push_binary_file(f"images/{imgfile}", imgpath, f"img ({now_str})")

    print("[img] img/earth.jpg (지구 텍스처) ...")
    _earth = os.path.join(BASE_DIR, "img", "earth.jpg")
    if os.path.exists(_earth):
        push_binary_file("img/earth.jpg", _earth, f"earth-texture ({now_str})")

    print("[img] img/ (칼럼 사진) ...")
    col_img_dir = os.path.join(BASE_DIR, "img")
    if os.path.exists(col_img_dir):
        for imgfile in sorted(os.listdir(col_img_dir)):
            imgpath = os.path.join(col_img_dir, imgfile)
            if os.path.isfile(imgpath):
                push_binary_file(f"img/{imgfile}", imgpath, f"col-img ({now_str})")

    print("[img] img/wonwoo/ (\xec\x9b\x90\xec\x9a\xb0 \xec\x82\xac\xec\xa7\x84) ...")
    wonwoo_dir = os.path.join(BASE_DIR, "img", "wonwoo")
    if os.path.exists(wonwoo_dir):
        _exts = {'.jpg', '.jpeg', '.png', '.gif', '.webp',
                 '.JPG', '.JPEG', '.PNG', '.GIF', '.WEBP'}
        wonwoo_files = sorted([
            f for f in os.listdir(wonwoo_dir)
            if os.path.isfile(os.path.join(wonwoo_dir, f))
            and os.path.splitext(f)[1] in _exts
        ])
        for _wf in wonwoo_files:
            push_binary_file(f"img/wonwoo/{_wf}",
                             os.path.join(wonwoo_dir, _wf),
                             f"wonwoo-img ({now_str})")
        _manifest = json.dumps(wonwoo_files, ensure_ascii=False)
        push_file("img/wonwoo/manifest.json", _manifest,
                  f"wonwoo-manifest ({now_str})")

    push_local("macallan.html",                      "update macallan")
    push_local("whisky.html",                        "update whisky")
    push_local("tour.html",                          "update tour")
    push_local("taipei_travel_plan_v10_upgrade.html","update taipei")
    push_local("vietnam_moto_guide.html",            "update vietnam")
    push_local("vietnam-motorbike-tour.html",        "update vietnam north tour")
    push_local("hiroshima_trip_memory.html",          "update hiroshima trip")
    push_local("budget_dashboard.html",      "update budget dashboard")
    push_local("guestbook.html",                     "update guestbook")
    push_local("chronicle.html",                     "update chronicle")
    push_local("about.html",                         "update about")
    push_local("jecheon_9th_policy_whitepaper.html", "update 9th term policy whitepaper")
    push_local("glenfiddich12.html",                 "update glenfiddich guide")
    push_local("balvenie12.html",                    "update balvenie guide")
    push_local("dalmore12.html",                     "update dalmore guide")
    push_local("glenlivet12.html",                   "update glenlivet guide")
    push_local("local.html",                         "update local introduction page")
    push_local("jecheon_dashboard.html",             "update jecheon dashboard")
    push_local("jecheon_budget_5yr_dashboard.html",  "update budget 5yr dashboard")
    push_binary_file("profile.jpg", os.path.join(BASE_DIR, "profile.jpg"), "add profile photo")
    push_local("tourism-plan.html",                  "update tourism plan (merged)")
    push_local("jobs_in_jecheon.html",               "add Jobs in Jecheon page")
    push_local("jecheon_investment_plan.html",       "add investment plan page")
    push_local("letter_wonwoo.html",                   "add letter to wonwoo")
    push_local("leaflet.html",                         "add leaflet maker")
    push_local("research.html",                      "update research")
    push_local("index.html",                         "update index")

    print("[css/js] index 페이지 스타일·스크립트 ...")
    push_local("css/index.css",                      "update index css")
    push_local("css/jc-picker.css",                   "update jc-picker css")
    push_local("js/site.js",                          "update site js")
    push_local("js/globe.js",                         "update globe js")
    push_local("js/jc-picker.js",                      "update jc-picker js")

    print("=" * 50)
    print("  Done!")
    print("=" * 50)
    base_url = "https://choijc79.github.io/"
    for p in ["", "memo.html", "column.html", "about.html", "research.html",
              "jecheon_dashboard.html", "jecheon_budget_5yr_dashboard.html",
              "jobs_in_jecheon.html", "jecheon_investment_plan.html", "leaflet.html"]:
        print(f"  {base_url}{p}")
    print()

if __name__ == "__main__":
    main()
