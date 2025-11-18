# Auth Service

Simple JWT authentication service with SQLite database.

## Features

- User registration with email and password
- User login with JWT token generation
- Token verification endpoint
- Password hashing with bcrypt
- SQLite database for user storage

## Endpoints

### POST /register
Register a new user.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "securepassword"
}
```

**Response (201):**
```json
{
  "user_id": "uuid-here",
  "email": "user@example.com"
}
```

### POST /login
Login and receive JWT token.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "securepassword"
}
```

**Response (200):**
```json
{
  "token": "jwt-token-here",
  "user_id": "uuid-here"
}
```

### GET /verify
Verify JWT token validity.

**Headers:**
```
Authorization: Bearer <jwt-token>
```

**Response (200):**
```json
{
  "user_id": "uuid-here",
  "valid": true
}
```

### GET /health
Health check endpoint.

**Response (200):**
```json
{
  "status": "ok",
  "service": "Auth Service"
}
```

## Local Development

### Run with Python
```bash
cd services/auth
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Access at: http://localhost:8000

### Run with Docker
```bash
docker build -t auth-service .
docker run -p 8004:8000 -e JWT_SECRET=your-secret auth-service
```

Access at: http://localhost:8004

## Environment Variables

- `JWT_SECRET` - Secret key for JWT token signing (default: "dev-secret-change-in-production")

## Database

Uses SQLite database stored as `auth.db` in the application directory.

## Testing

```bash
# Register user
curl -X POST http://localhost:8004/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"password"}'

# Login
curl -X POST http://localhost:8004/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"password"}'

# Verify token (use token from login response)
curl http://localhost:8004/verify \
  -H "Authorization: Bearer <your-token-here>"
```

## API Documentation

Interactive API documentation available at:
- Swagger UI: http://localhost:8004/docs
- ReDoc: http://localhost:8004/redoc
