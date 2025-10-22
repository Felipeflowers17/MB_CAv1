"""
Script para análisis de organismos
Extrae lista única de organismos del día para análisis
"""
import sys
from pathlib import Path
from datetime import datetime

# Agregar directorio raíz al path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from src.scraper.list_scraper import ScraperListado
from src.scraper.utilidades.helpers import guardar_json, obtener_timestamp
from config.config import FECHA_SCRAPING


def extraer_organismos_unicos(compras):
    """
    Extrae lista única de organismos con conteo de compras
    
    Args:
        compras: Lista de compras
    
    Returns:
        dict: Diccionario con organismos y estadísticas
    """
    # Diccionario para contar compras por organismo
    conteo_organismos = {}
    
    for compra in compras:
        organismo = compra.get('organismo', 'Sin organismo')
        conteo_organismos[organismo] = conteo_organismos.get(organismo, 0) + 1
    
    # Ordenar por cantidad de compras (mayor a menor)
    organismos_ordenados = sorted(
        conteo_organismos.items(),
        key=lambda x: x[1],
        reverse=True
    )
    
    return {
        'fecha_analisis': FECHA_SCRAPING,
        'total_compras': len(compras),
        'total_organismos_unicos': len(conteo_organismos),
        'organismos': [
            {
                'nombre': org,
                'cantidad_compras': cant,
                'porcentaje': round((cant / len(compras) * 100), 2)
            }
            for org, cant in organismos_ordenados
        ]
    }


def main():
    """
    Ejecuta análisis de organismos
    
    Returns:
        int: 0 si éxito, 1 si error
    """
    tiempo_inicio = datetime.now()
    
    print(f"Analisis de Organismos - {FECHA_SCRAPING}")
    print("-" * 50)
    
    try:
        # ========================================
        # EXTRACCIÓN DE COMPRAS
        # ========================================
        print("[1/2] Extrayendo compras del día...", end=" ", flush=True)
        
        scraper = ScraperListado(max_paginas=None)
        compras, _ = scraper.ejecutar(guardar=False)
        
        if not compras:
            print("ERROR")
            print("No se obtuvieron compras")
            return 1
        
        tiempo_extraccion = (datetime.now() - tiempo_inicio).total_seconds()
        
        print(f"OK")
        print(f"    Compras extraídas: {len(compras)}")
        print(f"    Tiempo: {int(tiempo_extraccion)}s")
        
        # ========================================
        # ANÁLISIS DE ORGANISMOS
        # ========================================
        print("[2/2] Analizando organismos...", end=" ", flush=True)
        
        analisis = extraer_organismos_unicos(compras)
        
        # Guardar análisis en JSON
        timestamp = obtener_timestamp()
        nombre_archivo = f"analisis_organismos_{timestamp}.json"
        ruta_analisis = guardar_json(analisis, nombre_archivo)
        
        print(f"OK")
        
        # ========================================
        # RESUMEN
        # ========================================
        tiempo_total = (datetime.now() - tiempo_inicio).total_seconds()
        
        print("-" * 50)
        print("RESUMEN:")
        print(f"  Total compras analizadas: {analisis['total_compras']}")
        print(f"  Organismos únicos: {analisis['total_organismos_unicos']}")
        print(f"  Tiempo total: {int(tiempo_total)}s")
        print()
        print("TOP 10 ORGANISMOS CON MÁS COMPRAS:")
        
        for i, org_data in enumerate(analisis['organismos'][:10], 1):
            nombre = org_data['nombre']
            cantidad = org_data['cantidad_compras']
            porcentaje = org_data['porcentaje']
            
            # Truncar nombre si es muy largo
            nombre_corto = nombre[:50] + "..." if len(nombre) > 50 else nombre
            
            print(f"  {i:2d}. {nombre_corto:50s} {cantidad:3d} ({porcentaje:5.2f}%)")
        
        print()
        print(f"ARCHIVO GENERADO: {Path(ruta_analisis).name}")
        print(f"Ubicación: data/raw/")
        print()
        print("Siguiente paso:")
        print("  1. Revisa el archivo JSON completo")
        print("  2. Identifica organismos de interés")
        print("  3. Actualiza config/filtros_config.py con los organismos seleccionados")
        
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
