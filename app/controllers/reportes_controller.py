import sys
import os

# Ajuste de path para importar database correctamente
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database import DatabaseManager

class ReportesController:
    """Reportes y agregaciones (GROUP BY, SUM, COUNT)."""

    def __init__(self):
        self.db = DatabaseManager()

    def obtener_cierre_diario(self, fecha_str):
        """Suma ingresos por método de pago en la fecha dada (YYYY-MM-DD)."""
        conn = self.db.get_connection()
        if not conn: return []

        try:
            cursor = conn.cursor()
            
            # SQLite guarda las fechas como texto ISO; date() las normaliza para agrupar.
            query = """
                SELECT metodo_pago, SUM(monto)
                FROM pagos
                WHERE date(fecha_pago) = date(?)
                GROUP BY metodo_pago
                ORDER BY metodo_pago ASC
            """
            
            cursor.execute(query, (fecha_str,))
            resultados = cursor.fetchall()
            return resultados

        except Exception as e:
            print(f"Error generando cierre diario: {e}")
            return []
        finally:
            conn.close()

    def obtener_comisiones(self, fecha_inicio, fecha_fin):
        """Calcula comisiones por barbero en un rango de fechas."""
        conn = self.db.get_connection()
        if not conn: return []

        try:
            cursor = conn.cursor()
            
            query = """
                SELECT b.nombre, SUM(c.total_estimado)
                FROM citas c
                JOIN barberos b ON c.id_barbero = b.id_barbero
                WHERE c.estado = 'Pagada'
                AND date(c.fecha) BETWEEN date(?) AND date(?)
                GROUP BY b.nombre
            """
            
            cursor.execute(query, (fecha_inicio, fecha_fin))
            resultados = cursor.fetchall()
            return resultados

        except Exception as e:
            print(f"Error generando reporte de comisiones: {e}")
            return []
        finally:
            conn.close()