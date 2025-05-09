#!/usr/bin/env python3
"""
Script de instalación para Montevideo Bus Tracker

Este script automatiza el proceso de instalación de la aplicación Montevideo Bus Tracker
en un servidor Linux. Configura el entorno, instala dependencias y configura las credenciales
de la API.
"""

import os
import sys
import subprocess
import getpass
import platform
from pathlib import Path

# Colores para mensajes
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
RESET = '\033[0m'
BOLD = '\033[1m'

def print_header():
    """Imprime el encabezado del script"""
    print(f"\n{BOLD}{GREEN}=================================================={RESET}")
    print(f"{BOLD}{GREEN}    Instalador de Montevideo Bus Tracker    {RESET}")
    print(f"{BOLD}{GREEN}=================================================={RESET}\n")

def check_python_version():
    """Verifica la versión de Python"""
    print(f"{BOLD}Verificando versión de Python...{RESET}")
    
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"{RED}Error: Se requiere Python 3.8 o superior. Versión actual: {sys.version}{RESET}")
        sys.exit(1)
    
    print(f"{GREEN}✓ Python {version.major}.{version.minor}.{version.micro} detectado{RESET}")
    return True

def create_virtual_environment():
    """Crea un entorno virtual"""
    print(f"\n{BOLD}Configurando entorno virtual...{RESET}")
    
    if Path("venv").exists():
        print(f"{YELLOW}Entorno virtual ya existe, omitiendo este paso{RESET}")
        return True
    
    try:
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        print(f"{GREEN}✓ Entorno virtual creado exitosamente{RESET}")
        return True
    except subprocess.CalledProcessError:
        print(f"{RED}Error al crear el entorno virtual{RESET}")
        return False

def install_dependencies():
    """Instala las dependencias del proyecto"""
    print(f"\n{BOLD}Instalando dependencias...{RESET}")
    
    # Determinar el ejecutable de pip
    pip_cmd = "./venv/bin/pip" if Path("venv").exists() else "pip"
    
    # Crear requirements.txt si no existe
    if not Path("requirements.txt").exists():
        requirements = [
            "flask",
            "flask-sqlalchemy",
            "gunicorn",
            "requests",
            "psycopg2-binary",
            "email-validator"
        ]
        
        with open("requirements.txt", "w") as f:
            f.write("\n".join(requirements))
        
        print(f"{YELLOW}Archivo requirements.txt creado automáticamente{RESET}")
    
    try:
        subprocess.run([pip_cmd, "install", "-r", "requirements.txt"], check=True)
        print(f"{GREEN}✓ Dependencias instaladas exitosamente{RESET}")
        return True
    except subprocess.CalledProcessError:
        print(f"{RED}Error al instalar dependencias{RESET}")
        return False

def configure_environment():
    """Configura las variables de entorno para la API"""
    print(f"\n{BOLD}Configurando credenciales de la API...{RESET}")
    
    env_file = ".env"
    
    # Verificar si ya existe el archivo .env
    if Path(env_file).exists():
        use_existing = input(f"{YELLOW}El archivo {env_file} ya existe. ¿Desea usar las credenciales existentes? (s/n): {RESET}").lower() == 's'
        if use_existing:
            print(f"{GREEN}✓ Usando credenciales existentes{RESET}")
            return True
    
    # Solicitar las credenciales
    client_id = input(f"Ingrese el CLIENT_ID de la API de Montevideo (ef860456): ") or "ef860456"
    client_secret = input(f"Ingrese el CLIENT_SECRET de la API de Montevideo (e9e1b4c1335ad884957522e937b066e7): ") or "e9e1b4c1335ad884957522e937b066e7"
    
    # Crear archivo .env
    with open(env_file, "w") as f:
        f.write(f"MONTEVIDEO_CLIENT_ID={client_id}\n")
        f.write(f"MONTEVIDEO_CLIENT_SECRET={client_secret}\n")
        f.write("SIMULATION_MODE=false\n")
    
    # Establecer las variables para la sesión actual
    os.environ["MONTEVIDEO_CLIENT_ID"] = client_id
    os.environ["MONTEVIDEO_CLIENT_SECRET"] = client_secret
    os.environ["SIMULATION_MODE"] = "false"
    
    print(f"{GREEN}✓ Credenciales configuradas exitosamente{RESET}")
    return True

