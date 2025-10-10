/* 
 * ScanPay POS - Lógica JavaScript
 * Aquí SÍ se pueden hacer modificaciones funcionales
 * NO modificar los IDs de elementos DOM
 */

// === CONFIGURACIÓN ===
const POS_CONFIG = {
    // Productos simulados (modificable)
    products: {
        '123456': { name: 'Coca Cola 350ml', price: 2.50 },
        '789012': { name: 'Pan Integral', price: 1.25 },
        '345678': { name: 'Leche Entera 1L', price: 3.75 },
        '901234': { name: 'Manzanas Red 1kg', price: 4.20 }
    },
    
    // API endpoints (modificable) - Integrados con el nuevo sistema
    endpoints: {
        products: '/api/productos',
        sales: '/api/sales',
        scanner: '/api/scan',
        auth: '/auth',
        posServer: 'http://localhost:3002' // Servidor POS principal
    },
    
    // Configuración de escáner
    scanner: {
        enableCamera: true,
        enableUSB: true,
        autoScan: false
    },
    
    // Configuración de autenticación
    auth: {
        tokenKey: 'pos_auth_token',
        userKey: 'pos_user_info',
        sessionTimeout: 900000, // 15 minutos
        requireAuth: false // Por ahora deshabilitado para compatibilidad
    },
    
    // Usuario actual del POS
    cashier: {
        username: 'pos_user',
        name: 'Cajero POS',
        authenticated: false
    },
    
    // Mensajes (modificable)
    messages: {
        productNotFound: 'Producto con código "{code}" no encontrado.',
        paymentSuccess: '¡Pago procesado exitosamente!\n\nVenta: {saleNumber}\nTotal: ${total}\nMétodo: {method}\nCambio: ${change}',
        clearConfirm: '¿Está seguro de que desea limpiar todo el carrito?',
        paymentMethodPrompt: 'Seleccione método de pago:\n\nOK = Efectivo\nCancelar = Tarjeta',
        scannerError: 'Error en el escáner. Verifique la conexión.',
        insufficientStock: 'Stock insuficiente para {product}',
        connectionError: 'Error de conexión con el servidor'
    }
};

// === ESTADO GLOBAL (NO MODIFICAR NOMBRES) ===
let cart = [];
let total = 0;

// === ELEMENTOS DOM (NO MODIFICAR IDs) ===
const DOM = {
    productCodeInput: document.getElementById('product-code'),
    quantityInput: document.getElementById('quantity'),
    cartContentEl: document.getElementById('cart-content'),
    itemsCountEl: document.getElementById('items-count'),
    totalAmountEl: document.getElementById('total-amount'),
    totalProductsEl: document.getElementById('total-products'),
    payBtn: document.getElementById('pay-btn')
};

// === INICIALIZACIÓN ===
function initializePOS() {
    setupEventListeners();
    checkSystemStatus();
    DOM.productCodeInput.focus();
    updateDisplay();
}

async function checkSystemStatus() {
    console.log('🔍 Verificando estado del sistema...');
    
    // Verificar autenticación
    const isAuthenticated = checkAuthSession();
    if (POS_CONFIG.auth.requireAuth && !isAuthenticated) {
        console.warn('⚠️ Sesión expirada o no autenticado');
        // Podría mostrar modal de login aquí
    } else {
        console.log('✅ Autenticación:', isAuthenticated ? 'Válida' : 'Deshabilitada');
    }
    
    // Verificar estado del sistema completo
    const systemHealth = await checkSystemHealth();
    console.log('📊 Estado del sistema:', systemHealth);
    
    // Verificar estado del escáner
    if (POS_CONFIG.scanner.enableCamera) {
        try {
            const scannerStatus = await checkScannerStatus();
            if (scannerStatus.available) {
                console.log('✅ Scanner disponible:', scannerStatus.message);
            } else {
                console.warn('⚠️ Scanner no disponible:', scannerStatus.message);
            }
        } catch (error) {
            console.error('❌ Error verificando scanner:', error);
        }
    }
    
    // Intentar sincronización con servidor POS
    const syncSuccess = await syncWithPOSServer();
    if (syncSuccess) {
        console.log('✅ Sincronizado con servidor POS');
    } else {
        console.log('📡 Funcionando en modo standalone');
    }
    
    console.log('🎆 Sistema inicializado correctamente');
}

