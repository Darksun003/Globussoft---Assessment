📘 Amazon Laptop Scraper – Task 1
<p align="left"> <img src="https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge"/> <img src="https://img.shields.io/badge/Selenium-Automation-orange?style=for-the-badge"/> <img src="https://img.shields.io/badge/BeautifulSoup-Parser-brightgreen?style=for-the-badge"/> <img src="https://img.shields.io/badge/CSV-Output-yellow?style=for-the-badge"/> <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge"/> <img src="https://img.shields.io/badge/Status-Active-success?style=for-the-badge"/> </p>

📌 Project Overview

This project is part of Globussoft Assessment – Task 1, where the objective is to build a Python script that scrapes laptop product information from Amazon.in and automatically saves the data into a timestamped CSV file.

Because Amazon blocks many bot requests (returns 503 errors), this scraper uses Selenium and a real Chrome browser to collect accurate results without being blocked.

🎯 Scraper Features
✔ Scrapes laptop listing details from Amazon.in
✔ Extracts essential product information:

🖼 Image URL
🏷 Title
⭐ Rating
💰 Price
🔖 Ad / Organic Result
🔗 Product URL
🆔 ASIN

📝 Review count, Seller snippet, etc.
✔ Retries pages when Amazon blocks with 503
✔ Warm-up session to avoid detection
✔ Auto-scrolls for lazy-loaded items
✔ Saves debug HTML for troubleshooting
✔ Output file name includes timestamp
✔ Runs on Python 3.8+

🛠️ Technologies & Tools Used
| Tool                   | Purpose                                           |
| ---------------------- | ------------------------------------------------- |
| **Python 3.8+**        | Base programming language                         |
| **Selenium WebDriver** | Full browser automation to bypass Amazon blocking |
| **webdriver-manager**  | Auto-installs and manages ChromeDriver            |
| **BeautifulSoup4**     | HTML parsing                                      |
| **LXML parser**        | Fast HTML/XML parsing backend                     |
| **Pandas**             | CSV creation & data manipulation                  |
| **Chrome Browser**     | Real browser rendering                            |

📦 Installation
1️⃣ Install dependencies:
    pip install selenium webdriver-manager beautifulsoup4 pandas lxml
2️⃣ Ensure Google Chrome is installed
    If Chrome is missing, download it from:
    https://www.google.com/chrome/
▶️ How to Run
    Run the scraper using:
        python task1_selenium_scraper.py
    The output CSV will be auto-generated in:
        outputs/amazon_laptops_YYYYMMDD_HHMMSS.csv

📂 Output Format
| Column           | Description                |
| ---------------- | -------------------------- |
| scrape_timestamp | Time of scraping           |
| ASIN             | Amazon product ID          |
| Title            | Laptop product title       |
| Product_URL      | URL of the product         |
| Image            | Product image link         |
| Price            | Price (numeric)            |
| Rating           | Star rating                |
| Reviews_Count    | Total reviews              |
| Seller_Snippet   | Seller / short description |
| Result_Type      | "Ad" or "Organic"          |

🧩 Project Structure
📁 Assessment/
│── task1_selenium_scraper.py
│── requirements.txt
│── README.md
│── 📁 outputs/
│     └── amazon_laptops_YYYYMMDD_HHMMSS.csv
│── 📁 debug_html/
│     └── page_1_attempt_1.html  (if any retries fail)

🧪 Why Selenium?
Amazon repeatedly blocks scraping via requests / BeautifulSoup, causing:
    ❌ 503 errors
    ❌ Empty pages
    ❌ Captcha pages
Using Selenium ensures:
    ✔ Real browser footprint
    ✔ Human-like scrolling
    ✔ Cookie/consent pop-up handling
    ✔ High success rate

🔒 Legal Note
    This scraper is intended only for educational and assessment purposes.
    Frequent scraping of Amazon violates their Terms of Service.
    Use responsibly.

📝 License
    This project is licensed under the MIT License.

👨‍💻 Author
GV Jayanth
Data Scientist| Python Developer | AI & Cloud Engineer
LinkedIn: https://www.linkedin.com/in/gv-jayanth