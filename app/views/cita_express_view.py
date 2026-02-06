from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, 
    QGridLayout, QPushButton, QMessageBox, QButtonGroup, QFrame
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QFont, QColor
from controllers.citas_controller import CitasController
from controllers.barberos_controller import BarberosController

class CitaExpressView(QDialog):
    """Modal de Atención Inmediata (Multi-Barbero)."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Atención Inmediata - Cita Express")
        self.setModal(True)
        self.resize(500, 650)
        
        self.controller = CitasController()
        self.barberos_controller = BarberosController()
        self.servicio_seleccionado = None
        self.id_publico_general = self.controller.obtener_o_crear_cliente_publico()
        
        self.init_ui()
        self.cargar_datos_iniciales()

    def init_ui(self):
        self.setStyleSheet(
            """
            QDialog { background-color: #1F2A35; color: #ECF0F1; }
            QLabel { color: #ECF0F1; }
            QComboBox { background-color: #34495E; color: white; border: 1px solid #5D6D7E; padding: 5px; }
            QComboBox QAbstractItemView { background-color: #2C3E50; color: white; selection-background-color: #27AE60; }
            QLineEdit, QDateEdit, QTimeEdit { background-color: #ECF0F1; color: #2C3E50; border: 1px solid #95A5A6; border-radius: 4px; padding: 5px; }
            QPushButton#cta { background-color: #27AE60; color: white; font-weight: bold; border-radius: 8px; }
            QPushButton#cta:hover { background-color: #2ECC71; }
            """
        )
        self.layout_principal = QVBoxLayout()
        self.setLayout(self.layout_principal)

        lbl_titulo = QLabel("⚡ ATENCIÓN INMEDIATA")
        lbl_titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_titulo.setFont(QFont("Arial", 16, QFont.Bold))
        lbl_titulo.setStyleSheet("color: #D35400; margin-bottom: 10px;")
        self.layout_principal.addWidget(lbl_titulo)

        self.layout_principal.addWidget(QLabel("<b>Barbero:</b>"))
        self.combo_barberos = QComboBox()
        self.combo_barberos.setStyleSheet(self.combo_barberos.styleSheet() + " font-size: 14px;")
        self.layout_principal.addWidget(self.combo_barberos)

        self.layout_principal.addWidget(QLabel("<b>Cliente:</b>"))
        self.combo_clientes = QComboBox()
        self.combo_clientes.setEditable(True)
        self.layout_principal.addWidget(self.combo_clientes)

        self.layout_principal.addSpacing(10)
        self.layout_principal.addWidget(QLabel("<b>Seleccionar Servicio:</b>"))
        self.frame_servicios = QFrame()
        self.layout_servicios = QGridLayout()
        self.frame_servicios.setLayout(self.layout_servicios)
        self.layout_principal.addWidget(self.frame_servicios)
        self.grupo_servicios = QButtonGroup(self)
        self.grupo_servicios.setExclusive(True)
        self.grupo_servicios.buttonClicked.connect(self.servicio_clickeado)

        self.layout_principal.addSpacing(15)
        frame_resumen = QFrame()
        frame_resumen.setObjectName("resumen")
        frame_resumen.setStyleSheet("#resumen { background-color: #2C3E50; border: 1px solid #5D6D7E; border-radius: 8px; padding: 12px; }")
        layout_resumen = QVBoxLayout()
        frame_resumen.setLayout(layout_resumen)

        self.lbl_hora_inicio = QLabel(f"Hora Inicio: {self.controller.get_hora_actual_formateada()} (AHORA)")
        self.lbl_hora_fin = QLabel("Hora Fin Estimada: --:--")
        self.lbl_total = QLabel("Total: $0.00")
        self.lbl_total.setFont(QFont("Arial", 12, QFont.Bold))
        self.lbl_total.setStyleSheet("color: #E67E22;")

        layout_resumen.addWidget(self.lbl_hora_inicio)
        layout_resumen.addWidget(self.lbl_hora_fin)
        layout_resumen.addWidget(self.lbl_total)
        self.layout_principal.addWidget(frame_resumen)

        self.layout_principal.addStretch()
        self.btn_iniciar = QPushButton("🚀 INICIAR SERVICIO AHORA")
        self.btn_iniciar.setMinimumHeight(60)
        self.btn_iniciar.setObjectName("cta")
        self.btn_iniciar.clicked.connect(self.procesar_cita_express)
        self.layout_principal.addWidget(self.btn_iniciar)

    def cargar_datos_iniciales(self):
        for b in self.barberos_controller.obtener_barberos_activos():
            self.combo_barberos.addItem(f"✂️ {b[1]}", b[0])

        clientes = self.controller.obtener_clientes()
        index_publico = 0
        for i, c in enumerate(clientes):
            self.combo_clientes.addItem(c[1], c[0])
            if c[0] == self.id_publico_general: index_publico = i
        if self.id_publico_general: self.combo_clientes.setCurrentIndex(index_publico)

        for i, s in enumerate(self.controller.obtener_servicios_activos()):
            row, col = divmod(i, 2)
            btn = QPushButton(f"{s[1]}\n${s[2]:.2f}\n{s[3]} min")
            btn.setCheckable(True)
            btn.setFixedSize(180, 70)
            btn.setStyleSheet(
                """
                QPushButton {
                    background-color: #34495E;
                    color: white;
                    border: 1px solid #5D6D7E;
                    border-radius: 6px;
                    font-weight: 600;
                }
                QPushButton:checked {
                    background-color: #27AE60;
                    border: 2px solid #2ECC71;
                    color: white;
                }
                """
            )
            btn.data_servicio = s 
            self.grupo_servicios.addButton(btn)
            self.layout_servicios.addWidget(btn, row, col)

    def servicio_clickeado(self, btn):
        self.servicio_seleccionado = btn.data_servicio
        self.actualizar_calculos()

    def actualizar_calculos(self):
        if not self.servicio_seleccionado: return
        precio = self.servicio_seleccionado[2]
        duracion = self.servicio_seleccionado[3]
        hora_actual = self.controller.get_hora_actual_formateada()
        hora_fin = self.controller.calcular_hora_fin(hora_actual, duracion)
        self.lbl_hora_inicio.setText(f"Hora Inicio: {hora_actual} (AHORA)")
        self.lbl_hora_fin.setText(f"Hora Fin Estimada: {hora_fin}")
        self.lbl_total.setText(f"Total: ${precio:.2f}")

    def procesar_cita_express(self):
        id_barbero = self.combo_barberos.currentData()
        nombre_barbero = self.combo_barberos.currentText()
        id_cliente = self.combo_clientes.currentData()

        if not id_barbero: return QMessageBox.warning(self, "Error", "Seleccione barbero.")
        if not self.servicio_seleccionado: return QMessageBox.warning(self, "Error", "Seleccione servicio.")

        id_servicio = self.servicio_seleccionado[0]
        precio = self.servicio_seleccionado[2]
        duracion = self.servicio_seleccionado[3]
        
        fecha_hoy = QDate.currentDate().toString("yyyy-MM-dd")
        hora_inicio = self.controller.get_hora_actual_formateada()
        hora_fin = self.controller.calcular_hora_fin(hora_inicio, duracion)
        
        # Chequeo de solape antes de permitir overbooking
        if self.controller.hay_solapamiento(fecha_hoy, hora_inicio, hora_fin, id_barbero):
            respuesta = QMessageBox.warning(
                self, "Conflicto",
                f"El barbero {nombre_barbero} ya está ocupado en este momento.\n¿Forzar atención (Overbooking)?",
                QMessageBox.Yes | QMessageBox.No
            )
            if respuesta == QMessageBox.No: return

        exito = self.controller.crear_cita(id_cliente, id_servicio, id_barbero, fecha_hoy, hora_inicio, hora_fin, precio, notas="Cita Express")
        if exito:
            QMessageBox.information(self, "Listo", "Servicio iniciado correctamente.")
            self.accept()