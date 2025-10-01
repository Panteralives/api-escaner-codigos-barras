import asyncio
import logging
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Optional
import threading
import time

from ...db.database import get_db
from ...db.models import Producto as ProductoModel, EscaneoHistorial
from ...scanner.usb_hid_scanner import get_hid_scanner
from ..schemas import EscaneoResponse, Producto

router = APIRouter(prefix="/usb-scanner", tags=["usb-scanner"])

# Configurar logging
logger = logging.getLogger(__name__)

# Variable global para manejar el estado del scanner
scanner_instance = None
listening_task = None

def get_scanner_instance():
    """Obtener instancia única del scanner USB-HID"""
    global scanner_instance
    if scanner_instance is None:
        scanner_instance = get_hid_scanner()
    return scanner_instance


@router.get("/status")
async def get_scanner_status():
    """
    Obtener estado actual del scanner USB-HID
    """
    try:
        scanner = get_scanner_instance()
        status = scanner.get_status()
        
        return {
            "status": "success",
            "scanner_info": status,
            "message": "Scanner USB-HID disponible" if status['keyboard_library'] else "Librería keyboard no disponible"
        }
    except Exception as e:
        logger.error(f"Error obteniendo estado del scanner: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Error al obtener estado del scanner", "detail": str(e)}
        )


@router.post("/start")
async def start_scanner(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """
    Iniciar la escucha del scanner USB-HID
    """
    try:
        scanner = get_scanner_instance()
        
        # Verificar si ya está escuchando
        if scanner.is_listening:
            return {
                "status": "info",
                "message": "Scanner ya está en funcionamiento",
                "listening": True
            }
        
        # Configurar callback para procesar códigos escaneados
        def on_barcode_scanned(barcode_data: str):
            """Callback que se ejecuta cuando se escanea un código"""
            try:
                logger.info(f"📷 Código detectado por scanner USB: {barcode_data}")
                
                # Buscar producto en base de datos
                with next(get_db()) as db_session:
                    producto = db_session.query(ProductoModel).filter(
                        ProductoModel.codigo_barra == barcode_data
                    ).first()
                    
                    # Guardar en historial
                    historial = EscaneoHistorial(
                        codigo_barra=barcode_data,
                        tipo_codigo="USB-HID",
                        encontrado=1 if producto else 0
                    )
                    db_session.add(historial)
                    db_session.commit()
                    
                    if producto:
                        logger.info(f"✅ Producto encontrado: {producto.nombre}")
                    else:
                        logger.warning(f"⚠️ Producto no encontrado para código: {barcode_data}")
                        
            except Exception as e:
                logger.error(f"Error procesando código escaneado: {e}")
        
        # Configurar callback
        scanner.set_barcode_callback(on_barcode_scanned)
        
        # Iniciar escucha
        success = scanner.start_listening()
        
        if success:
            return {
                "status": "success",
                "message": "Scanner USB-HID iniciado correctamente",
                "listening": True,
                "instructions": [
                    "El scanner está activo y detectará códigos automáticamente",
                    "Simplemente escanea cualquier código de barras",
                    "Los resultados se guardarán en la base de datos"
                ]
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={"error": "No se pudo iniciar el scanner USB-HID"}
            )
            
    except Exception as e:
        logger.error(f"Error iniciando scanner: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Error al iniciar scanner", "detail": str(e)}
        )


@router.post("/stop")
async def stop_scanner():
    """
    Detener la escucha del scanner USB-HID
    """
    try:
        scanner = get_scanner_instance()
        
        if not scanner.is_listening:
            return {
                "status": "info",
                "message": "Scanner ya está detenido",
                "listening": False
            }
        
        scanner.stop_listening()
        
        return {
            "status": "success",
            "message": "Scanner USB-HID detenido correctamente",
            "listening": False
        }
        
    except Exception as e:
        logger.error(f"Error deteniendo scanner: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Error al detener scanner", "detail": str(e)}
        )


@router.post("/test")
async def test_scanner(timeout: int = 30):
    """
    Probar el scanner USB-HID por un tiempo determinado
    
    Args:
        timeout: Tiempo máximo de espera en segundos (default: 30)
    """
    try:
        scanner = get_scanner_instance()
        
        # Realizar prueba
        result = scanner.test_scanner(timeout_seconds=timeout)
        
        if result:
            return {
                "status": "success",
                "message": f"Scanner funcionando correctamente - Código detectado: {result}",
                "barcode_detected": result,
                "test_successful": True
            }
        else:
            return {
                "status": "warning",
                "message": f"No se detectó ningún código durante {timeout} segundos",
                "barcode_detected": None,
                "test_successful": False,
                "suggestions": [
                    "Verifica que el scanner USB esté conectado",
                    "Prueba escanear en el Bloc de notas primero",
                    "Asegúrate de tener permisos de administrador"
                ]
            }
            
    except Exception as e:
        logger.error(f"Error probando scanner: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Error al probar scanner", "detail": str(e)}
        )


@router.get("/recent-scans")
async def get_recent_scans(db: Session = Depends(get_db), limit: int = 10):
    """
    Obtener escaneos recientes del scanner USB-HID
    """
    try:
        # Consultar historial reciente filtrado por tipo USB-HID
        escaneos = db.query(EscaneoHistorial).filter(
            EscaneoHistorial.tipo_codigo == "USB-HID"
        ).order_by(
            EscaneoHistorial.timestamp.desc()
        ).limit(limit).all()
        
        # Formatear resultados
        resultados = []
        for escaneo in escaneos:
            # Buscar información del producto si se encontró
            producto = None
            if escaneo.encontrado:
                producto = db.query(ProductoModel).filter(
                    ProductoModel.codigo_barra == escaneo.codigo_barra
                ).first()
            
            resultados.append({
                "codigo_barra": escaneo.codigo_barra,
                "tipo_codigo": escaneo.tipo_codigo,
                "encontrado": bool(escaneo.encontrado),
                "timestamp": escaneo.timestamp,
                "producto": {
                    "nombre": producto.nombre,
                    "precio": producto.precio,
                    "stock": producto.stock,
                    "categoria": producto.categoria
                } if producto else None
            })
        
        return {
            "status": "success",
            "escaneos": resultados,
            "total": len(resultados)
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo escaneos recientes: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Error al obtener escaneos recientes", "detail": str(e)}
        )


@router.post("/configure")
async def configure_scanner(
    min_length: int = 3,
    max_length: int = 50,
    speed_threshold: float = 100.0
):
    """
    Configurar parámetros del scanner USB-HID
    """
    try:
        scanner = get_scanner_instance()
        
        # Actualizar configuración
        scanner.min_barcode_length = min_length
        scanner.max_barcode_length = max_length  
        scanner.scanner_speed_threshold = speed_threshold
        
        return {
            "status": "success",
            "message": "Configuración actualizada correctamente",
            "configuration": {
                "min_barcode_length": min_length,
                "max_barcode_length": max_length,
                "speed_threshold_ms": speed_threshold
            }
        }
        
    except Exception as e:
        logger.error(f"Error configurando scanner: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Error al configurar scanner", "detail": str(e)}
        )