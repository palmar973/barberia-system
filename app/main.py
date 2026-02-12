import sys
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox  # <-- ¡Añadidos estos dos!
from database import DatabaseManager
from views.main_view import MainView

def main():
    """Arranca la app, valida la BD y abre el dashboard."""
    app = QApplication(sys.argv)

    db_manager = DatabaseManager()
    if not db_manager.inicializar_db():
        error_box = QMessageBox()
        error_box.setIcon(QMessageBox.Icon.Critical) # En Qt6 es .Icon.Critical
        error_box.setWindowTitle("Error de Sistema")
        error_box.setText("No se pudo inicializar la base de datos.")
        error_box.setInformativeText("Verifique los permisos de escritura.")
        error_box.exec()
        sys.exit(1)

    ventana_principal = MainView()
    ventana_principal.showMaximized()

    sys.exit(app.exec()) # En Qt6 es .exec() sin guion bajo

if __name__ == "__main__":
    main()