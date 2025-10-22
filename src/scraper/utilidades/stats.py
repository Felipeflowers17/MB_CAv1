"""
Clase para rastrear estadísticas durante el scraping
Mantiene contadores y métricas de progreso
"""
from datetime import datetime
from .helpers import calcular_tiempo_transcurrido, formatear_duracion


class EstadisticasScraper:
    """
    Clase para trackear métricas durante el scraping
    
    Atributos:
        tiempo_inicio: Momento de inicio del scraping
        paginas_procesadas: Contador de páginas procesadas
        items_scrapeados: Contador de items extraídos
        errores: Contador de errores encontrados
        reintentos: Contador de reintentos realizados
    """
    
    def __init__(self):
        """Inicializa estadísticas con contadores en cero"""
        self.tiempo_inicio = datetime.now()
        self.paginas_procesadas = 0
        self.items_scrapeados = 0
        self.errores = 0
        self.reintentos = 0
    
    def incrementar_paginas(self, cantidad=1):
        """
        Incrementa contador de páginas procesadas
        
        Args:
            cantidad: Número de páginas a incrementar
        """
        self.paginas_procesadas += cantidad
    
    def incrementar_items(self, cantidad=1):
        """
        Incrementa contador de items scrapeados
        
        Args:
            cantidad: Número de items a incrementar
        """
        self.items_scrapeados += cantidad
    
    def incrementar_errores(self, cantidad=1):
        """
        Incrementa contador de errores
        
        Args:
            cantidad: Número de errores a incrementar
        """
        self.errores += cantidad
    
    def incrementar_reintentos(self, cantidad=1):
        """
        Incrementa contador de reintentos
        
        Args:
            cantidad: Número de reintentos a incrementar
        """
        self.reintentos += cantidad
    
    def obtener_tiempo_transcurrido(self):
        """
        Retorna tiempo transcurrido desde el inicio
        
        Returns:
            str: Tiempo formateado
        """
        segundos = calcular_tiempo_transcurrido(self.tiempo_inicio)
        return formatear_duracion(segundos)
    
    def obtener_resumen(self):
        """
        Genera diccionario con resumen completo de estadísticas
        
        Returns:
            dict: Diccionario con todas las métricas
        """
        return {
            'tiempo_total': self.obtener_tiempo_transcurrido(),
            'paginas_procesadas': self.paginas_procesadas,
            'compras_scrapeadas': self.items_scrapeados,
            'errores': self.errores,
            'reintentos': self.reintentos,
            'inicio': self.tiempo_inicio.strftime('%Y-%m-%d %H:%M:%S'),
            'fin': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def registrar_resumen_en_log(self, logger):
        """
        Registra resumen de estadísticas en el logger
        
        Args:
            logger: Instancia de logger donde escribir
        """
        resumen = self.obtener_resumen()
        
        logger.info("=" * 50)
        logger.info("RESUMEN DE SCRAPING")
        logger.info("=" * 50)
        
        for clave, valor in resumen.items():
            logger.info(f"{clave}: {valor}")
        
        logger.info("=" * 50)
    
    def calcular_velocidad_scraping(self):
        """
        Calcula velocidad de scraping en items por segundo
        
        Returns:
            float: Items por segundo
        """
        segundos = calcular_tiempo_transcurrido(self.tiempo_inicio)
        
        if segundos == 0:
            return 0.0
        
        return self.items_scrapeados / segundos
    
    def obtener_tasa_error(self):
        """
        Calcula tasa de error como porcentaje
        
        Returns:
            float: Porcentaje de errores
        """
        total_operaciones = self.paginas_procesadas + self.errores
        
        if total_operaciones == 0:
            return 0.0
        
        return (self.errores / total_operaciones) * 100
    
    def reiniciar_estadisticas(self):
        """Reinicia todos los contadores a cero"""
        self.tiempo_inicio = datetime.now()
        self.paginas_procesadas = 0
        self.items_scrapeados = 0
        self.errores = 0
        self.reintentos = 0

