import time
import os
from urllib.parse import urlparse
from duckduckgo_search import DDGS
import requests

DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1568796481534558268/mW3Drv34lX8eY_SK4FmOMRAeapWmhV2d2alI7FhdYTFoUJ7_BT4WPPDP_dQ7pH87wyzS"
SEEN_FILE = "hittade_tavlingar.txt"

def load_seen():
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE, "r", encoding="utf-8") as f:
            return set(line.strip() for line in f)
    return set()

def save_seen_url(url):
    with open(SEEN_FILE, "a", encoding="utf-8") as f:
        f.write(url + "\n")

def send_to_discord(title, url):
    data = {
        "content": f"🎉 **Svensk Instagram-tävling!**\n**{title}**\n{url}"
    }
    try:
        requests.post(DISCORD_WEBHOOK_URL, json=data)
    except Exception as e:
        print(f"Fel vid skickande till Discord: {e}")

def is_valid_instagram_url(url):
    try:
        parsed = urlparse(url.lower())
        domain = parsed.netloc
        
        if domain not in ["instagram.com", "www.instagram.com"]:
            return False
            
        path = parsed.path
        if any(path.startswith(prefix) for prefix in ["/p/", "/reel/", "/tv/"]):
            return True
            
        return False
    except Exception:
        return False

def is_swedish_content(title):
    title_lower = title.lower()
    
    english_indicators = [
        "giveaway alert", "enter to win", "worldwide", "international giveaway",
        "rules to enter", "winner will be", "tag a friend to win", "free entry",
        "congratulations to", "how to enter", "open worldwide", "link in bio to enter"
    ]
    for eng in english_indicators:
        if eng in title_lower:
            return False
            
    swedish_words = ["tävling", "utlottning", "tävla", "vinn", "vinst", "grattis", "sverige"]
    if any(word in title_lower for word in swedish_words):
        return True
        
    return False

def search_competitions():
    seen = load_seen()
    queries = [
        "site:instagram.com/p/ tävling efter:2026-11-01 Sverige",
        "site:instagram.com/reel/ utlottning efter:2026-11-01 Sverige",
        "site:instagram.com/p/ \"tävla och vinn\" efter:2026-11-01 Sverige",
        "site:instagram.com/reel/ \"vinn\" efter:2026-11-01 Sverige"
    ]
    new_competitions = []

    with DDGS() as ddgs:
        for query in queries:
            try:
                results = ddgs.text(query, region="se-sv", max_results=30)
                for r in results:
                    title = r.get("title", "")
                    url = r.get("href", "")
                    
                    if not url or url in seen:
                        continue
                    
                    if not is_valid_instagram_url(url):
                        continue
                        
                    if not is_swedish_content(title):
                        continue
                        
                    seen.add(url)
                    save_seen_url(url)
                    new_competitions.append({"title": title, "url": url})
            except Exception as e:
                print(f"Fel vid sökning: {e}")

    return new_competitions

if __name__ == "__main__":
    print("Boten startad! Söker kontinuerligt efter svenska Instagram-tävlingar...")
    while True:
        tavlingar = search_competitions()
        for t in tavlingar:
            send_to_discord(t["title"], t["url"])
            time.sleep(1)
        time.sleep(15)
