import os
import requests
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

NEWS_API_KEY = os.getenv("NEWS_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

client = Groq(api_key=GROQ_API_KEY)

def fetch_news(interests: str) -> str:
    """Fetch news headlines based on user interests"""
    try:
        # Build search query from interests
        query = interests.replace(",", " OR ")
        
        url = "https://newsapi.org/v2/everything"
        params = {
            "q": query,
            "language": "en",
            "sortBy": "publishedAt",
            "pageSize": 10,
            "apiKey": NEWS_API_KEY
        }
        
        response = requests.get(url, params=params)
        data = response.json()
        
        if data["status"] != "ok":
            return None
            
        articles = data["articles"][:10]
        
        # Format headlines for AI
        headlines = ""
        for i, article in enumerate(articles, 1):
            headlines += f"{i}. {article['title']} — {article['source']['name']}\n"
            
        return headlines
        
    except Exception as e:
        print(f"News fetch error: {e}")
        return None

def summarise_news(interests: str, headlines: str) -> str:
    """Use Groq AI to summarise headlines into a morning briefing"""
    try:
        prompt = f"""You are DayMate, a friendly AI morning briefing assistant.
        
The user is interested in: {interests}

Here are today's top headlines:
{headlines}

Create a friendly, engaging morning briefing with exactly 5 bullet points.
Each bullet should be one clear sentence summarising the key news.
Start with "🌤️ Good morning! Here's your DayMate briefing for today:"
End with "Have a great day! 🚀"
Keep it upbeat and concise."""

        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        print(f"Groq error: {e}")
        return "Sorry, couldn't generate your briefing today. Try again later!"

def get_morning_briefing(interests: str) -> str:
    """Main function — fetch news and summarise it"""
    print(f"Fetching news for: {interests}")
    
    headlines = fetch_news(interests)
    
    if not headlines:
        return "⚠️ Couldn't fetch news right now. Please try again later!"
    
    briefing = summarise_news(interests, headlines)
    return briefing