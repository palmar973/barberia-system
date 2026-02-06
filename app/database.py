import sqlite3
import os
import sys

class DatabaseManager:
    """Administra SQLite y las migraciones (multi-barbero)."""

    def __init__(self, db_name="barberia.db"):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_dir = os.path.join(base_dir, 'data')
        
        if not os.path.exists(data_dir):
            try:
                os.makedirs(data_dir)
            except OSError as e:
                print(f"Error crítico: No se pudo crear el directorio de datos. {e}")
                sys.exit(1)

        self.db_path = os.path.join(data_dir, db_name)

    def get_connection(self):
        try:
            conn = sqlite3.connect(self.db_path)
            conn.execute("PRAGMA foreign_keys = ON")
            return conn
        except sqlite3.Error as e:
            print(f"Error al conectar con la base de datos: {e}")
            return None

    def inicializar_db(self):
        """Crea las tablas y realiza migraciones si es necesario."""
        conn = self.get_connection()
        if conn is None: return False

        try:
            cursor = conn.cursor()

            # Base: configuracion, clientes, servicios
            cursor.execute("CREATE TABLE IF NOT EXISTS configuracion (clave TEXT PRIMARY KEY, valor TEXT NOT NULL);")
            cursor.execute("CREATE TABLE IF NOT EXISTS clientes (id_cliente INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT NOT NULL, telefono TEXT, email TEXT, fecha_registro DATE DEFAULT CURRENT_DATE);")
            cursor.execute("CREATE TABLE IF NOT EXISTS servicios (id_servicio INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT NOT NULL, descripcion TEXT, precio REAL NOT NULL, duracion_minutos INTEGER NOT NULL, activo INTEGER DEFAULT 1);")

            # Nueva tabla: barberos
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS barberos (
                    id_barbero INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL UNIQUE,
                    activo INTEGER DEFAULT 1
                );
            """)

            # Citas ya con FK a barberos (migra si no existe)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS citas (
                    id_cita INTEGER PRIMARY KEY AUTOINCREMENT, 
                    id_cliente INTEGER NOT NULL, 
                    id_servicio INTEGER NOT NULL, 
                    id_barbero INTEGER NOT NULL DEFAULT 1, -- FK Nueva
                    fecha DATE NOT NULL, 
                    hora_inicio TEXT NOT NULL, 
                    hora_fin TEXT NOT NULL, 
                    total_estimado REAL, 
                    estado TEXT DEFAULT 'Pendiente', 
                    notas TEXT, 
                    FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente), 
                    FOREIGN KEY (id_servicio) REFERENCES servicios(id_servicio),
                    FOREIGN KEY (id_barbero) REFERENCES barberos(id_barbero)
                );
            """)

            # Pagos
            cursor.execute("CREATE TABLE IF NOT EXISTS pagos (id_pago INTEGER PRIMARY KEY AUTOINCREMENT, id_cita INTEGER NOT NULL, monto REAL NOT NULL, metodo_pago TEXT NOT NULL, referencia TEXT, fecha_pago DATETIME DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY (id_cita) REFERENCES citas(id_cita));")

            # --- MIGRACIÓN DE DATOS Y COLUMNAS ---

            # Seed básico: Ale y Fran
            barberos_data = [("Ale",), ("Fran",)]
            cursor.executemany("INSERT OR IGNORE INTO barberos (nombre) VALUES (?)", barberos_data)

            # Si citas existe sin id_barbero, la ampliamos sin perder datos
            cursor.execute("PRAGMA table_info(citas)")
            columnas = [col[1] for col in cursor.fetchall()]
            if 'id_barbero' not in columnas:
                print("Migrando DB: Agregando columna id_barbero a citas...")
                cursor.execute("ALTER TABLE citas ADD COLUMN id_barbero INTEGER NOT NULL DEFAULT 1")

            # Horario por defecto
            config_data = [("apertura", "08:00"), ("cierre", "18:00")]
            cursor.executemany("INSERT OR IGNORE INTO configuracion (clave, valor) VALUES (?, ?)", config_data)

            conn.commit()
            print("Base de datos inicializada y migrada correctamente.")
            return True

        except sqlite3.Error as e:
            print(f"Error al inicializar/migrar la base de datos: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

if __name__ == "__main__":
    db = DatabaseManager()
    db.inicializar_db()