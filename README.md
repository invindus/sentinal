# Sentinal - Blog Sentiment Analyzer

## Problem Statement

Build a web application that scrapes public blog posts, analyzes their emotional sentiment, and allows users to query topics to understand overall sentiment trends and common emotional themes.

## Goals
### Phase 1 - Minimum Features

1. Scrape text from a public blog source
2. Store raw and processed text in database
3. Run sentiment analysis through NLP
4. Display sentiment results in a simple UI

### Phase 2 - Stretch Features

1. Chatbot w/ interface and topic based querying
2. Bubble graph visualizations of topics and sentiment
3. LLM powered summaries

## System Design
### Tech Stack
**Backend**: FastAPI (Python)

**Frontend**: Next.js (TypeScript)

**Container**: Docker

**Database**: PostgreSQL

**Visualization**: Chart.js

**Scraping**: Requests + BeautifulSoup

**NLP**: VADER / TextBlob

### High-Level Architecture
[ Blog Source ] -> [ Scraper Service ] -> [ Text Cleaning / Preprocessing ] -> [ Sentiment Analyzer ] -> [ PostgreSQL Database ] -> [ FastAPI Backend ] -> [ Next.js Frontend ] -> [ Charts + Chatbot UI ]

### Database Design

**blogs**
- id
- source
- url
- scraped_at
- raw_text

**sentiment_results**
- blog_id (FK)
- sentiment_score
- sentiment_label
- emotion
- analyzed_at

## Project Plan
1. Init repo
2. Dockerize backend + database
3. Create basic schema
4. Implement Scraper
5. Save raw text
6. Sentiment analysis
7. Store results
8. Basic UI
9. Fetch and display sentiment results
10. Charts
11. Chatbot
12. LLM Summaries