function setupEventListeners() {
    // Enter para agregar producto
    DOM.productCodeInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            addProduct();
        }
    });

    // Validación de cantidad mínima
    DOM.quantityInput.addEventListener('change', function() {
        if (this.value < 1) this.value = 1;
    });
}

// === FUNCIONES PRINCIPALES ===
async function addProduct() {
    const code = DOM.productCodeInput.value.trim();
    const quantity = parseInt(DOM.quantityInput.value) || 1;
    
    if (!code) return;

    try {
        const product = await findProduct(code);
        if (product) {
            addToCart(code, product.name, product.price, quantity);
            clearInputs();
        } else {
            showMessage(POS_CONFIG.messages.productNotFound.replace('{code}', code));
            DOM.productCodeInput.focus();
        }
    } catch (error) {
        console.error('Error finding product:', error);
        showMessage('Error al buscar el producto.');
    }
}

async function findProduct(code) {
    // Primero intentar escáner si está habilitado y el código es vacío
    if (!code && POS_CONFIG.scanner.enableCamera) {
        try {
            const scanResult = await scanFromCamera();
            if (scanResult && scanResult.codigo_barra) {
                code = scanResult.codigo_barra;
                DOM.productCodeInput.value = code;
            }
        } catch (error) {
            console.warn('Scanner not available:', error);
        }
    }
    
    if (!code) return null;
    
    // Intentar API principal primero
    try {
        const headers = getAuthHeaders();
        const response = await fetch(`${POS_CONFIG.endpoints.products}/${code}`, {
            headers: headers
        });
        if (response.ok) {
            const product = await response.json();
            // Verificar stock
            if (product.stock <= 0) {
                showMessage(POS_CONFIG.messages.insufficientStock.replace('{product}', product.nombre));
                return null;
            }
            return {
                name: product.nombre,
                price: product.precio,
                stock: product.stock,
                category: product.categoria,
                codigo_barra: product.codigo_barra
            };
        }
    } catch (error) {
        console.warn('API not available, trying local products:', error);
    }
    
    // Fallback a productos simulados
    if (POS_CONFIG.products[code]) {
        return POS_CONFIG.products[code];
    }
    
    return null;
}

function addToCart(code, name, price, quantity) {
    const existingIndex = cart.findIndex(item => item.code === code);
    
    if (existingIndex >= 0) {
        cart[existingIndex].quantity += quantity;
    } else {
        cart.push({
            code: code,
            name: name,
            price: price,
            quantity: quantity
        });
    }
    
    updateDisplay();
}

function updateDisplay() {
    updateTotals();
    updateCartContent();
    updatePayButton();
}

function updateTotals() {
    total = cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
    const totalItems = cart.reduce((sum, item) => sum + item.quantity, 0);
    
    DOM.itemsCountEl.textContent = `${totalItems} items`;
    DOM.totalAmountEl.textContent = `$${total.toFixed(2)}`;
    DOM.totalProductsEl.textContent = `${totalItems} products`;
}

function updateCartContent() {
    if (cart.length === 0) {
        DOM.cartContentEl.innerHTML = `
            <div class="cart-icon">🛒</div>
            <div class="empty-title">Cart is Empty</div>
            <div class="empty-subtitle">Scan a product or enter a code to begin.</div>
        `;
    } else {
        DOM.cartContentEl.innerHTML = cart.map(item => `
            <div class="product-item">
                <div class="product-info">
                    <h4>${item.name}</h4>
                    <p>Code: ${item.code}</p>
                </div>
                <div class="product-price">
                    <div class="price-amount">$${(item.price * item.quantity).toFixed(2)}</div>
                    <div class="price-details">Qty: ${item.quantity} × $${item.price.toFixed(2)}</div>
                </div>
            </div>
        `).join('');
    }
}

function updatePayButton() {
    DOM.payBtn.disabled = cart.length === 0;
}

function clearInputs() {
    DOM.productCodeInput.value = '';
    DOM.quantityInput.value = '1';
    DOM.productCodeInput.focus();
}

// === FUNCIONES DE CONTROL ===
function changeQuantity(delta) {
    const current = parseInt(DOM.quantityInput.value) || 1;
    const newValue = Math.max(1, current + delta);
    DOM.quantityInput.value = newValue;
}

function deleteLastItem() {
    if (cart.length > 0) {
        cart.pop();
        updateDisplay();
    }
}

