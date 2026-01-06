import requests
from bs4 import BeautifulSoup
from datetime import datetime

url = "https://blogs.nvidia.com/blog/2026-ces-special-presentation/"
response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")

# --- Extract fields ---
article = soup.find("article")
title = article.find("h1").get_text()

time_tag = article.find("time")
published_at = time_tag["datetime"] if time_tag else None

author_tag = article.find("span", class_="author")
author = author_tag.get_text() if author_tag else None

content = article.find("div", class_="entry-content")

paragraphs = [
    p.get_text()
    for p in content.find_all("p")
]

data = {
    "source": "nvidia_blog",
    "url": url,
    "title": title,
    "author": author,
    "published_at": published_at,
    "content": content
}