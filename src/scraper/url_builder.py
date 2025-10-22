"""
Constructor de URLs para Mercado Público
Genera URLs para páginas web y endpoints de API
"""
from typing import Dict
from config.config import (
    URL_BASE_WEB,
    PARAMETROS_API,
    FECHA_SCRAPING
)


def construir_url_listado(numero_pagina=1):
    
    #Construye URL para página de listado de compras ágiles
    
    
    # Combinar parámetros por defecto con fecha y paginación
    parametros = {
        **PARAMETROS_API,
        'date_from': FECHA_SCRAPING,
        'date_to': FECHA_SCRAPING,
        'page_number': numero_pagina
    }
    
    # Construir string de parámetros (key=value&key=value)
    string_parametros = '&'.join([f"{k}={v}" for k, v in parametros.items()])
    
    # Retornar URL completa
    return f"{URL_BASE_WEB}/compra-agil?{string_parametros}"


def construir_url_ficha(codigo_compra):
    return f"{URL_BASE_WEB}/ficha?code={codigo_compra}"


def construir_url_historial(codigo_compra):
    return f"{URL_BASE_WEB}/compra-agil?action=historial&code={codigo_compra}"


def validar_url(url):
    """
    Valida que una URL tenga formato básico correcto
    
    True si es válida, False si no
    """
    if not isinstance(url, str) or not url:
        return False
    
    if not (url.startswith('http://') or url.startswith('https://')):
        return False
    
    if 'mercadopublico.cl' not in url:
        return False
    
    return True