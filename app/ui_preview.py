from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, QLabel
)
from PyQt6.QtCore import Qt
from app.models import SettingsModel
from app.ui_error_handler import show_error, show_info

class BillPreviewDialog(QDialog):
    def __init__(self, parent, bill_data, items, printer_manager):
        super().__init__(parent)
        self.setWindowTitle("Bill Preview")
        self.resize(400, 600)
        self.bill_data = bill_data
        self.items = items
        self.printer_manager = printer_manager
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Preview Area
        lbl_preview = QLabel("Receipt Preview (80mm)")
        lbl_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_preview)

        self.preview_area = QTextEdit()
        self.preview_area.setReadOnly(True)
        # Set a fixed width to simulate 80mm paper (approx 300-350px visible width)
        self.preview_area.setFixedWidth(380) 
        self.preview_area.setStyleSheet("background-color: white; color: black; font-family: 'Courier New'; font-size: 12px;")
        
        self.generate_html_preview()
        
        # Center the preview area
        h_layout = QHBoxLayout()
        h_layout.addStretch()
        h_layout.addWidget(self.preview_area)
        h_layout.addStretch()
        layout.addLayout(h_layout)

        # Buttons
        btn_layout = QHBoxLayout()
        
        btn_close = QPushButton("Close")
        btn_close.clicked.connect(self.reject)
        
        btn_print = QPushButton("🖨 Print")
        btn_print.setObjectName("primaryBtn")
        btn_print.clicked.connect(self.print_bill)
        
        btn_layout.addWidget(btn_close)
        btn_layout.addWidget(btn_print)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def generate_html_preview(self):
        store_name = SettingsModel.get_setting('store_name', 'Thangam Stores')
        store_address = SettingsModel.get_setting('store_address', '123 Main St, City')
        footer_text = SettingsModel.get_setting('receipt_footer', 'Thank you for shopping!')
        
        html = f"""
        <div style="text-align: center; font-weight: bold; font-size: 16px;">{store_name}</div>
        <div style="text-align: center; font-size: 12px;">{store_address}</div>
        <hr>
        <table width="100%" style="font-size: 12px;">
            <tr>
                <td align="left">Bill No: {self.bill_data['bill_number']}</td>
                <td align="right">{self.bill_data['date_time']}</td>
            </tr>
            <tr>
                <td align="left" colspan="2">Customer: {self.bill_data.get('customer_name', 'Walk-in')}</td>
            </tr>
            {f'<tr><td align="left" colspan="2">Phone: {self.bill_data.get("customer_phone")}</td></tr>' if self.bill_data.get('customer_phone') else ''}
        </table>
        <hr>
        <table width="100%" style="font-size: 12px;">
            <tr>
                <th align="left">Item</th>
                <th align="center">Qty</th>
                <th align="right">Price</th>
            </tr>
        """
        
        for item in self.items:
            html += f"""
            <tr>
                <td align="left">{item['product_name'][:15]}</td>
                <td align="center">{item['quantity']}{item['unit']}</td>
                <td align="right">{item['total']:.2f}</td>
            </tr>
            """
            
        html += f"""
        </table>
        <hr>
        <table width="100%" style="font-size: 12px;">
            <tr>
                <td align="left">Subtotal:</td>
                <td align="right">{self.bill_data['subtotal']:.2f}</td>
            </tr>
        """
        
        if self.bill_data.get('tax_amount'):
            html += f"""
            <tr>
                <td align="left">Tax:</td>
                <td align="right">{self.bill_data['tax_amount']:.2f}</td>
            </tr>
            """
            
        if self.bill_data.get('discount_amount'):
            html += f"""
            <tr>
                <td align="left">Discount:</td>
                <td align="right">-{self.bill_data['discount_amount']:.2f}</td>
            </tr>
            """
            
        html += f"""
            <tr style="font-weight: bold; font-size: 14px;">
                <td align="left">Total:</td>
                <td align="right">{self.bill_data['grand_total']:.2f}</td>
            </tr>
        </table>
        <hr>
        <div style="text-align: center; font-size: 12px;">{footer_text}</div>
        """
        
        self.preview_area.setHtml(html)

    def print_bill(self):
        try:
            self.printer_manager.print_receipt(self.bill_data, self.items)
            show_info(self, "Success", "Print command sent!")
            self.accept()
        except Exception as e:
            show_error(self, "Printing Error", f"Print failed: {e}")
