"""
Manejador de respuestas de la API de Mercado Público
Intercepta y procesa respuestas JSON
"""
from playwright.sync_api import Response
from .utilidades.helpers import validar_respuesta_api


class ManejadorAPI:
    """
    Clase para interceptar y procesar respuestas de la API
    
    Atributos:
        logger: Logger para registrar eventos
        datos_respuesta_actual: Última respuesta capturada
    """
    
    def __init__(self, logger):
    
    #Inicializa el manejador de API
    
        self.logger = logger
        self.datos_respuesta_actual = None
    
    def interceptar_respuesta(self, response: Response):
        
        #Intercepta respuestas de la API (callback de Playwright)
        #Solo procesa respuestas de la API de compra-agil

        url = response.url # Obtener URL de la respuesta
        
        # Solo procesar respuestas de la API de compra-agil
        if 'api.buscador.mercadopublico.cl/compra-agil' not in url:
            return
        
        try:
            # Intentar parsear como JSON
            datos_json = response.json()
            
            # Validar estructura
            if validar_respuesta_api(datos_json):
                self.datos_respuesta_actual = datos_json
                self.logger.debug("Respuesta API capturada exitosamente")
            else:
                self.logger.warning(f"Respuesta con estructura inválida desde: {url}")
                
        except Exception as e:
            self.logger.error(f"ERROR al parsear respuesta JSON: {e}")
    
    def obtener_respuesta_actual(self):
        
        #Obtiene la última respuesta capturada
        return self.datos_respuesta_actual
    
    def limpiar_respuesta_actual(self):
        """Limpia/resetea la respuesta actual"""
        self.datos_respuesta_actual = None
    
    def hay_respuesta_disponible(self):
        """
        Verifica si hay respuesta disponible
        True si hay respuesta, False si no
        """
        return self.datos_respuesta_actual is not None
    
    def extraer_resultados(self):
        """
        Extrae lista de resultados de la respuesta actual
        Lista de compras o lista vacía
        """
        if not self.datos_respuesta_actual:
            return []
        
        try:
            return self.datos_respuesta_actual['payload']['resultados']
        except (KeyError, TypeError) as e:
            self.logger.error(f"ERROR al extraer resultados: {e}")
            return []
    
    def extraer_metadata_paginacion(self):
        
        #Extrae información de paginación de la respuesta
        metadata_default = {
            'resultCount': 0,
            'pageCount': 0,
            'page': 0,
            'pageSize': 0
        }
        
        if not self.datos_respuesta_actual:
            return metadata_default
        
        try:
            payload = self.datos_respuesta_actual['payload']
            
            return {
                'resultCount': payload.get('resultCount', 0),
                'pageCount': payload.get('pageCount', 0),
                'page': payload.get('page', 0),
                'pageSize': payload.get('pageSize', 0)
            }
            
        except (KeyError, TypeError) as e:
            self.logger.error(f"ERROR al extraer metadata: {e}")
            return metadata_default
    
    def verificar_respuesta_exitosa(self):
        """
        Verifica si la respuesta indica éxito
        True si success == "OK", False si no
        """
        if not self.datos_respuesta_actual:
            return False
        
        try:
            return self.datos_respuesta_actual.get('success') == 'OK'
        except (AttributeError, TypeError):
            return False