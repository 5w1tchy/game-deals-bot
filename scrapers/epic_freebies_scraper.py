import requests

EPIC_FREE_GAMES_URL = "https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions?locale=en-US"


def fetch_epic_freebies():
    freebies = []
    response = requests.get(EPIC_FREE_GAMES_URL, headers={
        "User-Agent": "Mozilla/5.0"
    })

    if response.status_code != 200:
        print(f"Failed to fetch free games (status: {response.status_code})")
        return freebies

    data = response.json()
    elements = data.get("data", {}).get("Catalog", {}).get(
        "searchStore", {}).get("elements", [])

    for element in elements:
        promotions = element.get("promotions")
        if not promotions or not promotions.get("promotionalOffers"):
            continue

        current_offers = promotions.get("promotionalOffers")
        if not current_offers:
            continue

        title = element.get("title", "Unknown Title")
        slug = element.get("productSlug") or element.get("urlSlug")

        # Build working link using offerMappings if possible
        offer_mappings = element.get("offerMappings", [])
        if offer_mappings:
            mapping_page_slug = offer_mappings[0].get("pageSlug")
            if mapping_page_slug:
                link = f"https://store.epicgames.com/en-US/p/{mapping_page_slug}"
            else:
                link = f"https://store.epicgames.com/en-US/p/{slug}"
        else:
            link = f"https://store.epicgames.com/en-US/p/{slug}"

        image = None
        key_images = element.get("keyImages", [])
        for img in key_images:
            if img.get("type") == "DieselStoreFrontWide":
                image = img.get("url")
                break
        if not image and key_images:
            image = key_images[0].get("url")

        # Add description and price
        description = element.get("description") or "No description available."
        price = element.get("price", {}).get("totalPrice", {}).get(
            "fmtPrice", {}).get("originalPrice")

        freebies.append({
            "title": title,
            "link": link,
            "image": image,
            "description": description.strip(),
            "price": price or "Not listed"
        })

    return freebies
