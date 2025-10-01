"""
Modelos avanzados de base de datos para sistema POS completo
Incluye ventas, usuarios, clientes, pagos y auditoría
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, JSON, DECIMAL, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum

Base = declarative_base()


# === ENUMS PARA ESTADOS Y TIPOS ===

class SaleStatus(enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"

class PaymentMethod(enum.Enum):
    CASH = "cash"
    CARD = "card"
    TRANSFER = "transfer"
    MIXED = "mixed"
    CREDIT = "credit"

class UserRole(enum.Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    CASHIER = "cashier"
    INVENTORY = "inventory"


# === MODELO DE PRODUCTOS (EXPANDIDO) ===

class Producto(Base):
    """Modelo expandido de producto"""
    __tablename__ = "productos"
    
    id = Column(Integer, primary_key=True, index=True)
    codigo_barra = Column(String(50), unique=True, nullable=False, index=True)
    nombre = Column(String(200), nullable=False)
    descripcion = Column(Text)
    precio = Column(DECIMAL(10, 2), nullable=False)
    costo = Column(DECIMAL(10, 2), default=0.00)
    
    # Inventario
    stock = Column(Integer, default=0)
    stock_minimo = Column(Integer, default=5)
    
    # Categorización
    categoria = Column(String(100))
    subcategoria = Column(String(100))
    marca = Column(String(100))
    
    # Configuración
    is_active = Column(Boolean, default=True)
    is_taxable = Column(Boolean, default=True)
    tax_rate = Column(DECIMAL(5, 2), default=16.00)  # IVA México
    
    # Fechas
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relaciones
    sale_items = relationship("SaleItem", back_populates="producto")
    
    def __repr__(self):
        return f"<Producto(codigo='{self.codigo_barra}', nombre='{self.nombre}', precio={self.precio})>"


# === MODELO DE USUARIOS (EXPANDIDO) ===

class User(Base):
    """Sistema completo de usuarios con roles"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(120), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    
    # Información personal
    full_name = Column(String(120), nullable=False)
    phone = Column(String(20))
    
    # Configuración de cuenta
    role = Column(Enum(UserRole), default=UserRole.CASHIER)
    is_active = Column(Boolean, default=True)
    
    # Fechas
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_login = Column(DateTime)
    
    # Configuración POS
    default_printer = Column(String(100))
    cash_drawer_access = Column(Boolean, default=True)
    
    # Relaciones
    sales = relationship("Sale", back_populates="cashier")
    audit_logs = relationship("AuditLog", back_populates="user")
    
    def __repr__(self):
        return f"<User(username='{self.username}', role='{self.role.value}')>"


# === MODELO DE CLIENTES ===

class Customer(Base):
    """Modelo de clientes con programa de lealtad"""
    __tablename__ = "customers"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_code = Column(String(20), unique=True)  # CL-00001
    
    # Información personal
    name = Column(String(120), nullable=False)
    email = Column(String(120), unique=True)
    phone = Column(String(20))
    
    # Información fiscal
    tax_id = Column(String(50))  # RFC, CUIT, etc.
    business_name = Column(String(200))  # Razón social
    address = Column(Text)
    
    # Programa de lealtad
    loyalty_points = Column(Integer, default=0)
    total_spent = Column(DECIMAL(10, 2), default=0.00)
    visit_count = Column(Integer, default=0)
    
    # Configuración
    is_active = Column(Boolean, default=True)
    preferred_payment = Column(Enum(PaymentMethod))
    
    # Fechas
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_visit = Column(DateTime)
    birthday = Column(DateTime)
    
    # Relaciones
    sales = relationship("Sale", back_populates="customer")
    
    def __repr__(self):
        return f"<Customer(code='{self.customer_code}', name='{self.name}', points={self.loyalty_points})>"


# === MODELO DE VENTAS ===

