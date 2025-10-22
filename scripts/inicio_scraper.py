"""
Script principal de ejecución diaria
Extrae y filtra compras ágiles con segundo llamado
"""
import sys
from pathlib import Path
from datetime import datetime

# Agregar directorio raíz al path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from playwright.sync_api import sync_playwright
from src.scraper.list_scraper import ScraperListado
from src.scraper.detail_scraper import ScraperDetalles
from src.scraper.filters import FiltradorCompras
from config.config import FECHA_SCRAPING, MODO_HEADLESS


def main():
    """
    Ejecuta el proceso completo de scraping y filtrado
    
    Returns:
        int: 0 si éxito, 1 si error
    """
    tiempo_inicio = datetime.now()
    
    print(f"Scraping Mercado Publico - {FECHA_SCRAPING}")
    print("-" * 50)
    
    try:
        # ========================================
        # PASO 1: SCRAPING DE LISTADO COMPLETO
        # ========================================
        print("[1/4] Extrayendo listado completo...", end=" ", flush=True)
        
        scraper_listado = ScraperListado(max_paginas=None)
        compras_completas, archivo_completo = scraper_listado.ejecutar(guardar=True)
        
        if not compras_completas:
            print("ERROR")
            print("No se obtuvieron compras. Revisa logs/scraper/")
            return 1
        
        tiempo_paso1 = (datetime.now() - tiempo_inicio).total_seconds()
        velocidad_paso1 = len(compras_completas) / tiempo_paso1 if tiempo_paso1 > 0 else 0
        
        print(f"OK")
        print(f"    Compras extraídas: {len(compras_completas)}")
        print(f"    Tiempo: {int(tiempo_paso1)}s ({velocidad_paso1:.1f} compras/s)")
        
        # ========================================
        # PASO 2: PRE-FILTRADO POR TEXTO
        # ========================================
        print("[2/4] Pre-filtrando por texto...", end=" ", flush=True)
        
        tiempo_paso2_inicio = datetime.now()
        
        filtrador = FiltradorCompras()
        compras_marcadas = filtrador.pre_filtrar_por_texto(compras_completas)
        compras_posibles = filtrador.filtrar_posibles_segundo_llamado(compras_marcadas)
        
        tiempo_paso2 = (datetime.now() - tiempo_paso2_inicio).total_seconds()
        
        print(f"OK")
        print(f"    Posibles segundo llamado: {len(compras_posibles)}")
        print(f"    Tiempo: {int(tiempo_paso2)}s")
        
        if len(compras_posibles) == 0:
            print("\nNo se encontraron compras con posible segundo llamado")
            print("Proceso finalizado")
            return 0
        
        # ========================================
        # PASO 3: SCRAPING DE DETALLES
        # ========================================
        print(f"[3/4] Obteniendo detalles de {len(compras_posibles)} compras...", end=" ", flush=True)
        
        tiempo_paso3_inicio = datetime.now()
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=MODO_HEADLESS, slow_mo=500)
            context = browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                viewport={'width': 1920, 'height': 1080},
                locale='es-CL'
            )
            page = context.new_page()
            
            scraper_detalles = ScraperDetalles()
            page.on('response', scraper_detalles.interceptar_respuesta)
            
            compras_con_detalles = scraper_detalles.scrapear_multiples_detalles(
                page,
                compras_posibles,
                max_compras=None
            )
            
            browser.close()
        
        tiempo_paso3 = (datetime.now() - tiempo_paso3_inicio).total_seconds()
        velocidad_paso3 = len(compras_con_detalles) / tiempo_paso3 if tiempo_paso3 > 0 else 0
        
        print(f"OK")
        print(f"    Detalles obtenidos: {len(compras_con_detalles)}")
        print(f"    Tiempo: {int(tiempo_paso3)}s ({velocidad_paso3:.2f} compras/s)")
        
        # ========================================
        # PASO 4: VALIDACIÓN CON HISTORIAL
        # ========================================
        print("[4/4] Validando con historial...", end=" ", flush=True)
        
        tiempo_paso4_inicio = datetime.now()
        
        compras_filtradas, archivo_filtrado = filtrador.filtrar_y_guardar(
            compras_con_detalles,
            guardar=True
        )
        
        tiempo_paso4 = (datetime.now() - tiempo_paso4_inicio).total_seconds()
        
        print(f"OK")
        print(f"    Segundo llamado confirmado: {len(compras_filtradas)}")
        print(f"    Tiempo: {int(tiempo_paso4)}s")
        
        # ========================================
        # RESUMEN FINAL
        # ========================================
        tiempo_total = (datetime.now() - tiempo_inicio).total_seconds()
        minutos = int(tiempo_total // 60)
        segundos = int(tiempo_total % 60)
        tiempo_formateado = f"{minutos}m {segundos}s" if minutos > 0 else f"{segundos}s"
        
        print("-" * 50)
        print("RESUMEN:")
        print(f"  Total compras del día: {len(compras_completas)}")
        print(f"  Compras con segundo llamado: {len(compras_filtradas)}")
        print(f"  Tasa de relevancia: {(len(compras_filtradas)/len(compras_completas)*100):.1f}%")
        print(f"  Tiempo total: {tiempo_formateado}")
        print(f"  Velocidad promedio: {len(compras_completas)/tiempo_total:.1f} compras/s")
        print()
        print("ARCHIVOS GENERADOS:")
        print(f"  1. {Path(archivo_completo).name}")
        print(f"  2. {Path(archivo_filtrado).name}")
        print(f"  Ubicación: data/raw/")
        
        return 0
        
    except KeyboardInterrupt:
        print("\nProceso interrumpido por usuario")
        return 1
        
    except Exception as e:
        print(f"\nERROR: {e}")
        print("Revisa logs/scraper/ para más detalles")
        return 1


if __name__ == "__main__":
    codigo_salida = main()
    sys.exit(codigo_salida)