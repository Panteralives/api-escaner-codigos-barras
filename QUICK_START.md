# 🚀 GUÍA DE INICIO RÁPIDO - Sistema POS InventarioBarras

**¡Pon en marcha tu Sistema POS Avanzado en menos de 5 minutos!**

## ⚡ **Instalación Express**

### 📋 **Prerrequisitos**
- Windows 10/11
- Python 3.11+ ([Descargar aquí](https://www.python.org/downloads/))

### 🔧 **Pasos de Instalación**

1. **Clonar el proyecto:**
   ```bash
   git clone https://github.com/Panteralives/api-escaner-codigos-barras.git
   cd api-escaner-codigos-barras
   ```

2. **Instalar dependencias automáticamente:**
   ```bash
   python run.py --install
   ```

3. **Inicializar base de datos:**
   ```bash
   python run.py --init-db
   ```

4. **¡Listo! Iniciar el sistema:**
   ```bash
   # Opción 1: Sistema completo (RECOMENDADO)
   python run.py --production
   
   # Opción 2: Solo API para desarrollo
   python run.py
   
   # Opción 3: POS Avanzado completo
   python src/api/main_advanced.py
   ```

## 🌐 **URLs Principales**

Una vez iniciado, accede a:

| Servicio | URL | Descripción |
|----------|-----|-------------|
| **🏪 POS Principal** | http://localhost:3002/pos | **Interfaz de ventas completa** |
| **📊 Dashboard** | http://localhost:3002/dashboard | Panel ejecutivo |
| **📚 API Docs** | http://localhost:8000/docs | Documentación automática |
| **🎨 Streamlit** | http://localhost:8501 | Interfaz de desarrollo |

## 👥 **Usuarios por Defecto**

| Usuario | Contraseña | Rol | Acceso |
|---------|------------|-----|---------|
| `admin` | `admin123` | Administrador | **Completo** |
| `manager` | `manager123` | Gerente | Operaciones + Reportes |
| `cajero1` | `cajero123` | Cajero | Solo ventas |
| `inventario` | `inventario123` | Inventario | Solo productos |

## 🔧 **Comandos Útiles**

```bash
# Ver información del proyecto
python run.py --info

# Verificar hardware conectado
python run.py --check-hardware

# Probar scanner USB
python run.py --test-scanner

# Configurar inicio automático
python run.py --setup-autostart

# Modo producción optimizado
python autostart_pos_system.py
```

## 🏪 **Características Principales**

### ✅ **¿Qué Obtienes?**
- 🛒 **Sistema POS completo** con ventas y caja
- 📊 **Dashboard ejecutivo** con métricas en tiempo real
- 👥 **Multi-usuario** con roles y permisos
- 💾 **Backup automático** diario
- 🔍 **Escaneo de códigos** (cámara + USB)
- 🖨️ **Impresión de tickets** ESC/POS
- 📱 **Interfaz web responsive**
- 🔐 **Auditoría completa** de acciones

### 🎯 **Casos de Uso Típicos**
- **Tienda retail** con productos y clientes
- **Farmacia** con control de inventario
- **Mini market** con múltiples cajeros
- **Restaurante** con sistema de órdenes
- **Almacén** con control de stock

## 🛠️ **Solución de Problemas**

### ❌ **Error: "No module named..."**
```bash
# Reinstalar dependencias
python run.py --install
pip install -r requirements.txt
```

### ❌ **Error: "Database not found"**
```bash
# Recrear base de datos
python run.py --init-db
```

### ❌ **Error: "Port already in use"**
- Cerrar otras instancias del programa
- Reiniciar sistema si es necesario
- Usar puertos alternativos en configuración

### ❌ **Cámara no funciona**
- Verificar que la cámara esté conectada
- Cerrar otras apps que usen la cámara
- El sistema funciona sin cámara usando scanner USB

## 🎉 **¡Ya Estás Listo!**

1. **🚀 Inicia el sistema** con `python run.py --production`
2. **🌐 Abre** http://localhost:3002/pos en tu navegador
3. **🔐 Inicia sesión** con `admin` / `admin123`
4. **🛒 ¡Comienza a vender!**

## 📞 **Soporte y Documentación**

- 📚 **README completo:** [`README.md`](README.md)
- 📋 **Cambios:** [`CHANGELOG.md`](CHANGELOG.md)
- 🎯 **Problemas:** [GitHub Issues](https://github.com/Panteralives/api-escaner-codigos-barras/issues)
- 💬 **Discusiones:** [GitHub Discussions](https://github.com/Panteralives/api-escaner-codigos-barras/discussions)

---

**🏪 Sistema POS Avanzado - InventarioBarras**  
**⭐ ¡Dale una estrella en GitHub si te resulta útil!** ⭐