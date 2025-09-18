# 📷 API Escáner de Códigos de Barras

**Una API REST completa desarrollada en Python para el escaneo y gestión de códigos de barras con integración de hardware real.**

## 🚀 Características Principales

- **API REST completa** con FastAPI y documentación automática
- **Escaneo en tiempo real** usando cámaras USB con OpenCV y pyzbar
- **Base de datos SQLite** con SQLAlchemy ORM
- **Autenticación JWT** segura
- **Frontend web interactivo** con Streamlit
- **Testing automatizado** con pytest
- **Containerización** con Docker
- **CI/CD** con GitHub Actions

## 🛠️ Tecnologías Utilizadas

### Backend
- **Python 3.8+**
- **FastAPI** - Framework web moderno y rápido
- **SQLAlchemy** - ORM para base de datos
- **SQLite** - Base de datos ligera
- **JWT** - Autenticación basada en tokens
- **Pydantic** - Validación de datos

### Computer Vision & Hardware
- **OpenCV** - Procesamiento de imágenes
- **pyzbar** - Decodificación de códigos de barras
- **USB Camera Integration** - Soporte para cámaras reales

### Frontend & UI
- **Streamlit** - Interfaz web interactiva
- **Responsive Design** - Adaptable a diferentes dispositivos

### DevOps & Testing
- **Docker** - Containerización
- **pytest** - Testing automatizado
- **GitHub Actions** - CI/CD
- **Git** - Control de versiones

## 📁 Estructura del Proyecto

```
api/
├── src/
│   ├── api/           # API REST endpoints
│   ├── db/            # Modelos y configuración de BD
│   ├── scanner/       # Lógica de escaneo
│   └── frontend/      # Interfaz Streamlit
├── tests/             # Tests automatizados
├── docs/              # Documentación
├── Dockerfile         # Configuración Docker
└── requirements.txt   # Dependencias Python
```

## 🔧 Instalación y Uso

### Prerrequisitos
- Python 3.8 o superior
- Cámara USB (opcional, para escaneo en vivo)
- Git

### Instalación Rápida
```bash
# Clonar repositorio
git clone https://github.com/Panteralives/-api-escaner-codigos-barras.git
cd api-escaner-codigos-barras

# Instalar dependencias e inicializar
python run.py --install
python run.py --init-db

# Ejecutar API
python run.py
```

### Usar con Docker
```bash
# Construir imagen
docker build -t barcode-scanner-api .

# Ejecutar contenedor
docker run -p 8000:8000 barcode-scanner-api
```

## 📚 API Endpoints

- `GET /api/v1/productos/` - Listar productos
- `POST /api/v1/productos/` - Crear producto (requiere auth)
- `GET /api/v1/productos/{codigo}` - Obtener producto específico
- `POST /api/v1/scan/camera` - Escanear desde cámara
- `POST /api/v1/scan/image` - Escanear desde imagen
- `POST /api/v1/auth/login` - Autenticación

**Documentación completa:** `http://localhost:8000/docs`

## 🧪 Testing

```bash
# Ejecutar todos los tests
python -m pytest tests/ -v

# Tests con coverage
python -m pytest tests/ --cov=src
```

## 💡 Casos de Uso

- **Punto de Venta (POS)** - Escaneo rápido de productos
- **Gestión de Inventario** - Control de stock en tiempo real
- **Sistemas de Almacén** - Seguimiento de productos
- **Aplicaciones Retail** - Integración en tiendas

## 🔒 Seguridad

- Autenticación JWT implementada
- Variables de entorno para configuración sensible
- Validación de datos con Pydantic
- Rate limiting en endpoints críticos

## 📈 Rendimiento

- **FastAPI** - Una de las frameworks más rápidas de Python
- **Async/Await** - Operaciones no bloqueantes
- **Caching** - Optimización de consultas frecuentes
- **Docker** - Despliegue eficiente y escalable

---

**Desarrollado por:** [Ivan Pantera](https://github.com/Panteralives)

*Proyecto desarrollado como demostración de habilidades en desarrollo full-stack, integración de hardware, y arquitectura de APIs modernas.*