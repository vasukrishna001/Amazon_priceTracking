import csv
import os
import time
import requests
import smtplib
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

# ===================== CONFIGURATION ===================== #
csv_file = "wishlisted.csv"      # Input CSV with "URL" column
LOG_CSV = "prices_log.csv"       # Output CSV to log daily price checks
SENDER_EMAIL = "example@gmail.com"
RECIPIENT_EMAIL = "example@gmail.com"
APP_PASSWORD = os.getenv('GMAIL_APP_PASSWORD')  # Gmail app password from environment variable
# ========================================================= #


def read_wishlist(csv_file="wishlisted.csv"):
    """Read a CSV file containing a column named 'URL', return a list of URLs."""
    urls = []
    try:
        # Use "utf-8-sig" to handle possible BOM
        with open(csv_file, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                # 'row' is a dict, key must match header exactly: "URL"
                urls.append(row["URL"].strip())
    except FileNotFoundError:
        print(f"ERROR: The file '{csv_file}' was not found.")
    return urls


def scrape_product_data(url):
    """
    Scrape the product TITLE and PRICE (float) from an Amazon product page.
    Returns (title_str, price_str, price_float).
    Raises an exception if scraping fails.
    """
    HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/108.0.0.0 Safari/537.36"
        ),
        "Accept-Encoding": "gzip, deflate",
        "DNT": "1",
        "Connection": "close",
        "Upgrade-Insecure-Requests": "1",
    }
    
    response = requests.get(url, headers=HEADERS, timeout=15)
    if response.status_code != 200:
        raise ValueError(f"Request to {url} failed with status code {response.status_code}")
    
    soup = BeautifulSoup(response.text, "html.parser")
    
    # Find the product title
    title_elem = soup.find("span", class_="a-size-large product-title-word-break")
    if not title_elem:
        raise ValueError("Could not find product title on the page.")
    title = title_elem.get_text(strip=True)
    
    # Find the product price
    price_elem = soup.find('span', class_="a-price aok-align-center reinventPricePriceToPayMargin priceToPay")
    if not price_elem:
        raise ValueError("Could not find product price on the page.")
    price_str = price_elem.get_text(strip=True)
    
    # Convert price string to float (remove currency symbols, commas, etc.)
    price_float = float("".join(ch for ch in price_str if ch.isdigit() or ch == '.'))
    
    return title, price_str, price_float


def append_to_log_csv(title, url, price_str, price_float, log_file=LOG_CSV):
    """
    Appends a row to the log CSV with columns:
    [Date, Time, Title, URL, PriceStr, PriceFloat].
    """
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M:%S")
    
    row = {
        "Date": date_str,
        "Time": time_str,
        "Title": title,
        "URL": url,
        "PriceStr": price_str,
        "PriceFloat": price_float
    }
    
    # Check if CSV exists to decide if we write a header
    file_exists = os.path.isfile(log_file)
    
    df = pd.DataFrame([row])
    df.to_csv(log_file, mode='a', index=False, header=not file_exists)
    
    print(f"[LOG] {title} | {price_str} | {date_str} {time_str} logged to {log_file}.")


def send_email_notification(title, price_str, url, threshold=None,
                            sender=SENDER_EMAIL, recipient=RECIPIENT_EMAIL, password=APP_PASSWORD):
    """
    Sends an email (via Gmail SMTP) about the product and its price.
    Optionally includes a threshold in the message.
    """
    if not password:
        raise ValueError("GMAIL_APP_PASSWORD environment variable not set!")
    
    subject = f"Price Update: {title}"
    if threshold is not None:
        body = (
            f"The item '{title}' is currently {price_str}, "
            f"which is below your threshold of ${threshold:.2f}!\n\nLink: {url}"
        )
    else:
        body = f"The item '{title}' is currently {price_str}.\n\nLink: {url}"
    
    msg = f"Subject: {subject}\n\n{body}"
    
    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(sender, password)
        server.sendmail(sender, recipient, msg)
        server.close()
        print(f"[EMAIL] Notification sent to {recipient} about '{title}'.")
    except Exception as e:
        print(f"[ERROR] Sending email failed: {e}")


def main():
    """
    Runs a single pass:
      1) Reads URLs from 'wishlisted.csv'
      2) Scrapes each URL for price
      3) Logs data to 'prices_log.csv'
      4) (Optionally) sends notifications if price changed or meets conditions
      5) Exits
    """
    urls = read_wishlist(csv_file)
    if not urls:
        print("No URLs found in wishlisted.csv. Exiting.")
        return
    
    print(f"[INFO] Running one-pass check for {len(urls)} product(s).")
    
    # Keep track of last known prices if you want to detect changes
    # (But since we're only running once, you'd typically keep that data in a
    #  separate file or database from prior runs.)
    last_prices = {}
    
    for url in urls:
        try:
            title, price_str, price_float = scrape_product_data(url)
            
            # Log data
            append_to_log_csv(title, url, price_str, price_float, LOG_CSV)
            
            Example logic: if you had a stored price, compare for changes
            old_price = last_prices.get(url)
            if old_price is None:
                last_prices[url] = price_float
            else:
                if price_float != old_price:
                    send_email_notification(title, price_str, url)
                    last_prices[url] = price_float

            # If you wanted threshold logic, you'd define thresholds separately
            # threshold = ...
            # if threshold and price_float < threshold:
            #     send_email_notification(title, price_str, url, threshold=threshold)
            
        except Exception as e:
            print(f"[ERROR] Failed to scrape {url}. Error: {e}")

    print("[INFO] Script run complete. Exiting.")


if __name__ == "__main__":
    main()
