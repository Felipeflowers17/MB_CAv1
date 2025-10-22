"""
Scraper de detalles de fichas individuales
Extrae información completa de cada compra ágil
"""
from datetime import datetime
from playwright.sync_api import Page, Response
from .utilidades.logger import configurar_logger
from .utilidades.helpers import (
    guardar_json,
    obtener_timestamp,
    aplicar_delay
)
from .utilidades.stats import EstadisticasScraper
from .url_builder import construir_url_ficha
from config.config import (
    DELAY_ENTRE_REQUESTS,
    TIMEOUT_REQUESTS
)


class ScraperDetalles:
    
    #Scraper de fichas individuales de compras ágiles
    
    
    
    def __init__(self):
        #Inicializa el scraper de detalles
        # Logger con archivo por fecha
        nombre_log = f'scraper_detalles_{datetime.now().strftime("%Y%m%d")}.log'
        self.logger = configurar_logger('scraper_detalles', nombre_log)
        
        # Estadísticas
        self.estadisticas = EstadisticasScraper()
        
        # Variables para datos capturados
        self.datos_ficha_actual = None
        self.datos_historial_actual = None
    
    def interceptar_respuesta(self, response: Response):
        
        #Handler para interceptar respuestas de APIs de ficha e historial
        
        
        url = response.url
        
        try:
            # Capturar respuesta de ficha
            if 'action=ficha' in url:
                datos = response.json()
                if datos.get('success') == 'OK':
                    self.datos_ficha_actual = datos.get('payload')
                    self.logger.debug("Ficha capturada")
            
            # Capturar respuesta de historial
            elif 'action=historial' in url:
                datos = response.json()
                if datos.get('success') == 'OK':
                    self.datos_historial_actual = datos.get('payload')
                    self.logger.debug("Historial capturado")
                    
        except Exception as e:
            self.logger.error(f"ERROR al parsear respuesta: {e}")
    
    def scrapear_detalle_individual(self, page: Page, codigo_compra):
        
        #Scrapea el detalle completo de una compra específica
        #Retorna: Diccionario con datos completos o None
        
        try:
            # Resetear datos capturados
            self.datos_ficha_actual = None
            self.datos_historial_actual = None
            
            # Construir URL
            url_ficha = construir_url_ficha(codigo_compra)
            
            # Log de navegación
            self.logger.info(f"Obteniendo detalle: {codigo_compra}")
            
            # Navegar a la ficha
            page.goto(url_ficha, timeout=TIMEOUT_REQUESTS * 1000, wait_until='networkidle')
            
            # Esperar carga de APIs
            page.wait_for_timeout(3000)
            
            # Validar captura de ficha
            if not self.datos_ficha_actual:
                self.logger.warning(f"No se capturó ficha: {codigo_compra}")
                self.estadisticas.incrementar_errores()
                return None
            
            # Construir objeto con datos completos
            detalle_completo = {
                'codigo': codigo_compra,
                'ficha': self.datos_ficha_actual,
                'historial': self.datos_historial_actual if self.datos_historial_actual else [],
                'fecha_scraping_detalle': datetime.now().isoformat()
            }
            
            # Actualizar estadísticas
            self.estadisticas.incrementar_items()
            
            return detalle_completo
            
        except Exception as e:
            self.logger.error(f"ERROR al scrapear detalle {codigo_compra}: {e}")
            self.estadisticas.incrementar_errores()
            return None
    
    def scrapear_multiples_detalles(self, page: Page, compras, max_compras=None):
        
        #Scrapea detalles de múltiples compras
        #Retorna: Lista de compras con detalles completos
        
        # Log de inicio
        self.logger.info("=" * 60)
        self.logger.info("INICIANDO SCRAPING DE DETALLES")
        self.logger.info("=" * 60)
        
        # Determinar cantidad a procesar
        total_compras = len(compras)
        if max_compras:
            compras_a_procesar = min(total_compras, max_compras)
        else:
            compras_a_procesar = total_compras
        
        self.logger.info(f"Total compras: {total_compras}")
        self.logger.info(f"Compras a procesar: {compras_a_procesar}")
        self.logger.info("-" * 60)
        
        # Lista para resultados
        compras_con_detalle = []
        
        # Procesar cada compra
        for indice, compra in enumerate(compras[:compras_a_procesar], 1):
            # Obtener código
            codigo = compra.get('codigo')
            
            if not codigo:
                self.logger.warning(f"Compra sin código en índice {indice}")
                continue
            
            # Aplicar delay (excepto primera)
            if indice > 1:
                aplicar_delay(DELAY_ENTRE_REQUESTS)
            
            # Obtener detalle
            detalle = self.scrapear_detalle_individual(page, codigo)
            
            # Combinar con datos originales
            if detalle:
                compra_completa = {
                    **compra,
                    'detalle': detalle
                }
                compras_con_detalle.append(compra_completa)
                
                self.logger.info(
                    f"Progreso: {indice}/{compras_a_procesar} | "
                    f"Exitosos: {len(compras_con_detalle)}"
                )
            else:
                self.logger.warning(f"No se obtuvo detalle: {codigo}")
                compras_con_detalle.append(compra)
        
        # Log final
        self.logger.info("-" * 60)
        self.logger.info("SCRAPING DE DETALLES COMPLETADO")
        self.logger.info(f"Compras procesadas: {indice}")
        self.logger.info(f"Detalles obtenidos: {len(compras_con_detalle)}")
        self.logger.info("=" * 60)
        
        return compras_con_detalle
    
    def guardar_resultados(self, compras_con_detalle, nombre_archivo=None):
        
        #Guarda resultados con detalles en JSON
        #Retorna: Ruta del archivo guardado
        
        if not nombre_archivo:
            timestamp = obtener_timestamp()
            nombre_archivo = f"compras_detalladas_{timestamp}.json"
        
        ruta = guardar_json(compras_con_detalle, nombre_archivo)
        self.logger.info(f"Resultados guardados en: {ruta}")
        
        return str(ruta)