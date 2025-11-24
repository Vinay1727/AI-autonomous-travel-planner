import requests
import json
import re
from datetime import datetime, timedelta
import time
from typing import List, Dict, Optional
import sqlite3
class TrendingPlacesScraper:
    """
    Scraper for finding trending places and hashtags from social media
    Uses various APIs and techniques to gather trending travel data
    """
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # API endpoints (you'll need to replace with actual API keys)
        self.instagram_api_key = None  # Get from RapidAPI or official Instagram API
        self.twitter_api_key = None    # Get from Twitter API
    
    def get_trending_by_location(self, location: str, platform: str = "all") -> Dict:
        """
        Get trending hashtags and posts for a specific location
        
        Args:
            location: Location name (e.g., "Paris, France")
            platform: "instagram", "twitter", or "all"
        
        Returns:
            Dictionary with trending data
        """
        trending_data = {
            "location": location,
            "hashtags": [],
            "posts": [],
            "popularity_score": 0,
            "last_updated": datetime.now().isoformat()
        }
        
        try:
            if platform in ["instagram", "all"]:
                instagram_data = self._scrape_instagram_location(location)
                trending_data["hashtags"].extend(instagram_data.get("hashtags", []))
                trending_data["posts"].extend(instagram_data.get("posts", []))
            
            if platform in ["twitter", "all"]:
                twitter_data = self._scrape_twitter_location(location)
                trending_data["hashtags"].extend(twitter_data.get("hashtags", []))
                trending_data["posts"].extend(twitter_data.get("posts", []))
            
            # Remove duplicates and sort by popularity
            trending_data["hashtags"] = self._deduplicate_hashtags(trending_data["hashtags"])
            trending_data["popularity_score"] = len(trending_data["posts"])
            
        except Exception as e:
            print(f"Error scraping data for {location}: {str(e)}")
        
        return trending_data
    
    def _scrape_instagram_location(self, location: str) -> Dict:
        """
        Scrape Instagram data for a location (requires API key or alternative method)
        """
        # Method 1: Using Instagram Basic Display API (requires API key)
        if self.instagram_api_key:
            return self._instagram_api_request(location)
        
        # Method 2: Using public Instagram location data (limited)
        return self._instagram_public_scrape(location)
    
    def _instagram_api_request(self, location: str) -> Dict:
        """
        Use Instagram API to get location-based content
        """
        try:
            # This is a placeholder for Instagram API integration
            # You'll need to implement actual Instagram API calls
            api_url = f"https://graph.instagram.com/v12.0/ig_hashtag_search"
            params = {
                'user_id': 'YOUR_USER_ID',
                'q': location.replace(' ', ''),
                'access_token': self.instagram_api_key
            }
            
            response = requests.get(api_url, params=params, headers=self.headers)
            if response.status_code == 200:
                data = response.json()
                return self._process_instagram_data(data)
            
        except Exception as e:
            print(f"Instagram API error: {str(e)}")
        
        return {"hashtags": [], "posts": []}
    
    def _instagram_public_scrape(self, location: str) -> Dict:
        """
        Alternative method using public Instagram data
        Note: This is for educational purposes - respect Instagram's terms of service
        """
        hashtags = []
        posts = []
        
        try:
            # Generate location-based hashtags
            location_parts = location.lower().replace(',', '').split()
            base_hashtags = [
                f"#{part}" for part in location_parts if len(part) > 2
            ]
            
            # Add common travel hashtags for the location
            travel_hashtags = [
                f"#visit{location_parts[0]}" if location_parts else "#travel",
                f"#{location_parts[0]}travel" if location_parts else "#wanderlust",
                "#instatravel", "#photography", "#explore", "#adventure"
            ]
            
            hashtags = base_hashtags + travel_hashtags
            
            # Mock posts data (in real implementation, you'd scrape actual data)
            posts = [
                {
                    "id": f"ig_post_{i}",
                    "caption": f"Amazing {location}! #{hashtags[0] if hashtags else 'travel'}",
                    "hashtags": hashtags[:3],
                    "likes": 150 + i * 10,
                    "platform": "instagram"
                }
                for i in range(3)
            ]
            
        except Exception as e:
            print(f"Instagram scraping error: {str(e)}")
        
        return {"hashtags": hashtags, "posts": posts}
    
    def _scrape_twitter_location(self, location: str) -> Dict:
        """
        Scrape Twitter data for a location
        """
        if self.twitter_api_key:
            return self._twitter_api_request(location)
        else:
            return self._twitter_public_scrape(location)
    
    def _twitter_api_request(self, location: str) -> Dict:
        """
        Use Twitter API v2 to get location-based tweets
        """
        try:
            api_url = "https://api.twitter.com/2/tweets/search/recent"
            query = f"{location} (travel OR vacation OR visit) -is:retweet"
            
            params = {
                'query': query,
                'max_results': 10,
                'tweet.fields': 'public_metrics,created_at,entities'
            }
            
            headers = {
                **self.headers,
                'Authorization': f'Bearer {self.twitter_api_key}'
            }
            
            response = requests.get(api_url, params=params, headers=headers)
            if response.status_code == 200:
                data = response.json()
                return self._process_twitter_data(data)
                
        except Exception as e:
            print(f"Twitter API error: {str(e)}")
        
        return {"hashtags": [], "posts": []}
    
    def _twitter_public_scrape(self, location: str) -> Dict:
        """
        Alternative method for Twitter data (limited)
        """
        hashtags = []
        posts = []
        
        try:
            # Generate location-based hashtags
            location_clean = re.sub(r'[^a-zA-Z0-9\s]', '', location)
            location_parts = location_clean.lower().split()
            
            hashtags = [
                f"#{part}travel" for part in location_parts[:2] if len(part) > 2
            ] + [
                "#travel", "#vacation", "#wanderlust", "#explore"
            ]
            
            # Mock Twitter posts
            posts = [
                {
                    "id": f"tw_post_{i}",
                    "text": f"Just visited {location}! Amazing experience! {hashtags[0] if hashtags else '#travel'}",
                    "hashtags": hashtags[:2],
                    "retweets": 20 + i * 5,
                    "likes": 50 + i * 15,
                    "platform": "twitter"
                }
                for i in range(3)
            ]
            
        except Exception as e:
            print(f"Twitter scraping error: {str(e)}")
        
        return {"hashtags": hashtags, "posts": posts}
    
    def _process_instagram_data(self, data: Dict) -> Dict:
        """Process Instagram API response data"""
        hashtags = []
        posts = []
        
        try:
            if 'data' in data:
                for item in data['data'][:5]:  # Limit to 5 items
                    if 'name' in item:
                        hashtags.append(f"#{item['name']}")
            
            # Extract posts if available
            # Implementation depends on specific API response structure
            
        except Exception as e:
            print(f"Error processing Instagram data: {str(e)}")
        
        return {"hashtags": hashtags, "posts": posts}
    
    def _process_twitter_data(self, data: Dict) -> Dict:
        """Process Twitter API response data"""
        hashtags = []
        posts = []
        
        try:
            if 'data' in data:
                for tweet in data['data']:
                    # Extract hashtags from entities
                    if 'entities' in tweet and 'hashtags' in tweet['entities']:
                        for hashtag in tweet['entities']['hashtags']:
                            hashtags.append(f"#{hashtag['tag']}")
                    
                    # Create post object
                    post = {
                        "id": tweet['id'],
                        "text": tweet['text'][:100] + "..." if len(tweet['text']) > 100 else tweet['text'],
                        "created_at": tweet.get('created_at', ''),
                        "platform": "twitter"
                    }
                    
                    if 'public_metrics' in tweet:
                        post.update({
                            "likes": tweet['public_metrics'].get('like_count', 0),
                            "retweets": tweet['public_metrics'].get('retweet_count', 0)
                        })
                    
                    posts.append(post)
                    
        except Exception as e:
            print(f"Error processing Twitter data: {str(e)}")
        
        return {"hashtags": hashtags, "posts": posts}
    
    def _deduplicate_hashtags(self, hashtags: List[str]) -> List[Dict]:
        """
        Remove duplicate hashtags and count frequency
        """
        hashtag_count = {}
        
        for hashtag in hashtags:
            hashtag_clean = hashtag.lower().strip('#')
            if hashtag_clean:
                hashtag_count[hashtag_clean] = hashtag_count.get(hashtag_clean, 0) + 1
        
        # Sort by frequency and return top hashtags
        sorted_hashtags = sorted(
            hashtag_count.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        return [
            {"hashtag": hashtag, "count": count}
            for hashtag, count in sorted_hashtags[:10]
        ]
    
    def get_global_trending_destinations(self) -> List[Dict]:
        """
        Get globally trending travel destinations
        """
        # Popular destinations to check
        popular_destinations = [
            "Paris, France", "Tokyo, Japan", "New York, USA", "London, UK",
            "Rome, Italy", "Barcelona, Spain", "Bangkok, Thailand", "Sydney, Australia",
            "Dubai, UAE", "Istanbul, Turkey", "Bali, Indonesia", "Santorini, Greece",
            "Prague, Czech Republic", "Amsterdam, Netherlands", "Vienna, Austria"
        ]
        
        trending_destinations = []
        
        for destination in popular_destinations[:5]:  # Limit to avoid rate limits
            destination_data = self.get_trending_by_location(destination)
            destination_data["trending_score"] = self._calculate_trending_score(destination_data)
            trending_destinations.append(destination_data)
            
            # Add delay to avoid rate limiting
            time.sleep(1)
        
        # Sort by trending score
        trending_destinations.sort(key=lambda x: x["trending_score"], reverse=True)
        
        return trending_destinations
    
    def _calculate_trending_score(self, destination_data: Dict) -> float:
        """
        Calculate a trending score based on various factors
        """
        score = 0
        
        # Base score from number of hashtags
        score += len(destination_data.get("hashtags", [])) * 2
        
        # Score from number of posts
        score += destination_data.get("popularity_score", 0) * 0.5
        
        # Bonus for recent activity (you'd implement this with real timestamps)
        score += 10  # Mock bonus
        
        return score
    
    def search_trending_hashtags_by_category(self, category: str) -> List[str]:
        """
        Get trending hashtags by travel category
        """
        category_hashtags = {
            "adventure": ["#adventure", "#hiking", "#climbing", "#extreme", "#outdoors"],
            "beach": ["#beach", "#ocean", "#paradise", "#tropical", "#island"],
            "city": ["#citybreak", "#urban", "#architecture", "#nightlife", "#culture"],
            "food": ["#foodie", "#cuisine", "#localfood", "#restaurant", "#streetfood"],
            "luxury": ["#luxury", "#resort", "#spa", "#finedining", "#exclusive"],
            "budget": ["#backpacking", "#budgettravel", "#hostels", "#cheaptravel", "#solo"],
            "nature": ["#nature", "#wildlife", "#national park", "#scenic", "#landscape"],
            "history": ["#history", "#heritage", "#museum", "#ancient", "#historical"]
        }
        
        return category_hashtags.get(category.lower(), ["#travel"])

# Integration class for the community app
class TrendingIntegration:
    """
    Integration class to connect trending data with the community app
    """
    
    def __init__(self, community_db):
        self.scraper = TrendingPlacesScraper()
        self.db = community_db
    
    def update_trending_places(self):
        """
        Update the database with current trending places data
        """
        trending_destinations = self.scraper.get_global_trending_destinations()
        
        # Store trending data in a simple cache table
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        # Create trending cache table if not exists
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trending_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                location TEXT NOT NULL,
                trending_data TEXT NOT NULL,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Clear old data
        cursor.execute('DELETE FROM trending_cache')
        
        # Insert new trending data
        for destination in trending_destinations:
            cursor.execute('''
                INSERT INTO trending_cache (location, trending_data)
                VALUES (?, ?)
            ''', (destination['location'], json.dumps(destination)))
        
        conn.commit()
        conn.close()
    
    def get_cached_trending_places(self) -> List[Dict]:
        """
        Get cached trending places data
        """
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT location, trending_data FROM trending_cache
            ORDER BY updated_at DESC
        ''')
        
        results = cursor.fetchall()
        conn.close()
        
        trending_places = []
        for location, data_json in results:
            try:
                data = json.loads(data_json)
                trending_places.append(data)
            except:
                continue
        
        return trending_places

# Usage example
if __name__ == "__main__":
    scraper = TrendingPlacesScraper()
    
    # Test getting trending data for a location
    paris_data = scraper.get_trending_by_location("Paris, France")
    print("Paris trending data:", json.dumps(paris_data, indent=2))
    
    # Test global trending destinations
    global_trending = scraper.get_global_trending_destinations()
    print("\nGlobal trending destinations:")
    for destination in global_trending:
        print(f"- {destination['location']}: Score {destination['trending_score']}")
    
    # Test category hashtags
    adventure_hashtags = scraper.search_trending_hashtags_by_category("adventure")
    print(f"\nAdventure hashtags: {adventure_hashtags}")