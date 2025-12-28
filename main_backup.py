import streamlit as st
from PIL import Image
import base64
from pathlib import Path
from io import BytesIO
import json
import plotly.graph_objects as go
import plotly.express as px
from prediction_service import create_service, PredictionResponse, ExplainResponse
from config import (
    PAGE_CONFIG, SUPPORTED_IMAGE_TYPES, LOCATION_DISPLAY_NAMES,
    AGE_MIN, AGE_MAX, AGE_DEFAULT, DIAMETER_MIN, DIAMETER_MAX,
    DIAMETER_DEFAULT, DIAMETER_STEP, SEX_OPTIONS, get_risk_color,
    CHART_COLORS, GAUGE_CONFIG, FEATURES_PER_ROW, MODEL_INFO,
    APP_TITLE, APP_SUBTITLE, FOOTER_HTML, ERROR_MESSAGES,
    SUCCESS_MESSAGES, API_BASE_URL, map_location_to_api
)


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


# Removed - now using get_risk_color from config


def calculate_risk_category(probability: float) -> str:
    """
    Calculate risk category based on probability threshold

    Args:
        probability: Probability value (0.0 - 1.0)

    Returns:
        Risk category: "low", "medium", or "high"
    """
    from config import RISK_THRESHOLDS

    if probability < RISK_THRESHOLDS["low"]:
        return "low"
    elif probability < RISK_THRESHOLDS["medium"]:
        return "medium"
    else:
        return "high"


def display_risk_assessment(response: PredictionResponse):
    """
    Display risk assessment with color coding and visual elements for both models

    Args:
        response: PredictionResponse object from API
    """
    st.markdown("### Estimated Risk Output")

    # Add explanatory text
    st.markdown("""
        <div style="
            background-color: #fef3c7;
            border-left: 4px solid #f59e0b;
            border-radius: 8px;
            padding: 1rem;
            margin: 1rem 0;
        ">
            <p style="color: #92400e; margin: 0; font-size: 0.9rem;">
                <strong><span class="material-symbols-rounded" style="vertical-align: middle; font-size: 1.2rem; margin-right: 0.3rem;">info</span>Understanding Risk Levels:</strong> LOW (&lt;30%) suggests benign characteristics,
                MEDIUM (30-70%) requires clinical evaluation, HIGH (≥70%) indicates concerning features requiring immediate attention.
            </p>
        </div>
    """, unsafe_allow_html=True)

    # Calculate risk categories for both models
    model_a_risk = calculate_risk_category(response.model_a_probability)
    model_c_risk = calculate_risk_category(response.model_c_probability)

    # Create two columns for side-by-side display
    col1, col2 = st.columns(2)

    with col1:
        color_a, bg_color_a, icon_a = get_risk_color(model_a_risk)

        st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, {bg_color_a} 0%, {color_a}15 100%);
                border-left: 6px solid {color_a};
                border-radius: 12px;
                padding: 1.5rem;
                margin: 1rem 0;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            ">
                <h3 style="color: #1e40af; margin: 0; font-size: 1.2rem;">Image Classifier Model</h3>
                <p style="color: #6b7280; font-size: 0.9rem; margin: 0.5rem 0;">Analyzes the uploaded image to estimate lesion risk based on visual patterns.</p>
                <h2 style="color: {color_a}; margin: 0.5rem 0 0 0; font-size: 1.8rem;">
                    {icon_a} {model_a_risk.upper()} RISK
                </h2>
                <p style="font-size: 1.5rem; color: #374151; margin: 0.5rem 0 0 0;">
                    <strong style="color: {color_a};">{response.model_a_probability:.1%}</strong>
                </p>
            </div>
        """, unsafe_allow_html=True)

        # Gauge for Model A
        fig_a = go.Figure(go.Indicator(
            mode="gauge+number",
            value=response.model_a_probability * 100,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Image Classifier Model Risk (%)", 'font': {'size': 18}},
            number={'suffix': "%", 'font': {'size': 32}},
            gauge={
                'axis': {'range': GAUGE_CONFIG['range'], 'tickwidth': 2, 'tickcolor': color_a},
                'bar': {'color': color_a, 'thickness': 0.75},
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "#e5e7eb",
                'steps': [
                    {'range': GAUGE_CONFIG['low_range'], 'color': '#f0fdf4'},
                    {'range': GAUGE_CONFIG['medium_range'], 'color': '#fffbeb'},
                    {'range': GAUGE_CONFIG['high_range'], 'color': '#fef2f2'}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': GAUGE_CONFIG['threshold_value']
                }
            }
        ))

        fig_a.update_layout(
            height=250,
            margin=dict(l=20, r=20, t=40, b=20),
            paper_bgcolor="rgba(0,0,0,0)",
            font={'family': "Inter, sans-serif"}
        )

        st.plotly_chart(fig_a, use_container_width=True)

    with col2:
        color_c, bg_color_c, icon_c = get_risk_color(model_c_risk)

        st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, {bg_color_c} 0%, {color_c}15 100%);
                border-left: 6px solid {color_c};
                border-radius: 12px;
                padding: 1.5rem;
                margin: 1rem 0;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            ">
                <h3 style="color: #15803d; margin: 0; font-size: 1.2rem;">Feature-Based Risk Model</h3>
                <p style="color: #6b7280; font-size: 0.9rem; margin: 0.5rem 0;">Estimates lesion risk using extracted image features combined with patient data.</p>
                <h2 style="color: {color_c}; margin: 0.5rem 0 0 0; font-size: 1.8rem;">
                    {icon_c} {model_c_risk.upper()} RISK
                </h2>
                <p style="font-size: 1.5rem; color: #374151; margin: 0.5rem 0 0 0;">
                    <strong style="color: {color_c};">{response.model_c_probability:.1%}</strong>
                </p>
            </div>
        """, unsafe_allow_html=True)

        # Gauge for Model C
        fig_c = go.Figure(go.Indicator(
            mode="gauge+number",
            value=response.model_c_probability * 100,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Feature-Based Risk Model Risk (%)", 'font': {'size': 18}},
            number={'suffix': "%", 'font': {'size': 32}},
            gauge={
                'axis': {'range': GAUGE_CONFIG['range'], 'tickwidth': 2, 'tickcolor': color_c},
                'bar': {'color': color_c, 'thickness': 0.75},
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "#e5e7eb",
                'steps': [
                    {'range': GAUGE_CONFIG['low_range'], 'color': '#f0fdf4'},
                    {'range': GAUGE_CONFIG['medium_range'], 'color': '#fffbeb'},
                    {'range': GAUGE_CONFIG['high_range'], 'color': '#fef2f2'}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': GAUGE_CONFIG['threshold_value']
                }
            }
        ))

        fig_c.update_layout(
            height=250,
            margin=dict(l=20, r=20, t=40, b=20),
            paper_bgcolor="rgba(0,0,0,0)",
            font={'family': "Inter, sans-serif"}
        )

        st.plotly_chart(fig_c, use_container_width=True)


