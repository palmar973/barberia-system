from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QDateEdit, 
    QTableWidget, QTableWidgetItem, QHeaderView, QFrame, 
    QAbstractItemView, QPushButton
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QFont, QColor
from controllers.reportes_controller import ReportesController

class ReporteComisionesView(QDialog):
    """
    Ventana modal para visualizar el Reporte de Comisiones (Nómina).
    Muestra el total vendido por cada barbero y su comisión (50%).
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Cálculo de Comisiones")
        self.setModal(True)
        self.resize(700, 600)
        
        self.controller = ReportesController()
        
        self.init_ui()

    def init_ui(self):
        self.setStyleSheet(
            """
            QDialog { background-color: #2b2b2b; color: #ffffff; }
            QLabel { color: #ffffff; }
            QComboBox { background-color: #34495E; color: white; border: 1px solid #5D6D7E; padding: 5px; }
            QComboBox QAbstractItemView { background-color: #2C3E50; color: white; selection-background-color: #27AE60; }
            QDateEdit { background-color: #34495E; color: #ffffff; border: 1px solid #5D6D7E; border-radius: 4px; padding: 5px; }
            QTableWidget { background-color: #2C3E50; alternate-background-color: #273444; color: #ffffff; gridline-color: #5D6D7E; }
            QHeaderView::section { background-color: #34495E; color: #ffffff; border: 1px solid #5D6D7E; font-weight: bold; }
            QPushButton#consultar { background-color: #27AE60; color: white; border-radius: 6px; padding: 8px 16px; font-weight: bold; }
            QPushButton#consultar:hover { background-color: #229954; }
            QPushButton#close { background-color: #5D6D7E; color: white; border-radius: 6px; padding: 8px 12px; }
            QPushButton#close:hover { background-color: #707B7C; }
            """
        )
        self.layout_principal = QVBoxLayout()
        self.setLayout(self.layout_principal)
        self.layout_principal.setContentsMargins(20, 20, 20, 20)

        lbl_titulo = QLabel("CÁLCULO DE COMISIONES")
        lbl_titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_titulo.setFont(QFont("Arial", 16, QFont.Bold))
        lbl_titulo.setStyleSheet("margin-bottom: 10px;")
        self.layout_principal.addWidget(lbl_titulo)

        frame_filtro = QFrame()
        frame_filtro.setObjectName("filtro")
        frame_filtro.setStyleSheet("#filtro { background-color: #273444; border: 1px solid #5D6D7E; border-radius: 8px; padding: 10px; }")
        layout_filtro = QHBoxLayout()
        frame_filtro.setLayout(layout_filtro)

        lbl_fecha_inicio = QLabel("Fecha Inicio:")
        lbl_fecha_inicio.setFont(QFont("Arial", 11))
        
        self.date_inicio = QDateEdit()
        self.date_inicio.setCalendarPopup(True)
        self.date_inicio.setDate(QDate.currentDate().addDays(-30))
        self.date_inicio.setDisplayFormat("dd/MM/yyyy")
        self.date_inicio.setFixedWidth(120)
        self.date_inicio.setStyleSheet(self.date_inicio.styleSheet() + " font-size: 14px;")

        lbl_fecha_fin = QLabel("Fecha Fin:")
        lbl_fecha_fin.setFont(QFont("Arial", 11))
        
        self.date_fin = QDateEdit()
        self.date_fin.setCalendarPopup(True)
        self.date_fin.setDate(QDate.currentDate())
        self.date_fin.setDisplayFormat("dd/MM/yyyy")
        self.date_fin.setFixedWidth(120)
        self.date_fin.setStyleSheet(self.date_fin.styleSheet() + " font-size: 14px;")

        btn_consultar = QPushButton("Consultar")
        btn_consultar.setObjectName("consultar")
        btn_consultar.clicked.connect(self.cargar_reporte)

        layout_filtro.addWidget(lbl_fecha_inicio)
        layout_filtro.addWidget(self.date_inicio)
        layout_filtro.addSpacing(20)
        layout_filtro.addWidget(lbl_fecha_fin)
        layout_filtro.addWidget(self.date_fin)
        layout_filtro.addSpacing(20)
        layout_filtro.addWidget(btn_consultar)
        layout_filtro.addStretch()
        
        self.layout_principal.addWidget(frame_filtro)
        self.layout_principal.addSpacing(15)

        self.tabla = QTableWidget()
        self.tabla.setColumnCount(4)
        self.tabla.setHorizontalHeaderLabels(["Barbero", "Total Vendido", "% Comisión", "Pago a Realizar"])
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

        lbl_total_texto = QLabel("TOTAL A PAGAR:")
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
        fecha_inicio_str = self.date_inicio.date().toString("yyyy-MM-dd")
        fecha_fin_str = self.date_fin.date().toString("yyyy-MM-dd")
        datos = self.controller.obtener_comisiones(fecha_inicio_str, fecha_fin_str)
        
        self.tabla.setRowCount(0)
        gran_total = 0.0

        if not datos:
            self.lbl_gran_total.setText("$0.00")
            return

        for row_idx, fila in enumerate(datos):
            barbero = fila[0]
            total_vendido = fila[1] if fila[1] else 0.0
            porcentaje = 50.0
            pago_a_realizar = total_vendido * 0.50
            gran_total += pago_a_realizar
            
            self.tabla.insertRow(row_idx)
            
            item_barbero = QTableWidgetItem(f"✂️ {barbero}")
            item_barbero.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            item_barbero.setFont(QFont("Arial", 10, QFont.Bold))
            self.tabla.setItem(row_idx, 0, item_barbero)
            
            item_total = QTableWidgetItem(f"${total_vendido:.2f}")
            item_total.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.tabla.setItem(row_idx, 1, item_total)
            
            item_porcentaje = QTableWidgetItem(f"{porcentaje:.0f}%")
            item_porcentaje.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.tabla.setItem(row_idx, 2, item_porcentaje)
            
            item_pago = QTableWidgetItem(f"${pago_a_realizar:.2f}")
            item_pago.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            item_pago.setForeground(QColor("#27AE60"))
            item_pago.setFont(QFont("Arial", 10, QFont.Bold))
            self.tabla.setItem(row_idx, 3, item_pago)

        self.lbl_gran_total.setText(f"${gran_total:.2f}")
