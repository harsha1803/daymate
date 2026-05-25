import os
import base64
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY)

def encode_image(image_path: str) -> str:
    """Convert image to base64 for AI reading"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def read_bill(image_path: str) -> str:
    """Use Groq AI to read the bill image and extract items"""
    try:
        base64_image = encode_image(image_path)
        
        response = client.chat.completions.create(
            model="llama-3.2-11b-vision-preview",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        },
                        {
                            "type": "text",
                            "text": """Look at this restaurant bill carefully.
Extract ALL items with their prices.
Also find the total amount.
Format your response EXACTLY like this:

ITEMS:
- Item name: £X.XX
- Item name: £X.XX

TOTAL: £X.XX

If you cannot read the bill clearly, say UNREADABLE."""
                        }
                    ]
                }
            ],
            max_tokens=500
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        print(f"Bill reading error: {e}")
        return None

def split_bill(bill_text: str, num_people: int, tip_percent: int = 0) -> str:
    """Calculate how much each person owes"""
    try:
        prompt = f"""You are DayMate bill splitter.

Here is the bill:
{bill_text}

Number of people: {num_people}
Tip percentage: {tip_percent}%

Calculate:
1. Subtotal from items
2. Tip amount if any
3. Total with tip
4. Each person's share

Format your response EXACTLY like this:

🧾 *DayMate Bill Split*

📋 *Items:*
[list each item and price]

💰 *Subtotal:* £X.XX
🎁 *Tip ({tip_percent}%):* £X.XX  
💵 *Total:* £X.XX

👥 *Split {num_people} ways:*
Each person owes: *£X.XX*

Keep it clear and friendly!"""

        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        print(f"Split error: {e}")
        return "Sorry, couldn't split the bill. Please try again!"