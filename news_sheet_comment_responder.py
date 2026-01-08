"""
Google Sheet Comment Responder
- Reads comments from NEWS Google Sheet
- Matches to RSS feed for article context
- Generates AI response WITH article context
- Updates ChatGPT Suggestion column
"""

import requests
import json
import os
import re
import xml.etree.ElementTree as ET
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials

# ==================== CONFIG ====================

# Google Sheet
SHEET_ID = "11a-_IWhljPJHeKV8vdke-JiLmm_KCq-bedSceKB0kZI"
SHEET_NAME = "Comments"
GOOGLE_CREDS_FILE = "/Users/johnshay/jj_shay_takeaways/google_service_account.json"

# RSS Feed
RSS_FEED_URL = "https://rss.app/feeds/bJZbxhVRx0Xx77J3.xml"

# AI APIs - loaded from Google Sheet "API KEY" tab or environment
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
CLAUDE_API_KEY = os.environ.get("CLAUDE_API_KEY", "")
GROK_API_KEY = os.environ.get("GROK_API_KEY", "")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

# Column indices (0-based)
COL_DATE = 0          # A
COL_PROFILE_NAME = 1  # B
COL_ID = 2            # C
COL_TYPE = 4          # E
COL_TEXT = 5          # F
COL_PROFILE_URL = 6   # G
COL_PROFILE_ID = 7    # H
COL_USERNAME = 8      # I
COL_EMAIL = 9         # J
COL_INDUSTRY = 10     # K
COL_SUMMARY = 11      # L
COL_LOCATION = 12     # M
COL_COMPANY = 13      # N
COL_CHATGPT = 14      # O (ChatGPT Suggestion)
COL_POST_TITLE = 15   # P (Post Title - NEW)
COL_POST_CONTENT = 16 # Q (Post Content - NEW)

