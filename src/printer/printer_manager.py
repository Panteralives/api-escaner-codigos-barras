"""
PrinterManager - Maneja conexión a impresoras térmicas y apertura de cajón
Soporta:
- Impresoras USB/Red (via sockets) ESC/POS
- Impresión a archivo (para depuración)
- Apertura de cajón (escpos)
"""

import os
import socket
from typing import Optional, Dict, Any
from .escpos_commands import ESCPOSCommands

class PrinterManager:
    def __init__(self, mode: str = 'file', 
                 ip: Optional[str] = None, port: int = 9100,
                 file_path: str = 'ticket_output.bin'):
        """
        Args:
            mode: 'network' para impresora de red (RAW 9100), 'file' para volcar a archivo
            ip: IP de la impresora en modo 'network'
            port: Puerto TCP (por defecto 9100)
            file_path: Ruta de archivo para modo 'file'
        """
        self.mode = mode
        self.ip = ip
        self.port = port
        self.file_path = file_path
        self.cmd = ESCPOSCommands

    def print_bytes(self, data: bytes) -> Dict[str, Any]:
        """Enviar bytes a la impresora o archivo"""
        if self.mode == 'network' and self.ip:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(5)
                sock.connect((self.ip, self.port))
                sock.sendall(data)
                sock.close()
                return {"status": "success", "message": "Ticket enviado a impresora de red"}
            except Exception as e:
                return {"status": "error", "message": f"Error enviando a impresora: {e}"}
        else:
            # Modo archivo por defecto (útil para debug y Windows sin drivers)
            try:
                with open(self.file_path, 'ab') as f:
                    f.write(data)
                return {"status": "success", "message": f"Ticket guardado en {self.file_path}"}
            except Exception as e:
                return {"status": "error", "message": f"Error escribiendo archivo: {e}"}

    def open_cash_drawer(self, drawer: int = 1) -> Dict[str, Any]:
        """Enviar comando de apertura de cajón"""
        command = self.cmd.OPEN_DRAWER_1 if drawer == 1 else self.cmd.OPEN_DRAWER_2
        return self.print_bytes(command)

    def print_test(self) -> Dict[str, Any]:
        """Imprimir ticket de prueba"""
        from .ticket_formatter import TicketFormatter
        formatter = TicketFormatter()
        data = formatter.format_test_ticket()
        return self.print_bytes(data)

    def print_no_sale(self) -> Dict[str, Any]:
        """Imprimir ticket de apertura de cajón sin venta (no sale)"""
        from .ticket_formatter import TicketFormatter
        formatter = TicketFormatter()
        data = formatter.format_no_sale_ticket()
        return self.print_bytes(data)
