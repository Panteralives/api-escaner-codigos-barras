# 🔍 API Escáner de Códigos de Barras

Una API completa para escanear códigos de barras usando Python, FastAPI, OpenCV y Streamlit. Incluye integración con hardware real (cámaras USB), autenticación JWT, y un frontend interactivo.

## ✨ Características

- 🚀 **API REST rápida** con FastAPI y documentación automática
- 📱 **Escaneo real** de códigos de barras desde cámara USB o imágenes
- 🔐 **Autenticación JWT** para endpoints protegidos
- 📦 **Gestión de productos** con operaciones CRUD completas
- 🎨 **Frontend interactivo** con Streamlit
- 🗄️ **Base de datos SQLite** con SQLAlchemy ORM
- 🧪 **Tests automatizados** con pytest
- 🐳 **Containerización** con Docker
- 📊 **Historial de escaneos** y métricas

## 🚀 Inicio Rápido

### 1. Instalar dependencias
```bash
python run.py --install
```

### 2. Configurar entorno
```bash
copy .env.example .env
```

### 3. Inicializar base de datos
```bash
python run.py --init-db
```

### 4. Ejecutar API
```bash
python run.py
```

### 5. Ejecutar frontend (nueva terminal)
```bash
python run.py --frontend
```

🎉 **¡Listo!**
- API: http://localhost:8000
- Documentación: http://localhost:8000/docs
- Frontend: http://localhost:8501

## 🔧 Comandos Disponibles

| Comando | Descripción |
|---------|-------------|
| `python run.py` | Ejecutar API |
| `python run.py --frontend` | Ejecutar frontend Streamlit |
| `python run.py --init-db` | Inicializar base de datos |
| `python run.py --check-camera` | Verificar cámara USB |
| `python run.py --install` | Instalar dependencias |
| `python run.py --info` | Mostrar información del proyecto |
| `python -m pytest tests/` | Ejecutar tests |

## 📱 Uso con Hardware Real

### Conectar Cámara USB
1. Conecta una webcam USB
2. Verifica disponibilidad: `python run.py --check-camera`
3. ¡Ya puedes escanear códigos reales!

### Probar Escaneo
```bash
# Via API
curl -X POST http://localhost:8000/api/v1/scan/camera

# Via frontend
# Ve a http://localhost:8501 > Escanear > Desde Cámara
```

## 🏗️ Arquitectura

```
src/
├── api/              # FastAPI application
│   ├── main.py       # Main app and lifespan events
│   ├── schemas.py    # Pydantic models for validation
│   ├── auth.py       # JWT authentication
│   └── routes/       # API endpoints
├── db/               # Database layer
│   ├── models.py     # SQLAlchemy models
│   ├── database.py   # DB connection and session
│   └── init_db.py    # Database initialization
├── scanner/          # Barcode scanning logic
│   └── barcode_scanner.py  # OpenCV + pyzbar integration
└── frontend/         # Streamlit web interface
    └── streamlit_app.py    # Complete web app
```

## 📊 API Endpoints

### Productos
- `GET /api/v1/productos/` - Listar productos
- `GET /api/v1/productos/{codigo}` - Obtener producto por código
- `POST /api/v1/productos/` - Crear producto 🔒
- `PUT /api/v1/productos/{codigo}` - Actualizar producto 🔒
- `DELETE /api/v1/productos/{codigo}` - Eliminar producto 🔒

### Escáner
- `POST /api/v1/scan/image` - Escanear desde imagen
- `POST /api/v1/scan/camera` - Escanear desde cámara USB
- `GET /api/v1/scan/camera/status` - Estado de la cámara

### Autenticación
- `POST /api/v1/auth/login` - Iniciar sesión
- `POST /api/v1/auth/register` - Registrar usuario
- `GET /api/v1/auth/me` - Información del usuario actual 🔒

🔒 = Requiere autenticación JWT

## 🔐 Credenciales por Defecto

- **Usuario**: `admin`
- **Contraseña**: `admin123`

## 🧪 Testing

```bash
# Ejecutar todos los tests
python -m pytest tests/ -v

# Test específico
python -m pytest tests/test_api.py::TestAuth::test_login_success -v

# Con coverage
python -m pytest tests/ --cov=src
```

## 🐳 Docker

```bash
# Construir imagen
docker build -t barcode-scanner-api .

# Ejecutar contenedor
docker run -p 8000:8000 barcode-scanner-api
```

## 📚 Aprendizaje

Este proyecto está diseñado para aprender Python **"haciendo"**. Ve la [Guía de Aprendizaje](docs/GUIA_APRENDIZAJE.md) para:

- 📖 Explicaciones paso a paso
- 🔬 Ejercicios prácticos
- 🧠 Conceptos clave explicados
- 🎯 Proyectos reales para practicar

## 🛠️ Tecnologías Utilizadas

- **[FastAPI](https://fastapi.tiangolo.com/)** - Framework web moderno y rápido
- **[SQLAlchemy](https://sqlalchemy.org/)** - ORM de Python
- **[OpenCV](https://opencv.org/)** - Procesamiento de imágenes
- **[pyzbar](https://pypi.org/project/pyzbar/)** - Decodificación de códigos de barras
- **[Streamlit](https://streamlit.io/)** - Framework para aplicaciones web
- **[JWT](https://jwt.io/)** - Autenticación segura
- **[Docker](https://docker.com/)** - Containerización
- **[pytest](https://pytest.org/)** - Testing framework

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 🆘 Solución de Problemas

### Cámara no detectada
- Verifica que la cámara esté conectada
- Cierra otras aplicaciones que usen la cámara
- Ejecuta: `python run.py --check-camera`

### Error de dependencias
- Ejecuta: `python run.py --install`
- Verifica que tengas Python 3.8+

### Base de datos corrupta
- Elimina `barcode_scanner.db`
- Ejecuta: `python run.py --init-db`

---

⭐ Si te gusta este proyecto, ¡dale una estrella en GitHub!

📧 ¿Preguntas? Abre un issue en GitHub.
