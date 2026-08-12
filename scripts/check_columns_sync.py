#!/usr/bin/env python3
"""
check_columns_sync.py — 칼럼 3개 소스(md 원본 / column.html / columns/*.html) 동기화 검증

사용법:
  python scripts/check_columns_sync.py

검사 항목:
  1) 💬 칼럼·기고.md 의 칼럼 개수
  2) column.html <ol id="idx-list"> 안의 <li class="idx-row"> 개수
  3) column.html <div class="col-list"> 안의 <article class="col-item"> 개수
  4) column.html 의 "N편" 표시 라벨(idx-count) 값
  5) columns/*.html 실제 생성 파일 개수
  6) idx-row 슬러그 집합 == col-item data-slug 집합 == columns/ 파일 슬러그 집합

하나라도 다르면 어디가 몇 개/어떤 슬러그가 다른지 구체적으로 출력하고
종료 코드 1로 끝난다 (CI/사전 배포 체크용).
"""

import re
import sys
import unicodedata
from pathlib import Path

if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = Path(__file__).parent.parent
MD_PATH = BASE_DIR / '💬 칼럼·기고.md'
COLUMN_HTML = BASE_DIR / 'column.html'
COLUMNS_DIR = BASE_DIR / 'columns'


def normalize_unicode(value):
    """macOS 파일명과 HTML 값을 같은 유니코드 형식으로 비교한다."""
    return unicodedata.normalize('NFC', value)


def load_md_count():
    md = MD_PATH.read_text(encoding='utf-8')
    parts = re.split(r'\n---\n', md.strip())
    count = 0
    for part in parts:
        part = part.strip()
        if not part:
            continue
        if re.match(r'^## (.+?)\s*\|\s*(\d{4}-\d{2}-\d{2})\s*\|\s*(.+?)$', part, re.MULTILINE):
            count += 1
    return count


def load_idx_rows():
    """idx-list 안의 <li class="idx-row" ... /columns/{slug}.html> 슬러그 목록"""
    html = COLUMN_HTML.read_text(encoding='utf-8')
    m = re.search(r'<!--AUTO:INDEX-->(.*?)<!--/AUTO:INDEX-->', html, re.DOTALL)
    block = m.group(1) if m else ''
    return re.findall(r"<li class=\"idx-row\"[^>]*onclick=\"location\.href='/columns/([^']+)\.html'\"", block)


def load_idx_count_label():
    """'☰ 전체 칼럼 목록 <span class="idx-count">NN편</span>' 의 NN"""
    html = COLUMN_HTML.read_text(encoding='utf-8')
    m = re.search(r'<span class="idx-count">(\d+)편</span>', html)
    return int(m.group(1)) if m else None


def load_col_items():
    """col-list 안의 <article class="col-item" ... data-slug="...">  슬러그 목록"""
    html = COLUMN_HTML.read_text(encoding='utf-8')
    m = re.search(r'<!--AUTO:CARDS-->(.*?)<!--/AUTO:CARDS-->', html, re.DOTALL)
    block = m.group(1) if m else ''
    return re.findall(r'<article class="col-item[^"]*"[^>]*data-slug="([^"]+)"', block)


def load_columns_dir_slugs():
    if not COLUMNS_DIR.exists():
        return []
    return sorted(p.stem for p in COLUMNS_DIR.glob('*.html'))


def load_local_card_images():
    """카드에서 참조하는 로컬 img 파일 경로 목록"""
    html = COLUMN_HTML.read_text(encoding='utf-8')
    m = re.search(r'<!--AUTO:CARDS-->(.*?)<!--/AUTO:CARDS-->', html, re.DOTALL)
    block = m.group(1) if m else ''
    return [src[1:] for src in re.findall(r'<img src="([^"]+)"', block)
            if src.startswith('/img/')]


def load_local_image_paths():
    image_dir = BASE_DIR / 'img'
    if not image_dir.exists():
        return set()
    return {normalize_unicode(str(path.relative_to(BASE_DIR)))
            for path in image_dir.rglob('*') if path.is_file()}


