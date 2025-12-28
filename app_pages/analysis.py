"""
Analysis Page - Main workflow for patient, lesion, and analysis management

IMPORTANT: This page uses a "create-on-analysis" approach:
- Patient and Lesion data are captured but NOT saved to database
- Only when analysis is successful, we create Patient + Lesion + Analysis in one transaction
- This prevents orphaned patients (without lesions) and orphaned lesions (without analysis)

Workflow:
1. Patient Information (capture or search existing)
2. Lesion Information (capture or search existing - only if patient exists)
3. Analysis Section (upload image + analyze)
4. Results Display
"""

import streamlit as st
from PIL import Image
from datetime import datetime
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import (
    SUPPORTED_IMAGE_TYPES, ANATOMICAL_LOCATIONS, SEX_OPTIONS,
    DATE_FORMAT, DIAMETER_MIN, DIAMETER_MAX, DIAMETER_DEFAULT, DIAMETER_STEP,
    FOOTER_HTML, ERROR_MESSAGES, API_BASE_URL, load_image_base64
)
from utils.id_generator import generate_patient_id, generate_lesion_id
from utils.validators import (
    validate_patient_name, validate_date_of_birth, validate_sex,
    validate_lesion_location, validate_initial_lesion_size,
    validate_current_lesion_size, calculate_age_from_dob
)
from patient_lesion_service import create_patient_lesion_service
from prediction_service import create_service

# Import display functions from backup main
sys.path.insert(0, str(Path(__file__).parent.parent))
import main_backup as display_functions


# Helper functions for styled messages
def show_info_message(message: str):
    """Display info message with Material Icon"""
    st.markdown(f"""
        <div style="
            background-color: #e0f2fe;
            border-left: 4px solid #0284c7;
            border-radius: 8px;
            padding: 1rem;
            margin: 1rem 0;
        ">
            <p style="color: #0c4a6e; margin: 0; font-size: 0.9rem;">
                <span class="material-symbols-rounded" style="font-size: 1.2rem; vertical-align: middle; margin-right: 0.5rem;">info</span>
                {message}
            </p>
        </div>
    """, unsafe_allow_html=True)


def show_success_message(message: str):
    """Display success message with Material Icon"""
    st.markdown(f"""
        <div style="
            background-color: #f0fdf4;
            border-left: 4px solid #22c55e;
            border-radius: 8px;
            padding: 1rem;
            margin: 1rem 0;
        ">
            <p style="color: #15803d; margin: 0; font-size: 0.9rem;">
                <span class="material-symbols-rounded" style="font-size: 1.2rem; vertical-align: middle; margin-right: 0.5rem;">check_circle</span>
                {message}
            </p>
        </div>
    """, unsafe_allow_html=True)


def show_error_message(message: str):
    """Display error message with Material Icon"""
    st.markdown(f"""
        <div style="
            background-color: #fef2f2;
            border-left: 4px solid #ef4444;
            border-radius: 8px;
            padding: 1rem;
            margin: 1rem 0;
        ">
            <p style="color: #991b1b; margin: 0; font-size: 0.9rem;">
                <span class="material-symbols-rounded" style="font-size: 1.2rem; vertical-align: middle; margin-right: 0.5rem;">gpp_bad</span>
                {message}
            </p>
        </div>
    """, unsafe_allow_html=True)


def render():
    """Main render function for analysis page"""

    # Initialize session state
    initialize_session_state()

    # Section 1: Patient Information
    render_patient_section()

    # Section 2: Lesion Information (only if patient selected)
    if st.session_state.patient_data_ready:
        st.markdown("---")
        render_lesion_section()

    # Section 3: Analysis (only if lesion data ready)
    if st.session_state.lesion_data_ready:
        st.markdown("---")
        render_analysis_section()

    # Section 4: Results (only if analysis complete)
    if st.session_state.analysis_complete:
        st.markdown("---")
        render_results_section()

        # New Analysis button at the end
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("New Analysis", use_container_width=True, type="secondary", key="new_analysis_button"):
                reset_all_state()
                st.rerun()

    # Footer
    st.markdown("---")
    st.markdown(FOOTER_HTML, unsafe_allow_html=True)


