# Strava Sync Service

Handles OAuth with Strava and syncs running activities into the Running Trainer Service.

## Features

- OAuth 2.0 flow with Strava API
- Fetch recent running activities
- Automatic unit conversion (km to miles, time to pace)
- Sync runs to Running Trainer service with proper attribution

## Endpoints

### GET /strava/auth
Get Strava OAuth authorization URL.

**Query Parameters:**
- `redirect_uri`: URL to redirect to after authorization

**Response:**
```json
{
  "auth_url": "https://www.strava.com/oauth/authorize?..."
}
```

### GET /strava/callback
Handle OAuth callback and store access token.

**Query Parameters:**
- `code`: Authorization code from Strava
- `user_id`: User ID to associate with token

**Response:**
```json
{
  "status": "authorized"
}
```

### POST /strava/sync
Sync recent Strava runs to Running Trainer.

**Query Parameters:**
- `user_id`: User ID
- `plan_id`: Running plan ID to sync to

**Headers:**
- `Authorization`: Bearer token for Running Trainer API

**Response:**
```json
{
  "status": "synced",
  "runs_imported": 5,
  "plan_id": "123"
}
```

## Environment Variables

- `STRAVA_CLIENT_ID`: Strava application client ID
- `STRAVA_CLIENT_SECRET`: Strava application client secret
- `RUNNING_TRAINER_URL`: URL of Running Trainer service (default: http://running-trainer-service:8000)
- `LOG_LEVEL`: Logging level (default: INFO)

## MVP Notes

**Token Storage:** This MVP version uses in-memory token storage (simple dict). Tokens will be lost on service restart. Future versions should use persistent storage (database, Redis, etc.).

**Run Matching:** Runs are matched by date only in this MVP version.

## Running Locally

```bash
cd running_tracker/services/strava
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8003
```

## Running with Docker

```bash
docker-compose up strava-service
```

Service will be available at http://localhost:8003
