"""API Gateway - Single entry point for all microservices."""

import os
import logging
from typing import Optional
from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Running Tracker API Gateway")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Frontend development server
        "http://127.0.0.1:5173",
        "http://localhost:5175",  # Alternative frontend port
        "http://127.0.0.1:5175",
    ],
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, PUT, DELETE, OPTIONS, etc.)
    allow_headers=["*"],  # Allow all headers
)

# Load service URLs from environment
RUNNING_TRAINER_URL = os.getenv("RUNNING_TRAINER_URL", "http://running-trainer:8000")
AUTH_URL = os.getenv("AUTH_URL", "http://auth:8000")
PDF_URL = os.getenv("PDF_URL", "http://pdf:8000")
STRAVA_URL = os.getenv("STRAVA_URL", "http://strava:8000")


def forward_request(
    method: str,
    service_url: str,
    path: str,
    headers: dict,
    body: Optional[bytes] = None,
    params: Optional[dict] = None
) -> Response:
    """
    Forward request to target service.

    Args:
        method: HTTP method (GET, POST, etc.)
        service_url: Base URL of target service
        path: Path to append to service URL
        headers: Request headers to forward
        body: Request body (for POST, PUT, etc.)
        params: Query parameters

    Returns:
        Response from target service

    Raises:
        HTTPException: If service is unreachable (503)
    """
    target_url = f"{service_url}{path}"

    # Copy authorization header if present
    forward_headers = {}
    if "authorization" in headers:
        forward_headers["Authorization"] = headers["authorization"]
    if "content-type" in headers:
        forward_headers["Content-Type"] = headers["content-type"]

    logger.info(f"{method} {path} -> {target_url} (params: {params})")

    try:
        response = requests.request(
            method=method,
            url=target_url,
            headers=forward_headers,
            data=body,
            params=params,
            timeout=30
        )

        logger.info(f"{method} {path} <- {response.status_code}")

        return Response(
            content=response.content,
            status_code=response.status_code,
            headers=dict(response.headers)
        )

    except requests.exceptions.RequestException as e:
        logger.error(f"Service unreachable: {target_url} - {str(e)}")
        raise HTTPException(status_code=503, detail=f"Service unavailable: {str(e)}")


# Auth routes (no auth required)
@app.post("/auth/register")
async def register(request: Request):
    """Forward registration request to auth service."""
    body = await request.body()
    return forward_request(
        method="POST",
        service_url=AUTH_URL,
        path="/register",
        headers=dict(request.headers),
        body=body
    )


@app.post("/auth/login")
async def login(request: Request):
    """Forward login request to auth service."""
    body = await request.body()
    return forward_request(
        method="POST",
        service_url=AUTH_URL,
        path="/login",
        headers=dict(request.headers),
        body=body
    )


# Running Trainer routes - Plans
@app.get("/plans/{path:path}")
async def get_plans(path: str, request: Request):
    """Forward GET plans request to running trainer service."""
    return forward_request(
        method="GET",
        service_url=RUNNING_TRAINER_URL,
        path=f"/api/v1/plans/{path}",
        headers=dict(request.headers),
        params=dict(request.query_params)
    )


@app.get("/plans")
async def get_all_plans(request: Request):
    """Forward GET all plans request to running trainer service."""
    return forward_request(
        method="GET",
        service_url=RUNNING_TRAINER_URL,
        path="/api/v1/plans",
        headers=dict(request.headers),
        params=dict(request.query_params)
    )


@app.post("/plans/{path:path}")
async def post_plans(path: str, request: Request):
    """Forward POST plans request to running trainer service."""
    body = await request.body()
    return forward_request(
        method="POST",
        service_url=RUNNING_TRAINER_URL,
        path=f"/api/v1/plans/{path}",
        headers=dict(request.headers),
        body=body
    )


@app.post("/plans")
async def create_plan(request: Request):
    """Forward create plan request to running trainer service."""
    body = await request.body()
    return forward_request(
        method="POST",
        service_url=RUNNING_TRAINER_URL,
        path="/api/v1/plans",
        headers=dict(request.headers),
        body=body
    )


