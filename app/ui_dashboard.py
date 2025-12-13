from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QPushButton, QLabel, QFrame
)
from PyQt6.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from app.models import BillModel

class DashboardWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.load_data()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(20)

        # Top Bar: Filters
        filter_layout = QHBoxLayout()
        self.days_combo = QComboBox()
        self.days_combo.addItems(["Last 7 Days", "Last 30 Days", "Last 90 Days"])
        self.days_combo.currentIndexChanged.connect(self.load_data)
        
        btn_refresh = QPushButton("Refresh Data")
        btn_refresh.clicked.connect(self.load_data)

        filter_layout.addWidget(QLabel("Date Range:"))
        filter_layout.addWidget(self.days_combo)
        filter_layout.addWidget(btn_refresh)
        filter_layout.addStretch()
        layout.addLayout(filter_layout)

        # Charts Area
        charts_layout = QHBoxLayout()

        # Left: Sales Trends
        self.sales_canvas = FigureCanvas(Figure(figsize=(5, 4), dpi=100))
        charts_layout.addWidget(self.sales_canvas, stretch=2)

        # Right Column
        right_layout = QVBoxLayout()
        self.top_prod_canvas = FigureCanvas(Figure(figsize=(5, 3), dpi=100))
        self.payment_canvas = FigureCanvas(Figure(figsize=(5, 3), dpi=100))
        
        right_layout.addWidget(self.top_prod_canvas)
        right_layout.addWidget(self.payment_canvas)
        
        charts_layout.addLayout(right_layout, stretch=1)
        layout.addLayout(charts_layout)

        self.setLayout(layout)

    def load_data(self):
        range_map = {0: 7, 1: 30, 2: 90}
        days = range_map.get(self.days_combo.currentIndex(), 7)
        
        sales_data = BillModel.get_sales_trends(days)
        top_products = BillModel.get_top_selling_products()
        payment_stats = BillModel.get_payment_method_stats()

        self.plot_sales(sales_data)
        self.plot_top_products(top_products)
        self.plot_payment_dist(payment_stats)

    def plot_sales(self, data):
        self.sales_canvas.figure.clear()
        ax = self.sales_canvas.figure.add_subplot(111)
        
        dates = list(data.keys())
        totals = list(data.values())
        
        # Simple sorting by date
        sorted_pairs = sorted(zip(dates, totals))
        if sorted_pairs:
            dates, totals = zip(*sorted_pairs)
        
        ax.bar(dates, totals, color='#4CAF50')
        ax.set_title("Sales Trends")
        ax.set_ylabel("Sales (₹)")
        
        # Rotate dates if many
        if len(dates) > 5:
            ax.tick_params(axis='x', rotation=45)
            
        self.sales_canvas.figure.tight_layout()
        self.sales_canvas.draw()

    def plot_top_products(self, data):
        self.top_prod_canvas.figure.clear()
        ax = self.top_prod_canvas.figure.add_subplot(111)
        
        names = [item['name'][:15] + '..' if len(item['name']) > 15 else item['name'] for item in data]
        qtys = [item['qty'] for item in data]
        
        # Invert to have top most at top
        ax.barh(names[::-1], qtys[::-1], color='#2196F3')
        ax.set_title("Top Selling Products")
        ax.set_xlabel("Quantity Sold")
        
        self.top_prod_canvas.figure.tight_layout()
        self.top_prod_canvas.draw()

    def plot_payment_dist(self, data):
        self.payment_canvas.figure.clear()
        ax = self.payment_canvas.figure.add_subplot(111)
        
        labels = [d['method'] for d in data]
        sizes = [d['total'] for d in data]
        
        if sizes:
            ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=['#FFC107', '#9C27B0', '#F44336'])
            ax.set_title("Payment Methods (By Value)")
        else:
            ax.text(0.5, 0.5, 'No Data', ha='center', va='center')
            
        self.payment_canvas.figure.tight_layout()
        self.payment_canvas.draw()
