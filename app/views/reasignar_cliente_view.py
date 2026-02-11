from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QGridLayout,
    QLabel,
    QMessageBox,
)
from PySide6.QtCore import Qt

from controllers.citas_controller import CitasController
from controllers.clientes_controller import ClientesController


class ReasignarClienteView(QDialog):
    def __init__(self, id_cita, parent=None):
        super().__init__(parent)
        self.id_cita = id_cita
        self.setWindowTitle("Vincular a Cliente Registrado")
        self.setModal(True)

        self.citas_controller = CitasController()
        self.clientes_controller = ClientesController()

        self._setup_ui()
        self._cargar_clientes()

    def _setup_ui(self):
        layout = QGridLayout(self)

        titulo = QLabel("Selecciona el cliente registrado")
        titulo.setStyleSheet("color: #e0e0e0; font-size: 16px; font-weight: 600;")
        layout.addWidget(titulo, 0, 0, 1, 2)

        self.clientes_combo = QComboBox()
        self.clientes_combo.setEditable(True)
        self.clientes_combo.setStyleSheet(
            """
            QComboBox { background-color: #2d2d2d; color: #e0e0e0; padding: 6px; }
            QComboBox QAbstractItemView { background-color: #1e1e1e; color: #e0e0e0; }
            """
        )
        layout.addWidget(self.clientes_combo, 1, 0, 1, 2)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._confirmar)
        buttons.rejected.connect(self.reject)
        buttons.setStyleSheet(
            """
            QDialogButtonBox QPushButton { background-color: #3a3f44; color: #e0e0e0; padding: 6px 12px; }
            QDialogButtonBox QPushButton:hover { background-color: #4a525a; }
            """
        )
        layout.addWidget(buttons, 2, 0, 1, 2, alignment=Qt.AlignRight)

        self.setStyleSheet("background-color: #1e1e1e;")
        self.resize(380, 140)

    def _cargar_clientes(self):
        # Usa el listado general del controller de clientes
        clientes = self.clientes_controller.listar_todos()
        for cliente in clientes:
            if cliente[1] == "Público General":
                continue
            # Guarda el id en item data para recuperar fácil
            self.clientes_combo.addItem(cliente[1], cliente[0])
        if self.clientes_combo.count():
            self.clientes_combo.setCurrentIndex(0)

    def _confirmar(self):
        if self.clientes_combo.currentIndex() < 0:
            QMessageBox.warning(self, "Aviso", "Selecciona un cliente.")
            return

        nuevo_id = self.clientes_combo.currentData()
        ok, msg = self.citas_controller.reasignar_cliente(self.id_cita, nuevo_id)
        if ok:
            QMessageBox.information(self, "Éxito", msg)
            self.accept()
        else:
            QMessageBox.warning(self, "Aviso", msg)