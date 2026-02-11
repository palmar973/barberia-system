from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QSizePolicy
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

from controllers.reportes_controller import ReportesController


class DashboardView(QWidget):
    """Dashboard de Inteligencia de Negocios con gráficos y KPIs."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.controller = ReportesController()
        self.init_ui()
        self.cargar_datos()
    
    def init_ui(self):
        """Inicializa la interfaz del dashboard."""
        # Layout principal vertical
        layout_principal = QVBoxLayout()
        layout_principal.setContentsMargins(20, 20, 20, 20)
        layout_principal.setSpacing(20)
        self.setLayout(layout_principal)
        
        # Título
        lbl_titulo = QLabel("📈 Dashboard de Inteligencia de Negocios")
        lbl_titulo.setFont(QFont("Arial", 20, QFont.Bold))
        lbl_titulo.setStyleSheet("color: #ECF0F1; margin-bottom: 10px;")
        layout_principal.addWidget(lbl_titulo)
        
        # Fila Superior: KPIs
        layout_kpis = QHBoxLayout()
        layout_kpis.setSpacing(15)
        
        self.card_ventas_hoy = self.crear_tarjeta_kpi("Ventas Hoy", "$0.00", "#27AE60")
        self.card_citas_hoy = self.crear_tarjeta_kpi("Citas Hoy", "0", "#3498DB")
        self.card_proyeccion_mes = self.crear_tarjeta_kpi("Proyección Mes", "$0.00", "#9B59B6")
        
        layout_kpis.addWidget(self.card_ventas_hoy)
        layout_kpis.addWidget(self.card_citas_hoy)
        layout_kpis.addWidget(self.card_proyeccion_mes)
        
        layout_principal.addLayout(layout_kpis)
        
        # Fila Central: Gráficos de Tendencia e Ingresos y Top Barberos
        layout_graficos_centrales = QHBoxLayout()
        layout_graficos_centrales.setSpacing(15)
        
        # Gráfico de Líneas: Tendencia de Ingresos (7 días)
        frame_tendencia = self.crear_frame_grafico()
        layout_tendencia = QVBoxLayout()
        frame_tendencia.setLayout(layout_tendencia)
        
        lbl_tendencia = QLabel("Tendencia de Ingresos (7 días)")
        lbl_tendencia.setFont(QFont("Arial", 12, QFont.Bold))
        lbl_tendencia.setStyleSheet("color: #ECF0F1; padding: 5px;")
        layout_tendencia.addWidget(lbl_tendencia)
        
        self.canvas_tendencia = self.crear_grafico_tendencia()
        layout_tendencia.addWidget(self.canvas_tendencia)
        
        # Gráfico de Barras: Top Barberos
        frame_barberos = self.crear_frame_grafico()
        layout_barberos = QVBoxLayout()
        frame_barberos.setLayout(layout_barberos)
        
        lbl_barberos = QLabel("Top Barberos del Mes")
        lbl_barberos.setFont(QFont("Arial", 12, QFont.Bold))
        lbl_barberos.setStyleSheet("color: #ECF0F1; padding: 5px;")
        layout_barberos.addWidget(lbl_barberos)
        
        self.canvas_barberos = self.crear_grafico_barberos()
        layout_barberos.addWidget(self.canvas_barberos)
        
        layout_graficos_centrales.addWidget(frame_tendencia)
        layout_graficos_centrales.addWidget(frame_barberos)
        
        layout_principal.addLayout(layout_graficos_centrales)
        
        # Fila Inferior: Gráfico de Donut - Distribución de Servicios
        frame_servicios = self.crear_frame_grafico()
        layout_servicios = QVBoxLayout()
        frame_servicios.setLayout(layout_servicios)
        
        lbl_servicios = QLabel("Distribución de Servicios")
        lbl_servicios.setFont(QFont("Arial", 12, QFont.Bold))
        lbl_servicios.setStyleSheet("color: #ECF0F1; padding: 5px;")
        lbl_servicios.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout_servicios.addWidget(lbl_servicios)
        
        self.canvas_servicios = self.crear_grafico_servicios()
        layout_servicios.addWidget(self.canvas_servicios)
        
        layout_principal.addWidget(frame_servicios)
    
    def crear_tarjeta_kpi(self, titulo, valor, color):
        """Crea una tarjeta KPI."""
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: {color};
                border-radius: 10px;
                padding: 15px;
            }}
        """)
        frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        frame.setMinimumHeight(120)
        
        layout = QVBoxLayout()
        frame.setLayout(layout)
        
        lbl_titulo = QLabel(titulo)
        lbl_titulo.setFont(QFont("Arial", 12, QFont.Bold))
        lbl_titulo.setStyleSheet("color: white;")
        lbl_titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        lbl_valor = QLabel(valor)
        lbl_valor.setFont(QFont("Arial", 28, QFont.Bold))
        lbl_valor.setStyleSheet("color: white;")
        lbl_valor.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_valor.setObjectName("valor_kpi")
        
        layout.addWidget(lbl_titulo)
        layout.addWidget(lbl_valor)
        
        return frame
    
    def crear_frame_grafico(self):
        """Crea un frame contenedor para gráficos."""
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background-color: #2C3E50;
                border-radius: 10px;
                padding: 10px;
            }
        """)
        return frame
    
    def crear_grafico_tendencia(self):
        """Crea el gráfico de líneas para la tendencia de ingresos."""
        fig = Figure(figsize=(6, 4), facecolor='#2b2b2b')
        canvas = FigureCanvas(fig)
        self.ax_tendencia = fig.add_subplot(111)
        self.ax_tendencia.set_facecolor('#2b2b2b')
        self.ax_tendencia.tick_params(colors='white')
        self.ax_tendencia.spines['bottom'].set_color('white')
        self.ax_tendencia.spines['top'].set_color('white')
        self.ax_tendencia.spines['right'].set_color('white')
        self.ax_tendencia.spines['left'].set_color('white')
        self.ax_tendencia.xaxis.label.set_color('white')
        self.ax_tendencia.yaxis.label.set_color('white')
        self.ax_tendencia.title.set_color('white')
        
        return canvas
    
    def crear_grafico_barberos(self):
        """Crea el gráfico de barras para top barberos."""
        fig = Figure(figsize=(6, 4), facecolor='#2b2b2b')
        canvas = FigureCanvas(fig)
        self.ax_barberos = fig.add_subplot(111)
        self.ax_barberos.set_facecolor('#2b2b2b')
        self.ax_barberos.tick_params(colors='white')
        self.ax_barberos.spines['bottom'].set_color('white')
        self.ax_barberos.spines['top'].set_color('white')
        self.ax_barberos.spines['right'].set_color('white')
        self.ax_barberos.spines['left'].set_color('white')
        self.ax_barberos.xaxis.label.set_color('white')
        self.ax_barberos.yaxis.label.set_color('white')
        self.ax_barberos.title.set_color('white')
        
        return canvas
    
    def crear_grafico_servicios(self):
        """Crea el gráfico de donut para distribución de servicios."""
        fig = Figure(figsize=(8, 4), facecolor='#2b2b2b')
        canvas = FigureCanvas(fig)
        self.ax_servicios = fig.add_subplot(111)
        self.ax_servicios.set_facecolor('#2b2b2b')
        
        return canvas
    
    def cargar_datos(self):
        """Carga y actualiza todos los datos del dashboard."""
        # KPIs
        kpis = self.controller.obtener_kpis_hoy()
        self.actualizar_kpi(self.card_ventas_hoy, f"${kpis['ventas_hoy']:.2f}")
        self.actualizar_kpi(self.card_citas_hoy, str(kpis['citas_hoy']))
        
        # Calcular proyección del mes (simple: ventas_hoy * días restantes)
        import datetime
        dia_actual = datetime.datetime.now().day
        dias_mes = 30  # Aproximación
        if kpis['ventas_hoy'] > 0:
            proyeccion = kpis['ventas_hoy'] * (dias_mes / dia_actual)
        else:
            proyeccion = 0
        self.actualizar_kpi(self.card_proyeccion_mes, f"${proyeccion:.2f}")
        
        # Gráfico de Tendencia
        datos_tendencia = self.controller.obtener_ingresos_semana()
        self.actualizar_grafico_tendencia(datos_tendencia)
        
        # Gráfico de Barberos
        datos_barberos = self.controller.obtener_rendimiento_barberos_mes()
        self.actualizar_grafico_barberos(datos_barberos)
        
        # Gráfico de Servicios
        datos_servicios = self.controller.obtener_top_servicios()
        self.actualizar_grafico_servicios(datos_servicios)
    
    def actualizar_kpi(self, card, valor):
        """Actualiza el valor de una tarjeta KPI."""
        lbl_valor = card.findChild(QLabel, "valor_kpi")
        if lbl_valor:
            lbl_valor.setText(valor)
    
    def actualizar_grafico_tendencia(self, datos):
        """Actualiza el gráfico de tendencia de ingresos."""
        self.ax_tendencia.clear()
        
        if not datos:
            self.ax_tendencia.text(0.5, 0.5, 'No hay datos disponibles', 
                                  horizontalalignment='center',
                                  verticalalignment='center',
                                  transform=self.ax_tendencia.transAxes,
                                  color='white')
        else:
            fechas = [fila[0] for fila in datos]
            montos = [fila[1] for fila in datos]
            
            # Formatear fechas para mostrar solo día/mes
            fechas_formateadas = [fecha.split('-')[2] + '/' + fecha.split('-')[1] for fecha in fechas]
            
            self.ax_tendencia.plot(fechas_formateadas, montos, marker='o', color='#1ABC9C', linewidth=2, markersize=8)
            self.ax_tendencia.set_xlabel('Fecha', color='white')
            self.ax_tendencia.set_ylabel('Ingresos ($)', color='white')
            self.ax_tendencia.grid(True, alpha=0.3, color='gray')
            
            # Rotar etiquetas del eje x para mejor legibilidad
            self.ax_tendencia.tick_params(axis='x', rotation=45)
        
        # Configurar colores del tema oscuro
        self.ax_tendencia.set_facecolor('#2b2b2b')
        self.ax_tendencia.tick_params(colors='white')
        for spine in self.ax_tendencia.spines.values():
            spine.set_color('white')
        
        self.canvas_tendencia.draw()
    
    def actualizar_grafico_barberos(self, datos):
        """Actualiza el gráfico de top barberos."""
        self.ax_barberos.clear()
        
        if not datos:
            self.ax_barberos.text(0.5, 0.5, 'No hay datos disponibles', 
                                 horizontalalignment='center',
                                 verticalalignment='center',
                                 transform=self.ax_barberos.transAxes,
                                 color='white')
        else:
            nombres = [fila[0] for fila in datos]
            totales = [fila[1] for fila in datos]
            
            colores = ['#E74C3C', '#3498DB', '#F39C12', '#9B59B6', '#1ABC9C']
            barras = self.ax_barberos.bar(nombres, totales, color=colores[:len(nombres)])
            
            self.ax_barberos.set_xlabel('Barbero', color='white')
            self.ax_barberos.set_ylabel('Ingresos ($)', color='white')
            self.ax_barberos.grid(True, alpha=0.3, color='gray', axis='y')
            
            # Agregar valores sobre las barras
            for barra in barras:
                altura = barra.get_height()
                self.ax_barberos.text(barra.get_x() + barra.get_width()/2., altura,
                                     f'${altura:.2f}',
                                     ha='center', va='bottom', color='white', fontsize=9)
        
        # Configurar colores del tema oscuro
        self.ax_barberos.set_facecolor('#2b2b2b')
        self.ax_barberos.tick_params(colors='white')
        for spine in self.ax_barberos.spines.values():
            spine.set_color('white')
        
        self.canvas_barberos.draw()
    
    def actualizar_grafico_servicios(self, datos):
        """Actualiza el gráfico de donut de servicios."""
        self.ax_servicios.clear()
        
        if not datos:
            self.ax_servicios.text(0.5, 0.5, 'No hay datos disponibles', 
                                  horizontalalignment='center',
                                  verticalalignment='center',
                                  transform=self.ax_servicios.transAxes,
                                  color='white')
        else:
            servicios = [fila[0] for fila in datos]
            cantidades = [fila[1] for fila in datos]
            
            colores = ['#E74C3C', '#3498DB', '#F39C12', '#9B59B6', '#1ABC9C']
            
            # Crear gráfico de donut
            wedges, texts, autotexts = self.ax_servicios.pie(
                cantidades, 
                labels=servicios, 
                autopct='%1.1f%%',
                startangle=90,
                colors=colores[:len(servicios)],
                wedgeprops=dict(width=0.5, edgecolor='#2b2b2b')
            )
            
            # Configurar colores del texto
            for text in texts:
                text.set_color('white')
                text.set_fontsize(10)
            
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontsize(9)
                autotext.set_weight('bold')
        
        self.ax_servicios.set_facecolor('#2b2b2b')
        self.canvas_servicios.draw()
