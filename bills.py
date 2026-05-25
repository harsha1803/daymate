import os
import base64
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY)

def encode_image(image_path: str) -> str:
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def read_bill_items(image_path: str) -> list:
    """Read bill and return list of items with prices"""
    try:
        base64_image = encode_image(image_path)
        response = client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                        },
                        {
                            "type": "text",
                            "text": """Look at this receipt carefully.
List every item with its price.
Respond ONLY in this exact JSON format, nothing else:
{"items": [{"name": "Item Name", "price": 1.99}, {"name": "Item 2", "price": 2.49}], "total": 15.50}
If unreadable respond with: {"error": "unreadable"}"""
                        }
                    ]
                }
            ],
            max_tokens=500
        )
        import json
        text = response.choices[0].message.content.strip()
        # Clean any markdown
        text = text.replace("```json", "").replace("```", "").strip()
        data = json.loads(text)
        return data
    except Exception as e:
        print(f"Bill reading error: {e}")
        return None

def calculate_smart_split(assignments: dict, tip_percent: int = 0) -> str:
    """Calculate what each person owes based on their items"""
    try:
        totals = {}
        item_lines = []

        for item_name, (price, person) in assignments.items():
            if person.lower() == "shared" or "," in person:
                # Split between multiple people
                people = [p.strip() for p in person.split(",")]
                share = price / len(people)
                for p in people:
                    p = p.strip()
                    totals[p] = totals.get(p, 0) + share
                item_lines.append(f"- {item_name} £{price:.2f} → shared by {', '.join(people)}")
            else:
                totals[person] = totals.get(person, 0) + price
                item_lines.append(f"- {item_name} £{price:.2f} → {person}")

        subtotal = sum(totals.values())
        tip_amount = subtotal * (tip_percent / 100)

        # Apply tip proportionally
        result = "🧾 *DayMate Smart Bill Split*\n\n"
        result += "📋 *Items:*\n"
        result += "\n".join(item_lines)
        result += f"\n\n💰 *Subtotal:* £{subtotal:.2f}"
        result += f"\n🎁 *Tip ({tip_percent}%):* £{tip_amount:.2f}"
        result += f"\n💵 *Total:* £{subtotal + tip_amount:.2f}\n"
        result += "\n👤 *Each person owes:*\n"

        for person, amount in totals.items():
            tip_share = amount * (tip_percent / 100)
            result += f"• *{person}:* £{amount + tip_share:.2f}\n"

        return result

    except Exception as e:
        print(f"Split error: {e}")
        return "Sorry, couldn't calculate the split. Please try again!"

def split_bill_equal(bill_data: dict, num_people: int, tip_percent: int = 0) -> str:
    """Equal split fallback"""
    try:
        items = bill_data.get("items", [])
        total = bill_data.get("total", sum(i["price"] for i in items))
        tip = total * (tip_percent / 100)
        final = total + tip
        per_person = final / num_people

        result = "🧾 *DayMate Bill Split*\n\n📋 *Items:*\n"
        for item in items:
            result += f"- {item['name']}: £{item['price']:.2f}\n"
        result += f"\n💰 *Subtotal:* £{total:.2f}"
        result += f"\n🎁 *Tip ({tip_percent}%):* £{tip:.2f}"
        result += f"\n💵 *Total:* £{final:.2f}\n"
        result += f"\n👥 *Split {num_people} ways:*\n"
        result += f"Each person owes: *£{per_person:.2f}*"
        return result
    except Exception as e:
        return "Sorry, couldn't split the bill!"