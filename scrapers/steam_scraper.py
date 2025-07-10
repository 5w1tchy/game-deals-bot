import re
import time

import requests
from bs4 import BeautifulSoup

from scrapers.steam_reviews import fetch_steam_reviews


def fetch_steam_deals():
    good_deals = []
    bad_deals = []
    total_games_found = 0  # track if we fetched any games at all

    for page in [1, 2]:  # Fetch first two pages
        print(f"\nFetching page {page}...")
        url = f"https://store.steampowered.com/search/?specials=1&supportedlang=english&page={page}"
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            print(f"Failed to retrieve page {page}")
            continue

        soup = BeautifulSoup(response.text, 'html.parser')
        items = soup.select('a.search_result_row')
        print(f"Found {len(items)} games on page {page}")
        total_games_found += len(items)

        for item in items:
            title_elem = item.select_one('span.title')
            title = title_elem.text.strip() if title_elem else "No title"

            discount_elem = item.select_one('div.discount_pct')
            discount = discount_elem.text.strip(
            ) if discount_elem and discount_elem.text.strip() else None

            original_price_elem = item.select_one(
                'div.discount_original_price')
            original_price = original_price_elem.text.strip(
            ) if original_price_elem and original_price_elem.text.strip() else None

            final_price_elem = item.select_one('div.discount_final_price')
            final_price = final_price_elem.text.strip(
            ) if final_price_elem and final_price_elem.text.strip() else None

            link = item['href']

            if not discount or not final_price or not original_price:
                continue

            try:
                discount_value = int(discount.replace(
                    '%', '').replace('-', '').strip())
                original_price_value = float(
                    original_price.replace('$', '').replace(',', '').strip())
            except ValueError:
                continue  # skip if parsing fails

            app_id = extract_appid_from_link(link)
            if not app_id:
                continue

            print(f"Processing {title} (AppID: {app_id})")
            reviews = fetch_steam_reviews(app_id)
            print(f"Reviews fetched: {reviews}")
            time.sleep(0.1)  # polite delay

            if not reviews:
                continue

            # Good deals filter
            if reviews['review_count'] >= 3500 and \
                    reviews['review_summary'] in ['Very Positive', 'Overwhelmingly Positive'] and \
                    discount_value >= 50 and original_price_value > 30:
                good_deals.append({
                    'title': title,
                    'discount': discount,
                    'original_price': original_price,
                    'final_price': final_price,
                    'review_count': reviews['review_count'],
                    'review_summary': reviews['review_summary'],
                    'link': link
                })

            # Bad deals filter
            if reviews['review_count'] >= 10000 and \
                    reviews['review_summary'] in ['Mixed', 'Mostly Negative'] and \
                    discount_value >= 70 and original_price_value > 30:
                bad_deals.append({
                    'title': title,
                    'discount': discount,
                    'original_price': original_price,
                    'final_price': final_price,
                    'review_count': reviews['review_count'],
                    'review_summary': reviews['review_summary'],
                    'link': link
                })

    # Determine scraper failure: if we found no games at all on either page
    if total_games_found == 0:
        print("No games scraped at all — possible scraper failure.")
        return {"fetch_failed": True}

    return {'good_deals': good_deals, 'bad_deals': bad_deals}


def extract_appid_from_link(link):
    match = re.search(r'/app/(\d+)/', link)
    return int(match.group(1)) if match else None


def fetch_steam_deals_with_retries(max_retries=3, delay=5):
    for attempt in range(1, max_retries + 1):
        print(f"Attempt {attempt} to fetch Steam deals...")
        result = fetch_steam_deals()
        if not result.get("fetch_failed"):
            return result
        print(f"Fetch failed, retrying in {delay} seconds...")
        time.sleep(delay)
    print("All retries failed — returning empty result.")
    return {"good_deals": [], "bad_deals": []}
