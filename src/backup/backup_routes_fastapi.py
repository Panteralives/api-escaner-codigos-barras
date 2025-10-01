#!/usr/bin/env python3
"""
FastAPI Routes para Sistema de Backup
Endpoints para gestión de backups desde el frontend
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, List, Optional
from datetime import datetime
import logging
from pathlib import Path

from .backup_manager import BackupManager
from ..api.routes.auth_advanced import get_current_user, require_role
from ..db.models_advanced import User, UserRole

# Crear router
backup_router = APIRouter(prefix="/backup", tags=["backup"])

# Logger
logger = logging.getLogger(__name__)

# Instancia global del BackupManager
backup_manager = None

def init_backup_manager(config: Dict = None):
    """Inicializar el gestor de backups"""
    global backup_manager
    backup_manager = BackupManager(config)
    logger.info("BackupManager inicializado en FastAPI")


# Modelos Pydantic
class BackupCreateRequest(BaseModel):
    type: str = "manual"  # manual, emergency
    description: Optional[str] = ""


class BackupRestoreRequest(BaseModel):
    target_dir: str = "./restored"


class BackupSchedulerRequest(BaseModel):
    schedule: str = "daily"  # daily, hourly, weekly
    schedule_time: str = "02:00"


class BackupConfigRequest(BaseModel):
    max_backups: Optional[int] = None
    compress: Optional[bool] = None
    schedule: Optional[str] = None
    schedule_time: Optional[str] = None
    include_logs: Optional[bool] = None
    email_notifications: Optional[bool] = None


def get_backup_manager():
    """Dependency para obtener el backup manager"""
    if not backup_manager:
        raise HTTPException(
            status_code=500,
            detail="Sistema de backup no inicializado"
        )
    return backup_manager


@backup_router.post("/create")
async def create_backup(
    request: BackupCreateRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    manager: BackupManager = Depends(get_backup_manager)
):
    """
    Crear un nuevo backup
    
    Requiere rol de Manager o Admin
    """
    # Verificar permisos
    if current_user.role not in [UserRole.ADMIN, UserRole.MANAGER]:
        raise HTTPException(
            status_code=403,
            detail="Se requiere rol de Manager o Admin para crear backups"
        )
    
    logger.info(f"Usuario {current_user.username} solicitó creación de backup")
    
    if request.type not in ['manual', 'emergency']:
        raise HTTPException(
            status_code=400,
            detail="Tipo de backup inválido. Use: manual, emergency"
        )
    
    try:
        # Crear backup en background para no bloquear
        def create_backup_task():
            result = manager.create_backup(request.type)
            if result.get('success'):
                logger.info(f"Backup creado exitosamente por usuario {current_user.username}: {result['name']}")
            else:
                logger.error(f"Error creando backup para usuario {current_user.username}: {result.get('error')}")
            return result
        
        # Ejecutar backup inmediatamente (para demo - en producción usar background task)
        result = create_backup_task()
        
        if result.get('success'):
            return {
                'success': True,
                'message': 'Backup creado exitosamente',
                'backup': {
                    'name': result['name'],
                    'type': result['type'],
                    'size_mb': result['size_mb'],
                    'files_count': len(result.get('files', [])),
                    'compressed': result.get('compressed', False),
                    'created_at': result['datetime'],
                    'description': request.description
                }
            }
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Error creando backup: {result.get('error', 'Error desconocido')}"
            )
            
    except Exception as e:
        logger.error(f"Error en create_backup: {e}")
        raise HTTPException(status_code=500, detail=f'Error interno: {str(e)}')


@backup_router.get("/list")
async def list_backups(
    limit: int = 50,
    backup_type: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    manager: BackupManager = Depends(get_backup_manager)
):
    """
    Listar todos los backups disponibles
    
    Requiere rol de Manager o Admin
    """
    if current_user.role not in [UserRole.ADMIN, UserRole.MANAGER]:
        raise HTTPException(
            status_code=403,
            detail="Se requiere rol de Manager o Admin para listar backups"
        )
    
    try:
        backups = manager.list_backups()
        
        # Filtrar por tipo si se especifica
        if backup_type:
            backups = [b for b in backups if b.get('type') == backup_type]
        
        # Limitar resultados
        backups = backups[:limit]
        
        # Formatear respuesta
        formatted_backups = []
        for backup in backups:
            formatted_backups.append({
                'name': backup.get('name'),
                'type': backup.get('type'),
                'size_mb': backup.get('size_mb', 0),
                'files_count': len(backup.get('files', [])),
                'success': backup.get('success', False),
                'compressed': backup.get('compressed', False),
                'created_at': backup.get('datetime'),
                'timestamp': backup.get('timestamp'),
                'error': backup.get('error')
            })
        
        return {
            'success': True,
            'backups': formatted_backups,
            'total': len(formatted_backups)
        }
        
    except Exception as e:
        logger.error(f"Error en list_backups: {e}")
        raise HTTPException(status_code=500, detail=f'Error interno: {str(e)}')


@backup_router.get("/stats")
async def get_backup_stats(
    current_user: User = Depends(get_current_user),
    manager: BackupManager = Depends(get_backup_manager)
):
    """Obtener estadísticas de backups"""
    if current_user.role not in [UserRole.ADMIN, UserRole.MANAGER]:
        raise HTTPException(
            status_code=403,
            detail="Se requiere rol de Manager o Admin para ver estadísticas"
        )
    
    try:
        stats = manager.get_backup_stats()
        return {
            'success': True,
            'stats': stats
        }
        
    except Exception as e:
        logger.error(f"Error en get_backup_stats: {e}")
        raise HTTPException(status_code=500, detail=f'Error interno: {str(e)}')


@backup_router.post("/restore/{backup_name}")
async def restore_backup(
    backup_name: str,
    request: BackupRestoreRequest,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    manager: BackupManager = Depends(get_backup_manager)
):
    """
    Restaurar un backup específico
    
    SOLO ADMIN - Esta operación es peligrosa
    """
    logger.warning(f"Usuario {current_user.username} solicitó restauración de backup: {backup_name}")
    
    try:
        # Validar que el backup existe
        backups = manager.list_backups()
        backup_exists = any(b.get('name') == backup_name for b in backups)
        
        if not backup_exists:
            raise HTTPException(
                status_code=404,
                detail=f'Backup no encontrado: {backup_name}'
            )
        
        # Restaurar backup
        result = manager.restore_backup(backup_name, request.target_dir)
        
        if result.get('success'):
            logger.info(f"Backup restaurado exitosamente por usuario {current_user.username}: {backup_name}")
            return {
                'success': True,
                'message': result['message'],
                'files_restored': len(result.get('files_restored', [])),
                'target_directory': request.target_dir
            }
        else:
            logger.error(f"Error restaurando backup para usuario {current_user.username}: {result['message']}")
            raise HTTPException(
                status_code=500,
                detail=result['message']
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en restore_backup: {e}")
        raise HTTPException(status_code=500, detail=f'Error interno: {str(e)}')


@backup_router.delete("/delete/{backup_name}")
async def delete_backup(
    backup_name: str,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    manager: BackupManager = Depends(get_backup_manager)
):
    """
    Eliminar un backup específico
    
    SOLO ADMIN - Esta operación no se puede deshacer
    """
    logger.warning(f"Usuario {current_user.username} solicitó eliminación de backup: {backup_name}")
    
    try:
        # Buscar y eliminar el backup
        backup_dir = Path(manager.backup_dir)
        deleted = False
        
        # Intentar eliminar archivo ZIP
        zip_path = backup_dir / f"{backup_name}.zip"
        if zip_path.exists():
            zip_path.unlink()
            deleted = True
            logger.info(f"Backup ZIP eliminado: {zip_path}")
        
        # Intentar eliminar directorio
        dir_path = backup_dir / backup_name
        if dir_path.exists() and dir_path.is_dir():
            import shutil
            shutil.rmtree(dir_path)
            deleted = True
            logger.info(f"Backup directorio eliminado: {dir_path}")
        
        if deleted:
            return {
                'success': True,
                'message': f'Backup eliminado: {backup_name}'
            }
        else:
            raise HTTPException(
                status_code=404,
                detail=f'Backup no encontrado: {backup_name}'
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en delete_backup: {e}")
        raise HTTPException(status_code=500, detail=f'Error interno: {str(e)}')


@backup_router.post("/scheduler/start")
async def start_scheduler(
    request: BackupSchedulerRequest,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    manager: BackupManager = Depends(get_backup_manager)
):
    """
    Iniciar el programador automático de backups
    
    SOLO ADMIN
    """
    logger.info(f"Usuario {current_user.username} solicitó iniciar scheduler de backups")
    
    try:
        # Actualizar configuración
        if request.schedule:
            manager.config['schedule'] = request.schedule
        if request.schedule_time:
            manager.config['schedule_time'] = request.schedule_time
        
        # Iniciar scheduler
        manager.start_scheduler()
        
        logger.info(f"Scheduler iniciado por usuario {current_user.username}")
        return {
            'success': True,
            'message': 'Scheduler de backups iniciado',
            'schedule': manager.config.get('schedule'),
            'schedule_time': manager.config.get('schedule_time')
        }
        
    except Exception as e:
        logger.error(f"Error en start_scheduler: {e}")
        raise HTTPException(status_code=500, detail=f'Error interno: {str(e)}')


@backup_router.post("/scheduler/stop")
async def stop_scheduler(
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    manager: BackupManager = Depends(get_backup_manager)
):
    """Detener el programador automático de backups - SOLO ADMIN"""
    logger.info(f"Usuario {current_user.username} solicitó detener scheduler de backups")
    
    try:
        manager.stop_scheduler()
        
        logger.info(f"Scheduler detenido por usuario {current_user.username}")
        return {
            'success': True,
            'message': 'Scheduler de backups detenido'
        }
        
    except Exception as e:
        logger.error(f"Error en stop_scheduler: {e}")
        raise HTTPException(status_code=500, detail=f'Error interno: {str(e)}')


@backup_router.get("/scheduler/status")
async def get_scheduler_status(
    current_user: User = Depends(get_current_user),
    manager: BackupManager = Depends(get_backup_manager)
):
    """Obtener el estado del scheduler de backups"""
    if current_user.role not in [UserRole.ADMIN, UserRole.MANAGER]:
        raise HTTPException(
            status_code=403,
            detail="Se requiere rol de Manager o Admin para ver el scheduler"
        )
    
    try:
        stats = manager.get_backup_stats()
        
        return {
            'success': True,
            'scheduler': {
                'running': stats.get('scheduler_running', False),
                'schedule': manager.config.get('schedule'),
                'schedule_time': manager.config.get('schedule_time'),
                'max_backups': manager.config.get('max_backups'),
                'compress': manager.config.get('compress'),
                'backup_dir': str(manager.backup_dir)
            }
        }
        
    except Exception as e:
        logger.error(f"Error en get_scheduler_status: {e}")
        raise HTTPException(status_code=500, detail=f'Error interno: {str(e)}')


@backup_router.get("/config")
async def get_backup_config(
    current_user: User = Depends(get_current_user),
    manager: BackupManager = Depends(get_backup_manager)
):
    """Obtener configuración actual del sistema de backup"""
    if current_user.role not in [UserRole.ADMIN, UserRole.MANAGER]:
        raise HTTPException(
            status_code=403,
            detail="Se requiere rol de Manager o Admin para ver la configuración"
        )
    
    try:
        return {
            'success': True,
            'config': manager.config
        }
        
    except Exception as e:
        logger.error(f"Error en get_backup_config: {e}")
        raise HTTPException(status_code=500, detail=f'Error interno: {str(e)}')


@backup_router.post("/config")
async def update_backup_config(
    request: BackupConfigRequest,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    manager: BackupManager = Depends(get_backup_manager)
):
    """Actualizar configuración del sistema de backup - SOLO ADMIN"""
    try:
        # Actualizar configuración
        updated_keys = []
        
        for field, value in request.dict(exclude_none=True).items():
            if hasattr(request, field) and value is not None:
                manager.config[field] = value
                updated_keys.append(field)
        
        if updated_keys:
            logger.info(f"Usuario {current_user.username} actualizó configuración de backup: {updated_keys}")
            return {
                'success': True,
                'message': f'Configuración actualizada: {", ".join(updated_keys)}',
                'config': manager.config
            }
        else:
            raise HTTPException(
                status_code=400,
                detail='No se proporcionaron cambios válidos'
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en update_backup_config: {e}")
        raise HTTPException(status_code=500, detail=f'Error interno: {str(e)}')


@backup_router.get("/download/{backup_name}")
async def download_backup(
    backup_name: str,
    current_user: User = Depends(get_current_user),
    manager: BackupManager = Depends(get_backup_manager)
):
    """Descargar un backup específico"""
    if current_user.role not in [UserRole.ADMIN, UserRole.MANAGER]:
        raise HTTPException(
            status_code=403,
            detail="Se requiere rol de Manager o Admin para descargar backups"
        )
    
    logger.info(f"Usuario {current_user.username} solicitó descarga de backup: {backup_name}")
    
    try:
        # Buscar el archivo de backup
        backup_dir = Path(manager.backup_dir)
        zip_path = backup_dir / f"{backup_name}.zip"
        
        if zip_path.exists():
            from fastapi.responses import FileResponse
            return FileResponse(
                path=zip_path,
                filename=f"{backup_name}.zip",
                media_type='application/zip'
            )
        else:
            raise HTTPException(
                status_code=404,
                detail=f'Backup no encontrado: {backup_name}'
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en download_backup: {e}")
        raise HTTPException(status_code=500, detail=f'Error interno: {str(e)}')


# Endpoint para ejecutar backup manual de emergencia
@backup_router.post("/emergency")
async def emergency_backup(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    manager: BackupManager = Depends(get_backup_manager)
):
    """
    Crear backup de emergencia inmediato
    
    Disponible para todos los usuarios autenticados
    """
    logger.warning(f"Usuario {current_user.username} solicitó backup de emergencia")
    
    try:
        # Crear backup de emergencia
        result = manager.create_backup('emergency')
        
        if result.get('success'):
            logger.info(f"Backup de emergencia creado por usuario {current_user.username}: {result['name']}")
            return {
                'success': True,
                'message': 'Backup de emergencia creado exitosamente',
                'backup': {
                    'name': result['name'],
                    'type': result['type'],
                    'size_mb': result['size_mb'],
                    'created_at': result['datetime']
                }
            }
        else:
            logger.error(f"Error en backup de emergencia para usuario {current_user.username}: {result.get('error')}")
            raise HTTPException(
                status_code=500,
                detail=f"Error creando backup de emergencia: {result.get('error', 'Error desconocido')}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en emergency_backup: {e}")
        raise HTTPException(status_code=500, detail=f'Error interno: {str(e)}')