"""
Home Page - Landing page with information about the tool
"""

import streamlit as st
from config import FOOTER_HTML, load_image_base64


def render():
    """Render the home page"""

    # About This Tool section
    st.markdown("""
        ## About This Tool

        The Skin Lesion Triage Tool is an AI-powered prototype designed to assist healthcare professionals
        in the preliminary assessment of skin lesions. It combines advanced machine learning models to provide
        a comprehensive risk analysis.
    """)

    # Medical disclaimer
    st.markdown("""
        <div style="
            background-color: #fef2f2;
            border: 2px solid #ef4444;
            border-radius: 10px;
            padding: 1.2rem;
            margin: 1.5rem 0;
        ">
            <p style="color: #991b1b; margin: 0; font-size: 0.95rem; line-height: 1.6;">
                <strong><span class="material-symbols-rounded" style="color: #991b1b; font-size: 1.2rem; vertical-align: middle;">release_alert</span> MEDICAL DISCLAIMER:</strong> This tool is a research prototype for educational purposes only.
                It does not provide medical diagnosis and should not replace professional medical evaluation.
                Always consult a qualified dermatologist for any skin lesion concerns.
            </p>
        </div>
    """, unsafe_allow_html=True)

    # How it works - Load lupa.png icon
    lupa_base64 = load_image_base64('lupa.png')
    if lupa_base64:
        lupa_html = f'<img src="{lupa_base64}" alt="Search" style="height: 1.5rem; width: auto; vertical-align: middle; margin-right: 0.5rem;">'
    else:
        lupa_html = ""

    st.markdown(f"## {lupa_html}How It Works", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
            <div style="
                background: linear-gradient(135deg, #e0f2f7 0%, #b3e5f0 100%);
                border-left: 4px solid #2d8a9b;
                border-radius: 8px;
                padding: 1.5rem;
                height: 100%;
            ">
                <h3 style="color: #1e40af; margin-top: 0;">
                    <span class="material-symbols-rounded" style="font-size: 1.8rem; vertical-align: middle; margin-right: 0.5rem;">user_attributes</span>
                    Patient & Lesion
                </h3>
                <p style="color: #374151;">
                    Register patient information and lesion details. Track lesions over time
                    with comprehensive medical records.
                </p>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
            <div style="
                background: linear-gradient(135deg, #e0f2f7 0%, #b3e5f0 100%);
                border-left: 4px solid #2d8a9b;
                border-radius: 8px;
                padding: 1.5rem;
                height: 100%;
            ">
                <h3 style="color: #15803d; margin-top: 0;">
                    <span class="material-symbols-rounded" style="font-size: 1.8rem; vertical-align: middle; margin-right: 0.5rem;">image_arrow_up</span>
                    Image Analysis
                </h3>
                <p style="color: #374151;">
                    Upload dermoscopic images for analysis. Two AI models work together
                    to assess malignancy risk from different perspectives.
                </p>
            </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
            <div style="
                background: linear-gradient(135deg, #e0f2f7 0%, #b3e5f0 100%);
                border-left: 4px solid #2d8a9b;
                border-radius: 8px;
                padding: 1.5rem;
                height: 100%;
            ">
                <h3 style="color: #92400e; margin-top: 0;">
                    <span class="material-symbols-rounded" style="font-size: 1.8rem; vertical-align: middle; margin-right: 0.5rem;">analytics</span>
                    Results & Insights
                </h3>
                <p style="color: #374151;">
                    Receive detailed risk assessments with SHAP explainability to understand
                    which features influenced the prediction.
                </p>
            </div>
        """, unsafe_allow_html=True)

    # Feature highlights - Load key_features.png icon
    key_features_base64 = load_image_base64('key_features.png')
    if key_features_base64:
        key_features_html = f'<img src="{key_features_base64}" alt="Key Features" style="height: 1.5rem; width: auto; vertical-align: middle; margin-right: 0.5rem;">'
    else:
        key_features_html = ""

    st.markdown(f"## {key_features_html}Key Features", unsafe_allow_html=True)

    features = [
        ("splitscreen_left", "Dual Model Analysis", "Two complementary AI models provide comprehensive risk assessment"),
        # ("clinical_notes", "Patient Management", "Complete patient and lesion tracking system"),
        ("calendar_month", "Temporal Tracking", "Monitor lesion changes over time"),
        ("area_chart", "Key Influencing Factors", "Understand why the AI made its predictions"),
        ("database", "Database Storage", "Secure storage of all analyses and patient data"),
        ("sentiment_satisfied", "User-Friendly Interface", "Intuitive design for healthcare professionals")
    ]

    col1, col2 = st.columns(2)

    for i, (icon_name, title, description) in enumerate(features):
        with col1 if i % 2 == 0 else col2:
            st.markdown(f"""
                <div style="
                    background-color: #f9fafb;
                    border-radius: 8px;
                    padding: 1rem;
                    margin: 0.5rem 0;
                ">
                    <p style="margin: 0; color: #1e6b7a; font-weight: 600;">
                        <span class="material-symbols-rounded" style="font-size: 1.3rem; vertical-align: middle; margin-right: 0.5rem;">{icon_name}</span>
                        {title}
                    </p>
                    <p style="margin: 0.5rem 0 0 0; color: #6b7280; font-size: 0.9rem;">{description}</p>
                </div>
            """, unsafe_allow_html=True)

    # Call to action
    st.markdown("---")

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown("""
            <div style="text-align: center; padding: 2rem 0;">
                <h3 style="color: #1e6b7a;">Ready to Start?</h3>
                <p style="color: #6b7280;">Navigate to the Assessment page to begin.</p>
            </div>
        """, unsafe_allow_html=True)

    # Footer
    st.markdown("---")
    st.markdown(FOOTER_HTML, unsafe_allow_html=True)
