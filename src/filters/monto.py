import pandas as pd
from typing import Optional

def filtrar_por_monto(df: pd.DataFrame, min_monto: Optional[float] = None, max_monto: Optional[float] = None) -> pd.DataFrame:
    """
    Filtra el DataFrame por un rango de montos en CLP.

    Args:
        df: DataFrame de pandas con los datos de las compras.
        min_monto: Monto mínimo a incluir. Si es None, no hay límite inferior.
        max_monto: Monto máximo a incluir. Si es None, no hay límite superior.

    Returns:
        DataFrame de pandas con las compras filtradas por monto.
    """
    if 'monto_disponible_CLP' not in df.columns:
        return pd.DataFrame()

    # Asegurarse de que la columna es numérica, convirtiendo errores a NaN
    df['monto_disponible_CLP'] = pd.to_numeric(df['monto_disponible_CLP'], errors='coerce')
    
    # Eliminar filas donde el monto es NaN (inválido)
    df_filtrado = df.dropna(subset=['monto_disponible_CLP']).copy()

    if min_monto is not None:
        df_filtrado = df_filtrado[df_filtrado['monto_disponible_CLP'] >= min_monto]
    
    if max_monto is not None:
        df_filtrado = df_filtrado[df_filtrado['monto_disponible_CLP'] <= max_monto]
        
    return df_filtrado