import os
import requests
import json
import time
import logging
import random
import math
from flask import Flask, render_template, jsonify, request
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "montevideo-bus-tracker-secret")

# API Endpoints
AUTH_URL = "https://mvdapi-auth.montevideo.gub.uy/auth/realms/pci/protocol/openid-connect/token"
API_BASE_URL = "https://api.montevideo.gub.uy/api/transportepublico"

# Endpoints
BUSES_ENDPOINT = 'buses'
LINES_ENDPOINT = 'buses/linevariants'
STOPS_ENDPOINT = 'buses/busstops'

# Check if we should use simulation mode
SIMULATION_MODE = os.environ.get("SIMULATION_MODE", "false").lower() == "true"
logger.info(f"Simulation mode is {'enabled' if SIMULATION_MODE else 'disabled'}")

# Store the access token and its expiration
token_data = {
    "access_token": None,
    "expires_at": None
}

# Simulated data
MONTEVIDEO_CENTER = [-34.9011, -56.1645]  # Latitude, Longitude
SIMULATED_BUS_LINES = ['100', '102', '103', '105', '106', '109', '111', '112', '115', '116', '124', '125', '130', '142', '148', '150', '155', '156', '169', '174', '175', '180', '183', '185', '186', '187', '188', '192', '195', '199']

def get_access_token():
    """
    Obtain or refresh OAuth access token for the Montevideo Transport API
    """
    # Check if we have a valid token
    current_time = datetime.now()
    if token_data["access_token"] and token_data["expires_at"] and token_data["expires_at"] > current_time:
        logger.debug("Using cached access token")
        return token_data["access_token"]
    
    # We need a new token
    logger.debug("Requesting new access token")
    
    # Get credentials from environment variables
    client_id = os.environ.get("MONTEVIDEO_CLIENT_ID", "ef860456")  # Default value from the provided credentials
    client_secret = os.environ.get("MONTEVIDEO_CLIENT_SECRET", "e9e1b4c1335ad884957522e937b066e7")  # Default value from the provided credentials
    
    # Log redacted credentials for debugging (don't log actual secrets)
    logger.debug(f"Using client_id: {client_id[:4]}...{client_id[-4:] if len(client_id) > 8 else '****'}")
    
    # Create data parameters exactly as curl would format them
    data = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret
    }
    
    # Prepare headers similar to curl's default
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "*/*",
        "User-Agent": "BusTrackerApp/1.0"
    }
    
    try:
        logger.debug(f"Making auth request to: {AUTH_URL}")
        response = requests.post(AUTH_URL, data=data, headers=headers)
        
        # Log response details for debugging
        logger.debug(f"Auth response status: {response.status_code}")
        logger.debug(f"Response Content-Type: {response.headers.get('Content-Type', 'unknown')}")
        
        # Process the response
        if response.status_code == 200:
            try:
                auth_data = response.json()
                
                if "access_token" in auth_data:
                    logger.info("Successfully obtained access token")
                    token_data["access_token"] = auth_data["access_token"]
                    # Set expiration time with a small buffer
                    expires_in = auth_data.get("expires_in", 300)  # Default to 5 minutes if not provided
                    token_data["expires_at"] = datetime.now() + timedelta(seconds=expires_in - 30)
                    
                    logger.debug(f"New token obtained, expires in {expires_in} seconds")
                    return token_data["access_token"]
                else:
                    logger.error("No access_token found in response")
                    return None
                
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse authentication response as JSON: {str(e)}")
                return None
        else:
            logger.error(f"Authentication failed with status code: {response.status_code}")
            logger.error(f"Response content: {response.text[:100]}...")  # Log only a small portion
            return None
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Error obtaining access token: {str(e)}")
        return None

def make_api_request(endpoint, params=None):
    """
    Make authenticated request to the Montevideo Transport API
    """
    token = get_access_token()
    if not token:
        return {"error": "Failed to obtain authentication token"}, 500
    
    # Preparar los headers según el ejemplo de la documentación
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "User-Agent": "BusTrackerApp/1.0"
    }
    
    # Construir la URL completa
    url = f"{API_BASE_URL}/{endpoint}"
    logger.info(f"Making API request to: {url}")
    
    try:
        # Realizar la solicitud GET con los parámetros y headers adecuados
        response = requests.get(url, headers=headers, params=params)
        
        # Log de la respuesta para depuración
        logger.debug(f"API response status: {response.status_code}")
        logger.debug(f"API response content type: {response.headers.get('Content-Type', 'unknown')}")
        
        # Si recibimos un error, registrar detalles
        if response.status_code != 200:
            logger.error(f"API returned error status: {response.status_code}")
            logger.error(f"API error response: {response.text[:500]}...")
            return {"error": f"API Error: {response.status_code}"}, response.status_code
        
        # Intentar procesar la respuesta como JSON
        try:
            data = response.json()
            return data, 200
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse API response as JSON: {str(e)}")
            logger.error(f"Response content: {response.text[:500]}...")
            return {"error": "Invalid JSON response from API"}, 500
            
    except requests.exceptions.RequestException as e:
        logger.error(f"API request error: {str(e)}")
        error_msg = f"API request failed: {str(e)}"
        if hasattr(e, 'response') and e.response:
            error_msg += f" - Status code: {e.response.status_code}"
            if hasattr(e.response, 'text'):
                error_msg += f" - Response: {e.response.text[:500]}..."
        return {"error": error_msg}, 500

