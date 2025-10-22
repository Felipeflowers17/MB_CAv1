"""
Scraper principal de listado de compras ágiles
Extrae todas las CA del día usando Playwright
"""
from datetime import datetime
from playwright.sync_api import sync_playwright
from .utilidades.logger import configurar_logger
from .utilidades.helpers import (
    guardar_json,
    obtener_timestamp,
    aplicar_delay
)
from .utilidades.stats import EstadisticasScraper
from .api_handler import ManejadorAPI
from .url_builder import construir_url_listado
from config.config import (
    FECHA_SCRAPING,
    MODO_HEADLESS,
    TIMEOUT_REQUESTS,
    DELAY_ENTRE_REQUESTS
)


class ScraperListado:
    
    
    def __init__(self, max_paginas=None):
        #inicializa el scraper de listado
        # Configuración
        self.max_paginas = max_paginas
        
        # Logger con archivo por fecha
        nombre_log = f'scraper_listado_{datetime.now().strftime("%Y%m%d")}.log'
        self.logger = configurar_logger('scraper_listado', nombre_log)
        
        # Estadísticas
        self.estadisticas = EstadisticasScraper()
        
        # Lista de compras
        self.compras = []
    
    def scrapear_pagina(self, page, manejador_api, numero_pagina):
        
        #Scrapea una página específica del listado
        #retorna:Datos de la página o None si falla
        
        try:
            # Limpiar respuesta anterior
            manejador_api.limpiar_respuesta_actual()
            
            # Construir URL
            url = construir_url_listado(numero_pagina)
            
            # Log de navegación
            self.logger.info(f"Navegando a página {numero_pagina}")
            
            # Navegar y esperar carga completa
            page.goto(url, timeout=TIMEOUT_REQUESTS * 1000, wait_until='networkidle')
            
            # Esperar captura de respuesta
            page.wait_for_timeout(2000)
            
            # Verificar captura
            if manejador_api.hay_respuesta_disponible():
                datos = manejador_api.obtener_respuesta_actual()
                resultados = manejador_api.extraer_resultados()
                
                # Actualizar estadísticas
                self.estadisticas.incrementar_paginas()
                self.estadisticas.incrementar_items(len(resultados))
                
                self.logger.info(f"Página {numero_pagina} procesada: {len(resultados)} compras")
                return datos
            else:
                self.logger.error(f"ERROR: No se capturó respuesta en página {numero_pagina}")
                self.estadisticas.incrementar_errores()
                return None
                
        except Exception as e:
            self.logger.error(f"ERROR al scrapear página {numero_pagina}: {e}")
            self.estadisticas.incrementar_errores()
            return None
    
    def scrapear_todas_las_paginas(self):
        
        # Log de inicio
        self.logger.info("INICIANDO SCRAPING DE LISTADO")
        self.logger.info(f"Fecha: {FECHA_SCRAPING}")
        self.logger.info(f"Límite páginas: {self.max_paginas if self.max_paginas else 'Sin límite'}")

        
        # Iniciar Playwright
        with sync_playwright() as p:
            # Lanzar navegador
            self.logger.info("Iniciando navegador...")
            browser = p.chromium.launch(
                headless=MODO_HEADLESS,
                slow_mo=500
            )
            
            # Crear contexto
            context = browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                viewport={'width': 1920, 'height': 1080},
                locale='es-CL'
            )
            
            # Crear página
            page = context.new_page()
            
            # Crear manejador de API
            manejador_api = ManejadorAPI(self.logger)
            
            # Configurar interceptor
            page.on('response', manejador_api.interceptar_respuesta)
            
            try:
                # Primera página (obtener metadata de paginación)
                self.logger.info("Obteniendo información de paginación...")
                datos_pagina_1 = self.scrapear_pagina(page, manejador_api, 1)
                
                if not datos_pagina_1:
                    self.logger.error("ERROR: No se pudo obtener primera página")
                    return []
                
                # Extraer metadata
                metadata = manejador_api.extraer_metadata_paginacion()
                total_paginas = metadata['pageCount']
                total_resultados = metadata['resultCount']
                
                self.logger.info(f"Total de resultados: {total_resultados}")
                self.logger.info(f"Total de páginas: {total_paginas}")
                
                # Agregar resultados de página 1
                resultados_p1 = manejador_api.extraer_resultados()
                self.compras.extend(resultados_p1)
                
                # Determinar páginas a procesar
                if self.max_paginas:
                    paginas_a_procesar = min(total_paginas, self.max_paginas)
                else:
                    paginas_a_procesar = total_paginas
                
                self.logger.info(f"Páginas a procesar: {paginas_a_procesar}")
                self.logger.info("-" * 60)
                
                # Scrapear páginas restantes (desde 2)
                for num_pagina in range(2, paginas_a_procesar + 1):
                    # Aplicar delay
                    aplicar_delay(DELAY_ENTRE_REQUESTS)
                    
                    # Scrapear página
                    datos_pagina = self.scrapear_pagina(page, manejador_api, num_pagina)
                    
                    if datos_pagina:
                        resultados = manejador_api.extraer_resultados()
                        self.compras.extend(resultados)
                        
                        self.logger.info(
                            f"Progreso: {num_pagina}/{paginas_a_procesar} | "
                            f"Total compras: {len(self.compras)}"
                        )
                    else:
                        self.logger.warning(f"Saltando página {num_pagina} por error")
                
                # Log final
                self.logger.info("-" * 60)
                self.logger.info(f"Scraping completado: {len(self.compras)} compras")
                
            except Exception as e:
                self.logger.error(f"ERROR crítico durante scraping: {e}")
            
            finally:
                # Cerrar navegador
                context.close()
                browser.close()
                self.logger.info("Navegador cerrado")
        
        return self.compras
    
    def guardar_resultados(self, nombre_archivo=None):
        #Guarda resultados en JSON
        #y retorna ruta del archivo guardado
        if not nombre_archivo:
            timestamp = obtener_timestamp()
            nombre_archivo = f"compras_completas_{timestamp}.json"
        
        ruta = guardar_json(self.compras, nombre_archivo)
        self.logger.info(f"Resultados guardados en: {ruta}")
        
        return str(ruta)
    
    def ejecutar(self, guardar=True):
        
        #Ejecuta el scraping completo
        
        try:
            # Scrapear
            compras = self.scrapear_todas_las_paginas()
            
            # Guardar si se solicita
            ruta_archivo = None
            if guardar and compras:
                ruta_archivo = self.guardar_resultados()
            
            # Registrar estadísticas
            self.estadisticas.registrar_resumen_en_log(self.logger)
            
            return compras, ruta_archivo
            
        except Exception as e:
            self.logger.error(f"ERROR en ejecución: {e}")
            self.estadisticas.registrar_resumen_en_log(self.logger)
            return [], None