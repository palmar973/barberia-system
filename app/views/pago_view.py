from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, 
    QLineEdit, QPushButton, QMessageBox, QFormLayout, QFrame, QDoubleSpinBox,
    QListWidget, QListWidgetItem
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from controllers.pagos_controller import PagosController


class DesglosePagoDialog(QDialog):
    """
    Diálogo modal para configurar pagos mixtos (combinados).
    Permite agregar múltiples formas de pago parciales y retorna el total sumado.
    """
    
    def __init__(self, monto_a_cobrar, parent=None):
        super().__init__(parent)
        self.setWindowTitle("💳 Configurar Desglose de Pago Mixto")
        self.setModal(True)
        self.setFixedSize(550, 600)
        
        self.monto_a_cobrar = monto_a_cobrar
        self.pagos_mixtos = []  # Lista de pagos agregados
        
        self.init_ui()
    
    def init_ui(self):
        """Inicializar la interfaz del diálogo."""
        self.setStyleSheet(
            """
            QDialog { background-color: #1F2A35; color: #ECF0F1; }
            QLabel { color: #ECF0F1; }
            QComboBox { 
                background-color: #34495E; 
                color: white; 
                border: 1px solid #5D6D7E; 
                padding: 5px; 
                border-radius: 5px;
            }
            QComboBox QAbstractItemView { 
                background-color: #2C3E50; 
                color: white; 
                selection-background-color: #27AE60; 
            }
            QLineEdit { 
                background-color: #ECF0F1; 
                color: #2C3E50; 
                border: 1px solid #BDC3C7; 
                border-radius: 5px; 
                padding: 5px; 
            }
            QDoubleSpinBox { 
                background-color: #34495E; 
                color: #ECF0F1; 
                border: 2px solid #3498DB; 
                border-radius: 5px; 
                padding: 8px;
                font-size: 14px;
                font-weight: bold;
            }
            QDoubleSpinBox::up-button {
                subcontrol-origin: border;
                subcontrol-position: top right;
                width: 20px;
                border-left: 1px solid #BDC3C7;
                border-bottom: 1px solid #BDC3C7;
                border-top-right-radius: 3px;
                background-color: #D5DBDB; 
            }
            QDoubleSpinBox::up-button:hover { background-color: #3498DB; }
            QDoubleSpinBox::up-arrow {
                width: 0; 
                height: 0; 
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-bottom: 7px solid #2C3E50;
            }
            QDoubleSpinBox::down-button {
                subcontrol-origin: border;
                subcontrol-position: bottom right;
                width: 20px;
                border-left: 1px solid #BDC3C7;
                border-top: 1px solid #BDC3C7;
                border-bottom-right-radius: 3px;
                background-color: #D5DBDB;
            }
            QDoubleSpinBox::down-button:hover { background-color: #3498DB; }
            QDoubleSpinBox::down-arrow {
                width: 0; 
                height: 0; 
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 7px solid #2C3E50;
            }
            QListWidget {
                background-color: #34495E;
                color: white;
                border: 1px solid #5D6D7E;
                border-radius: 5px;
                padding: 5px;
            }
            QListWidget::item {
                padding: 5px;
                border-bottom: 1px solid #5D6D7E;
            }
            QListWidget::item:selected {
                background-color: #3498DB;
            }
            """
        )
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Título
        lbl_titulo = QLabel("💳 Desglose de Pago Mixto")
        lbl_titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_titulo.setFont(QFont("Arial", 14, QFont.Bold))
        lbl_titulo.setStyleSheet("color: #3498DB; margin-bottom: 10px;")
        layout.addWidget(lbl_titulo)
        
        # Mostrar monto total a cobrar
        lbl_monto_cobrar = QLabel(f"Monto Total a Cobrar: ${self.monto_a_cobrar:.2f}")
        lbl_monto_cobrar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_monto_cobrar.setFont(QFont("Arial", 12, QFont.Bold))
        lbl_monto_cobrar.setStyleSheet("color: #FFA726; background-color: #273444; padding: 8px; border-radius: 5px;")
        layout.addWidget(lbl_monto_cobrar)
        
        layout.addSpacing(15)
        
        # Formulario para agregar pagos
        frame_form = QFrame()
        frame_form.setStyleSheet("background-color: #273444; border: 1px solid #5D6D7E; border-radius: 8px; padding: 10px;")
        form_layout = QFormLayout()
        frame_form.setLayout(form_layout)
        
        lbl_form_titulo = QLabel("Agregar Pago Parcial")
        lbl_form_titulo.setFont(QFont("Arial", 11, QFont.Bold))
        lbl_form_titulo.setStyleSheet("color: #ECF0F1; border: none;")
        form_layout.addRow(lbl_form_titulo)
        
        # Método de pago
        self.combo_metodo = QComboBox()
        self.combo_metodo.addItems(['Efectivo ($)', 'Efectivo (Bs)', 'Pago Móvil', 'Zelle', 'Punto de Venta'])
        form_layout.addRow("Método:", self.combo_metodo)
        
        # Monto
        self.input_monto = QDoubleSpinBox()
        self.input_monto.setMaximum(999999.99)
        self.input_monto.setMinimum(0.00)
        self.input_monto.setDecimals(2)
        self.input_monto.setValue(0.00)
        self.input_monto.setMinimumHeight(40)
        form_layout.addRow("Monto ($):", self.input_monto)
        
        # Referencia
        self.input_referencia = QLineEdit()
        self.input_referencia.setPlaceholderText("Nro. de transacción (opcional para efectivo)")
        form_layout.addRow("Referencia:", self.input_referencia)
        
        layout.addWidget(frame_form)
        
        # Botón Agregar (grande y verde)
        self.btn_agregar = QPushButton("➕ Agregar Pago")
        self.btn_agregar.setMinimumHeight(45)
        self.btn_agregar.setFont(QFont("Arial", 12, QFont.Bold))
        self.btn_agregar.setStyleSheet("""
            QPushButton {
                background-color: #27AE60; 
                color: white; 
                font-weight: bold;
                border-radius: 5px;
                padding: 10px;
            }
            QPushButton:hover { background-color: #1E8449; }
        """)
        self.btn_agregar.clicked.connect(self.agregar_pago)
        layout.addWidget(self.btn_agregar)
        
        layout.addSpacing(10)
        
        # Lista de pagos agregados
        lbl_lista = QLabel("Pagos Agregados:")
        lbl_lista.setFont(QFont("Arial", 10, QFont.Bold))
        layout.addWidget(lbl_lista)
        
        self.list_pagos = QListWidget()
        self.list_pagos.setMinimumHeight(150)
        layout.addWidget(self.list_pagos)
        
        # Botón eliminar
        self.btn_eliminar = QPushButton("🗑️ Eliminar Seleccionado")
        self.btn_eliminar.setStyleSheet("""
            QPushButton {
                background-color: #E74C3C; 
                color: white; 
                font-weight: bold;
                border-radius: 3px;
                padding: 5px;
            }
            QPushButton:hover { background-color: #C0392B; }
        """)
        self.btn_eliminar.clicked.connect(self.eliminar_pago)
        layout.addWidget(self.btn_eliminar)
        
        layout.addSpacing(10)
        
        # Label mostrando el TOTAL ACUMULADO
        self.lbl_total = QLabel("TOTAL ACUMULADO: $0.00")
        self.lbl_total.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_total.setFont(QFont("Arial", 16, QFont.Bold))
        self.lbl_total.setStyleSheet(
            "color: #2ECC71; background-color: #1F2A35; padding: 15px; border-radius: 8px; border: 2px solid #27AE60;"
        )
        layout.addWidget(self.lbl_total)
        
        layout.addSpacing(15)
        
        # Botones Aceptar / Cancelar
        layout_botones = QHBoxLayout()
        
        self.btn_aceptar = QPushButton("✓ Aceptar")
        self.btn_aceptar.setMinimumHeight(45)
        self.btn_aceptar.setFont(QFont("Arial", 11, QFont.Bold))
        self.btn_aceptar.setStyleSheet("""
            QPushButton {
                background-color: #2E7D32; 
                color: white; 
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover { background-color: #1B5E20; }
        """)
        self.btn_aceptar.clicked.connect(self.aceptar)
        
        self.btn_cancelar = QPushButton("✗ Cancelar")
        self.btn_cancelar.setMinimumHeight(45)
        self.btn_cancelar.setFont(QFont("Arial", 11, QFont.Bold))
        self.btn_cancelar.setStyleSheet("""
            QPushButton {
                background-color: #95A5A6; 
                color: white; 
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover { background-color: #7F8C8D; }
        """)
        self.btn_cancelar.clicked.connect(self.reject)
        
        layout_botones.addWidget(self.btn_aceptar)
        layout_botones.addWidget(self.btn_cancelar)
        layout.addLayout(layout_botones)
    
    def agregar_pago(self):
        """Agregar un pago parcial a la lista."""
        metodo = self.combo_metodo.currentText()
        monto = self.input_monto.value()
        referencia = self.input_referencia.text().strip()
        
        if monto <= 0:
            QMessageBox.warning(self, "Monto Inválido", "El monto debe ser mayor que 0.")
            return
        
        # Validar referencia para métodos no efectivo
        if 'Efectivo' not in metodo and not referencia:
            QMessageBox.warning(
                self, 
                "Falta Referencia", 
                f"Para pagos en {metodo}, la referencia es obligatoria."
            )
            return
        
        # Agregar a la lista interna
        pago = {
            'metodo': metodo,
            'monto': monto,
            'referencia': referencia
        }
        self.pagos_mixtos.append(pago)
        
        # Mostrar en el QListWidget
        if referencia:
            texto = f"{metodo}: ${monto:.2f} (Ref: {referencia})"
        else:
            texto = f"{metodo}: ${monto:.2f}"
        self.list_pagos.addItem(texto)
        
        # Actualizar el total acumulado
        self.actualizar_total()
        
        # Limpiar campos
        self.input_monto.setValue(0.00)
        self.input_referencia.clear()
    
    def eliminar_pago(self):
        """Eliminar el pago seleccionado de la lista."""
        current_row = self.list_pagos.currentRow()
        
        if current_row < 0:
            QMessageBox.warning(
                self, 
                "Sin Selección", 
                "Por favor, seleccione un pago para eliminar."
            )
            return
        
        # Eliminar de la lista interna y del widget
        del self.pagos_mixtos[current_row]
        self.list_pagos.takeItem(current_row)
        
        # Actualizar el total
        self.actualizar_total()
    
    def actualizar_total(self):
        """Actualizar el label del total acumulado."""
        total = sum(pago['monto'] for pago in self.pagos_mixtos)
        self.lbl_total.setText(f"TOTAL ACUMULADO: ${total:.2f}")
        
        # Cambiar color según si cubre o no el monto
        if total >= self.monto_a_cobrar:
            self.lbl_total.setStyleSheet(
                "color: #2ECC71; background-color: #1F2A35; padding: 15px; border-radius: 8px; border: 2px solid #27AE60;"
            )
        else:
            self.lbl_total.setStyleSheet(
                "color: #FFA726; background-color: #1F2A35; padding: 15px; border-radius: 8px; border: 2px solid #FFA726;"
            )
    
    def aceptar(self):
        """Validar y aceptar el diálogo."""
        if not self.pagos_mixtos:
            QMessageBox.warning(
                self, 
                "Sin Pagos", 
                "Debe agregar al menos un pago antes de aceptar."
            )
            return
        
        total = sum(pago['monto'] for pago in self.pagos_mixtos)
        
        if total < self.monto_a_cobrar:
            faltante = self.monto_a_cobrar - total
            QMessageBox.warning(
                self, 
                "⚠️ Pago Insuficiente",
                f"El total acumulado (${total:.2f}) no cubre el monto a cobrar (${self.monto_a_cobrar:.2f}).\n\n"
                f"Falta: ${faltante:.2f}"
            )
            return
        
        self.accept()
    
    def get_pagos_mixtos(self):
        """Retornar la lista de pagos y el total sumado."""
        total = sum(pago['monto'] for pago in self.pagos_mixtos)
        return self.pagos_mixtos, total

