from fpdf import FPDF

# Crear PDF
pdf = FPDF()
pdf.add_page()

# Configuración de fuentes
pdf.set_font("Arial", "B", 24)
pdf.cell(0, 20, "BUS-MAIDAN", ln=True, align="C")

pdf.set_font("Arial", "B", 16)
pdf.cell(0, 10, "Documentación Técnica del Proyecto", ln=True, align="C")
pdf.ln(10)

# Introducción
pdf.set_font("Arial", "B", 14)
pdf.cell(0, 10, "1. Introducción", ln=True)
pdf.set_font("Arial", "", 11)
pdf.multi_cell(0, 5, "BUS-MAIDAN (anteriormente Montevideo Bus Tracker) es una aplicación web que muestra el movimiento en tiempo real de los autobuses en Montevideo, Uruguay. Utiliza la API oficial de Transporte Público de Montevideo para obtener datos de ubicación de los autobuses y los visualiza en un mapa interactivo.")
pdf.ln(5)

# Arquitectura
pdf.set_font("Arial", "B", 14)
pdf.cell(0, 10, "2. Arquitectura General", ln=True)
pdf.set_font("Arial", "", 11)
pdf.multi_cell(0, 5, "La aplicación sigue una arquitectura cliente-servidor donde:\n\n1. Backend (Flask): Se encarga de la autenticación con la API de Montevideo, la recuperación de datos y la exposición de endpoints REST.\n\n2. Frontend (JavaScript): Visualiza los datos en un mapa interactivo usando Leaflet y proporciona funcionalidades de UI.")
pdf.ln(5)

# Estructura de archivos
pdf.set_font("Arial", "B", 14)
pdf.cell(0, 10, "3. Estructura de Archivos", ln=True)
pdf.set_font("Arial", "", 11)
pdf.multi_cell(0, 5, "- app.py: Aplicación principal Flask\n- main.py: Punto de entrada\n- install.py: Script de instalación\n- static/: Recursos estáticos (CSS, JS, imágenes)\n- templates/: Plantillas HTML\n- static/js/main.js: Lógica principal del frontend\n- static/img/: Iconos SVG personalizados")
pdf.ln(5)

# Backend
pdf.set_font("Arial", "B", 14)
pdf.cell(0, 10, "4. Backend (Flask)", ln=True)
pdf.set_font("Arial", "B", 12)
pdf.cell(0, 8, "4.1 Autenticación con la API", ln=True)
pdf.set_font("Arial", "", 11)
pdf.multi_cell(0, 5, "La aplicación utiliza OAuth 2.0 con credenciales de cliente para autenticarse con la API. El método get_access_token() obtiene o refresca el token de acceso.")
pdf.ln(3)

pdf.set_font("Arial", "B", 12)
pdf.cell(0, 8, "4.2 Endpoints del Backend", ln=True)
pdf.set_font("Arial", "", 11)
pdf.multi_cell(0, 5, "- /: Página principal\n- /api/buses: Datos de autobuses\n- /api/lines: Líneas disponibles\n- /api/stops: Paradas de autobuses")
pdf.ln(3)

pdf.set_font("Arial", "B", 12)
pdf.cell(0, 8, "4.3 Modo de Simulación", ln=True)
pdf.set_font("Arial", "", 11)
pdf.multi_cell(0, 5, "Para desarrollo o cuando la API no está disponible, la aplicación puede usar datos simulados mediante las funciones generate_simulated_buses() y generate_simulated_stops().")
pdf.ln(5)

# Frontend
pdf.add_page()
pdf.set_font("Arial", "B", 14)
pdf.cell(0, 10, "5. Frontend (JavaScript)", ln=True)
pdf.set_font("Arial", "B", 12)
pdf.cell(0, 8, "5.1 Inicialización del Mapa", ln=True)
pdf.set_font("Arial", "", 11)
pdf.multi_cell(0, 5, "El mapa se inicializa con Leaflet y se configuran capas para buses y paradas. Se añaden controles de capas, geolocalización y escala.")
pdf.ln(3)

pdf.set_font("Arial", "B", 12)
pdf.cell(0, 8, "5.2 Marcadores de Mapa", ln=True)
pdf.set_font("Arial", "", 11)
pdf.multi_cell(0, 5, "Los marcadores de autobuses y paradas se crean con iconos SVG personalizados. Los autobuses se rotan según su dirección y muestran información en tooltips.")
pdf.ln(3)

pdf.set_font("Arial", "B", 12)
pdf.cell(0, 8, "5.3 Geolocalización", ln=True)
pdf.set_font("Arial", "", 11)
pdf.multi_cell(0, 5, "La aplicación utiliza la geolocalización del navegador para mostrar la ubicación del usuario y encontrar paradas cercanas a su posición.")
pdf.ln(5)

# API de Montevideo
pdf.set_font("Arial", "B", 14)
pdf.cell(0, 10, "6. API de Transporte Público de Montevideo", ln=True)
pdf.set_font("Arial", "", 11)
pdf.multi_cell(0, 5, "La aplicación utiliza los siguientes endpoints:\n\n- GET /buses: Autobuses en circulación\n- GET /buses/busstops: Todas las paradas\n- GET /buses/busstops/{id}/upcomingbuses: ETA a paradas\n- GET /buses/linevariants: Variantes de línea\n- GET /buses/gtfs/static/latest/google_transit.zip: Datos GTFS")
pdf.ln(5)

# Instalación
pdf.set_font("Arial", "B", 14)
pdf.cell(0, 10, "7. Instalación y Configuración", ln=True)
pdf.set_font("Arial", "B", 12)
pdf.cell(0, 8, "7.1 Variables de Entorno", ln=True)
pdf.set_font("Arial", "", 11)
pdf.multi_cell(0, 5, "- MONTEVIDEO_CLIENT_ID: ID de cliente para la API\n- MONTEVIDEO_CLIENT_SECRET: Secreto de cliente\n- SIMULATION_MODE: Activar modo simulación")
pdf.ln(3)

pdf.set_font("Arial", "B", 12)
pdf.cell(0, 8, "7.2 Proceso de Instalación", ln=True)
pdf.set_font("Arial", "", 11)
pdf.multi_cell(0, 5, "El proceso se documenta en README.md y se automatiza mediante install.py. Los pasos básicos son:\n\n1. Clonar el repositorio\n2. Crear entorno virtual (opcional)\n3. Instalar dependencias\n4. Configurar variables de entorno\n5. Iniciar con Gunicorn")
pdf.ln(5)

# Conclusión
pdf.set_font("Arial", "B", 14)
pdf.cell(0, 10, "8. Conclusión", ln=True)
pdf.set_font("Arial", "", 11)
pdf.multi_cell(0, 5, "BUS-MAIDAN es una aplicación web completa para seguimiento de autobuses que combina un backend Flask con un frontend JavaScript y visualización en mapa. Utiliza la API oficial de Transporte Público de Montevideo para proporcionar datos en tiempo real.")
pdf.ln(5)

pdf.set_font("Arial", "B", 12)
pdf.cell(0, 10, "Proyecto Open Source BUS-MAIDAN", ln=True, align="C")
pdf.set_font("Arial", "I", 10)
pdf.cell(0, 5, "Documentación Técnica - 2025", ln=True, align="C")

# Guardar el PDF
pdf.output("opensourcebusmaidan.pdf")