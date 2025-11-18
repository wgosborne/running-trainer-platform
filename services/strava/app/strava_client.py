"""Strava API client for OAuth and activity retrieval."""

from typing import List, Dict
import requests


class StravaClient:
    """Client for interacting with Strava API."""

    def __init__(self, client_id: str, client_secret: str):
        """
        Initialize Strava client.

        Args:
            client_id: Strava application client ID
            client_secret: Strava application client secret
        """
        self.client_id = client_id
        self.client_secret = client_secret

    def get_auth_url(self, redirect_uri: str) -> str:
        """
        Generate Strava OAuth authorization URL.

        Args:
            redirect_uri: URL to redirect to after authorization

        Returns:
            Complete OAuth authorization URL
        """
        base_url = "https://www.strava.com/oauth/authorize"
        params = {
            "client_id": self.client_id,
            "response_type": "code",
            "redirect_uri": redirect_uri,
            "scope": "activity:read"
        }
        param_str = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"{base_url}?{param_str}"

    def get_access_token(self, code: str) -> str:
        """
        Exchange authorization code for access token.

        Args:
            code: Authorization code from OAuth callback

        Returns:
            Access token string

        Raises:
            requests.RequestException: If token exchange fails
        """
        url = "https://www.strava.com/api/v3/oauth/token"
        payload = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": code,
            "grant_type": "authorization_code"
        }
        response = requests.post(url, data=payload)
        response.raise_for_status()
        return response.json()["access_token"]

    def get_recent_runs(self, access_token: str) -> List[Dict]:
        """
        Fetch recent running activities from Strava.

        Args:
            access_token: Valid Strava access token

        Returns:
            List of run activity dictionaries with normalized fields

        Raises:
            requests.RequestException: If API request fails
        """
        url = "https://www.strava.com/api/v3/athlete/activities"
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        activities = response.json()
        runs = []

        for activity in activities:
            if activity.get("type") == "Run":
                runs.append({
                    "id": activity["id"],
                    "distance_km": activity["distance"] / 1000,
                    "moving_time_sec": activity["moving_time"],
                    "start_date_local": activity["start_date_local"],
                    "name": activity["name"]
                })

        return runs
