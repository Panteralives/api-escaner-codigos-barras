"""
API Routes for Sales Management
Manejo completo de ventas, items y pagos
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date, timedelta
from decimal import Decimal

from ...db.models_advanced import Sale, SaleItem, Payment, Producto, User, Customer, SaleStatus, PaymentMethod
from ...db.database import get_db_engine
from sqlalchemy.orm import sessionmaker
from pydantic import BaseModel, Field

router = APIRouter(prefix="/sales", tags=["sales"])

# Dependency para obtener sesión de DB
def get_db():
    engine = get_db_engine()
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# === MODELOS PYDANTIC ===

class SaleItemRequest(BaseModel):
    codigo_barra: str
    quantity: int = Field(ge=1)
    unit_price: Optional[Decimal] = None
    discount_percentage: Optional[Decimal] = Field(default=0.0, ge=0, le=100)

class PaymentRequest(BaseModel):
    method: PaymentMethod
    amount: Decimal = Field(gt=0)
    cash_received: Optional[Decimal] = None
    reference: Optional[str] = None

class CreateSaleRequest(BaseModel):
    cashier_username: str
    customer_code: Optional[str] = None
    items: List[SaleItemRequest]
    payments: List[PaymentRequest]
    notes: Optional[str] = None

class SaleResponse(BaseModel):
    id: int
    sale_number: str
    cashier_name: str
    customer_name: Optional[str] = None
    subtotal: Decimal
    tax_amount: Decimal
    total_amount: Decimal
    status: SaleStatus
    created_at: datetime
    completed_at: Optional[datetime] = None
    items_count: int
    
    class Config:
        from_attributes = True


# === ENDPOINTS ===

@router.post("/", response_model=dict)
async def create_sale(sale_request: CreateSaleRequest, db: Session = Depends(get_db)):
    """Crear nueva venta completa"""
    
    try:
        # Buscar cajero
        cashier = db.query(User).filter_by(username=sale_request.cashier_username).first()
        if not cashier:
            raise HTTPException(status_code=404, detail="Cajero no encontrado")
        
        # Buscar cliente (opcional)
        customer = None
        if sale_request.customer_code:
            customer = db.query(Customer).filter_by(customer_code=sale_request.customer_code).first()
            if not customer:
                raise HTTPException(status_code=404, detail="Cliente no encontrado")
        
        # Generar número de venta
        today = datetime.now().strftime("%Y%m%d")
        last_sale = db.query(Sale).filter(Sale.sale_number.like(f"POS-{today}-%")).order_by(Sale.id.desc()).first()
        next_number = 1 if not last_sale else int(last_sale.sale_number.split('-')[-1]) + 1
        sale_number = f"POS-{today}-{next_number:04d}"
        
        # Crear venta
        sale = Sale(
            sale_number=sale_number,
            cashier_id=cashier.id,
            customer_id=customer.id if customer else None,
            subtotal=Decimal('0.00'),
            tax_amount=Decimal('0.00'), 
            total_amount=Decimal('0.00'),
            payment_method=sale_request.payments[0].method if sale_request.payments else PaymentMethod.CASH,
            status=SaleStatus.PENDING,
            notes=sale_request.notes
        )
        
        db.add(sale)
        db.flush()  # Para obtener el ID
        
        # Procesar items
        total = Decimal('0.00')
        for item_req in sale_request.items:
            # Buscar producto
            producto = db.query(Producto).filter_by(codigo_barra=item_req.codigo_barra).first()
            if not producto:
                raise HTTPException(status_code=404, detail=f"Producto {item_req.codigo_barra} no encontrado")
            
            # Verificar stock
            if producto.stock < item_req.quantity:
                raise HTTPException(status_code=400, detail=f"Stock insuficiente para {producto.nombre}")
            
            # Calcular precios
            unit_price = item_req.unit_price or producto.precio
            line_total = unit_price * item_req.quantity
            discount_amount = line_total * (item_req.discount_percentage / 100)
            final_line_total = line_total - discount_amount
            
            # Crear item de venta
            sale_item = SaleItem(
                sale_id=sale.id,
                producto_id=producto.id,
                quantity=item_req.quantity,
                unit_price=unit_price,
                discount_percentage=item_req.discount_percentage,
                discount_amount=discount_amount,
                line_total=final_line_total,
                tax_rate=producto.tax_rate if producto.is_taxable else Decimal('0.00')
            )
            
            # Calcular impuestos
            if producto.is_taxable:
                sale_item.tax_amount = final_line_total * (producto.tax_rate / 100)
            
            db.add(sale_item)
            total += final_line_total
            
            # Actualizar stock
            producto.stock -= item_req.quantity
        
        # Calcular totales de la venta
        sale.subtotal = total / (1 + (Decimal('16.00') / 100))  # Asumiendo 16% IVA
        sale.tax_amount = total - sale.subtotal
        sale.total_amount = total
        
        # Procesar pagos
        total_paid = Decimal('0.00')
        for payment_req in sale_request.payments:
            payment = Payment(
                sale_id=sale.id,
                method=payment_req.method,
                amount=payment_req.amount,
                cash_received=payment_req.cash_received,
                reference=payment_req.reference
            )
            
            # Calcular cambio para efectivo
            if payment_req.method == PaymentMethod.CASH and payment_req.cash_received:
                payment.change_amount = max(Decimal('0.00'), payment_req.cash_received - payment_req.amount)
            
            db.add(payment)
            total_paid += payment_req.amount
        
        # Verificar que los pagos cubran el total
        if total_paid < sale.total_amount:
            raise HTTPException(status_code=400, detail="El monto pagado es insuficiente")
        
        # Completar venta
        sale.status = SaleStatus.COMPLETED
        sale.completed_at = datetime.now()
        
        # Actualizar estadísticas del cliente
        if customer:
            customer.total_spent += sale.total_amount
            customer.visit_count += 1
            customer.last_visit = datetime.now()
            customer.loyalty_points += int(sale.total_amount / 10)  # 1 punto por cada $10
        
        db.commit()
        
        return {
            "status": "success",
            "message": "Venta creada exitosamente",
            "sale_id": sale.id,
            "sale_number": sale.sale_number,
            "total": float(sale.total_amount),
            "change": float(payment.change_amount) if 'payment' in locals() and payment.change_amount else 0.0
        }
        
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creando venta: {str(e)}")


@router.get("/", response_model=List[SaleResponse])
async def get_sales(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    cashier_id: Optional[int] = None,
    status: Optional[SaleStatus] = None,
    db: Session = Depends(get_db)
):
    """Obtener lista de ventas con filtros"""
    
    query = db.query(Sale)
    
    # Aplicar filtros
    if start_date:
        query = query.filter(Sale.created_at >= start_date)
    if end_date:
        query = query.filter(Sale.created_at <= end_date + timedelta(days=1))
    if cashier_id:
        query = query.filter(Sale.cashier_id == cashier_id)
    if status:
        query = query.filter(Sale.status == status)
    
    sales = query.order_by(Sale.created_at.desc()).offset(skip).limit(limit).all()
    
    # Formatear respuesta
    response = []
    for sale in sales:
        response.append(SaleResponse(
            id=sale.id,
            sale_number=sale.sale_number,
            cashier_name=sale.cashier.full_name,
            customer_name=sale.customer.name if sale.customer else None,
            subtotal=sale.subtotal,
            tax_amount=sale.tax_amount,
            total_amount=sale.total_amount,
            status=sale.status,
            created_at=sale.created_at,
            completed_at=sale.completed_at,
            items_count=len(sale.items)
        ))
    
    return response


@router.get("/{sale_id}")
async def get_sale_detail(sale_id: int, db: Session = Depends(get_db)):
    """Obtener detalles completos de una venta"""
    
    sale = db.query(Sale).filter(Sale.id == sale_id).first()
    if not sale:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    
    # Formatear respuesta completa
    response = {
        "sale": {
            "id": sale.id,
            "sale_number": sale.sale_number,
            "cashier": {
                "id": sale.cashier.id,
                "name": sale.cashier.full_name,
                "username": sale.cashier.username
            },
            "customer": {
                "id": sale.customer.id,
                "code": sale.customer.customer_code,
                "name": sale.customer.name
            } if sale.customer else None,
            "subtotal": float(sale.subtotal),
            "tax_amount": float(sale.tax_amount),
            "discount_amount": float(sale.discount_amount),
            "total_amount": float(sale.total_amount),
            "status": sale.status.value,
            "created_at": sale.created_at.isoformat(),
            "completed_at": sale.completed_at.isoformat() if sale.completed_at else None,
            "notes": sale.notes
        },
        "items": [
            {
                "id": item.id,
                "producto": {
                    "codigo_barra": item.producto.codigo_barra,
                    "nombre": item.producto.nombre,
                    "categoria": item.producto.categoria
                },
                "quantity": item.quantity,
                "unit_price": float(item.unit_price),
                "discount_percentage": float(item.discount_percentage),
                "discount_amount": float(item.discount_amount),
                "line_total": float(item.line_total),
                "tax_amount": float(item.tax_amount)
            }
            for item in sale.items
        ],
        "payments": [
            {
                "id": payment.id,
                "method": payment.method.value,
                "amount": float(payment.amount),
                "cash_received": float(payment.cash_received) if payment.cash_received else None,
                "change_amount": float(payment.change_amount),
                "reference": payment.reference,
                "created_at": payment.created_at.isoformat()
            }
            for payment in sale.payments
        ]
    }
    
    return response


@router.patch("/{sale_id}/cancel")
async def cancel_sale(sale_id: int, reason: str = "Cancelada por usuario", db: Session = Depends(get_db)):
    """Cancelar una venta y restaurar stock"""
    
    sale = db.query(Sale).filter(Sale.id == sale_id).first()
    if not sale:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    
    if sale.status != SaleStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Solo se pueden cancelar ventas completadas")
    
    try:
        # Restaurar stock de productos
        for item in sale.items:
            item.producto.stock += item.quantity
        
        # Actualizar estadísticas del cliente
        if sale.customer:
            sale.customer.total_spent -= sale.total_amount
            sale.customer.visit_count = max(0, sale.customer.visit_count - 1)
            sale.customer.loyalty_points = max(0, sale.customer.loyalty_points - int(sale.total_amount / 10))
        
        # Cambiar estado
        sale.status = SaleStatus.CANCELLED
        sale.notes = f"{sale.notes or ''} - CANCELADA: {reason}"
        
        db.commit()
        
        return {
            "status": "success",
            "message": f"Venta {sale.sale_number} cancelada exitosamente"
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error cancelando venta: {str(e)}")


# === ENDPOINTS DE REPORTES RÁPIDOS ===

@router.get("/reports/daily")
async def daily_sales_report(target_date: Optional[date] = None, db: Session = Depends(get_db)):
    """Reporte de ventas diarias"""
    
    if not target_date:
        target_date = date.today()
    
    start_datetime = datetime.combine(target_date, datetime.min.time())
    end_datetime = datetime.combine(target_date, datetime.max.time())
    
    # Query ventas del día
    sales = db.query(Sale).filter(
        Sale.created_at >= start_datetime,
        Sale.created_at <= end_datetime,
        Sale.status == SaleStatus.COMPLETED
    ).all()
    
    # Calcular métricas
    total_sales = len(sales)
    total_revenue = sum(sale.total_amount for sale in sales)
    total_items = sum(len(sale.items) for sale in sales)
    average_ticket = total_revenue / total_sales if total_sales > 0 else 0
    
    # Ventas por método de pago
    payment_methods = {}
    for sale in sales:
        for payment in sale.payments:
            method = payment.method.value
            payment_methods[method] = payment_methods.get(method, 0) + float(payment.amount)
    
    return {
        "date": target_date.isoformat(),
        "summary": {
            "total_sales": total_sales,
            "total_revenue": float(total_revenue),
            "total_items": total_items,
            "average_ticket": float(average_ticket)
        },
        "payment_methods": payment_methods,
        "hourly_sales": _get_hourly_breakdown(sales)
    }


def _get_hourly_breakdown(sales):
    """Calcular breakdown de ventas por hora"""
    hourly = {}
    for sale in sales:
        hour = sale.created_at.hour
        if hour not in hourly:
            hourly[hour] = {"count": 0, "revenue": 0.0}
        hourly[hour]["count"] += 1
        hourly[hour]["revenue"] += float(sale.total_amount)
    return hourly