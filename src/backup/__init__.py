"""
Módulo de Backup para POS Avanzado

Este módulo proporciona funcionalidad completa de backup y restauración
para el sistema POS, incluyendo programación automática y gestión de archivos.
"""

# Importaciones básicas sin dependencias problemáticas
try:
    from .backup_manager import BackupManager
except ImportError:
    BackupManager = None

# FastAPI routes (solo si está disponible)
try:
    from .backup_routes_fastapi import backup_router, init_backup_manager
except ImportError:
    backup_router = None
    init_backup_manager = None

__all__ = ['BackupManager', 'backup_router', 'init_backup_manager']
__version__ = '1.0.0'