import os
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from contextlib import asynccontextmanager

from ..db.database import create_tables
from ..db.init_db import init_database
from .routes import productos, scanner, auth, usb_scanner, printer

# Configurar logging
logging.basicConfig(
    level=getattr(logging, os.getenv("LOG_LEVEL", "INFO")),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Configurar eventos de inicio y cierre de la aplicación"""
    # Startup
    logger.info("🚀 Iniciando API Escáner de Códigos de Barras...")
    
    try:
        # Crear tablas de base de datos
        create_tables()
        logger.info("✅ Tablas de base de datos verificadas")
        
        # Inicializar con datos de ejemplo si es la primera vez
        init_database()
        logger.info("✅ Base de datos inicializada")
        
    except Exception as e:
        logger.error(f"❌ Error durante inicialización: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("🔄 Cerrando aplicación...")


# Crear aplicación FastAPI
app = FastAPI(
    title="API Escáner de Códigos de Barras",
    description="""
    API para escanear códigos de barras y gestionar productos.
    
    ## Características principales:
    
    * **Escaneo de códigos**: Escanea códigos EAN-13, QR y más desde cámara o imagen
    * **Gestión de productos**: CRUD completo para productos
    * **Autenticación**: Sistema JWT para endpoints protegidos
    * **Historial**: Registro de todos los escaneos realizados
    
    ## Cómo usar:
    
    1. **Obtener productos**: `GET /productos/` - No requiere autenticación
    2. **Escanear desde imagen**: `POST /scan/image` - Sube una imagen
    3. **Escanear desde cámara**: `POST /scan/camera` - Requiere cámara USB
    4. **Autenticarse**: `POST /auth/login` - Para endpoints protegidos
    5. **Gestionar productos**: Crear, actualizar, eliminar (requiere auth)
    
    ## Conectar hardware:
    
    - Conecta una cámara USB (webcam)
    - Verifica estado con `GET /scan/camera/status`
    - ¡Ya puedes escanear códigos reales!
    """,
    version="1.0.0",
    lifespan=lifespan
)

# Configurar CORS para permitir peticiones desde frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir rutas
app.include_router(productos.router, prefix="/api/v1")
app.include_router(scanner.router, prefix="/api/v1")
app.include_router(usb_scanner.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1")
app.include_router(printer.router, prefix="/api/v1")


@app.get("/")
async def root():
    """Redireccionar a la documentación de la API"""
    return RedirectResponse(url="/docs")


@app.get("/health")
async def health_check():
    """Endpoint para verificar el estado de la API"""
    return {
        "status": "healthy",
        "message": "API Escáner de Códigos de Barras funcionando correctamente",
        "version": "1.0.0"
    }


@app.get("/api/v1")
async def api_info():
    """Información sobre la API"""
    return {
        "name": "API Escáner de Códigos de Barras",
        "version": "1.0.0",
        "description": "API para escanear códigos de barras y gestionar productos",
        "endpoints": {
            "productos": "/api/v1/productos",
            "scanner": "/api/v1/scan",
            "usb_scanner": "/api/v1/usb-scanner",
            "auth": "/api/v1/auth",
            "printer": "/api/v1/printer",
            "docs": "/docs",
            "health": "/health"
        }
    }


# Manejador de errores global
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Manejo global de errores"""
    logger.error(f"Error no manejado: {exc}")
    return HTTPException(
        status_code=500,
        detail={"error": "Error interno del servidor", "detail": str(exc)}
    )


if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True,
        log_level=os.getenv("LOG_LEVEL", "info").lower()
    )