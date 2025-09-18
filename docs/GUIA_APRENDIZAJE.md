# 🎯 Guía de Aprendizaje: API Escáner de Códigos de Barras

Esta guía te llevará paso a paso por el desarrollo y uso de una API completa para escanear códigos de barras usando Python. Está diseñada para aprender **"haciendo"** - cada fase incluye código funcional que puedes probar inmediatamente.

## 📋 ¿Qué vas a aprender?

- **FastAPI**: Crear APIs REST modernas y rápidas
- **SQLAlchemy + SQLite**: Gestión de bases de datos con ORM
- **OpenCV + pyzbar**: Procesar imágenes y escanear códigos reales
- **Streamlit**: Crear interfaces web interactivas
- **JWT**: Implementar autenticación segura
- **Hardware Integration**: Conectar y usar cámaras USB reales

## 🎯 Objetivo Final

Al completar esta guía tendrás:
- ✅ Una API REST completamente funcional
- ✅ Frontend web para usar la aplicación
- ✅ Integración con hardware real (cámara USB)
- ✅ Sistema de autenticación
- ✅ Base de datos con productos reales
- ✅ Tests automatizados

---

## 🏁 Fase 0: Preparación del Entorno

### Verificar Python

```powershell
python --version
# Debe ser Python 3.8 o superior
```

### Instalar Dependencias

```powershell
# Desde el directorio del proyecto
python run.py --install

# O manualmente:
pip install -r requirements.txt
```

### Crear Archivo de Entorno

```powershell
# Copia el archivo de ejemplo
copy .env.example .env
```

**🧠 Concepto Clave**: Los archivos `.env` permiten configurar aplicaciones sin hardcodear valores en el código.

---

## 🗄️ Fase 1: Base de Datos y Modelos

### 1.1 Entender la Estructura de la Base de Datos

Abre `src/db/models.py` y examina los modelos:

```python
class Producto(Base):
    codigo_barra = Column(String, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    precio = Column(Float, nullable=False)
    # ... más campos
```

**🧠 Conceptos que aprendes aquí**:
- **ORM (Object-Relational Mapping)**: Mapear tablas de BD a clases Python
- **Primary Keys**: Claves primarias para identificar registros únicos
- **Indices**: Acelerar búsquedas en base de datos
- **Relaciones**: Cómo las tablas se conectan entre sí

### 1.2 Inicializar la Base de Datos

```powershell
python run.py --init-db
```

**¿Qué hace esto?**
1. Crea las tablas en SQLite
2. Inserta 8 productos de ejemplo
3. Crea un usuario administrador (admin/admin123)

### 1.3 Explorar la Base de Datos

```powershell
# Instalar sqlite3 (si no está instalado)
# En Windows, descargar desde https://sqlite.org/download.html

# Abrir la base de datos
sqlite3 barcode_scanner.db

# Comandos SQL para explorar:
.tables
SELECT * FROM productos;
SELECT * FROM usuarios;
.quit
```

**🔬 Ejercicio Práctico**:
1. Abre la base de datos con SQLite
2. Cuenta cuántos productos hay por categoría
3. Encuentra el producto más caro

```sql
SELECT categoria, COUNT(*) FROM productos GROUP BY categoria;
SELECT nombre, precio FROM productos ORDER BY precio DESC LIMIT 1;
```

---

## 🚀 Fase 2: API REST con FastAPI

### 2.1 Iniciar la API

```powershell
python run.py
```

**Resultado esperado**:
- ✅ API ejecutándose en http://localhost:8000
- ✅ Documentación en http://localhost:8000/docs
- ✅ Health check en http://localhost:8000/health

### 2.2 Explorar la Documentación Automática

1. Ve a http://localhost:8000/docs
2. Explora los diferentes endpoints
3. Prueba el endpoint `GET /api/v1/productos/`

**🧠 Conceptos que aprendes**:
- **OpenAPI/Swagger**: Documentación automática de APIs
- **HTTP Status Codes**: 200 (OK), 404 (Not Found), 401 (Unauthorized)
- **JSON**: Formato de intercambio de datos
- **CRUD Operations**: Create, Read, Update, Delete

### 2.3 Probar Endpoints Manualmente

#### Obtener todos los productos:
```powershell
curl http://localhost:8000/api/v1/productos/
```

#### Obtener un producto específico:
```powershell
curl http://localhost:8000/api/v1/productos/7501000673209
```

