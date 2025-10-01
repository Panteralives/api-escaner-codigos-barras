#!/usr/bin/env python3
"""
Advanced POS API - Sistema Completo de Punto de Venta
Incluye autenticación JWT, gestión de ventas, usuarios y reportes
"""

import os
import logging
import time
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.security import HTTPBearer
from contextlib import asynccontextmanager
from sqlalchemy.orm import Session, sessionmaker

from ..db.models_advanced import Base, User, Producto, SystemConfig, UserRole
from ..db.database import get_db_engine
from .routes import auth_advanced, sales, printer
from ..backup import backup_router, init_backup_manager

# Configurar logging
logging.basicConfig(
    level=getattr(logging, os.getenv("LOG_LEVEL", "INFO").upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Configurar base de datos para usar la nueva BD avanzada
DB_NAME = os.getenv("ADVANCED_DB_NAME", "inventario_pos_advanced.db")
engine = get_db_engine()

# Dependency para sesión de DB
def get_db():
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Configurar eventos de inicio y cierre de la aplicación"""
    # Startup
    logger.info("🚀 Iniciando API POS Avanzada...")
    
    try:
        # Verificar que exista la base de datos avanzada
        if not os.path.exists(DB_NAME):
            logger.error(f"❌ Base de datos {DB_NAME} no encontrada")
            logger.info("💡 Ejecuta 'python create_advanced_pos.py' primero")
            raise FileNotFoundError(f"Database {DB_NAME} not found")
        
        # Crear/verificar tablas
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Esquema de base de datos verificado")
        
        # Verificar configuraciones del sistema
        await verify_system_config()
        logger.info("✅ Configuraciones del sistema verificadas")
        
        # Inicializar sistema de backup
        backup_config = {
            'database_path': DB_NAME,
            'backup_dir': 'backups/',
            'max_backups': 30,
            'compress': True,
            'schedule': 'daily',
            'schedule_time': '02:00',
            'include_logs': True
        }
        init_backup_manager(backup_config)
        logger.info("✅ Sistema de backup inicializado")
        
    except Exception as e:
        logger.error(f"❌ Error durante inicialización: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("🔄 Cerrando API POS Avanzada...")


async def verify_system_config():
    """Verificar que existan configuraciones básicas del sistema"""
    db_gen = get_db()
    db = next(db_gen)
    
    try:
        # Verificar configuraciones esenciales
        essential_configs = [
            ("business_name", "INVENTARIO BARRAS"),
            ("tax_rate", "16.00"),
            ("printer_mode", "file")
        ]
        
        for key, default_value in essential_configs:
            config = db.query(SystemConfig).filter_by(key=key).first()
            if not config:
                new_config = SystemConfig(
                    key=key,
                    value=default_value,
                    description=f"Auto-created {key}",
                    category="system"
                )
                db.add(new_config)
                logger.info(f"✅ Configuración creada: {key}")
        
        db.commit()
        
    finally:
        db.close()


# Crear aplicación FastAPI
app = FastAPI(
    title="API POS Avanzada - Inventario Barras",
    description="""
    ## Sistema Completo de Punto de Venta
    
    ### 🛍️ Características principales:
    
    * **Autenticación JWT**: Sistema completo con roles y permisos
    * **Gestión de Ventas**: CRUD completo con items, pagos y auditoría
    * **Gestión de Usuarios**: Admin, Manager, Cajero, Inventario
    * **Reportes y Analytics**: Métricas en tiempo real y históricos
    * **Impresión de Tickets**: ESC/POS con apertura de cajón
    * **Auditoría Completa**: Logs de todas las acciones
    * **Gestión de Clientes**: Programa de lealtad y historial
    * **Backup Automático**: Sistema completo con rotación y compresión
    
    ### 🔐 Autenticación:
    
    1. **Obtener token**: `POST /api/v1/auth/login`
    2. **Usar token**: Incluir en header `Authorization: Bearer <token>`
    
    ### 👥 Usuarios por defecto:
    
    - **admin** / admin123 (Administrador)
    - **manager** / manager123 (Gerente)  
    - **cajero1** / cajero123 (Cajero)
    - **inventario** / inventario123 (Inventario)
    
    ### 🏪 Flujo típico de venta:
    
    1. Autenticarse: `POST /auth/login`
    2. Crear venta: `POST /sales/`
    3. Imprimir ticket: `POST /printer/print-sale`
    
    ⚠️ **Importante**: Cambiar passwords por defecto en producción
    """,
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción especificar dominios
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir rutas
app.include_router(auth_advanced.router, prefix="/api/v1")
app.include_router(sales.router, prefix="/api/v1")
app.include_router(printer.router, prefix="/api/v1")
app.include_router(backup_router, prefix="/api/v1")


@app.get("/")
async def root():
    """Redireccionar a la documentación de la API"""
    return RedirectResponse(url="/docs")


@app.get("/health")
async def health_check():
    """Endpoint para verificar el estado de la API"""
    return {
        "status": "healthy",
        "message": "API POS Avanzada funcionando correctamente",
        "version": "2.0.0",
        "database": DB_NAME
    }


@app.get("/api/v1")
async def api_info():
    """Información sobre la API"""
    return {
        "name": "API POS Avanzada - Inventario Barras",
        "version": "2.0.0",
        "description": "Sistema completo de punto de venta con autenticación JWT",
        "features": [
            "Autenticación JWT con roles",
            "Gestión completa de ventas",
            "Reportes y analytics",
            "Impresión de tickets",
            "Auditoría completa",
            "Gestión de usuarios"
        ],
        "endpoints": {
            "authentication": "/api/v1/auth",
            "sales": "/api/v1/sales",
            "printer": "/api/v1/printer",
            "backup": "/api/v1/backup",
            "docs": "/docs",
            "health": "/health"
        },
        "default_users": {
            "admin": "admin123 (Administrador)",
            "manager": "manager123 (Gerente)",
            "cajero1": "cajero123 (Cajero)",
            "inventario": "inventario123 (Inventario)"
        }
    }


@app.get("/api/v1/system/config")
async def get_system_config(db: Session = Depends(get_db)):
    """Obtener configuraciones del sistema (público)"""
    
    public_configs = db.query(SystemConfig).filter(
        SystemConfig.category.in_(["business", "pos"])
    ).all()
    
    config_dict = {}
    for config in public_configs:
        config_dict[config.key] = {
            "value": config.value,
            "description": config.description
        }
    
    return config_dict


@app.get("/api/v1/stats/overview")
async def get_overview_stats(db: Session = Depends(get_db)):
    """Estadísticas generales del sistema (público)"""
    
    from ..db.models_advanced import Sale, Customer, SaleStatus
    from sqlalchemy import func
    from datetime import datetime, timedelta
    
    # Estadísticas generales
    total_products = db.query(func.count(Producto.id)).scalar()
    total_customers = db.query(func.count(Customer.id)).scalar()
    total_users = db.query(func.count(User.id)).scalar()
    
    # Ventas de hoy
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_sales = db.query(Sale).filter(
        Sale.created_at >= today_start,
        Sale.status == SaleStatus.COMPLETED
    ).all()
    
    today_revenue = sum(sale.total_amount for sale in today_sales)
    
    # Producto más vendido (últimos 30 días)
    thirty_days_ago = datetime.now() - timedelta(days=30)
    from ..db.models_advanced import SaleItem
    
    top_product_query = db.query(
        SaleItem.producto_id,
        func.sum(SaleItem.quantity).label('total_sold'),
        Producto.nombre
    ).join(
        Sale, SaleItem.sale_id == Sale.id
    ).join(
        Producto, SaleItem.producto_id == Producto.id
    ).filter(
        Sale.created_at >= thirty_days_ago,
        Sale.status == SaleStatus.COMPLETED
    ).group_by(
        SaleItem.producto_id, Producto.nombre
    ).order_by(
        func.sum(SaleItem.quantity).desc()
    ).first()
    
    return {
        "system_overview": {
            "total_products": total_products,
            "total_customers": total_customers,
            "total_users": total_users,
            "database": DB_NAME
        },
        "today_stats": {
            "sales_count": len(today_sales),
            "revenue": float(today_revenue),
            "average_ticket": float(today_revenue / len(today_sales)) if today_sales else 0
        },
        "top_product": {
            "name": top_product_query.nombre if top_product_query else None,
            "quantity_sold": int(top_product_query.total_sold) if top_product_query else 0
        }
    }


# Manejador de errores global
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc):
    """Manejo global de errores"""
    logger.error(f"Error no manejado en {request.url}: {exc}")
    return HTTPException(
        status_code=500,
        detail={
            "error": "Error interno del servidor",
            "detail": str(exc),
            "path": str(request.url)
        }
    )


# Middleware de logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Middleware para logging de requests"""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    logger.info(
        f"{request.method} {request.url} - "
        f"Status: {response.status_code} - "
        f"Time: {process_time:.4f}s"
    )
    
    return response


if __name__ == "__main__":
    import uvicorn
    import time
    
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8001"))
    
    print(f"""
    ╔══════════════════════════════════════════════╗
    ║          🏪 API POS AVANZADA v2.0            ║
    ╠══════════════════════════════════════════════╣
    ║  Host: {host:<33} ║
    ║  Port: {port:<33} ║
    ║  DB:   {DB_NAME:<33} ║
    ║                                              ║
    ║  📖 Docs: http://{host}:{port}/docs       ║
    ║  🔐 Login: POST /api/v1/auth/login           ║
    ║                                              ║
    ║  👤 admin/admin123 (Admin)                   ║
    ║  👤 cajero1/cajero123 (Cajero)               ║
    ╚══════════════════════════════════════════════╝
    """)
    
    uvicorn.run(
        "src.api.main_advanced:app",
        host=host,
        port=port,
        reload=True,
        log_level=os.getenv("LOG_LEVEL", "info").lower()
    )