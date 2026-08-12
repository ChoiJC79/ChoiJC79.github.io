# 리플릿 제작기의 핵심 편집과 인쇄 레이아웃을 브라우저에서 검증하는 테스트
from playwright.sync_api import sync_playwright


with sync_playwright() as playwright:
    browser = playwright.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1440, "height": 1000})
    page.goto('http://127.0.0.1:4173/leaflet.html')
    page.wait_for_load_state('networkidle')

    assert page.locator('#outer .panel').count() == 3
    page.get_by_role('button', name='2단 리플렛 (4면)').click()
    assert page.locator('#outer .panel').count() == 2

    page.get_by_role('button', name='굵은 제목').click()
    page.locator('#elementText').fill('단양 여름 축제')
    assert page.get_by_text('단양 여름 축제').count() == 1

    page.locator('#addImageInput').set_input_files({
        'name': 'test.png',
        'mimeType': 'image/png',
        'buffer': bytes.fromhex(
            '89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c489'
            '0000000d49444154789c6360f8cfc0000004010100b1d0e7b90000000049454e44ae426082'
        ),
    })
    assert page.locator('.item-image').count() == 1

    page.get_by_role('button', name='현재 상태 저장 (새 버전)').click()
    assert page.locator('#versionSelect option').count() == 1

    page.emulate_media(media='print')
    assert page.locator('.leaflet.print').count() == 2
    page.screenshot(path='/private/tmp/leaflet-test.png', full_page=True)
    browser.close()
