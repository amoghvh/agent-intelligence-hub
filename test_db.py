import os
from dotenv import load_dotenv
from supabase import create_client

# Load keys
load_dotenv()
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

# Connect
supabase = create_client(url, key)

def test_connection():
    print("🚀 Attempting to connect to Supabase...")
    data = {
        "ticker": "AAPL",
        "summary": "Connection test successful!",
        "sentiment": "Bullish"
    }
    try:
        response = supabase.table("market_research").insert(data).execute()
        print("✅ Success! Data sent to the cloud.")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_connection()