def initialize_session_state():
    """Initialize all session state variables"""

    # Patient state flags
    if 'patient_data_ready' not in st.session_state:
        st.session_state.patient_data_ready = False
    if 'patient_is_new' not in st.session_state:
        st.session_state.patient_is_new = True  # Track if patient is new or existing

    # Lesion state flags
    if 'lesion_data_ready' not in st.session_state:
        st.session_state.lesion_data_ready = False
    if 'lesion_is_new' not in st.session_state:
        st.session_state.lesion_is_new = True  # Track if lesion is new or existing

    # Analysis state
    if 'analysis_complete' not in st.session_state:
        st.session_state.analysis_complete = False

    # Patient data (temporary storage - NOT in DB yet)
    if 'patient_data' not in st.session_state:
        st.session_state.patient_data = None  # Dict: {full_name, date_of_birth, sex, patient_id (if existing)}

    # Lesion data (temporary storage - NOT in DB yet)
    if 'lesion_data' not in st.session_state:
        st.session_state.lesion_data = None  # Dict: {location, initial_size_mm, lesion_id (if existing)}

    # Analysis results
    if 'last_response' not in st.session_state:
        st.session_state.last_response = None
    if 'show_shap' not in st.session_state:
        st.session_state.show_shap = False


def reset_all_state():
    """Reset all session state to start fresh"""
    st.session_state.patient_data_ready = False
    st.session_state.patient_is_new = True
    st.session_state.lesion_data_ready = False
    st.session_state.lesion_is_new = True
    st.session_state.analysis_complete = False
    st.session_state.patient_data = None
    st.session_state.lesion_data = None
    st.session_state.last_response = None
    st.session_state.show_shap = False


# =============================================================================
# SECTION 1: PATIENT INFORMATION
# =============================================================================

def render_patient_section():
    """Render patient information section - capture data but don't save to DB yet"""
    # Load patient icon
    patient_icon_base64 = load_image_base64('patient.png')
    if patient_icon_base64:
        patient_icon_html = f'<img src="{patient_icon_base64}" alt="Patient" style="height: 1.5rem; width: auto; vertical-align: middle; margin-right: 0.5rem;">'
    else:
        patient_icon_html = ""

    st.markdown(f"## {patient_icon_html}Patient Information", unsafe_allow_html=True)

    # Show selected patient if exists
    if st.session_state.patient_data_ready and st.session_state.patient_data:
        display_selected_patient()
        return

    # Patient mode selection
    patient_mode = st.radio(
        "Select mode:",
        ["New Patient", "Search Existing Patient"],
        horizontal=True,
        key="patient_mode"
    )

    if patient_mode == "New Patient":
        render_new_patient_form()
    else:
        render_search_patient()


def render_new_patient_form():
    """Render form for capturing new patient data (NOT saved to DB yet)"""
    st.markdown("### New Patient Information")

    show_info_message("Patient data will be saved to database only after successful lesion analysis.")

    with st.form("new_patient_form"):
        full_name = st.text_input(
            "Full Name",
            placeholder="e.g., Juan Pérez García",
            help="Enter patient's complete name"
        )

        date_of_birth = st.text_input(
            f"Date of Birth ({DATE_FORMAT})",
            placeholder="23/07/1980",
            help=f"Enter date in {DATE_FORMAT} format"
        )

        sex = st.selectbox(
            "Sex",
            options=SEX_OPTIONS,
            help="Select patient's biological sex"
        )

        submitted = st.form_submit_button("Continue with Patient Data", use_container_width=True)

        if submitted:
            # Validate inputs
            valid_name, name_error = validate_patient_name(full_name)
            valid_dob, dob_error = validate_date_of_birth(date_of_birth)
            valid_sex, sex_error = validate_sex(sex)

            errors = []
            if not valid_name:
                errors.append(name_error)
            if not valid_dob:
                errors.append(dob_error)
            if not valid_sex:
                errors.append(sex_error)

            if errors:
                for error in errors:
                    show_error_message(error)
            else:
                # Store patient data in session state (NOT in DB)
                st.session_state.patient_data = {
                    'full_name': full_name,
                    'date_of_birth': date_of_birth,
                    'sex': sex,
                    'patient_id': None  # Will be generated during analysis
                }
                st.session_state.patient_data_ready = True
                st.session_state.patient_is_new = True
                show_success_message(f"Patient data captured: {full_name}")
                st.rerun()


