import pandas as pd
from typing import Optional

def filtrar_por_codigo(df: pd.DataFrame, codigo: str) -> Optional[pd.DataFrame]:
    """
    Busca una compra específica por su 'codigo' o 'id'.

    Args:
        df: DataFrame de pandas con los datos de las compras.
        codigo: El código o id exacto a buscar.

    Returns:
        Un DataFrame con la fila única que coincide, o un DataFrame vacío si no se encuentra.
    """
    if not codigo:
        return pd.DataFrame()

    # Buscar primero en la columna 'codigo' si existe
    if 'codigo' in df.columns:
        resultado = df[df['codigo'] == codigo]
        if not resultado.empty:
            return resultado.copy()
    
    # Si no se encontró en 'codigo' o la columna no existe, buscar en 'id'
    # El campo id es numérico en el JSON de ejemplo, por lo que intentamos convertir el código a número.
    if 'id' in df.columns:
        try:
            # Intentar convertir el código a int para la comparación
            codigo_numerico = int(codigo)
            resultado = df[df['id'] == codigo_numerico]
            if not resultado.empty:
                return resultado.copy()
        except (ValueError, TypeError):
            # Si el código no es numérico, o hay un error, no se puede comparar con 'id'
            pass

    return pd.DataFrame() # Retornar DataFrame vacío si no se encuentra en ninguna columna