@app.route('/')
def index():
    """Render the main page"""
    # Check API connection status
    api_status = "No conectado"
    api_status_class = "danger"
    
    # Try to get a token to verify API connection
    token = get_access_token()
    if token:
        api_status = "API conectada correctamente"
        api_status_class = "success"
    else:
        api_status = "Error de conexión con la API"
        api_status_class = "danger"
    
    return render_template('index.html', api_status=api_status, api_status_class=api_status_class)

# Simulation functions
def generate_simulated_buses(line_filter=None):
    """
    Generate simulated bus data for demonstration purposes
    """
    buses = []
    
    # Seed random with current time to ensure buses move between requests
    random.seed(int(time.time() / 15))  # Change position every 15 seconds
    
    # Use either the requested line filter or generate buses for several lines
    lines_to_use = [line_filter] if line_filter else random.sample(SIMULATED_BUS_LINES, 10)
    
    # For each line, generate 3-8 buses
    for line in lines_to_use:
        if not line:
            continue
            
        num_buses = random.randint(3, 8)
        
        for i in range(num_buses):
            # Generate a bus within Montevideo area
            latitude = MONTEVIDEO_CENTER[0] + (random.random() - 0.5) * 0.05
            longitude = MONTEVIDEO_CENTER[1] + (random.random() - 0.5) * 0.05
            
            # Random heading (0-359 degrees)
            heading = random.randint(0, 359)
            
            # Random speed (0-45 km/h)
            speed = random.randint(0, 45)
            
            # Create bus object
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

def generate_simulated_lines():
    """
    Generate simulated bus line data for demonstration purposes
    """
    return SIMULATED_BUS_LINES

@app.route('/api/buses', methods=['GET'])
def get_buses():
    """Get active buses, optionally filtered by line"""
    line = request.args.get('line')
    
    if SIMULATION_MODE:
        logger.info("Using simulation mode for bus data")
        return jsonify(generate_simulated_buses(line)), 200
    
    # Otherwise use real API
    # If a line filter is provided, add it to API request params
    params = {}
    if line:
        params['lines'] = line
        logger.info(f"Filtering buses by line: {line}")
    
    bus_data, status_code = make_api_request('buses', params=params)
    
    if status_code != 200:
        logger.error(f"Failed to get bus data: {bus_data}")
        return jsonify(bus_data), status_code
    
    # Log number of buses returned
    if isinstance(bus_data, list):
        logger.info(f"Retrieved {len(bus_data)} buses from API")
        
        # Transform the API data to match our frontend's expected format
        formatted_buses = []
        for bus in bus_data:
            # Extract lat/lng from the location object if available
            latitude = None
            longitude = None
            
            if 'location' in bus and 'coordinates' in bus['location'] and len(bus['location']['coordinates']) >= 2:
                # API returns [longitude, latitude] format, so we need to swap
                longitude = bus['location']['coordinates'][0]
                latitude = bus['location']['coordinates'][1]
            
            if latitude is None or longitude is None:
                # Skip buses without valid coordinates
                continue
                
            # Extract heading from the bus data if available
            heading = 0  # Default heading
            if 'heading' in bus:
                heading = bus['heading']
            elif 'direction' in bus:
                heading = bus['direction']
                
            # Create a formatted bus object
            formatted_bus = {
                "id": bus.get('id', f"{bus.get('line', 'unknown')}-{bus.get('busId', 'unknown')}"),
                "line": bus.get('line', 'unknown'),
                "order": bus.get('order', 1),  # Default order
                "latitude": latitude,
                "longitude": longitude,
                "heading": heading,
                "speed": bus.get('speed', 0),
                "destination": bus.get('destination', bus.get('subline', 'Unknown')),
                "timestamp": bus.get('timestamp', datetime.now().isoformat()),
                "company": bus.get('company', ''),
                "subline": bus.get('subline', '')
            }
            
            formatted_buses.append(formatted_bus)
            
        logger.info(f"Formatted {len(formatted_buses)} buses for frontend")
        return jsonify(formatted_buses), 200
    
    return jsonify(bus_data), 200

