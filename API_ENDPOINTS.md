# API Endpoints Reference

Base URL: `http://localhost:8000`

## 📚 Novel Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/novels/` | List all novels (paginated) |
| GET | `/api/novels/{id}` | Get novel details |
| POST | `/api/novels/` | Create new novel |
| PUT | `/api/novels/{id}` | Update novel |
| DELETE | `/api/novels/{id}` | Delete novel (cascade deletes related data) |

## 👥 Character Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/characters/` | List all characters (filterable by novel_id) |
| GET | `/api/characters/{id}` | Get character details |
| POST | `/api/characters/` | Create new character |
| PUT | `/api/characters/{id}` | Update character |
| DELETE | `/api/characters/{id}` | Delete character |

**Character Fields:**
- `name`, `role`, `description`, `personality`, `background`, `appearance`, `relationships`

## 🎭 Plot Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/plots/` | List all plots (filterable by novel_id) |
| GET | `/api/plots/{id}` | Get plot details |
| POST | `/api/plots/` | Create new plot |
| PUT | `/api/plots/{id}` | Update plot |
| DELETE | `/api/plots/{id}` | Delete plot |

**Plot Fields:**
- `title`, `description`, `plot_type` (main/subplot/arc), `order`, `status`, `notes`

## 📖 Chapter Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/chapters/` | List all chapters (filterable by novel_id) |
| GET | `/api/chapters/{id}` | Get chapter details |
| POST | `/api/chapters/` | Create new chapter |
| PUT | `/api/chapters/{id}` | Update chapter |
| DELETE | `/api/chapters/{id}` | Delete chapter |

**Chapter Fields:**
- `title`, `chapter_number`, `summary`, `content`, `word_count`, `status`, `notes`

## 🌍 World Settings

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/worlds/` | List world settings |

*Note: Complete CRUD endpoints to be implemented*

## 🤖 AI Content Generation

### General Generation
```http
POST /api/ai/generate
Content-Type: application/json

{
  "novel_id": "uuid",
  "prompt": "Your prompt here",
  "context_type": "character|world|plot|content",
  "max_tokens": 2000,
  "provider": "openai",  // optional
  "model_name": "gpt-4"  // optional
}
```

### Character Generation
```http
POST /api/ai/generate-character
Content-Type: application/json

{
  "novel_id": "uuid",
  "character_role": "protagonist|antagonist|supporting",
  "character_traits": "brave, intelligent, kind",  // optional
  "provider": "openai",  // optional
  "model_name": "gpt-4"  // optional
}
```

**Returns:** Complete character profile with:
- Name, Role, Physical Appearance
- Personality Traits, Background Story
- Motivations and Goals
- Character Arc Potential
- Relationships

### Plot Generation
```http
POST /api/ai/generate-plot
Content-Type: application/json

{
  "novel_id": "uuid",
  "plot_type": "main|subplot|twist",
  "plot_length": "short|medium|long",  // optional
  "provider": "openai",  // optional
  "model_name": "gpt-4"  // optional
}
```

**Returns:** Plot outline with:
- Plot Title and Type
- Main Conflict/Hook
- Key Plot Points
- Character Involvement
- Resolution/Climax
- Story Integration

### Chapter Outline Generation
```http
POST /api/ai/generate-chapter-outline
Content-Type: application/json

{
  "novel_id": "uuid",
  "chapter_number": 1,
  "chapter_theme": "awakening",  // optional
  "provider": "openai",  // optional
  "model_name": "gpt-4"  // optional
}
```

**Returns:** Chapter outline with:
- Chapter Title and Summary
- Opening Scene
- Key Events
- Character Development
- Plot Advancement
- Cliffhanger/Transition
- Word Count Estimate

### Content Expansion
```http
POST /api/ai/expand-content
Content-Type: application/json

{
  "novel_id": "uuid",
  "chapter_id": "uuid",
  "content_snippet": "He walked into the dark forest",
  "expansion_style": "brief|detailed|dramatic",  // optional
  "provider": "openai",  // optional
  "model_name": "gpt-4"  // optional
}
```

**Returns:** Expanded content (2-3x original length)

## 🔐 Admin Authentication

### Register Admin
```http
POST /api/admin/register
Content-Type: application/json

{
  "username": "admin",
  "email": "admin@example.com",
  "password": "password123",
  "full_name": "Admin Name",
  "is_superuser": false  // first admin is automatically superuser
}
```

### Login
```http
POST /api/admin/login
Content-Type: application/json

{
  "username": "admin",
  "password": "password123"
}
```

**Returns:**
```json
{
  "access_token": "jwt.token.here",
  "token_type": "bearer"
}
```

### Get Current Admin
```http
GET /api/admin/me
Authorization: Bearer {token}
```

## 👨‍💼 Admin Management (Requires Authentication)

### List Admins (Superuser Only)
```http
GET /api/admin/admins
Authorization: Bearer {token}
```

### Update Admin
```http
PUT /api/admin/admins/{id}
Authorization: Bearer {token}
Content-Type: application/json

{
  "email": "newemail@example.com",
  "full_name": "New Name",
  "password": "newpassword",  // optional
  "is_active": true,
  "is_superuser": false  // requires superuser
}
```

### Delete Admin (Superuser Only)
```http
DELETE /api/admin/admins/{id}
Authorization: Bearer {token}
```

### Platform Statistics
```http
GET /api/admin/stats
Authorization: Bearer {token}
```

**Returns:**
```json
{
  "novels": {
    "total": 10,
    "draft": 3,
    "in_progress": 5,
    "completed": 2,
    "published": 0
  },
  "admins": 2
}
```

### Admin Novel List
```http
GET /api/admin/novels
Authorization: Bearer {token}
```

## 🏥 System Endpoints

### Health Check
```http
GET /health
```

**Returns:**
```json
{
  "status": "healthy",
  "app_name": "AI Novel Platform"
}
```

### Root
```http
GET /
```

**Returns:**
```json
{
  "message": "AI Novel Platform",
  "version": "1.0.0",
  "status": "running"
}
```

## 📝 Common Response Formats

### Success Response (200/201)
```json
{
  "id": "uuid",
  "title": "Novel Title",
  ...fields...
  "created_at": "2024-11-04T12:00:00",
  "updated_at": "2024-11-04T12:00:00"
}
```

### Error Response (4xx/5xx)
```json
{
  "detail": "Error message here"
}
```

### Validation Error (422)
```json
{
  "detail": [
    {
      "loc": ["body", "field_name"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

## 🔒 Authentication

All `/api/admin/*` endpoints (except `/api/admin/register` and `/api/admin/login`) require Bearer token authentication:

```
Authorization: Bearer {your_jwt_token}
```

Get token from `/api/admin/login` response.

## 📊 Pagination

List endpoints support pagination:
- `skip`: Number of records to skip (default: 0)
- `limit`: Maximum records to return (default: 100)

Example:
```
GET /api/novels/?skip=0&limit=10
```

## 🔍 Filtering

Some endpoints support filtering:

**Characters by Novel:**
```
GET /api/characters/?novel_id={uuid}
```

**Plots by Novel:**
```
GET /api/plots/?novel_id={uuid}
```

**Chapters by Novel:**
```
GET /api/chapters/?novel_id={uuid}
```

## 📖 Interactive Documentation

Visit these URLs when the server is running:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

These provide interactive API documentation where you can test endpoints directly.
