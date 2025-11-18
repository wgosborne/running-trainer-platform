# PDF Import Service

Service for importing training plans from PDF files and creating workouts in the Running Trainer Service.

## Features

- Parse training plan PDFs
- Extract workout information (day, type, distance, pace)
- Automatically create workouts in Running Trainer Service
- Support for multi-week training plans

## Expected PDF Format

The PDF should contain workout information in the following format:

```
Week 1
Monday | Easy | 8 | 10:00-11:00
Tuesday | Tempo | 6 | 8:30-9:00
Wednesday | Rest | 0 | -
...

Week 2
Monday | Long | 12 | 11:00-12:00
...
```

**Format:** `Day | Workout Type | Distance (km) | Pace Range (MM:SS-MM:SS)`

### Supported Workout Types

- `Easy` - Easy run
- `Tempo` - Tempo run
- `Intervals` - Interval training
- `Long` - Long run
- `Recovery` - Recovery run
- `Race` - Race pace

### Supported Days

- Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, Sunday

## API Endpoints

### POST /import/pdf

Import workouts from a PDF file.

**Request:**
- **File:** PDF file (multipart/form-data)
- **Query Parameters:**
  - `plan_id` (string) - UUID of the training plan
  - `plan_start_date` (string) - Start date in YYYY-MM-DD format
- **Headers:**
  - `Authorization: Bearer <token>` - Authentication token

**Response (200):**
```json
{
  "status": "success",
  "workouts_created": 42,
  "workouts_failed": 0,
  "plan_id": "uuid-here"
}
```

### GET /health

Health check endpoint.

**Response (200):**
```json
{
  "status": "ok",
  "service": "PDF Import Service"
}
```

## Local Development

### Run with Python
```bash
cd services/pdf
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Run with Docker
```bash
docker build -t pdf-service .
docker run -p 8002:8000 \
  -e RUNNING_TRAINER_URL=http://localhost:8001 \
  pdf-service
```

## Environment Variables

- `RUNNING_TRAINER_URL` - URL of the Running Trainer Service (default: http://localhost:8001)
- `LOG_LEVEL` - Logging level (default: INFO)

## Usage Example

```bash
# 1. Create a training plan first (via Running Trainer API)
curl -X POST http://localhost:8001/api/v1/plans \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Marathon Training",
    "start_date": "2025-01-13",
    "end_date": "2025-04-13"
  }'

# 2. Import workouts from PDF
curl -X POST "http://localhost:8002/import/pdf?plan_id=<plan-id>&plan_start_date=2025-01-13" \
  -H "Authorization: Bearer <your-token>" \
  -F "file=@training_plan.pdf"
```

## How It Works

1. **Upload PDF** - Client uploads PDF file with query parameters
2. **Parse PDF** - Service extracts text using pdfplumber
3. **Extract Workouts** - Parses workout information from text
4. **Calculate Dates** - Computes scheduled dates based on plan start date
5. **Create Workouts** - Calls Running Trainer API to create each workout
6. **Return Results** - Returns count of successful and failed creations

## Dependencies

- FastAPI - Web framework
- pdfplumber - PDF text extraction
- requests - HTTP client for API calls
- pydantic - Data validation

## API Documentation

Interactive API documentation available at:
- Swagger UI: http://localhost:8002/docs
- ReDoc: http://localhost:8002/redoc
