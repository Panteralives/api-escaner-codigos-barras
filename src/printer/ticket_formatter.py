"""
Formateador de tickets con diseño profesional
Genera el contenido y formato para tickets de venta
"""

from datetime import datetime
from typing import List, Dict, Any, Optional
from .escpos_commands import ESCPOSCommands

class TicketFormatter:
    """Formateador de tickets para impresoras térmicas"""
    
    def __init__(self, business_name: str = "PUNTO DE VENTA", 
                 business_address: str = "", business_phone: str = "",
                 ticket_width: int = 48):
        self.business_name = business_name
        self.business_address = business_address
        self.business_phone = business_phone
        self.ticket_width = ticket_width
        self.cmd = ESCPOSCommands
    
    def format_sale_ticket(self, sale_data: Dict[str, Any]) -> bytes:
        """
        Formatear ticket de venta completo
        
        Args:
            sale_data: Diccionario con datos de la venta
                - items: Lista de productos
                - total: Total de la venta
                - payment_method: Método de pago
                - sale_id: ID de la venta
                - cashier: Nombre del cajero (opcional)
                - customer: Datos del cliente (opcional)
        """
        ticket = b''
        
        # Inicializar impresora
        ticket += self.cmd.INIT
        
        # Header del negocio
        ticket += self._format_header()
        
        # Información de la venta
        ticket += self._format_sale_info(sale_data)
        
        # Lista de productos
        ticket += self._format_items(sale_data.get('items', []))
        
        # Totales
        ticket += self._format_totals(sale_data)
        
        # Información de pago
        ticket += self._format_payment_info(sale_data)
        
        # Footer
        ticket += self._format_footer(sale_data)
        
        # Código de barras del ticket (opcional)
        if sale_data.get('sale_id'):
            ticket += self._format_barcode(sale_data['sale_id'])
        
        # Corte de papel
        ticket += self.cmd.LINE_FEED * 3
        ticket += self.cmd.CUT_PARTIAL
        
        return ticket
    
    def _format_header(self) -> bytes:
        """Formatear header del negocio"""
        header = b''
        
        # Nombre del negocio en grande
        header += self.cmd.text_double_size(self.business_name)
        header += self.cmd.LINE_FEED * 2
        
        # Dirección centrada
        if self.business_address:
            header += self.cmd.text_centered(self.business_address, self.ticket_width)
            header += self.cmd.LINE_FEED
        
        # Teléfono centrado
        if self.business_phone:
            header += self.cmd.text_centered(f"Tel: {self.business_phone}", self.ticket_width)
            header += self.cmd.LINE_FEED
        
        # Línea separadora
        header += self.cmd.line_separator('=', self.ticket_width)
        
        return header
    
    def _format_sale_info(self, sale_data: Dict[str, Any]) -> bytes:
        """Formatear información de la venta"""
        info = b''
        
        # Fecha y hora
        now = datetime.now()
        date_str = now.strftime("%d/%m/%Y")
        time_str = now.strftime("%H:%M:%S")
        
        info += f"FECHA: {date_str}".ljust(24).encode() + f"HORA: {time_str}".encode()
        info += self.cmd.LINE_FEED
        
        # Número de ticket
        if sale_data.get('sale_id'):
            ticket_num = f"TICKET #: {sale_data['sale_id']}"
            info += ticket_num.encode()
            info += self.cmd.LINE_FEED
        
        # Cajero
        if sale_data.get('cashier'):
            cashier = f"CAJERO: {sale_data['cashier']}"
            info += cashier.encode()
            info += self.cmd.LINE_FEED
        
        # Cliente
        if sale_data.get('customer'):
            customer = f"CLIENTE: {sale_data['customer']}"
            info += customer.encode()
            info += self.cmd.LINE_FEED
        
        info += self.cmd.line_separator('-', self.ticket_width)
        
        return info
    
    def _format_items(self, items: List[Dict[str, Any]]) -> bytes:
        """Formatear lista de productos"""
        items_section = b''
        
        # Header de productos
        header = "DESCRIPCION".ljust(26) + "CANT" + "  PRECIO"
        items_section += self.cmd.text_bold(header)
        items_section += self.cmd.LINE_FEED
        items_section += self.cmd.line_separator('-', self.ticket_width)
        
        # Productos
        for item in items:
            name = item.get('name', 'Producto')
            quantity = item.get('quantity', 1)
            price = item.get('price', 0.0)
            subtotal = item.get('subtotal', price * quantity)
            
            # Línea del producto
            items_section += self.cmd.format_item_line(name, subtotal, quantity, self.ticket_width)
            
            # Si hay código de barras, mostrarlo en línea separada
            if item.get('barcode'):
                barcode_line = f"  COD: {item['barcode']}"
                items_section += barcode_line.encode()
                items_section += self.cmd.LINE_FEED
        
        items_section += self.cmd.line_separator('-', self.ticket_width)
        
        return items_section
    
    def _format_totals(self, sale_data: Dict[str, Any]) -> bytes:
        """Formatear sección de totales"""
        totals = b''
        
        # Subtotal (si hay impuestos)
        if sale_data.get('subtotal') and sale_data.get('tax'):
            subtotal_line = f"SUBTOTAL: ${sale_data['subtotal']:.2f}"
            totals += subtotal_line.rjust(self.ticket_width).encode()
            totals += self.cmd.LINE_FEED
            
            # Impuestos
            tax_line = f"IMPUESTOS: ${sale_data['tax']:.2f}"
            totals += tax_line.rjust(self.ticket_width).encode()
            totals += self.cmd.LINE_FEED
        
        # Total
        total = sale_data.get('total', 0.0)
        total_line = f"TOTAL: ${total:.2f}"
        totals += self.cmd.text_bold(total_line.rjust(self.ticket_width))
        totals += self.cmd.LINE_FEED
        
        # Cantidad de artículos
        total_items = sum(item.get('quantity', 1) for item in sale_data.get('items', []))
        items_line = f"ARTICULOS: {total_items}"
        totals += items_line.rjust(self.ticket_width).encode()
        totals += self.cmd.LINE_FEED
        
        totals += self.cmd.line_separator('=', self.ticket_width)
        
        return totals
    
    def _format_payment_info(self, sale_data: Dict[str, Any]) -> bytes:
        """Formatear información de pago"""
        payment = b''
        
        payment_method = sale_data.get('payment_method', 'Efectivo')
        total = sale_data.get('total', 0.0)
        
        # Método de pago
        method_line = f"PAGO: {payment_method}"
        payment += method_line.encode()
        payment += self.cmd.LINE_FEED
        
        # Monto pagado
        paid_amount = sale_data.get('paid_amount', total)
        paid_line = f"PAGADO: ${paid_amount:.2f}"
        payment += paid_line.encode()
        payment += self.cmd.LINE_FEED
        
        # Cambio (solo para efectivo)
        if payment_method.lower() == 'efectivo' and paid_amount > total:
            change = paid_amount - total
            change_line = f"CAMBIO: ${change:.2f}"
            payment += self.cmd.text_bold(change_line)
            payment += self.cmd.LINE_FEED
        
        payment += self.cmd.line_separator('-', self.ticket_width)
        
        return payment
    
    def _format_footer(self, sale_data: Dict[str, Any]) -> bytes:
        """Formatear footer del ticket"""
        footer = b''
        
        # Mensaje de agradecimiento
        thanks = "GRACIAS POR SU COMPRA"
        footer += self.cmd.text_centered(thanks, self.ticket_width)
        footer += self.cmd.LINE_FEED * 2
        
        # Mensaje de devoluciones o garantía
        policy = "CONSERVE SU TICKET"
        footer += self.cmd.text_centered(policy, self.ticket_width)
        footer += self.cmd.LINE_FEED
        
        # Información adicional
        if sale_data.get('return_policy'):
            footer += self.cmd.text_centered(sale_data['return_policy'], self.ticket_width)
            footer += self.cmd.LINE_FEED
        
        # Website o redes sociales
        if sale_data.get('website'):
            footer += self.cmd.text_centered(sale_data['website'], self.ticket_width)
            footer += self.cmd.LINE_FEED
        
        return footer
    
    def _format_barcode(self, sale_id: str) -> bytes:
        """Formatear código de barras del ticket"""
        barcode = b''
        
        barcode += self.cmd.LINE_FEED
        barcode += self.cmd.ALIGN_CENTER
        
        # Generar código de barras con el ID de venta
        barcode_data = f"TICKET{sale_id:06d}"  # Formato: TICKET000001
        barcode += self.cmd.barcode_code128(barcode_data)
        
        barcode += self.cmd.LINE_FEED
        barcode += self.cmd.ALIGN_LEFT
        
        return barcode
    
    def format_test_ticket(self) -> bytes:
        """Generar ticket de prueba"""
        test_data = {
            'sale_id': 1,
            'cashier': 'Sistema',
            'items': [
                {
                    'name': 'Producto de Prueba',
                    'quantity': 1,
                    'price': 10.00,
                    'subtotal': 10.00,
                    'barcode': '1234567890123'
                }
            ],
            'total': 10.00,
            'payment_method': 'Efectivo',
            'paid_amount': 10.00
        }
        
        return self.format_sale_ticket(test_data)
    
    def format_no_sale_ticket(self) -> bytes:
        """Generar ticket de apertura de cajón sin venta (no sale)"""
        ticket = b''
        
        # Inicializar
        ticket += self.cmd.INIT
        
        # Header
        ticket += self._format_header()
        
        # Información
        now = datetime.now()
        ticket += f"FECHA: {now.strftime('%d/%m/%Y %H:%M:%S')}".encode()
        ticket += self.cmd.LINE_FEED * 2
        
        # Mensaje principal
        message = "APERTURA DE CAJON"
        ticket += self.cmd.text_double_size(message)
        ticket += self.cmd.LINE_FEED * 2
        
        ticket += self.cmd.text_centered("SIN VENTA", self.ticket_width)
        ticket += self.cmd.LINE_FEED * 2
        
        # Footer mínimo
        ticket += self.cmd.line_separator('-', self.ticket_width)
        ticket += self.cmd.text_centered("SISTEMA POS", self.ticket_width)
        ticket += self.cmd.LINE_FEED * 3
        
        # Corte
        ticket += self.cmd.CUT_PARTIAL
        
        return ticket