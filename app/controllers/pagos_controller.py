import sys
import os

# Ajuste de path para importar database correctamente
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database import DatabaseManager

class PagosController:
    """Pagos y caja con transacciones atómicas."""

    def __init__(self):
        self.db = DatabaseManager()

    def obtener_detalle_cita(self, id_cita):
        """Detalle rápido de la cita para el ticket previo al cobro."""
        conn = self.db.get_connection()
        if not conn: return None
        try:
            cursor = conn.cursor()
            query = """
                SELECT cl.nombre, s.nombre, c.total_estimado, c.hora_inicio
                FROM citas c
                JOIN clientes cl ON c.id_cliente = cl.id_cliente
                JOIN servicios s ON c.id_servicio = s.id_servicio
                WHERE c.id_cita = ?
            """
            cursor.execute(query, (id_cita,))
            return cursor.fetchone()
        except Exception as e:
            print(f"Error al obtener detalle de cita: {e}")
            return None
        finally:
            conn.close()

    def registrar_pago(self, id_cita, monto, metodo_pago, referencia):
        """Tx: inserta pago y marca la cita como pagada; rollback si algo falla."""
        conn = self.db.get_connection()
        if not conn: return False

        try:
            cursor = conn.cursor()
            
            # Evitar cobrar citas ya cerradas
            cursor.execute("SELECT estado FROM citas WHERE id_cita = ?", (id_cita,))
            estado_actual = cursor.fetchone()[0]
            if estado_actual in ['Pagada', 'Cancelada']:
                print("Intento de pago sobre cita ya cerrada.")
                return False

            query_pago = """
                INSERT INTO pagos (id_cita, monto, metodo_pago, referencia)
                VALUES (?, ?, ?, ?)
            """
            cursor.execute(query_pago, (id_cita, monto, metodo_pago, referencia))

            query_cita = "UPDATE citas SET estado = 'Pagada' WHERE id_cita = ?"
            cursor.execute(query_cita, (id_cita,))
            conn.commit()
            print(f"Pago registrado con éxito para cita ID {id_cita}")
            return True

        except Exception as e:
            conn.rollback() # Deshacer todo si hay error
            print(f"Error CRÍTICO en transacción de pago: {e}")
            return False
        finally:
            conn.close()