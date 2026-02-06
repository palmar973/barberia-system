import sys
import os

# Ajuste de path para importar database correctamente
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database import DatabaseManager

class ClientesController:
    """CRUD de clientes, búsqueda y su historial."""

    def __init__(self):
        self.db = DatabaseManager()

    def listar_todos(self):
        """Obtiene todos los clientes ordenados por nombre."""
        conn = self.db.get_connection()
        if not conn: return []
        
        try:
            cursor = conn.cursor()
            query = "SELECT id_cliente, nombre, telefono, email FROM clientes ORDER BY nombre ASC"
            cursor.execute(query)
            return cursor.fetchall()
        except Exception as e:
            print(f"Error al listar clientes: {e}")
            return []
        finally:
            conn.close()

    def buscar_clientes(self, texto):
        """Busca clientes cuyo nombre O teléfono contengan el texto proporcionado."""
        conn = self.db.get_connection()
        if not conn: return []

        try:
            cursor = conn.cursor()
            texto_busqueda = f"%{texto}%"
            query = """
                SELECT id_cliente, nombre, telefono, email 
                FROM clientes 
                WHERE nombre LIKE ? OR telefono LIKE ?
                ORDER BY nombre ASC
            """
            cursor.execute(query, (texto_busqueda, texto_busqueda))
            return cursor.fetchall()
        except Exception as e:
            print(f"Error al buscar clientes: {e}")
            return []
        finally:
            conn.close()

    def crear_cliente(self, nombre, telefono, email=None):
        """Inserta un nuevo cliente."""
        conn = self.db.get_connection()
        if not conn: return False

        try:
            cursor = conn.cursor()
            query = "INSERT INTO clientes (nombre, telefono, email) VALUES (?, ?, ?)"
            cursor.execute(query, (nombre, telefono, email))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error al crear cliente: {e}")
            return False
        finally:
            conn.close()

    def editar_cliente(self, id_cliente, nombre, telefono, email=None):
        """Actualiza los datos de un cliente existente."""
        conn = self.db.get_connection()
        if not conn: return False

        try:
            cursor = conn.cursor()
            query = """
                UPDATE clientes 
                SET nombre = ?, telefono = ?, email = ?
                WHERE id_cliente = ?
            """
            cursor.execute(query, (nombre, telefono, email, id_cliente))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error al editar cliente: {e}")
            return False
        finally:
            conn.close()

    def obtener_historial_cliente(self, id_cliente):
        """Historial de citas no canceladas con servicios y barberos."""
        conn = self.db.get_connection()
        if not conn: return []

        try:
            cursor = conn.cursor()
            query = """
                SELECT 
                    c.fecha, 
                    c.hora_inicio, 
                    s.nombre AS servicio, 
                    b.nombre AS barbero, 
                    c.total_estimado, 
                    c.estado
                FROM citas c
                JOIN servicios s ON c.id_servicio = s.id_servicio
                JOIN barberos b ON c.id_barbero = b.id_barbero
                WHERE c.id_cliente = ? 
                  AND c.estado != 'Cancelada'
                ORDER BY c.fecha DESC, c.hora_inicio DESC;
            """
            cursor.execute(query, (id_cliente,))
            return cursor.fetchall()
        except Exception as e:
            print(f"Error al obtener historial del cliente: {e}")
            return []
        finally:
            conn.close()