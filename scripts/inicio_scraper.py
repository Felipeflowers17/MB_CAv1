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

from src.scraper.list_scraper import ScraperListado
from src.scraper.filters import FiltradorCompras
from config.config import FECHA_SCRAPING


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
        print("[1/2] Extrayendo listado completo...", end=" ", flush=True)
        
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
        # PASO 2: FILTRADO POR ESTADO_CONVOCATORIA
        # ========================================
        print("[2/2] Filtrando por segundo llamado...", end=" ", flush=True)
        
        tiempo_paso2_inicio = datetime.now()
        
        filtrador = FiltradorCompras()
        compras_filtradas = filtrador.filtrar_segundo_llamado(compras_completas)
        estadisticas = filtrador.generar_estadisticas(compras_completas, compras_filtradas)
        
        # Guardar resultados
        archivo_filtrado = None
        if compras_filtradas:
            archivo_filtrado = filtrador.guardar_compras_filtradas(compras_filtradas)
        
        tiempo_paso2 = (datetime.now() - tiempo_paso2_inicio).total_seconds()
        
        print(f"OK")
        print(f"    Segundo llamado encontrado: {len(compras_filtradas)}")
        print(f"    Tiempo: {tiempo_paso2:.2f}s")
        
        # ========================================
        # RESUMEN FINAL
        # ========================================
        tiempo_total = (datetime.now() - tiempo_inicio).total_seconds()
        minutos = int(tiempo_total // 60)
        segundos = int(tiempo_total % 60)
        tiempo_formateado = f"{minutos}m {segundos}s" if minutos > 0 else f"{segundos}s"
        
        print("-" * 50)
        print("RESUMEN:")
        print(f"  Total compras del día: {estadisticas['total_compras']}")
        print(f"  Compras segundo llamado: {estadisticas['segundo_llamado']}")
        print(f"  Compras primer llamado: {estadisticas['primer_llamado']}")
        print(f"  Tasa segundo llamado: {estadisticas['porcentaje_segundo_llamado']:.1f}%")
        print(f"  Tiempo total: {tiempo_formateado}")
        print(f"  Velocidad promedio: {len(compras_completas)/tiempo_total:.1f} compras/s")
        print()
        print("ARCHIVOS GENERADOS:")
        print(f"  1. {Path(archivo_completo).name}")
        if archivo_filtrado:
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