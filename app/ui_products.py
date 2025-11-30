from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QLineEdit, QPushButton, QHeaderView, QMessageBox, QFormLayout, QComboBox
)
from PyQt6.QtCore import Qt
from app.models import ProductModel
from app.ui_error_handler import show_error, show_info

class ProductDialog(QDialog):
    def __init__(self, parent=None, product=None):
        super().__init__(parent)
        self.setWindowTitle("Add/Edit Product")
        self.product = product
        self.init_ui()

    def init_ui(self):
        layout = QFormLayout()
        self.name = QLineEdit(self.product['name'] if self.product else "")
        self.code = QLineEdit(self.product['code'] if self.product else "")
        self.unit = QComboBox()
        self.unit.addItems(["kg", "g", "litre", "ml", "pc"])
        if self.product: self.unit.setCurrentText(self.product['base_unit'])
        
        self.price = QLineEdit(str(self.product['price_per_unit']) if self.product else "")
        self.category = QLineEdit(self.product['category'] if self.product else "General")

        layout.addRow("Name:", self.name)
        layout.addRow("Code:", self.code)
        layout.addRow("Base Unit:", self.unit)
        layout.addRow("Price:", self.price)
        layout.addRow("Category:", self.category)

        btn_save = QPushButton("Save")
        btn_save.clicked.connect(self.save_product)
        layout.addRow(btn_save)
        self.setLayout(layout)

    def save_product(self):
        try:
            price = float(self.price.text())
            if self.product:
                ProductModel.update_product(self.product['id'], self.name.text(), self.code.text(), 
                                          self.unit.currentText(), price, self.category.text())
            else:
                ProductModel.add_product(self.name.text(), self.code.text(), 
                                       self.unit.currentText(), price, self.category.text())
            self.accept()
        except ValueError:
            show_error(self, "Input Error", "Price must be a number.")

class ManageProductsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Manage Products")
        self.resize(800, 600)
        self.init_ui()
        self.load_products()

    def init_ui(self):
        layout = QVBoxLayout()

        # Top Bar: Search and Add
        top_layout = QHBoxLayout()
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("🔍 Search by Name or Code...")
        self.search_bar.textChanged.connect(self.search_products)
        
        btn_add = QPushButton("+ Add New Product")
        btn_add.clicked.connect(self.add_product)
        
        top_layout.addWidget(self.search_bar)
        top_layout.addWidget(btn_add)
        layout.addLayout(top_layout)

        # Product Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "Name", "Code", "Unit", "Price", "Category"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.hideColumn(0) # Hide ID column
        layout.addWidget(self.table)

        # Action Buttons
        action_layout = QHBoxLayout()
        btn_edit = QPushButton("Edit Selected")
        btn_edit.clicked.connect(self.edit_product)
        
        btn_delete = QPushButton("Delete Selected")
        btn_delete.setObjectName("dangerBtn")
        btn_delete.clicked.connect(self.delete_product)
        
        action_layout.addStretch()
        action_layout.addWidget(btn_edit)
        action_layout.addWidget(btn_delete)
        layout.addLayout(action_layout)

        self.setLayout(layout)

    def load_products(self):
        self.products = ProductModel.get_all_products()
        self.update_table(self.products)

    def search_products(self):
        query = self.search_bar.text().lower()
        filtered = [p for p in self.products if query in p['name'].lower() or query in p['code'].lower()]
        self.update_table(filtered)

    def update_table(self, products):
        self.table.setRowCount(len(products))
        for row, p in enumerate(products):
            self.table.setItem(row, 0, QTableWidgetItem(str(p['id'])))
            self.table.setItem(row, 1, QTableWidgetItem(p['name']))
            self.table.setItem(row, 2, QTableWidgetItem(p['code']))
            self.table.setItem(row, 3, QTableWidgetItem(p['base_unit']))
            self.table.setItem(row, 4, QTableWidgetItem(f"{p['price_per_unit']:.2f}"))
            self.table.setItem(row, 5, QTableWidgetItem(p['category']))

    def add_product(self):
        dlg = ProductDialog(self)
        if dlg.exec():
            self.load_products()

    def edit_product(self):
        row = self.table.currentRow()
        if row < 0:
            show_info(self, "Selection", "Please select a product to edit.")
            return
        
        product_id = int(self.table.item(row, 0).text())
        product = next((p for p in self.products if p['id'] == product_id), None)
        
        if product:
            dlg = ProductDialog(self, product)
            if dlg.exec():
                self.load_products()

    def delete_product(self):
        row = self.table.currentRow()
        if row < 0:
            show_info(self, "Selection", "Please select a product to delete.")
            return
        
        product_name = self.table.item(row, 1).text()
        confirm = QMessageBox.question(self, "Confirm Delete", 
                                     f"Are you sure you want to delete '{product_name}'?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if confirm == QMessageBox.StandardButton.Yes:
            product_id = int(self.table.item(row, 0).text())
            ProductModel.delete_product(product_id)
            self.load_products()