#### Probar endpoint protegido (sin autenticación):
```powershell
curl -X POST http://localhost:8000/api/v1/productos/ -H "Content-Type: application/json" -d '{
    "codigo_barra": "1234567890123",
    "nombre": "Producto Test",
    "precio": 1.50
}'
```

**Resultado esperado**: Error 401 (No autorizado)

**🔬 Ejercicio Práctico**:
1. Usa la documentación en `/docs` para probar diferentes endpoints
2. Intenta obtener un producto que no existe
3. Observa los diferentes códigos de respuesta HTTP

---

## 🔐 Fase 3: Autenticación JWT

### 3.1 Entender JWT

**🧠 Conceptos**:
- **JWT (JSON Web Tokens)**: Tokens seguros para autenticación
- **Bearer Token**: Formato estándar para enviar tokens en headers
- **Hash de Contraseñas**: Nunca almacenar contraseñas en texto plano

### 3.2 Iniciar Sesión y Obtener Token

#### Usando cURL:
```powershell
curl -X POST http://localhost:8000/api/v1/auth/login -H "Content-Type: application/x-www-form-urlencoded" -d "username=admin&password=admin123"
```

#### Resultado esperado:
```json
{
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "token_type": "bearer"
}
```

### 3.3 Usar el Token para Operaciones Protegidas

```powershell
# Reemplaza TOKEN_AQUI con el token obtenido
curl -X POST http://localhost:8000/api/v1/productos/ -H "Content-Type: application/json" -H "Authorization: Bearer TOKEN_AQUI" -d '{
    "codigo_barra": "1234567890123",
    "nombre": "Mi Producto Test",
    "precio": 2.50,
    "descripcion": "Producto creado via API",
    "stock": 10,
    "categoria": "Test"
}'
```

**🔬 Ejercicio Práctico**:
1. Obtén un token JWT
2. Usa el token para crear un nuevo producto
3. Verifica que el producto fue creado consultando la lista
4. Intenta usar un token expirado o inválido

---

## 📷 Fase 4: Integración con Hardware - Escáner de Códigos

### 4.1 Verificar Hardware

```powershell
python run.py --check-camera
```

**Resultados posibles**:
- ✅ "Cámara disponible" - Puedes continuar
- ❌ "Cámara no disponible" - Sigue los pasos de solución

#### Si no tienes cámara disponible:
1. **Conecta una webcam USB**
2. **Cierra Skype, Zoom, Teams** (pueden bloquear la cámara)
3. **Verifica Device Manager** (Windows)
4. **Prueba con aplicación de cámara** del sistema

### 4.2 Probar Escaneo desde la API

#### Verificar estado de cámara via API:
```powershell
curl http://localhost:8000/api/v1/scan/camera/status
```

#### Escanear desde cámara:
```powershell
curl -X POST http://localhost:8000/api/v1/scan/camera
```

**🧠 Conceptos que aprendes**:
- **OpenCV**: Biblioteca para procesamiento de imágenes
- **pyzbar**: Decodificación de códigos de barras
- **Integración Hardware-Software**: Conectar dispositivos físicos con código
- **Procesamiento de Imágenes**: Convertir imágenes a datos útiles

### 4.3 Preparar Códigos de Barras para Probar

**Opciones para obtener códigos**:

1. **Productos Físicos**: Usa productos reales de tu casa
2. **Códigos Online**: Busca "EAN-13 barcode generator"
3. **Códigos de Ejemplo**: Los productos en la BD tienen códigos reales

**Códigos de productos en la base de datos**:
- `7501000673209` - Coca Cola 600ml
- `7501000673308` - Pepsi 600ml  
- `7501000125643` - Leche Entera Lala 1L

### 4.4 Escanear Códigos Reales

1. **Abre un generador de códigos de barras online**
2. **Genera el código** `7501000673209`
3. **Muestra el código a tu cámara**
4. **Ejecuta el escaneo**:
   ```powershell
   curl -X POST http://localhost:8000/api/v1/scan/camera
   ```

**Resultado esperado**:
```json
{
    "codigo_barra": "7501000673209",
    "tipo_codigo": "EAN13",
    "encontrado": true,
    "producto": {
        "codigo_barra": "7501000673209",
        "nombre": "Coca Cola 600ml",
        "precio": 1.25,
        "categoria": "Bebidas"
    },
    "timestamp": "2024-01-15T10:30:45"
}
```

