# BUS-MAIDAN

## Documentación Técnica Detallada

### Introducción

BUS-MAIDAN (anteriormente Montevideo Bus Tracker) es una aplicación web que muestra el movimiento de los autobuses en tiempo real en Montevideo, Uruguay. Utiliza la API de Transporte Público de Montevideo para obtener los datos de ubicación de los autobuses y los visualiza en un mapa interactivo.

Esta documentación detalla la arquitectura de la aplicación, la estructura de los archivos, el flujo de datos y las funciones principales del código fuente.

### Arquitectura General

La aplicación sigue una arquitectura cliente-servidor donde:

1. **Backend (Flask)**: Se encarga de la autenticación con la API de Montevideo, la recuperación de datos y la exposición de endpoints REST para el frontend.
2. **Frontend (JavaScript)**: Visualiza los datos en un mapa interactivo usando Leaflet y proporciona funcionalidades de UI.

### Estructura de Archivos

```
├── app.py                # Aplicación principal Flask
├── main.py               # Punto de entrada 
├── install.py            # Script de instalación
├── requirements.txt      # Dependencias del proyecto
├── static/
│   ├── css/style.css     # Estilos personalizados
│   ├── img/              # Imágenes e iconos
│   │   ├── bus-icon.svg  # Icono de autobús
│   │   └── stop-icon.svg # Icono de parada de autobús
│   └── js/
│       ├── main.js       # Lógica principal del frontend
│       └── leaflet-rotatedmarker.js # Plugin para rotación de marcadores
└── templates/
    └── index.html        # Plantilla principal HTML
```

### Backend (Flask)

#### Autenticación con la API

La aplicación utiliza OAuth 2.0 con credenciales de cliente para autenticarse con la API de Transporte de Montevideo:

```python
def get_access_token():
    """
    Obtiene o refresca el token de acceso OAuth para la API de Transporte de Montevideo
    """
    # Verifica si ya tenemos un token válido
    current_time = datetime.now()
    if token_data["access_token"] and token_data["expires_at"] and token_data["expires_at"] > current_time:
        logger.debug("Usando token de acceso en caché")
        return token_data["access_token"]
    
    # Necesitamos un nuevo token
    logger.debug("Solicitando nuevo token de acceso")
    
    # Obtener credenciales de variables de entorno
    client_id = os.environ.get("MONTEVIDEO_CLIENT_ID", "ef860456")
    client_secret = os.environ.get("MONTEVIDEO_CLIENT_SECRET", "e9e1b4c1335ad884957522e937b066e7")
    
    # Datos para la petición
    data = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret
    }
    
    # Cabeceras para la petición
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "*/*",
        "User-Agent": "BusTrackerApp/1.0"
    }
    
    # Realizar la solicitud
    response = requests.post(AUTH_URL, data=data, headers=headers)
    
    # Procesar la respuesta
    if response.status_code == 200:
        auth_data = response.json()
        
        if "access_token" in auth_data:
            token_data["access_token"] = auth_data["access_token"]
            expires_in = auth_data.get("expires_in", 300)
            token_data["expires_at"] = datetime.now() + timedelta(seconds=expires_in - 30)
            
            return token_data["access_token"]
    
    return None
```

#### Solicitudes a la API

Para realizar solicitudes a la API, la aplicación usa un método genérico que maneja la autenticación y los errores:

```python
def make_api_request(endpoint, params=None):
    """
    Realiza solicitudes autenticadas a la API de Transporte de Montevideo
    """
    token = get_access_token()
    if not token:
        return {"error": "Failed to obtain authentication token"}, 500
    
    # Preparar los headers
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "User-Agent": "BusTrackerApp/1.0"
    }
    
    # Construir la URL completa
    url = f"{API_BASE_URL}/{endpoint}"
    
    try:
        # Realizar la solicitud GET
        response = requests.get(url, headers=headers, params=params)
        
        # Si recibimos un error, registrar detalles
        if response.status_code != 200:
            logger.error(f"API returned error status: {response.status_code}")
            return {"error": f"API Error: {response.status_code}"}, response.status_code
        
        # Intentar procesar la respuesta como JSON
        data = response.json()
        return data, 200
            
    except Exception as e:
        logger.error(f"API request error: {str(e)}")
        return {"error": f"API request failed: {str(e)}"}, 500
```

#### Endpoints del Backend

La aplicación ofrece los siguientes endpoints REST para el frontend:

1. **/** - Página principal
   - Renderiza la plantilla HTML principal
   - Muestra el estado de conexión con la API

2. **/api/buses** - Datos de autobuses
   - Parámetros opcionales:
     - `line`: Filtrar por número de línea
   - Devuelve JSON con ubicaciones de autobuses

3. **/api/lines** - Líneas de autobuses
   - Devuelve JSON con todas las líneas disponibles

