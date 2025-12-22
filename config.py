"""
Configuration settings for Skin Lesion AI Frontend

This module contains all configuration constants and settings used across the application.
Centralized configuration makes it easy to modify settings without changing code in multiple places.
"""

# =============================================================================
# API CONFIGURATION
# =============================================================================

# Backend API base URL
API_BASE_URL = "http://localhost:8001"

# API request timeout in seconds
API_TIMEOUT = 30

# API endpoints (relative to base URL)
API_ENDPOINTS = {
    "health": "/health",
    "info": "/",
    "predict": "/api/predict"
}


# =============================================================================
# APPLICATION SETTINGS
# =============================================================================

# Streamlit page configuration
PAGE_CONFIG = {
    "page_title": "Skin Lesion Analyzer",
    "page_icon": "🩺",
    "layout": "wide",
    "initial_sidebar_state": "collapsed"
}

# Supported image file types
SUPPORTED_IMAGE_TYPES = ["png", "jpg", "jpeg", "bmp", "tiff"]

# Maximum file size in MB (optional, for future implementation)
MAX_FILE_SIZE_MB = 10


# =============================================================================
# MEDICAL CONFIGURATION
# =============================================================================

# Valid anatomical locations for lesions
VALID_ANATOMICAL_LOCATIONS = [
    "torso front",
    "torso back",
    "head & neck",
    "left leg",
    "right leg",
    "left arm",
    "right arm"
]

# UI display names mapped to API values
LOCATION_DISPLAY_NAMES = {
    "Head and Neck": "head & neck",
    "Torso Front": "torso front",
    "Torso Back": "torso back",
    "Left Leg": "left leg",
    "Right Leg": "right leg",
    "Left Arm": "left arm",
    "Right Arm": "right arm"
}

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


# =============================================================================
# RISK CATEGORIZATION
# =============================================================================

# Risk category thresholds
RISK_THRESHOLDS = {
    "low": 0.3,      # < 0.3 = LOW
    "medium": 0.7    # 0.3-0.7 = MEDIUM, >= 0.7 = HIGH
}

# Risk category colors (primary_color, background_color, icon)
RISK_COLORS = {
    "low": ("#22c55e", "#f0fdf4", "✅"),
    "medium": ("#f59e0b", "#fffbeb", "⚠️"),
    "high": ("#ef4444", "#fef2f2", "🚨"),
    "unknown": ("#6b7280", "#f3f4f6", "ℹ️")
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
        "name": "Model C - Tabular ML",
        "architecture": "Random Forest Classifier",
        "description": "Uses extracted features for classification"
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
    Skin Lesion Triage Prototype<br>
    <strong>For research purposes only, always consult a medical professional</strong><br>
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
