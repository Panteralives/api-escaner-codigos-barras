#!/usr/bin/env python3
"""
Sistema de Backup Automático para POS Avanzado
Incluye backup de base de datos, rotación de archivos y compresión
"""

import os
import shutil
import sqlite3
import zipfile
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import schedule
import time
import threading

# Configurar logging específico para backup
backup_logger = logging.getLogger('backup')
backup_handler = logging.FileHandler('backup.log')
backup_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
backup_handler.setFormatter(backup_formatter)
backup_logger.addHandler(backup_handler)
backup_logger.setLevel(logging.INFO)


class BackupManager:
    """Gestor de backups automáticos con rotación y compresión"""
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Inicializar gestor de backups
        
        Args:
            config: Configuración del backup {
                'database_path': 'ruta/base_datos.db',
                'backup_dir': 'ruta/backups/',
                'max_backups': 30,
                'compress': True,
                'schedule': 'daily',  # daily, hourly, weekly
                'schedule_time': '02:00'
            }
        """
        self.config = config or self._default_config()
        self.backup_dir = Path(self.config['backup_dir'])
        self.database_path = Path(self.config['database_path'])
        
        # Crear directorio de backups si no existe
        self.backup_dir.mkdir(exist_ok=True, parents=True)
        
        # Estado del scheduler
        self._scheduler_running = False
        self._scheduler_thread = None
        
        backup_logger.info(f"BackupManager inicializado - Dir: {self.backup_dir}")
    
    def _default_config(self) -> Dict:
        """Configuración por defecto"""
        return {
            'database_path': 'inventario_pos_advanced.db',
            'backup_dir': 'backups/',
            'max_backups': 30,
            'compress': True,
            'schedule': 'daily',
            'schedule_time': '02:00',
            'include_logs': True,
            'email_notifications': False
        }
    
    def create_backup(self, backup_type: str = 'manual') -> Dict:
        """
        Crear backup completo del sistema
        
        Args:
            backup_type: Tipo de backup ('manual', 'scheduled', 'emergency')
            
        Returns:
            Dict con información del backup creado
        """
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_name = f"backup_{backup_type}_{timestamp}"
            
            backup_logger.info(f"Iniciando backup: {backup_name}")
            
            # Crear directorio temporal para el backup
            temp_dir = self.backup_dir / f"temp_{timestamp}"
            temp_dir.mkdir(exist_ok=True)
            
            backup_info = {
                'name': backup_name,
                'type': backup_type,
                'timestamp': timestamp,
                'datetime': datetime.now().isoformat(),
                'files': [],
                'size_mb': 0,
                'success': False,
                'error': None
            }
            
            # 1. Backup de base de datos
            db_backup = self._backup_database(temp_dir)
            backup_info['files'].extend(db_backup['files'])
            
            # 2. Backup de logs si está habilitado
            if self.config.get('include_logs', True):
                logs_backup = self._backup_logs(temp_dir)
                backup_info['files'].extend(logs_backup['files'])
            
            # 3. Backup de configuración
            config_backup = self._backup_config(temp_dir)
            backup_info['files'].extend(config_backup['files'])
            
            # 4. Comprimir si está habilitado
            final_path = None
            if self.config.get('compress', True):
                final_path = self._compress_backup(temp_dir, backup_name)
                backup_info['compressed'] = True
            else:
                final_path = self.backup_dir / backup_name
                shutil.move(str(temp_dir), str(final_path))
                backup_info['compressed'] = False
            
            # Calcular tamaño
            if final_path and final_path.exists():
                if final_path.is_file():
                    backup_info['size_mb'] = round(final_path.stat().st_size / (1024 * 1024), 2)
                else:
                    backup_info['size_mb'] = round(self._get_directory_size(final_path) / (1024 * 1024), 2)
                
                backup_info['path'] = str(final_path)
                backup_info['success'] = True
                
                # Guardar información del backup
                self._save_backup_info(backup_info)
                
                backup_logger.info(f"Backup completado: {backup_name} ({backup_info['size_mb']} MB)")
            
            # Limpiar directorio temporal
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
            
            # Rotar backups antiguos
            self._rotate_backups()
            
            return backup_info
            
        except Exception as e:
            backup_logger.error(f"Error creando backup: {e}")
            backup_info['error'] = str(e)
            return backup_info
    
    def _backup_database(self, backup_dir: Path) -> Dict:
        """Backup de la base de datos SQLite"""
        backup_logger.info("Creando backup de base de datos...")
        
        files = []
        
        if not self.database_path.exists():
            backup_logger.warning(f"Base de datos no encontrada: {self.database_path}")
            return {'files': files}
        
        try:
            # Backup usando SQL VACUUM INTO (más seguro)
            db_backup_path = backup_dir / "database.db"
            
            with sqlite3.connect(str(self.database_path)) as source:
                # Backup completo usando VACUUM INTO
                source.execute(f"VACUUM INTO '{db_backup_path}'")
            
            files.append({
                'name': 'database.db',
                'type': 'database',
                'size_mb': round(db_backup_path.stat().st_size / (1024 * 1024), 2)
            })
            
            backup_logger.info(f"Backup de BD completado: {db_backup_path}")
            
        except Exception as e:
            backup_logger.error(f"Error en backup de BD: {e}")
            # Fallback: copia directa
            try:
                db_backup_path = backup_dir / "database_copy.db"
                shutil.copy2(self.database_path, db_backup_path)
                files.append({
                    'name': 'database_copy.db',
                    'type': 'database_fallback',
                    'size_mb': round(db_backup_path.stat().st_size / (1024 * 1024), 2)
                })
                backup_logger.info("Backup BD completado usando copia directa")
            except Exception as e2:
                backup_logger.error(f"Error en backup BD fallback: {e2}")
        
        return {'files': files}
    
    def _backup_logs(self, backup_dir: Path) -> Dict:
        """Backup de archivos de log"""
        backup_logger.info("Creando backup de logs...")
        
        files = []
        logs_dir = backup_dir / "logs"
        logs_dir.mkdir(exist_ok=True)
        
        # Buscar archivos de log
        log_patterns = ['*.log', '*.txt']
        current_dir = Path('.')
        
        for pattern in log_patterns:
            for log_file in current_dir.glob(pattern):
                if log_file.is_file() and log_file.stat().st_size > 0:
                    dest_file = logs_dir / log_file.name
                    shutil.copy2(log_file, dest_file)
                    
                    files.append({
                        'name': f"logs/{log_file.name}",
                        'type': 'log',
                        'size_mb': round(dest_file.stat().st_size / (1024 * 1024), 4)
                    })
        
        backup_logger.info(f"Backup de logs completado: {len(files)} archivos")
        return {'files': files}
    
    def _backup_config(self, backup_dir: Path) -> Dict:
        """Backup de archivos de configuración"""
        backup_logger.info("Creando backup de configuración...")
        
        files = []
        config_dir = backup_dir / "config"
        config_dir.mkdir(exist_ok=True)
        
        # Archivos de configuración a respaldar
        config_files = [
            'requirements.txt',
            '.env',
            'config.json',
            'printer_config.json'
        ]
        
        current_dir = Path('.')
        
        for config_file in config_files:
            file_path = current_dir / config_file
            if file_path.exists():
                dest_file = config_dir / config_file
                shutil.copy2(file_path, dest_file)
                
                files.append({
                    'name': f"config/{config_file}",
                    'type': 'config',
                    'size_mb': round(dest_file.stat().st_size / (1024 * 1024), 4)
                })
        
        # Información del sistema
        system_info = {
            'backup_created': datetime.now().isoformat(),
            'python_version': os.sys.version,
            'os_info': os.name,
            'backup_config': self.config
        }
        
        system_info_file = config_dir / "system_info.json"
        with open(system_info_file, 'w', encoding='utf-8') as f:
            json.dump(system_info, f, indent=2, ensure_ascii=False)
        
        files.append({
            'name': "config/system_info.json",
            'type': 'system_info',
            'size_mb': round(system_info_file.stat().st_size / (1024 * 1024), 4)
        })
        
        backup_logger.info(f"Backup de configuración completado: {len(files)} archivos")
        return {'files': files}
    
    def _compress_backup(self, backup_dir: Path, backup_name: str) -> Path:
        """Comprimir backup en ZIP"""
        backup_logger.info(f"Comprimiendo backup: {backup_name}")
        
        zip_path = self.backup_dir / f"{backup_name}.zip"
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in backup_dir.rglob('*'):
                if file_path.is_file():
                    # Ruta relativa dentro del ZIP
                    arcname = file_path.relative_to(backup_dir)
                    zipf.write(file_path, arcname)
        
        backup_logger.info(f"Compresión completada: {zip_path}")
        return zip_path
    
    def _get_directory_size(self, directory: Path) -> int:
        """Calcular tamaño total de un directorio"""
        total_size = 0
        for file_path in directory.rglob('*'):
            if file_path.is_file():
                total_size += file_path.stat().st_size
        return total_size
    
    def _save_backup_info(self, backup_info: Dict):
        """Guardar información del backup en un índice"""
        index_file = self.backup_dir / "backup_index.json"
        
        # Cargar índice existente
        if index_file.exists():
            with open(index_file, 'r', encoding='utf-8') as f:
                index = json.load(f)
        else:
            index = {'backups': []}
        
        # Agregar nuevo backup
        index['backups'].append(backup_info)
        index['last_updated'] = datetime.now().isoformat()
        
        # Guardar índice actualizado
        with open(index_file, 'w', encoding='utf-8') as f:
            json.dump(index, f, indent=2, ensure_ascii=False)
    
    def _rotate_backups(self):
        """Eliminar backups antiguos según configuración"""
        max_backups = self.config.get('max_backups', 30)
        backup_logger.info(f"Rotando backups, máximo: {max_backups}")
        
        # Buscar todos los archivos de backup
        backup_files = []
        
        # ZIP files
        for zip_file in self.backup_dir.glob("backup_*.zip"):
            backup_files.append(zip_file)
        
        # Directory backups
        for backup_dir in self.backup_dir.glob("backup_*"):
            if backup_dir.is_dir():
                backup_files.append(backup_dir)
        
        # Ordenar por fecha de modificación (más reciente primero)
        backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        # Eliminar backups excedentes
        for old_backup in backup_files[max_backups:]:
            try:
                if old_backup.is_file():
                    old_backup.unlink()
                else:
                    shutil.rmtree(old_backup)
                backup_logger.info(f"Backup eliminado: {old_backup.name}")
            except Exception as e:
                backup_logger.error(f"Error eliminando backup {old_backup.name}: {e}")
    
    def list_backups(self) -> List[Dict]:
        """Listar todos los backups disponibles"""
        index_file = self.backup_dir / "backup_index.json"
        
        if index_file.exists():
            with open(index_file, 'r', encoding='utf-8') as f:
                index = json.load(f)
                return sorted(index.get('backups', []), 
                            key=lambda x: x.get('datetime', ''), reverse=True)
        
        return []
    
    def restore_backup(self, backup_name: str, target_dir: str = ".") -> Dict:
        """Restaurar un backup específico"""
        backup_logger.info(f"Iniciando restauración: {backup_name}")
        
        result = {
            'success': False,
            'message': '',
            'files_restored': []
        }
        
        try:
            # Buscar el archivo de backup
            backup_path = None
            zip_path = self.backup_dir / f"{backup_name}.zip"
            dir_path = self.backup_dir / backup_name
            
            if zip_path.exists():
                backup_path = zip_path
                is_compressed = True
            elif dir_path.exists():
                backup_path = dir_path
                is_compressed = False
            else:
                result['message'] = f"Backup no encontrado: {backup_name}"
                return result
            
            target_path = Path(target_dir)
            target_path.mkdir(exist_ok=True, parents=True)
            
            if is_compressed:
                # Extraer ZIP
                with zipfile.ZipFile(backup_path, 'r') as zipf:
                    zipf.extractall(target_path)
                    result['files_restored'] = zipf.namelist()
            else:
                # Copiar directorio
                for file_path in backup_path.rglob('*'):
                    if file_path.is_file():
                        rel_path = file_path.relative_to(backup_path)
                        dest_path = target_path / rel_path
                        dest_path.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(file_path, dest_path)
                        result['files_restored'].append(str(rel_path))
            
            result['success'] = True
            result['message'] = f"Backup restaurado exitosamente: {len(result['files_restored'])} archivos"
            backup_logger.info(f"Restauración completada: {backup_name}")
            
        except Exception as e:
            result['message'] = f"Error en restauración: {e}"
            backup_logger.error(f"Error en restauración: {e}")
        
        return result
    
    def start_scheduler(self):
        """Iniciar el programador de backups automáticos"""
        if self._scheduler_running:
            backup_logger.warning("Scheduler ya está ejecutándose")
            return
        
        schedule_type = self.config.get('schedule', 'daily')
        schedule_time = self.config.get('schedule_time', '02:00')
        
        # Limpiar horarios anteriores
        schedule.clear()
        
        # Configurar horario según tipo
        if schedule_type == 'daily':
            schedule.every().day.at(schedule_time).do(self._scheduled_backup)
        elif schedule_type == 'hourly':
            schedule.every().hour.do(self._scheduled_backup)
        elif schedule_type == 'weekly':
            schedule.every().sunday.at(schedule_time).do(self._scheduled_backup)
        
        self._scheduler_running = True
        
        # Ejecutar scheduler en thread separado
        self._scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self._scheduler_thread.start()
        
        backup_logger.info(f"Scheduler iniciado: {schedule_type} a las {schedule_time}")
    
    def stop_scheduler(self):
        """Detener el programador de backups"""
        self._scheduler_running = False
        schedule.clear()
        backup_logger.info("Scheduler detenido")
    
    def _scheduled_backup(self):
        """Ejecutar backup programado"""
        backup_logger.info("Ejecutando backup programado...")
        result = self.create_backup('scheduled')
        
        if result.get('success'):
            backup_logger.info(f"Backup programado completado: {result['name']}")
        else:
            backup_logger.error(f"Error en backup programado: {result.get('error', 'Unknown')}")
    
    def _run_scheduler(self):
        """Bucle principal del scheduler"""
        backup_logger.info("Scheduler thread iniciado")
        
        while self._scheduler_running:
            schedule.run_pending()
            time.sleep(60)  # Verificar cada minuto
        
        backup_logger.info("Scheduler thread terminado")
    
    def get_backup_stats(self) -> Dict:
        """Obtener estadísticas de backups"""
        backups = self.list_backups()
        
        if not backups:
            return {
                'total_backups': 0,
                'total_size_mb': 0,
                'last_backup': None,
                'oldest_backup': None,
                'success_rate': 0
            }
        
        successful = [b for b in backups if b.get('success', False)]
        total_size = sum(b.get('size_mb', 0) for b in backups)
        
        return {
            'total_backups': len(backups),
            'successful_backups': len(successful),
            'total_size_mb': round(total_size, 2),
            'last_backup': backups[0].get('datetime') if backups else None,
            'oldest_backup': backups[-1].get('datetime') if backups else None,
            'success_rate': round((len(successful) / len(backups)) * 100, 1) if backups else 0,
            'scheduler_running': self._scheduler_running
        }


def main():
    """Función principal para ejecutar backup manual"""
    print("=== Sistema de Backup POS Avanzado ===")
    
    backup_manager = BackupManager()
    
    print("\n1. Crear backup manual")
    print("2. Listar backups")
    print("3. Ver estadísticas")
    print("4. Iniciar scheduler automático")
    
    choice = input("\nElige una opción (1-4): ")
    
    if choice == '1':
        print("\n[*] Creando backup...")
        result = backup_manager.create_backup('manual')
        
        if result.get('success'):
            print(f"[OK] Backup creado exitosamente!")
            print(f"   Nombre: {result['name']}")
            print(f"   Archivos: {len(result.get('files', []))}")
            print(f"   Tamaño: {result['size_mb']} MB")
            print(f"   Ruta: {result.get('path', 'N/A')}")
        else:
            print(f"[ERROR] Error creando backup: {result.get('error', 'Unknown')}")
    
    elif choice == '2':
        backups = backup_manager.list_backups()
        print(f"\n📋 Backups disponibles ({len(backups)}):")
        
        for i, backup in enumerate(backups[:10], 1):  # Mostrar solo los 10 más recientes
            status = "✅" if backup.get('success') else "❌"
            print(f"   {i}. {status} {backup['name']} - {backup.get('size_mb', 0)} MB")
    
    elif choice == '3':
        stats = backup_manager.get_backup_stats()
        print(f"\n📊 Estadísticas de Backup:")
        print(f"   Total backups: {stats['total_backups']}")
        print(f"   Exitosos: {stats['successful_backups']}")
        print(f"   Tamaño total: {stats['total_size_mb']} MB")
        print(f"   Tasa de éxito: {stats['success_rate']}%")
        print(f"   Último backup: {stats['last_backup']}")
        print(f"   Scheduler activo: {'Sí' if stats['scheduler_running'] else 'No'}")
    
    elif choice == '4':
        print("\n⏰ Iniciando scheduler automático...")
        backup_manager.start_scheduler()
        print("✅ Scheduler iniciado. Presiona Ctrl+C para detener.")
        
        try:
            while True:
                time.sleep(10)
                print(f"⏳ Scheduler activo... Próximo backup según configuración")
        except KeyboardInterrupt:
            print("\n🛑 Deteniendo scheduler...")
            backup_manager.stop_scheduler()
            print("✅ Scheduler detenido")


if __name__ == "__main__":
    main()