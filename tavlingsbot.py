import time
import os
from duckduckgo_search import DDGS
import requests

# Din Discord Webhook URL
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
        "content": f"🎉 **Svensk Instagram-tävling (Från 1 nov & framåt)!**\n**{title}**\n{url}"
    }
    try:
        requests.post(DISCORD_WEBHOOK_URL, json=data)
    except Exception as e:
        print(f"Fel vid skickande till Discord: {e}")

def search_competitions():
    seen = load_seen()
    
    # Sökfrågor låsta till 1 november 2026 och framåt
    queries = [
        "site:instagram.com tävling efter:2026-11-01",
        "site:instagram.com utlottning efter:2026-11-01",
        "site:instagram.com \"tävla och vinn\" efter:2026-11-01",
        "site:instagram.com giveaway Sverige efter:2026-11-01",
        "site:instagram.com \"vinn\" efter:2026-11-01"
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
                    
                    url_lower = url.lower()
                    
                    # KRÄVER Instagram och blockerar allt annat stenhårt
                    if "instagram.com" not in url_lower:
                        continue
                        
                    if "facebook.com" in url_lower or "youtube.com" in url_lower or "youtu.be" in url_lower:
                        continue
                        
                    seen.add(url)
                    save_seen_url(url)
                    new_competitions.append({"title": title, "url": url})
                    
            except Exception as e:
                print(f"Fel vid sökning: {e}")

    return new_competitions

if __name__ == "__main__":
    print("Boten startad! Hämtar tävlingar från 1 nov 2026 och alla helt nya framåt...")
    while True:
        tavlingar = search_competitions()
        for t in tavlingar:
            send_to_discord(t["title"], t["url"])
            time.sleep(1)
        
        # Söker om var 10:e minut för att fånga nya direkt när de läggs ut
        time.sleep(600)