class NewsSheetResponder:
    def __init__(self):
        self.posts_cache = {}
        self.sheet = None
        self.spreadsheet = None
        self.api_keys = {}
        self.connect_sheet()
        self.load_api_keys()
        self.refresh_rss_feed()

    def connect_sheet(self):
        """Connect to Google Sheet"""
        try:
            scopes = [
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive'
            ]

            if os.path.exists(GOOGLE_CREDS_FILE):
                creds = Credentials.from_service_account_file(GOOGLE_CREDS_FILE, scopes=scopes)
                client = gspread.authorize(creds)
                self.spreadsheet = client.open_by_key(SHEET_ID)
                self.sheet = self.spreadsheet.worksheet(SHEET_NAME)
                print(f"✅ Connected to Google Sheet: {SHEET_NAME}")
            else:
                print(f"❌ Google credentials not found: {GOOGLE_CREDS_FILE}")
                print("Using local file mode...")

        except Exception as e:
            print(f"❌ Sheet connection error: {e}")
            self.sheet = None

    def load_api_keys(self):
        """Load API keys from 'API KEY' tab in Google Sheet"""
        global OPENAI_API_KEY, CLAUDE_API_KEY, GROK_API_KEY, GEMINI_API_KEY

        if not self.spreadsheet:
            print("⚠️ No spreadsheet connection, using environment variables for API keys")
            return

        try:
            api_sheet = self.spreadsheet.worksheet("API KEY")
            all_values = api_sheet.get_all_values()

            # Row 5 = Claude (index 4), Row 6 = ChatGPT (index 5)
            # Row 8 = Grok (index 7), Row 10 = Gemini (index 9)
            # Assuming key is in column B (index 1)

            if len(all_values) >= 6:
                CLAUDE_API_KEY = all_values[4][1] if len(all_values[4]) > 1 else ""
                OPENAI_API_KEY = all_values[5][1] if len(all_values[5]) > 1 else ""
            if len(all_values) >= 8:
                GROK_API_KEY = all_values[7][1] if len(all_values[7]) > 1 else ""
            if len(all_values) >= 10:
                GEMINI_API_KEY = all_values[9][1] if len(all_values[9]) > 1 else ""

            self.api_keys = {
                'chatgpt': OPENAI_API_KEY,
                'claude': CLAUDE_API_KEY,
                'grok': GROK_API_KEY,
                'gemini': GEMINI_API_KEY
            }

            print(f"🔑 API Keys loaded from sheet:")
            print(f"   ChatGPT (Row 6): {'✅' if OPENAI_API_KEY else '❌'}")
            print(f"   Claude (Row 5):  {'✅' if CLAUDE_API_KEY else '❌'}")
            print(f"   Grok (Row 8):    {'✅' if GROK_API_KEY else '❌'}")
            print(f"   Gemini (Row 10): {'✅' if GEMINI_API_KEY else '❌'}")

        except Exception as e:
            print(f"⚠️ Could not load API keys from sheet: {e}")
            print("   Using environment variables instead")

    def refresh_rss_feed(self):
        """Fetch and parse RSS feed for article context"""
        print("📰 Fetching RSS feed...")
        try:
            response = requests.get(RSS_FEED_URL, timeout=10)
            response.raise_for_status()

            root = ET.fromstring(response.content)

            for item in root.findall('.//item'):
                title = item.find('title')
                description = item.find('description')
                link = item.find('link')
                guid = item.find('guid')

                if link is not None:
                    post_url = link.text
                    post_data = {
                        "title": title.text if title is not None else "",
                        "description": self.clean_html(description.text) if description is not None else "",
                        "link": post_url,
                        "guid": guid.text if guid is not None else "",
                    }

                    # Store by URL
                    self.posts_cache[post_url] = post_data

                    # Extract activity ID from URL and store by that
                    activity_match = re.search(r'activity[:\-](\d+)', post_url)
                    if activity_match:
                        activity_id = activity_match.group(1)
                        self.posts_cache[activity_id] = post_data

                    # Also store by guid
                    if guid is not None and guid.text:
                        self.posts_cache[guid.text] = post_data

            print(f"   Loaded {len([k for k in self.posts_cache if k.isdigit()])} posts")

        except Exception as e:
            print(f"❌ RSS error: {e}")

    def clean_html(self, html_text):
        """Remove HTML tags"""
        if not html_text:
            return ""
        clean = re.sub(r'<[^>]+>', '', html_text)
        return ' '.join(clean.split())[:2000]

    def find_article_by_id(self, comment_id):
        """Find article in RSS by activity ID from comment"""
        # Extract activity ID from comment ID
        # Format: 7402396743583338497-ACoAABB7Kw8BOdPQnNzFg-L6jf8ThqBAM9AyyTs
        if not comment_id:
            return None

        # Try direct activity ID match
        activity_id = comment_id.split('-')[0] if '-' in str(comment_id) else str(comment_id)

        if activity_id in self.posts_cache:
            return self.posts_cache[activity_id]

        # Try partial match
        for key, data in self.posts_cache.items():
            if activity_id in key or key in activity_id:
                return data

        return None

    def generate_ai_response(self, article_context, comment_text, commenter_name, comment_type, profile_data=None):
        """Generate contextual AI response with profile data"""

        # Build prompt based on whether we have article context
        if article_context:
            context_text = f"""ORIGINAL ARTICLE/POST:
Title: {article_context.get('title', 'N/A')}
Content: {article_context.get('description', 'N/A')[:1500]}"""
        else:
            context_text = "ORIGINAL POST: [Article context not available]"

        # Build profile context
        profile_context = ""
        if profile_data:
            profile_parts = []
            if profile_data.get('industry'):
                profile_parts.append(f"Industry: {profile_data['industry']}")
            if profile_data.get('company'):
                profile_parts.append(f"Company: {profile_data['company']}")
            if profile_data.get('location'):
                profile_parts.append(f"Location: {profile_data['location']}")
            if profile_data.get('summary'):
                profile_parts.append(f"Bio: {profile_data['summary'][:300]}")

            if profile_parts:
                profile_context = f"\n\nABOUT {commenter_name.upper()}:\n" + "\n".join(profile_parts)

        if comment_type == 'reaction':
            prompt = f"""You are JJ Shay, a business AI influencer on LinkedIn.

{context_text}{profile_context}

Someone named {commenter_name} reacted to this post with a "{comment_text or 'like'}".

Write a brief, personalized LinkedIn comment (2-3 sentences) that:
1. Thanks them for engaging
2. References something specific from the article if available
3. Asks an insightful follow-up question tailored to their industry/background if known
4. Sounds authentic and conversational

Reply only with the response text."""

        else:  # comment
            prompt = f"""You are JJ Shay, a business AI influencer on LinkedIn.

{context_text}{profile_context}

COMMENT FROM {commenter_name}:
{comment_text}

Write a brief LinkedIn reply (2-3 sentences) that:
1. Directly addresses their specific point
2. References the original article topic for context
3. Adds an insightful perspective tailored to their industry/background if known
4. Encourages further discussion
5. Sounds authentic, not corporate

Reply only with the response text."""

        # Try ChatGPT (primary - Row 6)
        response = self.call_chatgpt(prompt)
        if response:
            return response, "ChatGPT"

        # Fallback to Claude (Row 5)
        response = self.call_claude(prompt)
        if response:
            return response, "Claude"

        # Fallback to Grok (Row 8)
        response = self.call_grok(prompt)
        if response:
            return response, "Grok"

        # Fallback to Gemini (Row 10)
        response = self.call_gemini(prompt)
        if response:
            return response, "Gemini"

        return self.template_response(comment_text, comment_type), "Template"

    def call_chatgpt(self, prompt):
        """Call ChatGPT API (Primary - Row 6)"""
        if not OPENAI_API_KEY:
            return None

        try:
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENAI_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "gpt-4o-mini",
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 250,
                    "temperature": 0.7
                },
                timeout=30
            )

            if response.status_code == 200:
                return response.json()['choices'][0]['message']['content'].strip()

        except Exception as e:
            print(f"   ChatGPT error: {e}")

        return None

    def call_claude(self, prompt):
        """Call Claude API (Backup - Row 5)"""
        if not CLAUDE_API_KEY:
            return None

        try:
            response = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": CLAUDE_API_KEY,
                    "anthropic-version": "2023-06-01",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "claude-3-haiku-20240307",
                    "max_tokens": 250,
                    "messages": [{"role": "user", "content": prompt}]
                },
                timeout=30
            )

            if response.status_code == 200:
                return response.json()['content'][0]['text'].strip()

        except Exception as e:
            print(f"   Claude error: {e}")

        return None

    def call_grok(self, prompt):
        """Call Grok/xAI API (Row 8)"""
        if not GROK_API_KEY:
            return None

        try:
            response = requests.post(
                "https://api.x.ai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {GROK_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "grok-3",
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 250,
                    "temperature": 0.7
                },
                timeout=30
            )

            if response.status_code == 200:
                return response.json()['choices'][0]['message']['content'].strip()

        except Exception as e:
            print(f"   Grok error: {e}")

        return None

    def call_gemini(self, prompt):
        """Call Gemini API"""
        if not GEMINI_API_KEY:
            return None

        try:
            response = requests.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_API_KEY}",
                headers={"Content-Type": "application/json"},
                json={
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {"maxOutputTokens": 250, "temperature": 0.7}
                },
                timeout=30
            )

            if response.status_code == 200:
                return response.json()['candidates'][0]['content']['parts'][0]['text'].strip()

        except Exception as e:
            print(f"   Gemini error: {e}")

        return None

    def template_response(self, comment_text, comment_type):
        """Fallback template response"""
        if comment_type == 'reaction':
            return "Thanks for engaging! I'd love to hear your thoughts on this topic. What aspect resonated most with you?"
        else:
            return "Great point! Thanks for adding to the conversation. What's your experience been with this?"

    def process_comments(self, update_sheet=False, limit=None):
        """Process comments and generate contextual responses"""

        if self.sheet:
            # Get all data from sheet
            all_data = self.sheet.get_all_values()
            headers = all_data[0]
            rows = all_data[1:]
        else:
            print("❌ No sheet connection")
            return

        processed = 0
        updated = 0

        for i, row in enumerate(rows):
            if limit and processed >= limit:
                break

            # Skip if already has a good response (optional: always regenerate)
            current_suggestion = row[COL_CHATGPT] if len(row) > COL_CHATGPT else ""

            # Get row data
            comment_id = row[COL_ID] if len(row) > COL_ID else ""
            comment_type = row[COL_TYPE].lower() if len(row) > COL_TYPE else ""
            comment_text = row[COL_TEXT] if len(row) > COL_TEXT else ""
            commenter_name = row[COL_PROFILE_NAME] if len(row) > COL_PROFILE_NAME else "Someone"

            # Extract profile data
            profile_data = {
                'industry': row[COL_INDUSTRY] if len(row) > COL_INDUSTRY else "",
                'summary': row[COL_SUMMARY] if len(row) > COL_SUMMARY else "",
                'location': row[COL_LOCATION] if len(row) > COL_LOCATION else "",
                'company': row[COL_COMPANY] if len(row) > COL_COMPANY else "",
            }

            # Skip reactions without meaningful processing (optional)
            if comment_type == 'reaction' and not comment_text:
                comment_text = "liked"

            print(f"\n{'='*50}")
            print(f"Row {i+2}: {commenter_name}")
            print(f"Type: {comment_type}")
            print(f"Text: {comment_text[:50]}...")
            if profile_data.get('industry') or profile_data.get('company'):
                print(f"👤 Profile: {profile_data.get('industry', '')} | {profile_data.get('company', '')}")

            # Find article context
            article = self.find_article_by_id(comment_id)
            if article:
                print(f"📰 Article: {article.get('title', 'Unknown')[:40]}...")
            else:
                print("⚠️ No article context found")

            # Generate response with profile data
            response, source = self.generate_ai_response(
                article,
                comment_text,
                commenter_name,
                comment_type,
                profile_data
            )

            print(f"💬 Response ({source}):")
            print(f"   {response[:100]}...")

            # Update sheet with response AND article context
            if update_sheet and self.sheet:
                try:
                    # Update Column O (ChatGPT Suggestion)
                    self.sheet.update(f"O{i+2}", [[response]])

                    # Update Column P (Post Title) and Q (Post Content)
                    if article:
                        post_title = article.get('title', '')[:500]
                        post_content = article.get('description', '')[:2000]
                        self.sheet.update(f"P{i+2}", [[post_title]])
                        self.sheet.update(f"Q{i+2}", [[post_content]])
                        print(f"✅ Updated O, P, Q for row {i+2}")
                    else:
                        print(f"✅ Updated O{i+2} (no article context for P, Q)")

                    updated += 1
                except Exception as e:
                    print(f"❌ Update error: {e}")

            processed += 1

        print(f"\n{'='*50}")
        print(f"Processed: {processed} comments")
        print(f"Updated: {updated} rows")

    def process_new_comments_only(self, update_sheet=True):
        """Only process comments without suggestions"""

        if not self.sheet:
            print("❌ No sheet connection")
            return

        all_data = self.sheet.get_all_values()
        rows = all_data[1:]  # Skip header
        new_count = 0

        for i, row in enumerate(rows):
            current_suggestion = row[COL_CHATGPT] if len(row) > COL_CHATGPT else ""

            # Skip if already has suggestion
            if current_suggestion and len(current_suggestion) > 20:
                continue

            # Process this row
            comment_id = row[COL_ID] if len(row) > COL_ID else ""
            comment_type = row[COL_TYPE].lower() if len(row) > COL_TYPE else ""
            comment_text = row[COL_TEXT] if len(row) > COL_TEXT else ""
            commenter_name = row[COL_PROFILE_NAME] if len(row) > COL_PROFILE_NAME else "Someone"

            # Extract profile data
            profile_data = {
                'industry': row[COL_INDUSTRY] if len(row) > COL_INDUSTRY else "",
                'summary': row[COL_SUMMARY] if len(row) > COL_SUMMARY else "",
                'location': row[COL_LOCATION] if len(row) > COL_LOCATION else "",
                'company': row[COL_COMPANY] if len(row) > COL_COMPANY else "",
            }

            if comment_type == 'reaction' and not comment_text:
                comment_text = "liked"

            print(f"\n🆕 New comment Row {i+2}: {commenter_name}")
            if profile_data.get('industry') or profile_data.get('company'):
                print(f"   👤 {profile_data.get('industry', '')} | {profile_data.get('company', '')}")

            article = self.find_article_by_id(comment_id)
            if article:
                print(f"   📰 {article.get('title', '')[:50]}...")

            response, source = self.generate_ai_response(
                article,
                comment_text,
                commenter_name,
                comment_type,
                profile_data
            )

            print(f"   💬 Response ({source}): {response[:80]}...")

            if update_sheet:
                try:
                    # Update Column O (ChatGPT Suggestion)
                    self.sheet.update(f"O{i+2}", [[response]])

                    # Update Column P (Post Title) and Q (Post Content)
                    if article:
                        post_title = article.get('title', '')[:500]
                        post_content = article.get('description', '')[:2000]
                        self.sheet.update(f"P{i+2}", [[post_title]])
                        self.sheet.update(f"Q{i+2}", [[post_content]])
                        print(f"   ✅ Updated O, P, Q")
                    else:
                        print(f"   ✅ Updated O (no article found)")

                    new_count += 1
                except Exception as e:
                    print(f"   ❌ Error: {e}")

        print(f"\n{'='*50}")
        print(f"Processed {new_count} new comments")


