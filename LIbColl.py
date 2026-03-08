import os
import time
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

BASE_URL = "https://library.iitmandi.ac.in/os/ebk/publisherssearch.php?page="
QUERY = "&kwdd=Springer"

START_PAGE = 76
END_PAGE = 1326

DOWNLOAD_FOLDER = "/home/honcho/PersBund"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64)"
}

session = requests.Session()
session.headers.update(HEADERS)


def clean_filename(name):
    bad = ['\\','/','*','?','"','<','>','|',':']
    for b in bad:
        name = name.replace(b, "")
    return name.strip()


def safe_request(url, retries=3):
    for _ in range(retries):
        try:
            r = session.get(url, timeout=30)
            if r.status_code == 200:
                return r
        except:
            pass
        time.sleep(2)
    return None


def extract_biblio(row_text):
    match = re.search(r'\b\d{5}\b', row_text)
    if match:
        return int(match.group())
    return None


def download_file(url, title, biblio):

    filename = f"{biblio}_{clean_filename(title)}.pdf"
    path = os.path.join(DOWNLOAD_FOLDER, filename)

    if os.path.exists(path):
        print(f"✓ Already exists [{biblio}] :", filename)
        return

    try:
        r = session.get(url, stream=True, timeout=60)

        if r.status_code != 200:
            print("✖ Bad response:", url)
            return

        print(f"⬇ Downloading [{biblio}] :", filename)

        with open(path, "wb") as f:
            for chunk in r.iter_content(8192):
                if chunk:
                    f.write(chunk)

        print("✔ Saved:", filename)

    except Exception as e:
        print("✖ Download failed:", e)


for page in range(START_PAGE, END_PAGE + 1):

    page_url = f"{BASE_URL}{page}{QUERY}"
    print(f"\n=========== PAGE {page} ===========")

    response = safe_request(page_url)

    if not response:
        print("Page failed")
        continue

    soup = BeautifulSoup(response.text, "html.parser")

    rows = soup.find_all("tr")

    page_books = []

    # Collect all biblio rows
    for row in rows:

        text = row.get_text(" ", strip=True)
        biblio = extract_biblio(text)

        link = row.find("a")

        if biblio and link:
            page_books.append((biblio, link))

    # Sort by biblio
    page_books.sort(key=lambda x: x[0])

    # Process each book sequentially
    for biblio, link in page_books:

        title = link.text.strip()

        detail_url = urljoin(page_url, link.get("href"))

        print(f"\nChecking Biblio {biblio}")
        print("Title:", title)

        detail_response = safe_request(detail_url)

        if not detail_response:
            print("Detail page error")
            continue

        detail_soup = BeautifulSoup(detail_response.text, "html.parser")

        pdf_link = None

        for a in detail_soup.find_all("a", href=True):
            if ".pdf" in a["href"].lower():
                pdf_link = urljoin(detail_url, a["href"])
                break

        if pdf_link:
            download_file(pdf_link, title, biblio)
        else:
            print("No PDF found")

        time.sleep(1)

    print(f"\n✔ Completed PAGE {page}")

    time.sleep(2)


print("\n✔ ALL PAGES FINISHED")