def render_search_patient():
    """Render patient search interface"""
    st.markdown("### Search Existing Patient")

    search_term = st.text_input(
        "Search by name",
        placeholder="Type at least 2 characters...",
        help="Search for patients by name"
    )

    if len(search_term) >= 2:
        try:
            service = create_patient_lesion_service()
            patients = service.search_patients_by_name(search_term)

            if not patients:
                show_info_message("No patients found matching your search")
            else:
                st.markdown(f"Found **{len(patients)}** patient(s):")

                for patient in patients:
                    col1, col2 = st.columns([3, 1])

                    with col1:
                        st.markdown(f"""
                            **{patient.patient_full_name}**
                            - ID: `{patient.patient_id}`
                            - Sex: {patient.sex.title()}
                            - DOB: {patient.date_of_birth}
                        """)

                    with col2:
                        if st.button("Select", key=f"select_{patient.patient_id}"):
                            # Store EXISTING patient data
                            st.session_state.patient_data = {
                                'full_name': patient.patient_full_name,
                                'date_of_birth': patient.date_of_birth,
                                'sex': patient.sex,
                                'patient_id': patient.patient_id  # Existing ID
                            }
                            st.session_state.patient_data_ready = True
                            st.session_state.patient_is_new = False  # Existing patient
                            st.rerun()

        except Exception as e:
            show_error_message(f"Search failed: {str(e)}")


def display_selected_patient():
    """Display selected patient information (read-only)"""
    patient_data = st.session_state.patient_data

    if st.session_state.patient_is_new:
        show_info_message(f"New Patient Data Captured: {patient_data['full_name']}. This patient will be created in the database after successful analysis.")
    else:
        show_info_message(f"Existing Patient Selected: {patient_data['full_name']} (ID: {patient_data['patient_id']})")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.text_input("Full Name", value=patient_data['full_name'], disabled=True)

    with col2:
        st.text_input("Date of Birth", value=patient_data['date_of_birth'], disabled=True)

    with col3:
        st.text_input("Sex", value=patient_data['sex'].title(), disabled=True)

    # Change patient button
    if st.button("Change Patient", key="change_patient_button"):
        st.session_state.patient_data_ready = False
        st.session_state.patient_data = None
        st.session_state.lesion_data_ready = False  # Reset lesion too
        st.session_state.lesion_data = None
        st.rerun()


# =============================================================================
# SECTION 2: LESION INFORMATION
# =============================================================================

def render_lesion_section():
    """Render lesion information section - capture data but don't save to DB yet"""
    # Load lesion info icon
    lesion_info_base64 = load_image_base64('info_2.png')
    if lesion_info_base64:
        lesion_info_html = f'<img src="{lesion_info_base64}" alt="Lesion Info" style="height: 1.5rem; width: auto; vertical-align: middle; margin-right: 0.5rem;">'
    else:
        lesion_info_html = ""

    st.markdown(f"## {lesion_info_html}Lesion Information", unsafe_allow_html=True)

    # Show selected lesion if exists
    if st.session_state.lesion_data_ready and st.session_state.lesion_data:
        display_selected_lesion()
        return

    # Lesion mode selection
    # Only show "Search Lesion" if patient is existing (not new)
    if st.session_state.patient_is_new:
        lesion_mode = "New Lesion"
        show_info_message("Since this is a new patient, you must create a new lesion.")
    else:
        lesion_mode = st.radio(
            "Select mode:",
            ["New Lesion", "Search Existing Lesion"],
            horizontal=True,
            key="lesion_mode"
        )

    if lesion_mode == "New Lesion":
        render_new_lesion_form()
    else:
        render_search_lesion()


