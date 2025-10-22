"""
Configuración de logging para el sistema
Maneja logs en consola y archivos
"""
import logging
from pathlib import Path
from config.config import (
    DIRECTORIO_LOGS_SCRAPER,
    FORMATO_LOG,
    FORMATO_FECHA_LOG,
    NIVEL_LOG
)


def configurar_logger(nombre_modulo, nombre_archivo_log=None):
    """
    Configura logger para un módulo específico
    
    Args:
        nombre_modulo: Nombre identificador del logger
        nombre_archivo_log: Nombre del archivo de log (opcional)
    
    Returns:
        logging.Logger: Logger configurado
    """
    # Crear instancia del logger
    logger = logging.getLogger(nombre_modulo)
    logger.setLevel(getattr(logging, NIVEL_LOG))
    
    # Si ya tiene handlers, retornar (evita duplicados)
    if logger.handlers:
        return logger
    
    # Crear formateador
    formateador = logging.Formatter(FORMATO_LOG, datefmt=FORMATO_FECHA_LOG)
    
    # Handler para consola
    handler_consola = logging.StreamHandler()
    handler_consola.setFormatter(formateador)
    logger.addHandler(handler_consola)
    
    # Handler para archivo (si se especifica)
    if nombre_archivo_log:
        ruta_archivo = DIRECTORIO_LOGS_SCRAPER / nombre_archivo_log
        handler_archivo = logging.FileHandler(ruta_archivo, encoding='utf-8')
        handler_archivo.setFormatter(formateador)
        logger.addHandler(handler_archivo)
    
    return logger