from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, 
    QTableWidgetItem, QHeaderView, QPushButton, QFrame, QAbstractItemView
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor
from controllers.clientes_controller import ClientesController

class HistorialClienteView(QDialog):
    """
    Ventana modal de solo lectura para visualizar el historial de servicios de un cliente.
    """
    def __init__(self, id_cliente, nombre_cliente, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Historial de Servicios del Cliente")
        self.setModal(True)
        self.resize(800, 500)
        
        self.id_cliente = id_cliente
        self.nombre_cliente = nombre_cliente
        self.controller = ClientesController()
        
        self.init_ui()
        self.cargar_historial()

    def init_ui(self):
        self.layout_principal = QVBoxLayout()
        self.setLayout(self.layout_principal)
        self.layout_principal.setContentsMargins(20, 20, 20, 20)

        frame_header = QFrame()
        frame_header.setStyleSheet("background-color: #f0f0f0; border-radius: 5px;")
        layout_header = QHBoxLayout()
        frame_header.setLayout(layout_header)

        lbl_titulo = QLabel("HISTORIAL DE:")
        lbl_titulo.setFont(QFont("Arial", 12))
        
        lbl_nombre = QLabel(self.nombre_cliente.upper())
        lbl_nombre.setFont(QFont("Arial", 16, QFont.Bold))
        lbl_nombre.setStyleSheet("color: #2C3E50;")

        layout_header.addWidget(lbl_titulo)
        layout_header.addWidget(lbl_nombre)
        layout_header.addStretch()
        
        self.layout_principal.addWidget(frame_header)
        self.layout_principal.addSpacing(10)

        self.tabla = QTableWidget()
        self.tabla.setColumnCount(6)
        self.tabla.setHorizontalHeaderLabels(["Fecha", "Hora", "Servicio", "Barbero", "Precio", "Estado"])
        self.tabla.setSelectionMode(QAbstractItemView.NoSelection)
        self.tabla.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tabla.verticalHeader().setVisible(False)
        self.tabla.setAlternatingRowColors(True)

        header = self.tabla.horizontalHeader()
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        
        self.layout_principal.addWidget(self.tabla)

        self.layout_principal.addSpacing(10)
        btn_cerrar = QPushButton("Cerrar")
        btn_cerrar.setMinimumHeight(40)
        btn_cerrar.setStyleSheet("padding: 10px; font-weight: bold;")
        btn_cerrar.clicked.connect(self.accept)
        
        self.layout_principal.addWidget(btn_cerrar, alignment=Qt.AlignmentFlag.AlignRight)

    def cargar_historial(self):
        """Obtiene los datos del controlador y llena la tabla."""
        citas = self.controller.obtener_historial_cliente(self.id_cliente)
        
        self.tabla.setRowCount(0)

        if not citas:
            self.tabla.setRowCount(1)
            item_aviso = QTableWidgetItem("Este cliente aún no ha tomado servicios.")
            item_aviso.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item_aviso.setFont(QFont("Arial", 10, QFont.StyleItalic))
            self.tabla.setSpan(0, 0, 1, 6)
            self.tabla.setItem(0, 0, item_aviso)
            return

        for row_idx, cita in enumerate(citas):
            self.tabla.insertRow(row_idx)
            self.tabla.setItem(row_idx, 0, QTableWidgetItem(cita[0]))
            self.tabla.setItem(row_idx, 1, QTableWidgetItem(cita[1]))
            self.tabla.setItem(row_idx, 2, QTableWidgetItem(cita[2]))
            item_barbero = QTableWidgetItem(f"✂️ {cita[3]}")
            item_barbero.setFont(QFont("Arial", 9, QFont.Bold))
            self.tabla.setItem(row_idx, 3, item_barbero)
            item_precio = QTableWidgetItem(f"${cita[4]:.2f}")
            item_precio.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.tabla.setItem(row_idx, 4, item_precio)
            estado = cita[5]
            item_estado = QTableWidgetItem(estado)
            item_estado.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            
            if estado == 'Pendiente':
                item_estado.setForeground(QColor('#FF8C00'))
            elif estado == 'Pagada':
                item_estado.setForeground(QColor('green'))
            
            font = item_estado.font()
            font.setBold(True)
            item_estado.setFont(font)
            self.tabla.setItem(row_idx, 5, item_estado)