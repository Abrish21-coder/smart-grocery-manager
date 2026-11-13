import streamlit as st
from agent import run_agent, pending_actions, apply_action, inventory

st.set_page_config(page_title="Smart Grocery Manager", page_icon="🛒", layout="wide")

if "messages" not in st.session_state:
    st.session_state.messages = []

st.title("🛒 Smart Grocery Manager")
st.caption("AI-powered inventory agent with human-in-the-loop approval")

expiring_soon = len([p for p in inventory if p["expiry_days"] <= 3])
low_stock = len([p for p in inventory if p["stock"] < 10])

m1, m2, m3, m4 = st.columns(4)
m1.metric("Total Products", len(inventory))
m2.metric("Expiring Soon", expiring_soon)
m3.metric("Low Stock", low_stock)
m4.metric("Pending Approvals", len(pending_actions))

st.divider()
left, right = st.columns([2, 1])

with left:
    st.subheader("💬 Ask the Agent")
    chat_box = st.container(height=350)
    with chat_box:
        for role, text in st.session_state.messages:
            with st.chat_message(role):
                st.write(text)

    user_query = st.chat_input("Ask something (e.g. 'what's expiring soon?')")
    if user_query:
        st.session_state.messages.append(("user", user_query))
        response = run_agent(user_query)
        st.session_state.messages.append(("assistant", response))
        st.rerun()

with right:
    st.subheader("⏳ Pending Approvals")
    if pending_actions:
        for i, action in enumerate(pending_actions):
            with st.container(border=True):
                st.write(f"**{action['product']}** — {action['discount']}% off")
                c1, c2 = st.columns(2)
                if c1.button("✅ Approve", key=f"approve_{i}", use_container_width=True):
                    st.success(apply_action(i))
                    st.rerun()
                if c2.button("❌ Reject", key=f"reject_{i}", use_container_width=True):
                    pending_actions.pop(i)
                    st.rerun()
    else:
        st.info("No pending suggestions right now.")

st.divider()
st.subheader("📦 Current Inventory")
st.dataframe(inventory, use_container_width=True, hide_index=True)