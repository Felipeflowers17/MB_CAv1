"""
Configuración centralizada del proyecto MB_CAv1
"""
import os
from pathlib import Path
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

# ============================================
# RUTAS DEL PROYECTO
# ============================================
DIRECTORIO_BASE = Path(__file__).resolve().parent.parent

# Subdirectorios
DIRECTORIO_DATOS = DIRECTORIO_BASE / "data"
DIRECTORIO_DATOS_RAW = DIRECTORIO_DATOS / "raw"
DIRECTORIO_DATOS_PROCESADOS = DIRECTORIO_DATOS / "processed"
DIRECTORIO_EXPORTACIONES = DIRECTORIO_DATOS / "exports"

DIRECTORIO_LOGS = DIRECTORIO_BASE / "logs"
DIRECTORIO_LOGS_SCRAPER = DIRECTORIO_LOGS / "scraper"

# Crear directorios si no existen
for directorio in [DIRECTORIO_DATOS_RAW, DIRECTORIO_DATOS_PROCESADOS, 
                    DIRECTORIO_EXPORTACIONES, DIRECTORIO_LOGS_SCRAPER]:
    directorio.mkdir(parents=True, exist_ok=True)


# ============================================
# MERCADO PÚBLICO - URLs
# ============================================
URL_BASE_WEB = "https://buscador.mercadopublico.cl"
URL_BASE_API = "https://api.buscador.mercadopublico.cl/compra-agil"

# ============================================
# PARÁMETROS DE SCRAPING
# ============================================
# Fecha: siempre el día anterior
fecha_ayer = datetime.now().date() - timedelta(days=1)
FECHA_SCRAPING = fecha_ayer.strftime('%Y-%m-%d')

# Parámetros API por defecto
PARAMETROS_API = {
    'status': 2,            # Estado: Publicadas
    'order_by': 'recent',   # Orden: Más recientes
    'region': 'all',        # Región: Todas
    'page_number': 1        # Página inicial
}

# Configuración de delays y timeouts
DELAY_ENTRE_REQUESTS = float(os.getenv('REQUEST_DELAY', 2))
TIMEOUT_REQUESTS = int(os.getenv('REQUEST_TIMEOUT', 30))
MODO_HEADLESS = os.getenv('HEADLESS', 'True').lower() == 'true'

# ============================================
# LOGGING
# ============================================
NIVEL_LOG = os.getenv('LOG_LEVEL', 'INFO')
FORMATO_LOG = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
FORMATO_FECHA_LOG = '%Y-%m-%d %H:%M:%S'