import pandas as pd
import sys
from pathlib import Path
from datetime import datetime, timedelta

# --- Configuración para importar los módulos de filtros ---
# Esto permite que el script encuentre los archivos en la carpeta 'src'
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

# --- Importar todas las funciones de los filtros ---
from src.filters.Segundo_llamado import filtrar_por_estado_convocatoria
from src.filters.monto import filtrar_por_monto
from src.filters.fecha import filtrar_por_fecha
from src.filters.ID import filtrar_por_codigo
from src.filters.urgencia_filter import aplicar_criterio_urgencia
from src.filters.keywords_filters import contar_keywords
from src.filters.organismo_filters import categorizar_organismos

# --- Importar configuración de organismos y keywords ---
# (Asegúrate de que este archivo tenga la configuración que necesitas para las pruebas)
from config.filters_config import ORGANISMOS_PRIORITARIOS, CATEGORIAS_ORGANISMOS

# --- Datos de Prueba ---
# Un pequeño set de datos que cubre varios casos de uso para probar los filtros.
DATOS_DE_PRUEBA = [
    {"id": 101, "codigo": "111-1-COT21", "nombre": "Compra de Herramientas de Ferretería", "monto_disponible_CLP": 50000, "fecha_publicacion": "2023-10-01 10:00:00", "estado_convocatoria": 2, "cantidad_provedores_cotizando": 0, "fecha_cierre": (datetime.now() + timedelta(hours=5)).strftime('%Y-%m-%d %H:%M:%S'), "organismo": "Hospital de Curicó"},
    {"id": 102, "codigo": "222-2-COT22", "nombre": "Servicio de Riego y Jardinería", "monto_disponible_CLP": 150000, "fecha_publicacion": "2023-10-15 12:30:00", "estado_convocatoria": 1, "cantidad_provedores_cotizando": 3, "fecha_cierre": (datetime.now() + timedelta(days=3)).strftime('%Y-%m-%d %H:%M:%S'), "organismo": "Municipalidad de Santiago"},
    {"id": 103, "codigo": "333-3-COT23", "nombre": "Adquisición de Semillas Orgánicas", "monto_disponible_CLP": 75000, "fecha_publicacion": "2023-11-05 08:00:00", "estado_convocatoria": 2, "cantidad_provedores_cotizando": 1, "fecha_cierre": (datetime.now() + timedelta(days=10)).strftime('%Y-%m-%d %H:%M:%S'), "organismo": "Ministerio de Agricultura"},
    {"id": 104, "codigo": "444-4-COT24", "nombre": "Maquinaria Agrícola Pesada", "monto_disponible_CLP": 1200000, "fecha_publicacion": "2023-11-20 15:00:00", "estado_convocatoria": 1, "cantidad_provedores_cotizando": 0, "fecha_cierre": (datetime.now() + timedelta(hours=20)).strftime('%Y-%m-%d %H:%M:%S'), "organismo": "Universidad de Chile"},
    {"id": 105, "codigo": "555-5-COT25", "nombre": "Material de Oficina y Limpieza", "monto_disponible_CLP": 30000, "fecha_publicacion": "2023-12-01 09:00:00", "estado_convocatoria": 2, "cantidad_provedores_cotizando": 5, "fecha_cierre": (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S'), "organismo": "Servicio de Salud Metropolitano"},
]

# Keywords para la prueba de filtro de palabras clave
KEYWORDS_EMPRESA = ["herramientas", "riego", "semillas", "ferretería"]


def mostrar_df(df, titulo="DataFrame"):
    """Función auxiliar para imprimir el DataFrame de forma legible."""
    print(f"\n--- {titulo} ---")
    if df.empty:
        print("El DataFrame está vacío.")
    else:
        print(df.to_string())
    print("-" * (len(titulo) + 8))

# --- Funciones de prueba para cada filtro ---

def probar_filtro_estado(df):
    print("\n** Probando Filtro: Estado Convocatoria (solo 'Segundo llamado') **")
    mostrar_df(df[['id', 'estado_convocatoria']], "Datos Originales")
    df_filtrado = filtrar_por_estado_convocatoria(df)
    mostrar_df(df_filtrado[['id', 'estado_convocatoria']], "Datos Filtrados (estado_convocatoria == 2)")

def probar_filtro_monto(df):
    print("\n** Probando Filtro: Monto **")
    try:
        min_monto_str = input("Ingrese el monto mínimo (o presione Enter para omitir): ")
        min_monto = float(min_monto_str) if min_monto_str else None
        
        max_monto_str = input("Ingrese el monto máximo (o presione Enter para omitir): ")
        max_monto = float(max_monto_str) if max_monto_str else None

        mostrar_df(df[['id', 'monto_disponible_CLP']], "Datos Originales")
        df_filtrado = filtrar_por_monto(df, min_monto, max_monto)
        mostrar_df(df_filtrado[['id', 'monto_disponible_CLP']], "Datos Filtrados")

    except ValueError:
        print("Error: Ingrese un número válido para los montos.")

def probar_filtro_fecha(df):
    print("\n** Probando Filtro: Fecha **")
    fecha_inicio = input("Ingrese la fecha de inicio (YYYY-MM-DD, o Enter para omitir): ")
    fecha_fin = input("Ingrese la fecha de fin (YYYY-MM-DD, o Enter para omitir): ")

    mostrar_df(df[['id', 'fecha_publicacion']], "Datos Originales")
    df_filtrado = filtrar_por_fecha(df, fecha_inicio if fecha_inicio else None, fecha_fin if fecha_fin else None)
    mostrar_df(df_filtrado[['id', 'fecha_publicacion']], "Datos Filtrados")

def probar_filtro_codigo(df):
    print("\n** Probando Filtro: Código **")
    codigo = input("Ingrese el código o ID exacto a buscar: ")
    
    mostrar_df(df[['id', 'codigo']], "Datos Originales")
    df_filtrado = filtrar_por_codigo(df, codigo)
    mostrar_df(df_filtrado, f"Resultado de la búsqueda para '{codigo}'")

def probar_criterio_urgencia(df):
    print("\n** Probando Criterio: Urgencia **")
    mostrar_df(df[['id', 'cantidad_provedores_cotizando', 'fecha_cierre']], "Datos Originales")
    df_resultado = aplicar_criterio_urgencia(df)
    mostrar_df(df_resultado[['id', 'cantidad_provedores_cotizando', 'fecha_cierre', 'alerta_oportunidad']], "Resultado con 'alerta_oportunidad'")

def probar_filtro_keywords(df):
    print(f"\n** Probando Filtro: Keywords (usando: {KEYWORDS_EMPRESA}) **")
    mostrar_df(df[['id', 'nombre']], "Datos Originales")
    df_resultado = contar_keywords(df, KEYWORDS_EMPRESA)
    mostrar_df(df_resultado[['id', 'nombre', 'keywords_encontradas_conteo', 'keywords_encontradas_lista']], "Resultado con conteo de keywords")

def probar_filtro_organismo(df):
    print("\n** Probando Filtro: Organismo **")
    mostrar_df(df[['id', 'organismo']], "Datos Originales")
    df_resultado = categorizar_organismos(df, ORGANISMOS_PRIORITARIOS, CATEGORIAS_ORGANISMOS)
    mostrar_df(df_resultado[['id', 'organismo', 'es_organismo_prioritario', 'categoria_organismo']], "Resultado con categorización de organismo")

def main():
    """Función principal que ejecuta el menú interactivo."""
    df_prueba = pd.DataFrame(DATOS_DE_PRUEBA)

    while True:
        print("\n" + "="*50)
        print("Menú de Prueba para Filtros Individuales")
        print("="*50)
        print("1. Probar Filtro de Estado (Segundo Llamado)")
        print("2. Probar Filtro de Monto")
        print("3. Probar Filtro de Fecha")
        print("4. Probar Filtro de Código")
        print("5. Probar Criterio de Urgencia")
        print("6. Probar Filtro de Keywords")
        print("7. Probar Filtro de Organismo")
        print("0. Salir")
        print("="*50)
        
        opcion = input("Seleccione una opción: ")

        if opcion == '1':
            probar_filtro_estado(df_prueba.copy())
        elif opcion == '2':
            probar_filtro_monto(df_prueba.copy())
        elif opcion == '3':
            probar_filtro_fecha(df_prueba.copy())
        elif opcion == '4':
            probar_filtro_codigo(df_prueba.copy())
        elif opcion == '5':
            probar_criterio_urgencia(df_prueba.copy())
        elif opcion == '6':
            probar_filtro_keywords(df_prueba.copy())
        elif opcion == '7':
            probar_filtro_organismo(df_prueba.copy())
        elif opcion == '0':
            print("Saliendo del programa de pruebas.")
            break
        else:
            print("Opción no válida. Por favor, intente de nuevo.")

if __name__ == "__main__":
    main()