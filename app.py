from flask import Flask, jsonify
import sqlite3
from datetime import datetime

app = Flask(__name__)
DB_PATH = 'data/news_articles.db'


def fetch_latest_articles(limit=5):
    print("here" * 80)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute('''
        SELECT * FROM Article_Table
        ORDER BY Publication_timestamp DESC
        LIMIT ?
    ''', (limit,))

    rows = cursor.fetchall()
    conn.close()

    articles = []
    for row in rows:
        articles.append({
            "article_id": row["Article_id"],
            "title": row["Title"],
            "author": row["Author"],
            "url": row["URL"],
            "source": row["Source"],
            "published_at": row["Publication_timestamp"],
        })

    return articles


@app.route('/api/latest-articles', methods=['GET'])
def latest_articles():
    articles = fetch_latest_articles()
    print(articles)
    return jsonify({
        "status": "success",
        "data": articles
    })


if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0', port=5100)
