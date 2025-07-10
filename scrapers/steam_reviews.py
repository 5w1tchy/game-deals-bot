def fetch_steam_reviews(appid):
    import requests

    url = f"https://store.steampowered.com/appreviews/{appid}?json=1&language=english"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f"Failed to fetch reviews for app ID {appid}")
        return None

    data = response.json()
    query_summary = data.get('query_summary')
    if not query_summary:
        print(f"No review summary found for app ID {appid}")
        return None

    return {
        'review_count': query_summary.get('total_reviews', 0),
        'review_summary': query_summary.get('review_score_desc', 'No summary available'),
    }