def create_service_file():
    """Crea un archivo de servicio systemd para ejecutar la aplicación como servicio"""
    print(f"\n{BOLD}Configurando servicio systemd...{RESET}")
    
    # Verificar si estamos en Linux y tenemos permisos sudo
    if platform.system() != "Linux":
        print(f"{YELLOW}No se puede crear un servicio systemd en {platform.system()}{RESET}")
        return False
    
    # Obtener la ruta completa al directorio actual
    app_path = os.path.abspath(".")
    
    service_content = f"""[Unit]
Description=Montevideo Bus Tracker
After=network.target

[Service]
User={os.getlogin()}
WorkingDirectory={app_path}
ExecStart={app_path}/venv/bin/gunicorn --bind 0.0.0.0:5000 main:app
Restart=always
Environment="MONTEVIDEO_CLIENT_ID={os.environ.get('MONTEVIDEO_CLIENT_ID', '')}"
Environment="MONTEVIDEO_CLIENT_SECRET={os.environ.get('MONTEVIDEO_CLIENT_SECRET', '')}"

[Install]
WantedBy=multi-user.target
"""
    
    service_file = "montevideo-bus-tracker.service"
    with open(service_file, "w") as f:
        f.write(service_content)
    
    print(f"{GREEN}✓ Archivo de servicio creado: {service_file}{RESET}")
    print(f"{YELLOW}Para instalar el servicio, ejecute como administrador:{RESET}")
    print(f"  sudo cp {service_file} /etc/systemd/system/")
    print(f"  sudo systemctl daemon-reload")
    print(f"  sudo systemctl enable {service_file}")
    print(f"  sudo systemctl start {service_file}")
    
    return True

def test_api_connection():
    """Prueba la conexión con la API"""
    print(f"\n{BOLD}Probando conexión con la API...{RESET}")
    
    # Importar las bibliotecas necesarias
    try:
        import requests
        from datetime import datetime, timedelta
    except ImportError:
        print(f"{RED}Error: No se pudieron importar las bibliotecas necesarias{RESET}")
        return False
    
    # URL de autenticación
    auth_url = "https://mvdapi-auth.montevideo.gub.uy/auth/realms/pci/protocol/openid-connect/token"
    
    # Credenciales
    client_id = os.environ.get("MONTEVIDEO_CLIENT_ID")
    client_secret = os.environ.get("MONTEVIDEO_CLIENT_SECRET")
    
    if not client_id or not client_secret:
        print(f"{RED}Error: No se encontraron credenciales de API{RESET}")
        return False
    
    # Datos para la autenticación
    data = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret
    }
    
    # Encabezados
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "*/*",
        "User-Agent": "BusTrackerApp/1.0"
    }
    
    try:
        response = requests.post(auth_url, data=data, headers=headers)
        
        if response.status_code == 200:
            token_data = response.json()
            if "access_token" in token_data:
                print(f"{GREEN}✓ Conexión exitosa con la API. Token obtenido.{RESET}")
                return True
        
        print(f"{RED}Error al conectar con la API. Código: {response.status_code}{RESET}")
        print(f"{RED}Respuesta: {response.text[:200]}...{RESET}")
        return False
        
    except Exception as e:
        print(f"{RED}Error al conectar con la API: {str(e)}{RESET}")
        return False

def print_completion_message():
    """Imprime el mensaje de finalización"""
    print(f"\n{BOLD}{GREEN}=================================================={RESET}")
    print(f"{BOLD}{GREEN}    Instalación Completada    {RESET}")
    print(f"{BOLD}{GREEN}=================================================={RESET}")
    print(f"\nPara iniciar la aplicación manualmente, ejecute:")
    print(f"  source venv/bin/activate  # Si está usando entorno virtual")
    print(f"  gunicorn --bind 0.0.0.0:5000 main:app")
    print(f"\nLa aplicación estará disponible en: http://localhost:5000")
    print(f"\n{YELLOW}Recuerde configurar su firewall si desea acceder desde otras máquinas.{RESET}")

def main():
    """Función principal"""
    print_header()
    
    # Verificar versión de Python
    if not check_python_version():
        return
    
    # Crear entorno virtual
    create_virtual_environment()
    
    # Instalar dependencias
    if not install_dependencies():
        print(f"{RED}Error: No se pudieron instalar las dependencias. Abortando.{RESET}")
        return
    
    # Configurar variables de entorno
    if not configure_environment():
        print(f"{RED}Error: No se pudieron configurar las credenciales. Abortando.{RESET}")
        return
    
    # Probar conexión con la API
    test_api_connection()
    
    # Crear archivo de servicio systemd
    create_service_file()
    
    # Mensaje de finalización
    print_completion_message()

if __name__ == "__main__":
    main()