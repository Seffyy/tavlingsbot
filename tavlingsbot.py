import time
import requests
from datetime import datetime
from duckduckgo_search import DDGS

# Din Discord Webhook
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1568796481534558268/mW3Drv34lX8eY_SK4FmOMRAeapWmhV2d2alI7FhdYTFoUJ7_BT4WPPDP_dQ7pH87wyzS"

SEEN_FILE = "hittade_tavlingar.txt"

def load_seen_urls():
    try:
        with open(SEEN_FILE, "r", encoding="utf-8") as f:
            return set(line.strip() for line in f if line.strip())
    except FileNotFoundError:
        return set()

def save_seen_url(url):
    with open(SEEN_FILE, "a", encoding="utf-8") as f:
        f.write(url + "\n")

def search_competitions():
    queries = [
        "site:instagram.com tävling Örebro vinn",
        "site:instagram.com utlottning gilla dela tävla",
        "site:instagram.com tävling presentkort Sverige",
        "tävlingar pågående vinn biobiljetter presentkort",
        "vinn ica coop city gross tävling"
    ]
    
    seen_urls = load_seen_urls()
    new_competitions = []

    print("Söker igenom webben efter aktiva tävlingar...")
    
    try:
        with DDGS() as ddgs:
            for query in queries:
                results = ddgs.text(query, max_results=8)
                if results:
                    for r in results:
                        title = r.get('title', 'Aktiv tävling')
                        url = r.get('href', '')
                        
                        if url and "facebook.com" not in url and url not in seen_urls:
                            seen_urls.add(url)
                            save_seen_url(url)
                            new_competitions.append({"title": title, "url": url})
    except Exception as e:
        print(f"Fel vid sökning: {e}")

    return new_competitions

def run_bot():
    comps = search_competitions()
    today = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    if comps:
        print(f"Hittade {len(comps)} nya tävlingar! Skickar till Discord...")
        for c in comps:
            content = f"🎁 **NY TÄVLING HITTAD ({today})**\n**{c['title']}**\n🔗 {c['url']}"
            requests.post(DISCORD_WEBHOOK_URL, json={"content": content})
            time.sleep(1)
    else:
        print("Inga nya tävlingar hittades vid denna sökning.")

if __name__ == "__main__":
    print("Tävlingsboten är startad och kör kontinuerligt!")
    run_bot()
    
    while True:
        print("\nVäntar 5 minuter till nästa sökning...")
        time.sleep(300)
        run_bot()