**🔬 Ejercicio Práctico**:
1. Escanea al menos 3 códigos diferentes
2. Intenta escanear un código que NO está en la base de datos
3. Observa cómo cambia la respuesta cuando el producto no se encuentra

---

## 🎨 Fase 5: Frontend con Streamlit

### 5.1 Iniciar el Frontend

```powershell
# En una nueva terminal (mantén la API ejecutándose)
python run.py --frontend
```

**Resultado esperado**:
- ✅ Frontend en http://localhost:8501
- ✅ Interfaz gráfica funcionando
- ✅ Conexión con la API verificada

### 5.2 Explorar la Interfaz

1. **Dashboard**: Ve métricas generales y estado de la cámara
2. **Escanear**: Prueba escaneo desde cámara e imagen
3. **Productos**: Explora y gestiona productos
4. **Historial**: (En desarrollo)

### 5.3 Probar Funcionalidades Completas

#### Autenticación en el Frontend:
1. En el sidebar, usa: **Usuario**: `admin`, **Contraseña**: `admin123`
2. Verifica que aparezca "Sesión activa"

#### Escaneo desde Imagen:
1. Ve a la pestaña "Escanear" > "Desde Imagen"
2. Descarga una imagen de código de barras
3. Súbela y escanea

#### Gestión de Productos:
1. Ve a "Productos" > "Agregar Producto"
2. Crea un nuevo producto (requiere estar logueado)
3. Verifica que aparezca en la lista

**🧠 Conceptos que aprendes**:
- **Streamlit**: Framework para crear aplicaciones web con Python
- **Estado de Sesión**: Mantener información entre páginas
- **Integración Frontend-Backend**: Cómo las interfaces consumen APIs
- **Experiencia de Usuario**: Diseñar interfaces intuitivas

**🔬 Ejercicio Práctico**:
1. Crea al menos 2 productos nuevos usando el frontend
2. Prueba el escaneo con ambos métodos (cámara e imagen)
3. Explora todas las secciones del dashboard

---

## 🧪 Fase 6: Testing y Validación

### 6.1 Ejecutar Tests Automatizados

```powershell
# Ejecutar todos los tests
python -m pytest tests/ -v

# Ejecutar un test específico
python -m pytest tests/test_api.py::TestAuth::test_login_success -v
```

**🧠 Conceptos que aprendes**:
- **Testing Automatizado**: Verificar que el código funciona correctamente
- **Test-Driven Development**: Escribir tests antes que código
- **Assertions**: Verificar que los resultados son los esperados
- **Test Coverage**: Qué porcentaje del código está cubierto por tests

### 6.2 Entender los Tests

Examina `tests/test_api.py`:

```python
def test_login_success(self):
    """Test de login exitoso"""
    login_data = {"username": "admin", "password": "admin123"}
    response = client.post("/api/v1/auth/login", data=login_data)
    assert response.status_code == 200  # Verifica respuesta exitosa
    data = response.json()
    assert "access_token" in data       # Verifica que hay token
```

**🔬 Ejercicio Práctico**:
1. Ejecuta cada clase de tests por separado
2. Modifica un test para que falle intencionalmente
3. Crea un test nuevo para verificar que puedes obtener categorías

---

## 🐳 Fase 7: Containerización con Docker

### 7.1 Construir la Imagen Docker

```powershell
docker build -t barcode-scanner-api .
```

### 7.2 Ejecutar en Docker

```powershell
# Ejecutar el contenedor
docker run -p 8000:8000 barcode-scanner-api

# Ejecutar en background
docker run -d -p 8000:8000 --name barcode-scanner barcode-scanner-api
```

**🧠 Conceptos que aprendes**:
- **Containerización**: Empaquetar aplicaciones con sus dependencias
- **Docker**: Plataforma para crear y ejecutar contenedores
- **Portabilidad**: Ejecutar la misma aplicación en cualquier sistema
- **Aislamiento**: Separar aplicaciones de su entorno

**🔬 Ejercicio Práctico**:
1. Construye la imagen Docker
2. Ejecuta el contenedor y verifica que la API funciona
3. Para el contenedor y reinícialo

---

## 📊 Fase 8: Integración Completa - Proyecto Real

### 8.1 Escenario: Sistema para Tienda

**Objetivo**: Simular un sistema real de punto de venta

