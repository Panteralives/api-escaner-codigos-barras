from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional

from ...printer import PrinterManager, TicketFormatter

router = APIRouter(prefix="/printer", tags=["printer"])


class SaleItem(BaseModel):
    name: str
    price: float
    quantity: int = 1
    barcode: Optional[str] = None

    @property
    def subtotal(self) -> float:
        return self.price * self.quantity


class PrintSaleRequest(BaseModel):
    sale_id: Optional[int] = None
    cashier: Optional[str] = None
    payment_method: str = Field(default="Efectivo")
    paid_amount: Optional[float] = None
    items: List[SaleItem]
    total: float


class PrinterConfig(BaseModel):
    mode: str = Field(default="file", description="'network' o 'file'")
    ip: Optional[str] = None
    port: int = 9100
    file_path: str = "ticket_output.bin"


@router.post("/print-test")
async def print_test(
    mode: str = Query(default="file", description="'network' o 'file'"),
    ip: Optional[str] = Query(default=None, description="IP de la impresora (solo para modo network)"),
    port: int = Query(default=9100, description="Puerto de la impresora"),
    file_path: str = Query(default="ticket_output.bin", description="Archivo de salida (solo para modo file)")
):
    try:
        printer = PrinterManager(mode=mode, ip=ip, port=port, file_path=file_path)
        result = printer.print_test()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": str(e)})


@router.post("/open-drawer")
async def open_drawer(
    drawer: int = Query(default=1, description="Número de cajón (1 o 2)"),
    mode: str = Query(default="file", description="'network' o 'file'"),
    ip: Optional[str] = Query(default=None, description="IP de la impresora (solo para modo network)"),
    port: int = Query(default=9100, description="Puerto de la impresora"),
    file_path: str = Query(default="ticket_output.bin", description="Archivo de salida (solo para modo file)")
):
    try:
        printer = PrinterManager(mode=mode, ip=ip, port=port, file_path=file_path)
        result = printer.open_cash_drawer(drawer=drawer)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": str(e)})


@router.post("/print-sale")
async def print_sale(
    req: PrintSaleRequest,
    mode: str = Query(default="file", description="'network' o 'file'"),
    ip: Optional[str] = Query(default=None, description="IP de la impresora (solo para modo network)"),
    port: int = Query(default=9100, description="Puerto de la impresora"),
    file_path: str = Query(default="ticket_output.bin", description="Archivo de salida (solo para modo file)")
):
    try:
        # Formatear ticket de venta
        formatter = TicketFormatter(business_name="INVENTARIO BARRAS")
        sale_data = {
            "sale_id": req.sale_id,
            "cashier": req.cashier,
            "items": [
                {"name": it.name, "price": it.price, "quantity": it.quantity, "subtotal": it.subtotal, "barcode": it.barcode}
                for it in req.items
            ],
            "total": req.total,
            "payment_method": req.payment_method,
            "paid_amount": req.paid_amount or req.total,
        }
        data = formatter.format_sale_ticket(sale_data)

        # Enviar a impresora
        printer = PrinterManager(mode=mode, ip=ip, port=port, file_path=file_path)
        result = printer.print_bytes(data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": str(e)})
