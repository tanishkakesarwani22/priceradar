# 📡 PriceRadar: Price Tracker and Deal Alert System

PriceRadar tracks product prices automatically, stores the price history in MySQL, shows trends on a dashboard, and sends an email alert when a price drops to the target.

## Features
- Scrapes product name and price using Python (requests + BeautifulSoup)
- Tracks multiple products with a random delay between requests
- Saves price history only when the price changes
- Runs automatically on a schedule (every 3 hours)
- Sends an email alert when price <= target price
- Prevents duplicate alerts using an `alert_sent` flag
- Streamlit dashboard with a product table, metrics, and a price history chart
- Add new products from the dashboard with a target price (no code editing needed)
- Chart shows the target price as a horizontal line
- Pause or resume tracking for any product from the dashboard (history is kept)
- Multi-site support: each website's selectors are kept in a `SITE_SELECTORS` config, so a new site needs one new line, not new code


## Tech Stack
Python, MySQL (XAMPP), BeautifulSoup, pandas, Streamlit, smtplib, schedule

## Database
- `products`: url, name, current_price, lowest_price, target_price, alert_sent
- `price_history`: product_id, price, checked_at (indexed on product_id + checked_at)

## How to Run
1. Start MySQL in XAMPP and create the database using the SQL in `db/schema.sql`
2. Create a virtual environment and install the libraries:
   `pip install -r requirements.txt`
3. Create a `.env` file:
   ```
   DB_HOST=localhost
   DB_USER=root
   DB_PASSWORD=
   DB_NAME=priceradar
   EMAIL_SENDER=your_email@gmail.com
   EMAIL_PASSWORD=your_gmail_app_password
   EMAIL_RECEIVER=your_email@gmail.com

4. Start the tracker: `python scraper.py`
5. Start the dashboard: `streamlit run dashboard.py`

## Notes
- The practice site `books.toscrape.com` is used because it is built for scraping practice.
- Price history shown in the dashboard is partly **simulated demo data**, since the practice site's prices do not change.
- Secrets are stored in `.env`, which is excluded from Git.
- Supported sites: `books.toscrape.com` and `webscraper.io/test-sites` (both built for scraping practice)

## Screenshots
![Dashboard](screenshots/dashboard.png)
![Email alert](screenshots/email.jpeg)

## What I Learned
Web scraping, MySQL schema design and indexing, scheduling, SMTP email, duplicate-alert prevention, and building dashboards with Streamlit.

## Author
[Tanishka] | [GitHub:https://github.com/t
anishkakesarwani22]