# filepath: /home/gupta/nfdi-demonstrator/test_browser_load.py
import asyncio
from playwright.async_api import async_playwright

async def simulate_user(user_id):
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            print(f"User {user_id} loading page...")
            await page.goto("http://localhost:8000/index.html")
            await page.fill("#ms-id", str(user_id % 10))
            await page.evaluate('''(value) => {
                const slider = document.getElementById('kappa1');
                slider.value = value;
                slider.dispatchEvent(new Event('input', { bubbles: true }));
                slider.dispatchEvent(new Event('change', { bubbles: true }));
            }''', str(2.0 + (user_id % 5)))
            await page.evaluate('''(value) => {
                const slider = document.getElementById('alpha');
                slider.value = value;
                slider.dispatchEvent(new Event('input', { bubbles: true }));
                slider.dispatchEvent(new Event('change', { bubbles: true }));
            }''', str(30.0 + (user_id % 6) * 10))
            await page.click("#update-btn")
            await page.wait_for_selector(".info-panel", timeout=30000)
            print(f"User {user_id} simulation complete")
            await browser.close()
    except Exception as e:
        print(f"User {user_id} error: {e}")

async def main():
    users = 10
    await asyncio.gather(*(simulate_user(i) for i in range(users)))

if __name__ == "__main__":
    asyncio.run(main())