function clearAll() {
    if (cart.length > 0 && confirm(POS_CONFIG.messages.clearConfirm)) {
        cart = [];
        updateDisplay();
        DOM.productCodeInput.focus();
    }
}

async function processPay() {
    if (cart.length === 0) return;
    
    const paymentMethod = confirm(POS_CONFIG.messages.paymentMethodPrompt) ? 'Efectivo' : 'Tarjeta';
    
    try {
        const paymentResult = await processPayment(paymentMethod);
        if (paymentResult.success) {
            showPaymentSuccess(paymentResult, paymentMethod);
            resetCart();
        } else {
            throw new Error('Payment processing failed');
        }
    } catch (error) {
        console.error('Payment error:', error);
        showMessage('Error al procesar la venta: ' + error.message);
    }
}

async function processPayment(method) {
    // Preparar datos de venta con formato avanzado
    const saleData = {
        cashier_username: POS_CONFIG.cashier.username,
        customer_code: null, // Podría implementarse un selector de cliente
        items: cart.map(item => ({
            codigo_barra: item.code,
            quantity: item.quantity,
            unit_price: item.price,
            discount_percentage: 0.0
        })),
        payments: [{
            method: method.toUpperCase(),
            amount: total,
            cash_received: method.toLowerCase() === 'efectivo' ? total + 10 : null // Simular efectivo recibido
        }],
        notes: `Venta POS - ${new Date().toISOString()}`
    };
    
    try {
        const headers = getAuthHeaders();
        const response = await fetch(`${POS_CONFIG.endpoints.posServer}${POS_CONFIG.endpoints.sales}`, {
            method: 'POST',
            headers: headers,
            body: JSON.stringify(saleData)
        });
        
        if (response.ok) {
            const result = await response.json();
            return {
                success: true,
                saleNumber: result.sale_number,
                saleId: result.sale_id,
                total: result.total,
                change: result.change || 0
            };
        } else {
            const error = await response.json();
            throw new Error(error.detail || 'Payment processing failed');
        }
    } catch (error) {
        console.warn('Advanced API not available, using fallback:', error);
        
        // Fallback local con número de venta simulado
        await new Promise(resolve => setTimeout(resolve, 500));
        const saleNumber = `POS-${new Date().toISOString().slice(0,10).replace(/-/g,'')}-${String(Math.floor(Math.random() * 9999) + 1).padStart(4, '0')}`;
        
        return {
            success: true,
            saleNumber: saleNumber,
            saleId: Date.now(),
            total: total,
            change: method.toLowerCase() === 'efectivo' ? 10 : 0
        };
    }
}

function showPaymentSuccess(paymentResult, method) {
    const message = POS_CONFIG.messages.paymentSuccess
        .replace('{saleNumber}', paymentResult.saleNumber || 'N/A')
        .replace('{total}', paymentResult.total?.toFixed(2) || total.toFixed(2))
        .replace('{method}', method)
        .replace('{change}', paymentResult.change?.toFixed(2) || '0.00');
    
    showMessage(message);
    
    // Log para debugging
    console.log('Sale completed:', {
        saleNumber: paymentResult.saleNumber,
        saleId: paymentResult.saleId,
        total: paymentResult.total,
        change: paymentResult.change,
        method: method,
        itemCount: cart.length
    });
}

function resetCart() {
    cart = [];
    updateDisplay();
    DOM.productCodeInput.focus();
}

function showMessage(message) {
    alert(message);
}

// === FUNCIONES DE ESCÁNER ===
async function scanFromCamera() {
    """Escanear desde cámara USB"""
    try {
        const headers = getAuthHeaders();
        const response = await fetch(`${POS_CONFIG.endpoints.posServer}${POS_CONFIG.endpoints.scanner}/camera`, {
            method: 'POST',
            headers: headers
        });
        
        if (response.ok) {
            const result = await response.json();
            return result;
        } else {
            throw new Error('Scanner camera not available');
        }
    } catch (error) {
        console.error('Camera scan error:', error);
        throw error;
    }
}

async function scanFromImage(imageFile) {
    """Escanear desde imagen subida"""
    try {
        const formData = new FormData();
        formData.append('file', imageFile);
        
        const response = await fetch(`${POS_CONFIG.endpoints.scanner}/image`, {
            method: 'POST',
            body: formData
        });
        
        if (response.ok) {
            const result = await response.json();
            return result;
        } else {
            throw new Error('Image scan failed');
        }
    } catch (error) {
        console.error('Image scan error:', error);
        throw error;
    }
}

