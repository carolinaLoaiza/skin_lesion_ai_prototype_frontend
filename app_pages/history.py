"""
History Page - Patient medical history and lesion tracking

This page allows users to:
1. Search for a patient
2. View all lesions for that patient
3. See analysis timeline for each lesion
4. View evolution graphs (size and risk over time)
5. Compare multiple analyses
"""

import streamlit as st
from PIL import Image
from datetime import datetime
import plotly.graph_objects as go
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import FOOTER_HTML, ERROR_MESSAGES, API_BASE_URL, get_risk_color
from patient_lesion_service import create_patient_lesion_service
from analysis_service import create_analysis_service
from utils.validators import calculate_age_from_dob
import requests


def render():
    """Main render function for history page"""

    # Utility to load base64 images
    def load_image_base64(image_filename):
        """Load image from assets folder and convert to base64"""
        import base64
        from pathlib import Path

        image_path = Path(__file__).parent.parent / "assets" / image_filename
        if not image_path.exists():
            return ""

        with open(image_path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode()
            ext = image_path.suffix[1:]  # Remove the dot
            return f"data:image/{ext};base64,{encoded}"

    # Load records icon
    records_icon_base64 = load_image_base64('records.png')
    records_icon_html = f'<img src="{records_icon_base64}" style="width: 32px; height: 32px; vertical-align: middle; margin-right: 10px;">' if records_icon_base64 else ""

    st.markdown(f"# {records_icon_html}Patient History & Medical Records", unsafe_allow_html=True)

    # Load feature display names from backend (cache in session state)
    if 'feature_display_names' not in st.session_state:
        try:
            analysis_service = create_analysis_service()
            st.session_state.feature_display_names = analysis_service.get_feature_display_names()
        except:
            st.session_state.feature_display_names = {}

    # Section 1: Patient Search
    render_patient_search()

    # Section 2: Patient Overview (if selected)
    if 'selected_patient_history' in st.session_state and st.session_state.selected_patient_history:
        st.markdown("---")
        render_patient_overview()

        # Section 3: Lesions & Analyses
        st.markdown("---")
        render_lesions_and_analyses()

    # Footer
    st.markdown("---")
    st.markdown(FOOTER_HTML, unsafe_allow_html=True)


def render_patient_search():
    """Render patient search section"""
    st.markdown("## Select Patient")

    # Clear selection button (if patient selected)
    if 'selected_patient_history' in st.session_state and st.session_state.selected_patient_history:
        if st.button("← Back to Patient Search", key="back_to_search"):
            st.session_state.selected_patient_history = None
            st.session_state.selected_patient_lesions = []
            st.rerun()
        return

    # Search mode selection
    search_mode = st.radio(
        "Search method:",
        ["Search by Name", "Browse All Patients"],
        horizontal=True,
        key="history_search_mode"
    )

    if search_mode == "Search by Name":
        render_search_by_name()
    else:
        render_browse_all_patients()


def render_search_by_name():
    """Render search by name with autocomplete"""
    st.markdown("### Search by Patient Name")

    search_term = st.text_input(
        "Patient name",
        placeholder="Type at least 2 characters...",
        help="Search for patients by name",
        key="history_search_input"
    )

    if len(search_term) >= 2:
        try:
            service = create_patient_lesion_service()
            patients = service.search_patients_by_name(search_term)

            if not patients:
                st.info("No patients found matching your search")
            else:
                st.markdown(f"Found **{len(patients)}** patient(s):")

                for patient in patients:
                    col1, col2 = st.columns([3, 1])

                    with col1:
                        age = calculate_age_from_dob(patient.date_of_birth)
                        st.markdown(f"""
                            **{patient.patient_full_name}**
                            - ID: `{patient.patient_id}`
                            - Age: {age} years | Sex: {patient.sex.title()}
                            - DOB: {patient.date_of_birth}
                        """)

                    with col2:
                        if st.button("View History", key=f"view_history_{patient.patient_id}"):
                            st.session_state.selected_patient_history = patient
                            st.rerun()

        except Exception as e:
            st.error(f"❌ Search failed: {str(e)}")


def render_browse_all_patients():
    """Render all patients in a table"""
    st.markdown("### All Patients")

    try:
        analysis_service = create_analysis_service()
        patients_data = analysis_service.get_all_patients()

        if not patients_data:
            st.info("No patients found in the system")
        else:
            st.markdown(f"Total patients: **{len(patients_data)}**")

            # Create table
            for patient_dict in patients_data:
                col1, col2 = st.columns([3, 1])

                with col1:
                    age = calculate_age_from_dob(patient_dict['date_of_birth'])
                    st.markdown(f"""
                        **{patient_dict['patient_full_name']}**
                        - ID: `{patient_dict['patient_id']}`
                        - Age: {age} years | Sex: {patient_dict['sex'].title()}
                        - DOB: {patient_dict['date_of_birth']}
                    """)

                with col2:
                    if st.button("View History", key=f"view_history_all_{patient_dict['patient_id']}"):
                        # Convert dict to Patient-like object for consistency
                        from patient_lesion_service import Patient
                        patient = Patient(
                            patient_id=patient_dict['patient_id'],
                            patient_full_name=patient_dict['patient_full_name'],
                            sex=patient_dict['sex'],
                            date_of_birth=patient_dict['date_of_birth'],
                            created_at=patient_dict.get('created_at'),
                            _id=patient_dict.get('_id')
                        )
                        st.session_state.selected_patient_history = patient
                        st.rerun()

    except Exception as e:
        st.error(f"❌ Failed to load patients: {str(e)}")


def render_patient_overview():
    """Render patient overview section"""
    st.markdown("## Patient Overview")

    patient = st.session_state.selected_patient_history
    age = calculate_age_from_dob(patient.date_of_birth)

    # Load patient icon
    def load_image_base64(image_filename):
        """Load image from assets folder and convert to base64"""
        import base64
        from pathlib import Path

        image_path = Path(__file__).parent.parent / "assets" / image_filename
        if not image_path.exists():
            return ""

        with open(image_path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode()
            ext = image_path.suffix[1:]
            return f"data:image/{ext};base64,{encoded}"

    patient_icon_base64 = load_image_base64('patient.png')
    patient_icon_html = f'<img src="{patient_icon_base64}" style="width: 28px; height: 28px; vertical-align: middle; margin-right: 8px;">' if patient_icon_base64 else ""

    # Patient info card
    st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #a8d5dd 0%, #7eb8c4 100%);
            border-radius: 12px;
            padding: 1.5rem;
            color: #0a3940;
            margin-bottom: 1.5rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        ">
            <h2 style="color: #0a3940; margin: 0 0 1rem 0;">{patient_icon_html}{patient.patient_full_name}</h2>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem;">
                <div>
                    <p style="margin: 0; opacity: 0.9; font-size: 0.9rem;">Patient ID</p>
                    <p style="margin: 0; font-weight: 600; font-size: 1.1rem;">{patient.patient_id}</p>
                </div>
                <div>
                    <p style="margin: 0; opacity: 0.9; font-size: 0.9rem;">Age</p>
                    <p style="margin: 0; font-weight: 600; font-size: 1.1rem;">{age} years</p>
                </div>
                <div>
                    <p style="margin: 0; opacity: 0.9; font-size: 0.9rem;">Sex</p>
                    <p style="margin: 0; font-weight: 600; font-size: 1.1rem;">{patient.sex.title()}</p>
                </div>
                <div>
                    <p style="margin: 0; opacity: 0.9; font-size: 0.9rem;">Date of Birth</p>
                    <p style="margin: 0; font-weight: 600; font-size: 1.1rem;">{patient.date_of_birth}</p>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Load patient's lesions
    try:
        service = create_patient_lesion_service()
        lesions = service.get_lesions_by_patient(patient.patient_id)
        st.session_state.selected_patient_lesions = lesions

        # Summary statistics
        total_lesions = len(lesions)
        total_analyses = 0

        # Get analyses count for each lesion
        analysis_service = create_analysis_service()
        for lesion in lesions:
            try:
                analyses = analysis_service.get_lesion_analyses(lesion.lesion_id)
                total_analyses += len(analyses)
            except:
                pass

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Lesions", total_lesions)

        with col2:
            st.metric("Total Analyses", total_analyses)

        with col3:
            if lesions:
                first_date = min(l.created_at for l in lesions if l.created_at)
                st.metric("First Visit", first_date[:10] if first_date else "N/A")
            else:
                st.metric("First Visit", "N/A")

        with col4:
            if lesions:
                last_date = max(l.created_at for l in lesions if l.created_at)
                st.metric("Last Visit", last_date[:10] if last_date else "N/A")
            else:
                st.metric("Last Visit", "N/A")

    except Exception as e:
        st.error(f"❌ Failed to load patient data: {str(e)}")
        st.session_state.selected_patient_lesions = []


def render_lesions_and_analyses():
    """Render lesions and their analysis timelines"""
    st.markdown("## Lesions & Analysis History")

    if not st.session_state.selected_patient_lesions:
        st.info("This patient has no lesions registered yet.")
        return

    analysis_service = create_analysis_service()

    for lesion in st.session_state.selected_patient_lesions:
        with st.container():
            # Lesion header
            st.markdown(f"""
                <div style="
                    background: linear-gradient(135deg, #a8d5dd 0%, #7eb8c4 100%);
                    border-radius: 12px;
                    padding: 1.5rem;
                    color: #0a3940;
                    margin: 1rem 0;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                ">
                    <h3 style="color: #0a3940; margin: 0 0 1rem 0; font-weight: 600;">{lesion.lesion_location.title()}</h3>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 1rem;">
                        <div>
                            <p style="margin: 0; opacity: 0.9; font-size: 0.9rem;">Lesion ID</p>
                            <p style="margin: 0; font-weight: 600; font-size: 1.1rem;">{lesion.lesion_id}</p>
                        </div>
                        <div>
                            <p style="margin: 0; opacity: 0.9; font-size: 0.9rem;">Initial Size</p>
                            <p style="margin: 0; font-weight: 600; font-size: 1.1rem;">{lesion.initial_size_mm} mm</p>
                        </div>
                        <div>
                            <p style="margin: 0; opacity: 0.9; font-size: 0.9rem;">Created</p>
                            <p style="margin: 0; font-weight: 600; font-size: 1.1rem;">{lesion.created_at[:10] if lesion.created_at else 'N/A'}</p>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            # Load analyses for this lesion
            try:
                analyses = analysis_service.get_lesion_analyses(lesion.lesion_id)

                if not analyses:
                    st.info(f"No analyses found for {lesion.lesion_id}")
                else:
                    # Evolution graphs - size and probability separated
                    render_size_evolution_graph(lesion, analyses)
                    render_probability_evolution_graph(lesion, analyses)

                    st.markdown("---")

                    # Analysis timeline
                    render_analysis_timeline(lesion, analyses)

            except Exception as e:
                st.error(f"❌ Failed to load analyses for {lesion.lesion_id}: {str(e)}")

            # st.markdown("---")


def render_size_evolution_graph(lesion, analyses):
    """Render size evolution graph over time"""
    st.markdown('<h3 style="margin-bottom: 0.5rem;">Lesion Size Evolution</h3>', unsafe_allow_html=True)

    # Prepare data - dates only (no timestamps)
    dates = [a.capture_datetime.strftime('%d/%m/%Y') for a in analyses]
    sizes = [a.lesion_size_mm for a in analyses]

    # Create figure
    fig = go.Figure()

    # Add size trace
    fig.add_trace(
        go.Scatter(
            x=dates,
            y=sizes,
            name="Size (mm)",
            mode='lines+markers',
            line=dict(color='#3b82f6', width=3),
            marker=dict(size=12, color='#3b82f6'),
            hovertemplate='<b>Size:</b> %{y:.1f} mm<br><b>Date:</b> %{x}<extra></extra>'
        )
    )

    # Update axes
    fig.update_xaxes(title_text="Date")
    fig.update_yaxes(title_text="Lesion Size (mm)")

    # Update layout
    fig.update_layout(
        height=350,
        hovermode='x unified',
        showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(250,250,250,1)",
        font={'family': "Inter, sans-serif"}
    )

    st.plotly_chart(fig, use_container_width=True)


def render_probability_evolution_graph(lesion, analyses):
    """Render malignancy probability evolution graph over time"""
    st.markdown('<h3 style="margin-bottom: 0.5rem;">Malignancy Probability Evolution</h3>', unsafe_allow_html=True)

    # Prepare data - dates only (no timestamps)
    dates = [a.capture_datetime.strftime('%d/%m/%Y') for a in analyses]
    model_a_probs = [a.model_a_probability * 100 for a in analyses]
    model_c_probs = [a.model_c_probability * 100 for a in analyses]

    # Create figure
    fig = go.Figure()

    # Add Model A probability trace
    fig.add_trace(
        go.Scatter(
            x=dates,
            y=model_a_probs,
            name="Image Classifier model",
            mode='lines+markers',
            line=dict(color='#8b5cf6', width=3),
            marker=dict(size=10, color='#8b5cf6'),
            hovertemplate='<b>Image Classifier model:</b> %{y:.1f}%<br><b>Date:</b> %{x}<extra></extra>'
        )
    )

    # Add Model C probability trace
    fig.add_trace(
        go.Scatter(
            x=dates,
            y=model_c_probs,
            name="Feature-Based Risk Model",
            mode='lines+markers',
            line=dict(color='#22c55e', width=3),
            marker=dict(size=10, color='#22c55e'),
            hovertemplate='<b>Feature-Based Risk Model:</b> %{y:.1f}%<br><b>Date:</b> %{x}<extra></extra>'
        )
    )

    # Update axes
    fig.update_xaxes(title_text="Date")
    fig.update_yaxes(title_text="Malignancy Probability (%)", range=[0, 100])

    # Update layout
    fig.update_layout(
        height=350,
        hovermode='x unified',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(250,250,250,1)",
        font={'family': "Inter, sans-serif"}
    )

    st.plotly_chart(fig, use_container_width=True)


def render_analysis_timeline(lesion, analyses):
    """Render timeline of analyses for a lesion"""
    st.markdown("### Analysis Timeline")

    st.markdown(f"**Total analyses:** {len(analyses)}")

    # Reverse to show newest first
    for i, analysis in enumerate(reversed(analyses)):
        render_analysis_card(analysis, len(analyses) - i)


def render_analysis_card(analysis, index):
    """Render a single analysis card in the timeline"""

    # Utility to load base64 images
    def load_image_base64(image_filename):
        """Load image from assets/images folder and convert to base64"""
        import base64
        from pathlib import Path

        image_path = Path(__file__).parent.parent / "assets" / "images" / image_filename
        if not image_path.exists():
            return ""

        with open(image_path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode()
            ext = image_path.suffix[1:]
            return f"data:image/{ext};base64,{encoded}"

    # Calculate risk categories
    risk_a = calculate_risk_category(analysis.model_a_probability)
    risk_c = calculate_risk_category(analysis.model_c_probability)
    color_a, _, icon_a = get_risk_color(risk_a)
    color_c, _, icon_c = get_risk_color(risk_c)

    # Format date
    capture_date_str = analysis.capture_datetime.strftime("%d/%m/%Y %H:%M")

    # Determine if this is the initial analysis
    is_initial = analysis.days_since_first_observation == 0
    days_tag = "(Initial)" if is_initial else f"(Day {analysis.days_since_first_observation})"

    # Analysis card
    with st.expander(f"{capture_date_str} {days_tag} - Size: {analysis.lesion_size_mm} mm", expanded=(index == 1)):
        col1, col2 = st.columns(2)

        with col1:
            # Show lesion image using the dedicated image endpoint
            try:
                # Use the new /api/analyses/{analysis_id}/image endpoint
                image_url = create_analysis_service().get_analysis_image_url(analysis.analysis_id)

                response = requests.get(image_url, timeout=10)

                if response.status_code == 200:
                    from io import BytesIO
                    image = Image.open(BytesIO(response.content))
                    st.image(image, use_container_width=True)
                    # Show filename below image
                    if analysis.image_filename:
                        st.caption(f"{analysis.image_filename}")
                elif response.status_code == 404:
                    st.info("No image available for this analysis")
                else:
                    st.warning(f"Image not accessible (HTTP {response.status_code})")
                    if st.session_state.get('show_debug_info', False):
                        st.caption(f"URL: {image_url}")

            except requests.exceptions.Timeout:
                st.warning("Image load timeout. Backend may be slow.")
            except Exception as e:
                st.warning(f"Could not load image")
                if st.session_state.get('show_debug_info', False):
                    with st.expander("Error details"):
                        st.code(f"URL: {image_url}\nError: {str(e)}")

        with col2:
            # Analysis details in styled box
            st.markdown(f"""
                <div style="
                    background: linear-gradient(135deg, #e0f2f7 0%, #b3e5f0 100%);
                    border-radius: 8px;
                    padding: 1rem;
                    margin-bottom: 1rem;
                ">
                    <p style="margin: 0.3rem 0; color: #0a3940; font-size: 0.95rem;"><strong>Analysis ID:</strong> {analysis.analysis_id}</p>
                    <p style="margin: 0.3rem 0; color: #0a3940; font-size: 0.95rem;"><strong>Capture Date:</strong> {capture_date_str}</p>
                    <p style="margin: 0.3rem 0; color: #0a3940; font-size: 0.95rem;"><strong>Days Since First Observation:</strong> {analysis.days_since_first_observation}</p>
                    <p style="margin: 0.3rem 0; color: #0a3940; font-size: 0.95rem;"><strong>Patient Age:</strong> {analysis.age_at_capture} years</p>
                    <p style="margin: 0.3rem 0; color: #0a3940; font-size: 0.95rem;"><strong>Lesion Size:</strong> {analysis.lesion_size_mm} mm</p>
                </div>
            """, unsafe_allow_html=True)

            st.markdown("---")

            # Risk assessment
            st.markdown("**Risk Assessment:**")

            st.markdown(f"""
                <div style="
                    background-color: #f0f9ff;
                    border-left: 4px solid {color_a};
                    border-radius: 8px;
                    padding: 1rem;
                    margin: 0.5rem 0;
                ">
                    <p style="margin: 0; color: #1e40af; font-weight: 600;">Image Classifier Model</p>
                    <p style="margin: 0.5rem 0 0 0; color: {color_a}; font-size: 1.5rem; font-weight: 700;">
                        {icon_a} {analysis.model_a_probability:.1%} - {risk_a.upper()}
                    </p>
                </div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
                <div style="
                    background-color: #f0fdf4;
                    border-left: 4px solid {color_c};
                    border-radius: 8px;
                    padding: 1rem;
                    margin: 0.5rem 0;
                ">
                    <p style="margin: 0; color: #15803d; font-weight: 600;">Feature-Based Risk Model</p>
                    <p style="margin: 0.5rem 0 0 0; color: {color_c}; font-size: 1.5rem; font-weight: 700;">
                        {icon_c} {analysis.model_c_probability:.1%} - {risk_c.upper()}
                    </p>
                </div>
            """, unsafe_allow_html=True)

        # Advanced Analysis Section (SHAP + Extracted Features)
        if analysis.shap_top_features or (hasattr(analysis, 'extracted_features') and analysis.extracted_features):
            st.markdown("---")

            # Warning message
            st.markdown("""
                <div style="
                    background-color: #fef3c7;
                    border-left: 4px solid #f59e0b;
                    border-radius: 8px;
                    padding: 1rem;
                    margin: 1rem 0;
                ">
                    <p style="color: #92400e; margin: 0; font-size: 0.9rem;">
                        <strong><span class="material-symbols-rounded" style="vertical-align: middle; font-size: 1.2rem; margin-right: 0.3rem;">warning</span>Advanced Technical Analysis:</strong> This section provides detailed technical outputs, including extracted features from the Feature Extractor Model and full feature contributions from the Feature-Based Risk Model (SHAP analysis). Intended for advanced users and research purposes.
                    </p>
                </div>
            """, unsafe_allow_html=True)

            # Button to view/hide advanced analysis
            if not st.session_state.get(f'show_advanced_{analysis.analysis_id}', False):
                # Show "View" button
                col_adv1, col_adv2, col_adv3 = st.columns([1, 2, 1])
                with col_adv2:
                    if st.button("View Advanced Analysis", use_container_width=True, type="secondary", key=f"view_advanced_{analysis.analysis_id}"):
                        st.session_state[f'show_advanced_{analysis.analysis_id}'] = True
                        st.rerun()
            else:
                # Show "Hide" button
                col_close1, col_close2, col_close3 = st.columns([1, 2, 1])
                with col_close2:
                    if st.button("Hide Advanced Analysis", use_container_width=True, type="secondary", key=f"hide_advanced_{analysis.analysis_id}"):
                        st.session_state[f'show_advanced_{analysis.analysis_id}'] = False
                        st.rerun()

            # Show advanced analysis if toggled
            if st.session_state.get(f'show_advanced_{analysis.analysis_id}', False):
                st.markdown("---")

                # EXPANDABLE 1: Extracted Features
                if hasattr(analysis, 'extracted_features') and analysis.extracted_features:
                    with st.expander(":material/dynamic_form: Feature Extractor Model – Extracted Features", expanded=False):
                        st.markdown("""
                            <div style="
                                background-color: #fef3c7;
                                border-left: 4px solid #f59e0b;
                                border-radius: 8px;
                                padding: 1rem;
                                margin: 1rem 0;
                            ">
                                <p style="color: #92400e; margin: 0; font-size: 0.9rem;">
                                    <strong><span class="material-symbols-rounded" style="vertical-align: middle; font-size: 1.2rem; margin-right: 0.3rem;">warning</span>Notice:</strong> This modal shows all quantitative features extracted from the uploaded image by the Feature Extractor Model. Intended for advanced users and research purposes.
                                </p>
                            </div>
                        """, unsafe_allow_html=True)

                        st.markdown("#### Extracted Features – Feature Extractor Model")
                        st.markdown("**View all numeric features extracted from this lesion image.**")

                        import pandas as pd

                        # Get feature display names mapping
                        feature_names_map = st.session_state.get('feature_display_names', {})

                        # Create DataFrame
                        extracted_data = []
                        for feature in analysis.extracted_features:
                            feature_name = feature.get('feature_name', 'Unknown')
                            feature_value = feature.get('value', 0.0)

                            # Get display name from mapping
                            display_name = feature_names_map.get(feature_name, feature_name)

                            extracted_data.append({
                                'Feature': display_name,
                                'Technical Name': feature_name,
                                'Value': f"{feature_value:.4f}"
                            })

                        df_extracted = pd.DataFrame(extracted_data)

                        st.dataframe(
                            df_extracted,
                            hide_index=True,
                            use_container_width=True,
                            height=min(500, len(extracted_data) * 35 + 38)
                        )

                # EXPANDABLE 2: SHAP Analysis with Tabs
                if analysis.shap_top_features:
                    with st.expander(":material/arrow_shape_up_stack: Feature-Based Risk Model – Feature Contribution Analysis", expanded=False):
                        st.markdown("""
                            <div style="
                                background-color: #fef3c7;
                                border-left: 4px solid #f59e0b;
                                border-radius: 8px;
                                padding: 1rem;
                                margin: 1rem 0;
                            ">
                                <p style="color: #92400e; margin: 0; font-size: 0.9rem;">
                                    <strong><span class="material-symbols-rounded" style="vertical-align: middle; font-size: 1.2rem; margin-right: 0.3rem;">warning</span>Notice:</strong> This modal shows how each feature contributed to the model's risk estimate, presented in both table and chart formats. Intended for advanced users and research purposes.
                                </p>
                            </div>
                        """, unsafe_allow_html=True)

                        # Create Tabs
                        tab1, tab2 = st.tabs([
                            ":material/table_view: Understanding Feature Contributions",
                            ":material/finance: Chart"
                        ])

                        # Prepare data for both tabs
                        import pandas as pd

                        df_data = []
                        for feature_data in analysis.shap_top_features:
                            display_name = feature_data.get('display_name', feature_data.get('feature', 'Unknown'))
                            feature_value = feature_data.get('value', 0.0)
                            shap_value = feature_data.get('shap_value', 0.0)
                            impact = feature_data.get('impact', 'increases' if shap_value > 0 else 'decreases')

                            df_data.append({
                                'display_name': display_name,
                                'value': feature_value,
                                'shap_value': shap_value,
                                'impact': impact,
                                'abs_shap': abs(shap_value)
                            })

                        # Sort by absolute SHAP value
                        df_data_sorted = sorted(df_data, key=lambda x: x['abs_shap'], reverse=True)

                        # TAB 1: Understanding and Table
                        with tab1:
                            st.markdown("""
                                <div style="
                                    background: linear-gradient(135deg, #e0f2f7 0%, #b3e5f0 100%);
                                    border-left: 4px solid #2d8a9b;
                                    border-radius: 8px;
                                    padding: 1.5rem;
                                    margin: 1rem 0;
                                ">
                                    <h4 style="color: #2d8a9b; margin-top: 0;">Understanding Feature Contributions</h4>
                                    <p style="color: #2d8a9b; margin: 0.5rem 0; font-size: 0.95rem; line-height: 1.6;">
                                        This table shows how each feature contributed to the Feature-Based Risk Model's prediction for this specific lesion. Each row represents one feature with its details:
                                    </p>
                                    <ul style="color: #2d8a9b; margin: 0.5rem 0; font-size: 0.9rem; line-height: 1.7;">
                                        <li><strong>Feature</strong>: The name of the characteristic being analyzed (e.g., patient age, color metrics, texture measurements)</li>
                                        <li><strong>Value</strong>: The actual measured value of this feature for the current lesion</li>
                                        <li><strong>SHAP Value</strong>: How much this feature contributed to the final prediction. Positive values increase risk, negative values decrease risk</li>
                                        <li><strong>Impact</strong>: A simplified label indicating whether the feature pushed the prediction towards <span style="color: #ef4444; font-weight: 600;">"Increases Risk"</span> (red background) or <span style="color: #3b82f6; font-weight: 600;">"Decreases Risk"</span> (blue background)</li>
                                    </ul>
                                    <p style="color: #2d8a9b; margin: 0.5rem 0; font-size: 0.9rem; line-height: 1.6;">
                                        Features are sorted by importance (absolute SHAP value), with the most influential features appearing first.
                                    </p>
                                </div>
                            """, unsafe_allow_html=True)

                            st.markdown("#### Feature Contributions Table")

                            # Create table DataFrame
                            table_data = []
                            for f in df_data_sorted:
                                impact_label = 'Increases Risk' if f['impact'] == 'increases' else 'Decreases Risk'
                                table_data.append({
                                    'Feature': f['display_name'],
                                    'Value': f"{f['value']:.2f}",
                                    'SHAP Value': f"{f['shap_value']:+.4f}",
                                    'Impact': impact_label
                                })

                            df_table = pd.DataFrame(table_data)

                            # Style the dataframe
                            def color_impact(val):
                                if val == 'Increases Risk':
                                    return 'background-color: #fee2e2; color: #991b1b'
                                else:
                                    return 'background-color: #dbeafe; color: #1e40af'

                            styled_df = df_table.style.applymap(color_impact, subset=['Impact'])

                            st.dataframe(
                                styled_df,
                                hide_index=True,
                                use_container_width=True,
                                height=min(500, len(table_data) * 35 + 38)
                            )

                        # TAB 2: Chart with ALL features
                        with tab2:
                            st.markdown("""
                                <div style="
                                    background: linear-gradient(135deg, #e0f2f7 0%, #b3e5f0 100%);
                                    border-left: 4px solid #2d8a9b;
                                    border-radius: 8px;
                                    padding: 1.5rem;
                                    margin: 1rem 0;
                                ">
                                    <h4 style="color: #2d8a9b; margin-top: 0;">Understanding Feature Contributions</h4>
                                    <p style="color: #2d8a9b; margin: 0.5rem 0; font-size: 0.95rem; line-height: 1.6;">
                                        Each bar shows how much a specific feature influenced the risk estimate for this lesion. This provides transparency and helps interpret the Feature-Based Risk Model's output.
                                    </p>
                                    <ul style="color: #2d8a9b; margin: 0.5rem 0; font-size: 0.9rem; line-height: 1.7;">
                                        <li><span style="color: #ef4444; font-weight: 600;">Red bars (positive values)</span>: Features pushing towards <strong>higher malignancy risk</strong></li>
                                        <li><span style="color: #3b82f6; font-weight: 600;">Blue bars (negative values)</span>: Features pushing towards <strong>lower malignancy risk</strong></li>
                                        <li><strong>Bar length</strong>: Represents the magnitude of influence on the prediction</li>
                                        <li><strong>Base Value</strong>: Average prediction across all training samples</li>
                                        <li><strong>Final Prediction</strong>: Base value plus all feature contributions equals the model output</li>
                                    </ul>
                                </div>
                            """, unsafe_allow_html=True)

                            st.markdown("#### SHAP Feature Contributions – All Features")

                            # Display summary metrics if available
                            if hasattr(analysis, 'shap_prediction') and hasattr(analysis, 'shap_base_value'):
                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    st.metric(
                                        "Feature-Based Risk Model",
                                        f"{analysis.shap_prediction:.1%}",
                                        help="Final prediction probability from Feature-Based Risk Model (XGBoost)"
                                    )
                                with col2:
                                    st.metric(
                                        "Base Value",
                                        f"{analysis.shap_base_value:.1%}",
                                        help="The average prediction across all training samples"
                                    )
                                with col3:
                                    impact_sum = sum(abs(f.get('shap_value', 0)) for f in df_data_sorted)
                                    st.metric(
                                        "Total Impact",
                                        f"{impact_sum:.3f}",
                                        help="Sum of absolute SHAP values"
                                    )

                            # ALL features for the chart (not just top 15)
                            all_features = df_data_sorted

                            # Prepare chart data
                            feature_names = [f['display_name'] for f in all_features]
                            shap_values = [f['shap_value'] for f in all_features]
                            feature_values = [f['value'] for f in all_features]
                            colors = ['#ef4444' if f['impact'] == 'increases' else '#3b82f6' for f in all_features]

                            # Create horizontal bar chart
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

                            # Get prediction and base value if available
                            prediction_val = getattr(analysis, 'shap_prediction', analysis.model_c_probability)
                            base_val = getattr(analysis, 'shap_base_value', 0.5)

                            # Calculate dynamic height based on number of features
                            chart_height = max(600, len(all_features) * 25)

                            fig.update_layout(
                                title=dict(
                                    text=f"SHAP Values (Base: {base_val:.3f} → Prediction: {prediction_val:.3f})",
                                    font=dict(size=14)
                                ),
                                xaxis_title="SHAP Value Contribution",
                                yaxis_title="Features",
                                height=chart_height,
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
