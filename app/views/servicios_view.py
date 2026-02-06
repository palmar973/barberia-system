from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QLineEdit, QMessageBox, QHeaderView, QFormLayout,
    QAbstractItemView
)
from PySide6.QtCore import Qt
from controllers.servicios_controller import ServiciosController

class FormularioServicio(QDialog):
    """
    Diálogo modal para Crear o Editar un servicio.
    """
    def __init__(self, parent=None, servicio_data=None):
        super().__init__(parent)
        self.setWindowTitle("Detalle de Servicio")
        self.setModal(True)
        self.setFixedSize(400, 300)
        self.datos_guardados = None

        layout = QFormLayout()

        self.input_nombre = QLineEdit()
        self.input_precio = QLineEdit()
        self.input_precio.setPlaceholderText("Ej: 15.00")
        self.input_duracion = QLineEdit()
        self.input_duracion.setPlaceholderText("Minutos (Ej: 30)")
        self.input_descripcion = QLineEdit()

        layout.addRow("Nombre:", self.input_nombre)
        layout.addRow("Precio ($):", self.input_precio)
        layout.addRow("Duración (min):", self.input_duracion)
        layout.addRow("Descripción:", self.input_descripcion)

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

        if servicio_data:
            self.input_nombre.setText(str(servicio_data[1]))
            self.input_precio.setText(str(servicio_data[2]))
            self.input_duracion.setText(str(servicio_data[3]))
            self.input_descripcion.setText(str(servicio_data[4]))

    def validar_y_guardar(self):
        nombre = self.input_nombre.text().strip()
        precio_txt = self.input_precio.text().strip()
        duracion_txt = self.input_duracion.text().strip()
        descripcion = self.input_descripcion.text().strip()

        if not nombre or not precio_txt or not duracion_txt:
            QMessageBox.warning(self, "Error", "Nombre, Precio y Duración son obligatorios.")
            return

        try:
            precio = float(precio_txt)
            duracion = int(duracion_txt)
        except ValueError:
            QMessageBox.warning(self, "Error", "Precio debe ser número y Duración un entero.")
            return

        self.datos_guardados = (nombre, precio, duracion, descripcion)
        self.accept()


class ServiciosView(QDialog):
    """
    Vista principal para la gestión (CRUD) de Servicios.
    Muestra una tabla y botones de acción.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Gestión de Servicios")
        self.resize(800, 600)
        self.controller = ServiciosController()
        
        self.layout_principal = QVBoxLayout()
        self.setLayout(self.layout_principal)

        self.tabla = QTableWidget()
        self.tabla.setColumnCount(5)
        self.tabla.setHorizontalHeaderLabels(["ID", "Nombre", "Precio ($)", "Duración (min)", "Descripción"])
        self.tabla.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tabla.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tabla.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.tabla.setColumnHidden(0, True)
        header = self.tabla.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        
        self.layout_principal.addWidget(self.tabla)

        self.layout_botones = QHBoxLayout()
        
        self.btn_crear = QPushButton("Nuevo Servicio")
        self.btn_editar = QPushButton("Editar Seleccionado")
        self.btn_eliminar = QPushButton("Eliminar Seleccionado")
        self.btn_cerrar = QPushButton("Cerrar")

        self.btn_crear.setStyleSheet("padding: 10px; font-weight: bold;")
        self.btn_editar.setStyleSheet("padding: 10px;")
        self.btn_eliminar.setStyleSheet("padding: 10px; color: red;")
        self.btn_cerrar.setStyleSheet("padding: 10px;")

        self.layout_botones.addWidget(self.btn_crear)
        self.layout_botones.addWidget(self.btn_editar)
        self.layout_botones.addWidget(self.btn_eliminar)
        self.layout_botones.addStretch()
        self.layout_botones.addWidget(self.btn_cerrar)

        self.layout_principal.addLayout(self.layout_botones)

        self.btn_crear.clicked.connect(self.abrir_crear)
        self.btn_editar.clicked.connect(self.abrir_editar)
        self.btn_eliminar.clicked.connect(self.eliminar_servicio)
        self.btn_cerrar.clicked.connect(self.accept)

        self.cargar_datos()

    def cargar_datos(self):
        """Consulta al controlador y rellena la tabla."""
        servicios = self.controller.listar_activos()
        self.tabla.setRowCount(0)

        for row_idx, servicio in enumerate(servicios):
            self.tabla.insertRow(row_idx)
            self.tabla.setItem(row_idx, 0, QTableWidgetItem(str(servicio[0])))
            self.tabla.setItem(row_idx, 1, QTableWidgetItem(str(servicio[1])))
            self.tabla.setItem(row_idx, 2, QTableWidgetItem(f"{servicio[2]:.2f}"))
            self.tabla.setItem(row_idx, 3, QTableWidgetItem(str(servicio[3])))
            self.tabla.setItem(row_idx, 4, QTableWidgetItem(str(servicio[4] or "")))

    def abrir_crear(self):
        dialogo = FormularioServicio(self)
        if dialogo.exec():
            datos = dialogo.datos_guardados
            exito = self.controller.crear_servicio(*datos)
            if exito:
                QMessageBox.information(self, "Éxito", "Servicio creado correctamente.")
                self.cargar_datos()
            else:
                QMessageBox.critical(self, "Error", "No se pudo guardar el servicio.")

    def abrir_editar(self):
        seleccion = self.tabla.selectedItems()
        if not seleccion:
            QMessageBox.warning(self, "Aviso", "Seleccione un servicio para editar.")
            return

        fila = seleccion[0].row()
        id_servicio = int(self.tabla.item(fila, 0).text())
        nombre = self.tabla.item(fila, 1).text()
        precio = float(self.tabla.item(fila, 2).text())
        duracion = int(self.tabla.item(fila, 3).text())
        descripcion = self.tabla.item(fila, 4).text()

        datos_actuales = (id_servicio, nombre, precio, duracion, descripcion)

        dialogo = FormularioServicio(self, servicio_data=datos_actuales)
        if dialogo.exec():
            nuevos_datos = dialogo.datos_guardados
            exito = self.controller.editar_servicio(id_servicio, *nuevos_datos)
            if exito:
                QMessageBox.information(self, "Éxito", "Servicio actualizado correctamente.")
                self.cargar_datos()
            else:
                QMessageBox.critical(self, "Error", "No se pudo actualizar el servicio.")

    def eliminar_servicio(self):
        seleccion = self.tabla.selectedItems()
        if not seleccion:
            QMessageBox.warning(self, "Aviso", "Seleccione un servicio para eliminar.")
            return

        fila = seleccion[0].row()
        id_servicio = int(self.tabla.item(fila, 0).text())
        nombre = self.tabla.item(fila, 1).text()

        confirmacion = QMessageBox.question(
            self, "Confirmar Eliminación",
            f"¿Estás seguro de eliminar el servicio '{nombre}'?",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirmacion == QMessageBox.Yes:
            exito = self.controller.eliminar_servicio(id_servicio)
            if exito:
                QMessageBox.information(self, "Eliminado", "Servicio eliminado correctamente.")
                self.cargar_datos()
            else:
                QMessageBox.critical(self, "Error", "No se pudo eliminar el servicio.")