import os
import requests
import mysql.connector
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from alerts import send_email
from urllib.parse import urlparse

load_dotenv()
HEADERS = {"User-Agent": "Mozilla/5.0 (PriceRadar student project)"}


def get_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
    )


SITE_SELECTORS = {
    "books.toscrape.com": {"name": "h1", "price": "p.price_color"},
    "webscraper.io": {"name": "h4.title", "price": 'span[itemprop="price"]'},
}

def fetch_product(url):
    domain = urlparse(url).netloc
    sel = SITE_SELECTORS.get(domain)
    if sel is None:
        raise ValueError(f"{domain} ke selectors set nahi hain")

    resp = requests.get(url, headers=HEADERS, timeout=10)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    name_tag = soup.select_one(sel["name"])
    price_tag = soup.select_one(sel["price"])
    if name_tag is None or price_tag is None:
        raise ValueError("Naam ya price page par nahi mila (selector galat ho sakta hai)")

    name = name_tag.get_text(strip=True)
    price_text = price_tag.get_text()
    price = float("".join(c for c in price_text if c.isdigit() or c == "."))
    return name, price


def save_price(url, name, price):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT id, current_price, lowest_price FROM products WHERE url = %s", (url,))
    row = cur.fetchone()

    if row is None:
        cur.execute(
            "INSERT INTO products (url, name, current_price, lowest_price, last_checked) "
            "VALUES (%s, %s, %s, %s, NOW())",
            (url, name, price, price),
        )
        product_id = cur.lastrowid
        cur.execute("INSERT INTO price_history (product_id, price) VALUES (%s, %s)", (product_id, price))
        print(f"Naya product add hua: {name} - {price}")
    else:
        product_id, old_price, lowest = row
        lowest = min(float(lowest), price)
        cur.execute(
            "UPDATE products SET current_price=%s, lowest_price=%s, last_checked=NOW() WHERE id=%s",
            (price, lowest, product_id),
        )
        # sirf tab history save karo jab price badla ho
        if float(old_price) != price:
            cur.execute("INSERT INTO price_history (product_id, price) VALUES (%s, %s)", (product_id, price))
            print(f"Price badla: {old_price} -> {price}")
        else:
            print("Price same hai, history save nahi ki.")

    conn.commit()
    cur.close()
    conn.close()


import time
import random

def get_urls():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT url FROM products WHERE is_active = 1")
    urls = [row[0] for row in cur.fetchall()]
    cur.close()
    conn.close()
    return urls

def check_alert(url):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, name, current_price, target_price, alert_sent "
        "FROM products WHERE url = %s",
        (url,),
    )
    row = cur.fetchone()
    if row is None:
        cur.close()
        conn.close()
        return

    product_id, name, price, target, alert_sent = row

    if target is not None and float(price) <= float(target):
        if alert_sent == 0:
            send_email(
                f"Price Drop: {name}",
                f"{name} ab sirf {price} mein mil raha hai.\n"
                f"Aapka target price {target} tha.\n\n"
                f"Link: {url}",
            )
            cur.execute("UPDATE products SET alert_sent = 1 WHERE id = %s", (product_id,))
    else:
        # price wapas upar chala gaya, to agli baar phir alert bhej sakein
        cur.execute("UPDATE products SET alert_sent = 0 WHERE id = %s", (product_id,))

    conn.commit()
    cur.close()
    conn.close()

def check_all():
    for url in get_urls():
        try:
            name, price = fetch_product(url)
            save_price(url, name, price)
            check_alert(url)
        except Exception as e:
            print(f"Error aaya {url} par: {e}")
        time.sleep(random.uniform(1, 3))  # sites ko tang na karne ke liye delay


import schedule


def run_scheduler():
    print("PriceRadar chalu ho gaya. Band karne ke liye Ctrl + C dabao.")
    check_all()  # shuru mein ek baar turant check karo
    schedule.every(3).hours.do(check_all)

    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    run_scheduler()