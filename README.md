# Montevideo Bus Tracker

Una aplicación web para rastrear el movimiento de los autobuses en tiempo real en Montevideo, Uruguay.

## Descripción

Esta aplicación utiliza la API de Transporte Público de Montevideo para mostrar la ubicación en tiempo real de los autobuses en un mapa interactivo. Permite a los usuarios:

- Ver todos los autobuses activos en la ciudad
- Filtrar por líneas específicas
- Ver detalles de cada autobús (línea, destino, velocidad)
- Encontrar paradas cercanas a su ubicación
- Geolocalizar al usuario en el mapa

## Características

- Visualización en tiempo real de los autobuses en un mapa interactivo
- Interfaz responsiva y amigable
- Modo de simulación cuando la API no está disponible
- Filtrado de líneas de autobuses
- Información detallada sobre cada autobús
- Paradas de autobús cercanas
- Geolocalización del usuario

## Instalación en un servidor Linux

### Requisitos previos

- Python 3.8 o superior
- pip (administrador de paquetes de Python)
- Acceso a internet para descargar dependencias
- Credenciales para la API de Transporte Público de Montevideo

### Instalación manual

1. Clonar o descargar este repositorio:
   ```bash
   git clone https://github.com/tuusuario/montevideo-bus-tracker.git
   cd montevideo-bus-tracker
   ```

2. Crear y activar un entorno virtual (opcional pero recomendado):
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

3. Instalar las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

4. Configurar las variables de entorno:
   ```bash
   export MONTEVIDEO_CLIENT_ID="tu_client_id"
   export MONTEVIDEO_CLIENT_SECRET="tu_client_secret"
   ```

5. Iniciar la aplicación:
   ```bash
   gunicorn --bind 0.0.0.0:5000 main:app
   ```

6. Acceder a la aplicación en tu navegador:
   ```
   http://tu_servidor:5000
   ```

### Instalación automática

1. Clonar o descargar este repositorio:
   ```bash
   git clone https://github.com/tuusuario/montevideo-bus-tracker.git
   cd montevideo-bus-tracker
   ```

2. Ejecutar el script de instalación:
   ```bash
   python install.py
   ```

3. Seguir las instrucciones en pantalla para ingresar las credenciales de la API.

## Configuración

La aplicación necesita las siguientes variables de entorno:

- `MONTEVIDEO_CLIENT_ID`: El ID del cliente para la API de Transporte Público de Montevideo
- `MONTEVIDEO_CLIENT_SECRET`: El secreto del cliente para la API

También puedes configurar:
- `SIMULATION_MODE`: Establecer en "true" para activar el modo de simulación (sin usar la API real)

## API de Transporte Público de Montevideo

Esta aplicación utiliza la API oficial de Transporte Público de Montevideo. Algunos endpoints útiles son:

- GET /buses: Todos los buses en circulación
- GET /buses/busstops: Todas las paradas del sistema
- GET /buses/busstops/{id}/upcomingbuses: ETA de los buses a una parada específica
- GET /buses/linevariants: Lista de variantes de líneas
- GET /buses/gtfs/static/latest/google_transit.zip: Descarga datos GTFS para uso offline

## Licencia

Este proyecto está licenciado bajo la licencia MIT - ver el archivo LICENSE para más detalles.