class Sale(Base):
    """Modelo completo de ventas"""
    __tablename__ = "sales"
    
    id = Column(Integer, primary_key=True, index=True)
    sale_number = Column(String(50), unique=True, nullable=False, index=True)  # SALE-2024-001234
    
    # Referencias
    cashier_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    customer_id = Column(Integer, ForeignKey('customers.id'))
    
    # Totales financieros
    subtotal = Column(DECIMAL(10, 2), nullable=False)
    tax_amount = Column(DECIMAL(10, 2), default=0.00)
    discount_amount = Column(DECIMAL(10, 2), default=0.00)
    total_amount = Column(DECIMAL(10, 2), nullable=False)
    
    # Información de pago
    payment_method = Column(Enum(PaymentMethod), nullable=False)
    payment_reference = Column(String(100))
    cash_received = Column(DECIMAL(10, 2))
    change_given = Column(DECIMAL(10, 2))
    
    # Estados
    status = Column(Enum(SaleStatus), default=SaleStatus.PENDING, index=True)
    
    # Fechas importantes
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    completed_at = Column(DateTime)
    
    # Control operativo
    receipt_printed = Column(Boolean, default=False)
    drawer_opened = Column(Boolean, default=False)
    notes = Column(Text)
    
    # Facturación
    requires_invoice = Column(Boolean, default=False)
    invoice_number = Column(String(50))
    cfdi_uuid = Column(String(50))  # Para México
    
    # Relaciones
    cashier = relationship("User", back_populates="sales")
    customer = relationship("Customer", back_populates="sales")
    items = relationship("SaleItem", back_populates="sale", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="sale", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Sale(number='{self.sale_number}', total={self.total_amount}, status='{self.status.value}')>"


# === MODELO DE ITEMS DE VENTA ===

class SaleItem(Base):
    """Items individuales de cada venta"""
    __tablename__ = "sale_items"
    
    id = Column(Integer, primary_key=True, index=True)
    sale_id = Column(Integer, ForeignKey('sales.id'), nullable=False, index=True)
    producto_id = Column(Integer, ForeignKey('productos.id'), nullable=False)
    
    # Cantidades y precios
    quantity = Column(Integer, nullable=False)
    unit_price = Column(DECIMAL(10, 2), nullable=False)
    discount_amount = Column(DECIMAL(10, 2), default=0.00)
    discount_percentage = Column(DECIMAL(5, 2), default=0.00)
    line_total = Column(DECIMAL(10, 2), nullable=False)
    
    # Impuestos
    tax_rate = Column(DECIMAL(5, 2), default=0.00)
    tax_amount = Column(DECIMAL(10, 2), default=0.00)
    
    # Metadatos
    notes = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relaciones
    sale = relationship("Sale", back_populates="items")
    producto = relationship("Producto", back_populates="sale_items")
    
    def __repr__(self):
        return f"<SaleItem(qty={self.quantity}, price={self.unit_price}, total={self.line_total})>"


# === MODELO DE PAGOS ===

class Payment(Base):
    """Modelo para pagos mixtos y detalles de pago"""
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True, index=True)
    sale_id = Column(Integer, ForeignKey('sales.id'), nullable=False)
    
    # Detalles del pago
    method = Column(Enum(PaymentMethod), nullable=False)
    amount = Column(DECIMAL(10, 2), nullable=False)
    
    # Referencias externas
    reference = Column(String(100))  # Número de autorización, folio
    authorization_code = Column(String(50))
    terminal_id = Column(String(20))
    
    # Para efectivo
    cash_received = Column(DECIMAL(10, 2))
    change_amount = Column(DECIMAL(10, 2), default=0.00)
    
    # Fechas
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    processed_at = Column(DateTime)
    
    # Relaciones
    sale = relationship("Sale", back_populates="payments")
    
    def __repr__(self):
        return f"<Payment(method='{self.method.value}', amount={self.amount})>"


# === MODELO DE HISTORIAL DE ESCANEOS (EXPANDIDO) ===

