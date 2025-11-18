"""Strava Sync Service - FastAPI application."""

import os
from typing import Dict
from fastapi import FastAPI, HTTPException, Header, Query
from strava_client import StravaClient
import requests

app = FastAPI(title="Strava Sync Service")

# In-memory token storage (MVP - no persistence)
token_store: Dict[str, str] = {}

# Load environment variables
STRAVA_CLIENT_ID = os.getenv("STRAVA_CLIENT_ID", "")
STRAVA_CLIENT_SECRET = os.getenv("STRAVA_CLIENT_SECRET", "")
RUNNING_TRAINER_URL = os.getenv("RUNNING_TRAINER_URL", "http://running-trainer-service:8000")

# Initialize Strava client
strava_client = StravaClient(STRAVA_CLIENT_ID, STRAVA_CLIENT_SECRET)


@app.get("/strava/auth")
async def get_auth_url(redirect_uri: str = Query(..., description="OAuth redirect URI")) -> Dict[str, str]:
    """
    Get Strava OAuth authorization URL.

    Args:
        redirect_uri: URL to redirect to after authorization

    Returns:
        Dictionary containing the authorization URL
    """
    try:
        auth_url = strava_client.get_auth_url(redirect_uri)
        return {"auth_url": auth_url}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to generate auth URL: {str(e)}")


@app.get("/strava/callback")
async def oauth_callback(
    code: str = Query(..., description="Authorization code from Strava"),
    user_id: str = Query(..., description="User ID to associate with token")
) -> Dict[str, str]:
    """
    Handle Strava OAuth callback and store access token.

    Args:
        code: Authorization code from Strava OAuth flow
        user_id: User ID to associate with the token

    Returns:
        Status confirmation
    """
    try:
        token = strava_client.get_access_token(code)
        token_store[user_id] = token
        return {"status": "authorized"}
    except requests.RequestException as e:
        raise HTTPException(status_code=400, detail=f"Failed to exchange code for token: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Authorization failed: {str(e)}")


@app.post("/strava/sync")
async def sync_runs(
    user_id: str = Query(..., description="User ID"),
    plan_id: str = Query(..., description="Running plan ID"),
    authorization: str = Header(..., description="Bearer token for Running Trainer API")
) -> Dict:
    """
    Sync recent Strava runs to Running Trainer service.

    Args:
        user_id: User ID to retrieve Strava token
        plan_id: Running plan ID to sync runs to
        authorization: Authorization header with Bearer token for Running Trainer API

    Returns:
        Sync status with number of runs imported
    """
    try:
        # Check if user has authorized Strava
        if user_id not in token_store:
            raise HTTPException(status_code=400, detail="User has not authorized Strava access")

        # Fetch recent runs from Strava
        access_token = token_store[user_id]
        runs = strava_client.get_recent_runs(access_token)

        # Sync each run to Running Trainer
        for run in runs:
            distance_km = run["distance_km"]
            distance_miles = distance_km * 0.621371

            # Calculate pace in seconds per mile
            moving_time_sec = run["moving_time_sec"]
            if distance_miles > 0:
                pace_sec_per_mile = moving_time_sec / distance_miles
            else:
                pace_sec_per_mile = 0

            # Prepare payload for Running Trainer API
            payload = {
                "distance_miles": distance_miles,
                "pace_sec_per_mile": int(pace_sec_per_mile),
                "date": run["start_date_local"],
                "source": "strava",
                "external_id": run["id"]
            }

            # POST to Running Trainer API
            url = f"{RUNNING_TRAINER_URL}/api/v1/plans/{plan_id}/runs"
            headers = {"Authorization": authorization}
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()

        return {
            "status": "synced",
            "runs_imported": len(runs),
            "plan_id": plan_id
        }

    except requests.RequestException as e:
        raise HTTPException(status_code=400, detail=f"API request failed: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Sync failed: {str(e)}")


@app.get("/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}
