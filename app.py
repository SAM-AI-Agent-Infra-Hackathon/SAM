#!/usr/bin/env python3
"""
Immigration Chatbot UI (Streamlit)
=================================

A lightweight chatbot UI that wraps the EnhancedImmigrationAgent.
- Chat with the agent about OPT, H-1B, and PERM/Green Card.
- Run company immigration profiles with /profile CompanyName.
- Uses your existing Supabase-backed data services and tools.

Run:
  streamlit run app.py
"""

import os
import sys
import time
import streamlit as st
from dotenv import load_dotenv

# Ensure src is importable
BASE_DIR = os.path.dirname(__file__)
sys.path.append(os.path.join(BASE_DIR, 'src'))

# Lazy imports from our project
from immigration_main_agent import EnhancedImmigrationAgent

# -----------------------------------------------------------------------------
# App Setup
# -----------------------------------------------------------------------------
st.set_page_config(page_title="Immigration Assistant", page_icon="🛂", layout="centered")

# Load env
load_dotenv()

# Sidebar: Environment and Controls
with st.sidebar:
    st.header("Settings")
    st.caption("Environment variables from your .env are loaded on startup.")

    st.markdown("**Supabase URL:**")
    st.code(os.getenv("SUPABASE_URL", "<missing>"), language="bash")

    st.markdown("**Supabase Key (masked):**")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "<missing>")
    st.code((key[:6] + "...masked...") if key and key != "<missing>" else "<missing>")

    st.divider()

    st.subheader("Quick Prompts")
    examples = [
        "I'm on OPT. Who sponsors H-1B in San Francisco?",
        "What companies sponsor green cards for software engineers?",
        "/profile Google",
        "High-paying PERM jobs in New York",
        "Help me plan F-1 → OPT → H-1B → Green Card",
    ]
    for ex in examples:
        if st.button(ex, use_container_width=True):
            st.session_state.get("queued_prompt", None)
            st.session_state["queued_prompt"] = ex

    st.divider()
    st.caption("Tip: Use /profile CompanyName for a detailed immigration profile.")

# Initialize agent (once)
@st.cache_resource(show_spinner=True)
def _get_agent():
    return EnhancedImmigrationAgent()

# Session state for chat
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hi! I'm your Immigration Assistant. Ask me about OPT, H-1B, or Green Card (PERM)."}
    ]

agent = _get_agent()

st.title("🛂 Immigration Assistant for International Students")
st.caption("Powered by your LCA + PERM data and immigration-aware reasoning.")

# Render history (preserve formatting for assistant messages)
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        if m["role"] == "assistant":
            # Use code block to strictly preserve spacing/line breaks
            st.code(m["content"], language="text")
        else:
            st.markdown(m["content"])

# Input box
default_value = st.session_state.pop("queued_prompt", "") if "queued_prompt" in st.session_state else ""
prompt = st.chat_input("Ask about companies, locations, salaries, or immigration process...", key="chat_input",)
if default_value and not prompt:
    # If user clicked a quick prompt button
    prompt = default_value

if prompt:
    # Show user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Agent thinking spinner
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                if prompt.strip().lower().startswith("/profile "):
                    company = prompt.strip()[9:].strip()
                    if not company:
                        response = "Please provide a company name, e.g., /profile Google"
                    else:
                        response = agent.get_company_profile(company)
                else:
                    response = agent.process_query(prompt)
            except Exception as e:
                response = f"❌ Error: {e}\n\nPlease check your environment (.env) and try again."

            # Render once in fixed-width block to preserve layout
            final = response.strip()
            st.code(final, language="text")

    # Persist assistant message
    st.session_state.messages.append({"role": "assistant", "content": final})
