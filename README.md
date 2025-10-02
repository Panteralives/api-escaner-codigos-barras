# 🏪 Sistema POS Avanzado - InventarioBarras

**Sistema completo de Punto de Venta (POS) y gestión de inventario desarrollado en Python. Combina tecnologías modernas como FastAPI, SQLAlchemy, OpenCV, y Streamlit para crear una solución empresarial robusta de escaneo de códigos de barras y gestión comercial.**

[![Estado: Producción](https://img.shields.io/badge/Estado-Producción-brightgreen)]()
[![Python](https://img.shields.io/badge/Python-3.11%2B-blue)]()
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-009688)]()
[![Licencia](https://img.shields.io/badge/Licencia-MIT-yellow)]()

## 🚀 Características Principales

### 💼 **Sistema POS Completo**
- **🛒 Gestión de ventas** con múltiples métodos de pago
- **👥 Sistema multi-usuario** con roles (Admin, Manager, Cajero, Inventario)
- **👤 Gestión de clientes** con programa de lealtad
- **📊 Reportes y analytics** en tiempo real
- **🖨️ Impresión de tickets** ESC/POS con apertura de cajón
- **💰 Manejo de sesiones de caja** y control de efectivo

### 🔍 **Sistema de Escaneo Avanzado**
- **📷 Escaneo desde cámara USB** en tiempo real (OpenCV + pyzbar)
- **🖼️ Escaneo desde imágenes** subidas
- **⌨️ Scanner USB-HID** (funciona como teclado)
- **🏷️ Múltiples tipos de códigos** (EAN-13, UPC-A, QR, Code 128)

### 🖥️ **Múltiples Interfaces**
- **🎨 Frontend Streamlit** - Interfaz interactiva moderna
- **🌐 Frontend FastAPI Web** - Interfaz web nativa
- **📱 POS Avanzado** - Dashboard ejecutivo con WebSocket
- **🛡️ Panel de administración** de backups

### 🔒 **Seguridad Empresarial**
- **🔑 Autenticación JWT** con refresh tokens
- **👮 Control de acceso** por roles granular
- **📝 Auditoría completa** de todas las acciones
- **🛡️ Validación robusta** con Pydantic

### 💾 **Sistema de Backup Automático**
- **⏰ Backups programados** diarios a las 02:00
- **📦 Compresión ZIP** (60-80% reducción de espacio)
- **🔄 Rotación automática** de archivos antiguos
- **🆘 Backup de emergencia** con un clic
- **📊 Estadísticas** y monitoreo completo

## 🛠️ Tecnologías Utilizadas

### 🔙 **Backend Core**
- **Python 3.11+** - Lenguaje principal
- **FastAPI 0.104.1** - Framework web moderno y rápido
- **SQLAlchemy 2.0.23** - ORM para manejo de base de datos
- **SQLite** - Base de datos ligera y eficiente
- **Uvicorn 0.24.0** - Servidor ASGI de alto rendimiento
- **JWT** - Autenticación basada en tokens
- **Pydantic** - Validación de datos

### 👁️ **Computer Vision & Hardware**
- **OpenCV 4.8.1.78** - Procesamiento de imágenes
- **pyzbar 0.1.9** - Decodificación de códigos de barras
- **Pillow 10.1.0** - Manipulación de imágenes
- **pyserial 3.5** - Comunicación serie
- **pyusb 1.2.1** - Dispositivos USB
- **keyboard 0.13.5** - Captura de eventos de teclado
- **customtkinter 5.2.0** - Interfaces desktop modernas

### 🎨 **Frontend & UI**
- **Streamlit 1.28.1** - Framework para interfaces web rápidas
- **Bootstrap 5** - Framework CSS moderno
- **HTML5/CSS3/JavaScript** - Frontend web nativo
- **Chart.js** - Gráficos interactivos
- **WebSockets** - Comunicación en tiempo real

## 📁 Estructura del Proyecto Actualizada

```
C:\InventarioBarras/
├── 📁 src/                          # Código fuente principal
│   ├── 📁 api/                      # API REST con FastAPI
│   │   ├── main.py                  # API básica
│   │   ├── main_advanced.py         # API avanzada con POS
│   │   ├── auth.py                  # Autenticación JWT
│   │   └── schemas.py               # Schemas Pydantic
│   ├── 📁 db/                       # Capa de datos
│   │   ├── database.py              # Configuración SQLAlchemy
│   │   ├── models.py                # Modelos básicos
│   │   ├── models_advanced.py       # Modelos POS avanzados
│   │   └── init_db.py               # Inicialización
│   ├── 📁 scanner/                  # Sistema de escaneo
│   │   ├── barcode_scanner.py       # Scanner OpenCV/pyzbar
│   │   └── usb_hid_scanner.py       # Scanner USB-HID
│   ├── 📁 printer/                  # Sistema de impresión
│   │   ├── printer_manager.py       # Gestión impresoras
│   │   ├── ticket_formatter.py      # Formateo tickets
│   │   └── escpos_commands.py       # Comandos ESC/POS
│   ├── 📁 backup/                   # Sistema de backup
│   │   ├── backup_manager.py        # Gestor principal
│   │   └── backup_routes_fastapi.py # API de backup
│   └── 📁 frontend/                 # Interfaces web
│       ├── streamlit_app.py         # Interfaz Streamlit
│       ├── web_app.py               # Frontend FastAPI web
│       └── backup.html              # Gestión de backups
├── 📁 frontend-pos/                 # POS avanzado independiente
│   ├── pos_server.py                # Servidor POS especializado
│   └── 📁 templates/                # Templates HTML
│       ├── pos_dashboard.html       # Dashboard principal
│       ├── pos_interface.html       # Interfaz de ventas
│       └── dashboard_advanced.html  # Dashboard ejecutivo
├── 📁 backups/                      # Backups automáticos
├── 📁 config/                       # Configuraciones
│   ├── app_config.json              # Configuración principal
│   └── backup_config.json           # Configuración backups
├── 📁 tests/                        # Tests automatizados
└── 📁 docs/                         # Documentación
```

## 🔧 Instalación y Uso

### 🔍 **Prerrequisitos**
- Python 3.11 o superior
- Cámara USB (opcional, para escaneo en vivo)
- Scanner USB-HID (opcional)
- Impresora térmica ESC/POS (opcional)

### 🚀 **Instalación Rápida**
```bash
# Clonar repositorio
git clone https://github.com/Panteralives/api-escaner-codigos-barras.git
cd api-escaner-codigos-barras

# Instalar dependencias e inicializar
python run.py --install
python run.py --init-db

# Verificar hardware
python run.py --check-hardware

# Ejecutar API básica
python run.py
```

### 🏪 **Iniciar POS Avanzado**
```bash
# Terminal 1: API Backend Avanzado
cd C:\InventarioBarras
python src/api/main_advanced.py

# Terminal 2: Frontend POS
cd C:\InventarioBarras
python frontend-pos/pos_server.py
```

### 🐳 **Usar con Docker**
```bash
# Construir imagen
docker build -t inventario-barras-pos .

# Ejecutar contenedor
docker run -p 8000:8000 -p 8001:8001 -p 3002:3002 inventario-barras-pos
```

## 📚 API Endpoints

### 🔍 **API Básica**
- `GET /api/v1/productos/` - Listar productos
- `POST /api/v1/productos/` - Crear producto (requiere auth)
- `GET /api/v1/productos/{codigo}` - Obtener producto específico
- `POST /api/v1/scan/camera` - Escanear desde cámara
- `POST /api/v1/scan/image` - Escanear desde imagen
- `POST /api/v1/auth/login` - Autenticación

### 💰 **API POS Avanzada**
- `POST /api/v1/sales/` - Crear venta
- `GET /api/v1/sales/` - Listar ventas
- `GET /api/v1/sales/{id}` - Detalle de venta
- `POST /api/v1/printer/print-sale` - Imprimir ticket
- `GET /api/v1/stats/overview` - Estadísticas generales
- `GET /api/v1/backup/list` - Listar backups

**Documentación completa:**
- API Básica: `http://localhost:8000/docs`
- API POS: `http://localhost:8001/docs`

## 🖥️ Interfaces Disponibles

| Servicio | URL | Descripción |
|----------|-----|-------------|
| **API Docs Básica** | http://localhost:8000/docs | Documentación Swagger API básica |
| **API Docs Avanzada** | http://localhost:8001/docs | Documentación Swagger POS avanzado |
| **Frontend Streamlit** | http://localhost:8501 | Interfaz principal interactiva |
| **Frontend Web** | http://localhost:3001 | Interfaz web FastAPI |
| **POS Avanzado** | http://localhost:3002 | Sistema POS completo |

## 🧪 Testing

```bash
# Ejecutar todos los tests
python -m pytest tests/ -v

# Tests con coverage
python -m pytest tests/ --cov=src

# Test específico del scanner
python run.py --test-scanner

# Verificar hardware
python run.py --check-hardware
```

## 💡 Casos de Uso

- **🏪 Punto de Venta (POS)** - Sistema completo para tiendas retail
- **📦 Gestión de Inventario** - Control de stock en tiempo real
- **🏭 Sistemas de Almacén** - Seguimiento de productos
- **👥 Gestión de Clientes** - Programa de lealtad integrado
- **📊 Business Intelligence** - Analytics y reportes avanzados
- **🖨️ Impresión de Tickets** - Soporte para hardware real

## 🔒 Seguridad Empresarial

- **👮 Autenticación JWT** con refresh tokens
- **👥 Sistema multi-rol** (Admin, Manager, Cajero, Inventario)
- **📝 Auditoría completa** de todas las acciones
- **🔐 Variables de entorno** para configuración sensible
- **✅ Validación de datos** con Pydantic
- **⚡ Rate limiting** en endpoints críticos

## 📈 Rendimiento

- **⚡ FastAPI** - Una de las frameworks más rápidas de Python
- **📊 Consultas BD optimizadas** - Índices y relaciones eficientes
- **🔄 Async/Await** - Operaciones no bloqueantes
- **💾 Caching estratégico** - Optimización de consultas frecuentes
- **🔍 Compresión de respuestas** - Menor uso de ancho de banda

## 📝 Comandos Principales del Sistema

```bash
# Ejecutar API de desarrollo
python run.py

# Ejecutar frontend Streamlit
python run.py --frontend

# Ejecutar frontend web FastAPI
python run.py --web-frontend

# Modo PRODUCCIÓN (sin reload, optimizado)
python run.py --production

# Inicializar base de datos
python run.py --init-db

# Instalar dependencias
python run.py --install

# Verificar hardware
python run.py --check-camera
python run.py --check-hardware
python run.py --test-scanner

# Configurar autostart (Windows)
python run.py --setup-autostart

# Ver información del proyecto
python run.py --info
```

---

**Desarrollado por:** [Ivan Pantera](https://github.com/Panteralives)

*Sistema POS Avanzado - InventarioBarras es una solución empresarial completa para retail, desarrollada como demostración de habilidades en desarrollo full-stack, integración de hardware, y arquitectura de software moderno.*