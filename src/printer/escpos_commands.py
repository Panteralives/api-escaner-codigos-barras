"""
Comandos ESC/POS para impresoras térmicas
Incluye comandos para formateo de texto, apertura de cajón, corte de papel, etc.
"""

class ESCPOSCommands:
    """Constantes y comandos ESC/POS para impresoras térmicas"""
    
    # Comandos básicos
    ESC = b'\x1b'
    GS = b'\x1d'
    
    # Inicialización
    INIT = ESC + b'@'
    
    # Formateo de texto
    BOLD_ON = ESC + b'E\x01'
    BOLD_OFF = ESC + b'E\x00'
    UNDERLINE_ON = ESC + b'-\x01'
    UNDERLINE_OFF = ESC + b'-\x00'
    DOUBLE_HEIGHT = ESC + b'!\x10'
    DOUBLE_WIDTH = ESC + b'!\x20'
    DOUBLE_SIZE = ESC + b'!\x30'
    NORMAL_SIZE = ESC + b'!\x00'
    
    # Alineación
    ALIGN_LEFT = ESC + b'a\x00'
    ALIGN_CENTER = ESC + b'a\x01'
    ALIGN_RIGHT = ESC + b'a\x02'
    
    # Espaciado
    LINE_FEED = b'\n'
    FORM_FEED = b'\x0c'
    CARRIAGE_RETURN = b'\r'
    
    # Corte de papel
    CUT_FULL = GS + b'V\x00'
    CUT_PARTIAL = GS + b'V\x01'
    
    # Apertura de cajón
    OPEN_DRAWER_1 = ESC + b'p\x00\x19\xfa'  # Cajón 1
    OPEN_DRAWER_2 = ESC + b'p\x01\x19\xfa'  # Cajón 2
    
    # Códigos de barras
    BARCODE_HEIGHT = GS + b'h\x64'  # Altura 100 puntos
    BARCODE_WIDTH = GS + b'w\x03'   # Ancho 3
    BARCODE_POSITION = GS + b'H\x02'  # Mostrar texto debajo
    BARCODE_FONT = GS + b'f\x00'    # Fuente A
    
    # Tipos de códigos de barras
    BARCODE_CODE128 = GS + b'k\x49'
    BARCODE_EAN13 = GS + b'k\x43'
    
    @classmethod
    def barcode_code128(cls, data):
        """Generar comando para código de barras CODE128"""
        data_bytes = data.encode('utf-8')
        length = len(data_bytes)
        return (cls.BARCODE_HEIGHT + cls.BARCODE_WIDTH + 
                cls.BARCODE_POSITION + cls.BARCODE_FONT +
                cls.BARCODE_CODE128 + bytes([length]) + data_bytes)
    
    @classmethod
    def barcode_ean13(cls, data):
        """Generar comando para código de barras EAN13"""
        data_bytes = data.encode('utf-8')
        return (cls.BARCODE_HEIGHT + cls.BARCODE_WIDTH + 
                cls.BARCODE_POSITION + cls.BARCODE_FONT +
                cls.BARCODE_EAN13 + data_bytes + b'\x00')
    
    @classmethod
    def text_bold(cls, text):
        """Texto en negrita"""
        return cls.BOLD_ON + text.encode('utf-8') + cls.BOLD_OFF
    
    @classmethod
    def text_double_size(cls, text):
        """Texto en doble tamaño"""
        return cls.DOUBLE_SIZE + text.encode('utf-8') + cls.NORMAL_SIZE
    
    @classmethod
    def text_centered(cls, text, width=48):
        """Texto centrado en el ancho especificado"""
        text = text[:width]  # Truncar si es muy largo
        padding = (width - len(text)) // 2
        centered_text = ' ' * padding + text
        return cls.ALIGN_CENTER + centered_text.encode('utf-8') + cls.ALIGN_LEFT
    
    @classmethod
    def line_separator(cls, char='-', width=48):
        """Línea separadora"""
        return (char * width + '\n').encode('utf-8')
    
    @classmethod
    def format_price(cls, price, width=48):
        """Formatear precio alineado a la derecha"""
        price_str = f"${price:.2f}"
        spaces = width - len(price_str)
        return (' ' * spaces + price_str).encode('utf-8')
    
    @classmethod
    def format_item_line(cls, name, price, quantity=1, width=48):
        """Formatear línea de producto"""
        # Calcular espacios disponibles
        price_str = f"${price:.2f}"
        qty_str = f" x{quantity}" if quantity > 1 else ""
        
        # Truncar nombre si es necesario
        available_width = width - len(price_str) - len(qty_str) - 1
        if len(name) > available_width:
            name = name[:available_width-3] + "..."
        
        # Calcular espacios para alineación
        spaces_needed = width - len(name) - len(qty_str) - len(price_str)
        spaces = ' ' * max(1, spaces_needed)
        
        line = name + qty_str + spaces + price_str + '\n'
        return line.encode('utf-8')
    
    @classmethod
    def qr_code(cls, data, size=3):
        """Generar código QR (si la impresora lo soporta)"""
        # Comando para QR Code (GS ( k)
        data_bytes = data.encode('utf-8')
        length = len(data_bytes) + 3
        
        commands = []
        # Establecer modelo QR
        commands.append(GS + b'(k\x04\x00\x01\x41\x32\x00')
        # Establecer tamaño
        commands.append(GS + b'(k\x03\x00\x01\x43' + bytes([size]))
        # Establecer nivel de corrección de errores
        commands.append(GS + b'(k\x03\x00\x01\x45\x30')
        # Almacenar datos
        commands.append(GS + b'(k' + length.to_bytes(2, 'little') + b'\x01\x50\x30' + data_bytes)
        # Imprimir QR
        commands.append(GS + b'(k\x03\x00\x01\x51\x30')
        
        return b''.join(commands)