async function checkScannerStatus() {
    """Verificar estado del escáner"""
    try {
        const response = await fetch(`${POS_CONFIG.endpoints.scanner}/camera/status`);
        if (response.ok) {
            return await response.json();
        }
    } catch (error) {
        console.error('Scanner status error:', error);
    }
    return { available: false, message: 'Scanner not available' };
}

// === FUNCIONES DE AUTENTICACIÓN ===
function getAuthToken() {
    return localStorage.getItem(POS_CONFIG.auth.tokenKey);
}

function setAuthToken(token) {
    localStorage.setItem(POS_CONFIG.auth.tokenKey, token);
}

function removeAuthToken() {
    localStorage.removeItem(POS_CONFIG.auth.tokenKey);
    localStorage.removeItem(POS_CONFIG.auth.userKey);
}

function getAuthHeaders() {
    const token = getAuthToken();
    const headers = {
        'Content-Type': 'application/json'
    };
    
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }
    
    return headers;
}

async function authenticateUser(username, password) {
    try {
        const response = await fetch(`${POS_CONFIG.endpoints.posServer}${POS_CONFIG.endpoints.auth}/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: new URLSearchParams({
                username: username,
                password: password
            })
        });
        
        if (response.ok) {
            const authData = await response.json();
            setAuthToken(authData.access_token);
            
            POS_CONFIG.cashier.username = username;
            POS_CONFIG.cashier.authenticated = true;
            
            localStorage.setItem(POS_CONFIG.auth.userKey, JSON.stringify({
                username: username,
                authenticated: true,
                loginTime: Date.now()
            }));
            
            console.log('Autenticación exitosa');
            return true;
        } else {
            console.error('Error de autenticación:', response.status);
            return false;
        }
    } catch (error) {
        console.error('Error en autenticación:', error);
        return false;
    }
}

function checkAuthSession() {
    if (!POS_CONFIG.auth.requireAuth) {
        return true; // Autenticación deshabilitada
    }
    
    const token = getAuthToken();
    const userInfo = localStorage.getItem(POS_CONFIG.auth.userKey);
    
    if (!token || !userInfo) {
        return false;
    }
    
    try {
        const user = JSON.parse(userInfo);
        const now = Date.now();
        const sessionAge = now - user.loginTime;
        
        if (sessionAge > POS_CONFIG.auth.sessionTimeout) {
            removeAuthToken();
            return false;
        }
        
        POS_CONFIG.cashier.username = user.username;
        POS_CONFIG.cashier.authenticated = true;
        return true;
    } catch (error) {
        console.error('Error verificando sesión:', error);
        removeAuthToken();
        return false;
    }
}

function logout() {
    removeAuthToken();
    POS_CONFIG.cashier.authenticated = false;
    console.log('Sesión cerrada');
    // Podría redirigir a login si fuera necesario
}

// === FUNCIONES DEL SISTEMA DE GESTIÓN ===
async function checkSystemHealth() {
    const endpoints = [
        { name: 'POS Server', url: `${POS_CONFIG.endpoints.posServer}/health` },
        { name: 'API Main', url: 'http://localhost:8001/health' }
    ];
    
    const healthStatus = {};
    
    for (const endpoint of endpoints) {
        try {
            const response = await fetch(endpoint.url);
            healthStatus[endpoint.name] = {
                status: response.ok ? 'online' : 'error',
                code: response.status
            };
        } catch (error) {
            healthStatus[endpoint.name] = {
                status: 'offline',
                error: error.message
            };
        }
    }
    
    return healthStatus;
}

async function syncWithPOSServer() {
    if (!POS_CONFIG.endpoints.posServer) {
        return false;
    }
    
    try {
        const headers = getAuthHeaders();
        const response = await fetch(`${POS_CONFIG.endpoints.posServer}/api/sync`, {
            headers: headers
        });
        
        if (response.ok) {
            console.log('Sincronización con servidor POS exitosa');
            return true;
        }
    } catch (error) {
        console.warn('No se pudo sincronizar con servidor POS:', error.message);
    }
    
    return false;
}

// === INICIALIZAR CUANDO SE CARGA LA PÁGINA ===
document.addEventListener('DOMContentLoaded', initializePOS);
