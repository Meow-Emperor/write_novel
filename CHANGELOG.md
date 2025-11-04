# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2024-11-04

### Added - Core Features
- 👥 **Character Management System**
  - Complete CRUD API for character management
  - Character model with detailed fields (name, role, personality, background, appearance, relationships)
  - Support for filtering characters by novel
- 📖 **Chapter Blueprint System**
  - Complete CRUD API for chapter management
  - Chapter model with content, word count, status tracking
  - Chapter numbering and ordering support
- 🎭 **Plot Structure System**
  - Complete CRUD API for plot management
  - Plot model supporting main plots, subplots, and story arcs
  - Plot ordering and status tracking
- 🌍 **World Settings Enhancement**
  - Completed world settings integration with novels

### Added - AI Features
- 🤖 **AI Character Generator** - POST `/api/ai/generate-character`
  - Generate detailed character profiles based on role and traits
  - Includes name, appearance, personality, background, motivations, character arc
- 📝 **AI Plot Generator** - POST `/api/ai/generate-plot`
  - Generate main plots, subplots, or plot twists
  - Configurable length (short/medium/long)
  - Context-aware with existing characters and plots
- 📋 **AI Chapter Outline Generator** - POST `/api/ai/generate-chapter-outline`
  - Generate detailed chapter outlines
  - Considers previous chapters for continuity
  - Includes key events, character development, plot advancement
- ✨ **AI Content Expansion** - POST `/api/ai/expand-content`
  - Expand brief content snippets into detailed prose
  - Multiple style options (brief, detailed, dramatic)
  - Context-aware with novel genre and theme

### Added - Admin System
- 🔐 **Complete Admin Authentication System**
  - JWT-based authentication
  - Password hashing with bcrypt
  - Admin model with permissions (is_superuser, is_active)
  - Security module (`app/core/security.py`)
- 👨‍💼 **Admin Management API**
  - POST `/api/admin/register` - Register admin (first is superuser)
  - POST `/api/admin/login` - Login with JWT token
  - GET `/api/admin/me` - Get current admin info
  - GET `/api/admin/admins` - List all admins (superuser only)
  - PUT `/api/admin/admins/{id}` - Update admin
  - DELETE `/api/admin/admins/{id}` - Delete admin (superuser only)
  - GET `/api/admin/stats` - Platform statistics
  - GET `/api/admin/novels` - Admin view of all novels
- 🎨 **Admin Frontend**
  - Admin login page (`AdminLogin.vue`)
  - Admin dashboard (`Admin.vue`)
  - Three main sections: Dashboard, Novel Management, Admin Management
  - Token-based authentication with localStorage
  - Request interceptor for automatic auth header injection

### Added - Infrastructure
- 📦 Database initialization script (`init_db.py`)
- 🚀 One-click setup script (`setup.sh`)
- 🔧 Development start script (`dev-start.sh`)
- 🧪 API testing script (`test_api.sh`)
- 📝 Comprehensive update documentation (`UPDATES.md`)
- 🔑 Environment variable examples for all components
- 🔄 Database relationships with cascade delete

### Fixed
- 🐛 **Docker Compose 500 Error**
  - Fixed SQLite database path to use absolute path
  - Updated to `sqlite:////app/data/ai_novel.db`
  - Added proper volume mapping for database persistence
  - Added health checks to Docker services
- 🔧 **Database Initialization**
  - Automatic table creation on app startup
  - Proper cascade delete for related entities
- 🌐 **CORS Configuration**
  - Added admin routes to CORS origins

### Changed
- 📊 **Novel Model**
  - Added relationships for characters, plots, chapters
  - Cascade delete for all related data
- 🔌 **API Schemas**
  - Enhanced AI schemas with new request types
  - Added admin schemas for authentication and management
- ⚙️ **Configuration**
  - Added SECRET_KEY to settings
  - Updated Docker environment variables
- 🎨 **Frontend Routing**
  - Added admin routes (`/admin`, `/admin/login`)
  - Added auth requirement for admin routes
- 📦 **Models Package**
  - Updated to include Admin, Character, Chapter, Plot models
  - Proper model imports and exports

### Database Schema
- 📋 **New Tables**
  - `admins` - Admin users with authentication
  - `characters` - Character profiles for novels
  - `plots` - Plot structures and story arcs
  - `chapters` - Chapter content and metadata
- 🔗 **Updated Relationships**
  - Novel → Characters (one-to-many)
  - Novel → Plots (one-to-many)
  - Novel → Chapters (one-to-many)
  - Novel → WorldSetting (one-to-one)
  - All with cascade delete support

## [1.1.0] - 2024-11-04

### Added
- 📝 Comprehensive `.gitignore` file for both backend and frontend
- 🔧 Environment variable templates (`.env.example`) for all components
- 📊 Logging system with development and production configurations
- ⚡ API rate limiting using SlowAPI
- 🗄️ Database connection pooling and optimization
- 📈 Database indexes on frequently queried fields
- 🧪 Unit testing framework with pytest
- ✅ Basic test suite for novels API and health endpoints
- 🏥 Health check endpoints with proper status reporting
- 📚 API documentation (API.md)
- 🤝 Contributing guidelines (CONTRIBUTING.md)
- 🚀 Deployment guide (DEPLOYMENT.md)
- ⚡ Performance optimization guide (OPTIMIZATION.md)
- 🛠️ Makefile for common development tasks
- 💾 Simple cache manager for performance optimization
- 🎯 Frontend error handling composables
- 🔄 Loading state management composables
- 🌐 Unified axios request configuration
- 📝 Request/response interceptors for better error handling
- 🔄 Startup and shutdown event handlers

### Changed
- 🔧 Improved database models with indexes and cascade deletes
- 🔍 Enhanced API error handling with detailed logging
- 📊 Better logging throughout API endpoints
- 🔄 Updated main.py with middleware for request logging
- 📦 Enhanced Docker health checks
- 📚 Expanded README with new features and guidelines
- 🏗️ Improved project structure and organization

### Fixed
- 🐛 Database session management and connection leaks
- ⚠️ Error handling consistency across API endpoints
- 🔒 Security improvements with environment variable handling

## [1.0.0] - Initial Release

### Added
- 🎨 Vue 3 + TypeScript frontend
- ⚡ FastAPI backend
- 🗄️ SQLAlchemy ORM with SQLite/PostgreSQL support
- 🔄 Alembic database migrations
- 🤖 Multi-AI provider support (OpenAI, Anthropic, Custom)
- 📚 Novel CRUD operations
- 🌍 World setting data models
- 🎯 Pinia state management
- 🎨 Element Plus UI components
- 🐳 Docker and Docker Compose setup
- 📝 Basic documentation
- 🔧 CORS configuration
- 📋 API routing structure
