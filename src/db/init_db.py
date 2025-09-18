"""
Script para inicializar la base de datos con datos de ejemplo
"""
from sqlalchemy.orm import Session
from .database import engine, SessionLocal
from .models import Base, Producto, Usuario
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_sample_products(db: Session):
    """Crear productos de ejemplo en la base de datos"""
    productos_ejemplo = [
        {
            "codigo_barra": "7501000673209",
            "nombre": "Coca Cola 600ml",
            "precio": 1.25,
            "descripcion": "Refresco de cola, botella de 600ml",
            "stock": 50,
            "categoria": "Bebidas"
        },
        {
            "codigo_barra": "7501000673308",
            "nombre": "Pepsi 600ml",
            "precio": 1.20,
            "descripcion": "Refresco de cola, botella de 600ml",
            "stock": 30,
            "categoria": "Bebidas"
        },
        {
            "codigo_barra": "7501000125643",
            "nombre": "Leche Entera Lala 1L",
            "precio": 1.50,
            "descripcion": "Leche pasteurizada entera, envase de 1 litro",
            "stock": 25,
            "categoria": "Lácteos"
        },
        {
            "codigo_barra": "7501000673001",
            "nombre": "Pan Bimbo Blanco",
            "precio": 0.85,
            "descripcion": "Pan de caja blanco, grande",
            "stock": 15,
            "categoria": "Panadería"
        },
        {
            "codigo_barra": "7501000673456",
            "nombre": "Huevos San Juan 12pz",
            "precio": 2.10,
            "descripcion": "Huevos blancos, paquete de 12 piezas",
            "stock": 40,
            "categoria": "Proteínas"
        },
        {
            "codigo_barra": "7501000673789",
            "nombre": "Aceite Capullo 1L",
            "precio": 3.50,
            "descripcion": "Aceite vegetal comestible, botella de 1 litro",
            "stock": 20,
            "categoria": "Aceites"
        },
        {
            "codigo_barra": "7501000673912",
            "nombre": "Arroz Verde Valle 1kg",
            "precio": 1.80,
            "descripcion": "Arroz blanco grano largo, bolsa de 1kg",
            "stock": 35,
            "categoria": "Granos"
        },
        {
            "codigo_barra": "7501000674123",
            "nombre": "Frijoles La Costeña 560g",
            "precio": 1.25,
            "descripcion": "Frijoles negros enteros, lata de 560g",
            "stock": 28,
            "categoria": "Enlatados"
        }
    ]
    
    for producto_data in productos_ejemplo:
        # Verificar si el producto ya existe
        existing = db.query(Producto).filter(
            Producto.codigo_barra == producto_data["codigo_barra"]
        ).first()
        
        if not existing:
            producto = Producto(**producto_data)
            db.add(producto)
    
    db.commit()
    print("✅ Productos de ejemplo creados")


def create_admin_user(db: Session):
    """Crear usuario administrador por defecto"""
    # Verificar si ya existe un usuario admin
    existing_admin = db.query(Usuario).filter(Usuario.username == "admin").first()
    
    if not existing_admin:
        hashed_password = pwd_context.hash("admin123")
        admin_user = Usuario(
            username="admin",
            email="admin@barcodescanner.com",
            hashed_password=hashed_password
        )
        db.add(admin_user)
        db.commit()
        print("✅ Usuario administrador creado (username: admin, password: admin123)")
    else:
        print("ℹ️ Usuario administrador ya existe")


def init_database():
    """Inicializar la base de datos con datos de ejemplo"""
    print("🔧 Iniciando configuración de base de datos...")
    
    # Crear todas las tablas
    Base.metadata.create_all(bind=engine)
    print("✅ Tablas de base de datos creadas")
    
    # Crear sesión
    db = SessionLocal()
    
    try:
        # Crear productos de ejemplo
        create_sample_products(db)
        
        # Crear usuario administrador
        create_admin_user(db)
        
        print("🎉 Base de datos inicializada correctamente")
        
    except Exception as e:
        print(f"❌ Error al inicializar base de datos: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    init_database()