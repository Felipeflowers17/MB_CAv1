import pandas as pd
from typing import Optional

def filtrar_por_fecha(df: pd.DataFrame, fecha_inicio: Optional[str] = None, fecha_fin: Optional[str] = None) -> pd.DataFrame:
    """
    Filtra el DataFrame por un rango de fechas de publicación.

    Args:
        df: DataFrame de pandas con los datos de las compras.
        fecha_inicio: Fecha de inicio del rango (formato 'YYYY-MM-DD').
        fecha_fin: Fecha de fin del rango (formato 'YYYY-MM-DD').

    Returns:
        DataFrame de pandas con las compras filtradas por fecha.
    """
    if 'fecha_publicacion' not in df.columns:
        return pd.DataFrame()

    # Convertir la columna de fecha a formato datetime, los errores se convertirán en NaT (Not a Time)
    df_filtrado = df.copy()
    df_filtrado['fecha_publicacion'] = pd.to_datetime(df_filtrado['fecha_publicacion'], errors='coerce')

    # Eliminar filas con fechas inválidas
    df_filtrado.dropna(subset=['fecha_publicacion'], inplace=True)

    # Convertir las fechas de entrada a datetime si se proporcionan
    if fecha_inicio:
        start_date = pd.to_datetime(fecha_inicio)
        df_filtrado = df_filtrado[df_filtrado['fecha_publicacion'].dt.date >= start_date.date()]
    
    if fecha_fin:
        end_date = pd.to_datetime(fecha_fin)
        df_filtrado = df_filtrado[df_filtrado['fecha_publicacion'].dt.date <= end_date.date()]
        
    return df_filtrado