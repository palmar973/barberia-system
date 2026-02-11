from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, 
    QLineEdit, QPushButton, QMessageBox, QFormLayout, QFrame, QDoubleSpinBox
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
        self.setFixedSize(450, 700)
        
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
            QDoubleSpinBox { 
                background-color: #ECF0F1; 
                color: #2C3E50; 
                border: 2px solid #3498DB; 
                border-radius: 5px; 
                padding: 8px;
                font-size: 16px;
                font-weight: bold;
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
            "background-color: #2b2b2b; border: 2px solid #FFA726; border-radius: 8px; padding: 10px;"
        )
        layout_calculadora = QVBoxLayout()
        frame_calculadora.setLayout(layout_calculadora)

        lbl_calc_titulo = QLabel("💰 Calculadora de Vuelto")
        lbl_calc_titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_calc_titulo.setFont(QFont("Arial", 12, QFont.Bold))
        lbl_calc_titulo.setStyleSheet("color: #FFA726; margin-bottom: 5px;")
        layout_calculadora.addWidget(lbl_calc_titulo)

        # Total a Pagar
        self.lbl_total_a_pagar = QLabel("Total a Pagar: $0.00 / Bs 0.00")
        self.lbl_total_a_pagar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_total_a_pagar.setStyleSheet("color: #ECF0F1; font-size: 13px; font-weight: bold;")
        layout_calculadora.addWidget(self.lbl_total_a_pagar)

        layout_calculadora.addSpacing(10)

        # Monto Recibido
        lbl_monto_recibido = QLabel("<b>Monto Recibido:</b>")
        layout_calculadora.addWidget(lbl_monto_recibido)
        self.input_monto_recibido = QDoubleSpinBox()
        self.input_monto_recibido.setMaximum(999999.99)
        self.input_monto_recibido.setMinimum(0.00)
        self.input_monto_recibido.setDecimals(2)
        self.input_monto_recibido.setValue(0.00)
        self.input_monto_recibido.setMinimumHeight(45)
        lbl_monto_recibido.setBuddy(self.input_monto_recibido)
        layout_calculadora.addWidget(self.input_monto_recibido)

        # Moneda Recibida
        lbl_moneda_recibida = QLabel("<b>Moneda Recibida:</b>")
        layout_calculadora.addWidget(lbl_moneda_recibida)
        self.combo_moneda_recibida = QComboBox()
        self.combo_moneda_recibida.addItems(['USD ($)', 'Bolívares (Bs)'])
        lbl_moneda_recibida.setBuddy(self.combo_moneda_recibida)
        layout_calculadora.addWidget(self.combo_moneda_recibida)

        layout_calculadora.addSpacing(10)

        # Vuelto / Restante (Resultado)
        self.lbl_vuelto_resultado = QLabel("VUELTO: $0.00 / Bs 0.00")
        self.lbl_vuelto_resultado.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_vuelto_resultado.setFont(QFont("Arial", 14, QFont.Bold))
        self.lbl_vuelto_resultado.setStyleSheet(
            "color: #2ECC71; background-color: #1F2A35; padding: 10px; border-radius: 5px;"
        )
        layout_calculadora.addWidget(self.lbl_vuelto_resultado)

        layout.addWidget(frame_calculadora)
        # ========== FIN CALCULADORA DE VUELTO ==========

        layout.addSpacing(15)

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