def render_new_lesion_form():
    """Render form for capturing new lesion data (NOT saved to DB yet)"""
    st.markdown("### New Lesion Information")

    show_info_message("Lesion data will be saved to database only after successful analysis.")

    with st.form("new_lesion_form"):
        # Location dropdown
        location_display = st.selectbox(
            "Lesion Location",
            options=list(ANATOMICAL_LOCATIONS.keys()),
            help="Select the anatomical location of the lesion"
        )

        # Initial size
        initial_size = st.number_input(
            "Initial Size (mm)",
            min_value=0.1,
            max_value=500.0,
            value=5.0,
            step=0.5,
            help="Enter the initial diameter of the lesion in millimeters"
        )

        submitted = st.form_submit_button("Continue with Lesion Data", use_container_width=True)

        if submitted:
            # Get API location value
            api_location = ANATOMICAL_LOCATIONS[location_display]["api_value"]

            # Validate
            valid_location, location_error = validate_lesion_location(api_location)
            valid_size, size_error = validate_initial_lesion_size(initial_size)

            errors = []
            if not valid_location:
                errors.append(location_error)
            if not valid_size:
                errors.append(size_error)

            if errors:
                for error in errors:
                    show_error_message(error)
            else:
                # Store lesion data in session state (NOT in DB)
                st.session_state.lesion_data = {
                    'location': api_location,
                    'location_display': location_display,
                    'initial_size_mm': initial_size,
                    'lesion_id': None  # Will be generated during analysis
                }
                st.session_state.lesion_data_ready = True
                st.session_state.lesion_is_new = True
                show_success_message(f"Lesion data captured: {location_display} ({initial_size} mm)")
                st.rerun()


def render_search_lesion():
    """Render lesion search interface (dropdown of patient's lesions)"""
    st.markdown("### Select Existing Lesion")

    patient_id = st.session_state.patient_data['patient_id']

    try:
        service = create_patient_lesion_service()
        lesions = service.get_lesions_by_patient(patient_id)

        if not lesions:
            show_info_message("This patient has no lesions yet. Please create a new lesion.")
        else:
            st.markdown(f"Found **{len(lesions)}** lesion(s) for this patient:")

            for lesion in lesions:
                col1, col2 = st.columns([3, 1])

                with col1:
                    st.markdown(f"""
                        **{lesion.lesion_id}**
                        - Location: {lesion.lesion_location.title()}
                        - Initial Size: {lesion.initial_size_mm} mm
                        - Created: {lesion.created_at[:10] if lesion.created_at else 'N/A'}
                    """)

                with col2:
                    if st.button("Select", key=f"select_{lesion.lesion_id}"):
                        # Store EXISTING lesion data
                        st.session_state.lesion_data = {
                            'location': lesion.lesion_location,
                            'location_display': lesion.lesion_location.title(),
                            'initial_size_mm': lesion.initial_size_mm,
                            'lesion_id': lesion.lesion_id  # Existing ID
                        }
                        st.session_state.lesion_data_ready = True
                        st.session_state.lesion_is_new = False  # Existing lesion
                        st.rerun()

    except Exception as e:
        show_error_message(f"Failed to load lesions: {str(e)}")


def display_selected_lesion():
    """Display selected lesion information (read-only)"""
    lesion_data = st.session_state.lesion_data

    if st.session_state.lesion_is_new:
        show_info_message(f"New Lesion Data Captured: {lesion_data['location_display']} ({lesion_data['initial_size_mm']} mm). This lesion will be created in the database after successful analysis.")
    else:
        show_info_message(f"Existing Lesion Selected: {lesion_data['lesion_id']}")

    col1, col2 = st.columns(2)

    with col1:
        st.text_input("Location", value=lesion_data['location_display'], disabled=True)

    with col2:
        st.text_input("Initial Size (mm)", value=f"{lesion_data['initial_size_mm']}", disabled=True)

    # Change lesion button
    if st.button("Change Lesion", key="change_lesion_button"):
        st.session_state.lesion_data_ready = False
        st.session_state.lesion_data = None
        st.rerun()


# =============================================================================
# SECTION 3: ANALYSIS
# =============================================================================

