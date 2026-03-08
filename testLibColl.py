import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re

BASE_URL = "https://library.iitmandi.ac.in/os/ebk/publisherssearch.php?page="
QUERY = "&kwdd=Springer"
TEST_PAGE = 76

HEADERS = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64)"}
session = requests.Session()
session.headers.update(HEADERS)

def extract_biblio(text):
    match = re.search(r'\b\d{5}\b', text)
    return int(match.group()) if match else None

# Fetch page
url = f"{BASE_URL}{TEST_PAGE}{QUERY}"
r = session.get(url)
soup = BeautifulSoup(r.text, "html.parser")

rows = soup.find_all("tr")
biblio_rows = []

for row in rows:
    text = row.get_text(" ", strip=True)
    biblio = extract_biblio(text)
    link = row.find("a")
    if biblio and link:
        biblio_rows.append((biblio, link.text.strip()))

# Sort by Biblio
biblio_rows.sort(key=lambda x: x[0])

# Print sequential check
for biblio, title in biblio_rows:
    print(f"Biblio {biblio} → Title: {title}")


"""

Final complete level of test and understanding , Testing for LibColl.py and we can see here 
"""
