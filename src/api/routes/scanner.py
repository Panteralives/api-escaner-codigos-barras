import os
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
from sqlalchemy.orm import Session

from ...db.database import get_db
from ...db.models import Producto as ProductoModel, EscaneoHistorial
from ...scanner.barcode_scanner import BarcodeScanner
from ..schemas import EscaneoResponse, Producto

router = APIRouter(prefix="/scan", tags=["scanner"])

# Instancia global del escáner (se inicializa al primer uso)
scanner = None


def get_scanner() -> BarcodeScanner:
    """Obtener instancia del escáner (singleton)"""
    global scanner
    if scanner is None:
        camera_index = int(os.getenv("DEFAULT_CAMERA_INDEX", "0"))
        scanner = BarcodeScanner(camera_index=camera_index)
    return scanner


@router.post("/image", response_model=EscaneoResponse)
async def scan_from_image(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Escanear código de barras desde imagen subida
    
    Acepta imágenes en formato JPG, PNG, etc.
    """
    # Validar tipo de archivo
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "El archivo debe ser una imagen"}
        )
    
    try:
        # Leer bytes de la imagen
        image_bytes = await file.read()
        
        # Escanear código
        scanner_instance = get_scanner()
        result = scanner_instance.scan_from_image_bytes(image_bytes)
        
        if result is None:
            # No se encontró código
            return EscaneoResponse(
                codigo_barra="",
                tipo_codigo="",
                encontrado=False,
                producto=None,
                timestamp=datetime.now()
            )
        
        codigo_barra, tipo_codigo = result
        
        # Buscar producto en base de datos
        producto = db.query(ProductoModel).filter(
            ProductoModel.codigo_barra == codigo_barra
        ).first()
        
        # Guardar en historial
        historial = EscaneoHistorial(
            codigo_barra=codigo_barra,
            tipo_codigo=tipo_codigo,
            encontrado=1 if producto else 0
        )
        db.add(historial)
        db.commit()
        
        return EscaneoResponse(
            codigo_barra=codigo_barra,
            tipo_codigo=tipo_codigo,
            encontrado=bool(producto),
            producto=producto,
            timestamp=datetime.now()
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Error al procesar la imagen", "detail": str(e)}
        )


@router.post("/camera", response_model=EscaneoResponse)
async def scan_from_camera(
    db: Session = Depends(get_db)
):
    """
    Escanear código de barras desde cámara en tiempo real
    
    Requiere que una cámara USB esté conectada al sistema
    """
    scanner_instance = get_scanner()
    
    # Verificar si la cámara está disponible
    if not BarcodeScanner.is_camera_available(scanner_instance.camera_index):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "Cámara no disponible", "camera_index": scanner_instance.camera_index}
        )
    
    try:
        # Inicializar cámara si no está ya inicializada
        if scanner_instance.cap is None or not scanner_instance.cap.isOpened():
            if not scanner_instance.start_camera():
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail={"error": "No se pudo inicializar la cámara"}
                )
        
        # Intentar escanear (múltiples intentos para mejor detección)
        max_attempts = 10
        for attempt in range(max_attempts):
            result = scanner_instance.scan_from_camera()
            
            if result is not None:
                codigo_barra, tipo_codigo = result
                
                # Buscar producto en base de datos
                producto = db.query(ProductoModel).filter(
                    ProductoModel.codigo_barra == codigo_barra
                ).first()
                
                # Guardar en historial
                historial = EscaneoHistorial(
                    codigo_barra=codigo_barra,
                    tipo_codigo=tipo_codigo,
                    encontrado=1 if producto else 0
                )
                db.add(historial)
                db.commit()
                
                return EscaneoResponse(
                    codigo_barra=codigo_barra,
                    tipo_codigo=tipo_codigo,
                    encontrado=bool(producto),
                    producto=producto,
                    timestamp=datetime.now()
                )
        
        # No se encontró código después de todos los intentos
        return EscaneoResponse(
            codigo_barra="",
            tipo_codigo="",
            encontrado=False,
            producto=None,
            timestamp=datetime.now()
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Error al escanear desde cámara", "detail": str(e)}
        )


@router.get("/camera/status")
async def camera_status():
    """
    Verificar estado de la cámara
    """
    camera_index = int(os.getenv("DEFAULT_CAMERA_INDEX", "0"))
    available = BarcodeScanner.is_camera_available(camera_index)
    
    return {
        "camera_index": camera_index,
        "available": available,
        "message": "Cámara disponible" if available else "Cámara no disponible"
    }


@router.post("/camera/stop")
async def stop_camera():
    """
    Detener la cámara y liberar recursos
    """
    global scanner
    if scanner is not None:
        scanner.stop_camera()
    
    return {"message": "Cámara detenida"}