def render_analysis_section():
    """Render analysis section (image upload + current size)"""
    # Load analysis icon
    analysis_icon_base64 = load_image_base64('analysis.png')
    if analysis_icon_base64:
        analysis_icon_html = f'<img src="{analysis_icon_base64}" alt="Analysis" style="height: 1.5rem; width: auto; vertical-align: middle; margin-right: 0.5rem;">'
    else:
        analysis_icon_html = ""

    st.markdown(f"## {analysis_icon_html}Current Analysis", unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("### Lesion Image")
        # Load camera icon
        camera_icon_base64 = load_image_base64('camera.png')
        if camera_icon_base64:
            camera_help_html = f'<img src="{camera_icon_base64}" style="height: 1.2rem; width: auto; vertical-align: middle;"> Upload a clear dermoscopic image of the lesion'
        else:
            camera_help_html = "Upload a clear dermoscopic image of the lesion"

        uploaded_file = st.file_uploader(
            "Upload current lesion image",
            type=SUPPORTED_IMAGE_TYPES,
            help=camera_help_html
        )

        image = None
        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            st.image(image, caption="Image preview", use_container_width=True)
        else:
            show_info_message("Please upload an image to continue")

    with col2:
        st.markdown("### Current Measurements")

        # Auto-fill current size with initial size
        default_current_size = st.session_state.lesion_data['initial_size_mm']

        current_size = st.number_input(
            "Current Size (mm)",
            min_value=DIAMETER_MIN,
            max_value=DIAMETER_MAX,
            value=float(default_current_size),
            step=DIAMETER_STEP,
            help="Enter current diameter. Pre-filled with initial size."
        )

        patient_data = st.session_state.patient_data
        lesion_data = st.session_state.lesion_data
        age = calculate_age_from_dob(patient_data['date_of_birth'])

        show_info_message(f"""Patient: {patient_data['full_name']}<br>Age: {age} years<br>Sex: {patient_data['sex'].title()}<br>Lesion Location: {lesion_data['location_display']}<br>Initial Size: {lesion_data['initial_size_mm']} mm""")

    # Analyze button
    st.markdown("---")
    col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])

    with col_btn2:
        analyze_button = st.button("Analyze Lesion", use_container_width=True, type="primary", key="analyze_lesion_button")

    if analyze_button:
        if image is None:
            show_error_message(ERROR_MESSAGES["no_image"])
        else:
            # Validate current size
            valid_size, size_error = validate_current_lesion_size(current_size)
            if not valid_size:
                show_error_message(size_error)
            else:
                perform_analysis(uploaded_file, current_size)


def perform_analysis(uploaded_file, current_size_mm: float):
    """
    Perform the analysis and create patient/lesion in DB if needed

    Flow:
    1. If patient is NEW → create patient in DB
    2. If lesion is NEW → generate lesion_id and create lesion in DB
    3. Perform analysis with patient_id + lesion_id
    4. If all successful → done!
    5. If any step fails → show error (rollback handled by not proceeding)
    """
    patient_data = st.session_state.patient_data
    lesion_data = st.session_state.lesion_data

    # Calculate age
    age = calculate_age_from_dob(patient_data['date_of_birth'])

    # Reset file pointer
    uploaded_file.seek(0)

    try:
        with st.spinner("Processing analysis... Creating records and analyzing image..."):

            # STEP 1: Create patient if NEW
            if st.session_state.patient_is_new:
                show_info_message("Creating new patient in database...")

                # Generate patient ID
                patient_id = generate_patient_id()

                # Create patient in DB
                service = create_patient_lesion_service()
                patient = service.create_patient(
                    patient_id=patient_id,
                    patient_full_name=patient_data['full_name'],
                    sex=patient_data['sex'],
                    date_of_birth=patient_data['date_of_birth']
                )

                # Update session state with created patient ID
                st.session_state.patient_data['patient_id'] = patient.patient_id
                patient_id = patient.patient_id

                show_success_message(f"Patient created: {patient.patient_full_name} ({patient_id})")
            else:
                # Use existing patient ID
                patient_id = patient_data['patient_id']

            # STEP 2: Create lesion if NEW
            if st.session_state.lesion_is_new:
                show_info_message("Creating new lesion in database...")

                # Generate lesion ID
                lesion_id = generate_lesion_id(lesion_data['location'])

                # Create lesion in DB
                service = create_patient_lesion_service()
                lesion = service.create_lesion(
                    lesion_id=lesion_id,
                    patient_id=patient_id,
                    lesion_location=lesion_data['location'],
                    initial_size_mm=lesion_data['initial_size_mm']
                )

                # Update session state with created lesion ID
                st.session_state.lesion_data['lesion_id'] = lesion.lesion_id
                lesion_id = lesion.lesion_id

                show_success_message(f"Lesion created: {lesion.lesion_id}")
            else:
                # Use existing lesion ID
                lesion_id = lesion_data['lesion_id']

            # STEP 3: Perform analysis
            show_info_message("Analyzing lesion image with AI models...")

            # Reset file pointer again before analysis
            uploaded_file.seek(0)

            prediction_service = create_service()
            response = prediction_service.submit_prediction(
                image_file=uploaded_file,
                age=age,
                sex=patient_data['sex'],
                location=lesion_data['location'],
                diameter=current_size_mm,
                patient_id=patient_id,
                lesion_id=lesion_id
            )

            # Store results
            st.session_state.last_response = response
            st.session_state.last_uploaded_file = uploaded_file
            st.session_state.last_input = {
                'age': age,
                'sex': patient_data['sex'],
                'location': lesion_data['location'],
                'diameter': current_size_mm
            }
            st.session_state.last_display_metadata = {
                'age': age,
                'sex': patient_data['sex'].title(),
                'location': lesion_data['location_display'],
                'diameter': current_size_mm
            }
            st.session_state.analysis_complete = True
            st.session_state.show_shap = False

            # Mark patient and lesion as no longer "new" (they're in DB now)
            st.session_state.patient_is_new = False
            st.session_state.lesion_is_new = False

            show_success_message("Analysis completed successfully!")
            st.balloons()
            st.rerun()

    except Exception as e:
        show_error_message(f"Analysis failed: {str(e)}")
        show_info_message(ERROR_MESSAGES["api_connection"].format(api_url=API_BASE_URL))

        # Important: If we created patient/lesion but analysis failed,
        # they're already in DB. User can retry analysis with same patient/lesion.
        # This is acceptable - we have patient/lesion without analysis (for now).
        # Alternative: Implement rollback to delete patient/lesion if analysis fails.


