import os
import time
import random
import datetime
import pandas as pd
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import WebDriverException, ElementClickInterceptedException
HEADLESS = False            
PAGES_TO_SCRAPE = 3        
QUERY = "laptops"
MAX_RETRIES = 4
OUT_FOLDER = "outputs"
DEBUG_FOLDER = "debug_html"

def make_driver(headless=HEADLESS):
    opts = Options()
    if headless:
        opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_argument("--disable-infobars")
    opts.add_argument("--window-size=1200,900")
    opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    opts.add_experimental_option("useAutomationExtension", False)
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=opts)
    try:
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            """
        })
    except Exception:
        pass

    return driver
def safe_click_if_exists(driver, selectors):
    """
    Try to click the first element found from the list of selectors.
    selectors: list of (by, value) pairs but we use CSS selectors here for simplicity.
    """
    for sel in selectors:
        try:
            el = driver.find_element("css selector", sel)
            if el:
                try:
                    el.click()
                    time.sleep(0.8 + random.random())
                    print(f"Clicked element {sel}")
                    return True
                except ElementClickInterceptedException:
                    try:
                        driver.execute_script("arguments[0].click();", el)
                        time.sleep(0.5)
                        print(f"Script-clicked element {sel}")
                        return True
                    except Exception:
                        pass
        except Exception:
            continue
    return False
def warm_up_session(driver):
    try:
        print("Warming up session by visiting amazon.in homepage...")
        driver.get("https://www.amazon.in")
        time.sleep(2.0 + random.random())
        for _ in range(2):
            driver.execute_script("window.scrollBy(0, window.innerHeight * 0.35);")
            time.sleep(0.6 + random.random())
        cookie_selectors = [
            "#sp-cc-accept",                      # common accept cookies button id (if present)
            "input[name='accept']",               # generic
            "button#accept",                      # generic
            "button[aria-label='Close']",         # modal close
            "button[aria-label='Dismiss']",
            "div#nav-main .nav-sprite"            # fallback
        ]
        clicked = safe_click_if_exists(driver, cookie_selectors)
        if clicked:
            print("Tried dismissing cookie/consent modal.")
        time.sleep(1.0 + random.random())
    except Exception as e:
        print("Warm-up error:", e)
def fetch_page_with_retries(driver, query=QUERY, page=1, max_attempts=MAX_RETRIES):
    """
    Load the search results page with multiple attempts, scrolling and refreshes,
    returning (html, num_results_found)
    """
    os.makedirs(DEBUG_FOLDER, exist_ok=True)
    base = f"https://www.amazon.in/s?k={query}&page={page}"
    attempt = 0
    last_html = ""
    while attempt < max_attempts:
        attempt += 1
        print(f"[Attempt {attempt}/{max_attempts}] Loading {base}")
        try:
            driver.get(base)
        except WebDriverException as e:
            print("driver.get exception:", e)
        time.sleep(2.0 + (1.0 if attempt > 1 else 1.8) + random.random())
        scrolls = random.randint(3, 6)
        for i in range(scrolls):
            try:
                driver.execute_script("window.scrollBy(0, window.innerHeight * 0.8);")
            except Exception:
                pass
            time.sleep(0.6 + random.random())
        html = driver.page_source
        last_html = html
        soup = BeautifulSoup(html, "lxml")
        results = soup.select("div[data-component-type='s-search-result']")
        found = len(results)
        print(f"   Found {found} result containers on attempt {attempt}")
        lower = html.lower()
        blocked_signals = ("service unavailable", "503", "unusual activity", "robot", "automated", "captcha", "sorry! something went wrong")
        if found > 0:
            return html, found
        if any(sig in lower for sig in blocked_signals):
            print("   Block-like content detected (contains block keywords).")
        else:
            print("   No results found; will retry (this may be lazy-loading).")
        fname = os.path.join(DEBUG_FOLDER, f"page_{page}_attempt_{attempt}.html")
        with open(fname, "w", encoding="utf-8") as f:
            f.write(html)
        print("   Saved debug HTML:", fname)
        time.sleep(1.2 + random.random() * 1.5)
        try:
            driver.refresh()
        except Exception:
            pass
        time.sleep(0.8 + random.random())
    return last_html, 0
def parse_items_from_html(html, base_url="https://www.amazon.in"):
    soup = BeautifulSoup(html, "lxml")
    results = soup.select("div[data-component-type='s-search-result']")
    items = []
    for it in results:
        try:
            asin = it.get("data-asin") or None
            t1 = it.select_one("h2 a span")
            t2 = it.select_one("span.a-size-medium")
            t3 = it.select_one("span.a-size-base-plus")
            t4 = it.select_one("span.a-size-base.a-text-normal")
            title = None
            for t in (t1, t2, t3, t4):
                if t and t.get_text(strip=True):
                    title = t.get_text(strip=True)
                    break
            a = it.select_one("h2 a")
            prod_url = None
            if a and a.get("href"):
                prod_url = urljoin(base_url, a.get("href"))
            img = it.select_one("img.s-image")
            image = img.get("src") if img else (img.get("data-src") if img and img.get("data-src") else None)
            price = None
            p = it.select_one("span.a-offscreen")
            if p:
                price = p.get_text(strip=True).replace("₹", "").replace(",", "")
            else:
                whole = it.select_one("span.a-price-whole")
                frac = it.select_one("span.a-price-fraction")
                if whole:
                    price = whole.get_text(strip=True).replace(",", "")
                    if frac:
                        price = price + "." + frac.get_text(strip=True)
            rating = None
            r = it.select_one("span.a-icon-alt")
            if r:
                rating = r.get_text(strip=True).split()[0]
            reviews_count = None
            rev = it.select_one("span.a-size-base")
            if rev:
                txt = rev.get_text(strip=True).replace(",", "")
                if txt.isdigit():
                    reviews_count = txt
            rev_alt = it.select_one("a.a-size-small .a-size-base")
            if not reviews_count and rev_alt:
                txt2 = rev_alt.get_text(strip=True).replace(",", "")
                if txt2.isdigit():
                    reviews_count = txt2
            seller_snip = None
            seller_el = it.select_one("div.a-row.a-size-base.a-color-secondary")
            if seller_el:
                seller_snip = seller_el.get_text(" ", strip=True)
            ad_or_organic = "Ad" if it.find(string=lambda s: s and "Sponsored" in s) else "Organic"
            items.append({
                "scrape_timestamp": datetime.datetime.now().isoformat(),
                "ASIN": asin,
                "Title": title,
                "Product_URL": prod_url,
                "Image": image,
                "Price": price,
                "Rating": rating,
                "Reviews_Count": reviews_count,
                "Seller_Snippet": seller_snip,
                "Result_Type": ad_or_organic
            })
        except Exception as e:
            print("   parse item error:", e)
            continue

    return items
def save_csv(items, out_folder=OUT_FOLDER, prefix="amazon_laptops"):
    os.makedirs(out_folder, exist_ok=True)
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    fname = os.path.join(out_folder, f"{prefix}_{ts}.csv")
    df = pd.DataFrame(items)
    cols = ["scrape_timestamp", "ASIN", "Title", "Product_URL", "Image",
            "Price", "Rating", "Reviews_Count", "Seller_Snippet", "Result_Type"]
    cols = [c for c in cols if c in df.columns] + [c for c in df.columns if c not in cols]
    df.to_csv(fname, index=False, columns=cols)
    print("Saved", fname)
    return fname
# -------------------- MAIN --------------------
def main():
    driver = make_driver(headless=HEADLESS)
    all_items = []
    try:
        warm_up_session(driver)
        for p in range(1, PAGES_TO_SCRAPE + 1):
            print("\n--- Fetching page", p, "---")
            html, found_count = fetch_page_with_retries(driver, QUERY, p, MAX_RETRIES)
            if found_count > 0:
                items = parse_items_from_html(html)
                print(f"Parsed {len(items)} items from page {p}")
                all_items.extend(items)
            else:
                fallback_items = parse_items_from_html(html)
                if fallback_items:
                    print(f"Fallback parsed {len(fallback_items)} items on page {p}")
                    all_items.extend(fallback_items)
                else:
                    print(f"No items found for page {p} after retries. See debug_html/ for saved HTML.")
            time.sleep(1.5 + random.random() * 2.0)
    finally:
        try:
            driver.quit()
        except Exception:
            pass
    if all_items:
        save_csv(all_items)
    else:
        print("No items scraped overall. Inspect debug_html/ for saved HTML files.")
if __name__ == "__main__":
    main()