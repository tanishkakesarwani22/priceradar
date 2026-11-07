import requests
from bs4 import BeautifulSoup

url = "https://webscraper.io/test-sites/e-commerce/static/product/32"
html = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10).text
soup = BeautifulSoup(html, "html.parser")

for sel in ['[itemprop="name"]', "h4", "h4.title", "h4.price", 'span[itemprop="price"]', "h1"]:
    found = [t.get_text(strip=True) for t in soup.select(sel)]
    print(sel, "->", found)