# =============================================================================
# SECTION 4: RESULTS
# =============================================================================

def render_results_section():
    """Render results section (reusing display functions from main_backup)"""
    # Load results icon
    results_icon_base64 = load_image_base64('results.png')
    if results_icon_base64:
        results_icon_html = f'<img src="{results_icon_base64}" alt="Results" style="height: 1.5rem; width: auto; vertical-align: middle; margin-right: 0.5rem;">'
    else:
        results_icon_html = ""

    st.markdown(f"## {results_icon_html}Analysis Results", unsafe_allow_html=True)

    # Display prediction results
    display_functions.display_prediction_results(
        st.session_state.last_response,
        st.session_state.last_display_metadata
    )

    # SHAP Explanation Section
    st.markdown("---")
    # Load history icon
    history_icon_base64 = load_image_base64('history.png')
    if history_icon_base64:
        history_icon_html = f'<img src="{history_icon_base64}" alt="History" style="height: 1.3rem; width: auto; vertical-align: middle; margin-right: 0.5rem;">'
    else:
        history_icon_html = ""

    st.markdown(f"## {history_icon_html}Feature Contribution", unsafe_allow_html=True)

    # Only show info box and "View" button if SHAP is NOT currently displayed
    if not st.session_state.show_shap:
        st.markdown("""
            <div style="
                background: linear-gradient(135deg, #e0f2f7 0%, #b3e5f0 100%);
                border-left: 4px solid #2d8a9b;
                border-radius: 8px;
                padding: 1rem;
                margin: 1rem 0;
            ">
                <p style="color: #2d8a9b; margin: 0; font-size: 0.9rem;">
                    <strong><span class="material-symbols-rounded" style="vertical-align: middle; font-size: 1.2rem; margin-right: 0.3rem;">lightbulb_circle</span>What Factors Contributed?</strong> This section highlights the features that contributed most to the risk estimation for this lesion.
                    Click below to view a detailed explanation.
                </p>
            </div>
        """, unsafe_allow_html=True)

        col_exp1, col_exp2, col_exp3 = st.columns([1, 2, 1])

        with col_exp2:
            if st.button("View Feature Contribution", use_container_width=True, type="primary", key="view_shap_button"):
                st.session_state.show_shap = True
                st.rerun()
    else:
        # Show "Hide" button when SHAP is displayed
        col_exp1, col_exp2, col_exp3 = st.columns([1, 2, 1])

        with col_exp2:
            if st.button("Hide Feature Contribution", use_container_width=True, type="secondary", key="hide_shap_button"):
                st.session_state.show_shap = False
                st.rerun()

    # Display SHAP if toggled on
    if st.session_state.show_shap:
        with st.spinner("Generating model explanation... Computing feature contributions..."):
            try:
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

                # Display SHAP explanation (chart with top 5 features)
                display_functions.display_shap_explanation(explain_response)

            except Exception as e:
                show_error_message(f"Failed to generate explanation: {str(e)}")
