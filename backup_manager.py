#!/usr/bin/env python3
"""
Gestor de backups simplificado para testing
"""

import os
import shutil
import zipfile
import json
from datetime import datetime
from pathlib import Path

class BackupManager:
    def __init__(self, backup_dir="./backups"):
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True)
    
    def create_backup(self, backup_type="manual", description=""):
        """Crear un backup"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"backup_{timestamp}_{backup_type}.zip"
            backup_path = self.backup_dir / backup_filename
            
            with zipfile.ZipFile(backup_path, 'w') as zipf:
                # Respaldar base de datos
                if Path("inventario.db").exists():
                    zipf.write("inventario.db")
                
                # Respaldar configuración
                if Path("config").exists():
                    for file in Path("config").rglob("*"):
                        if file.is_file():
                            zipf.write(file, f"config/{file.name}")
                
                # Crear info del backup
                backup_info = {
                    "timestamp": datetime.now().isoformat(),
                    "type": backup_type,
                    "description": description,
                    "files": zipf.namelist()
                }
                
                info_json = json.dumps(backup_info, indent=2)
                zipf.writestr("backup_info.json", info_json)
            
            return {
                "success": True,
                "backup_file": str(backup_path),
                "size": backup_path.stat().st_size
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def list_backups(self):
        """Listar backups disponibles"""
        backups = []
        
        for backup_file in self.backup_dir.glob("backup_*.zip"):
            stat = backup_file.stat()
            backups.append({
                "filename": backup_file.name,
                "timestamp": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "size_mb": stat.st_size / (1024 * 1024)
            })
        
        return sorted(backups, key=lambda x: x["timestamp"], reverse=True)
    
    def get_stats(self):
        """Obtener estadísticas"""
        backups = self.list_backups()
        
        total_size = sum(b["size_mb"] for b in backups)
        
        return {
            "total_backups": len(backups),
            "total_size_mb": total_size,
            "last_backup_date": backups[0]["timestamp"] if backups else None,
            "success_rate": 100.0  # Simplificado
        }
