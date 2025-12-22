"""
Prediction Service for Skin Lesion AI Backend

This service handles all communication with the backend API,
including health checks and prediction requests.
"""

import requests
from typing import Dict, Any, Optional
from dataclasses import dataclass
from config import API_BASE_URL, API_TIMEOUT, VALID_ANATOMICAL_LOCATIONS


@dataclass
class PredictionResponse:
    """Data class for prediction API response"""
    final_probability: float
    model_a_probability: float
    model_c_probability: float
    extracted_features: list
    risk_category: str
    metadata: Dict[str, Any]

    def __str__(self):
        return f"Risk: {self.risk_category.upper()} | Probability: {self.final_probability:.2%}"


class PredictionService:
    """Service to interact with the Skin Lesion AI backend API"""

    def __init__(self, base_url: str = None):
        """
        Initialize the prediction service

        Args:
            base_url: Base URL of the backend API (defaults to config.API_BASE_URL)
        """
        self.base_url = (base_url or API_BASE_URL).rstrip('/')
        self.timeout = API_TIMEOUT

    def check_health(self) -> Dict[str, str]:
        """
        Check if the backend API is healthy

        Returns:
            Dictionary with status information

        Raises:
            requests.exceptions.RequestException: If connection fails
        """
        try:
            response = requests.get(
                f"{self.base_url}/health",
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Health check failed: {str(e)}")

    def get_api_info(self) -> Dict[str, Any]:
        """
        Get API information

        Returns:
            Dictionary with API details

        Raises:
            requests.exceptions.RequestException: If connection fails
        """
        try:
            response = requests.get(
                f"{self.base_url}/",
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to get API info: {str(e)}")

    def submit_prediction(
        self,
        image_file,
        age: int,
        sex: str,
        location: str,
        diameter: float
    ) -> PredictionResponse:
        """
        Submit a prediction request to the backend API

        Args:
            image_file: File object or bytes of the image
            age: Patient age (0-120)
            sex: Patient sex ("male" or "female")
            location: Anatomical location of lesion
            diameter: Lesion diameter in millimeters (> 0)

        Returns:
            PredictionResponse object with prediction results

        Raises:
            ValueError: If validation fails
            requests.exceptions.RequestException: If API call fails
        """
        # Validate inputs
        self._validate_inputs(age, sex, location, diameter)

        # Prepare the multipart form data
        # Need to ensure the file is properly formatted with filename and content-type
        # Get the filename from the file object if available
        filename = getattr(image_file, 'name', 'lesion_image.jpg')

        # Determine content type based on filename extension
        content_type = 'image/jpeg'
        if filename.lower().endswith('.png'):
            content_type = 'image/png'
        elif filename.lower().endswith('.bmp'):
            content_type = 'image/bmp'
        elif filename.lower().endswith(('.tiff', '.tif')):
            content_type = 'image/tiff'

        files = {
            'image': (filename, image_file, content_type)
        }

        data = {
            'age': age,
            'sex': sex.lower(),
            'location': location,
            'diameter': diameter
        }

        try:
            response = requests.post(
                f"{self.base_url}/api/predict",
                files=files,
                data=data,
                timeout=self.timeout
            )
            response.raise_for_status()

            # Parse response
            result = response.json()

            return PredictionResponse(
                final_probability=result['final_probability'],
                model_a_probability=result['model_a_probability'],
                model_c_probability=result['model_c_probability'],
                extracted_features=result['extracted_features'],
                risk_category=result['risk_category'],
                metadata=result['metadata']
            )

        except requests.exceptions.HTTPError as e:
            # Handle HTTP errors with detail from API
            try:
                error_detail = response.json().get('detail', str(e))
            except:
                error_detail = str(e)
            raise Exception(f"API Error: {error_detail}")

        except requests.exceptions.RequestException as e:
            raise Exception(f"Connection error: {str(e)}")

    def _validate_inputs(self, age: int, sex: str, location: str, diameter: float):
        """
        Validate input parameters

        Raises:
            ValueError: If validation fails
        """
        if not (0 <= age <= 120):
            raise ValueError(f"Age must be between 0 and 120, got {age}")

        if sex.lower() not in ["male", "female"]:
            raise ValueError(f"Sex must be 'male' or 'female', got {sex}")

        if location.lower() not in VALID_ANATOMICAL_LOCATIONS:
            raise ValueError(
                f"Location must be one of {VALID_ANATOMICAL_LOCATIONS}, got {location}"
            )

        if diameter <= 0:
            raise ValueError(f"Diameter must be positive, got {diameter}")


# Utility function for easy import
def create_service(base_url: str = None) -> PredictionService:
    """
    Factory function to create a PredictionService instance

    Args:
        base_url: Base URL of the backend API (defaults to config.API_BASE_URL)

    Returns:
        Configured PredictionService instance
    """
    return PredictionService(base_url)
