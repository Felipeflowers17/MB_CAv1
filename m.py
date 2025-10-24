"""
Script de uso único para extracción masiva de compras ágiles
Extrae todas las CA entre 2025-10-20 y 2025-10-23 (estado=2)
Aproximadamente 10,000 compras ágiles

Uso:
    python scraper_masivo_unico.py
"""
import json
import time
from datetime import datetime
from playwright.sync_api import sync_playwright, Response


# ============================================
# CONFIGURACIÓN
# ============================================
URL_BASE = "https://buscador.mercadopublico.cl/compra-agil"
PARAMETROS = {
    'date_from': '2025-09-23',
    'date_to': '2025-10-23',
    'status': 2,
    'order_by': 'closing_soon',
    'region': 'all',
    'page_number': 1
}

# Archivo de salida
ARCHIVO_SALIDA = f"compras_agiles_masivas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

# Delays y timeouts
DELAY_ENTRE_PAGINAS = 1  # segundos entre cada página
TIMEOUT_NAVEGACION = 45000  # 45 segundos
MAX_REINTENTOS = 3  # reintentos por página si falla


# ============================================
# CLASE PARA CAPTURAR DATOS DE API
# ============================================
class CapturadorAPI:
    """Captura respuestas JSON de la API"""
    
    def __init__(self):
        self.datos_actuales = None
        self.total_capturado = 0
    
    def interceptar_respuesta(self, response: Response):
        """Callback para interceptar respuestas de la API"""
        url = response.url
        
        # Solo procesar respuestas de la API de compra-agil
        if 'api.buscador.mercadopublico.cl/compra-agil' not in url:
            return
        
        try:
            datos = response.json()
            
            # Validar que tenga la estructura correcta
            if datos.get('success') == 'OK' and 'payload' in datos:
                self.datos_actuales = datos
                
        except Exception as e:
            print(f"  ⚠️ Error al parsear respuesta: {e}")
    
    def obtener_resultados(self):
        """Extrae lista de resultados"""
        if not self.datos_actuales:
            return []
        
        try:
            return self.datos_actuales['payload']['resultados']
        except (KeyError, TypeError):
            return []
    
    def obtener_metadata_paginacion(self):
        """Extrae información de paginación"""
        if not self.datos_actuales:
            return None
        
        try:
            payload = self.datos_actuales['payload']
            return {
                'total_resultados': payload.get('resultCount', 0),
                'total_paginas': payload.get('pageCount', 0),
                'pagina_actual': payload.get('page', 0),
                'tamanio_pagina': payload.get('pageSize', 0)
            }
        except (KeyError, TypeError):
            return None
    
    def limpiar(self):
        """Limpia datos actuales"""
        self.datos_actuales = None


# ============================================
# FUNCIÓN DE NAVEGACIÓN CON REINTENTOS
# ============================================
def navegar_con_reintentos(page, url, capturador, max_reintentos=MAX_REINTENTOS):
    """
    Navega a una URL con reintentos en caso de fallo
    
    Args:
        page: Página de Playwright
        url: URL a navegar
        capturador: Instancia del capturador API
        max_reintentos: Número máximo de reintentos
    
    Returns:
        bool: True si tuvo éxito, False si falló
    """
    for intento in range(1, max_reintentos + 1):
        try:
            capturador.limpiar()
            
            # Estrategia: domcontentloaded es más rápido que networkidle
            page.goto(url, timeout=TIMEOUT_NAVEGACION, wait_until='domcontentloaded')
            
            # Esperar un poco para que la API responda
            page.wait_for_timeout(3000)
            
            # Verificar si obtuvimos datos
            if capturador.obtener_resultados():
                return True
            
            # Si no hay datos, esperar más tiempo
            page.wait_for_timeout(2000)
            
            if capturador.obtener_resultados():
                return True
            
        except Exception as e:
            if intento < max_reintentos:
                print(f"  ⚠️ Intento {intento} falló, reintentando... ({str(e)[:50]})")
                time.sleep(2)
            else:
                print(f"  ❌ Falló después de {max_reintentos} intentos")
                return False
    
    return False


