from pathlib import Path
from playwright.sync_api import sync_playwright

with sync_playwright() as playwright:
    browser = playwright.chromium.launch()
    page = browser.new_page(viewport={"width": 1440, "height": 900})
    errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    page.clock.install()
    page.goto(Path(__file__).with_name("index.html").resolve().as_uri())
    page.get_by_role("button", name="התחלה", exact=True).click()
    previous = 0
    for seconds, title in [
        (70, "הגיע הזמן לדובר הבא"),
        (160, "עוברים לצד השני"),
        (250, "הגיע הזמן לדובר הבא"),
        (340, "מחליפים צד"),
        (430, "הגיע הזמן לדובר הבא"),
        (520, "דקה אחרונה לסיכום"),
        (580, "הזמן הסתיים"),
    ]:
        page.clock.fast_forward((seconds - previous) * 1000 - 1000)
        assert page.locator("#elapsed").inner_text() == f"{(seconds-1)//60:02d}:{(seconds-1)%60:02d}"
        page.clock.fast_forward(1000)
        assert page.locator("#notice-title").inner_text() == title
        assert page.locator("li.done").count() == [70,160,250,340,430,520,580].index(seconds)+1
        previous = seconds
    page.clock.fast_forward(10000)
    assert page.locator("#elapsed").inner_text() == "09:40"
    assert page.locator("#remaining").inner_text() == "00:00"
    page.get_by_role("button", name="נושא חדש", exact=True).click()
    page.clock.fast_forward(10000)
    assert page.locator("#elapsed").inner_text() == "00:10"
    page.get_by_role("button", name="השהיה", exact=True).click()
    page.clock.fast_forward(30000)
    assert page.locator("#elapsed").inner_text() == "00:10"
    page.get_by_role("button", name="המשך", exact=True).click()
    page.clock.fast_forward(60000)
    assert page.locator("#notice-label").inner_text() == "עכשיו · 01:10"
    page.get_by_role("button", name="איפוס", exact=True).click()
    assert page.locator("#elapsed").inner_text() == "00:00"
    assert page.locator("#notice-title").inner_text() == "הבמה שלכם"
    page.locator("h1").click()
    page.keyboard.press("Space")
    page.clock.fast_forward(161000)
    assert page.locator("#notice-title").inner_text() == "עוברים לצד השני"
    page.keyboard.press("Space")
    page.clock.fast_forward(10000)
    assert page.locator("#elapsed").inner_text() == "02:41"
    for width, height in [(1920,1080),(1280,720),(390,844),(844,390)]:
        page.set_viewport_size({"width":width,"height":height})
        assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
        for selector in ["#elapsed", ".controls", "#notice"]:
            assert page.locator(selector).is_visible()
    page.set_viewport_size({"width":1440,"height":900})
    page.screenshot(path="/tmp/meetup-timer-preview.png", full_page=True)
    assert not errors, errors
    browser.close()
print("Passed: all 7 milestones, automatic stop, restart, pause/resume, reset, keyboard, 4 viewport sizes.")
