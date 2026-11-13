# Smart Grocery Manager

An AI assistant for a grocery store manager. 
## What it does
- Shows a store inventory dashboard (total products, items expiring
  soon, low stock, pending approvals).
- Lets the manager chat with an AI agent (Google Gemini) to ask things
  like "what is expiring soon?"
- The agent can check expiring items, check low stock, and suggest a
  discount for a product.

## Human-in-the-loop approval
The AI only suggests a discount. It cannot change a price by itself.
The suggestion goes to a "Pending Approvals" list, and the manager must
click Approve or Reject. Only then is the price changed.

## Tools used
Python, Streamlit, Google Gemini API

## Limits
This is a hackathon prototype. The inventory is sample data inside the
code (not a real database), so changes reset when the app restarts.

## How to run
1. pip install -r requirements.txt
2. Set your own Gemini API key as an environment variable named
   GEMINI_API_KEY
3. streamlit run app.py

