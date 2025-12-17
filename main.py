import streamlit as st
from PIL import Image
import base64
from pathlib import Path
from io import BytesIO
import json
import plotly.graph_objects as go
import plotly.express as px
from prediction_service import create_service, PredictionResponse


def load_icon(icon_path):
    """Load and encode icon as base64 for inline HTML display"""
    try:
        with open(icon_path, "rb") as f:
            data = base64.b64encode(f.read()).decode()
        return f"data:image/png;base64,{data}"
    except FileNotFoundError:
        return None


def get_icon_html(icon_name, size=20):
    """Generate HTML for custom icon with fallback to emoji"""
    icons_dir = Path(__file__).parent / "assets" / "icons"
    icon_path = icons_dir / f"{icon_name}.png"

    # Fallback emojis if icon file doesn't exist
    emoji_fallbacks = {
        "location": "📍",
        "camera": "📸",
        "patient": "👤",
        "analyse": "🔬",
        "medical": "🩺",
        "chart": "📊",
        "upload": "📤"
    }

    icon_data = load_icon(icon_path)
    if icon_data:
        return f'<img src="{icon_data}" width="{size}" height="{size}" style="vertical-align: middle; margin-right: 8px;">'
    else:
        # Fallback to emoji
        return emoji_fallbacks.get(icon_name, "•")


def apply_custom_styles():
    """Apply custom CSS styles for a modern medical app look"""
    st.markdown("""
        <style>
        /* Import modern font */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

        /* Global styling */
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }

        /* Main title styling */
        h1 {
            color: #1e3a8a;
            font-weight: 700;
            padding-bottom: 0.5rem;
            border-bottom: 3px solid #3b82f6;
        }

        /* Headers */
        h2, h3 {
            color: #1e40af;
            font-weight: 600;
        }

        /* Info box */
        .info-box {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 1.5rem;
            border-radius: 12px;
            color: white;
            margin-bottom: 2rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }

        .info-box h3 {
            color: white;
            margin-top: 0;
            font-size: 1.3rem;
        }

        .info-box p {
            color: #f0f0f0;
            line-height: 1.6;
        }

        /* Instructions styling */
        .instruction-item {
            background-color: #f0f9ff;
            border-left: 4px solid #3b82f6;
            padding: 1rem;
            margin: 0.5rem 0;
            border-radius: 4px;
        }

        /* Analyze button */
        .stButton > button {
            background: linear-gradient(90deg, #3b82f6 0%, #2563eb 100%);
            color: white;
            font-weight: 600;
            border: none;
            padding: 0.75rem 2rem;
            border-radius: 8px;
            font-size: 1.1rem;
            width: 100%;
            transition: all 0.3s ease;
        }

        .stButton > button:hover {
            background: linear-gradient(90deg, #2563eb 0%, #1d4ed8 100%);
            box-shadow: 0 4px 12px rgba(37, 99, 235, 0.4);
            transform: translateY(-2px);
        }

        /* Input fields styling */
        .stNumberInput > div > div > input,
        .stSelectbox > div > div > select {
            border-radius: 6px;
            border: 2px solid #e5e7eb;
            font-size: 1rem;
        }

        /* File uploader */
        .stFileUploader {
            background-color: #fafafa;
            border: 2px dashed #cbd5e1;
            border-radius: 8px;
            padding: 1rem;
        }

        /* Card-like sections */
        .section-card {
            background-color: #ffffff;
            border-radius: 10px;
            padding: 1.5rem;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
            margin-bottom: 1.5rem;
        }
        </style>
    """, unsafe_allow_html=True)


