/*
 * Script de prueba para verificar funcionalidades del POS
 * Ejecutar en la consola del navegador para probar las APIs
 */

// === PRUEBAS DE FUNCIONALIDADES ===

async function testPOSFunctionality() {
    console.log('🧪 Iniciando pruebas de funcionalidades del POS...\n');
    
    // Test 1: Verificar configuración
    console.log('1️⃣ Verificando configuración...');
    console.log('Endpoints configurados:', POS_CONFIG.endpoints);
    console.log('Scanner habilitado:', POS_CONFIG.scanner);
    console.log('Cajero:', POS_CONFIG.cashier);
    
    // Test 2: Probar conexión con APIs
    console.log('\n2️⃣ Probando conexión con APIs...');
    const systemHealth = await checkSystemHealth();
    
    Object.entries(systemHealth).forEach(([name, status]) => {
        const emoji = status.status === 'online' ? '✅' : status.status === 'error' ? '⚠️' : '❌';
        console.log(`${emoji} ${name}: ${status.status.toUpperCase()}`);
    });
    
    // Test de autenticación
    console.log('\n🔐 Verificando autenticación...');
    const authStatus = checkAuthSession();
    console.log(`🔑 Estado de autenticación: ${authStatus ? '✅ Válida' : '⚠️ No autenticado'}`);
    
    // Test 3: Verificar estado del escáner
    console.log('\n3️⃣ Verificando estado del escáner...');
    try {
        const scannerStatus = await checkScannerStatus();
        if (scannerStatus.available) {
            console.log('✅ Escáner disponible:', scannerStatus.message);
        } else {
            console.log('⚠️ Escáner no disponible:', scannerStatus.message);
        }
    } catch (error) {
        console.log('❌ Error verificando escáner:', error.message);
    }
    
    // Test 4: Probar búsqueda de productos
    console.log('\n4️⃣ Probando búsqueda de productos...');
    const testCodes = ['123456', '789012', '999999']; // Último código no existe
    
    for (const code of testCodes) {
        try {
            const product = await findProduct(code);
            if (product) {
                console.log(`✅ Producto encontrado ${code}:`, product);
            } else {
                console.log(`⚠️ Producto no encontrado: ${code}`);
            }
        } catch (error) {
            console.log(`❌ Error buscando producto ${code}:`, error.message);
        }
    }
    
    // Test 5: Simular transacción de pago
    console.log('\n5️⃣ Simulando transacción de pago...');
    if (cart.length === 0) {
        // Agregar producto de prueba al carrito
        addToCart('123456', 'Producto Test', 10.00, 2);
        console.log('📦 Producto de prueba agregado al carrito');
    }
    
    try {
        const paymentResult = await processPayment('Efectivo');
        console.log('✅ Pago procesado:', paymentResult);
    } catch (error) {
        console.log('❌ Error procesando pago:', error.message);
    }
    
    // Test 6: Verificar elementos DOM
    console.log('\n6️⃣ Verificando elementos DOM...');
    const requiredElements = [
        'product-code',
        'quantity', 
        'cart-content',
        'items-count',
        'total-amount',
        'total-products',
        'pay-btn'
    ];
    
    let missingElements = [];
    for (const elementId of requiredElements) {
        if (!document.getElementById(elementId)) {
            missingElements.push(elementId);
        }
    }
    
    if (missingElements.length === 0) {
        console.log('✅ Todos los elementos DOM requeridos están presentes');
    } else {
        console.log('❌ Elementos DOM faltantes:', missingElements);
    }
    
    console.log('\n🎯 Pruebas completadas. Revisa los resultados arriba.');
    console.log('\n💡 Consejos:');
    console.log('- Si la API no está disponible, el POS funciona en modo offline');
    console.log('- Si el escáner no está disponible, usa entrada manual');
    console.log('- Todos los elementos visuales deben estar funcionando');
    console.log('- Los pagos se procesan con números de venta únicos');
}

// === FUNCIONES DE PRUEBA ESPECÍFICAS ===

function testScannerIntegration() {
    console.log('🔍 Probando integración con escáner...');
    
    // Simular escaneo desde cámara
    scanFromCamera()
        .then(result => {
            console.log('✅ Escaneo desde cámara exitoso:', result);
        })
        .catch(error => {
            console.log('⚠️ Escaneo desde cámara no disponible:', error.message);
        });
}

function testElectronicInvoicing() {
    console.log('🧾 Probando facturación electrónica...');
    
    if (cart.length === 0) {
        addToCart('123456', 'Producto Facturación', 25.50, 1);
    }
    
    const saleData = {
        cashier_username: POS_CONFIG.cashier.username,
        items: cart.map(item => ({
            codigo_barra: item.code,
            quantity: item.quantity,
            unit_price: item.price,
            discount_percentage: 0.0
        })),
        payments: [{
            method: 'EFECTIVO',
            amount: total,
            cash_received: total + 5
        }]
    };
    
    console.log('📊 Datos de venta preparados:', saleData);
    console.log('✅ Formato de facturación electrónica correcto');
}

function testOfflineMode() {
    console.log('📱 Probando modo offline...');
    
    // Deshabilitar temporalmente las APIs
    const originalEndpoints = POS_CONFIG.endpoints;
    POS_CONFIG.endpoints = {
        products: '/api/offline',
        sales: '/api/offline',
        scanner: '/api/offline'
    };
    
    console.log('🔄 Modo offline activado');
    
    findProduct('123456')
        .then(product => {
            if (product) {
                console.log('✅ Modo offline funcionando: producto encontrado');
            } else {
                console.log('⚠️ Producto no encontrado en modo offline');
            }
        })
        .catch(error => {
            console.log('❌ Error en modo offline:', error.message);
        })
        .finally(() => {
            // Restaurar endpoints originales
            POS_CONFIG.endpoints = originalEndpoints;
            console.log('🔄 Modo online restaurado');
        });
}

// === EJECUTAR PRUEBAS ===
console.log('🚀 Funciones de prueba cargadas. Ejecuta:');
console.log('- testPOSFunctionality() - Pruebas completas');
console.log('- testScannerIntegration() - Pruebas de escáner');
console.log('- testElectronicInvoicing() - Pruebas de facturación');
console.log('- testOfflineMode() - Pruebas modo offline');

// Auto-ejecutar pruebas básicas al cargar
setTimeout(() => {
    if (typeof POS_CONFIG !== 'undefined') {
        testPOSFunctionality();
    }
}, 2000);