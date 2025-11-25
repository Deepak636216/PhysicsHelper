"""
Test script to verify Gemini API connection.
Run this to ensure your GOOGLE_API_KEY is configured correctly.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_gemini_connection():
    """Test basic Gemini API connection."""
    api_key = os.getenv("GOOGLE_API_KEY")

    if not api_key:
        print("❌ GOOGLE_API_KEY not found in environment variables")
        print("Please create a .env file with your API key:")
        print("GOOGLE_API_KEY=your_api_key_here")
        return False

    print(f"✅ GOOGLE_API_KEY found (length: {len(api_key)} characters)")

    try:
        from google import genai
        from google.genai import types

        # Initialize client
        client = genai.Client(api_key=api_key)
        print("✅ Genai client initialized successfully")

        # Test simple generation
        response = client.models.generate_content(
            model='gemini-2.0-flash-exp',
            contents='Say "Hello from JEE-Helper!" in one short sentence.'
        )

        print(f"✅ API call successful!")
        print(f"Response: {response.text}")
        return True

    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please install dependencies: pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Please check your API key and internet connection")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("JEE-Helper: Testing Gemini API Connection")
    print("=" * 60)

    success = test_gemini_connection()

    print("=" * 60)
    if success:
        print("✅ All checks passed! You're ready to proceed.")
    else:
        print("❌ Setup incomplete. Please fix the errors above.")
    print("=" * 60)