# Running Trainer routes - Runs
@app.get("/runs/{path:path}")
async def get_runs(path: str, request: Request):
    """Forward GET runs request to running trainer service."""
    return forward_request(
        method="GET",
        service_url=RUNNING_TRAINER_URL,
        path=f"/api/v1/runs/{path}",
        headers=dict(request.headers),
        params=dict(request.query_params)
    )


@app.get("/runs")
async def get_all_runs(request: Request):
    """Forward GET all runs request to running trainer service."""
    return forward_request(
        method="GET",
        service_url=RUNNING_TRAINER_URL,
        path="/api/v1/runs",
        headers=dict(request.headers),
        params=dict(request.query_params)
    )


@app.post("/runs/{path:path}")
async def post_runs(path: str, request: Request):
    """Forward POST runs request to running trainer service."""
    body = await request.body()
    return forward_request(
        method="POST",
        service_url=RUNNING_TRAINER_URL,
        path=f"/api/v1/runs/{path}",
        headers=dict(request.headers),
        body=body
    )


@app.post("/runs")
async def create_run(request: Request):
    """Forward create run request to running trainer service."""
    body = await request.body()
    return forward_request(
        method="POST",
        service_url=RUNNING_TRAINER_URL,
        path="/api/v1/runs",
        headers=dict(request.headers),
        body=body
    )


# Workout routes
@app.get("/plans/{plan_id}/workouts")
async def get_workouts_for_plan(plan_id: str, request: Request):
    """Forward GET workouts for plan request to running trainer service."""
    return forward_request(
        method="GET",
        service_url=RUNNING_TRAINER_URL,
        path=f"/api/v1/plans/{plan_id}/workouts",
        headers=dict(request.headers),
        params=dict(request.query_params)
    )


@app.post("/plans/{plan_id}/workouts")
async def create_workout(plan_id: str, request: Request):
    """Forward create workout request to running trainer service."""
    body = await request.body()
    return forward_request(
        method="POST",
        service_url=RUNNING_TRAINER_URL,
        path=f"/api/v1/plans/{plan_id}/workouts",
        headers=dict(request.headers),
        body=body
    )


@app.get("/plans/{plan_id}/workouts/{workout_id}")
async def get_workout(plan_id: str, workout_id: str, request: Request):
    """Forward GET workout request to running trainer service."""
    return forward_request(
        method="GET",
        service_url=RUNNING_TRAINER_URL,
        path=f"/api/v1/plans/{plan_id}/workouts/{workout_id}",
        headers=dict(request.headers),
        params=dict(request.query_params)
    )


@app.patch("/plans/{plan_id}/workouts/{workout_id}")
async def update_workout(plan_id: str, workout_id: str, request: Request):
    """Forward PATCH workout request to running trainer service."""
    body = await request.body()
    return forward_request(
        method="PATCH",
        service_url=RUNNING_TRAINER_URL,
        path=f"/api/v1/plans/{plan_id}/workouts/{workout_id}",
        headers=dict(request.headers),
        body=body
    )


@app.delete("/plans/{plan_id}/workouts/{workout_id}")
async def delete_workout(plan_id: str, workout_id: str, request: Request):
    """Forward DELETE workout request to running trainer service."""
    return forward_request(
        method="DELETE",
        service_url=RUNNING_TRAINER_URL,
        path=f"/api/v1/plans/{plan_id}/workouts/{workout_id}",
        headers=dict(request.headers)
    )


# Plan-scoped runs routes
@app.get("/plans/{plan_id}/runs")
async def get_runs_for_plan(plan_id: str, request: Request):
    """Forward GET runs for plan request to running trainer service."""
    return forward_request(
        method="GET",
        service_url=RUNNING_TRAINER_URL,
        path=f"/api/v1/plans/{plan_id}/runs",
        headers=dict(request.headers),
        params=dict(request.query_params)
    )


@app.post("/plans/{plan_id}/runs")
async def create_run_for_plan(plan_id: str, request: Request):
    """Forward create run for plan request to running trainer service."""
    body = await request.body()
    return forward_request(
        method="POST",
        service_url=RUNNING_TRAINER_URL,
        path=f"/api/v1/plans/{plan_id}/runs",
        headers=dict(request.headers),
        body=body
    )


