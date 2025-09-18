# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview
This is a complete FastAPI-based barcode scanner application with real hardware integration, authentication, and a Streamlit frontend. The project demonstrates modern Python development practices with computer vision capabilities.

## Technology Stack
- **Backend**: FastAPI + SQLAlchemy + SQLite
- **Computer Vision**: OpenCV + pyzbar
- **Frontend**: Streamlit
- **Authentication**: JWT tokens
- **Testing**: pytest
- **Containerization**: Docker

## Development Commands

### Quick Start
```powershell
# Install dependencies
python run.py --install

# Initialize database
python run.py --init-db

# Run API server
python run.py

# Run frontend (new terminal)
python run.py --frontend

# Check camera hardware
python run.py --check-camera
```

### Testing
```powershell
# Run all tests
python -m pytest tests/ -v

# Run specific test class
python -m pytest tests/test_api.py::TestAuth -v

# Run with coverage
python -m pytest tests/ --cov=src
```

### Database Operations
```powershell
# Initialize/reset database
python run.py --init-db

# Direct database access
sqlite3 barcode_scanner.db
```

### Docker
```powershell
# Build image
docker build -t barcode-scanner-api .

# Run container
docker run -p 8000:8000 barcode-scanner-api
```

### API Development
```powershell
# Start API with auto-reload
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

# Manual API testing
curl http://localhost:8000/health
curl http://localhost:8000/api/v1/productos/
```

## Architecture

### High-Level Structure
```
src/
├── api/                    # FastAPI REST API
│   ├── main.py            # App initialization, middleware, lifespan
│   ├── schemas.py         # Pydantic models for request/response validation
│   ├── auth.py            # JWT authentication and security
│   └── routes/            # API endpoint handlers
│       ├── productos.py   # Product CRUD operations
│       ├── scanner.py     # Barcode scanning endpoints
│       └── auth.py        # Authentication endpoints
├── db/                    # Database layer
│   ├── models.py          # SQLAlchemy ORM models
│   ├── database.py        # DB connection and session management
│   └── init_db.py         # Database initialization with sample data
├── scanner/               # Computer vision module
│   └── barcode_scanner.py # OpenCV + pyzbar integration for real camera scanning
└── frontend/              # Web interface
    └── streamlit_app.py   # Complete Streamlit dashboard
```

### Key Architectural Patterns

**Dependency Injection**: FastAPI's dependency system manages database sessions and authentication
```python
def get_db() -> Session:  # Database dependency
async def get_current_user(...) -> Usuario:  # Auth dependency
```

**Repository Pattern**: Database operations abstracted through SQLAlchemy ORM models

**Service Layer**: Business logic separated in dedicated modules (scanner, auth)

**API Versioning**: All endpoints under `/api/v1/` prefix for future compatibility

### Database Schema
- **productos**: Product catalog with barcode, name, price, stock, category
- **usuarios**: User accounts with hashed passwords
- **escaneo_historial**: Audit trail of all barcode scans

### Hardware Integration
The scanner module provides real-time camera integration:
- Automatic camera detection and initialization
- Multiple barcode format support (EAN-13, QR, etc.)
- Image processing pipeline with OpenCV
- Error handling for camera unavailability

## API Endpoints Reference

### Public Endpoints
- `GET /health` - Health check
- `GET /api/v1/productos/` - List products
- `GET /api/v1/productos/{codigo}` - Get product by barcode
- `POST /api/v1/auth/login` - Authenticate user
- `POST /api/v1/scan/image` - Scan barcode from uploaded image
- `POST /api/v1/scan/camera` - Scan barcode from USB camera
- `GET /api/v1/scan/camera/status` - Check camera availability

### Protected Endpoints (require JWT)
- `POST /api/v1/productos/` - Create product
- `PUT /api/v1/productos/{codigo}` - Update product  
- `DELETE /api/v1/productos/{codigo}` - Delete product
- `GET /api/v1/auth/me` - Get current user info

## Environment Configuration
Key environment variables in `.env`:
- `DATABASE_URL`: SQLite database path
- `SECRET_KEY`: JWT signing key
- `DEFAULT_CAMERA_INDEX`: Camera device index
- `LOG_LEVEL`: Application logging level

## Common Development Tasks

### Adding New Endpoints
1. Define Pydantic schemas in `schemas.py`
2. Create route handlers in appropriate `routes/` file
3. Add authentication dependency if needed
4. Update OpenAPI documentation
5. Add corresponding tests

### Database Changes
1. Modify models in `db/models.py`
2. Update initialization in `init_db.py`
3. Add migration logic if needed
4. Update API schemas and endpoints

### Testing Hardware Integration
1. Use `python run.py --check-camera` to verify camera
2. Test endpoints with real barcodes using `/docs` interface
3. Monitor logs for computer vision processing details

### Frontend Development
The Streamlit app provides a complete web interface with:
- Real-time camera integration
- Product management dashboard
- User authentication flow
- Responsive design with metrics

## Performance Considerations
- Database queries use proper indexing on barcode fields
- Camera resources are managed with singleton pattern
- JWT tokens have configurable expiration
- Image processing is optimized for real-time scanning

## Security Notes
- Passwords are hashed with bcrypt
- JWT tokens include proper expiration
- Protected endpoints validate authorization headers
- File uploads are validated for image types
- Database uses parameterized queries via SQLAlchemy

## Learning Resources
- Full step-by-step tutorial in `docs/GUIA_APRENDIZAJE.md`
- Interactive API documentation at `/docs` when running
- Sample data and test scenarios included
- Hardware setup instructions for camera integration