#### Pasos:
1. **Preparar productos reales**: Busca 5-10 productos físicos en tu casa
2. **Obtener códigos**: Usa los códigos de barras reales de esos productos
3. **Registrar en sistema**: Usa el frontend para agregar cada producto
4. **Simular ventas**: Escanea productos usando la cámara
5. **Gestionar inventario**: Actualiza stocks usando la API

### 8.2 Script de Automatización

Crea un script `test_integration.py`:

```python
import requests
import time

API_BASE = "http://localhost:8000/api/v1"

# Login
login_response = requests.post(f"{API_BASE}/auth/login", 
    data={"username": "admin", "password": "admin123"})
token = login_response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# Crear productos
productos_test = [
    {"codigo_barra": "1111111111111", "nombre": "Producto A", "precio": 5.50},
    {"codigo_barra": "2222222222222", "nombre": "Producto B", "precio": 3.25},
]

for producto in productos_test:
    response = requests.post(f"{API_BASE}/productos/", 
        json=producto, headers=headers)
    print(f"Producto creado: {response.status_code}")

# Simular escaneos
for i in range(3):
    response = requests.post(f"{API_BASE}/scan/camera")
    print(f"Escaneo {i+1}: {response.json()}")
    time.sleep(2)
```

### 8.3 Métricas y Monitoreo

**Cosas a verificar**:
1. **Performance**: ¿Qué tan rápido responde la API?
2. **Precision**: ¿El escáner detecta códigos correctamente?
3. **Reliability**: ¿La aplicación se mantiene estable?
4. **Usability**: ¿Es fácil usar el frontend?

**🔬 Ejercicio Final**:
1. Implementa el escenario completo de tienda
2. Documenta cualquier problema encontrado
3. Propón mejoras para cada componente

---

## 🎯 Conceptos Clave Aprendidos

### **Backend Development**
- ✅ **API REST**: Diseño de endpoints RESTful
- ✅ **FastAPI**: Framework moderno para APIs
- ✅ **SQLAlchemy**: ORM para base de datos
- ✅ **Authentication**: JWT y seguridad
- ✅ **Validation**: Pydantic schemas
- ✅ **Error Handling**: Manejo apropiado de errores

### **Computer Vision & Hardware**
- ✅ **OpenCV**: Procesamiento de imágenes
- ✅ **pyzbar**: Decodificación de códigos de barras
- ✅ **Camera Integration**: Usar hardware real
- ✅ **Image Processing**: Convertir imágenes a datos

### **Frontend Development**
- ✅ **Streamlit**: Interfaces web con Python
- ✅ **State Management**: Manejo de estado de sesión
- ✅ **UI/UX**: Diseño de experiencia de usuario
- ✅ **API Integration**: Conectar frontend con backend

### **DevOps & Testing**
- ✅ **Docker**: Containerización de aplicaciones
- ✅ **pytest**: Testing automatizado
- ✅ **Environment Management**: Configuración con variables
- ✅ **Logging**: Registro y monitoreo de aplicaciones

### **Database Design**
- ✅ **Database Modeling**: Diseño de esquemas
- ✅ **Indexing**: Optimización de consultas
- ✅ **Migrations**: Manejo de cambios en BD
- ✅ **Data Seeding**: Inicialización con datos de ejemplo

---

## 🚀 Próximos Pasos

### **Mejoras Sugeridas**
1. **WebSocket**: Escaneo en tiempo real
2. **Multi-Camera**: Soporte para múltiples cámaras
3. **ML Integration**: Detección de productos por imagen
4. **Mobile App**: Aplicación móvil nativa
5. **Analytics**: Dashboard de métricas avanzadas
6. **Backup System**: Respaldo automático de datos

### **Proyectos Relacionados**
1. **Sistema de Inventario**: Expande para manejar almacenes
2. **POS System**: Sistema completo de punto de venta
3. **QR Menu**: Sistema de menú digital para restaurantes
4. **Asset Tracking**: Seguimiento de activos empresariales

### **Recursos para Continuar Aprendiendo**
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **OpenCV Tutorials**: https://opencv.org/courses/
- **Streamlit Gallery**: https://streamlit.io/gallery
- **Docker Learning**: https://docs.docker.com/get-started/

---

## 🎉 ¡Felicidades!

Has completado una aplicación completa que integra:
- ✅ Backend API profesional
- ✅ Frontend interactivo
- ✅ Integración con hardware real
- ✅ Base de datos funcional
- ✅ Autenticación segura
- ✅ Tests automatizados
- ✅ Containerización

