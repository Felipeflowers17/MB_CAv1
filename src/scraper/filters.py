"""
Sistema de filtrado de compras ágiles
Detecta compras con segundo llamado usando método híbrido
"""
from datetime import datetime
from .utilidades.logger import configurar_logger
from .utilidades.helpers import (
    guardar_json,
    obtener_timestamp
)
from config.filters_config import KEYWORDS_SEGUNDO_LLAMADO


class FiltradorCompras:
    
    #Filtrador de compras ágiles por segundo llamado
    #Usa método híbrido: detección por texto + validación por historial
    
    
    
    def __init__(self):
        #Inicializa el filtrador
        # Logger con archivo por fecha
        nombre_log = f'filtrador_{datetime.now().strftime("%Y%m%d")}.log'
        self.logger = configurar_logger('filtrador', nombre_log)
        
        # Contadores
        self.total_procesadas = 0
        self.total_relevantes = 0
    
    def detectar_segundo_llamado_por_texto(self, compra):
        
        #Detecta posible segundo llamado buscando keywords en nombre
        #Método rápido para pre-filtrado
        
        #Retorna: (es_posible_segundo_llamado: bool, keywords_encontradas: list)
        
        # Obtener nombre de la compra
        nombre = compra.get('nombre', '').lower()
        
        if not nombre:
            return False, []
        
        # Buscar cada keyword
        keywords_encontradas = []
        for keyword in KEYWORDS_SEGUNDO_LLAMADO:
            if keyword.lower() in nombre:
                keywords_encontradas.append(keyword)
        
        # Si encontró al menos una keyword
        es_posible = len(keywords_encontradas) > 0
        
        return es_posible, keywords_encontradas
    
    def validar_segundo_llamado_por_historial(self, compra):
        
        #Valida segundo llamado revisando el historial de la compra
        #Método preciso que requiere datos de detalles
        #Retorna: (es_segundo_llamado: bool, cantidad_publicaciones: int)
        
        try:
            # Verificar que tenga detalles
            if 'detalle' not in compra:
                return False, 0
            
            # Obtener historial
            historial = compra['detalle'].get('historial', [])
            
            # Si no hay historial o está vacío
            if not historial or not isinstance(historial, list):
                return False, 0
            
            # Contar publicaciones en el historial
            # Normalmente el historial tiene una entrada por cada publicación
            cantidad_publicaciones = len(historial)
            
            # Si hay más de 1 publicación, es segundo llamado (o más)
            es_segundo_llamado = cantidad_publicaciones > 1
            
            return es_segundo_llamado, cantidad_publicaciones
            
        except Exception as e:
            self.logger.error(f"ERROR al validar historial: {e}")
            return False, 0
    
    def pre_filtrar_por_texto(self, compras):
        
        #PASO 1: Pre-filtrado rápido por texto
        #Marca compras como "posible segundo llamado"
        #Retorna: Lista de compras con campo 'posible_segundo_llamado'

        self.logger.info("=" * 60)
        self.logger.info("PASO 1: PRE-FILTRADO POR TEXTO")
        self.logger.info("=" * 60)
        self.logger.info(f"Total compras a analizar: {len(compras)}")
        
        compras_marcadas = []
        contador_posibles = 0
        
        for compra in compras:
            # Detectar por texto
            es_posible, keywords = self.detectar_segundo_llamado_por_texto(compra)
            
            # Agregar metadata
            compra_marcada = {
                **compra,
                'metadata_filtrado': {
                    'posible_segundo_llamado': es_posible,
                    'keywords_encontradas': keywords,
                    'fecha_pre_filtrado': datetime.now().isoformat()
                }
            }
            
            compras_marcadas.append(compra_marcada)
            
            if es_posible:
                contador_posibles += 1
        
        self.logger.info(f"Compras marcadas como posible segundo llamado: {contador_posibles}")
        self.logger.info(f"Tasa de pre-filtrado: {(contador_posibles/len(compras)*100):.1f}%")
        
        return compras_marcadas
    
    def filtrar_posibles_segundo_llamado(self, compras_marcadas):
        
        #Extrae solo las compras marcadas como "posible segundo llamado"
        #Estas son las que se enviarán a scraping de detalles
        #Retorna lista de compras posibles
        
        posibles = [
            c for c in compras_marcadas 
            if c.get('metadata_filtrado', {}).get('posible_segundo_llamado', False)
        ]
        
        self.logger.info(f"Compras a verificar con detalles: {len(posibles)}")
        
        return posibles
    
    def validar_con_historial(self, compras_con_detalles):
        
        #Validación precisa con historial
        #Confirma cuáles son realmente segundo llamado
        #Retorna: Lista de compras confirmadas como segundo llamado
        
        self.logger.info("PASO 2: VALIDACIÓN POR HISTORIAL")
        self.logger.info(f"Total compras a validar: {len(compras_con_detalles)}")
        
        compras_confirmadas = []
        
        for compra in compras_con_detalles:
            # Validar con historial
            es_segundo_llamado, num_publicaciones = self.validar_segundo_llamado_por_historial(compra)
            
            # Actualizar metadata
            metadata = compra.get('metadata_filtrado', {})
            metadata.update({
                'es_segundo_llamado_confirmado': es_segundo_llamado,
                'cantidad_publicaciones': num_publicaciones,
                'fecha_validacion': datetime.now().isoformat()
            })
            
            compra['metadata_filtrado'] = metadata
            
            # Si está confirmado, agregar a lista final
            if es_segundo_llamado:
                compras_confirmadas.append(compra)
                self.total_relevantes += 1
            
            self.total_procesadas += 1
        
        self.logger.info(f"Compras confirmadas como segundo llamado: {len(compras_confirmadas)}")
        
        if self.total_procesadas > 0:
            tasa_confirmacion = (self.total_relevantes / self.total_procesadas * 100)
            self.logger.info(f"Tasa de confirmación: {tasa_confirmacion:.1f}%")
        
        return compras_confirmadas
    
    def generar_estadisticas(self, compras_filtradas):
        #Genera estadísticas básicas de las compras filtradas
        if not compras_filtradas:
            return {}
        
        # Contar por cantidad de publicaciones
        conteo_publicaciones = {}
        
        for compra in compras_filtradas:
            num_pub = compra.get('metadata_filtrado', {}).get('cantidad_publicaciones', 0)
            conteo_publicaciones[num_pub] = conteo_publicaciones.get(num_pub, 0) + 1
        
        estadisticas = {
            'total_compras_segundo_llamado': len(compras_filtradas),
            'distribucion_publicaciones': conteo_publicaciones
        }
        
        return estadisticas
    
    def registrar_estadisticas(self, estadisticas):
        #registra estadísticas en el log
        self.logger.info("ESTADÍSTICAS DE FILTRADO")
        
        total = estadisticas.get('total_compras_segundo_llamado', 0)
        self.logger.info(f"Total compras con segundo llamado: {total}")
        
        distribucion = estadisticas.get('distribucion_publicaciones', {})
        if distribucion:
            self.logger.info("Distribución por cantidad de publicaciones:")
            for num_pub, cantidad in sorted(distribucion.items()):
                self.logger.info(f"  {num_pub} publicaciones: {cantidad} compras")
        
        self.logger.info("=" * 60)
    
    def guardar_compras_filtradas(self, compras_filtradas, nombre_archivo=None):
        #guarda compras filtradas en JSON
        if not nombre_archivo:
            timestamp = obtener_timestamp()
            nombre_archivo = f"compras_filtradas_{timestamp}.json"
        
        ruta = guardar_json(compras_filtradas, nombre_archivo)
        self.logger.info(f"Compras filtradas guardadas en: {ruta}")
        
        return str(ruta)


def filtrar_y_guardar(compras_con_detalles, guardar=True):
    #Función principal para filtrar compras con segundo llamado
    #Usa método híbrido: pre-filtrado por texto + validación por historial
    
    # Crear instancia del filtrador
    filtrador = FiltradorCompras()
    
    # Validar con historial
    compras_filtradas = filtrador.validar_con_historial(compras_con_detalles)
    
    # Generar y registrar estadísticas
    estadisticas = filtrador.generar_estadisticas(compras_filtradas)
    filtrador.registrar_estadisticas(estadisticas)
    
    # Guardar si se solicita
    ruta_archivo = None
    if guardar and compras_filtradas:
        ruta_archivo = filtrador.guardar_compras_filtradas(compras_filtradas)
    
    return compras_filtradas, ruta_archivo