def load_col_num_badges():
    """col-item 카드 등장 순서대로 col-num / col-visual-num 값 목록 (개수는 맞는데 번호가 밀리지 않은 경우를 잡기 위함)"""
    html = COLUMN_HTML.read_text(encoding='utf-8')
    m = re.search(r'<!--AUTO:CARDS-->(.*?)<!--/AUTO:CARDS-->', html, re.DOTALL)
    block = m.group(1) if m else ''
    articles = re.findall(r'<article class="col-item.*?</article>', block, re.DOTALL)
    pairs = []
    for art in articles:
        num = re.search(r'<span class="col-num">(\d+)</span>', art)
        vnum = re.search(r'<span class="col-visual-num">(\d+)</span>', art)
        pairs.append((num.group(1) if num else None, vnum.group(1) if vnum else None))
    return pairs


def main():
    ok = True

    md_count = load_md_count()
    idx_rows = load_idx_rows()
    col_items = load_col_items()
    idx_label = load_idx_count_label()
    dir_slugs = load_columns_dir_slugs()
    card_images = load_local_card_images()
    local_images = load_local_image_paths()

    counts = {
        'md 원본 칼럼 수 (💬 칼럼·기고.md)': md_count,
        'idx-list <li> 개수 (column.html)': len(idx_rows),
        'col-item <article> 개수 (column.html)': len(col_items),
        'idx-count 라벨 값 ("N편")': idx_label,
        'columns/*.html 파일 개수': len(dir_slugs),
    }

    print('=== 개수 비교 ===')
    values = [v for v in counts.values() if v is not None]
    all_equal = len(set(values)) <= 1
    for label, v in counts.items():
        mark = '✅' if v == values[0] else '❌'
        print(f'  {mark} {label}: {v}')
    if not all_equal:
        ok = False
        print('  → 개수가 서로 다릅니다. 위 항목 중 누락되거나 중복 추가된 곳을 확인하세요.')

    print('\n=== 슬러그 집합 비교 ===')
    set_idx = {normalize_unicode(slug) for slug in idx_rows}
    set_cards = {normalize_unicode(slug) for slug in col_items}
    set_dir = {normalize_unicode(slug) for slug in dir_slugs}

    if set_idx == set_cards == set_dir:
        print(f'  ✅ 세 곳의 슬러그 집합이 모두 일치합니다 ({len(set_idx)}개)')
    else:
        ok = False
        only_idx = set_idx - set_cards - set_dir
        only_cards = set_cards - set_idx - set_dir
        only_dir = set_dir - set_idx - set_cards
        missing_in_dir = (set_idx | set_cards) - set_dir
        missing_in_html = set_dir - (set_idx & set_cards)

        if only_idx:
            print(f'  ❌ idx-list에만 있음 (카드/파일 누락): {sorted(only_idx)}')
        if only_cards:
            print(f'  ❌ col-item 카드에만 있음 (idx-list/파일 누락): {sorted(only_cards)}')
        if only_dir:
            print(f'  ❌ columns/ 폴더에만 있음 (column.html에 미등록, 유령 페이지): {sorted(only_dir)}')
        if missing_in_dir - only_idx - only_cards:
            print(f'  ❌ column.html에는 있는데 columns/*.html이 없음: {sorted(missing_in_dir - only_idx - only_cards)}')

    print('\n=== 카드 이미지 경로 검증 ===')
    missing_images = [path for path in card_images if normalize_unicode(path) not in local_images]
    if missing_images:
        ok = False
        print(f'  ❌ 카드에서 참조하지만 img/에 없는 파일: {missing_images}')
    else:
        print(f'  ✅ 로컬 카드 이미지 {len(card_images)}개가 모두 존재합니다.')

    print('\n=== 카드 번호(col-num) 순서 검증 ===')
    badges = load_col_num_badges()
    expected = [f'{i:02d}' for i in range(1, len(badges) + 1)]
    actual_num = [n for n, _ in badges]
    actual_vnum = [v for _, v in badges]
    if actual_num == expected and actual_vnum == expected:
        print(f'  ✅ 01~{expected[-1]}까지 순서대로 매겨져 있습니다.')
    else:
        ok = False
        for i, ((n, v), e) in enumerate(zip(badges, expected)):
            if n != e or v != e:
                print(f'  ❌ {i+1}번째 카드: col-num={n}, col-visual-num={v} (기대값 {e}) — 새 칼럼을 목록 위쪽에 끼워 넣고 이후 카드 번호를 밀지 않았을 가능성')

    print()
    if ok:
        print('✅ 전체 동기화 정상. 발행 실행 파일 진행 가능.')
        return 0
    else:
        print('❌ 동기화 깨짐. 배포 전에 위 불일치를 먼저 해결하세요.')
        return 1


if __name__ == '__main__':
    sys.exit(main())
