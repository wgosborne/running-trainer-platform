"""
PDF Import Service - Imports training plans from PDF files.

This service parses training plan PDFs and creates workouts in the
Running Trainer Service via API calls.
"""

import logging
import os
from datetime import datetime
from typing import Annotated

import requests
from fastapi import FastAPI, UploadFile, File, Header, HTTPException, Query
from pydantic import BaseModel

from parser import extract_workouts_from_pdf

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="PDF Import Service",
    description="Import training plans from PDF files",
    version="1.0.0"
)

# Configuration
RUNNING_TRAINER_URL = os.getenv("RUNNING_TRAINER_URL", "http://localhost:8001")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")


# Pydantic models
class ImportResponse(BaseModel):
    """Response model for PDF import."""
    status: str
    workouts_created: int
    workouts_failed: int
    plan_id: str


@app.on_event("startup")
def startup_event():
    """Log startup information."""
    logger.info("PDF Import Service started")
    logger.info(f"Running Trainer URL: {RUNNING_TRAINER_URL}")


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "ok", "service": "PDF Import Service"}


@app.post("/import/pdf", response_model=ImportResponse)
async def import_pdf(
    file: Annotated[UploadFile, File(description="PDF file to import")],
    plan_id: Annotated[str, Query(description="Training plan ID (UUID)")],
    plan_start_date: Annotated[str, Query(description="Plan start date (YYYY-MM-DD)")],
    authorization: Annotated[str | None, Header()] = None
) -> ImportResponse:
    """
    Import workouts from PDF file.

    Args:
        file: PDF file upload
        plan_id: UUID of the training plan
        plan_start_date: Start date of the plan (YYYY-MM-DD format)
        authorization: Bearer token for authentication

    Returns:
        Import status with counts

    Raises:
        HTTPException: If PDF parsing fails or authentication is missing
    """
    # Validate authorization header
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header required")

    # Validate file type
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="File must be a PDF")

    logger.info(f"Starting PDF import for plan {plan_id}")
    logger.info(f"Plan start date: {plan_start_date}")
    logger.info(f"Uploaded file: {file.filename}")

    try:
        # Parse plan start date
        try:
            start_date = datetime.fromisoformat(plan_start_date)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid date format. Use YYYY-MM-DD"
            )

        # Read PDF file
        pdf_bytes = await file.read()
        logger.info(f"Read {len(pdf_bytes)} bytes from PDF")

        # Extract workouts from PDF
        workouts = extract_workouts_from_pdf(pdf_bytes, start_date)

        if not workouts:
            logger.warning("No workouts extracted from PDF")
            raise HTTPException(
                status_code=400,
                detail="Failed to extract workouts from PDF. Check PDF format."
            )

        logger.info(f"Extracted {len(workouts)} workouts from PDF")

        # Create workouts in Running Trainer Service
        workouts_created = 0
        workouts_failed = 0

        for workout in workouts:
            try:
                # Prepare workout data for API
                workout_data = {
                    "name": workout["name"],
                    "workout_type": workout["workout_type"],
                    "planned_distance": workout["planned_distance"],
                    "scheduled_date": workout["scheduled_date"],
                }

                # Add pace range if available
                if workout.get("target_pace_min_sec") and workout.get("target_pace_max_sec"):
                    workout_data["target_pace_min_sec"] = workout["target_pace_min_sec"]
                    workout_data["target_pace_max_sec"] = workout["target_pace_max_sec"]

                # Call Running Trainer API - plan_id goes in URL path, NOT in body
                url = f"{RUNNING_TRAINER_URL}/api/v1/plans/{plan_id}/workouts"
                headers = {"Authorization": authorization}

                response = requests.post(url, json=workout_data, headers=headers, timeout=10)

                if response.status_code == 201:
                    workouts_created += 1
                    logger.debug(f"Created workout: {workout['name']}")
                else:
                    workouts_failed += 1
                    logger.error(
                        f"Failed to create workout: {workout['name']} - "
                        f"Status: {response.status_code}, Response: {response.text}"
                    )

            except requests.exceptions.RequestException as e:
                workouts_failed += 1
                logger.error(f"Failed to create workout: {workout['name']} - Error: {str(e)}")
            except Exception as e:
                workouts_failed += 1
                logger.error(f"Unexpected error creating workout: {workout['name']} - {str(e)}")

        logger.info(
            f"PDF import complete. Created: {workouts_created}, Failed: {workouts_failed}"
        )

        return ImportResponse(
            status="success",
            workouts_created=workouts_created,
            workouts_failed=workouts_failed,
            plan_id=plan_id
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"PDF import failed: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=f"PDF import failed: {str(e)}"
        )
