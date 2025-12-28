"""
ID Generation Utilities

Generates unique IDs for patients and lesions using timestamp-based approach.
Uses centralized configuration from config.py for location codes.
"""

from datetime import datetime
from typing import Optional
import sys
from pathlib import Path

# Add parent directory to path to import config
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import get_location_code


def generate_patient_id() -> str:
    """
    Generate a unique patient ID using timestamp

    Format: PAT-YYYYMMDDHHMMSS
    Example: PAT-20250126143025

    Returns:
        Unique patient ID string
    """
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"PAT-{timestamp}"


def generate_lesion_id(api_location: str, counter: Optional[int] = None) -> str:
    """
    Generate a unique lesion ID using location code and counter

    Format: LESION_XX_NNN
    Where:
        XX = Location code (LL, RL, LA, RA, FT, BT, HN)
        NNN = Counter (001-999) or timestamp-based if not provided

    Examples:
        LESION_LL_001  (Left Leg, first lesion)
        LESION_HN_002  (Head & Neck, second lesion)

    Args:
        api_location: Anatomical location in API format (e.g., "left leg", "head & neck")
        counter: Optional counter number (1-999). If None, uses timestamp.

    Returns:
        Unique lesion ID string

    Raises:
        ValueError: If location is not recognized
    """
    # Get location code from centralized config
    location_code = get_location_code(api_location)

    # Generate counter part
    if counter is not None:
        if not (1 <= counter <= 999):
            raise ValueError(f"Counter must be between 1 and 999, got {counter}")
        counter_str = f"{counter:03d}"
    else:
        # Use last 3 digits of timestamp as counter
        timestamp = datetime.now().strftime("%H%M%S")
        counter_str = timestamp[-3:]

    return f"LESION_{location_code}_{counter_str}"
