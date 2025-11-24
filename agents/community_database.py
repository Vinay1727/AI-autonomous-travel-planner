import sqlite3
import hashlib
from datetime import datetime
import json

class CommunityDatabase:
    def __init__(self, db_path="travel_community.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize all community-related tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                profile_pic TEXT DEFAULT NULL,
                bio TEXT DEFAULT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1
            )
        ''')
        
        # Posts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                image_url TEXT NOT NULL,
                caption TEXT NOT NULL,
                hashtags TEXT DEFAULT NULL,
                location_name TEXT DEFAULT NULL,
                lat REAL DEFAULT NULL,
                lon REAL DEFAULT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        # Likes table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS likes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                post_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(post_id, user_id),
                FOREIGN KEY (post_id) REFERENCES posts(id),
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        # Comments table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                post_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                comment TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1,
                FOREIGN KEY (post_id) REFERENCES posts(id),
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        # Trending hashtags tracking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS hashtag_trends (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                hashtag TEXT NOT NULL,
                usage_count INTEGER DEFAULT 1,
                last_used DATETIME DEFAULT CURRENT_TIMESTAMP,
                week_start DATE NOT NULL
            )
        ''')
        
        # User sessions (for login management)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                session_token TEXT UNIQUE NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                expires_at DATETIME NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def create_user(self, username, email, password, bio=None):
        """Create a new user account"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Hash password
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        try:
            cursor.execute('''
                INSERT INTO users (username, email, password_hash, bio)
                VALUES (?, ?, ?, ?)
            ''', (username, email, password_hash, bio))
            user_id = cursor.lastrowid
            conn.commit()
            return user_id
        except sqlite3.IntegrityError as e:
            return None
        finally:
            conn.close()
    
    def authenticate_user(self, username, password):
        """Authenticate user login"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        cursor.execute('''
            SELECT id, username, email FROM users 
            WHERE username = ? AND password_hash = ? AND is_active = 1
        ''', (username, password_hash))
        
        user = cursor.fetchone()
        conn.close()
        
        if user:
            return {"id": user[0], "username": user[1], "email": user[2]}
        return None
    
    def create_post(self, user_id, image_url, caption, hashtags=None, location_name=None, lat=None, lon=None):
        """Create a new post"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Convert hashtags list to JSON string
        hashtags_json = json.dumps(hashtags) if hashtags else None
        
        cursor.execute('''
            INSERT INTO posts (user_id, image_url, caption, hashtags, location_name, lat, lon)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, image_url, caption, hashtags_json, location_name, lat, lon))
        
        post_id = cursor.lastrowid
        
        # Update hashtag trends
        if hashtags:
            self._update_hashtag_trends(cursor, hashtags)
        
        conn.commit()
        conn.close()
        return post_id
    
    def get_feed_posts(self, limit=20, offset=0):
        """Get posts for main feed"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT p.id, p.image_url, p.caption, p.hashtags, p.location_name, 
                   p.created_at, u.username, u.profile_pic,
                   COUNT(l.id) as like_count,
                   COUNT(c.id) as comment_count
            FROM posts p
            JOIN users u ON p.user_id = u.id
            LEFT JOIN likes l ON p.id = l.post_id
            LEFT JOIN comments c ON p.id = c.post_id AND c.is_active = 1
            WHERE p.is_active = 1
            GROUP BY p.id
            ORDER BY p.created_at DESC
            LIMIT ? OFFSET ?
        ''', (limit, offset))
        
        posts = cursor.fetchall()
        conn.close()
        
        return [self._format_post(post) for post in posts]
    
    def get_trending_hashtags(self, limit=10):
        """Get trending hashtags for current week"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get current week start (Monday)
        from datetime import date, timedelta
        today = date.today()
        week_start = today - timedelta(days=today.weekday())
        
        cursor.execute('''
            SELECT hashtag, SUM(usage_count) as total_usage
            FROM hashtag_trends
            WHERE week_start >= ?
            GROUP BY hashtag
            ORDER BY total_usage DESC
            LIMIT ?
        ''', (week_start, limit))
        
        trends = cursor.fetchall()
        conn.close()
        
        return [{"hashtag": row[0], "count": row[1]} for row in trends]
    
    def like_post(self, post_id, user_id):
        """Like or unlike a post"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if already liked
        cursor.execute('''
            SELECT id FROM likes WHERE post_id = ? AND user_id = ?
        ''', (post_id, user_id))
        
        existing_like = cursor.fetchone()
        
        if existing_like:
            # Unlike
            cursor.execute('''
                DELETE FROM likes WHERE post_id = ? AND user_id = ?
            ''', (post_id, user_id))
            liked = False
        else:
            # Like
            cursor.execute('''
                INSERT INTO likes (post_id, user_id) VALUES (?, ?)
            ''', (post_id, user_id))
            liked = True
        
        conn.commit()
        conn.close()
        return liked
    
    def add_comment(self, post_id, user_id, comment):
        """Add a comment to a post"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO comments (post_id, user_id, comment)
            VALUES (?, ?, ?)
        ''', (post_id, user_id, comment))
        
        comment_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return comment_id
    
    def get_post_comments(self, post_id, limit=50):
        """Get comments for a specific post"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT c.comment, c.created_at, u.username, u.profile_pic
            FROM comments c
            JOIN users u ON c.user_id = u.id
            WHERE c.post_id = ? AND c.is_active = 1
            ORDER BY c.created_at ASC
            LIMIT ?
        ''', (post_id, limit))
        
        comments = cursor.fetchall()
        conn.close()
        
        return [{"comment": row[0], "created_at": row[1], 
                "username": row[2], "profile_pic": row[3]} for row in comments]
    
    def get_user_profile(self, username):
        """Get user profile information"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT u.id, u.username, u.email, u.profile_pic, u.bio, u.created_at,
                   COUNT(p.id) as post_count
            FROM users u
            LEFT JOIN posts p ON u.id = p.user_id AND p.is_active = 1
            WHERE u.username = ? AND u.is_active = 1
            GROUP BY u.id
        ''', (username,))
        
        user = cursor.fetchone()
        conn.close()
        
        if user:
            return {
                "id": user[0], "username": user[1], "email": user[2],
                "profile_pic": user[3], "bio": user[4], "created_at": user[5],
                "post_count": user[6]
            }
        return None
    
    def _update_hashtag_trends(self, cursor, hashtags):
        """Update hashtag trend tracking"""
        from datetime import date, timedelta
        
        today = date.today()
        week_start = today - timedelta(days=today.weekday())
        
        for hashtag in hashtags:
            hashtag = hashtag.lower().strip('#')
            
            cursor.execute('''
                SELECT id FROM hashtag_trends 
                WHERE hashtag = ? AND week_start = ?
            ''', (hashtag, week_start))
            
            existing = cursor.fetchone()
            
            if existing:
                cursor.execute('''
                    UPDATE hashtag_trends 
                    SET usage_count = usage_count + 1, last_used = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (existing[0],))
            else:
                cursor.execute('''
                    INSERT INTO hashtag_trends (hashtag, week_start)
                    VALUES (?, ?)
                ''', (hashtag, week_start))
    
    def _format_post(self, post_row):
        """Format post data for display"""
        return {
            "id": post_row[0],
            "image_url": post_row[1],
            "caption": post_row[2],
            "hashtags": json.loads(post_row[3]) if post_row[3] else [],
            "location_name": post_row[4],
            "created_at": post_row[5],
            "username": post_row[6],
            "profile_pic": post_row[7],
            "like_count": post_row[8],
            "comment_count": post_row[9]
        }

# Initialize database
if __name__ == "__main__":
    db = CommunityDatabase()
    print("Community database initialized successfully!")