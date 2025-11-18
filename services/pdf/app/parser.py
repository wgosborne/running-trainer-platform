"""
PDF parser for extracting workout data from training plan PDFs.

Supports table-based training plans with weekly schedules.
"""

import logging
import re
from datetime import datetime, timedelta
from io import BytesIO
from typing import List, Dict, Optional

import pdfplumber

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

# Day columns in the table (0-indexed after Week column)
DAY_COLUMNS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]


def parse_week_date(week_str: str) -> Optional[datetime]:
    """
    Parse week start date from string.

    Args:
        week_str: Date string like "21-Jul", "28-Jul", etc.

    Returns:
        datetime object or None if parsing fails
    """
    try:
        # Try parsing "DD-MMM" format (e.g., "21-Jul")
        # Assume current year or infer from context
        current_year = datetime.now().year

        # Parse with current year
        parsed_date = datetime.strptime(f"{week_str}-{current_year}", "%d-%b-%Y")

        # If the parsed date is way in the past (more than 6 months ago), try next year
        if (datetime.now() - parsed_date).days > 180:
            parsed_date = datetime.strptime(f"{week_str}-{current_year + 1}", "%d-%b-%Y")

        return parsed_date
    except (ValueError, AttributeError) as e:
        logger.warning(f"Failed to parse week date '{week_str}': {e}")
        return None


def parse_distance_from_text(text: str) -> Optional[float]:
    """
    Extract distance in miles from workout text.

    Args:
        text: Workout description like "3.5 easy", "5", "4 easy + strides", "cool down to 6 miles"

    Returns:
        Distance in miles or None
    """
    if not text or text.strip().upper() in ["XT", "OFF", "PARTAY"]:
        return None

    try:
        # Clean up the text - remove newlines and normalize spaces
        text = ' '.join(text.split())

        # Look for "to X miles" pattern (e.g., "cool down to 6 miles")
        to_miles_match = re.search(r'to\s+(\d+\.?\d*)\s*(?:miles?|mi)', text, re.IGNORECASE)
        if to_miles_match:
            distance = float(to_miles_match.group(1))
            if 0.5 <= distance <= 25:
                return distance

        # Look for "X miles total" pattern
        total_miles_match = re.search(r'(\d+\.?\d*)\s*(?:miles?|mi)?\s+total', text, re.IGNORECASE)
        if total_miles_match:
            distance = float(total_miles_match.group(1))
            if 0.5 <= distance <= 25:
                return distance

        # Look for "X miles" or "X mi" pattern anywhere
        miles_match = re.search(r'(\d+\.?\d*)\s*(?:miles?|mi)\b', text, re.IGNORECASE)
        if miles_match:
            distance = float(miles_match.group(1))
            if 0.5 <= distance <= 25:
                return distance

        # If text starts with just a number (like "3.5 easy" or "5"), use that
        start_match = re.match(r'^(\d+\.?\d*)\s+', text)
        if start_match:
            distance = float(start_match.group(1))
            if 0.5 <= distance <= 25:
                return distance

        # Last resort: find the first number in the text
        match = re.search(r'(\d+\.?\d*)', text)
        if match:
            distance = float(match.group(1))
            # Sanity check: typical daily run is 1-20 miles
            if 0.5 <= distance <= 25:
                return distance
    except (ValueError, AttributeError):
        pass

    return None


def classify_workout_type(text: str) -> str:
    """
    Classify workout type based on description.

    Args:
        text: Workout description

    Returns:
        Workout type string (must match backend enum: EASY, TEMPO, LONG, SPEED, RECOVERY, CROSS_TRAINING, REST)
    """
    if not text:
        return "REST"

    # Clean up text - join multi-line text
    text = ' '.join(text.split())
    text_lower = text.lower()

    # Cross-training
    if "xt" in text_lower or "cross" in text_lower:
        return "CROSS_TRAINING"

    # Rest day
    if "off" in text_lower or text_lower.strip() == "":
        return "REST"

    # Tempo run (check before easy because "tempo" workouts might contain "easy" in warm-up/cool-down)
    if "tempo" in text_lower or "ghmp" in text_lower:
        return "TEMPO"

    # Speed work / Intervals
    if any(keyword in text_lower for keyword in [
        "interval", " x ", "@", "pace", "min on", "min off",
        "uphill", "5k pace", "10k pace", "400", "800", "1200", "warm-up"
    ]):
        return "SPEED"

    # Long run (typically higher mileage or explicitly labeled)
    if "long" in text_lower:
        return "LONG"

    # Recovery runs
    if "recovery" in text_lower:
        return "RECOVERY"

    # Easy run (most common, check after more specific types)
    if "easy" in text_lower:
        return "EASY"

    # Strides (usually part of easy run)
    if "stride" in text_lower:
        return "EASY"

    # Race
    if "race" in text_lower or "5 mc" in text_lower:
        return "SPEED"

    # Default to easy run
    return "EASY"


