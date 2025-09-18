from sqlalchemy import Column, String, Float, Integer, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()


class Producto(Base):
    """Modelo de producto para la base de datos"""
    __tablename__ = "productos"
    
    codigo_barra = Column(String, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    precio = Column(Float, nullable=False)
    descripcion = Column(Text, nullable=True)
    stock = Column(Integer, default=0)
    categoria = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<Producto(codigo_barra='{self.codigo_barra}', nombre='{self.nombre}')>"


class EscaneoHistorial(Base):
    """Modelo para guardar historial de escaneos"""
    __tablename__ = "escaneo_historial"
    
    id = Column(Integer, primary_key=True, index=True)
    codigo_barra = Column(String, nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    tipo_codigo = Column(String, nullable=True)  # EAN-13, QR, etc.
    encontrado = Column(Integer, default=0)  # 0 = no encontrado, 1 = encontrado
    
    def __repr__(self):
        return f"<EscaneoHistorial(codigo_barra='{self.codigo_barra}', timestamp='{self.timestamp}')>"


class Usuario(Base):
    """Modelo de usuario para autenticación"""
    __tablename__ = "usuarios"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Integer, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<Usuario(username='{self.username}', email='{self.email}')>"