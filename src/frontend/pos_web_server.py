#!/usr/bin/env python3
"""
Servidor web simple para la interfaz POS HTML
"""

from flask import Flask, send_from_directory, jsonify
import os
from pathlib import Path

app = Flask(__name__)

# Directorio de templates
FRONTEND_DIR = Path(__file__).parent

@app.route('/')
def index():
    """Servir la interfaz principal POS"""
    return send_from_directory(FRONTEND_DIR, 'pos_web_interface.html')

@app.route('/pos')
def pos_interface():
    """Servir la interfaz POS (ruta alternativa)"""
    return send_from_directory(FRONTEND_DIR, 'pos_web_interface.html')

@app.route('/health')
def health_check():
    """Health check del servidor web"""
    return jsonify({
        "status": "healthy",
        "message": "Servidor POS Web funcionando",
        "version": "1.0.0"
    })

if __name__ == '__main__':
    print("🛒 Iniciando servidor POS Web...")
    print("📱 Interfaz disponible en: http://localhost:3002")
    print("🔗 Ruta POS: http://localhost:3002/pos")
    print("⏹️ Presiona Ctrl+C para detener")
    print("-" * 50)
    
    app.run(
        host='0.0.0.0',
        port=3002,
        debug=False,
        threaded=True
    )