# ==================== ZAPIER WEBHOOK HANDLER ====================

def handle_zapier_webhook(comment_data):
    """
    Called by Zapier when new comment arrives.
    Add this as a webhook endpoint or run as cloud function.

    Expected comment_data fields:
    - id: Activity ID from LinkedIn
    - text: Comment text
    - profile_name: Commenter's name
    - type: 'comment' or 'reaction'
    - profile_industry: Industry from profile
    - profile_summary: Bio/summary
    - profile_location: Location
    - profile_company: Company name
    """
    responder = NewsSheetResponder()

    comment_id = comment_data.get('id', '')
    comment_text = comment_data.get('text', '')
    commenter_name = comment_data.get('profile_name', 'Someone')
    comment_type = comment_data.get('type', 'comment')

    # Extract profile data
    profile_data = {
        'industry': comment_data.get('profile_industry', ''),
        'summary': comment_data.get('profile_summary', ''),
        'location': comment_data.get('profile_location', ''),
        'company': comment_data.get('profile_company', ''),
    }

    # Find article
    article = responder.find_article_by_id(comment_id)

    # Generate response with profile context
    response, source = responder.generate_ai_response(
        article,
        comment_text,
        commenter_name,
        comment_type,
        profile_data
    )

    return {
        "suggested_response": response,
        "source": source,
        "article_found": article is not None,
        "article_title": article.get('title', '') if article else None,
        "post_content": article.get('description', '')[:500] if article else None
    }


