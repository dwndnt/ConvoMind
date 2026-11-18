import logging
import os
import re
import time
from typing import Any, Optional, Tuple
import pandas as pd
from pywinauto import Desktop
from pywinauto.keyboard import send_keys
import streamlit as st

# Logging Configuration
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# Constants
MAX_SCROLL_ITERATIONS = 30
SCROLL_PAUSE_TIME = 0.3
STABILITY_THRESHOLD = 2
MESSAGE_BODY_PREFIX = "message-body-"
CONTENT_PREFIX = "content-"

# --- Backend Extraction Logic ---

def get_teams_window() -> Optional[Any]:
    """Find and return the Microsoft Teams window."""
    desktop = Desktop(backend="uia")
    teams_windows = [w for w in desktop.windows() if "Microsoft Teams" in w.window_text()]
    return teams_windows[0] if teams_windows else None


def extract_messages() -> Tuple[Optional[pd.DataFrame], Optional[str]]:
    """Extract messages from the active Teams window with dynamic auto-scrolling to top."""
    window = get_teams_window()
    if not window:
        return None, "Microsoft Teams window not found."

    target_pane = next((c for c in window.children() if c.element_info.name), None)
    if not target_pane:
        return None, "Microsoft Teams main pane not found."

    documents = target_pane.descendants(control_type="Document")
    if not documents:
        return None, "Document element not found inside Teams."

    doc = documents[0]

    # Dynamic auto-scroll up to the very beginning of the chat
    try:
        window.set_focus()
        prev_count = 0
        no_change_count = 0
        
        for _ in range(MAX_SCROLL_ITERATIONS):
            messages = [
                c for c in doc.descendants(control_type="Group") 
                if c.element_info.automation_id and MESSAGE_BODY_PREFIX in c.element_info.automation_id
            ]
            current_count = len(messages)
            
            if current_count == prev_count:
                no_change_count += 1
                if no_change_count >= STABILITY_THRESHOLD:
                    break
            else:
                no_change_count = 0
                
            prev_count = current_count
            send_keys("{PGUP}")
            time.sleep(SCROLL_PAUSE_TIME)
    except Exception as e:
        logger.warning(f"Dynamic auto-scroll skipped: {e}")

    # Retrieve all messages after scrolling
    all_groups = doc.descendants(control_type="Group")
    messages = [
        c for c in all_groups 
        if c.element_info.automation_id and MESSAGE_BODY_PREFIX in c.element_info.automation_id
    ]

    if not messages:
        return None, "No chat messages found in the active window."

    data = []
    seen_ids = set()

    for msg in messages:
        try:
            info = msg.element_info
            aid = info.automation_id or ""
            if aid and aid in seen_ids:
                continue
            if aid:
                seen_ids.add(aid)

            outer_name = info.name or ""
            
            # Find content group inside message
            content_groups = [
                g for g in msg.descendants(control_type="Group") 
                if g.element_info.automation_id and CONTENT_PREFIX in g.element_info.automation_id
            ]

            if content_groups:
                content = content_groups[0].element_info.name or ""
                sender = "Unknown"
                
                # Remove timestamp/date info from the end of outer_name
                base_text = re.sub(r'(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday),?\s+\d{1,2}.*$', '', outer_name).strip()
                if not base_text:
                    base_text = outer_name

                if content and base_text.startswith(content):
                    remainder = base_text[len(content):].strip().rstrip(',')
                    if remainder:
                        sender = remainder
                elif content and content in base_text:
                    idx = base_text.find(content)
                    remainder = base_text[idx + len(content):].strip().rstrip(',')
                    if remainder:
                        sender = remainder
            else:
                content = outer_name
                sender = "System / Notification"

            if content:
                data.append({
                    "sender": sender,
                    "content": content,
                    "id": aid
                })
        except Exception as ex:
            logger.warning(f"Failed to process message: {ex}")
            continue

    if not data:
        return None, "Failed to extract message contents."

    df = pd.DataFrame(data)
    df = df.drop_duplicates(subset=["content"]).reset_index(drop=True)
    return df, None


def convert_to_markdown(df: pd.DataFrame) -> str:
    """Convert DataFrame to Markdown format."""
    md = "# Microsoft Teams Conversation Extraction\n\n"
    for _, row in df.iterrows():
        md += f"### {row['sender']}\n{row['content']}\n\n---\n"
    return md


# --- Streamlit UI ---
st.set_page_config(
    page_title="ConvoMind",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional Styling (Button Polish)
st.markdown(
    """
    <style>
    /* Primary Action Buttons */
    .stButton>button {
        border-radius: 8px;
        background: linear-gradient(135deg, #4f46e5 0%, #4338ca 100%);
        color: white;
        font-weight: 600;
        padding: 0.6rem 1.2rem;
        border: none;
        box-shadow: 0 4px 12px rgba(79, 70, 229, 0.25);
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #4338ca 0%, #3730a3 100%);
        box-shadow: 0 6px 16px rgba(79, 70, 229, 0.4);
        transform: translateY(-1px);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Main Header
st.title("ConvoMind")
st.markdown("Transforming conversations into structured knowledge.")
st.markdown("---")

# Instructions Card
with st.container(border=True):
    st.markdown("### Operation Workflow")
    st.markdown(
        "1. Open Microsoft Teams and navigate to the target chat or channel.\n"
        "2. Ensure the chat window is active and visible.\n"
        "3. Click the **Extract Active Chat** button below to begin."
    )

st.markdown("")

col1, col2 = st.columns([1, 3])
with col1:
    extract_btn = st.button("Extract Active Chat", use_container_width=True)

if extract_btn:
    with st.status("Processing conversation...", expanded=True) as status:
        st.write("Initializing UI automation and scrolling chat history...")
        df, error = extract_messages()
        
        if error:
            st.error(error)
            status.update(label="Extraction Failed", state="error")
        else:
            st.success(f"Successfully extracted {len(df)} messages.")
            status.update(label="Extraction Completed", state="complete")
            
            # Data Table
            st.markdown("### Extracted Messages")
            st.dataframe(df[["sender", "content"]], use_container_width=True, height=400)
            
            # Download Markdown
            md_content = convert_to_markdown(df)
            st.download_button(
                label="Download Markdown Report",
                data=md_content,
                file_name="convomind_report.md",
                mime="text/markdown",
                use_container_width=True
            )

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #94a3b8; font-size: 0.85rem; padding: 1rem 0;'>"
    "ConvoMind &bull; Developed by Dewan Dinata Tarigan"
    "</div>",
    unsafe_allow_html=True,
)
