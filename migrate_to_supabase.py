# 로컬 마크다운 파일(칼럼 및 정리노트)을 Supabase 데이터베이스로 일괄 업로드 및 동기화하는 파이썬 스크립트

import os
import re
import sys
import json
import urllib.request
import urllib.error
import urllib.parse
from pathlib import Path

BASE_DIR = Path(__file__).parent.resolve()

# ─── 환경 변수 로드 (.env 파일이 있으면 우선 읽음) ──────────────────

def load_env():
    env_path = BASE_DIR / '.env'
    if env_path.exists():
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if '=' in line:
                    key, val = line.split('=', 1)
                    os.environ[key.strip()] = val.strip().strip('"').strip("'")

load_env()

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") # RLS 우회를 위해 service_role 키 권장

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ 오류: SUPABASE_URL 및 SUPABASE_SERVICE_ROLE_KEY 환경변수가 설정되어 있지 않습니다.")
    print("\n[해결 방법 1] 터미널에서 임시 설정 후 실행:")
    print("  export SUPABASE_URL=\"https://your-project.supabase.co\"")
    print("  export SUPABASE_SERVICE_ROLE_KEY=\"your-service-role-key\"")
    print("\n[해결 방법 2] 프로젝트 루트 디렉토리에 .env 파일을 만들고 아래 내용 입력:")
    print("  SUPABASE_URL=https://your-project.supabase.co")
    print("  SUPABASE_SERVICE_ROLE_KEY=your-service-role-key")
    sys.exit(1)

# ─── Supabase API 요청 헬퍼 함수 ───────────────────────────────

def sb_request(method, table, query="", body=None, headers=None):
    url = f"{SUPABASE_URL.rstrip('/')}/rest/v1/{table}"
    if query:
        url += f"?{query}"
        
    req_headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
    }
    if headers:
        req_headers.update(headers)
        
    data = json.dumps(body, ensure_ascii=False).encode("utf-8") if body else None
    req = urllib.request.Request(url, data=data, headers=req_headers, method=method)
    
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            status = resp.status
            resp_body = resp.read().decode("utf-8")
            return json.loads(resp_body) if resp_body else None, status
    except urllib.error.HTTPError as e:
        content = e.read().decode("utf-8", errors="replace")
        print(f"      API HTTP Error {e.code}: {content}")
        return None, e.code
    except Exception as e:
        print(f"      API Network Error: {e}")
        return None, 0

# ─── 1. 칼럼 데이터 파싱 (build_columns.py 기반) ─────────────────

def load_md_cols():
    md_path = BASE_DIR / '💬 칼럼·기고.md'
    if not md_path.exists():
        print("❌ '💬 칼럼·기고.md' 파일을 찾을 수 없습니다.")
        return []
        
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
    column_html_path = BASE_DIR / 'column.html'
    if not column_html_path.exists():
        print("❌ 'column.html' 파일을 찾을 수 없습니다.")
        return []
        
    with open(column_html_path, 'r', encoding='utf-8') as f:
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
    column_html_path = BASE_DIR / 'column.html'
    if not column_html_path.exists():
        return {}
        
    with open(column_html_path, 'r', encoding='utf-8') as f:
        c = f.read()
    cards = re.findall(
        r'<article[^>]*data-slug="([^"]*)">'
        r'<div class="col-visual"><img src="([^"]*)"',
        c
    )
    return {slug: img for slug, img in cards}

def title_key(t):
    t = t.split('—')[0].split('...')[0]
    return re.sub(r'[^가-힣a-zA-Z0-9]', '', t).lower()

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
            
        # 태그는 '·' 구분자를 split하여 리스트 배열로 변환
        tag_list = [t.strip() for t in tag.split('·') if t.strip()]
        
        result.append({
            'type': typ,
            'slug': slug,
            'tags': tag_list,
            'date': date,
            'title': title,
            'body': body
        })
    return result

# ─── 2. 4대 정리노트 메모 파싱 ───────────────────────────────────

