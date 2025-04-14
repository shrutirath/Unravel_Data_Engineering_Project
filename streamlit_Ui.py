import streamlit as st
import requests
from datetime import datetime

st.set_page_config(page_title="Latest Travel News", layout="wide")

st.title("📰 Latest Travel Articles")

API_URL = "http://flask_api:5100/api/latest-articles"

try:
    response = requests.get(API_URL)
    data = response.json()
    if data["status"] == "success":
        articles = data["data"]
        for article in articles:
            st.markdown("---")
            st.subheader(f"📌 {article['title']}")
            st.markdown(f"**Author:** {article['author']}  |  **Source:** {article['source']}")
            published_time = datetime.strptime(article["published_at"], "%Y-%m-%d %H:%M:%S")
            st.markdown(f"🕒 Published at: {published_time.strftime('%b %d, %Y %I:%M %p')}")
            st.markdown(f"[🔗 Read More]({article['url']})", unsafe_allow_html=True)
    else:
        st.error("Failed to fetch articles.")
except Exception as e:
    st.error(f"Error: {e}")
