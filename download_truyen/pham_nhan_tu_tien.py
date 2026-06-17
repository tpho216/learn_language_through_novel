import os
import time
import requests
from playwright.sync_api import sync_playwright

START_EPISODE = 1
END_EPISODE = 359

PAGE_URL = "https://nhattruyen.one/pham-nhan-tu-tien-lat-radio"

DOWNLOAD_DIR = "pham_nhan_tu_tien"

os.makedirs(DOWNLOAD_DIR, exist_ok=True)

dl_session = requests.Session()
dl_session.headers.update({
    "User-Agent": "Mozilla/5.0"
})


def download_file(url, filepath, page=None):
    """Download url to filepath. Uses page.request for CDN URLs that need browser cookies."""
    cdn_hosts = ("cdn.nhattruyen.one", "cdn2.nhattruyen.one")
    use_browser = page is not None and any(h in url for h in cdn_hosts)
    try:
        if use_browser:
            resp = page.request.get(url, timeout=120000)
            if not resp.ok:
                raise Exception(f"HTTP {resp.status} from browser request")
            data = resp.body()
            with open(filepath, "wb") as f:
                f.write(data)
            print(f"  Downloaded (browser): {os.path.basename(filepath)} ({len(data) / 1024 / 1024:.1f} MB)")
        else:
            with dl_session.get(url, stream=True, timeout=120) as r:
                r.raise_for_status()
                total = 0
                with open(filepath, "wb") as f:
                    for chunk in r.iter_content(chunk_size=1024 * 1024):
                        if chunk:
                            f.write(chunk)
                            total += len(chunk)
            print(f"  Downloaded: {os.path.basename(filepath)} ({total / 1024 / 1024:.1f} MB)")
    except Exception as e:
        print(f"  Failed download {filepath}: {e}")


def get_episode_url(page, items, episode):
    """Click an episode and return the best available audio URL.

    Prefers archive.org (downloadable without auth). If archive.org
    never appears within the timeout, falls back to the audio element src
    (which may be a CDN URL that needs browser cookies to download).
    """
    idx = episode - 1
    archive_urls = []

    def on_request(req):
        url = req.url
        if ".mp3" in url and "archive.org" in url:
            archive_urls.append(url)

    page.on("request", on_request)
    try:
        items[idx].click()

        # Wait up to 10 s for an archive.org URL
        deadline = time.time() + 10
        while time.time() < deadline and not archive_urls:
            time.sleep(0.3)

        if archive_urls:
            return archive_urls[0]

        # Fallback: whatever the audio element ended up with (may be CDN)
        audio_el = page.query_selector("audio")
        return audio_el.get_attribute("src") if audio_el else None
    finally:
        page.remove_listener("request", on_request)


with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    print("Loading playlist page...")
    page.goto(PAGE_URL, wait_until="networkidle", timeout=60000)
    time.sleep(2)

    items = page.query_selector_all(".jp-playlist li")
    print(f"Found {len(items)} episodes in playlist")

    for episode in range(START_EPISODE, END_EPISODE + 1):
        filename = f"Phàm Nhân Tu Tiên - Tập {episode}.mp3"
        filepath = os.path.join(DOWNLOAD_DIR, filename)

        if os.path.exists(filepath):
            print(f"[{episode}] Already exists, skipping.")
            continue

        if episode - 1 >= len(items):
            print(f"[{episode}] Index out of range ({len(items)} items)")
            continue

        print(f"\n[{episode}] Clicking playlist item...")
        try:
            audio_url = get_episode_url(page, items, episode)
            if not audio_url:
                print(f"[{episode}] No audio URL found")
                continue

            print(f"[{episode}] URL: {audio_url}")
            download_file(audio_url, filepath, page=page)

        except Exception as e:
            print(f"[{episode}] Error: {e}")

    browser.close()

print("\nDone.")