# ==================== MAIN ====================

def setup_sheet_headers(responder):
    """Add Post Title and Post Content headers if missing"""
    if not responder.sheet:
        print("❌ No sheet connection")
        return

    try:
        headers = responder.sheet.row_values(1)
        updated = False

        # Check if we need to add headers
        while len(headers) < 17:
            headers.append("")

        if len(headers) <= COL_POST_TITLE or not headers[COL_POST_TITLE]:
            responder.sheet.update(f"P1", [["Post Title"]])
            print("✅ Added 'Post Title' header to column P")
            updated = True

        if len(headers) <= COL_POST_CONTENT or not headers[COL_POST_CONTENT]:
            responder.sheet.update(f"Q1", [["Post Content"]])
            print("✅ Added 'Post Content' header to column Q")
            updated = True

        if not updated:
            print("Headers already exist in columns P and Q")

    except Exception as e:
        print(f"❌ Error setting headers: {e}")


if __name__ == "__main__":
    print("\n" + "="*50)
    print("NEWS SHEET COMMENT RESPONDER")
    print("="*50)
    print("AI Cascade: ChatGPT → Claude → Grok → Gemini → Template")

    responder = NewsSheetResponder()

    print("\nOptions:")
    print("1. Process all comments (preview only)")
    print("2. Process all comments (update sheet)")
    print("3. Process NEW comments only (update sheet)")
    print("4. Test with single row")
    print("5. Setup new columns (Post Title, Post Content)")

    choice = input("\nChoice: ").strip()

    if choice == "1":
        responder.process_comments(update_sheet=False, limit=5)

    elif choice == "2":
        confirm = input("This will UPDATE the Google Sheet. Continue? (y/n): ")
        if confirm.lower() == 'y':
            responder.process_comments(update_sheet=True)

    elif choice == "3":
        responder.process_new_comments_only(update_sheet=True)

    elif choice == "4":
        row_num = int(input("Row number to test: "))
        responder.process_comments(update_sheet=False, limit=1)

    elif choice == "5":
        setup_sheet_headers(responder)
        print("\nNow run option 2 or 3 to populate the new columns")