def parse_workout_cell(cell_text: str, scheduled_date: datetime) -> Optional[Dict]:
    """
    Parse a single workout cell from the table.

    Args:
        cell_text: Text content of the cell
        scheduled_date: Date this workout is scheduled for

    Returns:
        Workout dictionary or None if it's a rest day or invalid
    """
    if not cell_text or not cell_text.strip():
        return None

    # Clean up cell text - join multi-line text and normalize spaces
    cell_text = ' '.join(cell_text.split())

    # Skip rest days and cross-training (for now)
    if cell_text.upper() in ["OFF", "PARTAY"]:
        return None

    # Skip pure cross-training for now (no distance to track)
    if cell_text.upper() == "XT" or cell_text.upper().startswith("XT +"):
        return None

    # Extract distance
    distance = parse_distance_from_text(cell_text)

    # Skip if no distance found (e.g., pure strength training)
    if distance is None:
        return None

    # Classify workout type
    workout_type = classify_workout_type(cell_text)

    # Create workout name (truncate if too long)
    name = cell_text[:100] if len(cell_text) <= 100 else cell_text[:97] + "..."

    return {
        "name": name,
        "workout_type": workout_type,
        "planned_distance": distance,
        "scheduled_date": scheduled_date.date().isoformat()
    }


def extract_workouts_from_pdf(pdf_bytes: bytes, plan_start_date: datetime) -> List[Dict]:
    """
    Extract workouts from table-based PDF file.

    Args:
        pdf_bytes: PDF file content as bytes
        plan_start_date: Start date of the training plan (can be overridden by PDF dates)

    Returns:
        List of workout dictionaries
    """
    workouts = []

    try:
        with pdfplumber.open(BytesIO(pdf_bytes)) as pdf:
            logger.info(f"Processing PDF with {len(pdf.pages)} pages")

            for page_num, page in enumerate(pdf.pages):
                logger.info(f"Processing page {page_num + 1}")

                # Extract tables from page
                tables = page.extract_tables()

                if not tables:
                    logger.warning(f"No tables found on page {page_num + 1}")
                    continue

                # Process each table
                for table_num, table in enumerate(tables):
                    logger.info(f"Processing table {table_num + 1} with {len(table)} rows")

                    # Skip empty tables
                    if not table or len(table) < 2:
                        continue

                    # Get header row (assumed to be first row)
                    header = table[0]
                    logger.debug(f"Header: {header}")

                    # Find day columns (Monday-Sunday)
                    day_col_indices = {}
                    for idx, col_name in enumerate(header):
                        if col_name:
                            col_lower = col_name.lower().strip()
                            if col_lower in DAY_COLUMNS:
                                day_col_indices[col_lower] = idx

                    logger.info(f"Found {len(day_col_indices)} day columns: {list(day_col_indices.keys())}")

                    # Process data rows
                    for row_num, row in enumerate(table[1:], start=1):
                        if not row or len(row) == 0:
                            continue

                        # First column should be the week start date
                        week_cell = row[0] if len(row) > 0 else None

                        if not week_cell or not week_cell.strip():
                            continue

                        # Try to parse week start date
                        week_start = parse_week_date(week_cell.strip())

                        if not week_start:
                            logger.debug(f"Skipping row {row_num}: could not parse week date '{week_cell}'")
                            continue

                        logger.debug(f"Processing week starting {week_start.date()}")

                        # Process each day column
                        for day_name, day_index in day_col_indices.items():
                            if day_index >= len(row):
                                continue

                            cell_text = row[day_index]

                            if not cell_text or not cell_text.strip():
                                continue

                            # Calculate scheduled date for this day
                            day_offset = DAY_COLUMNS.index(day_name)
                            scheduled_date = week_start + timedelta(days=day_offset)

                            # Parse workout from cell
                            workout = parse_workout_cell(cell_text, scheduled_date)

                            if workout:
                                workouts.append(workout)
                                logger.debug(
                                    f"Added workout: {workout['name'][:50]}... "
                                    f"on {workout['scheduled_date']} "
                                    f"({workout['planned_distance']} mi)"
                                )

        logger.info(f"Successfully extracted {len(workouts)} workouts from PDF")
        return workouts

    except Exception as e:
        logger.error(f"Failed to extract workouts from PDF: {str(e)}", exc_info=True)
        return []
