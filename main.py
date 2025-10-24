import pandas as pd
import sys
import os
from pathlib import Path

# --- Configuración del Path para importar módulos ---
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

# --- Importaciones del proyecto ---
from src.scraper.list_scraper import ScraperListado
from src.scraper.utilidades.helpers import cargar_json
from src.filters.filter_advanced import FiltradorAvanzado
# Importamos la función 'main' del script de análisis para poder llamarla
from scripts.analizar_organismos import main as analizar_organismos_main

# --- DataFrame Global ---
DF_COMPRAS = pd.DataFrame()

def limpiar_pantalla():
    os.system('cls' if os.name == 'nt' else 'clear')

def esperar_enter():
    input("\nPresione Enter para continuar...")

def cargar_datos_json():
    """Pide al usuario la ruta de un archivo JSON y lo carga en el DataFrame global."""
    global DF_COMPRAS
    while True:
        ruta_archivo = input("Ingrese la ruta del archivo JSON (o 's' para salir): ")
        if ruta_archivo.lower() == 's': return False
        try:
            print(f"Cargando datos desde '{ruta_archivo}'...")
            DF_COMPRAS = pd.DataFrame(cargar_json(Path(ruta_archivo)))
            print(f"¡Éxito! Se cargaron {len(DF_COMPRAS)} compras.")
            return True
        except Exception as e:
            print(f"Ocurrió un error: {e}")

def gestionar_scraping():
    """Gestiona la ejecución del scraper."""
    limpiar_pantalla()
    print("--- Módulo de Scraping ---")
    try:
        limite_str = input("Límite de páginas a scrapear (Enter para sin límite): ")
        limite_paginas = int(limite_str) if limite_str else None
        
        compras, archivo = ScraperListado(max_paginas=limite_paginas).ejecutar(guardar=True)
        
        if compras:
            print(f"\nScraping completado: {len(compras)} compras encontradas.")
            print(f"Resultados guardados en: {archivo}")
            if input("¿Cargar estos datos para filtrar? (s/n): ").lower() == 's':
                global DF_COMPRAS
                DF_COMPRAS = pd.DataFrame(compras)
    except Exception as e:
        print(f"\nOcurrió un error durante el scraping: {e}")

def gestionar_filtrado_avanzado():
    """Gestiona la interfaz para el filtrado avanzado."""
    global DF_COMPRAS
    limpiar_pantalla()
    print("--- Módulo de Filtrado Avanzado y Puntuación ---")

    if DF_COMPRAS.empty and not cargar_datos_json():
        return
    
    print("\nDefina los criterios de filtrado (Enter para omitir).")
    
    codigo = input("Buscar por código exacto (anula otros filtros): ")
    if codigo:
        keywords_str = input("Keywords separadas por coma (ej: ferretería,riego): ")
        min_monto, max_monto, fecha_inicio, fecha_fin = None, None, None, None
    else:
        min_monto_str = input("Monto MÍNIMO en CLP: ")
        min_monto = float(min_monto_str) if min_monto_str else None
        max_monto_str = input("Monto MÁXIMO en CLP: ")
        max_monto = float(max_monto_str) if max_monto_str else None
        fecha_inicio = input("Fecha de inicio (YYYY-MM-DD): ") or None
        fecha_fin = input("Fecha de fin (YYYY-MM-DD): ") or None
        keywords_str = input("Keywords separadas por coma (ej: ferretería,riego): ")
    
    keywords = [k.strip() for k in keywords_str.split(',') if k.strip()]
    
    df_resultado = FiltradorAvanzado(DF_COMPRAS).ejecutar_filtrado(
        keywords=keywords, min_monto=min_monto, max_monto=max_monto,
        fecha_inicio=fecha_inicio, fecha_fin=fecha_fin, codigo_exacto=codigo
    )

    if df_resultado.empty:
        print("No se encontraron compras relevantes que cumplan los criterios.")
    else:
        print(f"Se encontraron {len(df_resultado)} compras relevantes:")
        cols = ['codigo', 'nombre', 'organismo', 'monto_disponible_CLP', 'puntuacion_relevancia', 'motivos_puntuacion']
        print(df_resultado[[c for c in cols if c in df_resultado.columns]].to_string())

        if input("\n¿Guardar resultados en JSON? (s/n): ").lower() == 's':
            nombre_archivo = input("Nombre del archivo (ej: resultados.json): ")
            df_resultado.to_json(nombre_archivo, orient='records', indent=4, force_ascii=False)
            print(f"Resultados guardados en '{Path(nombre_archivo).resolve()}'")

def gestionar_analisis():
    """Ejecuta el script de análisis de organismos."""
    limpiar_pantalla()
    print("--- Módulo de Análisis de Organismos ---")
    print("Iniciando análisis (requiere scraping completo)...")
    try:
        analizar_organismos_main()
    except Exception as e:
        print(f"Ocurrió un error durante el análisis: {e}")

def gestionar_tests():
    """Muestra un menú para ejecutar los scripts de prueba."""
    limpiar_pantalla()
    while True:
        print("--- Módulo de Pruebas ---")
        print("1. Test Interactivo de Filtros")
        print("2. Test Rápido de Scraper (1 pág)")
        print("3. Test de Flujo Completo (3 págs)")
        print("0. Volver al menú principal")
        opcion = input("Seleccione una prueba: ")
        
        script_map = {
            '1': "scripts/test_filtros_interactivo.py",
            '2': "scripts/test_scraper_mini.py",
            '3': "scripts/test_flujo_completo.py"
        }
        if opcion == '0': break
        if script_path := script_map.get(opcion):
            os.system(f"{sys.executable} {script_path}")
            esperar_enter()
            limpiar_pantalla()
        else:
            print("Opción no válida.")

def main():
    """Bucle principal de la aplicación."""
    while True:
        limpiar_pantalla()
        print("="*45)
        print("== Asistente de Scraping y Análisis M-CAv1 ==")
        print("="*45)
        print(f"Datos en memoria: {len(DF_COMPRAS)} compras")
        print("-"*45)
        print("\nMenú Principal:")
        print("1. Cargar Datos desde Archivo JSON")
        print("2. Ejecutar Scraping (Obtener datos nuevos)")
        print("3. Filtrado Avanzado y Puntuación")
        print("4. Ejecutar Análisis de Organismos")
        print("5. Ejecutar Pruebas del Sistema")
        print("0. Salir")
        
        opcion = input("\nSeleccione una opción: ")

        opciones = {
            '1': (cargar_datos_json, True), '2': (gestionar_scraping, True),
            '3': (gestionar_filtrado_avanzado, True), '4': (gestionar_analisis, True),
            '5': (gestionar_tests, False)
        }
        if opcion == '0':
            print("¡Hasta luego!"); break
        if accion := opciones.get(opcion):
            accion[0]()
            if accion[1]: esperar_enter()
        else:
            print("Opción no válida."); esperar_enter()

if __name__ == "__main__":
    main()