def show_instructions():
    """Display usage instructions in an attractive format"""
    st.markdown("""
        <div class="info-box">
            <h3>Skin Lesion Triage Tool</h3>
            <p>
                This tool provides a preliminary assessment of skin lesion images to support dermatological evaluation. It is intended for research and educational purposes only. Upload a clear image and enter patient information to obtain an analysis. This tool does not replace professional medical advice.
            </p>
        </div>
    """, unsafe_allow_html=True)

    with st.expander("📋 How to use this application?", expanded=False):
        st.markdown("""
            <div class="instruction-item">
                <b>1. Upload image:</b> Select a clear photo of the skin lesion (formats: PNG, JPG, JPEG).
            </div>
            <div class="instruction-item">
                <b>2. Patient information:</b> Complete the fields for age, sex, location, and diameter of the lesion.
            </div>
            <div class="instruction-item">
                <b>3. Analysis:</b> Click the "Analyze Lesion" button to process the information.
            </div>
            <div class="instruction-item">
                <b>⚠️ Important note:</b> This is a diagnostic support tool. Always consult with a medical professional.
            </div>
        """, unsafe_allow_html=True)


def get_risk_color(risk_category: str) -> tuple:
    """
    Get color scheme for risk category

    Returns:
        tuple: (primary_color, background_color, icon)
    """
    risk_colors = {
        "low": ("#22c55e", "#f0fdf4", "✅"),
        "medium": ("#f59e0b", "#fffbeb", "⚠️"),
        "high": ("#ef4444", "#fef2f2", "🚨")
    }
    return risk_colors.get(risk_category.lower(), ("#6b7280", "#f3f4f6", "ℹ️"))


def display_risk_assessment(response: PredictionResponse):
    """
    Display risk assessment with color coding and visual elements

    Args:
        response: PredictionResponse object from API
    """
    color, bg_color, icon = get_risk_color(response.risk_category)

    # Main risk display card
    st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, {bg_color} 0%, {color}15 100%);
            border-left: 6px solid {color};
            border-radius: 12px;
            padding: 2rem;
            margin: 1.5rem 0;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        ">
            <h2 style="color: {color}; margin: 0; font-size: 2rem;">
                {icon} {response.risk_category.upper()} RISK
            </h2>
            <p style="font-size: 1.3rem; color: #374151; margin: 1rem 0 0 0;">
                Malignancy Probability: <strong style="color: {color};">{response.final_probability:.1%}</strong>
            </p>
        </div>
    """, unsafe_allow_html=True)

    # Probability gauge chart
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=response.final_probability * 100,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Malignancy Risk (%)", 'font': {'size': 24, 'color': '#1f2937'}},
        number={'suffix': "%", 'font': {'size': 40}},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 2, 'tickcolor': color},
            'bar': {'color': color, 'thickness': 0.75},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "#e5e7eb",
            'steps': [
                {'range': [0, 30], 'color': '#f0fdf4'},
                {'range': [30, 70], 'color': '#fffbeb'},
                {'range': [70, 100], 'color': '#fef2f2'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 70
            }
        }
    ))

    fig.update_layout(
        height=300,
        margin=dict(l=20, r=20, t=60, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        font={'family': "Inter, sans-serif"}
    )

    st.plotly_chart(fig, use_container_width=True)


def display_model_breakdown(response: PredictionResponse):
    """
    Display individual model contributions with charts

    Args:
        response: PredictionResponse object from API
    """
    st.markdown("### 🤖 AI Model Ensemble Breakdown")

    # Create two columns for model comparison
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
            <div style="
                background-color: #f0f9ff;
                border-radius: 8px;
                padding: 1.5rem;
                border: 2px solid #3b82f6;
            ">
                <h4 style="color: #1e40af; margin: 0;">Model A - Deep Learning</h4>
                <p style="color: #6b7280; font-size: 0.9rem; margin: 0.5rem 0;">DenseNet-121 CNN</p>
            </div>
        """, unsafe_allow_html=True)

        # Model A probability display
        st.metric(
            label="Prediction Probability",
            value=f"{response.model_a_probability:.1%}",
            delta=f"{(response.model_a_probability - response.final_probability):.1%} vs final"
        )
        st.progress(response.model_a_probability)

    with col2:
        st.markdown("""
            <div style="
                background-color: #f0fdf4;
                border-radius: 8px;
                padding: 1.5rem;
                border: 2px solid #22c55e;
            ">
                <h4 style="color: #15803d; margin: 0;">Model C - Tabular ML</h4>
                <p style="color: #6b7280; font-size: 0.9rem; margin: 0.5rem 0;">Random Forest Classifier</p>
            </div>
        """, unsafe_allow_html=True)

        # Model C probability display
        st.metric(
            label="Prediction Probability",
            value=f"{response.model_c_probability:.1%}",
            delta=f"{(response.model_c_probability - response.final_probability):.1%} vs final"
        )
        st.progress(response.model_c_probability)

    # Comparison bar chart
    st.markdown("#### Model Comparison")

    fig = go.Figure(data=[
        go.Bar(
            name='Model Predictions',
            x=['Model A\n(DenseNet-121)', 'Final Ensemble', 'Model C\n(Random Forest)'],
            y=[response.model_a_probability * 100,
               response.final_probability * 100,
               response.model_c_probability * 100],
            marker_color=['#3b82f6', '#8b5cf6', '#22c55e'],
            text=[f"{response.model_a_probability:.1%}",
                  f"{response.final_probability:.1%}",
                  f"{response.model_c_probability:.1%}"],
            textposition='auto',
        )
    ])

    fig.update_layout(
        yaxis_title="Malignancy Probability (%)",
        yaxis_range=[0, 100],
        height=350,
        margin=dict(l=20, r=20, t=20, b=20),
        showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={'family': "Inter, sans-serif", 'size': 12}
    )

    fig.update_yaxes(gridcolor='#e5e7eb', gridwidth=1)

    st.plotly_chart(fig, use_container_width=True)


