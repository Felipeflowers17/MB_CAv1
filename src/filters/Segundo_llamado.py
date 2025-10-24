import pandas as pd

def filtrar_por_estado_convocatoria(df: pd.DataFrame) -> pd.DataFrame:
    
    if 'estado_convocatoria' not in df.columns:
        return pd.DataFrame()  # Devuelve un DataFrame vacío si la columna no existe

    # Asegurarse de que la columna es de tipo numérico, convirtiendo errores a NaN y luego a 0
    df['estado_convocatoria'] = pd.to_numeric(df['estado_convocatoria'], errors='coerce').fillna(0).astype(int)
    
    return df[df['estado_convocatoria'] == 2].copy()