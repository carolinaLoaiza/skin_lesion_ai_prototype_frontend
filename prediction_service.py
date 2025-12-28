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
    model_a_probability: float
    model_c_probability: float
    extracted_features: list
    metadata: Dict[str, Any]
    analysis_id: Optional[str] = None

    def __str__(self):
        return f"Model A: {self.model_a_probability:.2%} | Model C: {self.model_c_probability:.2%} | Analysis: {self.analysis_id}"


@dataclass
class FeatureContribution:
    """Data class for individual feature contribution"""
    feature_name: str
    display_name: str  # Human-readable feature name
    shap_value: float
    feature_value: float
    impact: str  # "increases" or "decreases"


@dataclass
class ExplainResponse:
    """Data class for SHAP explanation API response"""
    prediction: float
    base_value: float
    feature_contributions: list  # List of FeatureContribution objects
    metadata: Dict[str, Any]

    def __str__(self):
        return f"Prediction: {self.prediction:.2%} | Base: {self.base_value:.2%} | Features: {len(self.feature_contributions)}"


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
        diameter: float,
        patient_id: str,
        lesion_id: str
    ) -> PredictionResponse:
        """
        Submit a prediction request to the backend API and save analysis to database

        Args:
            image_file: File object or bytes of the image
            age: Patient age (0-120)
            sex: Patient sex ("male" or "female")
            location: Anatomical location of lesion
            diameter: Lesion diameter in millimeters (> 0)
            patient_id: Patient ID (required - analysis will be saved to this patient)
            lesion_id: Lesion ID (required - analysis will be saved to this lesion)

        Returns:
            PredictionResponse object with prediction results and analysis_id

        Raises:
            ValueError: If validation fails
            requests.exceptions.RequestException: If API call fails
        """
        # Validate inputs
        self._validate_inputs(age, sex, location, diameter)

        # Validate patient_id and lesion_id
        if not patient_id or not patient_id.strip():
            raise ValueError("patient_id is required")
        if not lesion_id or not lesion_id.strip():
            raise ValueError("lesion_id is required")

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
            'diameter': diameter,
            'patient_id': patient_id,
            'lesion_id': lesion_id
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
                model_a_probability=result['model_a_probability'],
                model_c_probability=result['model_c_probability'],
                extracted_features=result['extracted_features'],
                metadata=result['metadata'],
                analysis_id=result.get('analysis_id')
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

    def get_explanation(
        self,
        image_file,
        age: int,
        sex: str,
        location: str,
        diameter: float
    ) -> ExplainResponse:
        """
        Get SHAP explanation for a prediction

        Args:
            image_file: File object or bytes of the image
            age: Patient age (0-120)
            sex: Patient sex ("male" or "female")
            location: Anatomical location of lesion
            diameter: Lesion diameter in millimeters (> 0)

        Returns:
            ExplainResponse object with SHAP values and feature contributions

        Raises:
            ValueError: If validation fails
            requests.exceptions.RequestException: If API call fails
        """
        # Validate inputs
        self._validate_inputs(age, sex, location, diameter)

        # Prepare the multipart form data (same as prediction)
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
                f"{self.base_url}/api/explain",
                files=files,
                data=data,
                timeout=self.timeout
            )
            response.raise_for_status()

            # Parse response
            result = response.json()

            # Convert feature contributions to FeatureContribution objects
            feature_contributions = [
                FeatureContribution(
                    feature_name=fc['feature_name'],
                    display_name=fc['display_name'],
                    shap_value=fc['shap_value'],
                    feature_value=fc['feature_value'],
                    impact=fc['impact']
                )
                for fc in result['feature_contributions']
            ]

            return ExplainResponse(
                prediction=result['prediction'],
                base_value=result['base_value'],
                feature_contributions=feature_contributions,
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