def display_extracted_features(response: PredictionResponse):
    """
    Display extracted features in an expandable section

    Args:
        response: PredictionResponse object from API
    """
    with st.expander("🔬 Extracted Features (Model B - ResNet-50)", expanded=False):
        st.markdown("""
            <p style="color: #6b7280; margin-bottom: 1rem;">
                These are the 18 visual features extracted from the lesion image by the ResNet-50 model,
                which are then used by Model C (Random Forest) for classification.
            </p>
        """, unsafe_allow_html=True)

        # Display features in a grid
        num_features = len(response.extracted_features)
        cols_per_row = 6

        for i in range(0, num_features, cols_per_row):
            cols = st.columns(cols_per_row)
            for j, col in enumerate(cols):
                idx = i + j
                if idx < num_features:
                    with col:
                        st.metric(
                            label=f"F{idx + 1}",
                            value=f"{response.extracted_features[idx]:.2f}"
                        )


def display_prediction_results(response: PredictionResponse, input_metadata: dict):
    """
    Main function to display all prediction results

    Args:
        response: PredictionResponse object from API
        input_metadata: Dictionary with input data (age, sex, location, diameter)
    """
    st.markdown("---")
    st.markdown("## 📊 Analysis Results")

    # Risk assessment (main display)
    display_risk_assessment(response)

    # Model breakdown
    display_model_breakdown(response)

    # Extracted features (expandable)
    display_extracted_features(response)

    # Input metadata summary
    with st.expander("📋 Input Data Summary", expanded=False):
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Patient Age", f"{input_metadata['age']} years")
        with col2:
            st.metric("Sex", input_metadata['sex'].title())
        with col3:
            st.metric("Location", input_metadata['location'].title())
        with col4:
            st.metric("Diameter", f"{input_metadata['diameter']} mm")

    # Action buttons
    st.markdown("---")
    col1, col2, col3 = st.columns([2, 1, 2])

    with col2:
        if st.button("🔄 New Analysis", use_container_width=True, type="secondary"):
            st.rerun()


