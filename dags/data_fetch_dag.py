import requests
from bs4 import BeautifulSoup
import sqlite3
from datetime import datetime
import hashlib
import base64
from airflow import DAG
from airflow.operators.python import PythonOperator

default_args = {
    'owner': 'airscholar',
    'start_date': datetime(2025, 1, 1, 12, 00)
}


def hashIdFromTitle(title): #Unique Id creation uusing title of the news
    hash_object = hashlib.sha256(title.encode('utf-8')).digest()
    base64_hash = base64.urlsafe_b64encode(hash_object).decode('utf-8')
    return base64_hash[:-1]

def fetch_data_from_PhocusWire(last_time):# fetching the data from Phocuswire incrementally based on timestamp
    url = "https://www.phocuswire.com/Latest-News"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/117.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
    }
    response = requests.get(url,headers = headers)
    # 2. Parse HTML

    soup = BeautifulSoup(response.text, 'html.parser')
    # print(soup)

    # 3. Find and extract the data
    article_list = soup.find("div",class_="article-list")
    quotes = article_list.find_all("div",class_ = "item")
    # print(quotes)
    article_data = []
    # 4. Display the data
    for quote in quotes:
        text = (quote.find("a",class_= "title"))
        if text:
            try:
                author_metadata = (quote.find("div", class_="author"))
                author_name = author_metadata.get_text()
                author_name = author_name.replace("By ", "").strip()
                split_var = author_name.split('|')
                if split_var[0] and len(split_var) > 1:
                    author_name  = split_var[0].strip()
                else:
                    author_name = ""
                if split_var[1]:
                    timestamp = split_var[1].strip()
                    timestamp = datetime.strptime(timestamp, "%B %d, %Y")
                    now = datetime.now()
                    timestamp = timestamp.replace(hour = now.hour,minute = now.minute,second = now.second)
                else:
                    timestamp = datetime.now()
                # timestamp = author_name.split('|')[1]
            except Exception as e:
                print("ye text hai ab ::::::: ", text)
                print("ye qupwojew hai n::: ", quote)
                assert  False

            txt = text.get_text()
            url = text.get('href')
            url = 'https://www.phocuswire.com'+ url

            if(timestamp > last_time):
                article_data.append({
                    "article_id":hashIdFromTitle(txt),
                    "title": txt,
                    "author_name":author_name,
                    "published_at":timestamp,
                    "URL":url,
                    "Source" : 'PhocusWire',
                    "Created_at" : datetime.now()
                })
    return article_data

def fetch_data_from_Skift(last_time):# fetching data from Skift incrementally using publication_timestamp

    url = "https://skift.com/news/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/117.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
    }
    response = requests.get(url,headers = headers)
    article_data = []
    print(response)

    soup = BeautifulSoup(response.text, 'html.parser')

    article_list = soup.find("div",class_="o-container o-stack")

    quotes = article_list.find_all("article")

    for quote in quotes:
        head = (quote.find("h3"))
        title = head.get_text()
        title = title.replace("\n" ,"").strip()
        url = head.find("a").get('href')
        split_var = quote.find("div",class_="c-tease__byline").get_text()
        split_var = split_var.split('|')
        author_name = "NA"
        if(split_var[0] and len(split_var)>1):
            author_name = split_var[0].strip()
        timestamp = quote.find("div", class_="c-tease__byline").find("time").get('datetime')
        timestamp = datetime.fromisoformat(timestamp)
        timestamp = timestamp.replace(tzinfo=None)
        if(timestamp>last_time):
            article_data.append({
                "article_id": hashIdFromTitle(title),
                "title": title,
                "author_name": author_name,
                "published_at": timestamp,
                "URL": url,
                "Source": 'Skift',
                "Created_at": datetime.now()
            })
    return article_data

def insert_data(): #function to create table and insert data from both websites
    news_conn = sqlite3.connect("/opt/airflow/data/news_articles.db")
    news_cursor = news_conn.cursor()
    news_cursor.execute('''
       CREATE TABLE IF NOT EXISTS Article_Table(
       Article_id VARCHAR(200) Primary Key,
       URL VARCHAR(500) ,
       Publication_timestamp DATETIME,
       Source VARCHAR(100),
       Author VARCHAR(200),
       Title Varchar(500),
       Created_at DATETIME DEFAULT CURRENT_TIMESTAMP   
       );
    ''')

    news_cursor.execute('''
        SELECT MAX(Publication_timestamp) FROM Article_Table;
    ''')
    last_time = news_cursor.fetchone()[0] or "2025-04-01 00:00:00"
    last_time = datetime.strptime(last_time, "%Y-%m-%d %H:%M:%S")

    article_data = fetch_data_from_PhocusWire(last_time)
    for data in article_data :
        news_cursor.execute('''
            INSERT INTO Article_Table (Article_id, URL, Publication_timestamp, Source, Author, Title, Created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''',(data['article_id'],
            data['URL'],
            data['published_at'],
            data['Source'],
            data['author_name'],
            data['title'],
            data['Created_at']))
    article_data = fetch_data_from_Skift(last_time)
    for data in article_data :
        news_cursor.execute('''
            INSERT INTO Article_Table (Article_id, URL, Publication_timestamp, Source, Author, Title, Created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''',(data['article_id'],
            data['URL'],
            data['published_at'],
            data['Source'],
            data['author_name'],
            data['title'],
            data['Created_at']))
    news_conn.commit()
    news_conn.close()

with DAG('insert_data', #implementing DAG to schedule the data insertion
         default_args=default_args,
         schedule='@daily',
         catchup=False) as dag:

   insert_data_task = PythonOperator(
        task_id='insert_data',
        python_callable=insert_data
   )