def parse_memos(file_name, category):
    file_path = BASE_DIR / file_name
    if not file_path.exists():
        print(f"⚠️ 경고: '{file_name}' 파일이 존재하지 않아 건너뜁니다.")
        return []
        
    with open(file_path, 'r', encoding='utf-8') as f:
        md = f.read()
    
    marker = "<!-- 새 항목은 아래에 추가됩니다 -->"
    content = md.split(marker, 1)[1].strip() if marker in md else md.strip()
    if not content:
        return []
    
    items = []
    current_date = None
    current_text = []
    
    for line in content.splitlines():
        line = line.strip()
        if not line:
            if current_text and current_date:
                items.append({
                    'category': category,
                    'date': current_date,
                    'content': " ".join(current_text)
                })
                current_text = []
            continue
            
        # ### YYYY-MM-DD 헤더 매칭
        date_match = re.match(r'^#{1,4}\s*(\d{4}[.\-/]\d{2}[.\-/]\d{2})', line)
        if date_match:
            if current_text and current_date:
                items.append({
                    'category': category,
                    'date': current_date,
                    'content': " ".join(current_text)
                })
                current_text = []
            raw_date = date_match.group(1)
            current_date = raw_date.replace('.', '-').replace('/', '-')
        elif line.startswith("- ") or line.startswith("* "):
            if current_text and current_date:
                items.append({
                    'category': category,
                    'date': current_date,
                    'content': " ".join(current_text)
                })
                current_text = []
            current_text = [line[2:]]
        else:
            if current_date: # 날짜가 지정된 이후의 라인만 본문으로 취급
                current_text.append(line.lstrip("#").strip())
                
    if current_text and current_date:
        items.append({
            'category': category,
            'date': current_date,
            'content': " ".join(current_text)
        })
        
    return items

# ─── 메인 동기화 로직 ───────────────────────────────────────────

def sync_columns():
    print("\n--- 1. [columns] 테이블 동기화 시작 ---")
    md_cols = load_md_cols()
    li_data = load_column_index()
    img_map = load_card_images()
    
    if not li_data:
        print("❌ column.html에서 칼럼 목록 인덱스를 읽어오지 못했습니다.")
        return
        
    matched = match_cols(li_data, md_cols)
    print(f"-> 로컬에서 총 {len(matched)}개의 칼럼을 파싱했습니다.")
    
    # 이미지 URL 추가
    for col in matched:
        col['image_url'] = img_map.get(col['slug'])
        
    # Supabase로 Upsert 실행 (slug가 unique 키이므로 중복 시 덮어씀)
    # PostgREST bulk upsert (리스트 형태로 전송)
    print("-> Supabase 업로드 중...")
    headers = {
        "Prefer": "resolution=merge-duplicates, return=minimal"
    }
    _, status = sb_request("POST", "columns", "on_conflict=slug", matched, headers)
    if status in (200, 201):
        print(f"✅ 칼럼 동기화 완료! (총 {len(matched)}개)")
    else:
        print(f"❌ 칼럼 동기화 실패. HTTP Status: {status}")

def sync_memos():
    print("\n--- 2. [memos] 테이블 동기화 시작 ---")
    
    memo_files = [
        ("💡 아이디어·기획.md", "ideas"),
        ("🎯 목표·계획·다짐.md", "goals"),
        ("📖 일상·감정·회고.md", "diary"),
        ("📚 업무·논문·공부.md", "work")
    ]
    
    all_memos = []
    for file_name, cat in memo_files:
        items = parse_memos(file_name, cat)
        print(f"-> '{file_name}' 파싱 완료: {len(items)}개 항목 추출")
        all_memos.extend(items)
        
    if not all_memos:
        print("⚠️ 업로드할 메모 데이터가 없습니다.")
        return
        
    print(f"-> 총 {len(all_memos)}개의 메모 항목을 동기화합니다.")
    
    # 메모는 마크다운 파일 전체가 정본이므로, 디비 정합성을 위해 
    # 기존 DB의 메모 데이터를 초기화(DELETE)하고 전체 데이터를 일괄 INSERT하는 방식을 사용합니다.
    print("-> 기존 Supabase 메모 데이터 비우는 중...")
    _, del_status = sb_request("DELETE", "memos", "id=gt.0")
    if del_status not in (200, 204):
        # gt.0이 실패할 경우를 대비하여 전체 삭제 시도
        _, del_status = sb_request("DELETE", "memos")
        
    print(f"   (기존 데이터 삭제 결과: HTTP {del_status})")
    
    # 200개 단위로 청크 분할하여 bulk insert 실행 (포스트그레스 페이로드 크기 안전성 확보)
    chunk_size = 200
    success = True
    for i in range(0, len(all_memos), chunk_size):
        chunk = all_memos[i:i+chunk_size]
        print(f"-> 메모 데이터 전송 중... ({i+1}~{min(i+chunk_size, len(all_memos))} / {len(all_memos)})")
        _, status = sb_request("POST", "memos", body=chunk)
        if status not in (200, 201, 204):
            print(f"❌ 메모 동기화 실패 (청크 {i//chunk_size + 1}). HTTP Status: {status}")
            success = False
            break
            
    if success:
        print(f"✅ 메모 동기화 완료! (총 {len(all_memos)}개)")

def main():
    print("🚀 Supabase 콘텐츠 마이그레이션 도구 실행 🚀")
    print(f"Target Project: {SUPABASE_URL}")
    
    # 동기화 실행
    sync_columns()
    sync_memos()
    
    print("\n🎉 모든 동기화 작업이 완료되었습니다! 🎉")

if __name__ == '__main__':
    main()
