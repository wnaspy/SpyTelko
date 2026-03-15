import sqlite3
from flask import Flask, render_template, request, send_file

DB_FILE = "crawler.db"

app = Flask(__name__)


def get_latest_news():

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("""
    SELECT channel,text,urls
    FROM news
    ORDER BY id DESC
    LIMIT 50
    """)

    rows = cursor.fetchall()
    conn.close()

    return rows


def search_news(keyword):

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("""
    SELECT channel,text,urls
    FROM news
    WHERE text LIKE ?
    ORDER BY id DESC
    LIMIT 50
    """, (f"%{keyword}%",))

    rows = cursor.fetchall()
    conn.close()

    return rows


def search_documents(keyword):

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("""
    SELECT file_name,file_path
    FROM documents
    WHERE file_name LIKE ?
    ORDER BY id DESC
    LIMIT 50
    """, (f"%{keyword}%",))

    rows = cursor.fetchall()
    conn.close()

    return rows


@app.route("/")
def home():

    news_query = request.args.get("news_q")
    doc_query = request.args.get("doc_q")

    news = []
    docs = []

    # mặc định hiển thị news
    if not news_query and not doc_query:
        news = get_latest_news()

    # search news
    if news_query:
        news = search_news(news_query)

    # search documents
    if doc_query:
        docs = search_documents(doc_query)

    return render_template(
        "index.html",
        news=news,
        docs=docs,
        news_query=news_query,
        doc_query=doc_query
    )


@app.route("/download")
def download():

    path = request.args.get("path")

    return send_file(path, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)