# API Documentation

## Base URL

- Development: `http://localhost:8000`
- Production: Your deployed URL

## Authentication

Currently no authentication is required. Future versions will implement JWT-based authentication.

## Endpoints

### Health Check

#### GET /health

Check if the API is running.

**Response:**
```json
{
  "status": "healthy",
  "app_name": "AI Novel Platform"
}
```

### Novels

#### GET /api/novels

List all novels with pagination.

**Query Parameters:**
- `skip` (int, optional): Number of records to skip (default: 0)
- `limit` (int, optional): Maximum number of records to return (default: 100)

**Response:**
```json
[
  {
    "id": "uuid",
    "title": "My Novel",
    "author": "John Doe",
    "genre": "Fantasy",
    "synopsis": "A great story...",
    "status": "DRAFT",
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-01T00:00:00"
  }
]
```

#### GET /api/novels/{novel_id}

Get a specific novel by ID.

**Response:**
```json
{
  "id": "uuid",
  "title": "My Novel",
  "author": "John Doe",
  "genre": "Fantasy",
  "synopsis": "A great story...",
  "status": "DRAFT",
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:00:00"
}
```

**Error Responses:**
- `404`: Novel not found

#### POST /api/novels

Create a new novel.

**Request Body:**
```json
{
  "title": "My Novel",
  "author": "John Doe",
  "genre": "Fantasy",
  "synopsis": "A great story...",
  "status": "DRAFT"
}
```

**Response:** (201 Created)
```json
{
  "id": "uuid",
  "title": "My Novel",
  "author": "John Doe",
  "genre": "Fantasy",
  "synopsis": "A great story...",
  "status": "DRAFT",
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:00:00"
}
```

#### PUT /api/novels/{novel_id}

Update an existing novel.

**Request Body:**
```json
{
  "title": "Updated Title",
  "status": "IN_PROGRESS"
}
```

**Response:**
```json
{
  "id": "uuid",
  "title": "Updated Title",
  "author": "John Doe",
  "genre": "Fantasy",
  "synopsis": "A great story...",
  "status": "IN_PROGRESS",
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-02T00:00:00"
}
```

**Error Responses:**
- `404`: Novel not found

#### DELETE /api/novels/{novel_id}

Delete a novel.

**Response:** (204 No Content)

**Error Responses:**
- `404`: Novel not found

### AI Generation

#### POST /api/ai/generate

Generate content using AI.

**Request Body:**
```json
{
  "novel_id": "uuid",
  "prompt": "Write a scene where...",
  "provider": "openai",
  "model_name": "gpt-4",
  "max_tokens": 2000,
  "api_key": "optional-override-key",
  "base_url": "optional-custom-url"
}
```

**Response:**
```json
{
  "content": "Generated text content...",
  "tokens_used": 1500,
  "model": "gpt-4"
}
```

**Supported Providers:**
- `openai`: OpenAI GPT models
- `anthropic`: Anthropic Claude models
- `custom`: Custom API endpoints (OpenAI-compatible)

**Error Responses:**
- `404`: Novel not found
- `500`: AI generation error

## Novel Status Values

- `DRAFT`: Initial draft
- `IN_PROGRESS`: Actively being written
- `COMPLETED`: Writing finished
- `PUBLISHED`: Published/shared

## Rate Limiting

- Root endpoint: 10 requests per minute
- Other endpoints: No limit (development)

Production environments should implement stricter rate limiting.

## Error Format

All errors follow this format:

```json
{
  "detail": "Error message description"
}
```

Common HTTP status codes:
- `200`: Success
- `201`: Created
- `204`: No Content
- `400`: Bad Request
- `404`: Not Found
- `429`: Too Many Requests
- `500`: Internal Server Error

## Interactive Documentation

Visit `/docs` for Swagger UI interactive documentation.
Visit `/redoc` for ReDoc documentation.
