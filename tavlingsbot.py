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
        "content": f"🎉 **Ny Instagram-tävling på svenska!**\n**{title}**\n{url}"
    }
    try:
        requests.post(DISCORD_WEBHOOK_URL, json=data)
    except Exception as e:
        print(f"Fel vid skickande till Discord: {e}")

def search_competitions():
    seen = load_seen()
    
    # Sökfrågor som enbart letar efter Instagram-tävlingar på svenska (helt utan Facebook)
    queries = [
        "site:instagram.com tävling",
        "site:instagram.com vinn",
        "site:instagram.com utlottning"
    ]
    
    new_competitions = []

    with DDGS() as ddgs:
        for query in queries:
            try:
                # Sök på svenska (se-sv)
                results = ddgs.text(query, region="se-sv", max_results=10)
                for r in results:
                    title = r.get("title", "")
                    url = r.get("href", "")
                    
                    # Kontrollera att det är Instagram och att länken är unik
                    if url and url not in seen:
                        # Extra säkerhetskoll: Undvik Facebook helt
                        if "facebook.com" not in url.lower():
                            seen.add(url)
                            save_seen_url(url)
                            new_competitions.append({"title": title, "url": url})
            except Exception as e:
                print(f"Fel vid sökning: {e}")

    return new_competitions

if __name__ == "__main__":
    print("Boten startad! Letar endast efter svenska Instagram-tävlingar...")
    while True:
        tavlingar = search_competitions()
        for t in tavlingar:
            send_to_discord(t["title"], t["url"])
        
        # Vänta 1 timme innan nästa sökning
        time.sleep(3600)