# ============================================
# FUNCIÓN PRINCIPAL DE SCRAPING
# ============================================
def extraer_todas_las_compras():
    """
    Extrae todas las compras ágiles según los filtros
    
    Returns:
        list: Lista con todas las compras extraídas
    """
    print("=" * 70)
    print("EXTRACCIÓN MASIVA DE COMPRAS ÁGILES")
    print("=" * 70)
    print(f"Fecha desde: {PARAMETROS['date_from']}")
    print(f"Fecha hasta: {PARAMETROS['date_to']}")
    print(f"Estado: {PARAMETROS['status']} (Publicadas)")
    print()
    
    tiempo_inicio = datetime.now()
    todas_las_compras = []
    
    with sync_playwright() as p:
        # Iniciar navegador
        print("🌐 Iniciando navegador...")
        browser = p.chromium.launch(
            headless=True,  # Cambiar a False si quieres ver el navegador
            slow_mo=500
        )
        
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            viewport={'width': 1920, 'height': 1080},
            locale='es-CL'
        )
        
        page = context.new_page()
        
        # Crear capturador de API
        capturador = CapturadorAPI()
        page.on('response', capturador.interceptar_respuesta)
        
        try:
            # ========================================
            # PASO 1: OBTENER INFORMACIÓN DE PAGINACIÓN
            # ========================================
            print("📊 Obteniendo información de paginación...")
            
            # Construir URL para página 1
            params_str = '&'.join([f"{k}={v}" for k, v in PARAMETROS.items()])
            url_pagina_1 = f"{URL_BASE}?{params_str}"
            
            # Navegar a página 1 con reintentos
            if not navegar_con_reintentos(page, url_pagina_1, capturador):
                print("❌ ERROR: No se pudo cargar la página 1")
                return []
            
            # Obtener metadata
            metadata = capturador.obtener_metadata_paginacion()
            
            if not metadata:
                print("❌ ERROR: No se pudo obtener información de paginación")
                return []
            
            total_resultados = metadata['total_resultados']
            total_paginas = metadata['total_paginas']
            
            print(f"✅ Total de resultados: {total_resultados:,}")
            print(f"✅ Total de páginas: {total_paginas:,}")
            print()
            
            # Agregar resultados de página 1
            resultados_p1 = capturador.obtener_resultados()
            todas_las_compras.extend(resultados_p1)
            print(f"📄 Página 1/{total_paginas} procesada - {len(resultados_p1)} compras extraídas")
            
            # ========================================
            # PASO 2: SCRAPEAR TODAS LAS PÁGINAS RESTANTES
            # ========================================
            print()
            print("🔄 Iniciando extracción de todas las páginas...")
            print("-" * 70)
            
            for num_pagina in range(2, total_paginas + 1):
                # Delay entre requests
                time.sleep(DELAY_ENTRE_PAGINAS)
                
                # Actualizar número de página en parámetros
                PARAMETROS['page_number'] = num_pagina
                params_str = '&'.join([f"{k}={v}" for k, v in PARAMETROS.items()])
                url_pagina = f"{URL_BASE}?{params_str}"
                
                # Navegar con reintentos
                if navegar_con_reintentos(page, url_pagina, capturador):
                    # Extraer resultados
                    resultados = capturador.obtener_resultados()
                    
                    if resultados:
                        todas_las_compras.extend(resultados)
                        
                        # Mostrar progreso cada 10 páginas o en la última
                        if num_pagina % 10 == 0 or num_pagina == total_paginas:
                            porcentaje = (num_pagina / total_paginas) * 100
                            print(f"📄 Página {num_pagina}/{total_paginas} ({porcentaje:.1f}%) - "
                                  f"Total acumulado: {len(todas_las_compras):,} compras")
                    else:
                        print(f"  ⚠️ Página {num_pagina}: Sin resultados")
                else:
                    print(f"  ❌ Página {num_pagina}: No se pudo cargar")

            
            print("-" * 70)
            print()
            
        except KeyboardInterrupt:
            print("\n\n⚠️ Proceso interrumpido por el usuario")
            print(f"Compras extraídas hasta el momento: {len(todas_las_compras):,}")
        
        except Exception as e:
            print(f"\n❌ ERROR CRÍTICO: {e}")
        
        finally:
            # Cerrar navegador
            context.close()
            browser.close()
            print("✅ Navegador cerrado")
    
    # ========================================
    # ESTADÍSTICAS FINALES
    # ========================================
    tiempo_total = (datetime.now() - tiempo_inicio).total_seconds()
    minutos = int(tiempo_total // 60)
    segundos = int(tiempo_total % 60)
    
    print()
    print("=" * 70)
    print("EXTRACCIÓN COMPLETADA")
    print("=" * 70)
    print(f"✅ Total compras extraídas: {len(todas_las_compras):,}")
    print(f"⏱️  Tiempo total: {minutos}m {segundos}s")
    
    if len(todas_las_compras) > 0:
        velocidad = len(todas_las_compras) / tiempo_total
        print(f"⚡ Velocidad promedio: {velocidad:.1f} compras/segundo")
    
    return todas_las_compras


# ============================================
# FUNCIÓN PARA GUARDAR JSON
# ============================================
def guardar_compras_json(compras):
    """
    Guarda las compras en un archivo JSON
    
    Args:
        compras: Lista de compras a guardar
    
    Returns:
        str: Nombre del archivo guardado
    """
    print()
    print("💾 Guardando resultados en JSON...")
    
    try:
        with open(ARCHIVO_SALIDA, 'w', encoding='utf-8') as f:
            json.dump(compras, f, ensure_ascii=False, indent=2)
        
        # Obtener tamaño del archivo
        import os
        tamanio_kb = os.path.getsize(ARCHIVO_SALIDA) / 1024
        tamanio_mb = tamanio_kb / 1024
        
        print(f"✅ Archivo guardado exitosamente")
        print(f"📁 Nombre: {ARCHIVO_SALIDA}")
        print(f"📊 Tamaño: {tamanio_mb:.2f} MB ({tamanio_kb:.0f} KB)")
        
        return ARCHIVO_SALIDA
        
    except Exception as e:
        print(f"❌ ERROR al guardar archivo: {e}")
        return None


# ============================================
# FUNCIÓN PARA MOSTRAR PREVIEW DE DATOS
# ============================================
def mostrar_preview_datos(compras, cantidad=3):
    """
    Muestra preview de las primeras compras
    
    Args:
        compras: Lista de compras
        cantidad: Cantidad de ejemplos a mostrar
    """
    if not compras:
        return
    
    print()
    print("=" * 70)
    print("PREVIEW DE DATOS EXTRAÍDOS")
    print("=" * 70)
    
    for i, compra in enumerate(compras[:cantidad], 1):
        print(f"\n📋 Compra {i}:")
        print(f"  • ID: {compra.get('id', 'N/A')}")
        print(f"  • Código: {compra.get('codigo', 'N/A')}")
        print(f"  • Nombre: {compra.get('nombre', 'N/A')[:60]}...")
        print(f"  • Organismo: {compra.get('organismo', 'N/A')[:50]}...")
        print(f"  • Estado: {compra.get('estado', 'N/A')}")
        print(f"  • Monto disponible: ${compra.get('monto_disponible', 0):,}")
        print(f"  • Fecha publicación: {compra.get('fecha_publicacion', 'N/A')}")
        print(f"  • Fecha cierre: {compra.get('fecha_cierre', 'N/A')}")
    
    print()
    print(f"... y {len(compras) - cantidad:,} compras más")
    print("=" * 70)


# ============================================
# MAIN
# ============================================
def main():
    """Función principal"""
    print()
    print("⚠️  ADVERTENCIA: Este script hará requests reales a Mercado Público")
    print("⏱️  Duración estimada: 15-30 minutos (dependiendo de la conexión)")
    print()
    
    respuesta = input("¿Deseas continuar? (s/N): ").lower().strip()
    
    if respuesta != 's':
        print("❌ Operación cancelada")
        return 1
    
    print()
    
    try:
        # Extraer compras
        compras = extraer_todas_las_compras()
        
        if not compras:
            print("❌ No se extrajeron compras")
            return 1
        
        # Guardar en JSON
        archivo = guardar_compras_json(compras)
        
        if not archivo:
            print("❌ Error al guardar archivo")
            return 1
        
        # Mostrar preview
        mostrar_preview_datos(compras)
        
        print()
        print("🎉 PROCESO COMPLETADO EXITOSAMENTE")
        print()
        
        return 0
        
    except KeyboardInterrupt:
        print("\n\n❌ Proceso interrumpido por el usuario")
        return 1
    
    except Exception as e:
        print(f"\n❌ ERROR CRÍTICO: {e}")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())