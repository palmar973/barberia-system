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
        if not conn:
            return []

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

    def obtener_ingresos_semana(self):
        """Retorna [(Fecha, MontoTotal)] de los últimos 7 días."""
        conn = self.db.get_connection()
        if not conn:
            return []

        try:
            cursor = conn.cursor()
            
            query = """
                SELECT date(fecha_pago) as fecha, SUM(monto) as total
                FROM pagos
                WHERE date(fecha_pago) >= date('now', '-7 days')
                GROUP BY date(fecha_pago)
                ORDER BY fecha ASC
            """
            
            cursor.execute(query)
            resultados = cursor.fetchall()
            return resultados

        except Exception as e:
            print(f"Error obteniendo ingresos de la semana: {e}")
            return []
        finally:
            conn.close()

    def obtener_top_servicios(self):
        """Retorna [(NombreServicio, Cantidad)] (Top 5)."""
        conn = self.db.get_connection()
        if not conn:
            return []

        try:
            cursor = conn.cursor()
            
            query = """
                SELECT s.nombre, COUNT(c.id_cita) as cantidad
                FROM citas c
                JOIN servicios s ON c.id_servicio = s.id_servicio
                WHERE c.estado = 'Pagada'
                GROUP BY s.nombre
                ORDER BY cantidad DESC
                LIMIT 5
            """
            
            cursor.execute(query)
            resultados = cursor.fetchall()
            return resultados

        except Exception as e:
            print(f"Error obteniendo top servicios: {e}")
            return []
        finally:
            conn.close()

    def obtener_rendimiento_barberos_mes(self):
        """Retorna [(NombreBarbero, TotalDinero)] del mes actual."""
        conn = self.db.get_connection()
        if not conn:
            return []

        try:
            cursor = conn.cursor()
            
            query = """
                SELECT b.nombre, SUM(c.total_estimado) as total
                FROM citas c
                JOIN barberos b ON c.id_barbero = b.id_barbero
                WHERE c.estado = 'Pagada'
                AND strftime('%Y-%m', c.fecha) = strftime('%Y-%m', 'now')
                GROUP BY b.nombre
                ORDER BY total DESC
            """
            
            cursor.execute(query)
            resultados = cursor.fetchall()
            return resultados

        except Exception as e:
            print(f"Error obteniendo rendimiento de barberos: {e}")
            return []
        finally:
            conn.close()

    def obtener_kpis_hoy(self):
        """Retorna diccionario { 'ventas_hoy': $$, 'citas_hoy': ## }."""
        conn = self.db.get_connection()
        if not conn:
            return {'ventas_hoy': 0.0, 'citas_hoy': 0}

        try:
            cursor = conn.cursor()
            
            # Ventas hoy
            query_ventas = """
                SELECT COALESCE(SUM(monto), 0)
                FROM pagos
                WHERE date(fecha_pago) = date('now')
            """
            cursor.execute(query_ventas)
            ventas_hoy = cursor.fetchone()[0]
            
            # Citas hoy
            query_citas = """
                SELECT COUNT(*)
                FROM citas
                WHERE date(fecha) = date('now')
                AND estado IN ('Pendiente', 'Pagada')
            """
            cursor.execute(query_citas)
            citas_hoy = cursor.fetchone()[0]
            
            return {
                'ventas_hoy': float(ventas_hoy),
                'citas_hoy': int(citas_hoy)
            }

        except Exception as e:
            print(f"Error obteniendo KPIs de hoy: {e}")
            return {'ventas_hoy': 0.0, 'citas_hoy': 0}
        finally:
            conn.close()