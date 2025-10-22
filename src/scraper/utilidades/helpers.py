"""
Funciones auxiliares para el sistema de scraping
Incluye: manejo de JSON, tiempo, delays y validadores
"""
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Any, Dict
from config.config import (
    DIRECTORIO_DATOS_RAW,
    DELAY_ENTRE_REQUESTS
)


# ============================================
# FUNCIONES DE MANEJO DE JSON
# ============================================

def guardar_json(datos, nombre_archivo, directorio=DIRECTORIO_DATOS_RAW):
    """
    Guarda datos en formato JSON
    
    Args:
        datos: Datos a guardar (debe ser serializable)
        nombre_archivo: Nombre del archivo con extensión .json
        directorio: Directorio donde guardar (por defecto: data/raw/)
    
    Returns:
        Path: Ruta completa del archivo guardado
    """
    try:
        ruta_completa = directorio / nombre_archivo
        
        with open(ruta_completa, 'w', encoding='utf-8') as archivo:
            json.dump(datos, archivo, ensure_ascii=False, indent=2)
        
        return ruta_completa
        
    except Exception as e:
        raise Exception(f"ERROR al guardar JSON {nombre_archivo}: {e}")


def cargar_json(ruta_archivo):
    """
    Carga datos desde un archivo JSON
    
    Args:
        ruta_archivo: Ruta completa del archivo JSON
    
    Returns:
        Any: Datos cargados desde el JSON
    """
    try:
        with open(ruta_archivo, 'r', encoding='utf-8') as archivo:
            return json.load(archivo)
            
    except FileNotFoundError:
        raise FileNotFoundError(f"ERROR: Archivo no encontrado {ruta_archivo}")
    except json.JSONDecodeError as e:
        raise Exception(f"ERROR: JSON inválido en {ruta_archivo}: {e}")


def validar_json_serializable(datos):
    """
    Valida si los datos son serializables a JSON
    
    Args:
        datos: Datos a validar
    
    Returns:
        bool: True si es serializable, False si no
    """
    try:
        json.dumps(datos, ensure_ascii=False)
        return True
    except (TypeError, ValueError):
        return False


# ============================================
# FUNCIONES DE TIEMPO
# ============================================

def obtener_timestamp():
    """
    Genera timestamp en formato YYYYMMDD_HHMMSS
    
    Returns:
        str: Timestamp formateado
    """
    return datetime.now().strftime('%Y%m%d_%H%M%S')


def aplicar_delay(segundos=DELAY_ENTRE_REQUESTS):
    """
    Aplica pausa en la ejecución
    
    Args:
        segundos: Cantidad de segundos a esperar
    """
    time.sleep(segundos)


def calcular_tiempo_transcurrido(tiempo_inicio):
    """
    Calcula segundos transcurridos desde un tiempo inicial
    
    Args:
        tiempo_inicio: Datetime del momento inicial
    
    Returns:
        float: Segundos transcurridos
    """
    diferencia = datetime.now() - tiempo_inicio
    return diferencia.total_seconds()


def formatear_duracion(segundos):
    """
    Convierte segundos a formato legible (Xh Ym Zs)
    
    Args:
        segundos: Cantidad de segundos
    
    Returns:
        str: Duración formateada
    """
    segundos_totales = int(segundos)
    horas = segundos_totales // 3600
    minutos = (segundos_totales % 3600) // 60
    segundos_restantes = segundos_totales % 60
    
    if horas > 0:
        return f"{horas}h {minutos}m {segundos_restantes}s"
    elif minutos > 0:
        return f"{minutos}m {segundos_restantes}s"
    else:
        return f"{segundos_restantes}s"


# ============================================
# VALIDADORES
# ============================================

def validar_respuesta_api(datos):
    """
    Valida estructura de respuesta de la API de Mercado Público
    
    Estructura esperada:
    {
        "success": "OK",
        "payload": {
            "resultados": [...]
        }
    }
    
    Args:
        datos: Diccionario con respuesta de la API
    
    Returns:
        bool: True si es válida, False si no
    """
    try:
        if 'success' not in datos:
            return False
        if 'payload' not in datos:
            return False
        if 'resultados' not in datos['payload']:
            return False
        if not isinstance(datos['payload']['resultados'], list):
            return False
        return True
    except (TypeError, KeyError, AttributeError):
        return False


def validar_compra_agil(compra):
    """
    Valida que una compra tenga los campos mínimos requeridos
    
    Campos obligatorios:
    - codigo o id
    - nombre
    - organismo
    
    Args:
        compra: Diccionario con datos de compra
    
    Returns:
        bool: True si es válida, False si no
    """
    try:
        if not isinstance(compra, dict):
            return False
        
        # Verificar identificador
        tiene_id = 'id' in compra or 'codigo' in compra
        if not tiene_id:
            return False
        
        # Verificar nombre
        if 'nombre' not in compra or not compra['nombre']:
            return False
        
        # Verificar organismo
        if 'organismo' not in compra or not compra['organismo']:
            return False
        
        return True
        
    except (TypeError, KeyError):
        return False


def validar_codigo_compra(codigo):
    """
    Valida formato de código de compra ágil
    Formato esperado: XXXX-XXX-COTXX
    
    Args:
        codigo: Código a validar
    
    Returns:
        bool: True si es válido, False si no
    """
    try:
        if not isinstance(codigo, str) or not codigo:
            return False
        
        partes = codigo.split('-')
        
        # Debe tener 3 partes
        if len(partes) != 3:
            return False
        
        # Primera y segunda parte deben ser numéricas
        if not partes[0].isdigit() or not partes[1].isdigit():
            return False
        
        # Tercera parte debe empezar con 'COT'
        if not partes[2].startswith('COT'):
            return False
        
        return True
        
    except (AttributeError, IndexError):
        return False


def validar_lista_no_vacia(lista):
    """
    Valida que sea una lista con al menos un elemento
    
    Args:
        lista: Objeto a validar
    
    Returns:
        bool: True si es lista no vacía, False si no
    """
    return isinstance(lista, list) and len(lista) > 0