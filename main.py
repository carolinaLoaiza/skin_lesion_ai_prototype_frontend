"""
Skin Lesion Triage Tool - Main Application
Main entry point with sidebar navigation
"""

import streamlit as st
from config import PAGE_CONFIG, APP_TITLE, load_image_base64
from app_pages import home, analysis, history, about


# Configure page
st.set_page_config(**PAGE_CONFIG)

# Apply custom color scheme (medical/clinical theme)
st.markdown("""
    <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200" />

    <style>
        /* Sidebar styling - Medical blue-green theme */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0d4d5e 0%, #115e70 100%);
        }

        [data-testid="stSidebar"] * {
            color: white !important;
        }

        [data-testid="stSidebar"] .stMarkdown {
            color: white !important;
        }

        /* Page background - Light clinical theme */
        .main {
            background-color: #f0f7f9;
        }

        .block-container {
            background-color: #f0f7f9;
        }

        /* Button styling in sidebar */
        [data-testid="stSidebar"] button {
            background-color: rgba(255, 255, 255, 0.15) !important;
            border: 1px solid rgba(255, 255, 255, 0.3) !important;
            color: white !important;
        }

        [data-testid="stSidebar"] button:hover {
            background-color: rgba(255, 255, 255, 0.25) !important;
            border-color: rgba(255, 255, 255, 0.5) !important;
        }

        [data-testid="stSidebar"] button[kind="primary"] {
            background-color: rgba(255, 255, 255, 0.35) !important;
            font-weight: 600 !important;
            border: 2px solid rgba(255, 255, 255, 0.6) !important;
        }

        [data-testid="stSidebar"] button p {
            color: white !important;
        }

        /* Headings on main page - Medical theme colors */
        .main h1 {
            color: #0d4d5e !important;
        }

        .main h2 {
            color: #115e70 !important;
        }

        .main h3 {
            color: #15758a !important;
        }
    </style>
""", unsafe_allow_html=True)

# Initialize current page in session state
if 'current_page' not in st.session_state:
    st.session_state.current_page = "Home"

# Sidebar navigation
st.sidebar.title("Dashboard")
st.sidebar.markdown("---")

# Navigation buttons with updated names (no emojis)
pages = {
    "Home": "Overview",
    "Analysis": "Assessment",
    "History": "History",
    "About": "About"
}

for page_key, page_label in pages.items():
    # Check if this is the current page
    is_current = st.session_state.current_page == page_key

    # Create button with conditional styling
    button_type = "primary" if is_current else "secondary"

    if st.sidebar.button(
        page_label,
        key=f"nav_{page_key}",
        use_container_width=True,
        type=button_type,
        disabled=is_current
    ):
        st.session_state.current_page = page_key
        st.rerun()

st.sidebar.markdown("---")

# Header section with medical theme banner
# Load logo using centralized helper
logo_base64 = load_image_base64('logo.png')
if logo_base64:
    logo_html = f'<img src="{logo_base64}" alt="Logo" style="height: 3rem; width: auto; filter: drop-shadow(2px 2px 4px rgba(0, 0, 0, 0.2)); vertical-align: middle; margin-right: 1rem;">'
else:
    logo_html = "🩺"

# Get current page subtitle
current_page_subtitle = pages.get(st.session_state.current_page, "AI-Assisted Skin Lesion Risk Assessment")

st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #1e6b7a 0%, #2d8a9b 50%, #3aa3b8 100%);
        padding: 2rem 1rem;
        border-radius: 0 0 20px 20px;
        margin: -5rem -5rem 2rem -5rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.15);
    ">
        <div style="text-align: center; color: white;">
            <h1 style="
                margin: 0;
                font-size: 2.5rem;
                font-weight: 700;
                color: white !important;
                text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
            ">
                {logo_html} Skin Lesion AI Triage Tool
            </h1>
            <p style="
                margin: 0.5rem 0 0 0;
                font-size: 2.0rem;
                color: rgba(255, 255, 255, 0.95);
                font-weight: 300;
            ">
                {current_page_subtitle}
            </p>
        </div>
    </div>
""", unsafe_allow_html=True)

# Route to selected page
page = st.session_state.current_page

if page == "Home":
    home.render()
elif page == "Analysis":
    analysis.render()
elif page == "History":
    history.render()
elif page == "About":
    about.render()