# PDF Import route
@app.post("/import/pdf")
async def import_pdf(request: Request):
    """Forward PDF import request to PDF service."""
    body = await request.body()
    return forward_request(
        method="POST",
        service_url=PDF_URL,
        path="/import/pdf",
        headers=dict(request.headers),
        body=body,
        params=dict(request.query_params)
    )


# Strava routes
@app.get("/strava/auth")
async def strava_auth(request: Request):
    """Forward Strava auth request to Strava service."""
    return forward_request(
        method="GET",
        service_url=STRAVA_URL,
        path="/strava/auth",
        headers=dict(request.headers),
        params=dict(request.query_params)
    )


@app.get("/strava/callback")
async def strava_callback(request: Request):
    """Forward Strava callback to Strava service."""
    return forward_request(
        method="GET",
        service_url=STRAVA_URL,
        path="/strava/callback",
        headers=dict(request.headers),
        params=dict(request.query_params)
    )


@app.post("/strava/sync")
async def strava_sync(request: Request):
    """Forward Strava sync request to Strava service."""
    body = await request.body()
    return forward_request(
        method="POST",
        service_url=STRAVA_URL,
        path="/strava/sync",
        headers=dict(request.headers),
        body=body,
        params=dict(request.query_params)
    )


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "api-gateway"}


# Backward compatibility - support /api/v1 prefix
@app.get("/api/v1/plans/{path:path}")
async def get_plans_v1(path: str, request: Request):
    """Backward compatible GET plans request."""
    return forward_request(
        method="GET",
        service_url=RUNNING_TRAINER_URL,
        path=f"/api/v1/plans/{path}",
        headers=dict(request.headers),
        params=dict(request.query_params)
    )


@app.get("/api/v1/plans")
async def get_all_plans_v1(request: Request):
    """Backward compatible GET all plans request."""
    return forward_request(
        method="GET",
        service_url=RUNNING_TRAINER_URL,
        path="/api/v1/plans",
        headers=dict(request.headers),
        params=dict(request.query_params)
    )


@app.post("/api/v1/plans/{path:path}")
async def post_plans_v1(path: str, request: Request):
    """Backward compatible POST plans request."""
    body = await request.body()
    return forward_request(
        method="POST",
        service_url=RUNNING_TRAINER_URL,
        path=f"/api/v1/plans/{path}",
        headers=dict(request.headers),
        body=body
    )


@app.post("/api/v1/plans")
async def create_plan_v1(request: Request):
    """Backward compatible create plan request."""
    body = await request.body()
    return forward_request(
        method="POST",
        service_url=RUNNING_TRAINER_URL,
        path="/api/v1/plans",
        headers=dict(request.headers),
        body=body
    )


@app.get("/api/v1/runs/{path:path}")
async def get_runs_v1(path: str, request: Request):
    """Backward compatible GET runs request."""
    return forward_request(
        method="GET",
        service_url=RUNNING_TRAINER_URL,
        path=f"/api/v1/runs/{path}",
        headers=dict(request.headers),
        params=dict(request.query_params)
    )


@app.get("/api/v1/runs")
async def get_all_runs_v1(request: Request):
    """Backward compatible GET all runs request."""
    return forward_request(
        method="GET",
        service_url=RUNNING_TRAINER_URL,
        path="/api/v1/runs",
        headers=dict(request.headers),
        params=dict(request.query_params)
    )


@app.post("/api/v1/runs/{path:path}")
async def post_runs_v1(path: str, request: Request):
    """Backward compatible POST runs request."""
    body = await request.body()
    return forward_request(
        method="POST",
        service_url=RUNNING_TRAINER_URL,
        path=f"/api/v1/runs/{path}",
        headers=dict(request.headers),
        body=body
    )


@app.post("/api/v1/runs")
async def create_run_v1(request: Request):
    """Backward compatible create run request."""
    body = await request.body()
    return forward_request(
        method="POST",
        service_url=RUNNING_TRAINER_URL,
        path="/api/v1/runs",
        headers=dict(request.headers),
        body=body
    )
