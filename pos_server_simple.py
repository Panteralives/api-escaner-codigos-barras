#!/usr/bin/env python3
"""
Servidor POS simplificado para pruebas
Sin dependencias de RabbitMQ u otros servicios externos
"""

from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import json
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import os

# === MODELOS DE DATOS ===

class Product(BaseModel):
    codigo_barra: str
    nombre: str
    precio: float
    stock: int
    categoria: Optional[str] = None

class SaleItem(BaseModel):
    codigo_barra: str
    quantity: int
    unit_price: float
    discount_percentage: float = 0.0

class Payment(BaseModel):
    method: str
    amount: float
    cash_received: Optional[float] = None

class SaleRequest(BaseModel):
    cashier_username: str
    customer_code: Optional[str] = None
    items: List[SaleItem]
    payments: List[Payment]
    notes: Optional[str] = None

# === APLICACIÓN FASTAPI ===

app = FastAPI(
    title="ScanPay POS Server",
    description="Servidor POS simplificado para pruebas",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === DATOS DE PRUEBA ===

# Base de datos simulada en memoria
products_db = {
    "123456": {
        "codigo_barra": "123456",
        "nombre": "Coca Cola 350ml",
        "precio": 2.50,
        "stock": 100,
        "categoria": "Bebidas"
    },
    "789012": {
        "codigo_barra": "789012", 
        "nombre": "Pan Integral",
        "precio": 1.25,
        "stock": 50,
        "categoria": "Panadería"
    },
    "345678": {
        "codigo_barra": "345678",
        "nombre": "Leche Entera 1L", 
        "precio": 3.75,
        "stock": 30,
        "categoria": "Lácteos"
    },
    "901234": {
        "codigo_barra": "901234",
        "nombre": "Manzanas Red 1kg",
        "precio": 4.20,
        "stock": 25,
        "categoria": "Frutas"
    }
}

sales_db = []
scan_history = []

# === ENDPOINTS DE SALUD ===

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "ScanPay POS Server",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "dependencies": {
            "database": "memory",
            "rabbitmq": "disabled", 
            "scanner": "simulated"
        }
    }

# === ENDPOINTS DE PRODUCTOS ===

@app.get("/api/productos")
async def get_all_products():
    """Obtener todos los productos"""
    return list(products_db.values())

@app.get("/api/productos/{codigo_barra}")
async def get_product(codigo_barra: str):
    """Obtener producto por código de barras"""
    if codigo_barra in products_db:
        return products_db[codigo_barra]
    else:
        raise HTTPException(
            status_code=404,
            detail={"error": f"Producto con código {codigo_barra} no encontrado"}
        )

# === ENDPOINTS DE VENTAS ===

@app.post("/api/sales")
async def create_sale(sale_request: SaleRequest):
    """Crear nueva venta"""
    try:
        # Generar número de venta único
        today = datetime.now().strftime("%Y%m%d")
        sale_number = f"POS-{today}-{len(sales_db) + 1:04d}"
        
        # Verificar productos y stock
        total_amount = 0.0
        processed_items = []
        
        for item in sale_request.items:
            if item.codigo_barra not in products_db:
                raise HTTPException(
                    status_code=404,
                    detail=f"Producto {item.codigo_barra} no encontrado"
                )
            
            product = products_db[item.codigo_barra]
            
            if product["stock"] < item.quantity:
                raise HTTPException(
                    status_code=400,
                    detail=f"Stock insuficiente para {product['nombre']}"
                )
            
            # Calcular totales
            line_total = item.unit_price * item.quantity
            discount_amount = line_total * (item.discount_percentage / 100)
            final_total = line_total - discount_amount
            
            processed_items.append({
                "codigo_barra": item.codigo_barra,
                "nombre": product["nombre"],
                "quantity": item.quantity,
                "unit_price": item.unit_price,
                "discount_percentage": item.discount_percentage,
                "discount_amount": discount_amount,
                "line_total": final_total
            })
            
            total_amount += final_total
            
            # Actualizar stock
            products_db[item.codigo_barra]["stock"] -= item.quantity
        
        # Calcular cambio si es efectivo
        change = 0.0
        total_paid = sum(payment.amount for payment in sale_request.payments)
        
        if total_paid > total_amount:
            change = total_paid - total_amount
        
        # Crear registro de venta
        sale_record = {
            "id": len(sales_db) + 1,
            "sale_number": sale_number,
            "cashier_username": sale_request.cashier_username,
            "customer_code": sale_request.customer_code,
            "items": processed_items,
            "payments": [payment.dict() for payment in sale_request.payments],
            "subtotal": total_amount * 0.84,  # Simulando IVA 16%
            "tax_amount": total_amount * 0.16,
            "total_amount": total_amount,
            "change": change,
            "notes": sale_request.notes,
            "created_at": datetime.now().isoformat(),
            "status": "completed"
        }
        
        sales_db.append(sale_record)
        
        return {
            "status": "success",
            "message": "Venta creada exitosamente",
            "sale_id": sale_record["id"],
            "sale_number": sale_number,
            "total": total_amount,
            "change": change
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error procesando venta: {str(e)}"
        )

