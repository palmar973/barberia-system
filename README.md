# 💈 Barbería System - Sistema de Gestión Integral

Sistema de escritorio profesional desarrollado en **Python 3.12** y **PySide6** para la administración eficiente de barberías y centros estéticos. Incluye gestión de citas, control financiero multimoneda y reportes estadísticos.

## ✨ Características Principales

* **⚡ Atención Inmediata (Walk-in):** Módulo para registrar clientes sin cita previa ("Cita Express").
* **📅 Agenda Inteligente:** Visualización de citas diarias con validación de solapamiento de horarios.
* **👥 Soporte Multi-Barbero:** Gestión de múltiples agendas y asignación de profesionales.
* **💰 Control Financiero:**
    * Cierre de caja diario con desglose por método de pago.
    * **Tasa BCV en Tiempo Real:** Scraping automático del Banco Central de Venezuela para conversión de divisas.
    * Cálculo automático de comisiones y totales.
* **🎨 Interfaz Moderna:** UI diseñada en Dark Mode con PySide6, optimizada para uso prolongado.

## 🛠️ Tecnologías

* **Lenguaje:** Python 3.12+
* **GUI Framework:** PySide6 (Qt6)
* **Base de Datos:** SQLite (Relacional)
* **Integraciones:** `requests` & `beautifulsoup4` (Scraping web)

## 🚀 Instalación y Ejecución

Sigue estos pasos para desplegar el proyecto en un entorno local:

1.  **Clonar el repositorio:**
    ```bash
    git clone [https://github.com/TU_USUARIO/barberia-system.git](https://github.com/palmar973/barberia-system.git)
    cd barberia-system
    ```

2.  **Crear y activar entorno virtual:**
    ```bash
    # Windows
    py -m venv venv
    .\venv\Scripts\activate
    ```

3.  **Instalar dependencias:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Ejecutar la aplicación:**
    ```bash
    py main.py
    ```

## 📄 Estructura del Proyecto

* `/app`: Código fuente principal.
* `/views`: Interfaces gráficas (PySide6).
* `/controllers`: Lógica de negocio y conexión a BD.
* `/data`: Archivos de base de datos SQLite.

---
Desarrollado por **Claudio Palmar** - 2026.