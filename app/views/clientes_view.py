from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QLineEdit, QMessageBox, QHeaderView, QFormLayout,
    QAbstractItemView
)
from PySide6.QtCore import Qt, QRegularExpression
from PySide6.QtGui import QRegularExpressionValidator
from controllers.clientes_controller import ClientesController
from views.historial_cliente_view import HistorialClienteView

class FormularioCliente(QDialog):
    """
    Diálogo modal para Crear o Editar un cliente.
    """
    def __init__(self, parent=None, cliente_data=None):
        super().__init__(parent)
        self.setWindowTitle("Datos del Cliente")
        self.setModal(True)
        self.setFixedSize(400, 250)
        self.datos_guardados = None 

        layout = QFormLayout()

        self.input_nombre = QLineEdit()
        self.input_telefono = QLineEdit()
        self.input_email = QLineEdit()

        reg_ex = QRegularExpression("^[0-9\\-\\s]+$")
        validator = QRegularExpressionValidator(reg_ex, self.input_telefono)
        self.input_telefono.setValidator(validator)
        self.input_telefono.setPlaceholderText("Ej: 0414-1234567")

        layout.addRow("Nombre Completo *:", self.input_nombre)
        layout.addRow("Teléfono *:", self.input_telefono)
        layout.addRow("Email:", self.input_email)

        btn_box = QHBoxLayout()
        self.btn_guardar = QPushButton("Guardar")
        self.btn_cancelar = QPushButton("Cancelar")
        
        self.btn_guardar.setStyleSheet("background-color: #4CAF50; color: white; padding: 5px;")
        self.btn_cancelar.setStyleSheet("background-color: #f44336; color: white; padding: 5px;")

        btn_box.addWidget(self.btn_guardar)
        btn_box.addWidget(self.btn_cancelar)
        layout.addRow(btn_box)

        self.setLayout(layout)

        self.btn_guardar.clicked.connect(self.validar_y_guardar)
        self.btn_cancelar.clicked.connect(self.reject)

        if cliente_data:
            self.input_nombre.setText(str(cliente_data[1]))
            self.input_telefono.setText(str(cliente_data[2] or ""))
            self.input_email.setText(str(cliente_data[3] or ""))

    def validar_y_guardar(self):
        nombre = self.input_nombre.text().strip()
        telefono = self.input_telefono.text().strip()
        email = self.input_email.text().strip()

        if not nombre or not telefono:
            QMessageBox.warning(self, "Error", "El Nombre y el Teléfono son obligatorios.")
            return

        self.datos_guardados = (nombre, telefono, email)
        self.accept()


