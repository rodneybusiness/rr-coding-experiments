import json, asyncio
from pathlib import Path
from playwright.async_api import async_playwright

STATE_FILE = Path("imdbpro_state.json")

async def main():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.goto("https://pro.imdb.com")
        print("🟢  Log in via the UI, then press ENTER here.")
        input()
        state = await page.context.storage_state()
        STATE_FILE.write_text(json.dumps(state))
        print(f"✅  Saved session to {STATE_FILE}")
        await browser.close()

asyncio.run(main())

