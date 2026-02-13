from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QLineEdit, QPushButton, QMessageBox, QFormLayout, QFrame, QDoubleSpinBox,
    QListWidget, QDialogButtonBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QDoubleValidator
from controllers.pagos_controller import PagosController


class DesglosePagoDialog(QDialog):
    def __init__(self, tasa_bcv=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Desglose de Pago Mixto")
        self.setModal(True)
        self.setFixedSize(500, 500)

        self.tasa_bcv = tasa_bcv
        self.pagos = []
        self.total_acumulado = 0.0

        self.setStyleSheet(
            """
            QDialog { background-color: #2b2b2b; color: white; }
            QLabel { color: white; }
            QComboBox {
                background-color: #3a3a3a;
                color: white;
                border: 1px solid #555;
                border-radius: 5px;
                padding: 5px;
            }
            QComboBox QAbstractItemView {
                background-color: #2f2f2f;
                color: white;
                selection-background-color: #27AE60;
            }
            QLineEdit, QDoubleSpinBox {
                background-color: #3a3a3a;
                color: white;
                border: 1px solid #555;
                border-radius: 5px;
                padding: 6px;
            }
            QListWidget {
                background-color: #3a3a3a;
                color: white;
                border: 1px solid #555;
                border-radius: 5px;
                padding: 5px;
            }
            QListWidget::item {
                padding: 5px;
                border-bottom: 1px solid #555;
            }
            QListWidget::item:selected {
                background-color: #3498DB;
            }
            QPushButton {
                background-color: #4a4a4a;
                color: white;
                border: 1px solid #666;
                border-radius: 5px;
                padding: 6px 10px;
            }
            QPushButton:hover { background-color: #5a5a5a; }
            """
        )

        layout = QVBoxLayout()
        self.setLayout(layout)

        form_row = QHBoxLayout()

        self.combo_metodo = QComboBox()
        self.combo_metodo.addItems(['Efectivo ($)', 'Efectivo (Bs)', 'Pago Móvil', 'Zelle', 'Punto de Venta'])
        form_row.addWidget(self.combo_metodo, 2)

        self.input_monto = QDoubleSpinBox()
        self.input_monto.setMaximum(999999.99)
        self.input_monto.setMinimum(0.00)
        self.input_monto.setDecimals(2)
        self.input_monto.setValue(0.00)
        form_row.addWidget(self.input_monto, 1)

        self.input_referencia = QLineEdit()
        self.input_referencia.setPlaceholderText("Referencia")
        form_row.addWidget(self.input_referencia, 2)

        self.btn_agregar = QPushButton("Agregar")
        self.btn_agregar.setStyleSheet(
            """
            QPushButton {
                background-color: #27AE60;
                color: white;
                font-weight: bold;
                border-radius: 5px;
                padding: 6px 12px;
            }
            QPushButton:hover { background-color: #1E8449; }
            """
        )
        self.btn_agregar.clicked.connect(self.agregar_pago)
        form_row.addWidget(self.btn_agregar, 1)

        layout.addLayout(form_row)

        self.list_pagos = QListWidget()
        layout.addWidget(self.list_pagos)

        self.lbl_total = QLabel("TOTAL ACUMULADO: $0.00")
        self.lbl_total.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_total.setFont(QFont("Arial", 14, QFont.Bold))
        self.lbl_total.setStyleSheet(
            "color: #2ECC71; background-color: #1F2A35; padding: 10px; border-radius: 6px;"
        )
        layout.addWidget(self.lbl_total)

        botones = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        botones.button(QDialogButtonBox.Save).setText("Guardar/Aceptar")
        botones.button(QDialogButtonBox.Cancel).setText("Cancelar")
        botones.accepted.connect(self.validar_y_aceptar)
        botones.rejected.connect(self.reject)
        layout.addWidget(botones)

    def agregar_pago(self):
        metodo = self.combo_metodo.currentText()
        monto_ingresado = self.input_monto.value()
        referencia = self.input_referencia.text().strip()

        if monto_ingresado <= 0:
            QMessageBox.warning(self, "Monto Inválido", "El monto debe ser mayor que 0.")
            return

        if 'Efectivo' not in metodo and not referencia:
            QMessageBox.warning(self, "Falta Referencia", f"Para pagos en {metodo}, la referencia es obligatoria.")
            return

        metodos_en_bolivares = ['Efectivo (Bs)', 'Pago Móvil', 'Punto de Venta']
        es_bolivares = metodo in metodos_en_bolivares
        if es_bolivares:
            if not self.tasa_bcv or self.tasa_bcv <= 0:
                QMessageBox.warning(self, "Tasa BCV Requerida", "No se puede convertir Bs a USD sin tasa BCV válida.")
                return
            monto_usd = monto_ingresado / self.tasa_bcv
        else:
            monto_usd = monto_ingresado

        pago = {
            'metodo': metodo,
            'monto': monto_ingresado,
            'monto_usd': monto_usd,
            'referencia': referencia
        }
        self.pagos.append(pago)

        if es_bolivares:
            base_texto = f"{metodo}: {monto_ingresado:,.2f} (~${monto_usd:.2f})"
        else:
            base_texto = f"{metodo}: ${monto_ingresado:.2f}"

        if referencia:
            texto = f"{base_texto} (Ref: {referencia})"
        else:
            texto = base_texto
        self.list_pagos.addItem(texto)

        self.total_acumulado = sum(p['monto_usd'] for p in self.pagos)
        self.lbl_total.setText(f"TOTAL ACUMULADO: ${self.total_acumulado:.2f}")

        self.input_monto.setValue(0.00)
        self.input_referencia.clear()

    def validar_y_aceptar(self):
        if not self.pagos:
            QMessageBox.warning(self, "Sin Pagos", "Debe agregar al menos un pago parcial.")
            return
        self.accept()

    def get_total(self):
        return self.total_acumulado

    def get_pagos(self):
        return self.pagos

    def get_detalle_texto(self):
        detalles = []
        for pago in self.pagos:
            ref_text = f"Ref:{pago['referencia']}" if pago['referencia'] else "SinRef"
            detalles.append(f"[{pago['metodo']} ${pago['monto']:.2f} {ref_text}]")
        return "MIXTO: " + " + ".join(detalles)


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
        self.setFixedSize(450, 730)
        
        self.id_cita = id_cita
        self.tasa_bcv = tasa_bcv
        self.controller = PagosController()
        
        self.monto_a_cobrar = 0.0
        self.pagos_mixtos = []
        self.detalle_pago_mixto = ""
        
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
            QLineEdit#monto_recibido {
                background-color: #34495E;
                color: #ECF0F1;
                border: 2px solid #3498DB;
                border-radius: 5px;
                padding: 8px;
                font-size: 16px;
                font-weight: bold;
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
        self.input_monto_recibido = QLineEdit()
        self.input_monto_recibido.setObjectName("monto_recibido")
        self.input_monto_recibido.setValidator(QDoubleValidator(0.0, 999999.99, 2, self))
        self.input_monto_recibido.setText("")
        self.input_monto_recibido.setPlaceholderText("0.00")
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
        self.combo_metodo.addItems(['Efectivo ($)', 'Efectivo (Bs)', 'Pago Móvil', 'Zelle', 'Punto de Venta', self.METODO_MIXTO_DISPLAY])
        self.combo_metodo.currentIndexChanged.connect(self.on_metodo_changed)
        layout.addWidget(self.combo_metodo)

        self.btn_desglose = QPushButton("📝 Configurar Desglose")
        self.btn_desglose.setMinimumHeight(38)
        self.btn_desglose.setStyleSheet(
            """
            QPushButton {
                background-color: #3498DB;
                color: white;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover { background-color: #2E86C1; }
            """
        )
        self.btn_desglose.clicked.connect(self.abrir_desglose_pago)
        self.btn_desglose.setVisible(False)
        layout.addWidget(self.btn_desglose)

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
        self.input_monto_recibido.textChanged.connect(self.calcular_vuelto)
        self.combo_moneda_recibida.currentIndexChanged.connect(self.calcular_vuelto)

    def on_metodo_changed(self):
        """Mostrar/ocultar botón de desglose y bloquear/desbloquear input de monto."""
        metodo = self.combo_metodo.currentText()

        if self.METODO_MIXTO in metodo:
            self.btn_desglose.setVisible(True)
            self.input_monto_recibido.setReadOnly(True)
            self.pagos_mixtos.clear()
            self.detalle_pago_mixto = ""
            self.input_monto_recibido.setText("")
        else:
            self.btn_desglose.setVisible(False)
            self.input_monto_recibido.setReadOnly(False)
            self.pagos_mixtos.clear()
            self.detalle_pago_mixto = ""

    def abrir_desglose_pago(self):
        dialog = DesglosePagoDialog(tasa_bcv=self.tasa_bcv, parent=self)
        if dialog.exec() == QDialog.Accepted:
            self.pagos_mixtos = dialog.get_pagos()
            self.detalle_pago_mixto = dialog.get_detalle_texto()
            total = dialog.get_total()
            self.input_monto_recibido.setText(f"{total:.2f}")
            self.calcular_vuelto()

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
            monto_recibido = float(self.input_monto_recibido.text() or 0)
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
        monto_recibido = float(self.input_monto_recibido.text() or 0)
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

            referencia = self.detalle_pago_mixto
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