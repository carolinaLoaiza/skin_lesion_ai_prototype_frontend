# Configuration Guide

This document explains how to configure the Skin Lesion AI Frontend application.

## Configuration File

All application settings are centralized in [`config.py`](config.py). This makes it easy to modify settings without changing code in multiple files.

## Quick Configuration Changes

### Changing the Backend API URL

**Default**: `http://localhost:8001`

To change the backend URL, edit `config.py`:

```python
# Line 12 in config.py
API_BASE_URL = "http://your-new-url:port"
```

**Common scenarios:**
- Local development: `http://localhost:8001`
- Docker: `http://backend:8001`
- Production: `https://api.yourapp.com`

### Changing API Timeout

**Default**: 30 seconds

```python
# Line 15 in config.py
API_TIMEOUT = 60  # Increase to 60 seconds for slower connections
```

### Modifying Risk Thresholds

**Current thresholds:**
- LOW: < 30%
- MEDIUM: 30-70%
- HIGH: ≥ 70%

To change:

```python
# Lines 95-98 in config.py
RISK_THRESHOLDS = {
    "low": 0.4,      # Change to 40%
    "medium": 0.8    # Change to 80%
}
```

### Customizing UI Colors

**Risk category colors:**

```python
# Lines 101-106 in config.py
RISK_COLORS = {
    "low": ("#your_color", "#background", "icon"),
    "medium": ("#your_color", "#background", "icon"),
    "high": ("#your_color", "#background", "icon")
}
```

**Chart colors:**

```python
# Lines 114-118 in config.py
CHART_COLORS = {
    "model_a": "#3b82f6",    # Blue for DenseNet-121
    "model_c": "#22c55e",    # Green for Random Forest
    "ensemble": "#8b5cf6",   # Purple for Ensemble
}
```

### Adjusting Patient Input Constraints

**Age limits:**

```python
# Lines 73-75 in config.py
AGE_MIN = 0
AGE_MAX = 120
AGE_DEFAULT = 30
```

**Lesion diameter limits (mm):**

```python
# Lines 78-81 in config.py
DIAMETER_MIN = 0.0
DIAMETER_MAX = 200.0
DIAMETER_DEFAULT = 5.0
DIAMETER_STEP = 0.5
```

### Changing Anatomical Locations

To add/remove valid locations:

```python
# Lines 49-57 in config.py
VALID_ANATOMICAL_LOCATIONS = [
    "torso front",
    "torso back",
    # ... add more locations
]

# Lines 60-68 in config.py
LOCATION_DISPLAY_NAMES = {
    "Head and Neck": "head & neck",
    # ... add more mappings
}
```

### Modifying Application Text

**Page title and subtitle:**

```python
# Lines 151-152 in config.py
APP_TITLE = "Your Custom Title"
APP_SUBTITLE = "Your Custom Subtitle"
```

**Footer text:**

```python
# Lines 155-162 in config.py
FOOTER_HTML = """
<p>Your custom footer HTML here</p>
"""
```

**Error messages:**

```python
# Lines 165-170 in config.py
ERROR_MESSAGES = {
    "no_image": "Your custom message",
    "api_connection": "Your custom message with {api_url}",
    # ...
}
```

## Configuration Structure

```
config.py
├── API Configuration
│   ├── API_BASE_URL (Backend URL)
│   ├── API_TIMEOUT (Request timeout)
│   └── API_ENDPOINTS (Endpoint paths)
│
├── Application Settings
│   ├── PAGE_CONFIG (Streamlit page settings)
│   ├── SUPPORTED_IMAGE_TYPES (File types)
│   └── MAX_FILE_SIZE_MB (Upload limit)
│
├── Medical Configuration
│   ├── VALID_ANATOMICAL_LOCATIONS (Valid locations)
│   ├── LOCATION_DISPLAY_NAMES (UI to API mapping)
│   ├── AGE_MIN/MAX/DEFAULT (Age constraints)
│   └── DIAMETER_MIN/MAX/DEFAULT/STEP (Diameter constraints)
│
├── Risk Categorization
│   ├── RISK_THRESHOLDS (Risk level cutoffs)
│   └── RISK_COLORS (Color scheme per risk level)
│
├── Visualization Settings
│   ├── CHART_COLORS (Model colors)
│   ├── GAUGE_CONFIG (Gauge chart settings)
│   └── FEATURES_PER_ROW (Feature grid layout)
│
├── Model Information
│   └── MODEL_INFO (Model descriptions)
│
└── UI Text and Messages
    ├── APP_TITLE/SUBTITLE
    ├── FOOTER_HTML
    ├── ERROR_MESSAGES
    └── SUCCESS_MESSAGES
```

## Helper Functions

The config file also provides utility functions:

### `get_api_url(endpoint_key)`

Get full URL for a specific endpoint:

```python
from config import get_api_url

predict_url = get_api_url("predict")  # Returns full URL
base_url = get_api_url()  # Returns base URL only
```

### `get_risk_color(risk_category)`

Get color scheme for a risk level:

```python
from config import get_risk_color

color, bg_color, icon = get_risk_color("low")
```

### `map_location_to_api(display_name)`

Convert UI location to API format:

```python
from config import map_location_to_api

api_location = map_location_to_api("Head and Neck")  # Returns "head & neck"
```

## Best Practices

1. **Always edit `config.py` first** - Don't hardcode values in other files
2. **Restart Streamlit** after config changes for them to take effect
3. **Test after changes** - Especially when modifying validation rules
4. **Keep backups** - Before making major configuration changes
5. **Document custom changes** - Add comments explaining why you changed defaults

## Troubleshooting

### Config changes not taking effect

- **Solution**: Restart the Streamlit server (`Ctrl+C` then `streamlit run main.py`)

### Import errors after config changes

- **Solution**: Check that you haven't removed variables that are imported in other files

### Backend connection fails

- **Solution**: Verify `API_BASE_URL` in config.py matches your backend URL
- Check backend is running: `curl http://localhost:8001/health`

## Environment-Specific Configuration

For different environments (dev/staging/prod), you can:

1. Use environment variables:

```python
import os

API_BASE_URL = os.getenv("API_URL", "http://localhost:8001")
```

2. Create separate config files:

```
config_dev.py
config_staging.py
config_prod.py
```

Then import the appropriate one based on an environment variable.

---

**Note**: After any configuration change, always test the complete workflow to ensure everything works as expected.
