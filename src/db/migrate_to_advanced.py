#!/usr/bin/env python3
"""
Script de migración para actualizar la base de datos a la versión avanzada
Migra datos existentes y crea nuevas tablas
"""

import os
import sys
from pathlib import Path

# Agregar el directorio raíz al path
root_dir = Path(__file__).parent.parent.parent
sys.path.append(str(root_dir))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from src.db.models_advanced import Base, User, Producto, SystemConfig, UserRole
from src.db.models import Base as OldBase, Usuario, Producto as OldProducto
from src.db.database import DATABASE_URL, get_db_engine
import bcrypt
from datetime import datetime


def hash_password(password: str) -> str:
    """Hash de password usando bcrypt"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')


def migrate_database():
    """Ejecutar migración completa de base de datos"""
    
    print("🚀 Iniciando migración de base de datos...")
    
    # Crear engine
    engine = get_db_engine()
    
    # Crear todas las tablas nuevas
    print("📊 Creando nuevas tablas...")
    Base.metadata.create_all(bind=engine)
    
    # Crear sesión
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Migrar usuarios existentes
        print("👥 Migrando usuarios existentes...")
        migrate_users(db, engine)
        
        # Migrar productos existentes  
        print("📦 Migrando productos existentes...")
        migrate_products(db, engine)
        
        # Crear configuraciones por defecto
        print("⚙️ Creando configuraciones del sistema...")
        create_default_config(db)
        
        # Crear usuario administrador por defecto
        print("🔐 Creando usuario administrador...")
        create_admin_user(db)
        
        db.commit()
        print("✅ Migración completada exitosamente!")
        
    except Exception as e:
        print(f"❌ Error durante la migración: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def migrate_users(db, engine):
    """Migrar usuarios de tabla antigua a nueva"""
    
    # Obtener usuarios existentes
    with engine.connect() as conn:
        try:
            result = conn.execute(text("SELECT * FROM usuarios"))
            old_users = result.fetchall()
        except Exception:
            print("ℹ️ No se encontraron usuarios existentes para migrar")
            return
    
    for old_user in old_users:
        # Verificar si ya existe
        existing = db.query(User).filter_by(username=old_user.username).first()
        if existing:
            print(f"⚠️ Usuario {old_user.username} ya existe, omitiendo...")
            continue
            
        # Crear nuevo usuario
        new_user = User(
            username=old_user.username,
            email=old_user.email,
            password_hash=old_user.hashed_password,
            full_name=old_user.username.title(),  # Usar username como nombre por defecto
            role=UserRole.ADMIN if old_user.username == 'admin' else UserRole.CASHIER,
            is_active=bool(old_user.is_active),
            created_at=old_user.created_at if hasattr(old_user, 'created_at') else datetime.utcnow()
        )
        
        db.add(new_user)
        print(f"✅ Migrado usuario: {old_user.username}")


def migrate_products(db, engine):
    """Migrar productos de tabla antigua a nueva"""
    
    # Obtener productos existentes usando SQL directo
    with engine.connect() as conn:
        try:
            result = conn.execute(text("SELECT codigo_barra, nombre, precio, descripcion, stock, categoria, created_at, updated_at FROM productos"))
            old_products = result.fetchall()
        except Exception as e:
            print(f"ℹ️ No se encontraron productos existentes para migrar: {e}")
            return
    
    for old_product in old_products:
        # Verificar si ya existe usando SQL directo para evitar conflictos de esquema
        existing_result = db.execute(text("SELECT COUNT(*) FROM productos WHERE codigo_barra = :codigo"), {"codigo": old_product[0]})
        if existing_result.scalar() > 0:
            print(f"⚠️ Producto {old_product[0]} ya existe, omitiendo...")
            continue
            
        # Crear nuevo producto usando SQL directo
        try:
            db.execute(text("""
                INSERT INTO productos (
                    codigo_barra, nombre, descripcion, precio, costo, 
                    stock, categoria, is_active, created_at
                ) VALUES (
                    :codigo_barra, :nombre, :descripcion, :precio, :costo,
                    :stock, :categoria, :is_active, :created_at
                )
            """), {
                'codigo_barra': old_product[0],  # codigo_barra
                'nombre': old_product[1],        # nombre
                'descripcion': old_product[3] if len(old_product) > 3 else None,
                'precio': float(old_product[2]) if old_product[2] else 0.0,
                'costo': 0.0,
                'stock': old_product[4] if len(old_product) > 4 and old_product[4] else 0,
                'categoria': old_product[5] if len(old_product) > 5 else None,
                'is_active': True,
                'created_at': datetime.utcnow()
            })
            
            print(f"✅ Migrado producto: {old_product[1]}")
            
        except Exception as e:
            print(f"⚠️ Error migrando producto {old_product[1]}: {e}")


def create_default_config(db):
    """Crear configuraciones por defecto del sistema"""
    
    default_configs = [
        # Configuración del negocio
        ("business_name", "INVENTARIO BARRAS", "Nombre del negocio", "business"),
        ("business_address", "", "Dirección del negocio", "business"),
        ("business_phone", "", "Teléfono del negocio", "business"),
        ("business_tax_id", "", "RFC/RUC del negocio", "business"),
        
        # Configuración de impresión
        ("printer_mode", "file", "Modo de impresión por defecto", "printer"),
        ("printer_ip", "", "IP de impresora de red", "printer"),
        ("printer_port", "9100", "Puerto de impresora de red", "printer"),
        
        # Configuración fiscal
        ("tax_rate", "16.00", "Tasa de impuesto por defecto (%)", "tax"),
        ("tax_included", "false", "Precios incluyen impuestos", "tax"),
        
        # Configuración de caja
        ("cash_drawer_auto_open", "true", "Abrir cajón automáticamente", "pos"),
        ("require_customer_info", "false", "Requerir información de cliente", "pos"),
        
        # Configuración de backup
        ("backup_enabled", "true", "Backup automático habilitado", "backup"),
        ("backup_frequency", "daily", "Frecuencia de backup", "backup"),
    ]
    
    for key, value, desc, category in default_configs:
        existing = db.query(SystemConfig).filter_by(key=key).first()
        if not existing:
            config = SystemConfig(
                key=key,
                value=value,
                description=desc,
                category=category
            )
            db.add(config)
            print(f"✅ Configuración creada: {key}")


def create_admin_user(db):
    """Crear usuario administrador por defecto si no existe"""
    
    admin_user = db.query(User).filter_by(username="admin").first()
    if not admin_user:
        # Crear usuario admin
        admin = User(
            username="admin",
            email="admin@inventariobarras.com",
            password_hash=hash_password("admin123"),  # Cambiar en producción
            full_name="Administrador del Sistema",
            role=UserRole.ADMIN,
            is_active=True,
            cash_drawer_access=True
        )
        db.add(admin)
        print("✅ Usuario administrador creado (admin/admin123)")
    
    # Crear usuario cajero de prueba
    cashier_user = db.query(User).filter_by(username="cajero").first()
    if not cashier_user:
        cashier = User(
            username="cajero",
            email="cajero@inventariobarras.com", 
            password_hash=hash_password("cajero123"),
            full_name="Cajero de Prueba",
            role=UserRole.CASHIER,
            is_active=True,
            cash_drawer_access=True
        )
        db.add(cashier)
        print("✅ Usuario cajero creado (cajero/cajero123)")


def backup_current_database():
    """Hacer backup de la base de datos actual"""
    
    import shutil
    from datetime import datetime
    
    db_file = "inventario.db"
    if os.path.exists(db_file):
        backup_name = f"inventario_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        shutil.copy2(db_file, backup_name)
        print(f"📦 Backup creado: {backup_name}")


def main():
    """Función principal de migración"""
    
    print("=" * 60)
    print("   MIGRACIÓN DE BASE DE DATOS - SISTEMA POS AVANZADO")
    print("=" * 60)
    
    # Confirmar migración
    response = input("¿Deseas continuar con la migración? (y/N): ")
    if response.lower() != 'y':
        print("❌ Migración cancelada")
        return
    
    try:
        # Hacer backup
        print("\n📦 Creando backup de seguridad...")
        backup_current_database()
        
        # Ejecutar migración
        migrate_database()
        
        print("\n" + "=" * 60)
        print("✅ ¡MIGRACIÓN COMPLETADA EXITOSAMENTE!")
        print("=" * 60)
        print("\n📋 Usuarios creados:")
        print("   - admin / admin123 (Administrador)")
        print("   - cajero / cajero123 (Cajero)")
        print("\n⚠️  IMPORTANTE: Cambiar passwords por defecto en producción")
        
    except Exception as e:
        print(f"\n❌ Error durante la migración: {e}")
        print("💡 El backup puede restaurarse si es necesario")
        sys.exit(1)


if __name__ == "__main__":
    main()