def display_model_breakdown(response: PredictionResponse):
    """
    Display individual model contributions with comparison chart

    Args:
        response: PredictionResponse object from API
    """
    st.markdown("### Comparison of Estimated Risks")

    # Comparison bar chart
    fig = go.Figure(data=[
        go.Bar(
            name='Model Predictions',
            x=['Image Classifier\nModel', 'Feature-Based\nRisk Model'],
            y=[response.model_a_probability * 100,
               response.model_c_probability * 100],
            marker_color=[CHART_COLORS['model_a'], CHART_COLORS['model_c']],
            text=[f"{response.model_a_probability:.1%}",
                  f"{response.model_c_probability:.1%}"],
            textposition='auto',
            textfont=dict(size=14, color='white')
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

    # Show agreement/disagreement
    diff = abs(response.model_a_probability - response.model_c_probability)
    if diff < 0.1:
        st.success(f"✅ Strong agreement between models (difference: {diff:.1%})")
    elif diff < 0.3:
        st.warning(f"⚠️ Moderate agreement between models (difference: {diff:.1%})")
    else:
        st.error(f"🚨 Significant disagreement between models (difference: {diff:.1%}) - Consider additional evaluation")


def display_extracted_features(response: PredictionResponse):
    """
    Display extracted features in an expandable section

    Args:
        response: PredictionResponse object from API
    """
    with st.expander("🔬 Extracted Features (Model B - ResNet-50)", expanded=False):
        st.markdown(f"""
            <div style="line-height: 1.6;">
                <p style="color: #6b7280; margin-bottom: 1rem;">
                    <strong>What are these features?</strong>
                </p>
                <p style="color: #6b7280; margin-bottom: 1rem;">
                    These are the 18 visual features automatically extracted from the lesion image by {MODEL_INFO['model_b']['architecture']}.
                    The feature extractor identifies visual patterns such as color distribution, texture, shape asymmetry,
                    and border characteristics - all important dermatological indicators.
                </p>
                <p style="color: #6b7280; margin-bottom: 1rem;">
                    These features are combined with patient metadata (age, sex, location, diameter) and fed into
                    Model C ({MODEL_INFO['model_c']['architecture']}) for classification.
                </p>
            </div>
        """, unsafe_allow_html=True)

        # Display features in a grid
        num_features = len(response.extracted_features)

        for i in range(0, num_features, FEATURES_PER_ROW):
            cols = st.columns(FEATURES_PER_ROW)
            for j, col in enumerate(cols):
                idx = i + j
                if idx < num_features:
                    with col:
                        st.metric(
                            label=f"F{idx + 1}",
                            value=f"{response.extracted_features[idx]:.2f}"
                        )


def display_shap_explanation(explain_response: ExplainResponse):
    """
    Display SHAP explanation with waterfall chart

    Args:
        explain_response: ExplainResponse object from API
    """
    st.markdown("### Feature Contributions - Feature-Based Risk Model")

    st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #e0f2f7 0%, #b3e5f0 100%);
            border-left: 4px solid #2d8a9b;
            border-radius: 8px;
            padding: 1rem;
            margin: 1rem 0;
        ">
            <p style="color: #2d8a9b; margin: 0.5rem 0; font-size: 1rem;">
                <strong><span class="material-symbols-rounded" style="vertical-align: middle; font-size: 1.2rem; margin-right: 0.3rem;">help_clinic</span>Understanding Feature Contributions:</strong>
            </p>
            <p style="color: #2d8a9b; margin: 0.5rem 0; font-size: 0.9rem; line-height: 1.6;">
                Each bar shows how much a specific feature influenced the risk estimate for this lesion.
                This provides transparency and helps interpret the Feature-Based Risk Model’s output.
            </p>
            <ul style="list-style-type: circle; color: #2d8a9b; margin: 0.5rem 0; font-size: 0.9rem; line-height: 1.6;">
                <li><span style="color: #ef4444; font-weight: 600;">Red bars (positive values)</span>: Features pushing towards higher malignancy risk</li>
                <li><span style="color: #3b82f6; font-weight: 600;">Blue bars (negative values)</span>: Features pushing towards lower malignancy risk</li>
                <li><strong>Bar length</strong>: Represents the magnitude of influence on the prediction</li>
                <li><strong>Base Value</strong>: Average prediction across all training samples</li>
                <li><strong>Final Prediction</strong>: Base value plus all feature contributions equals the model output</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)

    # Display summary metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(
            "Feature-Based Risk Model",
            f"{explain_response.prediction:.1%}",
            help="Final prediction probability from Feature-Based Risk Model (XGBoost) after considering all features"
        )
    with col2:
        st.metric(
            "Base Value",
            f"{explain_response.base_value:.1%}",
            help="The average prediction across all training samples - the starting point before feature contributions"
        )
    with col3:
        impact_sum = sum(abs(fc.shap_value) for fc in explain_response.feature_contributions)
        st.metric(
            "Total Impact",
            f"{impact_sum:.3f}",
            help="Sum of absolute SHAP values - represents the total magnitude of feature influence"
        )

    # Prepare data for waterfall chart
    # Sort by absolute SHAP value (most impactful first)
    sorted_features = sorted(
        explain_response.feature_contributions,
        key=lambda x: abs(x.shap_value),
        reverse=True
    )

    # Take top 5 features for clarity
    top_n = 5
    top_features = sorted_features[:top_n]

    # Waterfall chart
    st.markdown(f"#### Top {top_n} Most Influential Features")

    st.markdown("""
        <p style="color: #6b7280; font-size: 0.9rem; margin-bottom: 1rem;">
            The features below had the strongest impact on this prediction. Hover over bars for detailed values.
        </p>
    """, unsafe_allow_html=True)

    # Prepare data for waterfall (using display_name for readability)
    feature_names = [fc.display_name for fc in top_features]
    shap_values = [fc.shap_value for fc in top_features]
    feature_values = [fc.feature_value for fc in top_features]

    # Create colors based on impact
    colors = ['#ef4444' if fc.impact == 'increases' else '#3b82f6' for fc in top_features]

    # Create horizontal bar chart (easier to read than waterfall for many features)
    fig = go.Figure()

    fig.add_trace(go.Bar(
        y=feature_names,
        x=shap_values,
        orientation='h',
        marker=dict(
            color=colors,
            line=dict(color='rgba(0,0,0,0.3)', width=1)
        ),
        text=[f"{sv:+.3f}" for sv in shap_values],
        textposition='outside',
        hovertemplate='<b>%{y}</b><br>' +
                      'SHAP Value: %{x:.4f}<br>' +
                      'Feature Value: %{customdata:.2f}<br>' +
                      '<extra></extra>',
        customdata=feature_values
    ))

    fig.update_layout(
        title=dict(
            text=f"Feature Contributions values (Base: {explain_response.base_value:.3f} → Prediction: {explain_response.prediction:.3f})",
            font=dict(size=14)
        ),
        xaxis_title="Feature Contributions value",
        yaxis_title="Features",
        height=600,
        margin=dict(l=20, r=100, t=60, b=40),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(250,250,250,1)",
        font={'family': "Inter, sans-serif"},
        xaxis=dict(
            gridcolor='#e5e7eb',
            gridwidth=1,
            zeroline=True,
            zerolinecolor='#374151',
            zerolinewidth=2
        ),
        yaxis=dict(
            autorange="reversed"  # Show most important at top
        )
    )

    st.plotly_chart(fig, use_container_width=True)

    # Warning message
    st.markdown("""
        <div style="background-color: #fef3c7; padding: 1rem; border-radius: 8px; margin-top: 1rem; border-left: 4px solid #f59e0b;">
            <p style="color: #92400e; margin: 0;"><strong><span class="material-symbols-rounded" style="vertical-align: middle; font-size: 1.2rem; margin-right: 0.3rem;">warning</span>Important:</strong> Feature Contributions shows which factors influence the output,
            but they don't guarantee clinical accuracy. Always combine AI insights with professional medical judgment.</p>
        </div>
    """, unsafe_allow_html=True)


def display_prediction_results(response: PredictionResponse, input_metadata: dict):
    """
    Main function to display all prediction results

    Args:
        response: PredictionResponse object from API
        input_metadata: Dictionary with input data (age, sex, location, diameter)
    """
    # st.markdown("---")

    # Risk assessment (main display)
    display_risk_assessment(response)

    # Model breakdown
    display_model_breakdown(response)

    # Removed extracted features section
    # Removed input summary section


def main():
    # Configure page
    st.set_page_config(**PAGE_CONFIG)

    # Apply custom styles
    apply_custom_styles()

    # Main title
    st.title(APP_TITLE)
    st.markdown(f"### {APP_SUBTITLE}")

    # Show instructions
    show_instructions()

    # Add medical disclaimer
    st.markdown("""
        <div style="
            background-color: #fef2f2;
            border: 2px solid #ef4444;
            border-radius: 10px;
            padding: 1.2rem;
            margin: 1.5rem 0;
        ">
            <p style="color: #991b1b; margin: 0; font-size: 0.95rem; line-height: 1.6;">
                <strong>⚠️ MEDICAL DISCLAIMERrrr:</strong> This tool is a <strong>research prototype</strong> for educational purposes only.
                It does NOT provide medical diagnosis and should NOT replace professional medical evaluation.
                <strong>Always consult a qualified dermatologist</strong> for any skin lesion concerns.
            </p>
        </div>
    """, unsafe_allow_html=True)

    # Create two columns for better layout
    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown(f"### {get_icon_html('camera', 24)} Lesion Image", unsafe_allow_html=True)
        uploaded_file = st.file_uploader(
            "Select a lesion image",
            type=SUPPORTED_IMAGE_TYPES,
            help="📸 Upload a clear and well-lit photo of the skin lesion. Supported formats: PNG, JPG, JPEG, BMP, TIFF. Maximum file size: 10MB."
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
            min_value=AGE_MIN,
            max_value=AGE_MAX,
            value=AGE_DEFAULT,
            help="👤 Enter patient's age in years (0-120). Age is an important risk factor for skin cancer."
        )

        sex = st.selectbox(
            "Sex",
            SEX_OPTIONS,
            help="👤 Select patient's biological sex. Male patients have higher incidence rates of melanoma."
        )

        st.markdown(f"### {get_icon_html('location', 24)} Lesion Information", unsafe_allow_html=True)

        lesion_location = st.selectbox(
            "Lesion location",
            list(LOCATION_DISPLAY_NAMES.keys()),
            help="📍 Select the anatomical location where the lesion is found. Some body areas have higher melanoma risk (e.g., back, trunk)."
        )

        lesion_diameter_mm = st.number_input(
            "Lesion diameter (mm)",
            min_value=DIAMETER_MIN,
            max_value=DIAMETER_MAX,
            value=DIAMETER_DEFAULT,
            step=DIAMETER_STEP,
            help="📏 Enter the approximate diameter of the lesion in millimeters. Larger lesions (>6mm) may indicate higher risk according to the ABCDE rule."
        )

    # Analyze button
    st.markdown("---")
    col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])

    with col_btn2:
        analyze_button = st.button(f"Analyze Lesion", use_container_width=True)

    # Initialize session state for results
    if 'results_ready' not in st.session_state:
        st.session_state.results_ready = False
    if 'show_shap' not in st.session_state:
        st.session_state.show_shap = False

    if analyze_button:
        if image is None:
            st.error(ERROR_MESSAGES["no_image"])
        else:
            with st.spinner("🔬 Analyzing lesion image... This may take a few seconds..."):
                try:
                    # Create prediction service
                    prediction_service = create_service()

                    # Reset file pointer to beginning
                    uploaded_file.seek(0)

                    # Prepare data for API
                    # Convert sex to lowercase as API expects
                    api_sex = sex.lower()

                    # Map location to API format using config
                    api_location = map_location_to_api(lesion_location)

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
                    print(f"Model A Probability (DenseNet-121): {response.model_a_probability}")
                    print(f"Model C Probability (XGBoost): {response.model_c_probability}")
                    print(f"Model A Risk: {calculate_risk_category(response.model_a_probability).upper()}")
                    print(f"Model C Risk: {calculate_risk_category(response.model_c_probability).upper()}")
                    print(f"Extracted Features (count): {len(response.extracted_features)}")
                    print(f"Metadata: {json.dumps(response.metadata, indent=2)}")
                    print("=" * 80)

                    # Store in session state
                    st.session_state.last_response = response
                    st.session_state.last_uploaded_file = uploaded_file
                    st.session_state.last_input = {
                        'age': age,
                        'sex': api_sex,
                        'location': api_location,
                        'diameter': lesion_diameter_mm
                    }
                    st.session_state.last_display_metadata = {
                        'age': age,
                        'sex': sex,
                        'location': lesion_location,
                        'diameter': lesion_diameter_mm
                    }
                    st.session_state.results_ready = True
                    st.session_state.show_shap = False  # Reset SHAP visibility

                except Exception as e:
                    st.error(ERROR_MESSAGES["prediction_failed"].format(error=str(e)))
                    print(f"ERROR: {str(e)}")
                    st.info(ERROR_MESSAGES["api_connection"].format(api_url=API_BASE_URL))
                    st.session_state.results_ready = False

    # Display results if available
    if st.session_state.results_ready:
        display_prediction_results(st.session_state.last_response, st.session_state.last_display_metadata)

        # SHAP Explanation Section (on-demand)
        st.markdown("---")
        st.markdown("### 🔍 Model Explainability")

        # Add explanatory text about SHAP
        st.markdown("""
            <div style="
                background-color: #ede9fe;
                border-left: 4px solid #8b5cf6;
                border-radius: 8px;
                padding: 1rem;
                margin: 1rem 0;
            ">
                <p style="color: #5b21b6; margin: 0; font-size: 0.9rem;">
                    <strong>💡 What is SHAP?</strong> SHAP (SHapley Additive exPlanations) provides a detailed breakdown
                    of how each feature influenced Model C's prediction. Click below to see which visual and clinical
                    features were most important for this specific case.
                </p>
            </div>
        """, unsafe_allow_html=True)

        col_exp1, col_exp2, col_exp3 = st.columns([1, 2, 1])

        with col_exp2:
            if st.button("📊 View Detailed SHAP Explanation", use_container_width=True, type="primary"):
                st.session_state.show_shap = not st.session_state.show_shap

        # Display SHAP if toggled on
        if st.session_state.show_shap:
            with st.spinner("🔍 Generating SHAP explanation... Computing feature contributions..."):
                try:
                    # Create prediction service
                    prediction_service = create_service()

                    # Reset file pointer
                    st.session_state.last_uploaded_file.seek(0)

                    # Get SHAP explanation
                    explain_response = prediction_service.get_explanation(
                        image_file=st.session_state.last_uploaded_file,
                        age=st.session_state.last_input['age'],
                        sex=st.session_state.last_input['sex'],
                        location=st.session_state.last_input['location'],
                        diameter=st.session_state.last_input['diameter']
                    )

                    # Display SHAP explanation
                    display_shap_explanation(explain_response)

                except Exception as e:
                    st.error(f"❌ Failed to generate explanation: {str(e)}")
                    print(f"SHAP ERROR: {str(e)}")

    # Footer
    st.markdown("---")
    st.markdown(FOOTER_HTML, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
