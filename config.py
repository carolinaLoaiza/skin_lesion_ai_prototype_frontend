"""
Configuration settings for Skin Lesion AI Frontend

This module contains all configuration constants and settings used across the application.
Centralized configuration makes it easy to modify settings without changing code in multiple places.
"""

# =============================================================================
# API CONFIGURATION
# =============================================================================

# Backend API base URL
API_BASE_URL = "http://localhost:8000"

# API request timeout in seconds
API_TIMEOUT = 30

# API endpoints (relative to base URL)
API_ENDPOINTS = {
    "health": "/health",
    "info": "/",
    "predict": "/api/predict",
    "explain": "/api/explain",
    "patients": "/api/patients",
    "patients_search": "/api/patients/search/by-name",
    "patient_by_id": "/api/patients/{patient_id}",
    "lesions": "/api/lesions",
    "lesion_by_id": "/api/lesions/{lesion_id}",
    "patient_lesions": "/api/patients/{patient_id}/lesions",
    "lesion_analyses": "/api/lesions/{lesion_id}/analyses",
    "analysis_by_id": "/api/analyses/{analysis_id}",
    "analysis_image": "/api/analyses/{analysis_id}/image",
    "feature_names": "/api/feature-names"
}


# =============================================================================
# APPLICATION SETTINGS
# =============================================================================

# Streamlit page configuration
PAGE_CONFIG = {
    "page_title": "Skin Lesion Analyzer",
    "page_icon": "🩺",
    "layout": "wide",
    "initial_sidebar_state": "expanded"
}

# Supported image file types
SUPPORTED_IMAGE_TYPES = ["png", "jpg", "jpeg", "bmp", "tiff"]

# Maximum file size in MB (optional, for future implementation)
MAX_FILE_SIZE_MB = 10


# =============================================================================
# MEDICAL CONFIGURATION
# =============================================================================

# =============================================================================
# ANATOMICAL LOCATIONS CONFIGURATION (Centralized)
# =============================================================================

# Master configuration for anatomical locations
# Format: {display_name: (api_value, location_code)}
ANATOMICAL_LOCATIONS = {
    "Head and Neck": {"api_value": "head & neck", "code": "HN"},
    "Torso Front": {"api_value": "torso front", "code": "FT"},
    "Torso Back": {"api_value": "torso back", "code": "BT"},
    "Left Leg": {"api_value": "left leg", "code": "LL"},
    "Right Leg": {"api_value": "right leg", "code": "RL"},
    "Left Arm": {"api_value": "left arm", "code": "LA"},
    "Right Arm": {"api_value": "right arm", "code": "RA"}
}

# Valid anatomical locations for API validation
VALID_ANATOMICAL_LOCATIONS = [loc["api_value"] for loc in ANATOMICAL_LOCATIONS.values()]

# UI display names mapped to API values (for backward compatibility)
LOCATION_DISPLAY_NAMES = {
    display: data["api_value"] for display, data in ANATOMICAL_LOCATIONS.items()
}

# Helper functions for location handling
def get_location_code(api_location: str) -> str:
    """Get location code from API location value"""
    for data in ANATOMICAL_LOCATIONS.values():
        if data["api_value"] == api_location:
            return data["code"]
    raise ValueError(f"Unknown location: {api_location}")

def get_api_location_from_display(display_name: str) -> str:
    """Get API location value from display name"""
    if display_name in ANATOMICAL_LOCATIONS:
        return ANATOMICAL_LOCATIONS[display_name]["api_value"]
    raise ValueError(f"Unknown display name: {display_name}")

# Patient age constraints
AGE_MIN = 0
AGE_MAX = 120
AGE_DEFAULT = 30

# Lesion diameter constraints (in millimeters)
DIAMETER_MIN = 0.0
DIAMETER_MAX = 200.0
DIAMETER_DEFAULT = 5.0
DIAMETER_STEP = 0.5

# Sex options
SEX_OPTIONS = ["Male", "Female"]

# Date format for patient date of birth
DATE_FORMAT = "DD/MM/YYYY"
DATE_FORMAT_PYTHON = "%d/%m/%Y"  # For datetime.strptime()


# =============================================================================
# RISK CATEGORIZATION
# =============================================================================

# Risk category thresholds
RISK_THRESHOLDS = {
    "low": 0.3,      # < 0.3 = LOW
    "medium": 0.7    # 0.3-0.7 = MEDIUM, >= 0.7 = HIGH
}

# Risk category colors (primary_color, background_color, icon - Material Symbols)
RISK_COLORS = {
    "low": ("#22c55e", "#f0fdf4", '<span class="material-symbols-rounded" style="vertical-align: middle;">verified_user</span>'),
    "medium": ("#f59e0b", "#fffbeb", '<span class="material-symbols-rounded" style="vertical-align: middle;">gpp_maybe</span>'),
    "high": ("#ef4444", "#fef2f2", '<span class="material-symbols-rounded" style="vertical-align: middle;">gpp_bad</span>'),
    "unknown": ("#6b7280", "#f3f4f6", '<span class="material-symbols-rounded" style="vertical-align: middle;">info</span>')
}


