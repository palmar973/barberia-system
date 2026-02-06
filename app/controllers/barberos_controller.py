import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database import DatabaseManager

class BarberosController:
    """Consultas de barberos para asignar citas."""

    def __init__(self):
        self.db = DatabaseManager()

    def obtener_barberos_activos(self):
        """Barberos activos ordenados para usar en combos."""
        conn = self.db.get_connection()
        if not conn: return []
        
        try:
            cursor = conn.cursor()
            query = "SELECT id_barbero, nombre FROM barberos WHERE activo = 1 ORDER BY nombre ASC"
            cursor.execute(query)
            return cursor.fetchall()
        except Exception as e:
            print(f"Error al obtener barberos: {e}")
            return []
        finally:
            conn.close()