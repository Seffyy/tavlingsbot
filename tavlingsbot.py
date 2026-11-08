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
        "content": f"🎉 **Aktiv / Ny svensk Instagram-tävling!**\n**{title}**\n{url}"
    }
    try:
        requests.post(DISCORD_WEBHOOK_URL, json=data)
    except Exception as e:
        print(f"Fel vid skickande till Discord: {e}")

def search_competitions():
    seen = load_seen()
    
    # Sökfrågor som siktar på svenska Instagram-tävlingar från 1 nov 2026
    queries = [
        "site:instagram.com tävling efter:2026-11-01",
        "site:instagram.com utlottning efter:2026-11-01",
        "site:instagram.com \"tävla och vinn\" efter:2026-11-01",
        "site:instagram.com giveaway Sverige efter:2026-11-01",
        "site:instagram.com \"vinn\" Sverige efter:2026-11-01"
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
                    
                    # 1. STENHÅRT KRAV: Länken MÅSTE vara en ren Instagram-länk
                    if not ("instagram.com/p/" in url_lower or "instagram.com/reel/" in url_lower or "instagram.com/" in url_lower):
                        continue
                    
                    # 2. BLOCKERA EXPLICIT allt annat som inte hör hemma (LinkedIn, Facebook, YouTube m.m.)
                    blocked_domains = ["linkedin.com", "facebook.com", "youtube.com", "youtu.be", "twitter.com", "x.com"]
                    if any(domain in url_lower for domain in blocked_domains):
                        continue
                        
                    seen.add(url)
                    save_seen_url(url)
                    new_competitions.append({"title": title, "url": url})
                    
            except Exception as e:
                print(f"Fel vid sökning: {e}")

    return new_competitions

if __name__ == "__main__":
    print("Boten startad! Filtrerar 100% enbart renodlade Instagram-länkar (från 1 nov & framåt)...")
    while True:
        tavlingar = search_competitions()
        for t in tavlingar:
            send_to_discord(t["title"], t["url"])
            time.sleep(1)
        
        # Söker på nytt var 10:e minut
        time.sleep(600)