class PagoView(QDialog):
    """
    Modal para procesar el cobro de una cita.
    Calcula conversión a Bs si hay tasa BCV disponible.
    Permite pagos mixtos y valida montos completos.
    """
    
    # Constantes para métodos de pago
    METODO_MIXTO = "Mixto"
    METODO_MIXTO_DISPLAY = "Mixto (Combinado)"
    
    # Tolerancia para validación de montos decimales (evitar errores de coma flotante)
    TOLERANCIA_MONTO = 0.01

    def __init__(self, id_cita, tasa_bcv=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Procesar Pago")
        self.setModal(True)
        # Tamaño reducido sin el frame de pagos mixtos
        self.setFixedSize(450, 650)
        
        self.id_cita = id_cita
        self.tasa_bcv = tasa_bcv
        self.controller = PagosController()
        
        self.monto_a_cobrar = 0.0
        self.pagos_mixtos = []  # Lista para almacenar los pagos parciales
        
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
            
            /* ESTILO CORREGIDO PARA SPINBOX (Flechas visibles) */
            QDoubleSpinBox { 
                background-color: #34495E; 
                color: #ECF0F1; 
                border: 2px solid #3498DB; 
                border-radius: 5px; 
                padding: 8px;
                font-size: 16px;
                font-weight: bold;
            }
            /* Botón Arriba */
            QDoubleSpinBox::up-button {
                subcontrol-origin: border;
                subcontrol-position: top right;
                width: 20px;
                border-left: 1px solid #BDC3C7;
                border-bottom: 1px solid #BDC3C7;
                border-top-right-radius: 3px;
                background-color: #D5DBDB; 
            }
            QDoubleSpinBox::up-button:hover { background-color: #3498DB; }
            
            /* Flecha Arriba (Dibujada con CSS) */
            QDoubleSpinBox::up-arrow {
                width: 0; 
                height: 0; 
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-bottom: 7px solid #2C3E50; /* Color de la flecha */
            }

            /* Botón Abajo */
            QDoubleSpinBox::down-button {
                subcontrol-origin: border;
                subcontrol-position: bottom right;
                width: 20px;
                border-left: 1px solid #BDC3C7;
                border-top: 1px solid #BDC3C7;
                border-bottom-right-radius: 3px;
                background-color: #D5DBDB;
            }
            QDoubleSpinBox::down-button:hover { background-color: #3498DB; }
            
            /* Flecha Abajo (Dibujada con CSS) */
            QDoubleSpinBox::down-arrow {
                width: 0; 
                height: 0; 
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 7px solid #2C3E50; /* Color de la flecha */
            }

            /* Estilos para la lista de pagos mixtos */
            QListWidget {
                background-color: #34495E;
                color: white;
                border: 1px solid #5D6D7E;
                border-radius: 5px;
                padding: 5px;
            }
            QListWidget::item {
                padding: 5px;
                border-bottom: 1px solid #5D6D7E;
            }
            QListWidget::item:selected {
                background-color: #3498DB;
            }
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

        layout.addSpacing(15)

        # ========== NUEVA SECCIÓN: CALCULADORA DE VUELTO ==========
        frame_calculadora = QFrame()
        frame_calculadora.setStyleSheet(
            "background-color: #2b2b2b; border: 2px solid #FFA726; border-radius: 8px;"
        )
        
        # Layout principal con VBox para título + formulario + resultado
        layout_calculadora_principal = QVBoxLayout()
        frame_calculadora.setLayout(layout_calculadora_principal)

        lbl_calc_titulo = QLabel("💰 Calculadora de Vuelto")
        lbl_calc_titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_calc_titulo.setFont(QFont("Arial", 12, QFont.Bold))
        lbl_calc_titulo.setStyleSheet("color: #FFA726; border: none;")
        layout_calculadora_principal.addWidget(lbl_calc_titulo)

        # Total a Pagar
        self.lbl_total_a_pagar = QLabel("Total a Pagar: $0.00 / Bs 0.00")
        self.lbl_total_a_pagar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_total_a_pagar.setStyleSheet("color: #ECF0F1; font-size: 13px; font-weight: bold; border: none;")
        layout_calculadora_principal.addWidget(self.lbl_total_a_pagar)

        layout_calculadora_principal.addSpacing(10)

        # Formulario con QFormLayout para alineación correcta
        layout_formulario = QFormLayout()
        layout_formulario.setSpacing(15)
        layout_formulario.setContentsMargins(20, 20, 20, 20)
        
        # Monto Recibido
        lbl_monto_recibido = QLabel("Monto Recibido:")
        lbl_monto_recibido.setStyleSheet("font-weight: bold; border: none;")
        self.input_monto_recibido = QDoubleSpinBox()
        self.input_monto_recibido.setMaximum(999999.99)
        self.input_monto_recibido.setMinimum(0.00)
        self.input_monto_recibido.setDecimals(2)
        self.input_monto_recibido.setValue(0.00)
        self.input_monto_recibido.setMinimumHeight(45)
        layout_formulario.addRow(lbl_monto_recibido, self.input_monto_recibido)

        # Moneda Recibida
        lbl_moneda_recibida = QLabel("Moneda Recibida:")
        lbl_moneda_recibida.setStyleSheet("font-weight: bold; border: none;")
        self.combo_moneda_recibida = QComboBox()
        self.combo_moneda_recibida.addItems(['USD ($)', 'Bolívares (Bs)'])
        self.combo_moneda_recibida.setMinimumHeight(35)
        layout_formulario.addRow(lbl_moneda_recibida, self.combo_moneda_recibida)
        
        layout_calculadora_principal.addLayout(layout_formulario)

        layout_calculadora_principal.addSpacing(15)

        # Vuelto / Restante (Resultado) - Destacado con fuente grande y negrita
        self.lbl_vuelto_resultado = QLabel("VUELTO: $0.00 / Bs 0.00")
        self.lbl_vuelto_resultado.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_vuelto_resultado.setFont(QFont("Arial", 16, QFont.Bold))
        self.lbl_vuelto_resultado.setStyleSheet(
            "color: #2ECC71; background-color: #1F2A35; padding: 12px; border-radius: 5px; border: none;"
        )
        layout_calculadora_principal.addWidget(self.lbl_vuelto_resultado)

        layout.addWidget(frame_calculadora)
        # ========== FIN CALCULADORA DE VUELTO ==========

        layout.addSpacing(15)

        # ========== SELECCIÓN DE MÉTODO DE PAGO ==========
        layout.addWidget(QLabel("<b>Método de Pago:</b>"))
        self.combo_metodo = QComboBox()
        # Agregamos la opción Mixto
        self.combo_metodo.addItems(['Efectivo ($)', 'Efectivo (Bs)', 'Pago Móvil', 'Zelle', 'Punto de Venta', self.METODO_MIXTO_DISPLAY])
        self.combo_metodo.currentIndexChanged.connect(self.on_metodo_changed)
        layout.addWidget(self.combo_metodo)

        # ========== BOTÓN PARA CONFIGURAR PAGO MIXTO (Inicialmente Oculto) ==========
        self.btn_configurar_mixto = QPushButton("📝 Configurar Desglose")
        self.btn_configurar_mixto.setMinimumHeight(40)
        self.btn_configurar_mixto.setStyleSheet("""
            QPushButton {
                background-color: #3498DB; 
                color: white; 
                font-weight: bold; 
                font-size: 13px;
                border-radius: 5px;
                padding: 8px;
            }
            QPushButton:hover { background-color: #2874A6; }
        """)
        self.btn_configurar_mixto.clicked.connect(self.abrir_dialogo_mixto)
        self.btn_configurar_mixto.setVisible(False)
        layout.addWidget(self.btn_configurar_mixto)

        layout.addWidget(QLabel("<b>Referencia / Nota Final:</b>"))
        self.input_referencia = QLineEdit()
        self.input_referencia.setObjectName("ref")
        self.input_referencia.setPlaceholderText("Nro. de transacción (Opcional para Efectivo)")
        layout.addWidget(self.input_referencia)

        layout.addStretch()

        layout_botones = QHBoxLayout()
        
        self.btn_cobrar = QPushButton("CONFIRMAR PAGO")
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

        # Conectar señales para cálculo automático
        self.input_monto_recibido.valueChanged.connect(self.calcular_vuelto)
        self.combo_moneda_recibida.currentIndexChanged.connect(self.calcular_vuelto)

    def on_metodo_changed(self):
        """Mostrar/ocultar botón de configuración según el método seleccionado."""
        metodo = self.combo_metodo.currentText()
        
        if self.METODO_MIXTO in metodo:
            # Modo mixto: mostrar botón de configuración y bloquear input principal
            self.btn_configurar_mixto.setVisible(True)
            self.input_monto_recibido.setReadOnly(True)
            self.input_monto_recibido.setStyleSheet("""
                QDoubleSpinBox { 
                    background-color: #7F8C8D; 
                    color: #ECF0F1; 
                    border: 2px solid #95A5A6; 
                    border-radius: 5px; 
                    padding: 8px;
                    font-size: 16px;
                    font-weight: bold;
                }
            """)
            # Limpiar pagos mixtos anteriores al entrar en este modo
            self.pagos_mixtos.clear()
            self.input_monto_recibido.setValue(0.00)
        else:
            # Modo normal: ocultar botón y desbloquear input
            self.btn_configurar_mixto.setVisible(False)
            self.input_monto_recibido.setReadOnly(False)
            # Restaurar estilo normal
            self.input_monto_recibido.setStyleSheet("""
                QDoubleSpinBox { 
                    background-color: #34495E; 
                    color: #ECF0F1; 
                    border: 2px solid #3498DB; 
                    border-radius: 5px; 
                    padding: 8px;
                    font-size: 16px;
                    font-weight: bold;
                }
                QDoubleSpinBox::up-button {
                    subcontrol-origin: border; subcontrol-position: top right; width: 20px;
                    border-left: 1px solid #BDC3C7; border-bottom: 1px solid #BDC3C7;
                    border-top-right-radius: 3px; background-color: #D5DBDB; 
                }
                QDoubleSpinBox::up-arrow {
                    width: 0; height: 0; 
                    border-left: 5px solid transparent; border-right: 5px solid transparent;
                    border-bottom: 7px solid #2C3E50;
                }
                QDoubleSpinBox::down-button {
                    subcontrol-origin: border; subcontrol-position: bottom right; width: 20px;
                    border-left: 1px solid #BDC3C7; border-top: 1px solid #BDC3C7;
                    border-bottom-right-radius: 3px; background-color: #D5DBDB;
                }
                QDoubleSpinBox::down-arrow {
                    width: 0; height: 0; 
                    border-left: 5px solid transparent; border-right: 5px solid transparent;
                    border-top: 7px solid #2C3E50;
                }
            """)
            self.pagos_mixtos.clear()
    
    def abrir_dialogo_mixto(self):
        """Abrir el diálogo modal para configurar pagos mixtos."""
        dialogo = DesglosePagoDialog(self.monto_a_cobrar, parent=self)
        
        # Si el usuario acepta, obtener los pagos y actualizar
        if dialogo.exec() == QDialog.DialogCode.Accepted:
            self.pagos_mixtos, total = dialogo.get_pagos_mixtos()
            self.input_monto_recibido.setValue(total)
            # Forzar recalcular vuelto
            self.calcular_vuelto()
            
            # Mostrar mensaje de confirmación
            QMessageBox.information(
                self,
                "Desglose Configurado",
                f"Se configuraron {len(self.pagos_mixtos)} pagos por un total de ${total:.2f}"
            )

    def cargar_datos(self):
        """Consulta el controlador para llenar los labels."""
        datos = self.controller.obtener_detalle_cita(self.id_cita)
        if datos:
            self.lbl_cliente.setText(datos[0])
            self.lbl_servicio.setText(datos[1])
            self.monto_a_cobrar = datos[2]
            self.lbl_monto.setText(f"${self.monto_a_cobrar:.2f}")
            self.lbl_hora.setText(datos[3])
            
            # Actualizar el label "Total a Pagar" en la calculadora
            if self.tasa_bcv and self.tasa_bcv > 0:
                total_bs = self.monto_a_cobrar * self.tasa_bcv
                self.lbl_total_a_pagar.setText(f"Total a Pagar: ${self.monto_a_cobrar:.2f} / Bs {total_bs:,.2f}")
            else:
                self.lbl_total_a_pagar.setText(f"Total a Pagar: ${self.monto_a_cobrar:.2f}")
            
            # Calcular vuelto inicial
            self.calcular_vuelto()
                
        else:
            QMessageBox.critical(self, "Error", "No se pudo cargar la información de la cita.")
            self.reject()

    def calcular_vuelto(self):
        """
        Calcula el vuelto o faltante en tiempo real.
        Muestra el resultado en USD y Bs.
        """
        try:
            # Obtener valores
            monto_recibido = self.input_monto_recibido.value()
            moneda_seleccionada = self.combo_moneda_recibida.currentText()
            
            # Convertir a USD para comparar
            if 'Bs' in moneda_seleccionada or 'Bolívares' in moneda_seleccionada:
                # Si recibimos en Bolívares, convertir a USD
                if self.tasa_bcv and self.tasa_bcv > 0:
                    monto_recibido_usd = monto_recibido / self.tasa_bcv
                else:
                    # Si no hay tasa, no podemos calcular
                    self.lbl_vuelto_resultado.setText("⚠️ No hay tasa BCV disponible")
                    self.lbl_vuelto_resultado.setStyleSheet(
                        "color: #FFA726; background-color: #1F2A35; padding: 10px; border-radius: 5px; font-weight: bold; font-size: 14px;"
                    )
                    return
            else:
                # Ya está en USD
                monto_recibido_usd = monto_recibido
            
            # Calcular diferencia
            diferencia_usd = monto_recibido_usd - self.monto_a_cobrar
            
            # Calcular en Bs
            if self.tasa_bcv and self.tasa_bcv > 0:
                diferencia_bs = diferencia_usd * self.tasa_bcv
            else:
                diferencia_bs = 0.0
            
            # Mostrar resultado según si es vuelto o falta
            if diferencia_usd < 0:
                # FALTA dinero
                falta_usd = abs(diferencia_usd)
                falta_bs = abs(diferencia_bs)
                self.lbl_vuelto_resultado.setText(f"⚠️ FALTA: ${falta_usd:.2f} / Bs {falta_bs:,.2f}")
                self.lbl_vuelto_resultado.setStyleSheet(
                    "color: #E74C3C; background-color: #1F2A35; padding: 10px; border-radius: 5px; font-weight: bold; font-size: 14px;"
                )
            else:
                # HAY vuelto o es exacto
                self.lbl_vuelto_resultado.setText(f"✓ VUELTO: ${diferencia_usd:.2f} / Bs {diferencia_bs:,.2f}")
                self.lbl_vuelto_resultado.setStyleSheet(
                    "color: #2ECC71; background-color: #1F2A35; padding: 10px; border-radius: 5px; font-weight: bold; font-size: 14px;"
                )
                
        except Exception as e:
            # Manejo de errores con logging
            import logging
            logging.error(f"Error en calcular_vuelto: {str(e)}", exc_info=True)
            self.lbl_vuelto_resultado.setText(f"❌ Error al calcular: Verifique los valores")
            self.lbl_vuelto_resultado.setStyleSheet(
                "color: #E74C3C; background-color: #1F2A35; padding: 10px; border-radius: 5px; font-weight: bold; font-size: 14px;"
            )

    def procesar_pago(self):
        metodo = self.combo_metodo.currentText()
        referencia = self.input_referencia.text().strip()

        # ========== VALIDACIÓN DE SEGURIDAD (NO PERMITIR PAGO INCOMPLETO) ==========
        monto_recibido = self.input_monto_recibido.value()
        moneda_seleccionada = self.combo_moneda_recibida.currentText()
        
        # Normalizar a USD
        if 'Bs' in moneda_seleccionada or 'Bolívares' in moneda_seleccionada:
            if self.tasa_bcv and self.tasa_bcv > 0:
                monto_recibido_usd = monto_recibido / self.tasa_bcv
            else:
                QMessageBox.warning(self, "Error de Tasa", "No se puede verificar el monto en Bs sin tasa BCV.")
                return
        else:
            monto_recibido_usd = monto_recibido

        # Validar si cubre el costo (con pequeña tolerancia por decimales)
        if monto_recibido_usd < (self.monto_a_cobrar - self.TOLERANCIA_MONTO):
            faltante = self.monto_a_cobrar - monto_recibido_usd
            QMessageBox.warning(
                self, 
                "⚠️ Pago Insuficiente", 
                f"El monto recibido (${monto_recibido_usd:.2f}) no cubre el costo del servicio (${self.monto_a_cobrar:.2f}).\n\n"
                f"Falta por cobrar: ${faltante:.2f}\n\n"
                "Por favor, complete el pago antes de confirmar."
            )
            return
        # ===========================================================================

        # Manejo especial para GUARDAR PAGO MIXTO
        if self.METODO_MIXTO in metodo:
            if not self.pagos_mixtos:
                QMessageBox.warning(self, "Sin Pagos", "Seleccionó pago Mixto pero no agregó ningún pago parcial.")
                return
            
            # Concatenar todos los pagos en un solo string para guardarlo en la DB sin cambios de esquema
            detalles = []
            for p in self.pagos_mixtos:
                ref_text = f"Ref:{p['referencia']}" if p['referencia'] else "SinRef"
                detalles.append(f"[{p['metodo']} ${p['monto']:.2f} {ref_text}]")
            
            # Sobrescribimos la referencia final con el detalle completo
            referencia = "MIXTO: " + " + ".join(detalles)
            # El método lo guardamos como "Mixto"
            metodo = "Mixto"
        
        else:
            # Validación estándar para pagos únicos
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