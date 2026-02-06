from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, 
    QGridLayout, QPushButton, QDateEdit, QTimeEdit, 
    QMessageBox, QButtonGroup, QFrame, QTextEdit
)
from PySide6.QtCore import Qt, QDate, QTime
from controllers.citas_controller import CitasController
from controllers.barberos_controller import BarberosController

class AgendarCitaView(QDialog):
    """
    Ventana modal para agendar una nueva cita (Multi-Barbero).
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Nueva Cita")
        self.setModal(True)
        self.resize(600, 750)
        
        self.controller = CitasController()
        self.barberos_controller = BarberosController()
        
        self.servicio_seleccionado = None
        
        self.init_ui()
        self.cargar_datos_iniciales()

    def init_ui(self):
        self.setStyleSheet(
            """
            QDialog { background-color: #1F2A35; color: #ECF0F1; }
            QLabel { color: #ECF0F1; }
            QComboBox { background-color: #34495E; color: white; border: 1px solid #5D6D7E; padding: 5px; }
            QComboBox QAbstractItemView { background-color: #2C3E50; color: white; selection-background-color: #27AE60; }
            QLineEdit { background-color: #ECF0F1; color: #2C3E50; border: 1px solid #95A5A6; border-radius: 4px; padding: 5px; }
            QDateEdit, QTimeEdit { background-color: #ECF0F1; color: #2C3E50; border: 1px solid #BDC3C7; border-radius: 4px; padding: 5px; }
            QPushButton#primary { background-color: #27AE60; color: white; font-weight: bold; border-radius: 6px; padding: 10px; }
            QPushButton#primary:hover { background-color: #2ECC71; }
            QPushButton#ghost { background-color: #5D6D7E; color: white; border-radius: 6px; padding: 10px; }
            QPushButton#ghost:hover { background-color: #707B7C; }
            """
        )
        self.layout_principal = QVBoxLayout()
        self.setLayout(self.layout_principal)

        self.layout_principal.addWidget(QLabel("<b>1. Seleccionar Barbero:</b>"))
        self.combo_barberos = QComboBox()
        self.combo_barberos.setStyleSheet(self.combo_barberos.styleSheet() + " font-size: 14px;")
        self.layout_principal.addWidget(self.combo_barberos)

        self.layout_principal.addSpacing(10)
        self.layout_principal.addWidget(QLabel("<b>2. Seleccionar Cliente:</b>"))
        self.combo_clientes = QComboBox()
        self.combo_clientes.setEditable(True)
        self.layout_principal.addWidget(self.combo_clientes)

        self.layout_principal.addSpacing(10)
        self.layout_principal.addWidget(QLabel("<b>3. Seleccionar Servicio:</b>"))
        
        self.frame_servicios = QFrame()
        self.layout_servicios = QGridLayout()
        self.frame_servicios.setLayout(self.layout_servicios)
        self.layout_principal.addWidget(self.frame_servicios)
        
        self.grupo_servicios = QButtonGroup(self)
        self.grupo_servicios.setExclusive(True)
        self.grupo_servicios.buttonClicked.connect(self.servicio_clickeado)

        self.layout_principal.addSpacing(10)
        self.layout_principal.addWidget(QLabel("<b>4. Fecha y Hora de Inicio:</b>"))
        
        layout_tiempo = QHBoxLayout()
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setDisplayFormat("yyyy-MM-dd")
        
        self.time_edit = QTimeEdit()
        self.time_edit.setTime(QTime(8, 0))
        self.time_edit.setDisplayFormat("HH:mm")
        self.time_edit.timeChanged.connect(self.actualizar_resumen)

        layout_tiempo.addWidget(QLabel("Fecha:"))
        layout_tiempo.addWidget(self.date_edit)
        layout_tiempo.addSpacing(20)
        layout_tiempo.addWidget(QLabel("Hora Inicio:"))
        layout_tiempo.addWidget(self.time_edit)
        self.layout_principal.addLayout(layout_tiempo)

        self.layout_principal.addStretch()
        frame_resumen = QFrame()
        frame_resumen.setObjectName("resumen")
        frame_resumen.setStyleSheet("#resumen { background-color: #2C3E50; border: 1px solid #5D6D7E; border-radius: 8px; padding: 12px; }")
        layout_resumen = QVBoxLayout()
        frame_resumen.setLayout(layout_resumen)
        
        self.lbl_total = QLabel("Total Estimado: $0.00")
        self.lbl_total.setStyleSheet("font-size: 16px; font-weight: bold; color: #27AE60;")
        self.lbl_hora_fin = QLabel("Hora Fin Estimada: --:--")
        
        layout_resumen.addWidget(self.lbl_total)
        layout_resumen.addWidget(self.lbl_hora_fin)
        self.layout_principal.addWidget(frame_resumen)

        layout_botones = QHBoxLayout()
        self.btn_guardar = QPushButton("Agendar Cita")
        self.btn_guardar.setObjectName("primary")
        self.btn_guardar.clicked.connect(self.guardar_cita)
        
        self.btn_cancelar = QPushButton("Cancelar")
        self.btn_cancelar.setObjectName("ghost")
        self.btn_cancelar.clicked.connect(self.reject)
        
        layout_botones.addWidget(self.btn_guardar)
        layout_botones.addWidget(self.btn_cancelar)
        self.layout_principal.addLayout(layout_botones)

    def cargar_datos_iniciales(self):
        barberos = self.barberos_controller.obtener_barberos_activos()
        for b in barberos:
            self.combo_barberos.addItem(f"✂️ {b[1]}", b[0])

        clientes = self.controller.obtener_clientes()
        self.combo_clientes.addItem("-- Seleccione Cliente --", None)
        for c in clientes:
            self.combo_clientes.addItem(c[1], c[0])

        servicios = self.controller.obtener_servicios_activos()
        row, col = 0, 0
        max_cols = 3 
        
        for s in servicios:
            texto = f"{s[1]}\n${s[2]:.2f}\n{s[3]} min"
            btn = QPushButton(texto)
            btn.setCheckable(True)
            btn.setFixedSize(120, 80)
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
            col += 1
            if col >= max_cols:
                col = 0
                row += 1

    def servicio_clickeado(self, btn):
        self.servicio_seleccionado = btn.data_servicio
        self.actualizar_resumen()

    def actualizar_resumen(self):
        if not self.servicio_seleccionado: return
        precio = self.servicio_seleccionado[2]
        duracion = self.servicio_seleccionado[3]
        self.lbl_total.setText(f"Total Estimado: ${precio:.2f}")
        hora_inicio = self.time_edit.time().toString("HH:mm")
        hora_fin = self.controller.calcular_hora_fin(hora_inicio, duracion)
        self.lbl_hora_fin.setText(f"Hora Fin Estimada: {hora_fin}")

    def guardar_cita(self):
        id_barbero = self.combo_barberos.currentData()
        nombre_barbero = self.combo_barberos.currentText()
        id_cliente = self.combo_clientes.currentData()
        
        if not id_barbero:
            QMessageBox.warning(self, "Error", "Seleccione un barbero.")
            return
        if not id_cliente:
            QMessageBox.warning(self, "Error", "Seleccione un cliente.")
            return
        if not self.servicio_seleccionado:
            QMessageBox.warning(self, "Error", "Seleccione un servicio.")
            return

        id_servicio = self.servicio_seleccionado[0]
        precio_total = self.servicio_seleccionado[2]
        duracion = self.servicio_seleccionado[3]
        
        fecha_str = self.date_edit.date().toString("yyyy-MM-dd")
        hora_inicio_str = self.time_edit.time().toString("HH:mm")
        hora_fin_str = self.controller.calcular_hora_fin(hora_inicio_str, duracion)

        # Verificación de choque de agenda por barbero
        hay_conflicto = self.controller.hay_solapamiento(fecha_str, hora_inicio_str, hora_fin_str, id_barbero)
        
        if hay_conflicto:
            QMessageBox.critical(
                self, "Conflicto de Horario",
                f"El barbero {nombre_barbero} ya tiene una cita ocupada en el rango {hora_inicio_str} - {hora_fin_str}."
            )
            return

        exito = self.controller.crear_cita(id_cliente, id_servicio, id_barbero, fecha_str, hora_inicio_str, hora_fin_str, precio_total)
        
        if exito:
            QMessageBox.information(self, "Éxito", f"Cita agendada correctamente con {nombre_barbero}.")
            self.accept()
        else:
            QMessageBox.critical(self, "Error", "No se pudo guardar la cita.")