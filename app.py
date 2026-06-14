import streamlit as st
from google import genai
from google.genai import types

# --- 1. THE EXPANDED MOCK DATABASE ---
# --- 1. THE EXPANDED MOCK DATABASE ---
order_database = {
    "1042": {"status": "Shipped", "arrival": "Tomorrow by 5:00 PM", "courier": "FedEx", "item": "Wireless Keyboard", "price": 49.99},
    "8891": {"status": "Processing", "arrival": "Next Tuesday", "courier": "UPS", "item": "Coffee Maker", "price": 89.50},
    "0012": {"status": "Delivered", "arrival": "Yesterday", "courier": "USPS", "item": "Running Shoes", "price": 120.00},
    "5533": {"status": "Delayed", "arrival": "Unknown (Weather delay)", "courier": "DHL", "item": "Winter Jacket", "price": 150.00},
    "9921": {"status": "Out for Delivery", "arrival": "Today by 8:00 PM", "courier": "FedEx", "item": "Smartphone Case", "price": 19.99},
    "7744": {"status": "Cancelled", "arrival": "N/A", "courier": "N/A", "item": "Desk Lamp", "price": 35.00}
}

# --- 2. THE BACKEND TOOL ---
# --- 2. THE BACKEND TOOL ---
def get_order_status(order_id: str) -> str:
    """Fetches the status of a customer order based on the order ID."""
    if order_id in order_database:
        order = order_database[order_id]
        if order["status"] == "Cancelled":
            return f"System Log: Order {order_id} ({order['item']}) was cancelled."
        return f"System Log: Order {order_id} ({order['item']}) is {order['status']}. Arriving {order['arrival']} via {order['courier']}."
    return f"System Log: Could not find order {order_id} in the database."

def get_account_summary() -> str:
    """Fetches a full summary of the user's account, including total orders, items purchased, and total amount spent."""
    total_orders = len(order_database)
    
    # Calculate total spent, ensuring we do NOT charge the user for cancelled orders!
    total_spent = sum(order["price"] for order in order_database.values() if order["status"] != "Cancelled")
    
    # Create a readable list of all order IDs, items, and their prices
    order_details = [f"#{oid} ({order['item']} - ${order['price']})" for oid, order in order_database.items()]
    details_str = ", ".join(order_details)
    
    return f"System Log: Found {total_orders} orders: {details_str}. Total amount spent (excluding cancelled items) is ${total_spent:.2f}."
# --- 3. FRONTEND UI SETUP (Streamlit) ---
st.set_page_config(page_title="Agentic Support", page_icon="🤖", layout="centered")
st.title("📦 Agentic Customer Support")
st.markdown("Ask me about your order status! *(Try asking: 'Where is my Winter Jacket, order 5533?' or 'Check order 1042')*")

# Securely ask for the API Key in the sidebar for public deployment
with st.sidebar:
    st.header("⚙️ Configuration")
    api_key = st.text_input("Enter your Gemini API Key", type="password", help="Get this from Google AI Studio")
    st.markdown("---")
    st.markdown("**Available Test Orders:**")
    for oid, details in order_database.items():
        st.markdown(f"- **#{oid}**: {details['item']}")

if api_key:
    # --- 4. THE BRAIN (LLM & Agentic Logic) ---
    # Initialize the NEW Google GenAI client
    client = genai.Client(api_key=api_key)
    
    # Set up our chat history list so it doesn't disappear when the page reloads
    if "messages" not in st.session_state:
        st.session_state.messages = []
        
    # Initialize the native chat session with our Database tool
   # Initialize the native chat session with our Database tool
   # Initialize the native chat session with our Database tools
    if "chat_session" not in st.session_state:
        st.session_state.chat_session = client.chats.create(
            model='gemini-2.5-flash', 
            config=types.GenerateContentConfig(
                tools=[get_order_status, get_account_summary], # <--- UPDATED TOOLS LIST
                temperature=0.2
            )
        )
    # Display previous chat messages on the screen
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # --- 5. THE USER INTERACTION ---
    user_input = st.chat_input("Type your message here...")
    if user_input:
        # Show what the user typed and save it to our history
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)
        
        # Show the "Agent Thinking" animation while the backend runs
        with st.chat_message("assistant"):
            with st.spinner("Agent Thinking..."):
                response = st.session_state.chat_session.send_message(user_input)
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
else:
    st.warning("👈 Please enter your Gemini API key in the sidebar to start chatting.")