def main():
    # Configure page
    st.set_page_config(
        page_title="Skin Lesion Analyzer",
        page_icon="🩺",
        layout="wide",
        initial_sidebar_state="collapsed"
    )

    # Apply custom styles
    apply_custom_styles()

    # Main title
    st.title("Skin Lesion Triage Tool")
    st.markdown("### Prototype for Dermatological Image Assessment")

    # Show instructions
    show_instructions()

    # Create two columns for better layout
    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown(f"### {get_icon_html('camera', 24)} Lesion Image", unsafe_allow_html=True)
        uploaded_file = st.file_uploader(
            "Select a lesion image",
            type=["png", "jpg", "jpeg"],
            help="Upload a clear and well-lit photo of the skin lesion"
        )

        image = None
        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            st.image(image, caption="Image preview", use_container_width=True)
        else:
            st.info("Please upload an image to begin the analysis")

    with col2:
        st.markdown(f"### {get_icon_html('patient', 24)} Patient Information", unsafe_allow_html=True)

        age = st.number_input(
            "Patient age",
            min_value=0,
            max_value=120,
            value=30,
            help="Enter age in years"
        )

        sex = st.selectbox(
            "Sex",
            ["Male", "Female"],
            help="Select patient's sex"
        )

        st.markdown(f"### {get_icon_html('location', 24)} Lesion Information", unsafe_allow_html=True)

        lesion_location = st.selectbox(
            "Lesion location",
            [
                "Head and Neck",
                "Torso Front",
                "Torso Back",                
                "Left Leg",
                "Right Leg",
                "Left Arm",
                "Right Arm",                
            ],
            help="Select the anatomical location of the lesion"
        )

        lesion_diameter_mm = st.number_input(
            "Lesion diameter (mm)",
            min_value=0.0,
            max_value=200.0,
            value=5.0,
            step=0.5,
            help="Enter approximate diameter in millimeters"
        )

    # Analyze button
    st.markdown("---")
    col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])

    with col_btn2:
        analyze_button = st.button(f"Analyze Lesion", use_container_width=True)

    if analyze_button:
        if image is None:
            st.error("⚠️ Please upload an image before continuing with the analysis.")
        else:
            with st.spinner("Analyzing image..."):
                try:
                    # Create prediction service
                    prediction_service = create_service(base_url="http://localhost:8001")

                    # Reset file pointer to beginning
                    uploaded_file.seek(0)

                    # Prepare data for API
                    # Convert sex to lowercase as API expects
                    api_sex = sex.lower()

                    # Map location to API format (lowercase)
                    location_mapping = {
                        "Head and Neck": "head & neck",
                        "Torso Front": "torso front",
                        "Torso Back": "torso back",
                        "Left Leg": "left leg",
                        "Right Leg": "right leg",
                        "Left Arm": "left arm",
                        "Right Arm": "right arm"
                    }
                    api_location = location_mapping.get(lesion_location, lesion_location.lower())

                    # Submit prediction
                    response = prediction_service.submit_prediction(
                        image_file=uploaded_file,
                        age=age,
                        sex=api_sex,
                        location=api_location,
                        diameter=lesion_diameter_mm
                    )

                    # Print response to console for debugging
                    print("=" * 80)
                    print("API RESPONSE:")
                    print("=" * 80)
                    print(f"Final Probability: {response.final_probability}")
                    print(f"Model A Probability (DenseNet-121): {response.model_a_probability}")
                    print(f"Model C Probability (Random Forest): {response.model_c_probability}")
                    print(f"Risk Category: {response.risk_category.upper()}")
                    print(f"Extracted Features (count): {len(response.extracted_features)}")
                    print(f"Metadata: {json.dumps(response.metadata, indent=2)}")
                    print("=" * 80)

                    # Display complete prediction results
                    input_metadata = {
                        'age': age,
                        'sex': sex,
                        'location': lesion_location,
                        'diameter': lesion_diameter_mm
                    }

                    display_prediction_results(response, input_metadata)

                except Exception as e:
                    st.error(f"❌ Error during analysis: {str(e)}")
                    print(f"ERROR: {str(e)}")
                    st.info("💡 Make sure the backend API is running at http://localhost:8001")

    # Footer
    st.markdown("---")
    st.markdown(
        "<p style='text-align: center; color: #6b7280; font-size: 0.9rem;'>"
        "Skin Lesion Triage Prototype<br>"
        "<strong>For research purposes only, always consult a medical professional</strong><br>"
        "Developed as part of Dissertation project of MSc Artificial Intelligence Technology, Northumbria University London<br>"
        "This prototype was fueled by lots of coffee, persistence, late night coding, and a little AI magic!"
        "</p>",
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
