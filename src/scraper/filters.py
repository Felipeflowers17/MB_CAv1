"""
Sistema de filtrado de compras ágiles
Detecta compras con segundo llamado usando campo estado_convocatoria
"""
from datetime import datetime
from .utilidades.logger import configurar_logger
from .utilidades.helpers import (
    guardar_json,
    obtener_timestamp
)


class FiltradorCompras:
    """
    Filtrador de compras ágiles por segundo llamado
    Usa campo estado_convocatoria de la API
    
    estado_convocatoria:
    - 1 = Primer llamado
    - 2 = Segundo llamado
    """
    
    def __init__(self):
        """Inicializa el filtrador"""
        # Logger con archivo por fecha
        nombre_log = f'filtrador_{datetime.now().strftime("%Y%m%d")}.log'
        self.logger = configurar_logger('filtrador', nombre_log)
        
        # Contadores
        self.total_procesadas = 0
        self.total_segundo_llamado = 0
    
    def es_segundo_llamado(self, compra):
        """
        Verifica si una compra es segundo llamado
        
        Args:
            compra: Diccionario con datos de compra
        
        Returns:
            bool: True si es segundo llamado, False si no
        """
        estado = compra.get('estado_convocatoria')
        return estado == 2
    
    def filtrar_segundo_llamado(self, compras):
        """
        Filtra compras que son segundo llamado
        
        Args:
            compras: Lista de compras
        
        Returns:
            list: Lista de compras con segundo llamado
        """
        self.logger.info("=" * 60)
        self.logger.info("INICIANDO FILTRADO POR ESTADO_CONVOCATORIA")
        self.logger.info("=" * 60)
        self.logger.info(f"Total compras a analizar: {len(compras)}")
        
        compras_filtradas = []
        
        for compra in compras:
            self.total_procesadas += 1
            
            # Verificar si es segundo llamado
            if self.es_segundo_llamado(compra):
                # Agregar metadata
                compra_con_metadata = {
                    **compra,
                    'metadata_filtrado': {
                        'es_segundo_llamado': True,
                        'estado_convocatoria': compra.get('estado_convocatoria'),
                        'fecha_filtrado': datetime.now().isoformat()
                    }
                }
                
                compras_filtradas.append(compra_con_metadata)
                self.total_segundo_llamado += 1
        
        self.logger.info(f"Compras con segundo llamado: {len(compras_filtradas)}")
        
        if self.total_procesadas > 0:
            porcentaje = (self.total_segundo_llamado / self.total_procesadas * 100)
            self.logger.info(f"Porcentaje: {porcentaje:.1f}%")
        
        self.logger.info("=" * 60)
        
        return compras_filtradas
    
    def generar_estadisticas(self, compras_totales, compras_filtradas):
        """
        Genera estadísticas del filtrado
        
        Args:
            compras_totales: Lista completa de compras
            compras_filtradas: Lista de compras filtradas
        
        Returns:
            dict: Diccionario con estadísticas
        """
        total = len(compras_totales)
        segundo_llamado = len(compras_filtradas)
        primer_llamado = total - segundo_llamado
        
        porcentaje = (segundo_llamado / total * 100) if total > 0 else 0
        
        estadisticas = {
            'total_compras': total,
            'segundo_llamado': segundo_llamado,
            'primer_llamado': primer_llamado,
            'porcentaje_segundo_llamado': round(porcentaje, 2)
        }
        
        return estadisticas
    
    def registrar_estadisticas(self, estadisticas):
        """
        Registra estadísticas en el log
        
        Args:
            estadisticas: Diccionario con estadísticas
        """
        self.logger.info("ESTADÍSTICAS DE FILTRADO")
        self.logger.info(f"Total compras: {estadisticas['total_compras']}")
        self.logger.info(f"Segundo llamado: {estadisticas['segundo_llamado']}")
        self.logger.info(f"Primer llamado: {estadisticas['primer_llamado']}")
        self.logger.info(f"Porcentaje segundo llamado: {estadisticas['porcentaje_segundo_llamado']}%")
        self.logger.info("=" * 60)
    
    def guardar_compras_filtradas(self, compras_filtradas, nombre_archivo=None):
        """
        Guarda compras filtradas en JSON
        
        Args:
            compras_filtradas: Lista de compras filtradas
            nombre_archivo: Nombre del archivo (opcional)
        
        Returns:
            str: Ruta del archivo guardado
        """
        if not nombre_archivo:
            timestamp = obtener_timestamp()
            nombre_archivo = f"compras_segundo_llamado_{timestamp}.json"
        
        ruta = guardar_json(compras_filtradas, nombre_archivo)
        self.logger.info(f"Compras filtradas guardadas en: {ruta}")
        
        return str(ruta)


def filtrar_y_guardar(compras, guardar=True):
    """
    Función principal para filtrar compras con segundo llamado
    
    Args:
        compras: Lista de compras
        guardar: Si debe guardar el resultado en JSON
    
    Returns:
        tuple: (compras_filtradas, ruta_archivo)
    """
    # Crear instancia del filtrador
    filtrador = FiltradorCompras()
    
    # Filtrar por estado_convocatoria
    compras_filtradas = filtrador.filtrar_segundo_llamado(compras)
    
    # Generar y registrar estadísticas
    estadisticas = filtrador.generar_estadisticas(compras, compras_filtradas)
    filtrador.registrar_estadisticas(estadisticas)
    
    # Guardar si se solicita
    ruta_archivo = None
    if guardar and compras_filtradas:
        ruta_archivo = filtrador.guardar_compras_filtradas(compras_filtradas)
    
    return compras_filtradas, ruta_archivo