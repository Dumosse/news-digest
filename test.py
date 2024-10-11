import streamlit as st
import requests
from transformers import pipeline
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

newsAPI_Key = os.getenv('NEWS_API_KEY')

summarizer = pipeline('summarization', model="facebook/bart-large-cnn", framework="pt")

@st.cache_data(ttl=3600)
def fetch_news_articles(api_key, domain, from_date, to_date, sortBy, language='en'):
    url = f'https://newsapi.org/v2/everything?domains={domain}&from={from_date}&to={to_date}&sortBy={sortBy}&language={language}&apiKey={api_key}'
    response = requests.get(url)
    articles = response.json().get('articles', [])
    return articles

def prepare_article_text(article):
    sections = [article.get('title', ''), article.get('description', ''), article.get('content', '')]
    return ' '.join([section for section in sections if section])

def summarize_article(article_text):
    summary = summarizer(article_text, max_length=130, min_length=30, do_sample=False)[0]['summary_text']
    return summary

def main():
    st.set_page_config(page_title="Smart News Digest", layout="wide")
    st.title("Smart News Digest")
    st.write("Get concise summaries of the latest news articles.")

    st.sidebar.header("News Filters")
    category_to_domain = {
        "Technology": "techcrunch.com",
        "Sports": "espn.com",
        "Science": "nationalgeographic.com",
        "Business": "bloomberg.com",
        "Entertainment": "ew.com"
    }
    category = st.sidebar.selectbox("Select Category", list(category_to_domain.keys()))
    num_articles = st.sidebar.slider("Number of Articles", 1, 10, 5)
    sort_by_options = ["relevancy", "popularity", "publishedAt"]
    sortBy = st.sidebar.selectbox("Sort Articles By", sort_by_options, index=2)

    from_date = st.sidebar.date_input("From Date", value=datetime.today()).strftime('%Y-%m-%d')
    to_date = st.sidebar.date_input("To Date", value=datetime.today()).strftime('%Y-%m-%d')

    domain = category_to_domain[category]

    with st.spinner('Fetching and summarizing articles...'):
        articles = fetch_news_articles(newsAPI_Key, domain, from_date, to_date, sortBy)[:num_articles]

    st.header(f"Top {num_articles} {category.capitalize()} News Articles")

    for i, article in enumerate(articles):
        st.subheader(f"{i + 1}. {article['title']}")
        st.write(f"**Source:** {article['source']['name']}")
        st.write(f"**Published At:** {article['publishedAt']}")

        article_text = prepare_article_text(article)
        if article_text:
            summary = summarize_article(article_text)
            st.write(f"**Summary:** {summary}")
        else:
            st.write("**Summary:** Content not available for summarization.")

        if article['url']:
            st.markdown(f"[Read more]({article['url']})")

if __name__ == "__main__":
    main()