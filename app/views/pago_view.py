from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, 
    QLineEdit, QPushButton, QMessageBox, QFormLayout, QFrame
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from controllers.pagos_controller import PagosController

class PagoView(QDialog):
    """
    Modal para procesar el cobro de una cita.
    Calcula conversión a Bs si hay tasa BCV disponible.
    """
    def __init__(self, id_cita, tasa_bcv=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Procesar Pago")
        self.setModal(True)
        self.setFixedSize(400, 500)
        
        self.id_cita = id_cita
        self.tasa_bcv = tasa_bcv
        self.controller = PagosController()
        
        self.monto_a_cobrar = 0.0
        
        self.init_ui()
        self.cargar_datos()

    def init_ui(self):
        self.setStyleSheet(
            """
            QDialog { background-color: #1F2A35; color: #ECF0F1; }
            QLabel { color: #ECF0F1; }
            QLineEdit[readonly="true"] {
                background-color: #34495E;
                color: white;
                border: 1px solid #5D6D7E;
                border-radius: 5px;
                padding: 5px;
            }
            QComboBox { background-color: #34495E; color: white; border: 1px solid #5D6D7E; padding: 5px; }
            QComboBox QAbstractItemView { background-color: #2C3E50; color: white; selection-background-color: #27AE60; }
            QLineEdit#ref { background-color: #ECF0F1; color: #2C3E50; border: 1px solid #BDC3C7; border-radius: 5px; padding: 5px; }
            """
        )
        layout = QVBoxLayout()
        self.setLayout(layout)

        lbl_titulo = QLabel("Detalle de Cobro")
        lbl_titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_titulo.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(lbl_titulo)

        frame_resumen = QFrame()
        frame_resumen.setStyleSheet("background-color: #273444; border: 1px solid #5D6D7E; border-radius: 8px; padding: 6px;")
        layout_resumen = QFormLayout()
        frame_resumen.setLayout(layout_resumen)

        self.lbl_cliente = QLineEdit("Cargando...")
        self.lbl_cliente.setReadOnly(True)
        self.lbl_servicio = QLineEdit("Cargando...")
        self.lbl_servicio.setReadOnly(True)
        self.lbl_hora = QLineEdit("Cargando...")
        self.lbl_hora.setReadOnly(True)
        self.lbl_monto = QLabel("$0.00")
        
        self.lbl_monto.setStyleSheet("background-color: #1F2A35; color: #2ECC71; font-weight: bold; font-size: 18px; padding: 6px; border-radius: 4px;")

        layout_resumen.addRow("Cliente:", self.lbl_cliente)
        layout_resumen.addRow("Servicio:", self.lbl_servicio)
        layout_resumen.addRow("Hora:", self.lbl_hora)
        layout_resumen.addRow("TOTAL (USD):", self.lbl_monto)
        
        layout.addWidget(frame_resumen)
        
        if self.tasa_bcv and self.tasa_bcv > 0:
            frame_bs = QFrame()
            frame_bs.setStyleSheet("background-color: #E3F2FD; border: 1px solid #2196F3; border-radius: 5px; padding: 5px;")
            layout_bs = QVBoxLayout()
            frame_bs.setLayout(layout_bs)
            
            self.lbl_tasa_info = QLabel(f"Tasa BCV: {self.tasa_bcv:.4f} Bs/$")
            self.lbl_tasa_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.lbl_tasa_info.setStyleSheet("color: #1565C0; font-weight: bold;")
            
            self.lbl_total_bs = QLabel("Total Bs: 0.00")
            self.lbl_total_bs.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.lbl_total_bs.setFont(QFont("Arial", 14, QFont.Bold))
            self.lbl_total_bs.setStyleSheet("color: #0D47A1;")
            
            layout_bs.addWidget(self.lbl_tasa_info)
            layout_bs.addWidget(self.lbl_total_bs)
            layout.addWidget(frame_bs)

        layout.addSpacing(20)

        layout.addWidget(QLabel("<b>Método de Pago:</b>"))
        self.combo_metodo = QComboBox()
        self.combo_metodo.addItems(['Efectivo ($)', 'Efectivo (Bs)', 'Pago Móvil', 'Zelle', 'Punto de Venta'])
        layout.addWidget(self.combo_metodo)

        layout.addWidget(QLabel("<b>Referencia / Nota:</b>"))
        self.input_referencia = QLineEdit()
        self.input_referencia.setObjectName("ref")
        self.input_referencia.setPlaceholderText("Nro. de transacción (Opcional para Efectivo)")
        layout.addWidget(self.input_referencia)

        layout.addStretch()

        layout_botones = QHBoxLayout()
        
        self.btn_cobrar = QPushButton("COBRAR")
        self.btn_cobrar.setMinimumHeight(45)
        self.btn_cobrar.setStyleSheet("""
            QPushButton {
                background-color: #2E7D32; 
                color: white; 
                font-weight: bold; 
                font-size: 14px;
                border-radius: 5px;
            }
            QPushButton:hover { background-color: #1B5E20; }
        """)
        
        self.btn_cancelar = QPushButton("Cancelar")
        self.btn_cancelar.setMinimumHeight(45)
        
        layout_botones.addWidget(self.btn_cobrar)
        layout_botones.addWidget(self.btn_cancelar)
        
        layout.addLayout(layout_botones)

        self.btn_cobrar.clicked.connect(self.procesar_pago)
        self.btn_cancelar.clicked.connect(self.reject)

    def cargar_datos(self):
        """Consulta el controlador para llenar los labels."""
        datos = self.controller.obtener_detalle_cita(self.id_cita)
        if datos:
            self.lbl_cliente.setText(datos[0])
            self.lbl_servicio.setText(datos[1])
            self.monto_a_cobrar = datos[2]
            self.lbl_monto.setText(f"${self.monto_a_cobrar:.2f}")
            self.lbl_hora.setText(datos[3])
            
            if self.tasa_bcv and self.tasa_bcv > 0:
                total_bs = self.monto_a_cobrar * self.tasa_bcv
                self.lbl_total_bs.setText(f"Total Bs: {total_bs:,.2f}")
                
        else:
            QMessageBox.critical(self, "Error", "No se pudo cargar la información de la cita.")
            self.reject()

    def procesar_pago(self):
        metodo = self.combo_metodo.currentText()
        referencia = self.input_referencia.text().strip()

        if 'Efectivo' not in metodo and not referencia:
            QMessageBox.warning(self, "Falta Referencia", f"Para pagos en {metodo}, la referencia es obligatoria.")
            return

        confirmacion = QMessageBox.question(
            self, "Confirmar Pago",
            f"¿Desea procesar el pago de ${self.monto_a_cobrar:.2f} en {metodo}?",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirmacion == QMessageBox.Yes:
            exito = self.controller.registrar_pago(self.id_cita, self.monto_a_cobrar, metodo, referencia)
            
            if exito:
                QMessageBox.information(self, "Pago Exitoso", "El pago ha sido registrado correctamente.")
                self.accept()
            else:
                QMessageBox.critical(self, "Error", "Hubo un error al registrar el pago en la base de datos.")