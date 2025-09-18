from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ...db.database import get_db
from ...db.models import Producto as ProductoModel
from ..schemas import Producto, ProductoCreate, ProductoUpdate, ErrorResponse
from ..auth import get_current_active_user

router = APIRouter(prefix="/productos", tags=["productos"])


@router.get("/", response_model=List[Producto])
async def listar_productos(
    skip: int = 0,
    limit: int = 100,
    categoria: str = None,
    db: Session = Depends(get_db)
):
    """Obtener lista de productos con filtros opcionales"""
    query = db.query(ProductoModel)
    
    if categoria:
        query = query.filter(ProductoModel.categoria == categoria)
    
    productos = query.offset(skip).limit(limit).all()
    return productos


@router.get("/{codigo_barra}", response_model=Producto)
async def obtener_producto(
    codigo_barra: str,
    db: Session = Depends(get_db)
):
    """Obtener producto por código de barras"""
    producto = db.query(ProductoModel).filter(
        ProductoModel.codigo_barra == codigo_barra
    ).first()
    
    if producto is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "Producto no encontrado", "codigo_barra": codigo_barra}
        )
    
    return producto


@router.post("/", response_model=Producto, status_code=status.HTTP_201_CREATED)
async def crear_producto(
    producto: ProductoCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Crear nuevo producto (requiere autenticación)"""
    # Verificar si el código de barras ya existe
    existing_producto = db.query(ProductoModel).filter(
        ProductoModel.codigo_barra == producto.codigo_barra
    ).first()
    
    if existing_producto:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "El código de barras ya existe", "codigo_barra": producto.codigo_barra}
        )
    
    db_producto = ProductoModel(**producto.dict())
    db.add(db_producto)
    db.commit()
    db.refresh(db_producto)
    
    return db_producto


@router.put("/{codigo_barra}", response_model=Producto)
async def actualizar_producto(
    codigo_barra: str,
    producto_update: ProductoUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Actualizar producto existente (requiere autenticación)"""
    producto = db.query(ProductoModel).filter(
        ProductoModel.codigo_barra == codigo_barra
    ).first()
    
    if producto is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "Producto no encontrado", "codigo_barra": codigo_barra}
        )
    
    # Actualizar solo campos proporcionados
    update_data = producto_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(producto, field, value)
    
    db.commit()
    db.refresh(producto)
    
    return producto


@router.delete("/{codigo_barra}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_producto(
    codigo_barra: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Eliminar producto (requiere autenticación)"""
    producto = db.query(ProductoModel).filter(
        ProductoModel.codigo_barra == codigo_barra
    ).first()
    
    if producto is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "Producto no encontrado", "codigo_barra": codigo_barra}
        )
    
    db.delete(producto)
    db.commit()
    
    return None


@router.get("/categorias/", response_model=List[str])
async def obtener_categorias(db: Session = Depends(get_db)):
    """Obtener lista única de categorías"""
    categorias = db.query(ProductoModel.categoria).distinct().all()
    return [cat[0] for cat in categorias if cat[0]]