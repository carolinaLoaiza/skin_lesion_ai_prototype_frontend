"""
Analysis Service

Handles all communication with the backend API for analysis history and retrieval.
"""

import requests
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
from config import API_BASE_URL, API_TIMEOUT, API_ENDPOINTS


@dataclass
class AnalysisCase:
    """Data class for analysis case information"""
    _id: str
    analysis_id: str
    patient_id: str
    lesion_id: str
    created_at: str
    capture_date: str
    days_since_first_observation: int
    age_at_capture: int
    lesion_size_mm: float
    model_a_probability: float  # image_only_model
    model_c_probability: float  # clinical_ml_model
    image_filename: Optional[str] = None
    image_path: Optional[str] = None
    shap_top_features: Optional[List[Dict[str, Any]]] = None  # SHAP features array
    shap_prediction: Optional[float] = None  # SHAP prediction value
    shap_base_value: Optional[float] = None  # SHAP base value
    extracted_features: Optional[List[Dict[str, Any]]] = None  # Extracted features from CV model

    def __str__(self):
        return f"{self.analysis_id} - {self.capture_date} - Size: {self.lesion_size_mm}mm"

    @property
    def capture_datetime(self) -> datetime:
        """Parse capture_date to datetime object"""
        try:
            return datetime.fromisoformat(self.capture_date.replace('Z', '+00:00'))
        except:
            return datetime.now()


class AnalysisService:
    """Service to interact with Analysis APIs"""

    def __init__(self, base_url: str = None):
        """
        Initialize the service

        Args:
            base_url: Base URL of the backend API (defaults to config.API_BASE_URL)
        """
        self.base_url = (base_url or API_BASE_URL).rstrip('/')
        self.timeout = API_TIMEOUT

    def get_lesion_analyses(self, lesion_id: str) -> List[AnalysisCase]:
        """
        Get all analyses for a specific lesion

        Args:
            lesion_id: Lesion ID

        Returns:
            List of AnalysisCase objects sorted by capture_date (oldest first)

        Raises:
            Exception: If API call fails
        """
        url = f"{self.base_url}{API_ENDPOINTS['lesion_analyses'].format(lesion_id=lesion_id)}"

        try:
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()

            data = response.json()
            analyses = []

            for item in data:
                # Parse the response structure
                clinical_data = item.get('clinical_data', {})
                model_outputs = item.get('model_outputs', {})
                temporal_data = item.get('temporal_data', {})
                image_data = item.get('image', {})
                shap_data = item.get('shap_analysis', {})

                analysis = AnalysisCase(
                    _id=item.get('_id'),
                    analysis_id=item.get('analysis_id'),
                    patient_id=item.get('patient_id'),
                    lesion_id=item.get('lesion_id'),
                    created_at=item.get('created_at'),
                    capture_date=temporal_data.get('capture_date', item.get('created_at')),
                    days_since_first_observation=temporal_data.get('days_since_first_observation', 0),
                    age_at_capture=clinical_data.get('age_at_capture', 0),
                    lesion_size_mm=clinical_data.get('lesion_size_mm', 0.0),
                    model_a_probability=model_outputs.get('image_only_model', {}).get('malignant_probability', 0.0),
                    model_c_probability=model_outputs.get('clinical_ml_model', {}).get('malignant_probability', 0.0),
                    image_filename=image_data.get('filename'),
                    image_path=image_data.get('path'),
                    shap_top_features=shap_data.get('features', []),  # Correct field name
                    shap_prediction=shap_data.get('prediction'),
                    shap_base_value=shap_data.get('base_value'),
                    extracted_features=model_outputs.get('extracted_features', [])
                )
                analyses.append(analysis)

            # Sort by capture_date (oldest first)
            analyses.sort(key=lambda x: x.capture_datetime)

            return analyses

        except requests.exceptions.HTTPError as e:
            if response.status_code == 404:
                return []  # No analyses found for this lesion
            try:
                error_detail = response.json().get('detail', str(e))
            except:
                error_detail = str(e)
            raise Exception(f"Failed to get lesion analyses: {error_detail}")

        except requests.exceptions.RequestException as e:
            raise Exception(f"Connection error: {str(e)}")

    def get_all_patients(self) -> List[Dict[str, Any]]:
        """
        Get all patients

        Returns:
            List of patient dictionaries

        Raises:
            Exception: If API call fails
        """
        url = f"{self.base_url}{API_ENDPOINTS['patients']}"

        try:
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()
            return response.json()

        except requests.exceptions.HTTPError as e:
            try:
                error_detail = response.json().get('detail', str(e))
            except:
                error_detail = str(e)
            raise Exception(f"Failed to get patients: {error_detail}")

        except requests.exceptions.RequestException as e:
            raise Exception(f"Connection error: {str(e)}")

    def get_analysis_image_url(self, analysis_id: str) -> str:
        """
        Get full URL for analysis image using the dedicated endpoint

        Args:
            analysis_id: Analysis ID

        Returns:
            Full URL to image endpoint
        """
        if not analysis_id:
            return None

        return f"{self.base_url}{API_ENDPOINTS['analysis_image'].format(analysis_id=analysis_id)}"

    def get_feature_display_names(self) -> Dict[str, str]:
        """
        Get feature name mappings from backend

        Returns:
            Dictionary mapping technical names to display names

        Raises:
            Exception: If API call fails
        """
        url = f"{self.base_url}{API_ENDPOINTS['feature_names']}"

        try:
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()
            return response.json()

        except requests.exceptions.HTTPError as e:
            # If endpoint doesn't exist, return empty dict
            if response.status_code == 404:
                return {}
            try:
                error_detail = response.json().get('detail', str(e))
            except:
                error_detail = str(e)
            raise Exception(f"Failed to get feature names: {error_detail}")

        except requests.exceptions.RequestException as e:
            # On connection error, return empty dict (graceful degradation)
            return {}


# Utility function for easy import
def create_analysis_service(base_url: str = None) -> AnalysisService:
    """
    Factory function to create an AnalysisService instance

    Args:
        base_url: Base URL of the backend API (defaults to config.API_BASE_URL)

    Returns:
        Configured AnalysisService instance
    """
    return AnalysisService(base_url)
