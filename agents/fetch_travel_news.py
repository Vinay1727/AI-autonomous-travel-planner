# agents/fetch_travel_news.py
import os
import requests
from datetime import datetime, timedelta
import feedparser
import json
from dotenv import load_dotenv
import re

# Load environment variables
load_dotenv()

# API keys for various news sources
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")   # https://newsapi.org/
GNEWS_KEY = os.getenv("GNEWS_KEY")       # https://gnews.io/
CURRENTS_KEY = os.getenv("CURRENTS_KEY") # https://currentsapi.services/

DEFAULT_DAYS_BACK = 10

# Enhanced travel keywords for better filtering
TRAVEL_KEYWORDS = [
    "travel", "tourism", "tourist", "vacation", "holiday", "trip", "journey",
    "sightseeing", "tour", "explore", "adventure", "destination", "visiting",
    "backpacking", "wanderlust", "itinerary", "guide", "attractions", "hotels",
    "flights", "airlines", "resort", "cruise", "booking", "travel tips",
    "travel guide", "things to do", "places to visit", "cultural sites",
    "landmarks", "museums", "restaurants", "local food", "travel blog",
    "travel experience", "solo travel", "family travel", "budget travel"
]

# Travel-specific domains and sources for better filtering
TRAVEL_DOMAINS = [
    "lonelyplanet.com", "tripadvisor.com", "travelandleisure.com", 
    "cntraveler.com", "afar.com", "nationalgeographic.com/travel",
    "fodors.com", "frommers.com", "roughguides.com", "timeout.com",
    "skyscanner.com", "booking.com", "expedia.com", "kayak.com",
    "travelzoo.com", "smartertravel.com", "momondo.com", "hostelworld.com"
]

def _normalize_article(item):
    """Return a uniform article dict used by UI."""
    return {
        "title": item.get("title") or item.get("headline"),
        "description": item.get("description") or item.get("summary"),
        "url": item.get("url") or item.get("link"),
        "image": item.get("urlToImage") or item.get("image"),
        "source": item.get("source", {}).get("name") if isinstance(item.get("source"), dict) else item.get("source"),
        "publishedAt": item.get("publishedAt") or item.get("pubDate") or item.get("published")
    }

def _is_travel_related(title, description, url=""):
    """Enhanced travel content detection using keywords and domain checking."""
    if not title and not description:
        return False
    
    # Combine title and description for analysis
    text = f"{title or ''} {description or ''}".lower()
    
    # Check if URL is from known travel domain
    if url:
        for domain in TRAVEL_DOMAINS:
            if domain in url.lower():
                return True
    
    # Count travel keyword matches
    keyword_matches = sum(1 for keyword in TRAVEL_KEYWORDS if keyword in text)
    
    # Consider it travel-related if:
    # 1. Multiple travel keywords found, OR
    # 2. Strong travel indicators present
    strong_indicators = ["travel", "tourism", "tourist", "vacation", "trip", "destination", "visit"]
    has_strong_indicator = any(indicator in text for indicator in strong_indicators)
    
    return keyword_matches >= 2 or has_strong_indicator

def _filter_travel_articles(articles):
    """Filter articles to only include travel-related content."""
    filtered = []
    for article in articles:
        title = article.get("title", "")
        description = article.get("description", "")
        url = article.get("url", "")
        
        if _is_travel_related(title, description, url):
            filtered.append(article)
    
    return filtered

# ----------------- Source fetchers -----------------
def fetch_from_newsapi(q, max_results=6, days_back=DEFAULT_DAYS_BACK):
    if not NEWSAPI_KEY:
        return []
    
    # Enhanced query with travel-specific domains
    travel_domains_query = " OR ".join([f"domain:{domain}" for domain in TRAVEL_DOMAINS[:5]])  # Limit to avoid too long query
    enhanced_query = f"({q}) AND ({travel_domains_query} OR travel OR tourism OR vacation)"
    
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": enhanced_query,
        "from": (datetime.utcnow() - timedelta(days=days_back)).strftime("%Y-%m-%d"),
        "sortBy": "publishedAt",
        "pageSize": max_results * 2,  # Get more to filter later
        "language": "en",
        "apiKey": NEWSAPI_KEY
    }
    try:
        r = requests.get(url, params=params, timeout=8)
        r.raise_for_status()
        items = r.json().get("articles", [])
        normalized = [_normalize_article(it) for it in items]
        filtered = _filter_travel_articles(normalized)
        return filtered[:max_results]
    except Exception as e:
        print("NewsAPI error:", e)
        return []

def fetch_from_gnews(q, max_results=6, days_back=DEFAULT_DAYS_BACK):
    if not GNEWS_KEY:
        return []
    
    # Enhanced query for travel content
    travel_query = f"travel {q} OR tourism {q} OR vacation {q} OR visit {q}"
    
    url = "https://gnews.io/api/v4/search"
    params = {
        "q": travel_query,
        "from": (datetime.utcnow() - timedelta(days=days_back)).strftime("%Y-%m-%d"),
        "max": max_results * 2,  # Get more to filter later
        "lang": "en",
        "token": GNEWS_KEY
    }
    try:
        r = requests.get(url, params=params, timeout=8)
        r.raise_for_status()
        data = r.json()
        items = data.get("articles", [])
        mapped = []
        for it in items:
            mapped.append({
                "title": it.get("title"),
                "description": it.get("description"),
                "url": it.get("url"),
                "image": it.get("image"),
                "source": it.get("source", {}).get("name") if isinstance(it.get("source"), dict) else it.get("source"),
                "publishedAt": it.get("publishedAt")
            })
        filtered = _filter_travel_articles(mapped)
        return filtered[:max_results]
    except Exception as e:
        print("GNews error:", e)
        return []