@app.route('/api/lines', methods=['GET'])
def get_lines():
    """Get all bus lines"""
    if SIMULATION_MODE:
        logger.info("Using simulation mode for bus lines")
        return jsonify(generate_simulated_lines()), 200
        
    # Otherwise use real API
    lines_data, status_code = make_api_request(LINES_ENDPOINT)
    
    if status_code != 200:
        return jsonify(lines_data), status_code
    
    # Extract unique line numbers
    unique_lines = set()
    if isinstance(lines_data, list):
        for line in lines_data:
            # Extract just the number from code (e.g., "L116" -> "116")
            if 'code' in line and line['code'].startswith('L'):
                line_number = line['code'][1:]
                unique_lines.add(line_number)
    
    # Sort lines numerically
    sorted_lines = sorted(list(unique_lines), key=lambda x: int(x) if x.isdigit() else x)
    
    return jsonify(sorted_lines), 200

# Simulate bus stops for when the API is not available
def generate_simulated_stops(latitude=None, longitude=None, radius=None):
    """Generate simulated bus stops for a given area"""
    if not latitude or not longitude:
        # Use Montevideo center if no coordinates provided
        latitude, longitude = MONTEVIDEO_CENTER[0], MONTEVIDEO_CENTER[1]
    
    radius = radius or 1000  # Default 1km radius
    
    # Generate 10-20 random bus stops within the radius
    num_stops = random.randint(10, 20)
    stops = []
    
    for i in range(num_stops):
        # Generate random position within radius
        # Convert radius from meters to latitude/longitude degrees (approximate)
        lat_offset = (random.random() - 0.5) * 2 * (radius / 111000)  # 1 degree lat = ~111km
        lng_offset = (random.random() - 0.5) * 2 * (radius / (111000 * math.cos(math.radians(latitude))))
        
        stop_lat = latitude + lat_offset
        stop_lng = longitude + lng_offset
        
        # Generate random lines that serve this stop (2-5 lines)
        num_lines = random.randint(2, 5)
        lines = random.sample(SIMULATED_BUS_LINES, num_lines)
        
        # Create stop object
        stop = {
            "id": f"stop-{i+1}",
            "code": f"P{1000 + i}",
            "name": f"Parada #{i+1}",
            "address": f"Calle {random.choice(['18 de Julio', 'Rivera', 'Agraciada', 'Luis A. de Herrera', 'Italia'])} {1000 + i*10}",
            "latitude": stop_lat,
            "longitude": stop_lng,
            "lines": lines
        }
        
        stops.append(stop)
    
    return stops

@app.route('/api/stops', methods=['GET'])
def get_stops():
    """Get bus stops, optionally filtered by location and radius"""
    # Get query parameters
    latitude = request.args.get('lat', type=float)
    longitude = request.args.get('lng', type=float)
    radius = request.args.get('radius', default=1000, type=int)  # default 1km radius
    
    if SIMULATION_MODE:
        logger.info("Using simulation mode for bus stops")
        return jsonify(generate_simulated_stops(latitude, longitude, radius)), 200
    
    # Otherwise use real API
    params = {}
    if latitude and longitude:
        # Build location-based query
        params['lat'] = latitude
        params['lng'] = longitude
        params['radius'] = radius
        logger.info(f"Querying stops near ({latitude}, {longitude}) with radius {radius}m")
    
    stops_data, status_code = make_api_request(STOPS_ENDPOINT, params=params)
    
    if status_code != 200:
        logger.error(f"Failed to get stops data: {stops_data}")
        return jsonify(stops_data), status_code
    
    # Format the stops data for the frontend
    if isinstance(stops_data, list):
        logger.info(f"Retrieved {len(stops_data)} stops from API")
        
        formatted_stops = []
        for stop in stops_data:
            # Extract location data
            latitude = None
            longitude = None
            
            if 'location' in stop and 'coordinates' in stop['location'] and len(stop['location']['coordinates']) >= 2:
                # API returns [longitude, latitude] format, so we need to swap
                longitude = stop['location']['coordinates'][0]
                latitude = stop['location']['coordinates'][1]
            
            if latitude is None or longitude is None:
                # Skip stops without valid coordinates
                continue
                
            # Create a formatted stop object
            formatted_stop = {
                "id": stop.get('id', ''),
                "code": stop.get('code', ''),
                "name": stop.get('nombre', stop.get('name', '')),
                "address": stop.get('direccion', stop.get('address', '')),
                "latitude": latitude,
                "longitude": longitude,
                "lines": stop.get('lines', [])
            }
            
            formatted_stops.append(formatted_stop)
            
        logger.info(f"Formatted {len(formatted_stops)} stops for frontend")
        return jsonify(formatted_stops), 200
    
    return jsonify(stops_data), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
