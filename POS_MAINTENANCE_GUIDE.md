# 🔒 Guía de Mantenimiento - ScanPay POS Frontend

## 📋 Estructura Modular

El frontend POS está dividido en **3 archivos separados** para facilitar el mantenimiento sin romper la estructura:

```
├── pos_modular.html      ← Estructura HTML (🚫 NO MODIFICAR)
├── pos_styles.css        ← Estilos visuales (✅ Modificable)
└── pos_script.js         ← Lógica funcional (✅ Modificable)
```

## ⚠️ REGLAS IMPORTANTES

### 🚫 **NO MODIFICAR JAMÁS:**
- **Estructura HTML** en `pos_modular.html`
- **IDs de elementos** (`#product-code`, `#quantity`, etc.)
- **Clases de layout** (`.main-container`, `.left-panel`, etc.)
- **Jerarquía de elementos DOM**

### ✅ **SÍ SE PUEDE MODIFICAR:**
- **Colores y fuentes** en `pos_styles.css`
- **Lógica de negocio** en `pos_script.js`
- **Mensajes de texto**
- **Productos simulados**
- **Endpoints de API**

---

## 🎨 Modificaciones Visuales

### **Archivo:** `pos_styles.css`

#### ✅ **Cambios Permitidos:**
```css
/* Cambiar colores */
.pay-button {
    background: #ff6b6b; /* Rojo en lugar de verde */
}

/* Cambiar fuentes */
body {
    font-family: 'Arial', sans-serif;
}

/* Cambiar tamaños de texto */
.total-amount {
    font-size: 3rem; /* Más grande */
}

/* Agregar efectos */
.pay-button:hover {
    transform: scale(1.05);
    box-shadow: 0 8px 16px rgba(0,0,0,0.2);
}
```

#### 🚫 **Cambios PROHIBIDOS:**
```css
/* NO cambiar displays */
.main-container {
    display: grid; /* ❌ NO! Debe ser flex */
}

/* NO cambiar estructura de flex */
.right-panel {
    flex-direction: row; /* ❌ NO! Debe ser column */
}

/* NO eliminar clases */
.actions-card {
    /* ❌ NO eliminar esta clase */
}
```

---

## ⚙️ Modificaciones Funcionales

### **Archivo:** `pos_script.js`

#### ✅ **Cambios Permitidos:**

##### **1. Agregar Productos:**
```javascript
const POS_CONFIG = {
    products: {
        '123456': { name: 'Coca Cola 350ml', price: 2.50 },
        '555555': { name: 'Nuevo Producto', price: 5.99 }, // ✅ Nuevo
        // ...más productos
    }
};
```

##### **2. Cambiar Mensajes:**
```javascript
messages: {
    productNotFound: 'Código no encontrado: {code}', // ✅ Cambiar
    paymentSuccess: 'Pago exitoso por ${total}',     // ✅ Cambiar
}
```

##### **3. Modificar API:**
```javascript
endpoints: {
    products: '/api/v2/productos',  // ✅ Cambiar endpoint
    sales: '/api/v2/ventas'         // ✅ Cambiar endpoint
}
```

##### **4. Agregar Funcionalidades:**
```javascript
// ✅ Agregar nuevas funciones
function generateReceipt() {
    console.log('Generando recibo...');
    // Nueva funcionalidad
}

// ✅ Modificar validaciones
function validateProduct(code) {
    return code.length >= 6; // Nueva validación
}
```

#### 🚫 **Cambios PROHIBIDOS:**
```javascript
// NO cambiar nombres de variables globales
let carrito = []; // ❌ NO! Debe ser 'cart'

// NO cambiar IDs de elementos DOM
const DOM = {
    inputCodigo: document.getElementById('codigo'), // ❌ NO!
    // Debe ser 'product-code'
};

// NO cambiar nombres de funciones llamadas desde HTML
function cambiarCantidad(delta) { // ❌ NO!
    // Debe ser 'changeQuantity'
}
```

---

## 🔄 Proceso de Actualización Segura

### **1. Crear Backup**
```bash
cp pos_modular.html pos_modular.html.backup
cp pos_styles.css pos_styles.css.backup  
cp pos_script.js pos_script.js.backup
```

### **2. Hacer Cambios Gradualmente**
- Cambiar **un archivo a la vez**
- Probar después de cada cambio
- Verificar que no se rompa la funcionalidad

### **3. Validar Funcionamiento**
```bash
# Abrir en navegador y probar:
# ✅ Escaneo de productos
# ✅ Controles de cantidad
# ✅ Botón de pago
# ✅ Limpiar carrito
# ✅ Borrar último item
```

### **4. Commit Cambios**
```bash
git add pos_styles.css pos_script.js
git commit -m "feat: Update POS colors and add new products"
```

---

## 🚨 Recuperación de Errores

### **Si algo se rompe:**

1. **Revertir cambios inmediatamente:**
   ```bash
   git checkout pos_styles.css pos_script.js
   ```

2. **Usar backups:**
   ```bash
   cp pos_styles.css.backup pos_styles.css
   cp pos_script.js.backup pos_script.js
   ```

3. **Verificar errores en consola:**
   - Abrir DevTools (F12)
   - Ver errores en Console
   - Revisar elementos en Elements tab

---

## 📝 Checklist de Modificaciones

Antes de hacer cambios, verificar:

- [ ] ¿Es solo un cambio visual? → `pos_styles.css`
- [ ] ¿Es solo funcionalidad? → `pos_script.js`  
- [ ] ¿No toca la estructura HTML?
- [ ] ¿No cambia IDs ni clases de layout?
- [ ] ¿Tengo backup de los archivos?
- [ ] ¿Probé en navegador después del cambio?

---

## ✨ Ejemplos de Modificaciones Comunes

### **Cambiar color del botón PAY a rojo:**
```css
/* En pos_styles.css */
.pay-button {
    background: #ef4444;
}
.pay-button:hover {
    background: #dc2626;
}
```

### **Agregar validación de código de barras:**
```javascript
// En pos_script.js
function validateBarcode(code) {
    if (code.length < 6) {
        showMessage('El código debe tener al menos 6 dígitos');
        return false;
    }
    return true;
}

// Modificar función addProduct()
async function addProduct() {
    const code = DOM.productCodeInput.value.trim();
    
    if (!validateBarcode(code)) return; // ✅ Nueva validación
    
    // ...resto del código igual
}
```

### **Cambiar moneda de $ a €:**
```javascript
// En pos_script.js, función updateTotals()
DOM.totalAmountEl.textContent = `€${total.toFixed(2)}`;
```

---

## 🎯 Contacto para Soporte

Si necesitas hacer cambios más complejos que requieran modificar la estructura HTML, contacta al desarrollador original para evitar romper el diseño.

**¡La clave es NUNCA tocar la estructura, solo el contenido y la funcionalidad!**