# =============================================================================
# VISUALIZATION SETTINGS
# =============================================================================

# Chart color scheme
CHART_COLORS = {
    "model_a": "#3b82f6",      # Blue for DenseNet-121
    "model_c": "#22c55e",      # Green for Random Forest
    "ensemble": "#8b5cf6",     # Purple for Final Ensemble
}

# Gauge chart settings
GAUGE_CONFIG = {
    "height": 300,
    "range": [0, 100],
    "low_range": [0, 30],
    "medium_range": [30, 70],
    "high_range": [70, 100],
    "threshold_value": 70
}

# Feature display settings
FEATURES_PER_ROW = 6


# =============================================================================
# MODEL INFORMATION
# =============================================================================

MODEL_INFO = {
    "model_a": {
        "name": "Model A - Deep Learning",
        "architecture": "DenseNet-121 CNN",
        "description": "Convolutional Neural Network for image classification"
    },
    "model_b": {
        "name": "Model B - Feature Extractor",
        "architecture": "ResNet-50",
        "description": "Extracts 18 visual features from lesion images"
    },
    "model_c": {
        "name": "Model C - Gradient Boosting",
        "architecture": "XGBoost Classifier",
        "description": "Uses extracted features and metadata for classification"
    }
}


# =============================================================================
# UI TEXT AND MESSAGES
# =============================================================================

# Application title and description
APP_TITLE = "Skin Lesion Triage Tool"
APP_SUBTITLE = "Prototype for Dermatological Image Assessment"

# Footer text
FOOTER_HTML = """
<p style='text-align: center; color: #6b7280; font-size: 0.9rem;'>
    Skin Lesion Triage Prototype | Version 1.0.0<br>
    <strong>© 2025 - For research purposes only, always consult a medical professional</strong><br>
    Developed as part of Dissertation project of MSc Artificial Intelligence Technology, Northumbria University London<br>
    This prototype was fueled by lots of coffee, persistence, late night coding, and a little AI magic!
</p>
"""

# Error messages
ERROR_MESSAGES = {
    "no_image": "⚠️ Please upload an image before continuing with the analysis.",
    "api_connection": "💡 Make sure the backend API is running at {api_url}",
    "invalid_file_type": "Invalid file type. Please upload an image file (PNG, JPG, JPEG, BMP, TIFF).",
    "prediction_failed": "❌ Error during analysis: {error}"
}

# Success messages
SUCCESS_MESSAGES = {
    "analysis_complete": "✅ Analysis completed successfully"
}


# =============================================================================
# DEVELOPMENT/DEBUG SETTINGS
# =============================================================================

# Enable debug mode (prints to console)
DEBUG_MODE = True

# Enable verbose logging
VERBOSE_LOGGING = False


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_api_url(endpoint_key: str = None) -> str:
    """
    Get the full API URL for a specific endpoint

    Args:
        endpoint_key: Key from API_ENDPOINTS dict (e.g., "predict", "health")
                     If None, returns base URL

    Returns:
        Full API URL string
    """
    if endpoint_key is None:
        return API_BASE_URL

    endpoint = API_ENDPOINTS.get(endpoint_key, "")
    return f"{API_BASE_URL}{endpoint}"


def get_risk_color(risk_category: str) -> tuple:
    """
    Get color scheme for a risk category

    Args:
        risk_category: Risk category string ("low", "medium", "high")

    Returns:
        Tuple of (primary_color, background_color, icon)
    """
    return RISK_COLORS.get(risk_category.lower(), RISK_COLORS["unknown"])


def map_location_to_api(display_name: str) -> str:
    """
    Map UI display location name to API format

    Args:
        display_name: Location name as displayed in UI

    Returns:
        Location name in API format
    """
    return LOCATION_DISPLAY_NAMES.get(display_name, display_name.lower())


def load_image_base64(filename: str) -> str:
    """
    Load image from assets/images and return as base64 data URL

    Args:
        filename: Image filename (e.g., 'lupa.png', 'logo.png')

    Returns:
        Base64 data URL string (e.g., 'data:image/png;base64,iVBORw0KG...')
        Returns empty string if file not found
    """
    import base64
    from pathlib import Path

    # Get path to assets/images directory
    config_dir = Path(__file__).parent
    image_path = config_dir / "assets" / "images" / filename

    if image_path.exists():
        with open(image_path, "rb") as f:
            image_data = base64.b64encode(f.read()).decode()
            # Detect file extension for proper MIME type
            extension = image_path.suffix.lower()
            mime_type = "image/png" if extension == ".png" else f"image/{extension[1:]}"
            return f'data:{mime_type};base64,{image_data}'

    return ""