@app.get("/api/sales")
async def get_sales():
    """Obtener lista de ventas"""
    return sales_db

@app.get("/api/sales/{sale_id}")
async def get_sale_detail(sale_id: int):
    """Obtener detalles de una venta"""
    for sale in sales_db:
        if sale["id"] == sale_id:
            return sale
    
    raise HTTPException(
        status_code=404,
        detail="Venta no encontrada"
    )

# === ENDPOINTS DE ESCÁNER ===

@app.get("/api/scan/camera/status")
async def scanner_status():
    """Estado del escáner (simulado)"""
    return {
        "camera_index": 0,
        "available": True,
        "message": "Escáner simulado disponible",
        "type": "simulated"
    }

@app.post("/api/scan/camera")
async def scan_from_camera():
    """Escanear desde cámara (simulado)"""
    # Simular escaneo exitoso con producto aleatorio
    import random
    
    codes = list(products_db.keys())
    if codes:
        selected_code = random.choice(codes)
        product = products_db[selected_code]
        
        # Agregar a historial
        scan_record = {
            "codigo_barra": selected_code,
            "tipo_codigo": "CODE_128",
            "encontrado": True,
            "producto": product,
            "timestamp": datetime.now().isoformat(),
            "method": "camera_simulation"
        }
        
        scan_history.append(scan_record)
        
        return scan_record
    else:
        return {
            "codigo_barra": "",
            "tipo_codigo": "",
            "encontrado": False,
            "producto": None,
            "timestamp": datetime.now().isoformat()
        }

# === ENDPOINTS DE AUTENTICACIÓN (SIMULADA) ===

@app.post("/auth/login")
async def login(username: str = Form(...), password: str = Form(...)):
    """Login simulado"""
    # Cualquier usuario/contraseña es válida en modo simulado
    if username and password:
        return {
            "access_token": f"simulated_token_{uuid.uuid4().hex[:16]}",
            "token_type": "bearer",
            "expires_in": 3600,
            "user": {
                "username": username,
                "role": "cashier",
                "authenticated": True
            }
        }
    else:
        raise HTTPException(
            status_code=401,
            detail="Credenciales inválidas"
        )

# === ENDPOINTS DE ESTADÍSTICAS ===

@app.get("/api/stats")
async def get_stats():
    """Estadísticas del sistema"""
    return {
        "products_count": len(products_db),
        "sales_count": len(sales_db),
        "scans_count": len(scan_history),
        "total_revenue": sum(sale["total_amount"] for sale in sales_db),
        "uptime": "Simulado",
        "last_sale": sales_db[-1]["created_at"] if sales_db else None
    }

# === ENDPOINT PARA SINCRONIZACIÓN ===

@app.get("/api/sync")
async def sync_data():
    """Sincronización de datos"""
    return {
        "status": "success",
        "message": "Sincronización completa",
        "timestamp": datetime.now().isoformat(),
        "data": {
            "products_synced": len(products_db),
            "sales_synced": len(sales_db)
        }
    }

# === FUNCIÓN PRINCIPAL ===

def main():
    print("🚀 Iniciando Servidor POS Simplificado...")
    print("📡 Modo: Standalone (sin dependencias externas)")
    print("🔧 Puerto: 3002")
    print("🌐 URL: http://localhost:3002")
    print("❤️ Health Check: http://localhost:3002/health")
    print("📊 Estadísticas: http://localhost:3002/api/stats")
    print("\n✅ Servidor listo para recibir conexiones")
    
    uvicorn.run(
        "pos_server_simple:app",
        host="0.0.0.0",
        port=3002,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    main()