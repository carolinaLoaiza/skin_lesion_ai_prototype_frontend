"""
Validation Utilities

Provides validation functions for patient and lesion data.
"""

from datetime import datetime
from typing import Tuple
import sys
from pathlib import Path

# Add parent directory to path to import config
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import (
    DATE_FORMAT_PYTHON,
    AGE_MIN,
    AGE_MAX,
    DIAMETER_MIN,
    DIAMETER_MAX,
    SEX_OPTIONS,
    VALID_ANATOMICAL_LOCATIONS
)


def validate_date_of_birth(date_string: str) -> Tuple[bool, str]:
    """
    Validate date of birth format and value

    Args:
        date_string: Date string in DD/MM/YYYY format

    Returns:
        Tuple of (is_valid, error_message)
        If valid: (True, "")
        If invalid: (False, "error description")
    """
    if not date_string or not date_string.strip():
        return False, "Date of birth is required"

    try:
        # Try to parse the date
        birth_date = datetime.strptime(date_string, DATE_FORMAT_PYTHON)

        # Check if date is in the future
        if birth_date > datetime.now():
            return False, "Date of birth cannot be in the future"

        # Check if person would be too old
        age_years = (datetime.now() - birth_date).days / 365.25
        if age_years > AGE_MAX:
            return False, f"Age cannot exceed {AGE_MAX} years"

        return True, ""

    except ValueError:
        return False, f"Invalid date format. Please use DD/MM/YYYY (e.g., 23/07/1980)"


def validate_patient_name(name: str) -> Tuple[bool, str]:
    """
    Validate patient full name

    Args:
        name: Patient full name

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not name or not name.strip():
        return False, "Patient name is required"

    if len(name.strip()) < 3:
        return False, "Name must be at least 3 characters long"

    return True, ""


def validate_sex(sex: str) -> Tuple[bool, str]:
    """
    Validate patient sex

    Args:
        sex: Patient sex value

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not sex or not sex.strip():
        return False, "Sex is required"

    if sex not in SEX_OPTIONS:
        return False, f"Sex must be one of: {', '.join(SEX_OPTIONS)}"

    return True, ""


def validate_lesion_location(location: str) -> Tuple[bool, str]:
    """
    Validate lesion anatomical location

    Args:
        location: Lesion location (API format)

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not location or not location.strip():
        return False, "Lesion location is required"

    if location.lower() not in VALID_ANATOMICAL_LOCATIONS:
        return False, f"Invalid location. Must be one of: {', '.join(VALID_ANATOMICAL_LOCATIONS)}"

    return True, ""


def validate_initial_lesion_size(size_mm: float) -> Tuple[bool, str]:
    """
    Validate initial lesion size in millimeters (for lesion creation)
    Accepts any positive size

    Args:
        size_mm: Lesion diameter in millimeters

    Returns:
        Tuple of (is_valid, error_message)
    """
    if size_mm is None:
        return False, "Initial lesion size is required"

    if size_mm <= 0:
        return False, "Lesion size must be greater than 0 mm"

    return True, ""


def validate_current_lesion_size(size_mm: float) -> Tuple[bool, str]:
    """
    Validate current lesion size for analysis (with model constraints)

    Args:
        size_mm: Current lesion diameter in millimeters

    Returns:
        Tuple of (is_valid, error_message)
    """
    if size_mm is None:
        return False, "Current lesion size is required"

    if size_mm < DIAMETER_MIN:
        return False, f"Lesion size for analysis must be at least {DIAMETER_MIN} mm"

    if size_mm > DIAMETER_MAX:
        return False, f"Lesion size for analysis cannot exceed {DIAMETER_MAX} mm"

    return True, ""


def calculate_age_from_dob(date_of_birth: str) -> int:
    """
    Calculate current age from date of birth

    Args:
        date_of_birth: Date string in DD/MM/YYYY format

    Returns:
        Age in years

    Raises:
        ValueError: If date format is invalid
    """
    try:
        birth_date = datetime.strptime(date_of_birth, DATE_FORMAT_PYTHON)
        age_years = int((datetime.now() - birth_date).days / 365.25)
        return age_years
    except ValueError as e:
        raise ValueError(f"Invalid date format: {e}")
