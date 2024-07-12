import requests
from bs4 import BeautifulSoup
from google.cloud import storage
from transformers import pipeline
import os
from googleapiclient.discovery import build

def search_ai_news():
    api_key = os.environ.get('GOOGLE_API_KEY')
    cse_id = os.environ.get('GOOGLE_CSE_ID')
    
    service = build("customsearch", "v1", developerKey=api_key)
    results = service.cse().list(q="artificial intelligence news", cx=cse_id, num=5).execute()
    
    urls = [item['link'] for item in results.get('items', [])]
    return urls

def extract_content(urls):
    articles = []
    for url in urls:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        articles.append(soup.get_text())
    return articles

def summarize_articles(articles):
    summarizer = pipeline("summarization")
    summaries = [summarizer(article, max_length=100, min_length=30, do_sample=False)[0]['summary_text'] for article in articles]
    return summaries

def main(event, context):
    urls = search_ai_news()
    articles = extract_content(urls)
    summaries = summarize_articles(articles)
    
    # Store summaries in Cloud Storage
    storage_client = storage.Client()
    bucket = storage_client.get_bucket('your-bucket-name')
    blob = bucket.blob('ai_news_summary.txt')
    blob.upload_from_string('\n\n'.join(summaries))

if __name__ == "__main__":
    main(None, None)