class ScanHistory(Base):
    """Historial expandido de escaneos"""
    __tablename__ = "scan_history"
    
    id = Column(Integer, primary_key=True, index=True)
    codigo_barra = Column(String(50), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    sale_id = Column(Integer, ForeignKey('sales.id'))
    
    # Resultado del escaneo
    found = Column(Boolean, default=False)
    product_name = Column(String(200))
    scan_type = Column(String(20))  # manual, usb_hid, camera
    
    # Fechas
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Relaciones
    user = relationship("User")
    sale = relationship("Sale")
    
    def __repr__(self):
        return f"<ScanHistory(codigo='{self.codigo_barra}', found={self.found})>"


# === MODELO DE AUDITORÍA ===

class AuditLog(Base):
    """Log de auditoría para todas las acciones del sistema"""
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    
    # Acción realizada
    action = Column(String(50), nullable=False, index=True)  # CREATE, UPDATE, DELETE, LOGIN
    table_name = Column(String(50), index=True)
    record_id = Column(Integer)
    
    # Datos de la acción
    old_values = Column(JSON)
    new_values = Column(JSON)
    
    # Información técnica
    ip_address = Column(String(45))
    user_agent = Column(String(500))
    session_id = Column(String(100))
    
    # Fecha
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Relaciones
    user = relationship("User", back_populates="audit_logs")
    
    def __repr__(self):
        return f"<AuditLog(action='{self.action}', table='{self.table_name}', user_id={self.user_id})>"


# === MODELO DE CONFIGURACIÓN DEL SISTEMA ===

class SystemConfig(Base):
    """Configuración del sistema"""
    __tablename__ = "system_config"
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), unique=True, nullable=False, index=True)
    value = Column(Text)
    description = Column(String(255))
    
    # Categorización
    category = Column(String(50), index=True)  # printer, tax, business, etc.
    
    # Control de cambios
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    updated_by = Column(Integer, ForeignKey('users.id'))
    
    def __repr__(self):
        return f"<SystemConfig(key='{self.key}', category='{self.category}')>"


# === MODELO DE SESIONES DE CAJA ===

class CashSession(Base):
    """Sesiones de caja para control de efectivo"""
    __tablename__ = "cash_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_number = Column(String(50), unique=True, nullable=False)
    cashier_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # Montos de apertura y cierre
    opening_amount = Column(DECIMAL(10, 2), nullable=False)
    closing_amount = Column(DECIMAL(10, 2))
    expected_amount = Column(DECIMAL(10, 2))
    difference = Column(DECIMAL(10, 2))
    
    # Estados
    is_open = Column(Boolean, default=True)
    
    # Fechas
    opened_at = Column(DateTime(timezone=True), server_default=func.now())
    closed_at = Column(DateTime)
    
    # Notas
    opening_notes = Column(Text)
    closing_notes = Column(Text)
    
    # Relaciones
    cashier = relationship("User")
    
    def __repr__(self):
        return f"<CashSession(number='{self.session_number}', cashier_id={self.cashier_id})>"


# === MODELO DE PROMOCIONES Y DESCUENTOS ===

class Promotion(Base):
    """Promociones y descuentos del sistema"""
    __tablename__ = "promotions"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False)
    description = Column(Text)
    
    # Tipo de promoción
    type = Column(String(50), nullable=False)  # percentage, fixed, buy_x_get_y
    discount_value = Column(DECIMAL(10, 2))
    discount_percentage = Column(DECIMAL(5, 2))
    
    # Condiciones
    min_amount = Column(DECIMAL(10, 2))
    max_discount = Column(DECIMAL(10, 2))
    applicable_products = Column(JSON)  # Lista de códigos de productos
    
    # Vigencia
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    
    # Estado
    is_active = Column(Boolean, default=True)
    
    # Fechas de sistema
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<Promotion(name='{self.name}', type='{self.type}')>"