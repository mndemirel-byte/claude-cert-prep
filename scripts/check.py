"""Smoke test with Playwright: opens dist/index.html, toggles EN, runs a full mock exam."""
import os, sys
from playwright.sync_api import sync_playwright
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
u = "file://" + os.path.join(ROOT, "dist", "index.html")
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={"width": 900, "height": 1000})
    errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(u); pg.click("#langtoggle")
    missing = pg.evaluate("MOCK_POOL.filter(q=>!q.en).length")
    pg.goto(u + "#mock"); pg.wait_for_timeout(200); pg.click("#mock-start"); pg.wait_for_timeout(300)
    n = pg.evaluate("document.querySelectorAll('#mock-palette button').length")
    for i in range(n):
        pg.click("#mock-q .opt[data-k='B']")
        if i < n - 1: pg.click("#mock-next")
    pg.on("dialog", lambda d: d.accept()); pg.click("#mock-finish"); pg.wait_for_timeout(300)
    score = pg.evaluate("document.querySelector('.bigscore').textContent")
    b.close()
print(f"mock questions: {n}, score with all-B: {score}, pool items without EN: {missing}, JS errors: {errs}")
sys.exit(1 if errs or missing else 0)
