# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
