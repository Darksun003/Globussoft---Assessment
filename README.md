📘 Assessment Project – Task 1 & Task 2
Author: GV Jayanth

This repository contains two complete data/ML engineering tasks:
Task 1 – Amazon Laptop Web Scraper
Task 2 – Face Verification API using Deep Learning (InsightFace)

----------------------------------------------
🧩 Task 1 – Amazon Laptop Web Scraper
----------------------------------------------
📌 Objective

Extract laptop details from Amazon search results using Selenium, and save the output to a timestamped CSV file.

📂 Data Extracted

For every laptop listing:
Laptop Image URL
Title
Rating
Price
Ad / Organic Result

🛠️ Technologies Used
| Tool                     | Purpose             |
| ------------------------ | ------------------- |
| Python 3.x               | Programming         |
| Selenium                 | Browser automation  |
| ChromeDriver Manager     | Driver handling     |
| BeautifulSoup (optional) | HTML parsing        |
| Pandas                   | CSV output handling |

▶️ How to Run Task 1
1️⃣ Install Requirements
  pip install -r requirements.txt
2️⃣ Run the Scraper
  python task1_amazon_scraper.py
3️⃣ Output
  outputs/amazon_laptops_YYYYMMDD_HHMMSS.csv

📦 Task 1 Folder Structure
```
Task 1/
│── task1_amazon_scraper.py
│── requirements.txt
│── outputs/
│   └── amazon_laptops_<timestamp>.csv
└── debug_html/
```
---------------------------------------------------
🧩 Task 2 – Deep Learning Face Verification API
---------------------------------------------------
📌 Objective
Build a face verification model and expose it via a FastAPI REST API.
This system compares two images and determines whether they belong to the same person.

🚀 Features

InsightFace face detection + embedding (state-of-the-art)
ONNX Runtime for fast inference (CPU/GPU supported)
OpenCV for image decoding (no Pillow required)
Cosine similarity-based verification
FastAPI service with interactive Swagger UI (/docs)
##Optional gallery pipeline:
Build mean embeddings per identity (gallery_insightface.npz)
Identify an unknown face against the gallery

📦 Requirements
Install all dependencies:
  pip install -r requirements.txt
▶️ Running the FastAPI Server
  uvicorn app_insightface:app --host 127.0.0.1 --port 8000
  
Use POST /verify to upload two images and get:
similarity score
bounding boxes
same/different decision
threshold used

🛠️ Training (Build Gallery Embeddings)
```
data/
 ├── alice/
 │     ├── img1.jpg
 │     └── img2.jpg
 ├── bob/
 │     ├── a1.jpg
 │     └── a2.jpg
```
python train_gallery_insightface.py --data_dir data --out gallery_insightface.npz

🧪 Testing (Verify or Identify)
from test_insightface import verify_pair
verify_pair("img1.jpg", "img2.jpg")

📁 Project Structure
```
Task 2/
│── app_insightface.py             # FastAPI verification service
│── train_gallery_insightface.py   # Build gallery embeddings
│── test_insightface.py            # Helper functions for testing
│── data/                          # Training images (organized by person)
│── gallery_insightface.npz        # Saved embeddings (optional)
│── requirements.txt
└── README.md
```
🔍 Threshold Notes

Default threshold: 0.6
Increase threshold → more strict
Decrease threshold → more lenient
Tune based on your dataset or production needs
