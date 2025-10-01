#!/usr/bin/env python3
"""
API Routes para Sistema de Backup
Endpoints para gestión de backups desde el frontend
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
import logging
from pathlib import Path
from typing import Dict, Any

from .backup_manager import BackupManager

# Crear blueprint
backup_bp = Blueprint('backup', __name__, url_prefix='/api/backup')

# Logger
logger = logging.getLogger(__name__)

# Instancia global del BackupManager (se inicializará en main)
backup_manager = None

def init_backup_manager(config: Dict = None):
    """Inicializar el gestor de backups"""
    global backup_manager
    backup_manager = BackupManager(config)
    logger.info("BackupManager inicializado en rutas API")


@backup_bp.route('/create', methods=['POST'])
@jwt_required()
def create_backup():
    """
    Crear un nuevo backup
    
    Body (JSON):
    {
        "type": "manual|emergency",
        "description": "Descripción opcional"
    }
    """
    try:
        user_id = get_jwt_identity()
        logger.info(f"Usuario {user_id} solicitó creación de backup")
        
        data = request.get_json() or {}
        backup_type = data.get('type', 'manual')
        description = data.get('description', '')
        
        if backup_type not in ['manual', 'emergency']:
            return jsonify({
                'success': False,
                'message': 'Tipo de backup inválido. Use: manual, emergency'
            }), 400
        
        if not backup_manager:
            return jsonify({
                'success': False,
                'message': 'Sistema de backup no inicializado'
            }), 500
        
        # Crear backup
        result = backup_manager.create_backup(backup_type)
        
        if result.get('success'):
            logger.info(f"Backup creado exitosamente por usuario {user_id}: {result['name']}")
            
            response = {
                'success': True,
                'message': 'Backup creado exitosamente',
                'backup': {
                    'name': result['name'],
                    'type': result['type'],
                    'size_mb': result['size_mb'],
                    'files_count': len(result.get('files', [])),
                    'compressed': result.get('compressed', False),
                    'created_at': result['datetime'],
                    'description': description
                }
            }
            return jsonify(response)
        else:
            logger.error(f"Error creando backup para usuario {user_id}: {result.get('error')}")
            return jsonify({
                'success': False,
                'message': f"Error creando backup: {result.get('error', 'Error desconocido')}"
            }), 500
            
    except Exception as e:
        logger.error(f"Error en create_backup: {e}")
        return jsonify({
            'success': False,
            'message': f'Error interno: {str(e)}'
        }), 500


@backup_bp.route('/list', methods=['GET'])
@jwt_required()
def list_backups():
    """
    Listar todos los backups disponibles
    
    Query params:
    - limit: Número máximo de backups a mostrar (default: 50)
    - type: Filtrar por tipo de backup
    """
    try:
        user_id = get_jwt_identity()
        limit = request.args.get('limit', 50, type=int)
        backup_type = request.args.get('type')
        
        if not backup_manager:
            return jsonify({
                'success': False,
                'message': 'Sistema de backup no inicializado'
            }), 500
        
        backups = backup_manager.list_backups()
        
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
        
        return jsonify({
            'success': True,
            'backups': formatted_backups,
            'total': len(formatted_backups)
        })
        
    except Exception as e:
        logger.error(f"Error en list_backups: {e}")
        return jsonify({
            'success': False,
            'message': f'Error interno: {str(e)}'
        }), 500


@backup_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_backup_stats():
    """Obtener estadísticas de backups"""
    try:
        user_id = get_jwt_identity()
        
        if not backup_manager:
            return jsonify({
                'success': False,
                'message': 'Sistema de backup no inicializado'
            }), 500
        
        stats = backup_manager.get_backup_stats()
        
        return jsonify({
            'success': True,
            'stats': stats
        })
        
    except Exception as e:
        logger.error(f"Error en get_backup_stats: {e}")
        return jsonify({
            'success': False,
            'message': f'Error interno: {str(e)}'
        }), 500


@backup_bp.route('/restore/<backup_name>', methods=['POST'])
@jwt_required()
def restore_backup(backup_name: str):
    """
    Restaurar un backup específico
    
    Body (JSON):
    {
        "target_dir": "directorio_destino" (opcional, default: "./restored")
    }
    
    ADVERTENCIA: Esta operación es peligrosa y debe usarse con cuidado
    """
    try:
        user_id = get_jwt_identity()
        logger.warning(f"Usuario {user_id} solicitó restauración de backup: {backup_name}")
        
        data = request.get_json() or {}
        target_dir = data.get('target_dir', './restored')
        
        if not backup_manager:
            return jsonify({
                'success': False,
                'message': 'Sistema de backup no inicializado'
            }), 500
        
        # Validar que el backup existe
        backups = backup_manager.list_backups()
        backup_exists = any(b.get('name') == backup_name for b in backups)
        
        if not backup_exists:
            return jsonify({
                'success': False,
                'message': f'Backup no encontrado: {backup_name}'
            }), 404
        
        # Restaurar backup
        result = backup_manager.restore_backup(backup_name, target_dir)
        
        if result.get('success'):
            logger.info(f"Backup restaurado exitosamente por usuario {user_id}: {backup_name}")
            return jsonify({
                'success': True,
                'message': result['message'],
                'files_restored': len(result.get('files_restored', [])),
                'target_directory': target_dir
            })
        else:
            logger.error(f"Error restaurando backup para usuario {user_id}: {result['message']}")
            return jsonify({
                'success': False,
                'message': result['message']
            }), 500
            
    except Exception as e:
        logger.error(f"Error en restore_backup: {e}")
        return jsonify({
            'success': False,
            'message': f'Error interno: {str(e)}'
        }), 500


@backup_bp.route('/delete/<backup_name>', methods=['DELETE'])
@jwt_required()
def delete_backup(backup_name: str):
    """
    Eliminar un backup específico
    ADVERTENCIA: Esta operación no se puede deshacer
    """
    try:
        user_id = get_jwt_identity()
        logger.warning(f"Usuario {user_id} solicitó eliminación de backup: {backup_name}")
        
        if not backup_manager:
            return jsonify({
                'success': False,
                'message': 'Sistema de backup no inicializado'
            }), 500
        
        # Buscar y eliminar el backup
        backup_dir = Path(backup_manager.backup_dir)
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
            return jsonify({
                'success': True,
                'message': f'Backup eliminado: {backup_name}'
            })
        else:
            return jsonify({
                'success': False,
                'message': f'Backup no encontrado: {backup_name}'
            }), 404
            
    except Exception as e:
        logger.error(f"Error en delete_backup: {e}")
        return jsonify({
            'success': False,
            'message': f'Error interno: {str(e)}'
        }), 500


@backup_bp.route('/scheduler/start', methods=['POST'])
@jwt_required()
def start_scheduler():
    """
    Iniciar el programador automático de backups
    
    Body (JSON):
    {
        "schedule": "daily|hourly|weekly",
        "schedule_time": "HH:MM" (para daily/weekly)
    }
    """
    try:
        user_id = get_jwt_identity()
        logger.info(f"Usuario {user_id} solicitó iniciar scheduler de backups")
        
        data = request.get_json() or {}
        
        if not backup_manager:
            return jsonify({
                'success': False,
                'message': 'Sistema de backup no inicializado'
            }), 500
        
        # Actualizar configuración si se proporciona
        if 'schedule' in data:
            backup_manager.config['schedule'] = data['schedule']
        if 'schedule_time' in data:
            backup_manager.config['schedule_time'] = data['schedule_time']
        
        # Iniciar scheduler
        backup_manager.start_scheduler()
        
        logger.info(f"Scheduler iniciado por usuario {user_id}")
        return jsonify({
            'success': True,
            'message': 'Scheduler de backups iniciado',
            'schedule': backup_manager.config.get('schedule'),
            'schedule_time': backup_manager.config.get('schedule_time')
        })
        
    except Exception as e:
        logger.error(f"Error en start_scheduler: {e}")
        return jsonify({
            'success': False,
            'message': f'Error interno: {str(e)}'
        }), 500


@backup_bp.route('/scheduler/stop', methods=['POST'])
@jwt_required()
def stop_scheduler():
    """Detener el programador automático de backups"""
    try:
        user_id = get_jwt_identity()
        logger.info(f"Usuario {user_id} solicitó detener scheduler de backups")
        
        if not backup_manager:
            return jsonify({
                'success': False,
                'message': 'Sistema de backup no inicializado'
            }), 500
        
        backup_manager.stop_scheduler()
        
        logger.info(f"Scheduler detenido por usuario {user_id}")
        return jsonify({
            'success': True,
            'message': 'Scheduler de backups detenido'
        })
        
    except Exception as e:
        logger.error(f"Error en stop_scheduler: {e}")
        return jsonify({
            'success': False,
            'message': f'Error interno: {str(e)}'
        }), 500


@backup_bp.route('/scheduler/status', methods=['GET'])
@jwt_required()
def get_scheduler_status():
    """Obtener el estado del scheduler de backups"""
    try:
        if not backup_manager:
            return jsonify({
                'success': False,
                'message': 'Sistema de backup no inicializado'
            }), 500
        
        stats = backup_manager.get_backup_stats()
        
        return jsonify({
            'success': True,
            'scheduler': {
                'running': stats.get('scheduler_running', False),
                'schedule': backup_manager.config.get('schedule'),
                'schedule_time': backup_manager.config.get('schedule_time'),
                'max_backups': backup_manager.config.get('max_backups'),
                'compress': backup_manager.config.get('compress'),
                'backup_dir': str(backup_manager.backup_dir)
            }
        })
        
    except Exception as e:
        logger.error(f"Error en get_scheduler_status: {e}")
        return jsonify({
            'success': False,
            'message': f'Error interno: {str(e)}'
        }), 500


@backup_bp.route('/config', methods=['GET', 'POST'])
@jwt_required()
def backup_config():
    """
    GET: Obtener configuración actual del sistema de backup
    POST: Actualizar configuración del sistema de backup
    """
    try:
        user_id = get_jwt_identity()
        
        if not backup_manager:
            return jsonify({
                'success': False,
                'message': 'Sistema de backup no inicializado'
            }), 500
        
        if request.method == 'GET':
            return jsonify({
                'success': True,
                'config': backup_manager.config
            })
        
        elif request.method == 'POST':
            data = request.get_json() or {}
            
            # Actualizar configuración
            valid_keys = [
                'max_backups', 'compress', 'schedule', 
                'schedule_time', 'include_logs', 'email_notifications'
            ]
            
            updated_keys = []
            for key in valid_keys:
                if key in data:
                    backup_manager.config[key] = data[key]
                    updated_keys.append(key)
            
            if updated_keys:
                logger.info(f"Usuario {user_id} actualizó configuración de backup: {updated_keys}")
                return jsonify({
                    'success': True,
                    'message': f'Configuración actualizada: {", ".join(updated_keys)}',
                    'config': backup_manager.config
                })
            else:
                return jsonify({
                    'success': False,
                    'message': 'No se proporcionaron cambios válidos'
                }), 400
        
    except Exception as e:
        logger.error(f"Error en backup_config: {e}")
        return jsonify({
            'success': False,
            'message': f'Error interno: {str(e)}'
        }), 500


@backup_bp.route('/download/<backup_name>', methods=['GET'])
@jwt_required()
def download_backup(backup_name: str):
    """
    Descargar un backup específico
    Nota: Esta ruta debería servir el archivo para descarga
    """
    try:
        user_id = get_jwt_identity()
        logger.info(f"Usuario {user_id} solicitó descarga de backup: {backup_name}")
        
        if not backup_manager:
            return jsonify({
                'success': False,
                'message': 'Sistema de backup no inicializado'
            }), 500
        
        # Buscar el archivo de backup
        backup_dir = Path(backup_manager.backup_dir)
        zip_path = backup_dir / f"{backup_name}.zip"
        
        if zip_path.exists():
            from flask import send_file
            return send_file(
                zip_path,
                as_attachment=True,
                download_name=f"{backup_name}.zip",
                mimetype='application/zip'
            )
        else:
            return jsonify({
                'success': False,
                'message': f'Backup no encontrado: {backup_name}'
            }), 404
            
    except Exception as e:
        logger.error(f"Error en download_backup: {e}")
        return jsonify({
            'success': False,
            'message': f'Error interno: {str(e)}'
        }), 500


# Middleware para logging de todas las operaciones de backup
@backup_bp.before_request
def log_backup_request():
    """Log de todas las peticiones al sistema de backup"""
    if request.endpoint:
        user_id = None
        try:
            from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
            verify_jwt_in_request(optional=True)
            user_id = get_jwt_identity()
        except:
            pass
        
        logger.info(f"Backup API request: {request.method} {request.endpoint} - Usuario: {user_id}")


# Error handler específico para backup
@backup_bp.errorhandler(Exception)
def handle_backup_error(error):
    """Manejo de errores específico para backup"""
    logger.error(f"Error no controlado en backup API: {error}")
    return jsonify({
        'success': False,
        'message': 'Error interno del sistema de backup'
    }), 500