def fetch_from_currents(q, max_results=6, days_back=DEFAULT_DAYS_BACK):
    if not CURRENTS_KEY:
        return []
    
    # Enhanced keywords for travel content
    travel_keywords = f"travel {q},tourism {q},vacation {q},visit {q}"
    
    url = "https://api.currentsapi.services/v1/search"
    params = {
        "keywords": travel_keywords,
        "start_date": (datetime.utcnow() - timedelta(days=days_back)).strftime("%Y-%m-%d"),
        "language": "en",
        "page_size": max_results * 2,  # Get more to filter later
        "apiKey": CURRENTS_KEY
    }
    try:
        r = requests.get(url, params=params, timeout=8)
        r.raise_for_status()
        items = r.json().get("news", [])
        mapped = []
        for it in items:
            mapped.append({
                "title": it.get("title"),
                "description": it.get("description"),
                "url": it.get("url"),
                "image": it.get("image"),
                "source": it.get("author") or it.get("source"),
                "publishedAt": it.get("published")
            })
        filtered = _filter_travel_articles(mapped)
        return filtered[:max_results]
    except Exception as e:
        print("CurrentsAPI error:", e)
        return []

def fetch_from_rss_list(rss_urls, max_results=6, destination_filter=None):
    """Enhanced RSS fetching with destination filtering."""
    results = []
    for feed_url in rss_urls:
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries:
                article = {
                    "title": entry.get("title"),
                    "description": entry.get("summary") or entry.get("description"),
                    "url": entry.get("link"),
                    "image": None,
                    "source": feed.feed.get("title"),
                    "publishedAt": entry.get("published") or entry.get("pubDate")
                }
                
                # Filter by destination if specified
                if destination_filter:
                    title_desc = f"{article.get('title', '')} {article.get('description', '')}".lower()
                    if destination_filter.lower() not in title_desc:
                        continue
                
                results.append(article)
                
                if len(results) >= max_results * 2:  # Get more for filtering
                    break
        except Exception as e:
            print("RSS fetch error for", feed_url, e)
    
    # Filter for travel content
    filtered = _filter_travel_articles(results)
    return filtered[:max_results]

# ----------------- Enhanced RSS sources -----------------
DEFAULT_TRAVEL_RSS = [
    "https://www.lonelyplanet.com/news/rss",
    "https://feeds.feedburner.com/afarmontheworld",
    "https://www.nationalgeographic.com/content/nationalgeographic/en_us/news/news.rss",
    "https://feeds.feedburner.com/travelandleisure/all",
    "https://www.cntraveler.com/feed/rss",
    "https://feeds.feedburner.com/smartertravel",
    "https://www.timeout.com/travel/rss",
    "https://feeds.feedburner.com/fodors",
    "https://www.roughguides.com/feed/",
    "https://feeds.feedburner.com/TravelZoo-top20"
]

# Travel blog RSS feeds
TRAVEL_BLOG_RSS = [
    "https://feeds.feedburner.com/nomadicmatt",
    "https://feeds.feedburner.com/ExpertVagabond",
    "https://feeds.feedburner.com/migrationology",
    "https://www.ytravelblog.com/feed/",
    "https://www.bemytravelmuse.com/feed/",
    "https://feeds.feedburner.com/ThePoorTraveler",
    "https://feeds.feedburner.com/adventurous-kate",
    "https://feeds.feedburner.com/hippie-in-heels"
]

def fetch_travel_news(destination, max_results=6, category=None, include_blogs=True):
    """
    Enhanced travel news fetching with better filtering.
    Attempts: NewsAPI -> GNews -> Currents -> RSS fallback.
    
    Args:
        destination: Target location
        max_results: Number of articles to return
        category: Optional category filter
        include_blogs: Whether to include travel blog RSS feeds
    """
    # Build enhanced query string
    if category:
        q = f"{category} {destination}"
    else:
        # More specific travel-related query
        q = f'"{destination}" AND (travel OR tourism OR visit OR vacation OR "things to do")'

    articles = []

    # 1) Primary: NewsAPI with enhanced filtering
    if NEWSAPI_KEY and not articles:
        articles = fetch_from_newsapi(destination, max_results)  # Pass destination directly for better filtering

    # 2) Fallback 1: GNews with enhanced filtering
    if GNEWS_KEY and not articles:
        articles = fetch_from_gnews(destination, max_results)

    # 3) Fallback 2: Currents with enhanced filtering
    if CURRENTS_KEY and not articles:
        articles = fetch_from_currents(destination, max_results)

    # 4) RSS fallback with travel-specific sources
    if not articles:
        rss_sources = DEFAULT_TRAVEL_RSS.copy()
        if include_blogs:
            rss_sources.extend(TRAVEL_BLOG_RSS)
        
        articles = fetch_from_rss_list(rss_sources, max_results, destination_filter=destination)

    # Final deduplication and quality check
    seen_urls = set()
    seen_titles = set()
    dedup = []
    
    for article in articles:
        url = article.get("url", "")
        title = article.get("title", "")
        
        # Skip if we've seen this URL or very similar title
        if url and url in seen_urls:
            continue
        if title and title in seen_titles:
            continue
            
        # Additional quality checks
        if not title or len(title.strip()) < 10:
            continue
            
        seen_urls.add(url)
        seen_titles.add(title)
        dedup.append(article)
        
        if len(dedup) >= max_results:
            break

    return dedup

def get_travel_news_categories():
    """Return available travel news categories for filtering."""
    return [
        "travel",
        "tourism", 
        "vacation",
        "adventure travel",
        "budget travel",
        "luxury travel",
        "solo travel",
        "family travel",
        "cultural travel",
        "food travel",
        "eco travel",
        "business travel"
    ]