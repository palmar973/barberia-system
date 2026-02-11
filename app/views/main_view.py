from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QLabel, QDateEdit, QTableWidget, QTableWidgetItem, QHeaderView, 
    QAbstractItemView, QFrame, QMessageBox, QMenu
)
# NOTA: QAction se movió a QtGui en PySide6
from PySide6.QtGui import QColor, QFont, QAction
from PySide6.QtCore import Qt, QDate

from controllers.citas_controller import CitasController
from controllers.bcv_controller import BCVWorker
from views.servicios_view import ServiciosView
from views.clientes_view import ClientesView
from views.agendar_view import AgendarCitaView
from views.pago_view import PagoView
from views.cierre_caja_view import CierreCajaView
from views.cita_express_view import CitaExpressView
from views.reasignar_cliente_view import ReasignarClienteView
from views.reporte_comisiones_view import ReporteComisionesView
from views.dashboard_view import DashboardView

class MainView(QMainWindow):
    """Dashboard Principal Multi-Barbero con Tasa BCV."""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Barbería System - Dashboard")
        self.setGeometry(100, 100, 1200, 800)
        
        self.controller = CitasController()
        self.tasa_bcv_actual = 0.0
        
        self.init_ui()
        self.cargar_citas_del_dia()
        self.iniciar_scraping_bcv()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        central_widget.setLayout(main_layout)

        sidebar = QFrame()
        sidebar.setStyleSheet("background-color: #2C3E50; color: white;")
        sidebar.setFixedWidth(250)
        sidebar_layout = QVBoxLayout()
        sidebar.setLayout(sidebar_layout)
        
        lbl_titulo = QLabel("BARBERÍA\nSYSTEM")
        lbl_titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_titulo.setFont(QFont("Arial", 16, QFont.Bold))
        lbl_titulo.setStyleSheet("padding: 20px 0 10px 0; color: #ECF0F1;")
        sidebar_layout.addWidget(lbl_titulo)
        
        self.lbl_tasa = QLabel("BCV: Cargando...")
        self.lbl_tasa.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_tasa.setFont(QFont("Arial", 11, QFont.Bold))
        self.lbl_tasa.setStyleSheet("color: #F1C40F; margin-bottom: 20px;")
        sidebar_layout.addWidget(self.lbl_tasa)
        
        btn_dashboard = self.crear_boton_menu("📈 Dashboard", "#9B59B6")
        btn_dashboard.clicked.connect(self.mostrar_dashboard)
        btn_express = self.crear_boton_menu("⚡ Atención Inmediata", "#D35400")
        btn_express.clicked.connect(self.abrir_cita_express)
        btn_nueva_cita = self.crear_boton_menu("📅 Agendar Cita", "#27AE60")
        btn_nueva_cita.clicked.connect(self.abrir_nueva_cita)
        btn_agenda = self.crear_boton_menu("📋 Agenda", "#34495E")
        btn_agenda.clicked.connect(self.mostrar_agenda)
        btn_clientes = self.crear_boton_menu("👥 Clientes", "#34495E")
        btn_clientes.clicked.connect(self.abrir_clientes)
        btn_servicios = self.crear_boton_menu("✂️ Servicios", "#34495E")
        btn_servicios.clicked.connect(self.abrir_servicios)
        btn_caja = self.crear_boton_menu("💰 Cierre de Caja", "#34495E")
        btn_caja.clicked.connect(self.abrir_cierre_caja)
        btn_comisiones = self.crear_boton_menu("📊 Comisiones", "#34495E")
        btn_comisiones.clicked.connect(self.abrir_comisiones)
        
        sidebar_layout.addWidget(btn_dashboard)
        sidebar_layout.addSpacing(10)
        sidebar_layout.addWidget(btn_express)
        sidebar_layout.addSpacing(10)
        sidebar_layout.addWidget(btn_nueva_cita)
        sidebar_layout.addWidget(btn_agenda)
        sidebar_layout.addWidget(btn_clientes)
        sidebar_layout.addWidget(btn_servicios)
        sidebar_layout.addWidget(btn_caja)
        sidebar_layout.addWidget(btn_comisiones)
        sidebar_layout.addStretch() 

        main_layout.addWidget(sidebar)

        # Content area: inicialmente mostrará la Agenda
        self.content_area = QWidget()
        self.content_layout = QVBoxLayout()
        self.content_area.setLayout(self.content_layout)
        self.content_layout.setContentsMargins(20, 20, 20, 20)
        
        main_layout.addWidget(self.content_area)
        
        # Crear vista de agenda
        self.crear_vista_agenda()


    def crear_vista_agenda(self):
        """Crea la vista de agenda diaria."""
        # Limpiar el content_layout
        self.limpiar_content_area()
        
        header_layout = QHBoxLayout()
        lbl_agenda = QLabel("Agenda Diaria")
        lbl_agenda.setFont(QFont("Arial", 18, QFont.Bold))
        
        self.date_selector = QDateEdit()
        self.date_selector.setCalendarPopup(True)
        self.date_selector.setDate(QDate.currentDate())
        self.date_selector.setDisplayFormat("dd/MM/yyyy")
        self.date_selector.setFixedWidth(150)
        self.date_selector.setStyleSheet("font-size: 14px; padding: 5px;")
        self.date_selector.dateChanged.connect(self.cargar_citas_del_dia)
        
        header_layout.addWidget(lbl_agenda)
        header_layout.addStretch()
        header_layout.addWidget(QLabel("Fecha:"))
        header_layout.addWidget(self.date_selector)
        self.content_layout.addLayout(header_layout)
        
        self.tabla_citas = QTableWidget()
        self.tabla_citas.setColumnCount(7)
        self.tabla_citas.setHorizontalHeaderLabels([
            "Inicio", "Fin", "Barbero", "Cliente", "Servicio", "Precio ($)", "Estado"
        ])
        self.tabla_citas.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tabla_citas.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tabla_citas.verticalHeader().setVisible(False)
        self.tabla_citas.setAlternatingRowColors(True)
        
        self.tabla_citas.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tabla_citas.customContextMenuRequested.connect(self.mostrar_menu_contextual)
        self.tabla_citas.cellDoubleClicked.connect(self.abrir_cobro)
        
        header = self.tabla_citas.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.content_layout.addWidget(self.tabla_citas)
        
        lbl_info = QLabel("ℹ️ Doble clic para COBRAR | Click derecho para CANCELAR.")
        lbl_info.setStyleSheet("color: #666; font-style: italic;")
        self.content_layout.addWidget(lbl_info)
    
    def limpiar_content_area(self):
        """Limpia el área de contenido."""
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self.limpiar_layout(item.layout())
    
    def limpiar_layout(self, layout):
        """Limpia un layout recursivamente."""
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self.limpiar_layout(item.layout())
    
    def mostrar_dashboard(self):
        """Muestra el dashboard de BI."""
        self.limpiar_content_area()
        self.dashboard_view = DashboardView(self)
        self.content_layout.addWidget(self.dashboard_view)
    
    def mostrar_agenda(self):
        """Muestra la vista de agenda."""
        self.crear_vista_agenda()
        self.cargar_citas_del_dia()

    def crear_boton_menu(self, texto, color_base):
        btn = QPushButton(texto)
        btn.setFixedHeight(50)
        btn.setStyleSheet(f"""
            QPushButton {{ background-color: {color_base}; color: white; border: none; font-size: 14px; text-align: left; padding-left: 20px; font-weight: bold; }}
            QPushButton:hover {{ background-color: #1ABC9C; }}
        """)
        return btn

    def iniciar_scraping_bcv(self):
        """Inicia el hilo para buscar el precio del dólar."""
        self.worker_bcv = BCVWorker()
        self.worker_bcv.precio_actualizado.connect(self.actualizar_tasa_ui)
        self.worker_bcv.error_ocurrido.connect(self.manejar_error_bcv)
        self.worker_bcv.start()

    def actualizar_tasa_ui(self, precio):
        """Se ejecuta cuando el hilo termina con éxito."""
        self.tasa_bcv_actual = precio
        self.lbl_tasa.setText(f"BCV: {precio:.2f} Bs/$")

    def manejar_error_bcv(self, mensaje):
        """Se ejecuta si el hilo falla."""
        self.lbl_tasa.setText("BCV: Error")
        print(f"Error scraping BCV: {mensaje}")

    def cargar_citas_del_dia(self):
        fecha_str = self.date_selector.date().toString("yyyy-MM-dd")
        citas = self.controller.obtener_citas_por_fecha(fecha_str)
        self.tabla_citas.setRowCount(0)
        for row_idx, cita in enumerate(citas):
            id_cita = cita[0]
            self.tabla_citas.insertRow(row_idx)
            item_inicio = QTableWidgetItem(cita[1])
            item_inicio.setData(Qt.ItemDataRole.UserRole, id_cita)
            self.tabla_citas.setItem(row_idx, 0, item_inicio)
            self.tabla_citas.setItem(row_idx, 1, QTableWidgetItem(cita[2]))
            item_barbero = QTableWidgetItem(f"✂️ {cita[3]}")
            item_barbero.setFont(QFont("Arial", 10, QFont.Bold))
            self.tabla_citas.setItem(row_idx, 2, item_barbero)
            self.tabla_citas.setItem(row_idx, 3, QTableWidgetItem(cita[4]))
            self.tabla_citas.setItem(row_idx, 4, QTableWidgetItem(cita[5]))
            precio_item = QTableWidgetItem(f"${cita[6]:.2f}")
            precio_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.tabla_citas.setItem(row_idx, 5, precio_item)
            estado = cita[7]
            item_estado = QTableWidgetItem(estado)
            item_estado.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            if estado == 'Pendiente': item_estado.setForeground(QColor('#FF8C00'))
            elif estado == 'Pagada': item_estado.setForeground(QColor('green'))
            elif estado == 'Cancelada': item_estado.setForeground(QColor('red'))
            font = item_estado.font()
            font.setBold(True)
            item_estado.setFont(font)
            self.tabla_citas.setItem(row_idx, 6, item_estado)

    def mostrar_menu_contextual(self, pos):
        index = self.tabla_citas.indexAt(pos)
        if not index.isValid(): return
        fila = index.row()
        self.tabla_citas.setCurrentCell(fila, index.column())
        item_inicio = self.tabla_citas.item(fila, 0)
        id_cita = item_inicio.data(Qt.ItemDataRole.UserRole)
        cliente = self.tabla_citas.item(fila, 3).text()
        estado = self.tabla_citas.item(fila, 6).text()
        menu = QMenu()

        if cliente == "Público General":
            accion_reasignar = QAction("👤 Vincular a Cliente Registrado", self)
            accion_reasignar.triggered.connect(lambda: self._abrir_reasignar_cliente(id_cita))
            menu.addAction(accion_reasignar)

        accion_cancelar = QAction("🚫 Cancelar Cita", self)
        accion_cancelar.triggered.connect(self.cancelar_cita_seleccionada)
        if estado not in ['Pagada', 'Cancelada']:
            menu.addAction(accion_cancelar)
        menu.exec(self.tabla_citas.mapToGlobal(pos))

    def _abrir_reasignar_cliente(self, id_cita):
        dialogo = ReasignarClienteView(id_cita, self)
        if dialogo.exec():
            self.cargar_citas_del_dia()

    def cancelar_cita_seleccionada(self):
        fila = self.tabla_citas.currentRow()
        if fila < 0: return
        item_inicio = self.tabla_citas.item(fila, 0)
        # CORRECCIÓN: Usar Qt.ItemDataRole.UserRole para consistencia
        id_cita = item_inicio.data(Qt.ItemDataRole.UserRole)
        cliente = self.tabla_citas.item(fila, 3).text()
        confirmacion = QMessageBox.question(self, "Confirmar Cancelación", f"¿Está seguro de CANCELAR la cita de {cliente}?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if confirmacion == QMessageBox.StandardButton.Yes:
            exito, mensaje = self.controller.cancelar_cita(id_cita)
            if exito: self.cargar_citas_del_dia()

    def abrir_cobro(self, row, col):
        item_inicio = self.tabla_citas.item(row, 0)
        id_cita = item_inicio.data(Qt.ItemDataRole.UserRole)
        item_estado = self.tabla_citas.item(row, 6)
        if item_estado.text() in ['Pagada', 'Cancelada']: return
        
        # Pasamos la tasa BCV vigente al modal de pago
        ventana_pago = PagoView(id_cita, tasa_bcv=self.tasa_bcv_actual, parent=self)
        ventana_pago.exec()
        self.cargar_citas_del_dia()

    def abrir_cita_express(self):
        dialogo = CitaExpressView(self)
        dialogo.exec()
        self.cargar_citas_del_dia()

    def abrir_nueva_cita(self):
        dialogo = AgendarCitaView(self)
        dialogo.exec() 
        self.cargar_citas_del_dia()

    def abrir_clientes(self):
        view = ClientesView(self)
        view.exec()

    def abrir_servicios(self):
        view = ServiciosView(self)
        view.exec()
    
    def abrir_cierre_caja(self):
        view = CierreCajaView(self)
        view.exec()
    
    def abrir_comisiones(self):
        view = ReporteComisionesView(self)
        view.exec()