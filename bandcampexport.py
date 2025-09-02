from playwright.sync_api import sync_playwright, TimeoutError
from bs4 import BeautifulSoup
import requests
import json
import time


# ================= CONFIG =================
USERNAME = "YOUR_USERNAME"

# get these cookies by logging into bandcamp and inspecting your browser cookies for "identity" and "session" never share these with anyone else
# they also expire after a while so you may need to update them periodically
COOKIES = [
    {"name": "identity", "value": "YOUR_IDENTITY_COOKIE", "domain": ".bandcamp.com", "path": "/"},
    {"name": "session", "value": "YOUR_SESSION_COOKIE", "domain": ".bandcamp.com", "path": "/"}
]
#see instructions below on how to get these 
GITHUB_TOKEN = "YOUR_GITHUB_TOKEN"
GIST_ID = None #YOUR GIST ID if you made one already otherwise leave as None and the script will create a new gist for you (i think)
GIST_FILENAME = "bandcamp_collection.json"

HEADLESS = False        # set to True if you don't need to see the browser (currently not working)
SCROLL_PAUSE_MS = 600  
MAX_STAGNANT_CYCLES = 2 
MAX_LOOPS = 50 

def get_collection_html(username, cookies):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        context.add_cookies(cookies)
        page = context.new_page()
        page.goto(f"https://bandcamp.com/{username}")
        page.wait_for_load_state("networkidle")

        try:
            btn = page.query_selector("text=Accept all")
            if btn:
                print("Clicking 'Accept all' on cookie banner...")
                btn.click()
                page.wait_for_timeout(1000)
        except:
            print("No cookie banner found or already accepted.")

        try:
            show_more_btn = page.query_selector("button.show-more")
            if show_more_btn:
                print("Clicking 'view all' to load all albums...")
                show_more_btn.click()
                page.wait_for_timeout(2000)  
        except:
            print("No 'view all' button found.")

        html = page.content()
        browser.close()
        print("Browser closed.")
        return html

def scrape_collection(username, cookies):
    html = get_collection_html(username, cookies)
    soup = BeautifulSoup(html, "html.parser")
    collection = []

    for item in soup.select("div.collection-item-gallery-container"):
        link_tag = item.select_one("a.item-link")
        if not link_tag:
            continue
        link = link_tag.get("href", "").strip()
        title_tag = link_tag.select_one("div.collection-item-title")
        if title_tag:
            title = title_tag.get_text(strip=True).replace("(gift given)", "").strip()
        else:
            title = ""

        art_tag = item.select_one("a.track_play_auxiliary img.collection-item-art")
        artwork = art_tag["src"] if art_tag else ""

        collection.append({
            "title": title,
            "link": link,
            "artwork": artwork
        })
        print(f"Scraped: {title}")

    return collection

def upload_to_gist(collection, token, gist_id, filename):
    headers = {"Authorization": f"token {token}"}
    data = {
        "files": {
            filename: {"content": json.dumps(collection, indent=4)}
        }
    }
    url = f"https://api.github.com/gists/{gist_id}"
    response = requests.patch(url, headers=headers, json=data)
    response.raise_for_status()
    print(f"Gist updated: {response.json()['html_url']}")
    return response.json()['html_url']

if __name__ == "__main__":
    print("Scraping Bandcamp collection...")
    collection = scrape_collection(USERNAME, COOKIES)
    print(f"Total albums scraped: {len(collection)}")
    print("Uploading collection to GitHub Gist...")
    gist_url = upload_to_gist(collection, GITHUB_TOKEN, GIST_ID, GIST_FILENAME)
    print(f"Done! Gist URL: {gist_url}")
    input("Press Enter to exit...")




#notes:
#honestly making it open a visible browser sucks but headless mode seems to have issues loading all items sometimes
#a more proper way of storing github token would be using environment variables, change "GITHUB_TOKEN = "TOKEN_HERE"" to "GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")" and 
# set the environment variable accordingly through powershell with setx GITHUB_TOKEN "your_actual_token_here" so your computer always sees "GITHUB_TOKEN" as your token
#i didnt implement this because im lazy 

