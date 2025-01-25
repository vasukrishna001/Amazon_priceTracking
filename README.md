# Price Tracker for Wishlisted Products

## Project Overview
This project is a Python-based price tracking system designed to help users monitor the prices of Amazon products on their wishlist. The system scrapes product data (title and price) from Amazon, logs the information into a CSV file, and sends email notifications if the price of a product drops below a specified threshold.

The script is set up to run automatically every day using **Task Scheduler** (Windows) or **cron** (Linux/macOS), ensuring that the user is always up to date with the prices of their wishlisted products.

### Key Features:
- **Product Price Scraping**: Scrapes Amazon product pages for the title and price of wishlisted items.
- **CSV Logging**: Logs product title, URL, and price data into a CSV file for tracking price changes over time.
- **Email Notifications**: Sends email notifications when a product's price drops below a user-defined threshold.
- **Daily Automation**: Uses **Task Scheduler** (Windows) or **cron** (Linux/macOS) to run the script automatically every day.

---

## Setup and Configuration

### Prerequisites:
- Python 3.x
- Libraries:
  - `requests` (for making HTTP requests)
  - `BeautifulSoup` (for web scraping)
  - `pandas` (for handling CSV files)
  - `smtplib` (for sending emails)
- **Gmail Account**: Required for email notifications (use a Gmail app password).

### Configuration:
- **CSV Files**:
  - **`wishlisted.csv`**: A CSV file containing a column named "URL" with the URLs of Amazon products you wish to track.
  - **`prices_log.csv`**: Output CSV file that logs the product data (including price and timestamp) after each check.

- **Gmail Configuration**:
  - Set up your Gmail account and generate an app password (for security reasons, this is recommended over using your main Gmail password).
  - Store the Gmail app password as an environment variable (`GMAIL_APP_PASSWORD`).

## Important Notice for Web Scraping

Please note that the web scraper is designed to scrape product data from **individual product pages** on Amazon. If you provide a URL that points to a **search results page** or a page displaying **multiple products**, the scraper may not work as intended.

For the scraper to function correctly:
- **Ensure that the URL points directly to a single product page**. The URL should contain the unique product identifier (e.g., `dp/B08N5WRWNW` for a specific product).
- **Multiple products on a page**: If a URL contains multiple products (as seen in category pages or search results), the scraper will not be able to extract the necessary details (like title and price) for each product.

For best results, always use **direct links to individual product pages** for scraping ( example image is uploaded in the name of sampleUrl_image)

---

## How It Works

### 1. **Read Product URLs**:
The system reads the `wishlisted.csv` file to get the list of Amazon product URLs.

### 2. **Scrape Product Data**:
Using BeautifulSoup, the script fetches the product title and price from each product's Amazon page. It cleans the price by removing any currency symbols and converts it to a float for comparison.

### 3. **Log Price Data**:
Each time the script runs, it logs the product data (title, URL, price) into the `prices_log.csv` file along with the current date and time.

### 4. **Send Price Drop Notifications**:
If the product price has dropped (or meets a specified threshold), an email notification is sent to the user with the details.

### 5. **One-Time Check**:
The script performs a one-time check for all URLs in the wishlist, scrapes the prices, logs them, and optionally sends notifications.

---

## Task Scheduler (Windows) or Cron (Linux/macOS) Integration

To automate the script to run daily, you can use **Task Scheduler** (on Windows) or **cron** (on Linux/macOS). Here’s how to set up each:

### Task Scheduler (Windows):
1. Open **Task Scheduler** by typing "Task Scheduler" into the Windows search bar and clicking the app.
2. Click on **Create Task** on the right side.
3. In the **General** tab:
   - Give the task a name like "Amazon Price Tracker".
   - Select **Run whether user is logged on or not**.
4. In the **Triggers** tab:
   - Click **New** and set the task to run **Daily** at your preferred time.
5. In the **Actions** tab:
   - Click **New**, choose **Start a program**, and browse to the Python script.
   - Make sure to use the full path to the Python executable (`python.exe`) and the script file (e.g., `python.exe C:\path\to\your\script.py`).
6. Click **OK** to save the task.

### Cron (Linux/macOS):
1. Open your terminal.
2. Type `crontab -e` to open the crontab editor.
3. Add a line to schedule the script to run daily, e.g.:
   
