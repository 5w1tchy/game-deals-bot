import asyncio
from datetime import datetime

from playwright.async_api import async_playwright


async def fetch_pc_games_for_month(target_month: str, target_year: int):
    url = f"https://www.gameinformer.com/{target_year}"
    print(f"Scraping {target_month} {target_year} PC releases from: {url}")

    pc_games = []

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(url, timeout=90000, wait_until="domcontentloaded")

        await page.wait_for_selector("span.calendar_entry", timeout=15000)
        entries = await page.locator("span.calendar_entry").all()

        found_target_month = False

        for entry in entries:
            if not await entry.locator("em").count():
                continue
            if not await entry.locator("time.datetime").count():
                continue

            platforms = await entry.locator("em").text_content()
            if "PC" not in platforms:
                continue

            title_elem = entry.locator("a")
            date_elem = entry.locator("time.datetime")

            title = await title_elem.text_content()
            href = await title_elem.get_attribute("href")
            date_str = await date_elem.text_content()

            # Detect target and next month section breaks
            if date_str.strip().startswith(target_month):
                found_target_month = True
            elif found_target_month:
                # Stop once we reach the next month after finding target
                break
            else:
                continue

            pc_games.append({
                "title": title.strip(),
                "link": f"https://www.gameinformer.com{href}",
                "date": date_str.strip()
            })

        await browser.close()

    return pc_games


async def get_pc_games_for_month(month, year):
    return await fetch_pc_games_for_month(month, year)


# Optional: run standalone for testing
if __name__ == "__main__":
    games = get_pc_games_for_month("July", 2025)
    print(f"\n📅 July 2025 PC Releases:")
    if not games:
        print("⚠️ No games found for this month!")
    else:
        for game in games:
            print(f"• {game['title']} – {game['date']} – {game['link']}")
