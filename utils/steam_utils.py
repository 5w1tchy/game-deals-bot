import re
import unicodedata

import aiohttp
from bs4 import BeautifulSoup


def normalize(text):
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = text.replace("Δ", "Delta")
    text = re.sub(r"[™®©]", "", text)
    return text.lower().strip()


async def get_steam_link_and_image(title):
    search_url = f"https://store.steampowered.com/search/?term={title}"
    headers = {"User-Agent": "Mozilla/5.0"}

    normalized_target = normalize(title)

    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(search_url) as response:
            if response.status != 200:
                print(f"Steam search failed for '{title}'")
                return None, None, None, None

            html = await response.text()
            soup = BeautifulSoup(html, "html.parser")
            results = soup.select("a.search_result_row")

            best_match = None
            best_score = 0

            for result in results:
                name_tag = result.select_one("span.title")
                if not name_tag:
                    continue

                candidate = normalize(name_tag.text)

                if normalized_target in candidate:
                    best_match = result
                    break

                score = sum(
                    word in candidate for word in normalized_target.split())
                if score > best_score:
                    best_score = score
                    best_match = result

            if not best_match:
                return None, None, None, None

            game_url = best_match["href"]

        # Get details from the game's Steam page
        async with session.get(game_url) as game_page:
            html = await game_page.text()
            soup = BeautifulSoup(html, "html.parser")

            # Get thumbnail
            image_tag = soup.select_one("meta[property='og:image']")
            image_url = image_tag["content"] if image_tag else None

            # Get description
            desc_tag = soup.select_one(".game_description_snippet")
            if desc_tag:
                description = desc_tag.get_text(strip=True)
            else:
                og_desc = soup.select_one("meta[property='og:description']")
                description = og_desc["content"].strip(
                ) if og_desc else "No description available."

            # Get price
            price_tag = soup.select_one(
                ".discount_final_price, .game_purchase_price")
            price = price_tag.get_text(
                strip=True) if price_tag else "Price not listed."

            return game_url, image_url, description, price
