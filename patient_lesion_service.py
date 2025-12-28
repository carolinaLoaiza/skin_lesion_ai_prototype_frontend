"""
Patient and Lesion Service

Handles all communication with the backend API for patient and lesion management.
"""

import requests
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from config import API_BASE_URL, API_TIMEOUT, API_ENDPOINTS


@dataclass
class Patient:
    """Data class for patient information"""
    patient_id: str
    patient_full_name: str
    sex: str
    date_of_birth: str
    created_at: Optional[str] = None
    _id: Optional[str] = None

    def __str__(self):
        return f"{self.patient_full_name} ({self.patient_id})"


@dataclass
class Lesion:
    """Data class for lesion information"""
    lesion_id: str
    patient_id: str
    lesion_location: str
    initial_size_mm: float
    created_at: Optional[str] = None
    _id: Optional[str] = None

    def __str__(self):
        return f"{self.lesion_id} - {self.lesion_location} ({self.initial_size_mm}mm)"


class PatientLesionService:
    """Service to interact with Patient and Lesion APIs"""

    def __init__(self, base_url: str = None):
        """
        Initialize the service

        Args:
            base_url: Base URL of the backend API (defaults to config.API_BASE_URL)
        """
        self.base_url = (base_url or API_BASE_URL).rstrip('/')
        self.timeout = API_TIMEOUT

    # =============================================================================
    # PATIENT METHODS
    # =============================================================================

    def create_patient(
        self,
        patient_id: str,
        patient_full_name: str,
        sex: str,
        date_of_birth: str
    ) -> Patient:
        """
        Create a new patient

        Args:
            patient_id: Unique patient ID (e.g., PAT-20250126143025)
            patient_full_name: Patient's full name
            sex: Patient sex ("male" or "female")
            date_of_birth: Date in DD/MM/YYYY format

        Returns:
            Patient object with created patient data

        Raises:
            Exception: If API call fails
        """
        url = f"{self.base_url}{API_ENDPOINTS['patients']}"

        payload = {
            "patient_id": patient_id,
            "patient_full_name": patient_full_name,
            "sex": sex.lower(),
            "date_of_birth": date_of_birth
        }

        try:
            response = requests.post(
                url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=self.timeout
            )
            response.raise_for_status()

            data = response.json()
            return Patient(
                _id=data.get("_id"),
                patient_id=data["patient_id"],
                patient_full_name=data["patient_full_name"],
                sex=data["sex"],
                date_of_birth=data["date_of_birth"],
                created_at=data.get("created_at")
            )

        except requests.exceptions.HTTPError as e:
            try:
                error_detail = response.json().get('detail', str(e))
            except:
                error_detail = str(e)
            raise Exception(f"Failed to create patient: {error_detail}")

        except requests.exceptions.RequestException as e:
            raise Exception(f"Connection error: {str(e)}")

    def search_patients_by_name(self, search_term: str) -> List[Patient]:
        """
        Search patients by name

        Args:
            search_term: Search string (minimum 2 characters)

        Returns:
            List of Patient objects matching the search

        Raises:
            Exception: If API call fails
        """
        if len(search_term) < 2:
            return []

        url = f"{self.base_url}{API_ENDPOINTS['patients_search']}"

        try:
            response = requests.get(
                url,
                params={"name": search_term},
                timeout=self.timeout
            )
            response.raise_for_status()

            data = response.json()
            return [
                Patient(
                    _id=p.get("_id"),
                    patient_id=p["patient_id"],
                    patient_full_name=p["patient_full_name"],
                    sex=p["sex"],
                    date_of_birth=p["date_of_birth"],
                    created_at=p.get("created_at")
                )
                for p in data
            ]

        except requests.exceptions.HTTPError as e:
            try:
                error_detail = response.json().get('detail', str(e))
            except:
                error_detail = str(e)
            raise Exception(f"Search failed: {error_detail}")

        except requests.exceptions.RequestException as e:
            raise Exception(f"Connection error: {str(e)}")

    def get_patient_by_id(self, patient_id: str) -> Optional[Patient]:
        """
        Get patient by ID

        Args:
            patient_id: Patient ID

        Returns:
            Patient object or None if not found

        Raises:
            Exception: If API call fails
        """
        url = f"{self.base_url}{API_ENDPOINTS['patient_by_id'].format(patient_id=patient_id)}"

        try:
            response = requests.get(url, timeout=self.timeout)

            if response.status_code == 404:
                return None

            response.raise_for_status()

            data = response.json()
            return Patient(
                _id=data.get("_id"),
                patient_id=data["patient_id"],
                patient_full_name=data["patient_full_name"],
                sex=data["sex"],
                date_of_birth=data["date_of_birth"],
                created_at=data.get("created_at")
            )

        except requests.exceptions.HTTPError as e:
            if response.status_code == 404:
                return None
            try:
                error_detail = response.json().get('detail', str(e))
            except:
                error_detail = str(e)
            raise Exception(f"Failed to get patient: {error_detail}")

        except requests.exceptions.RequestException as e:
            raise Exception(f"Connection error: {str(e)}")

    # =============================================================================
    # LESION METHODS
    # =============================================================================

    def create_lesion(
        self,
        lesion_id: str,
        patient_id: str,
        lesion_location: str,
        initial_size_mm: float
    ) -> Lesion:
        """
        Create a new lesion

        Args:
            lesion_id: Unique lesion ID (e.g., LESION_LL_001)
            patient_id: Patient ID this lesion belongs to
            lesion_location: Anatomical location (API format, e.g., "left leg")
            initial_size_mm: Initial size in millimeters

        Returns:
            Lesion object with created lesion data

        Raises:
            Exception: If API call fails
        """
        url = f"{self.base_url}{API_ENDPOINTS['lesions']}"

        payload = {
            "lesion_id": lesion_id,
            "patient_id": patient_id,
            "lesion_location": lesion_location,
            "initial_size_mm": initial_size_mm
        }

        try:
            response = requests.post(
                url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=self.timeout
            )
            response.raise_for_status()

            data = response.json()
            return Lesion(
                _id=data.get("_id"),
                lesion_id=data["lesion_id"],
                patient_id=data["patient_id"],
                lesion_location=data["lesion_location"],
                initial_size_mm=data["initial_size_mm"],
                created_at=data.get("created_at")
            )

        except requests.exceptions.HTTPError as e:
            try:
                error_detail = response.json().get('detail', str(e))
            except:
                error_detail = str(e)
            raise Exception(f"Failed to create lesion: {error_detail}")

        except requests.exceptions.RequestException as e:
            raise Exception(f"Connection error: {str(e)}")

    def get_lesions_by_patient(self, patient_id: str) -> List[Lesion]:
        """
        Get all lesions for a patient

        Args:
            patient_id: Patient ID

        Returns:
            List of Lesion objects

        Raises:
            Exception: If API call fails
        """
        url = f"{self.base_url}{API_ENDPOINTS['patient_lesions'].format(patient_id=patient_id)}"

        try:
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()

            data = response.json()
            return [
                Lesion(
                    _id=l.get("_id"),
                    lesion_id=l["lesion_id"],
                    patient_id=l["patient_id"],
                    lesion_location=l["lesion_location"],
                    initial_size_mm=l["initial_size_mm"],
                    created_at=l.get("created_at")
                )
                for l in data
            ]

        except requests.exceptions.HTTPError as e:
            try:
                error_detail = response.json().get('detail', str(e))
            except:
                error_detail = str(e)
            raise Exception(f"Failed to get lesions: {error_detail}")

        except requests.exceptions.RequestException as e:
            raise Exception(f"Connection error: {str(e)}")

    def get_lesion_by_id(self, lesion_id: str) -> Optional[Lesion]:
        """
        Get lesion by ID

        Args:
            lesion_id: Lesion ID

        Returns:
            Lesion object or None if not found

        Raises:
            Exception: If API call fails
        """
        url = f"{self.base_url}{API_ENDPOINTS['lesion_by_id'].format(lesion_id=lesion_id)}"

        try:
            response = requests.get(url, timeout=self.timeout)

            if response.status_code == 404:
                return None

            response.raise_for_status()

            data = response.json()
            return Lesion(
                _id=data.get("_id"),
                lesion_id=data["lesion_id"],
                patient_id=data["patient_id"],
                lesion_location=data["lesion_location"],
                initial_size_mm=data["initial_size_mm"],
                created_at=data.get("created_at")
            )

        except requests.exceptions.HTTPError as e:
            if response.status_code == 404:
                return None
            try:
                error_detail = response.json().get('detail', str(e))
            except:
                error_detail = str(e)
            raise Exception(f"Failed to get lesion: {error_detail}")

        except requests.exceptions.RequestException as e:
            raise Exception(f"Connection error: {str(e)}")


# Utility function for easy import
def create_patient_lesion_service(base_url: str = None) -> PatientLesionService:
    """
    Factory function to create a PatientLesionService instance

    Args:
        base_url: Base URL of the backend API (defaults to config.API_BASE_URL)

    Returns:
        Configured PatientLesionService instance
    """
    return PatientLesionService(base_url)