class ClientesView(QDialog):
    """
    Vista principal para la gestión de Clientes.
    Ahora incluye la opción de ver el Historial de Servicios.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Gestión de Clientes")
        self.resize(950, 600)
        self.controller = ClientesController()
        
        self.layout_principal = QVBoxLayout()
        self.setLayout(self.layout_principal)

        self.layout_busqueda = QHBoxLayout()
        lbl_buscar = QLabel("Buscar:")
        self.input_buscar = QLineEdit()
        self.input_buscar.setPlaceholderText("Escriba nombre o teléfono...")
        self.input_buscar.textChanged.connect(self.cargar_datos)
        
        self.layout_busqueda.addWidget(lbl_buscar)
        self.layout_busqueda.addWidget(self.input_buscar)
        self.layout_principal.addLayout(self.layout_busqueda)

        self.tabla = QTableWidget()
        self.tabla.setColumnCount(4)
        self.tabla.setHorizontalHeaderLabels(["ID", "Nombre", "Teléfono", "Email"])
        self.tabla.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tabla.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tabla.setEditTriggers(QAbstractItemView.NoEditTriggers)
        
        self.tabla.setColumnHidden(0, True)
        
        header = self.tabla.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        
        self.layout_principal.addWidget(self.tabla)

        self.layout_botones = QHBoxLayout()
        
        self.btn_crear = QPushButton("Nuevo Cliente")
        self.btn_editar = QPushButton("Editar Cliente")
        self.btn_historial = QPushButton("Ver Historial")
        self.btn_cerrar = QPushButton("Cerrar")

        self.btn_crear.setStyleSheet("padding: 10px; font-weight: bold;")
        self.btn_editar.setStyleSheet("padding: 10px;")
        self.btn_historial.setStyleSheet("padding: 10px; background-color: #17a2b8; color: white; font-weight: bold;")
        self.btn_cerrar.setStyleSheet("padding: 10px;")

        self.layout_botones.addWidget(self.btn_crear)
        self.layout_botones.addWidget(self.btn_editar)
        self.layout_botones.addWidget(self.btn_historial)
        self.layout_botones.addStretch()
        self.layout_botones.addWidget(self.btn_cerrar)

        self.layout_principal.addLayout(self.layout_botones)

        self.btn_crear.clicked.connect(self.abrir_crear)
        self.btn_editar.clicked.connect(self.abrir_editar)
        self.btn_historial.clicked.connect(self.abrir_historial)
        self.btn_cerrar.clicked.connect(self.accept)

        self.cargar_datos()

    def cargar_datos(self):
        texto = self.input_buscar.text().strip()
        if texto:
            clientes = self.controller.buscar_clientes(texto)
        else:
            clientes = self.controller.listar_todos()

        self.tabla.setRowCount(0)

        for row_idx, cliente in enumerate(clientes):
            self.tabla.insertRow(row_idx)
            self.tabla.setItem(row_idx, 0, QTableWidgetItem(str(cliente[0])))
            self.tabla.setItem(row_idx, 1, QTableWidgetItem(str(cliente[1])))
            self.tabla.setItem(row_idx, 2, QTableWidgetItem(str(cliente[2] or "")))
            self.tabla.setItem(row_idx, 3, QTableWidgetItem(str(cliente[3] or "")))

    def abrir_historial(self):
        """Abre la ventana del historial, bloqueando al Público General."""
        seleccion = self.tabla.selectedItems()
        if not seleccion:
            QMessageBox.warning(self, "Aviso", "Seleccione un cliente para ver su historial.")
            return

        fila = seleccion[0].row()
        id_cliente = int(self.tabla.item(fila, 0).text())
        nombre_cliente = self.tabla.item(fila, 1).text()

        # Bloqueamos al público general: es un placeholder sin historial
        if nombre_cliente == "Público General":
            QMessageBox.information(
                self, "Historial no disponible",
                "El cliente 'Público General' se utiliza para atenciones rápidas anónimas y no genera historial unificado."
            )
            return

        ventana_historial = HistorialClienteView(id_cliente, nombre_cliente, self)
        ventana_historial.exec()

    def abrir_crear(self):
        dialogo = FormularioCliente(self)
        if dialogo.exec():
            datos = dialogo.datos_guardados
            exito = self.controller.crear_cliente(*datos)
            if exito:
                QMessageBox.information(self, "Éxito", "Cliente registrado correctamente.")
                self.input_buscar.clear()
                self.cargar_datos()
            else:
                QMessageBox.critical(self, "Error", "No se pudo registrar el cliente.")

    def abrir_editar(self):
        seleccion = self.tabla.selectedItems()
        if not seleccion:
            QMessageBox.warning(self, "Aviso", "Seleccione un cliente para editar.")
            return

        fila = seleccion[0].row()
        id_cliente = int(self.tabla.item(fila, 0).text())
        nombre = self.tabla.item(fila, 1).text()
        
        # No tocar los datos del Público General
        if nombre == "Público General":
            QMessageBox.warning(self, "Acción no permitida", "No se pueden editar los datos del Público General.")
            return

        telefono = self.tabla.item(fila, 2).text()
        email = self.tabla.item(fila, 3).text()

        datos_actuales = (id_cliente, nombre, telefono, email)

        dialogo = FormularioCliente(self, cliente_data=datos_actuales)
        if dialogo.exec():
            nuevos_datos = dialogo.datos_guardados
            exito = self.controller.editar_cliente(id_cliente, *nuevos_datos)
            if exito:
                QMessageBox.information(self, "Éxito", "Cliente actualizado correctamente.")
                self.cargar_datos()
            else:
                QMessageBox.critical(self, "Error", "No se pudo actualizar el cliente.")