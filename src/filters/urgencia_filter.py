import pandas as pd
from datetime import datetime, timedelta

def aplicar_criterio_urgencia(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aplica el criterio de urgencia para identificar oportunidades.

    Crea una nueva columna 'alerta_oportunidad' (booleana) que es True si:
    - cantidad_provedores_cotizando es 0.
    - La fecha_cierre es dentro de las próximas 12 horas.

    Args:
        df: DataFrame de pandas con los datos de las compras.

    Returns:
        El DataFrame original con la nueva columna 'alerta_oportunidad'.
    """
    df_resultado = df.copy()
    
    # Columnas requeridas para el filtro
    columnas_requeridas = ['cantidad_provedores_cotizando', 'fecha_cierre']
    if not all(col in df_resultado.columns for col in columnas_requeridas):
        # Si faltan columnas, simplemente añade la columna de alerta en False y retorna
        df_resultado['alerta_oportunidad'] = False
        return df_resultado

    # --- Procesamiento de datos ---
    # Convertir 'cantidad_provedores_cotizando' a numérico, errores a NaN y luego rellenar con 0
    df_resultado['cantidad_provedores_cotizando'] = pd.to_numeric(
        df_resultado['cantidad_provedores_cotizando'], errors='coerce'
    ).fillna(0).astype(int)

    # Convertir 'fecha_cierre' a datetime, errores resultarán en NaT
    df_resultado['fecha_cierre'] = pd.to_datetime(df_resultado['fecha_cierre'], errors='coerce')

    # --- Lógica de la alerta ---
    ahora = datetime.now()
    limite_12_horas = ahora + timedelta(hours=12)

    # Condición 1: Cero proveedores
    condicion_proveedores = df_resultado['cantidad_provedores_cotizando'] == 0
    
    # Condición 2: Fecha de cierre es válida (no NaT), es futura y es antes del límite de 12 horas
    condicion_fecha = (df_resultado['fecha_cierre'].notna()) & \
                      (df_resultado['fecha_cierre'] > ahora) & \
                      (df_resultado['fecha_cierre'] <= limite_12_horas)

    # Aplicar ambas condiciones
    df_resultado['alerta_oportunidad'] = condicion_proveedores & condicion_fecha
    
    return df_resultado