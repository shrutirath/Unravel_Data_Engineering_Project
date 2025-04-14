# 📰 Travel News Pipeline Project

This project builds a **data pipeline** that scrapes the **latest travel news articles** from two popular sources: [Skift](https://skift.com) and [PhocusWire](https://www.phocuswire.com/). The pipeline runs **daily using Airflow**, stores results in **SQLite**, and presents the latest 5 articles on a **Streamlit UI**, powered by a **Flask API** — all containerized with **Docker**.

---

## 🔧 Tech Stack

- **Web Scraping**: Python, BeautifulSoup
- **Workflow Orchestration**: Apache Airflow
- **Database**: SQLite
- **API**: Flask
- **Frontend UI**: Streamlit
- **Containerization**: Docker & Docker Compose

---

## 🧩 Architecture Overview

Skift + PhocusWire ↓ [Web Scraping: data_fetch_dag.py] ↓ [Airflow DAG: Daily Insert to DB] ↓ [SQLite Database (news_articles.db)] ↓ [Flask API] ←────────── Streamlit UI ↓ /api/latest-articles


---

## 🛠️ Components

### 1. `data_fetch_dag.py`

- Scrapes articles from **Skift** and **PhocusWire**
- Cleans and transforms data
- Hashes article titles as unique IDs
- Inserts only **incremental** (new) articles based on the latest `Publication_timestamp`

### 2. `app.py`

- A **Flask REST API**
- Endpoint: `/api/latest-articles`
- Fetches the 5 most recent articles from the database
- Returns JSON response with metadata like title, author, timestamp, etc.

### 3. `streamlit_Ui.py`

- Fetches data from Flask API and displays it in a friendly UI
- Supports rich article formatting with title, author, timestamp, and a link to read more

### 4. `docker-compose.yml`

- Sets up:
  - Airflow Webserver & Scheduler
  - Postgres (for Airflow)
  - Flask API
  - Streamlit UI

- Each service runs in its own container, communicating over a shared `airflow_network`.

---

## 📂 Project Structure

```
project-root/
├── dags/
│   └── data_fetch.py             # Airflow DAG & scraping logic
├── app.py                        # Flask API
├── streamlit_Ui.py               # Streamlit frontend
├── new_requirements.txt          # Full dependencies for Airflow container and flask
├── docker-compose.yml            # Docker orchestration for all services
├── Readme.md           
├── data/
│   └── news_articles.db          # SQLite database
└── script/
    └── entrypoint.sh             # Custom Airflow entrypoint script
```

---

## 🚀 How to Run

### 1. Clone the repository

```bash
git clone https://github.com/shrutirath/Unravel_Data_Engineering_Project.git
cd Unravel_Data_Engineering_Project

Access Airflow at: http://localhost:8080

Access Flask API at: http://localhost:5100/api/latest-articles

Access Streamlit UI at: http://localhost:8501

docker-compose up -d

