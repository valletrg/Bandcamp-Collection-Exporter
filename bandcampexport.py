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
# =========================================

def get_full_page_html(username, cookies):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        page.context.add_cookies(cookies)

        page.goto(f"https://bandcamp.com/{username}")

        page.wait_for_selector(".collection-item-gallery-container", timeout=10000)

        while True:
            show_more_btns = page.query_selector_all("div.expand-container.show-button button.show-more")
            if not show_more_btns:
                break
            for btn in show_more_btns:
                try:
                    btn.scroll_into_view_if_needed()
                    btn.click()
                    time.sleep(1)  # wait for new items to load
                except:
                    pass
            # scroll to bottom to trigger lazy loading
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(1)

        html = page.content()
        browser.close()
        print("Browser closed")  # visual confirmation
        return html

def scrape_collection(username, cookies):
    html = get_full_page_html(username, cookies)
    soup = BeautifulSoup(html, "html.parser")
    containers = soup.select(".collection-item-gallery-container")

    albums = []
    for idx, c in enumerate(containers, 1):
        title_el = c.select_one(".collection-item-title")
        link_el = c.select_one(".collection-title-details a.item-link")
        img_el = c.select_one(".track_play_auxiliary img.collection-item-art")
        if title_el and link_el and img_el:
            albums.append({
                "title": title_el.get_text(strip=True),
                "link": link_el.get("href"),
                "artwork": img_el.get("src")
            })
        print(f"Processed album {idx}/{len(containers)}")  # progress

    return albums

def upload_to_gist(data, token, gist_id):
    headers = {"Authorization": f"token {token}"}
    payload = {
        "files": {"bandcamp_collection.json": {"content": json.dumps(data, indent=2)}},
        "description": "Bandcamp collection",
        "public": True
    }
    url = f"https://api.github.com/gists/{gist_id}"
    r = requests.patch(url, headers=headers, json=payload)
    r.raise_for_status()
    return r.json()

if __name__ == "__main__":
    collection = scrape_collection(USERNAME, COOKIES)
    print(f"Scraped {len(collection)} albums.")
    gist_data = upload_to_gist(collection, GITHUB_TOKEN, GIST_ID)
    print("Gist updated")
    print(f"View your Gist at: {gist_data['html_url']}")





#notes:
#honestly making it open a visible browser sucks but headless mode seems to have issues loading all items sometimes
#a more proper way of storing github token would be using environment variables, change "GITHUB_TOKEN = "TOKEN_HERE"" to "GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")" and 
# set the environment variable accordingly through powershell with setx GITHUB_TOKEN "your_actual_token_here" so your computer always sees "GITHUB_TOKEN" as your token
#i didnt implement this because im lazy 
