from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime


class ProductoBase(BaseModel):
    """Schema base para Producto"""
    nombre: str
    precio: float
    descripcion: Optional[str] = None
    stock: int = 0
    categoria: Optional[str] = None
    
    @validator('precio')
    def precio_debe_ser_positivo(cls, v):
        if v <= 0:
            raise ValueError('El precio debe ser mayor a 0')
        return v
    
    @validator('stock')
    def stock_no_negativo(cls, v):
        if v < 0:
            raise ValueError('El stock no puede ser negativo')
        return v


class ProductoCreate(ProductoBase):
    """Schema para crear producto"""
    codigo_barra: str


class ProductoUpdate(ProductoBase):
    """Schema para actualizar producto - todos los campos opcionales"""
    nombre: Optional[str] = None
    precio: Optional[float] = None
    stock: Optional[int] = None


class Producto(ProductoBase):
    """Schema para respuesta de producto"""
    codigo_barra: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class EscaneoResponse(BaseModel):
    """Schema para respuesta de escaneo"""
    codigo_barra: str
    tipo_codigo: str
    encontrado: bool
    producto: Optional[Producto] = None
    timestamp: datetime
    
    class Config:
        from_attributes = True


class EscaneoHistorialResponse(BaseModel):
    """Schema para historial de escaneos"""
    id: int
    codigo_barra: str
    timestamp: datetime
    tipo_codigo: Optional[str] = None
    encontrado: bool
    
    class Config:
        from_attributes = True


class UsuarioBase(BaseModel):
    """Schema base para Usuario"""
    username: str
    email: str


class UsuarioCreate(UsuarioBase):
    """Schema para crear usuario"""
    password: str


class Usuario(UsuarioBase):
    """Schema para respuesta de usuario"""
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    """Schema para token JWT"""
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Schema para datos del token"""
    username: Optional[str] = None


class ErrorResponse(BaseModel):
    """Schema para respuestas de error"""
    error: str
    detail: Optional[str] = None