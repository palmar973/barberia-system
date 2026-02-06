from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QDateEdit, 
    QTableWidget, QTableWidgetItem, QHeaderView, QFrame, 
    QAbstractItemView, QPushButton
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QFont, QColor
from controllers.reportes_controller import ReportesController

class CierreCajaView(QDialog):
    """
    Ventana modal para visualizar el Cierre de Caja Diario.
    Muestra ingresos desglosados por método de pago y el total general.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Cierre de Caja Diario")
        self.setModal(True)
        self.resize(500, 600)
        
        self.controller = ReportesController()
        
        self.init_ui()
        self.cargar_reporte()

    def init_ui(self):
        self.setStyleSheet(
            """
            QDialog { background-color: #1F2A35; color: #ECF0F1; }
            QLabel { color: #ECF0F1; }
            QComboBox { background-color: #34495E; color: white; border: 1px solid #5D6D7E; padding: 5px; }
            QComboBox QAbstractItemView { background-color: #2C3E50; color: white; selection-background-color: #27AE60; }
            QDateEdit { background-color: #ECF0F1; color: #2C3E50; border: 1px solid #95A5A6; border-radius: 4px; padding: 5px; }
            QTableWidget { background-color: #2C3E50; alternate-background-color: #273444; color: #ECF0F1; gridline-color: #5D6D7E; }
            QHeaderView::section { background-color: #34495E; color: #ECF0F1; border: 1px solid #5D6D7E; }
            QPushButton#close { background-color: #5D6D7E; color: white; border-radius: 6px; padding: 8px 12px; }
            QPushButton#close:hover { background-color: #707B7C; }
            """
        )
        self.layout_principal = QVBoxLayout()
        self.setLayout(self.layout_principal)
        self.layout_principal.setContentsMargins(20, 20, 20, 20)

        lbl_titulo = QLabel("REPORTE DE INGRESOS")
        lbl_titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_titulo.setFont(QFont("Arial", 16, QFont.Bold))
        lbl_titulo.setStyleSheet("margin-bottom: 10px;")
        self.layout_principal.addWidget(lbl_titulo)

        frame_filtro = QFrame()
        frame_filtro.setObjectName("filtro")
        frame_filtro.setStyleSheet("#filtro { background-color: #273444; border: 1px solid #5D6D7E; border-radius: 8px; padding: 10px; }")
        layout_filtro = QHBoxLayout()
        frame_filtro.setLayout(layout_filtro)

        lbl_fecha = QLabel("Fecha de Consulta:")
        lbl_fecha.setFont(QFont("Arial", 11))
        
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setDisplayFormat("dd/MM/yyyy")
        self.date_edit.setFixedWidth(120)
        self.date_edit.setStyleSheet(self.date_edit.styleSheet() + " font-size: 14px;")
        
        # Al cambiar fecha se refresca el reporte
        self.date_edit.dateChanged.connect(self.cargar_reporte)

        layout_filtro.addWidget(lbl_fecha)
        layout_filtro.addWidget(self.date_edit)
        layout_filtro.addStretch()
        
        self.layout_principal.addWidget(frame_filtro)
        self.layout_principal.addSpacing(15)

        self.tabla = QTableWidget()
        self.tabla.setColumnCount(2)
        self.tabla.setHorizontalHeaderLabels(["Método de Pago", "Total Recaudado"])
        self.tabla.setSelectionMode(QAbstractItemView.NoSelection)
        self.tabla.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tabla.verticalHeader().setVisible(False)
        self.tabla.setAlternatingRowColors(True)
        
        header = self.tabla.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        header.setStyleSheet("font-weight: bold;")

        self.layout_principal.addWidget(self.tabla)

        self.layout_principal.addSpacing(10)
        
        frame_total = QFrame()
        frame_total.setObjectName("totales")
        frame_total.setStyleSheet("#totales { background-color: #1E8449; color: white; border-radius: 8px; padding: 15px; }")
        layout_total = QHBoxLayout()
        frame_total.setLayout(layout_total)

        lbl_total_texto = QLabel("INGRESO TOTAL DEL DÍA:")
        lbl_total_texto.setFont(QFont("Arial", 12, QFont.Bold))
        
        self.lbl_gran_total = QLabel("$0.00")
        self.lbl_gran_total.setFont(QFont("Arial", 18, QFont.Bold))
        self.lbl_gran_total.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        layout_total.addWidget(lbl_total_texto)
        layout_total.addStretch()
        layout_total.addWidget(self.lbl_gran_total)
        
        self.layout_principal.addWidget(frame_total)

        self.layout_principal.addSpacing(10)
        btn_cerrar = QPushButton("Cerrar")
        btn_cerrar.setObjectName("close")
        btn_cerrar.clicked.connect(self.accept)
        self.layout_principal.addWidget(btn_cerrar, alignment=Qt.AlignmentFlag.AlignRight)

    def cargar_reporte(self):
        """Consulta al controlador y llena la tabla."""
        fecha_str = self.date_edit.date().toString("yyyy-MM-dd")
        datos = self.controller.obtener_cierre_diario(fecha_str)
        
        self.tabla.setRowCount(0)
        gran_total = 0.0

        if not datos:
            self.lbl_gran_total.setText("$0.00")
            return

        for row_idx, fila in enumerate(datos):
            metodo = fila[0]
            total = fila[1]
            gran_total += total
            
            self.tabla.insertRow(row_idx)
            item_metodo = QTableWidgetItem(metodo)
            item_metodo.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.tabla.setItem(row_idx, 0, item_metodo)
            item_total = QTableWidgetItem(f"${total:.2f}")
            item_total.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.tabla.setItem(row_idx, 1, item_total)

        self.lbl_gran_total.setText(f"${gran_total:.2f}")