4. **/api/stops** - Paradas de autobuses
   - Parámetros opcionales:
     - `lat`: Latitud para búsqueda geográfica
     - `lng`: Longitud para búsqueda geográfica
     - `radius`: Radio de búsqueda en metros
   - Devuelve JSON con paradas cercanas

#### Modo de Simulación

Para desarrollo o cuando la API no está disponible, la aplicación puede usar datos simulados:

```python
def generate_simulated_buses(line_filter=None):
    """
    Genera datos simulados de autobuses para propósitos de demostración
    """
    buses = []
    
    # Seed random con la hora actual para asegurar que los autobuses se mueven entre solicitudes
    random.seed(int(time.time() / 15))  # Cambiar posición cada 15 segundos
    
    # Usar el filtro de línea solicitado o generar autobuses para varias líneas
    lines_to_use = [line_filter] if line_filter else random.sample(SIMULATED_BUS_LINES, 10)
    
    # Para cada línea, generar 3-8 autobuses
    for line in lines_to_use:
        if not line:
            continue
            
        num_buses = random.randint(3, 8)
        
        for i in range(num_buses):
            # Generar un autobús dentro del área de Montevideo
            latitude = MONTEVIDEO_CENTER[0] + (random.random() - 0.5) * 0.05
            longitude = MONTEVIDEO_CENTER[1] + (random.random() - 0.5) * 0.05
            
            # Rumbo aleatorio (0-359 grados)
            heading = random.randint(0, 359)
            
            # Velocidad aleatoria (0-45 km/h)
            speed = random.randint(0, 45)
            
            # Crear objeto de autobús
            bus = {
                "id": f"{line}-{i+1}",
                "line": line,
                "order": i+1,
                "latitude": latitude,
                "longitude": longitude,
                "heading": heading,
                "speed": speed,
                "destination": f"Terminal {random.choice(['Centro', 'Pocitos', 'Punta Carretas', 'Ciudad Vieja', 'Malvín'])}",
                "timestamp": datetime.now().isoformat()
            }
            
            buses.append(bus)
    
    return buses
```

### Frontend (JavaScript)

#### Inicialización del Mapa

El mapa se inicializa con Leaflet y se configuran las capas y controles:

```javascript
function initMap() {
    // Coordenadas de Montevideo
    const mvdCenter = [-34.9011, -56.1645];
    
    // Crear mapa
    map = L.map('map').setView(mvdCenter, 13);
    
    // Añadir capa de OpenStreetMap para mostrar calles claramente
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        maxZoom: 19
    }).addTo(map);
    
    // Crear grupos de capas
    busLayer = L.layerGroup().addTo(map);
    stopLayer = L.layerGroup().addTo(map);
    
    // Añadir control de capas
    const overlays = {
        "Buses": busLayer,
        "Paradas": stopLayer
    };
    
    L.control.layers(null, overlays, {
        position: 'topright',
        collapsed: false
    }).addTo(map);
    
    // Añadir control de geolocalización
    const locateControl = L.control.locate({
        position: 'topright',
        locateOptions: {
            enableHighAccuracy: true,
            watch: true      // Observar la ubicación del usuario (actualizar continuamente)
        },
        strings: {
            title: "Mi ubicación",
            popup: "Estás aquí"
        },
        flyTo: true,
        showPopup: true,
        icon: 'fa fa-location-arrow'
    }).addTo(map);
    
    // Añadir control de escala
    L.control.scale({
        imperial: false,     // Solo mostrar escala métrica
        position: 'bottomleft'
    }).addTo(map);
}
```

#### Actualización de Datos

La aplicación actualiza los datos de autobuses periódicamente:

```javascript
function fetchBusData(line) {
    updateStatus('Updating bus positions...');
    
    // Construir la URL con parámetro de línea opcional
    const url = line ? `/api/buses?line=${line}` : '/api/buses';
    
    fetch(url)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.error) {
                throw new Error(data.error);
            }
            
            busesData = data;
            updateMap();
            updateStatus(`Showing ${busesData.length} buses. Last update: ${new Date().toLocaleTimeString()}`);
        })
        .catch(error => {
            console.error('Error fetching bus data:', error);
            showError('Failed to load bus data', error.message);
            updateStatus('Error loading data. Click refresh to try again.', 'danger');
        });
}
```

#### Marcadores de Mapa

Los marcadores de autobuses y paradas se crean con iconos SVG personalizados:

```javascript
function createBusMarker(bus, busId) {
    const busLine = bus.line || 'Unknown';
    
    // Crear icono de autobús personalizado
    const busIcon = L.icon({
        iconUrl: '/static/img/bus-icon.svg',
        iconSize: [32, 32],
        iconAnchor: [16, 16],
        popupAnchor: [0, -16],
        className: `bus-line-${busLine}` // Para potencial estilizado CSS
    });
    
    // Crear marcador con rotación
    const marker = L.marker([bus.latitude, bus.longitude], {
        icon: busIcon,
        rotationAngle: bus.heading || 0,
        rotationOrigin: 'center center'
    }).addTo(busLayer);
    
    // Añadir manejador de clics
    marker.on('click', function() {
        selectedBus = busId;
        updateBusInfo(bus);
    });
    
    // Crear tooltip con información del autobús
    marker.bindTooltip(`Línea ${busLine} → ${bus.destination || 'Unknown'}`, { 
        direction: 'top',
        offset: [0, -15]
    });
    
    // Almacenar el marcador
    busMarkers[busId] = marker;
}

function createStopMarker(stop) {
    // Crear icono para parada de autobús
    const stopIcon = L.icon({
        iconUrl: '/static/img/stop-icon.svg',
        iconSize: [24, 24],
        iconAnchor: [12, 24],
        popupAnchor: [0, -24]
    });
    
    // Crear marcador
    const marker = L.marker([stop.latitude, stop.longitude], {
        icon: stopIcon
    }).addTo(stopLayer);
    
    // Crear popup con información de la parada
    let busLinesList = '';
    if (stop.lines && stop.lines.length > 0) {
        busLinesList = `<p>Líneas: ${stop.lines.join(', ')}</p>`;
    }
    
    const popupContent = `
        <div class="stop-popup">
            <h5>${stop.name || 'Parada'}</h5>
            <p>${stop.code || ''}</p>
            <p>${stop.address || ''}</p>
            ${busLinesList}
        </div>
    `;
    
    marker.bindPopup(popupContent);
    
    // Crear tooltip con información básica
    marker.bindTooltip(stop.name || 'Parada de bus', { 
        direction: 'top',
        offset: [0, -10]
    });
    
    // Almacenar el marcador
    stopMarkers[stop.id] = marker;
}
```

#### Geolocalización

La aplicación utiliza la geolocalización del navegador para:
1. Mostrar la ubicación del usuario en el mapa
2. Encontrar paradas cercanas a la posición del usuario

```javascript
// Cuando se encuentra la ubicación del usuario
map.on('locationfound', function(e) {
    console.log("Location found:", e.latlng);
    userPosition = e.latlng;
    
    // Obtener paradas cercanas
    fetchNearbyStops(userPosition.lat, userPosition.lng);
    
    // Ocultar insignia de simulación si estamos usando datos reales
    const simulationBadge = document.getElementById('simulation-badge');
    if (simulationBadge) {
        simulationBadge.style.display = 'none';
    }
});
```

### Endpoints de la API de Montevideo

La aplicación utiliza los siguientes endpoints de la API de Transporte Público de Montevideo:

1. **GET /buses** - Autobuses en circulación
   - Parámetros opcionales:
     - `lines`: Filtrar por línea
     - `company`: Filtrar por empresa
     - `busstop`: Filtrar por parada

2. **GET /buses/busstops** - Todas las paradas de autobús
   - Parámetros opcionales:
     - `lat`: Latitud para búsqueda geográfica
     - `lng`: Longitud para búsqueda geográfica
     - `radius`: Radio de búsqueda en metros

3. **GET /buses/busstops/{id}/upcomingbuses** - ETA de los autobuses a una parada específica
   - Devuelve una lista de autobuses que llegarán a la parada con ETA estimado

4. **GET /buses/linevariants** - Lista de variantes de línea
   - Devuelve todas las variantes de línea de autobús disponibles

5. **GET /buses/gtfs/static/latest/google_transit.zip** - Datos GTFS para uso offline
   - Proporciona un archivo ZIP con datos GTFS para uso sin conexión

### Instalación y Configuración

#### Variables de Entorno

La aplicación utiliza las siguientes variables de entorno:

- `MONTEVIDEO_CLIENT_ID`: ID de cliente para la API de Transporte de Montevideo
- `MONTEVIDEO_CLIENT_SECRET`: Secreto de cliente para la API
- `SIMULATION_MODE`: (opcional) Establecer a "true" para activar el modo simulación

#### Proceso de Instalación

El proceso de instalación se documenta en el archivo `README.md` y se automatiza mediante el script `install.py`. Los pasos básicos son:

1. Clonar o descargar el repositorio
2. Crear y activar un entorno virtual (opcional)
3. Instalar dependencias usando `pip install -r requirements.txt`
4. Configurar variables de entorno
5. Iniciar la aplicación con Gunicorn: `gunicorn --bind 0.0.0.0:5000 main:app`

### Conclusión

BUS-MAIDAN es una aplicación web completa para seguimiento de autobuses que combina un backend Flask para las API y un frontend JavaScript con visualización en mapa. Utiliza la API oficial de Transporte Público de Montevideo para proporcionar datos en tiempo real y ofrece un modo de simulación para desarrollo o cuando la API no está disponible.

La aplicación es un proyecto de código abierto que puede servir como base para desarrollar soluciones similares para otras ciudades o para ampliar sus capacidades con funciones adicionales.