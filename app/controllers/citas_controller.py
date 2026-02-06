import sys
import os
from datetime import datetime, timedelta

# Ajuste de path para importar database correctamente
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database import DatabaseManager

class CitasController:
    """Gestiona citas con soporte multi-barbero."""

    def __init__(self):
        self.db = DatabaseManager()

    def obtener_clientes(self):
        conn = self.db.get_connection()
        if not conn: return []
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id_cliente, nombre FROM clientes ORDER BY nombre ASC")
            return cursor.fetchall()
        finally:
            conn.close()

    def obtener_servicios_activos(self):
        conn = self.db.get_connection()
        if not conn: return []
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id_servicio, nombre, precio, duracion_minutos FROM servicios WHERE activo = 1 ORDER BY nombre ASC")
            return cursor.fetchall()
        finally:
            conn.close()

    def get_hora_actual_formateada(self):
        return datetime.now().strftime("%H:%M")

    def calcular_hora_fin(self, hora_inicio_str, duracion_minutos):
        try:
            formato = "%H:%M"
            inicio_dt = datetime.strptime(hora_inicio_str, formato)
            fin_dt = inicio_dt + timedelta(minutes=int(duracion_minutos))
            return fin_dt.strftime(formato)
        except Exception:
            return hora_inicio_str

    def hay_solapamiento(self, fecha_str, hora_inicio, hora_fin, id_barbero):
        """Valida solapes solo contra el mismo barbero; otros pueden seguir."""
        conn = self.db.get_connection()
        if not conn: return True

        try:
            cursor = conn.cursor()
            query = """
                SELECT hora_inicio, hora_fin 
                FROM citas 
                WHERE fecha = ? 
                  AND id_barbero = ? 
                  AND estado != 'Cancelada'
            """
            cursor.execute(query, (fecha_str, id_barbero))
            citas_existentes = cursor.fetchall()

            for inicio_existente, fin_existente in citas_existentes:
                if (hora_inicio < fin_existente) and (hora_fin > inicio_existente):
                    return True  # Conflicto para este barbero
            return False
        except Exception as e:
            print(f"Error verificando solapamiento: {e}")
            return True
        finally:
            conn.close()

    def obtener_o_crear_cliente_publico(self):
        conn = self.db.get_connection()
        if not conn: return None
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id_cliente FROM clientes WHERE nombre = 'Público General'")
            resultado = cursor.fetchone()
            if resultado: return resultado[0]
            
            cursor.execute("INSERT INTO clientes (nombre) VALUES ('Público General')")
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()

    def crear_cita(self, id_cliente, id_servicio, id_barbero, fecha, hora_inicio, hora_fin, total, notas=""):
        """Inserta nueva cita asociándola a un barbero."""
        conn = self.db.get_connection()
        if not conn: return False

        try:
            cursor = conn.cursor()
            query = """
                INSERT INTO citas (id_cliente, id_servicio, id_barbero, fecha, hora_inicio, hora_fin, total_estimado, estado, notas)
                VALUES (?, ?, ?, ?, ?, ?, ?, 'Pendiente', ?)
            """
            cursor.execute(query, (id_cliente, id_servicio, id_barbero, fecha, hora_inicio, hora_fin, total, notas))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error creando cita: {e}")
            return False
        finally:
            conn.close()

    def obtener_citas_por_fecha(self, fecha_str):
        """Citas de la fecha con joins a barberos, clientes y servicios."""
        conn = self.db.get_connection()
        if not conn: return []

        try:
            cursor = conn.cursor()
            query = """
                SELECT c.id_cita, c.hora_inicio, c.hora_fin, b.nombre, cl.nombre, s.nombre, c.total_estimado, c.estado
                FROM citas c
                JOIN barberos b ON c.id_barbero = b.id_barbero
                JOIN clientes cl ON c.id_cliente = cl.id_cliente
                JOIN servicios s ON c.id_servicio = s.id_servicio
                WHERE c.fecha = ?
                ORDER BY c.hora_inicio ASC;
            """
            cursor.execute(query, (fecha_str,))
            return cursor.fetchall()
        finally:
            conn.close()

    def cancelar_cita(self, id_cita):
        conn = self.db.get_connection()
        if not conn: return False, "Error de conexión."

        try:
            cursor = conn.cursor()
            cursor.execute("SELECT estado FROM citas WHERE id_cita = ?", (id_cita,))
            resultado = cursor.fetchone()
            if not resultado: return False, "La cita no existe."
            
            if resultado[0] == 'Pagada': return False, "No se puede cancelar una cita ya cobrada."
            if resultado[0] == 'Cancelada': return False, "La cita ya está cancelada."

            cursor.execute("UPDATE citas SET estado = 'Cancelada' WHERE id_cita = ?", (id_cita,))
            conn.commit()
            return True, "Cita cancelada."
        finally:
            conn.close()