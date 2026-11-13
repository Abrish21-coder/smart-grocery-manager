from google import genai
from google.genai import types

client = genai.Client()

inventory = [
    {"name": "Whole Milk 1L", "price": 250, "stock": 40, "expiry_days": 2},
    {"name": "Brown Bread", "price": 150, "stock": 15, "expiry_days": 1},
    {"name": "Basmati Rice 5kg", "price": 1200, "stock": 60, "expiry_days": 180},
    {"name": "Yogurt 500g", "price": 180, "stock": 8, "expiry_days": 3},
    {"name": "Eggs (dozen)", "price": 320, "stock": 5, "expiry_days": 10},
    {"name": "Chicken Breast 1kg", "price": 650, "stock": 12, "expiry_days": 2},
    {"name": "Bananas (dozen)", "price": 200, "stock": 25, "expiry_days": 4},
    {"name": "Tomatoes 1kg", "price": 120, "stock": 30, "expiry_days": 5},
    {"name": "Onions 1kg", "price": 90, "stock": 50, "expiry_days": 20},
    {"name": "Potatoes 1kg", "price": 100, "stock": 45, "expiry_days": 25},
    {"name": "Cheddar Cheese 200g", "price": 450, "stock": 6, "expiry_days": 7},
    {"name": "Butter 250g", "price": 380, "stock": 10, "expiry_days": 30},
    {"name": "Cooking Oil 1L", "price": 550, "stock": 35, "expiry_days": 120},
    {"name": "Sugar 1kg", "price": 180, "stock": 40, "expiry_days": 200},
    {"name": "Tea Pack 400g", "price": 420, "stock": 22, "expiry_days": 365},
    {"name": "Coca-Cola 1.5L", "price": 220, "stock": 18, "expiry_days": 90},
    {"name": "Orange Juice 1L", "price": 280, "stock": 9, "expiry_days": 4},
    {"name": "Cereal Box 500g", "price": 480, "stock": 14, "expiry_days": 150},
    {"name": "Biscuits Pack", "price": 150, "stock": 3, "expiry_days": 60},
    {"name": "Frozen Peas 500g", "price": 200, "stock": 17, "expiry_days": 180},
    {"name": "Detergent Powder 1kg", "price": 350, "stock": 20, "expiry_days": 365},
    {"name": "Toothpaste 100g", "price": 220, "stock": 4, "expiry_days": 365},
    {"name": "Apples 1kg", "price": 280, "stock": 28, "expiry_days": 6},
    {"name": "Spinach Bunch", "price": 80, "stock": 7, "expiry_days": 1},
]


pending_actions = []  # holds AI suggestions waiting for human approval

def check_expiring_items(days_threshold: int) -> str:
    """Lists products expiring within the given number of days."""
    matches = [p for p in inventory if p["expiry_days"] <= days_threshold]
    if not matches:
        return "No products are expiring within that window."
    return "\n".join(f"{p['name']} - expires in {p['expiry_days']} days, stock: {p['stock']}" for p in matches)

def check_low_stock(threshold: int) -> str:
    """Lists products with stock below the given threshold."""
    matches = [p for p in inventory if p["stock"] < threshold]
    if not matches:
        return "No products are low on stock."
    return "\n".join(f"{p['name']} - only {p['stock']} units left" for p in matches)

def recommend_discount(product_name: str) -> str:
    """Suggests a safe discount (10-50% capped) and queues it for human approval — does NOT apply it."""
    product = next((p for p in inventory if p["name"].lower() == product_name.lower()), None)
    if not product:
        return f"No product found matching '{product_name}'."
    days = product["expiry_days"]
    if days <= 1: discount = 50
    elif days <= 3: discount = 30
    elif days <= 7: discount = 15
    else: discount = 10
    discount = max(10, min(discount, 50))
    pending_actions.append({"product": product["name"], "discount": discount})
    return f"Suggested: {discount}% discount on {product['name']} (expires in {days} days). Awaiting manager approval."

# IMPORTANT: apply_action is NOT given to the AI as a tool.
# It only runs when a human clicks "Approve" in the UI — this is the human-in-the-loop boundary.
def apply_action(index: int) -> str:
    action = pending_actions.pop(index)
    product = next((p for p in inventory if p["name"] == action["product"]), None)
    if product:
        new_price = round(product["price"] * (1 - action["discount"] / 100))
        product["price"] = new_price
        return f"Approved: {product['name']} now {new_price} (was {action['discount']}% off)"
    return "Product not found."

system_instruction = (
    "You are a store operations assistant for a grocery/mall management system. "
    "Help the manager monitor inventory, flag expiring products, and suggest safe "
    "discounts. Always use the available tools for real data instead of guessing."
)

chat = client.chats.create(
    model="gemini-2.5-flash",
    config=types.GenerateContentConfig(
        system_instruction=system_instruction,
        tools=[check_expiring_items, check_low_stock, recommend_discount],
    ),
)

def run_agent(query: str) -> str:
    """This is the function your friend's UI will call."""
    response = chat.send_message(query)
    return response.text

if __name__ == "__main__":
    print("Store Agent ready. Type a question (or 'quit' to exit).\n")
    while True:
        user_input = input("You: ")
        if user_input.lower() == "quit":
            break
        print("Agent:", run_agent(user_input), "\n")