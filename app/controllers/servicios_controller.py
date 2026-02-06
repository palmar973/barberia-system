import sys
import os

# Ajuste de path para poder importar database correctamente
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database import DatabaseManager

class ServiciosController:
    """CRUD de servicios con soft delete."""

    def __init__(self):
        self.db = DatabaseManager()

    def listar_activos(self):
        """Servicios activos (activo=1) o lista vacía si falla."""
        conn = self.db.get_connection()
        if not conn:
            return []
        
        try:
            cursor = conn.cursor()
            query = """
                SELECT id_servicio, nombre, precio, duracion_minutos, descripcion 
                FROM servicios 
                WHERE activo = 1 
                ORDER BY nombre ASC
            """
            cursor.execute(query)
            resultados = cursor.fetchall()
            return resultados
        except Exception as e:
            print(f"Error al listar servicios: {e}")
            return []
        finally:
            conn.close()

    def crear_servicio(self, nombre, precio, duracion, descripcion=""):
        """Crea servicio; retorna True/False."""
        conn = self.db.get_connection()
        if not conn:
            return False

        try:
            cursor = conn.cursor()
            query = """
                INSERT INTO servicios (nombre, precio, duracion_minutos, descripcion, activo)
                VALUES (?, ?, ?, ?, 1)
            """
            cursor.execute(query, (nombre, precio, duracion, descripcion))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error al crear servicio: {e}")
            return False
        finally:
            conn.close()

    def editar_servicio(self, id_servicio, nombre, precio, duracion, descripcion=""):
        """Actualiza un servicio existente."""
        conn = self.db.get_connection()
        if not conn:
            return False

        try:
            cursor = conn.cursor()
            query = """
                UPDATE servicios 
                SET nombre = ?, precio = ?, duracion_minutos = ?, descripcion = ?
                WHERE id_servicio = ?
            """
            cursor.execute(query, (nombre, precio, duracion, descripcion, id_servicio))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error al editar servicio: {e}")
            return False
        finally:
            conn.close()

    def eliminar_servicio(self, id_servicio):
        """Soft delete: pone activo=0."""
        conn = self.db.get_connection()
        if not conn:
            return False

        try:
            cursor = conn.cursor()
            query = "UPDATE servicios SET activo = 0 WHERE id_servicio = ?"
            cursor.execute(query, (id_servicio,))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error al eliminar servicio: {e}")
            return False
        finally:
            conn.close()