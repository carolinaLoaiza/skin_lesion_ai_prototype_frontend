"""
About Page - Information about the project
"""

import streamlit as st
from config import APP_TITLE, FOOTER_HTML
import base64
from pathlib import Path


def load_image_base64(image_filename):
    """Load image from assets/images folder and convert to base64"""
    image_path = Path(__file__).parent.parent / "assets" / "images" / image_filename
    if not image_path.exists():
        return ""

    with open(image_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()
        ext = image_path.suffix[1:]
        return f"data:image/{ext};base64,{encoded}"


def render():
    """Render the about page"""

    # Load architecture icon
    architecture_icon_base64 = load_image_base64('architecture.png')
    architecture_icon_html = f'<img src="{architecture_icon_base64}" style="width: 28px; height: 28px; vertical-align: middle; margin-right: 8px;">' if architecture_icon_base64 else ""

    # Project Overview
    st.markdown(f"""
        ## {architecture_icon_html}Project Overview
    """, unsafe_allow_html=True)

    st.markdown("""
        The Skin Lesion Triage Tool is a research prototype developed as part of the
        MSc Artificial Intelligence Technology dissertation project at Northumbria University London.
        This application demonstrates the application of advanced machine learning techniques
        to assist in the preliminary assessment of dermatological images. This is a research prototype
        for educational and demonstration purposes only. It is NOT intended for clinical use and should
        NOT be used for medical diagnosis. Always consult qualified healthcare professionals for medical advice.
    """)

    st.markdown("---")

    # Load AI model icon
    ai_model_icon_base64 = load_image_base64('ai_model.png')
    ai_model_icon_html = f'<img src="{ai_model_icon_base64}" style="width: 28px; height: 28px; vertical-align: middle; margin-right: 8px;">' if ai_model_icon_base64 else ""

    # Model Architecture
    st.markdown(f"""
        ## {ai_model_icon_html}Model Architecture
    """, unsafe_allow_html=True)

    # Three model boxes at the same level
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
            <div style="
                background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
                border-radius: 12px;
                padding: 1.5rem;
                height: 100%;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            ">
                <h5 style="color: #1e40af; margin: 0.5rem 0; text-align: center;">Image Classifier Model</h5>
                <hr style="border: none; border-top: 1px solid #93c5fd; margin: 1rem 0;">
                <p style="color: #1e3a8a; font-size: 0.85rem; margin: 0.5rem 0; text-align: center; line-height: 1.4;">
                    Convolutional Neural Network - DenseNet-121
                </p>
                <hr style="border: none; border-top: 1px solid #93c5fd; margin: 1rem 0;">
                <p style="color: #1e3a8a; font-size: 0.9rem; line-height: 1.6; margin: 0.5rem 0;">
                    Analyzes the uploaded image directly to estimate lesion risk based on visual patterns.
                    This model processes the raw image directly through multiple convolutional layers to
                    identify patterns associated with malignant and benign lesions.
                </p>
                <hr style="border: none; border-top: 1px solid #93c5fd; margin: 1rem 0;">
                <p style="color: #1e3a8a; font-size: 0.85rem; margin: 0.3rem 0;">
                    <strong>Input:</strong> Raw dermoscopic image pixels
                </p>
                <p style="color: #1e3a8a; font-size: 0.85rem; margin: 0.3rem 0;">
                    <strong>Output:</strong> Malignancy probability (0-100%)
                </p>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
            <div style="
                background: linear-gradient(135deg, #e9d5ff 0%, #d8b4fe 100%);
                border-radius: 12px;
                padding: 1.5rem;
                height: 100%;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            ">
                <h5 style="color: #7c3aed; margin: 0.5rem 0; text-align: center;">Feature Extractor Model</h5>
                <hr style="border: none; border-top: 1px solid #c084fc; margin: 1rem 0;">
                <p style="color: #6b21a8; font-size: 0.85rem; margin: 0.5rem 0; text-align: center; line-height: 1.4;">
                    Feature Extraction - ResNet-50
                </p>
                <hr style="border: none; border-top: 1px solid #c084fc; margin: 1rem 0;">
                <p style="color: #6b21a8; font-size: 0.9rem; line-height: 1.6; margin: 0.5rem 0;">
                    Extracts quantitative characteristics from the image to support subsequent analysis.
                    This model processes the image to extract 18 specific visual features that describe
                    the lesion's color, texture, shape, and borders.
                </p>
                <hr style="border: none; border-top: 1px solid #c084fc; margin: 1rem 0;">
                <p style="color: #6b21a8; font-size: 0.85rem; margin: 0.3rem 0;">
                    <strong>Input:</strong> Dermoscopic image and lesion diameter (mm)
                </p>
                <p style="color: #6b21a8; font-size: 0.85rem; margin: 0.3rem 0;">
                    <strong>Output:</strong> 18 extracted features (Color distribution, Texture, Border, Shape)
                </p>
            </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
            <div style="
                background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
                border-radius: 12px;
                padding: 1.5rem;
                height: 100%;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            ">
                <h5 style="color: #15803d; margin: 0.5rem 0; text-align: center;">Feature-Based Risk Model</h5>
                <hr style="border: none; border-top: 1px solid #6ee7b7; margin: 1rem 0;">
                <p style="color: #166534; font-size: 0.85rem; margin: 0.5rem 0; text-align: center; line-height: 1.4;">
                    Machine Learning - XGBoost
                </p>
                <hr style="border: none; border-top: 1px solid #6ee7b7; margin: 1rem 0;">
                <p style="color: #166534; font-size: 0.9rem; line-height: 1.6; margin: 0.5rem 0;">
                    Estimates lesion risk using extracted image features combined with patient data.
                    This model uses quantified characteristics from the image (color, texture, asymmetry)
                    along with clinical information to make predictions.
                </p>
                <hr style="border: none; border-top: 1px solid #6ee7b7; margin: 1rem 0;">
                <p style="color: #166534; font-size: 0.85rem; margin: 0.3rem 0;">
                    <strong>Input:</strong> 18 extracted features (from Feature Extractor Model) + Patient metadata (age, sex, anatomical location, lesion diameter)
                </p>
                <p style="color: #166534; font-size: 0.85rem; margin: 0.3rem 0;">
                    <strong>Output:</strong> Malignancy probability (0-100%) + SHAP explainability
                </p>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Why Two Outputs
    st.markdown("""
        ### Why Two Outputs?
        The Image Classifier focuses on visual patterns learned directly from the image, while the Feature-Based Risk Model integrates structured image features and patient-related data to provide interpretable insights.
        Comparing both outputs supports a more comprehensive assessment by combining pattern recognition, contextual information, and explainability.        
    """)

    # Mini cards with benefits
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
            <div style="
                background: linear-gradient(135deg, #e0f2f7 0%, #b3e5f0 100%);
                border-left: 4px solid #2d8a9b;
                border-radius: 8px;
                padding: 1rem;
                margin: 0.5rem 0;
            ">
                <p style="color: #0a3940; margin: 0; font-size: 0.9rem;">
                    Agreement between models strengthens result reliability
                </p>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("""
            <div style="
                background: linear-gradient(135deg, #e0f2f7 0%, #b3e5f0 100%);
                border-left: 4px solid #2d8a9b;
                border-radius: 8px;
                padding: 1rem;
                margin: 0.5rem 0;
            ">
                <p style="color: #0a3940; margin: 0; font-size: 0.9rem;">
                    Each model captures different types of risk signals                    
                </p>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
            <div style="
                background: linear-gradient(135deg, #e0f2f7 0%, #b3e5f0 100%);
                border-left: 4px solid #2d8a9b;
                border-radius: 8px;
                padding: 1rem;
                margin: 0.5rem 0;
            ">
                <p style="color: #0a3940; margin: 0; font-size: 0.9rem;">
                    Combines extracted features with lesion and patient data
                </p>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("""
            <div style="
                background: linear-gradient(135deg, #e0f2f7 0%, #b3e5f0 100%);
                border-left: 4px solid #2d8a9b;
                border-radius: 8px;
                padding: 1rem;
                margin: 0.5rem 0;
            ">
                <p style="color: #0a3940; margin: 0; font-size: 0.9rem;">
                    Shows which features contributed most to the risk estimation in one of the models.
                </p>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("""
        <div style="
            background-color: #fef3c7;
            border-left: 4px solid #f59e0b;
            border-radius: 8px;
            padding: 1rem;
            margin: 1rem 0;
        ">
            <p style="color: #92400e; margin: 0; font-size: 0.9rem;">
                <strong><span class="material-symbols-rounded" style="vertical-align: middle; font-size: 1.2rem; margin-right: 0.3rem;">warning</span>Clinical Recommendation:</strong> Use both model outputs together for a more comprehensive risk assessment.
                Significant disagreement between models may warrant additional clinical evaluation.
            </p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Load tech stack icon
    tech_stack_icon_base64 = load_image_base64('tech_stack.png')
    tech_stack_icon_html = f'<img src="{tech_stack_icon_base64}" style="width: 28px; height: 28px; vertical-align: middle; margin-right: 8px;">' if tech_stack_icon_base64 else ""

    # Technical Stack
    st.markdown(f"""
        ## {tech_stack_icon_html}Technical Stack
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
            <div style="
                background: linear-gradient(135deg, #e0f2f7 0%, #b3e5f0 100%);
                border-radius: 12px;
                padding: 1.5rem;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            ">
                <h4 style="color: #0a3940; margin-top: 0; text-align: center;">Frontend</h4>
                <p style="color: #0a3940; margin: 0.5rem 0; font-size: 0.9rem;">Streamlit: Web application framework</p>
                <p style="color: #0a3940; margin: 0.5rem 0; font-size: 0.9rem;">Plotly: Interactive data visualization</p>
                <p style="color: #0a3940; margin: 0.5rem 0; font-size: 0.9rem;">Python: Programming language</p>
                <p style="color: #0a3940; margin: 0.5rem 0; font-size: 0.9rem;">Pandas: Data manipulation</p>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
            <div style="
                background: linear-gradient(135deg, #e0f2f7 0%, #b3e5f0 100%);
                border-radius: 12px;
                padding: 1.5rem;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            ">
                <h4 style="color: #0a3940; margin-top: 0; text-align: center;">Backend (API)</h4>
                <p style="color: #0a3940; margin: 0.5rem 0; font-size: 0.9rem;">FastAPI: REST API framework</p>
                <p style="color: #0a3940; margin: 0.5rem 0; font-size: 0.9rem;">MongoDB: Database storage</p>
                <p style="color: #0a3940; margin: 0.5rem 0; font-size: 0.9rem;">PyTorch: Deep learning models</p>
                <p style="color: #0a3940; margin: 0.5rem 0; font-size: 0.9rem;">XGBoost: Machine learning framework</p>
                <p style="color: #0a3940; margin: 0.5rem 0; font-size: 0.9rem;">SHAP: Model explainability</p>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Load project icon
    project_icon_base64 = load_image_base64('project.png')
    project_icon_html = f'<img src="{project_icon_base64}" style="width: 28px; height: 28px; vertical-align: middle; margin-right: 8px;">' if project_icon_base64 else ""

    # Load university icon
    university_icon_base64 = load_image_base64('university.png')
    university_icon_html = f'<img src="{university_icon_base64}" style="width: 28px; height: 28px; vertical-align: middle; margin-right: 8px;">' if university_icon_base64 else ""

    # Contact/Feedback
    st.markdown(f"""
        ## {university_icon_html}Contact & Feedback
    """, unsafe_allow_html=True)

    st.markdown("""
        For questions, feedback, or research inquiries, please contact through
        the appropriate academic channels at Northumbria University London.
    """)

    # Footer
    st.markdown("---")
    st.markdown(FOOTER_HTML, unsafe_allow_html=True)
