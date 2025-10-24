import pandas as pd
from .keywords_filters import normalizar_texto # Reutilizamos la función para normalizar texto

def categorizar_organismos(df: pd.DataFrame, organismos_prioritarios: list, categorias_organismos: dict) -> pd.DataFrame:
    """
    Categoriza las compras según el organismo y si este es prioritario.

    Añade tres nuevas columnas:
    - 'es_organismo_prioritario': True si el organismo está en la lista de prioritarios.
    - 'categoria_organismo': El nombre de la categoría a la que pertenece (e.g., 'salud').
    - 'subcategoria_organismo': La palabra clave específica que coincidió (e.g., 'Hospital').

    Args:
        df: DataFrame de pandas con los datos de las compras.
        organismos_prioritarios: Lista de nombres exactos de organismos prioritarios.
        categorias_organismos: Diccionario con categorías y sus palabras clave.

    Returns:
        El DataFrame original con las nuevas columnas de categorización.
    """
    df_resultado = df.copy()

    if 'organismo' not in df_resultado.columns:
        df_resultado['es_organismo_prioritario'] = False
        df_resultado['categoria_organismo'] = None
        df_resultado['subcategoria_organismo'] = None
        return df_resultado

    # --- 1. Verificar Organismos Prioritarios (coincidencia exacta) ---
    organismos_prioritarios_lower = [org.lower() for org in organismos_prioritarios]
    df_resultado['es_organismo_prioritario'] = df_resultado['organismo'].str.lower().isin(organismos_prioritarios_lower)

    # --- 2. Mapear Categorías ---
    def encontrar_categoria(organismo_str):
        if not isinstance(organismo_str, str):
            return None, None
        
        organismo_normalizado = normalizar_texto(organismo_str)
        
        for categoria, keywords in categorias_organismos.items():
            for keyword in keywords:
                # Buscamos la keyword normalizada dentro del nombre del organismo normalizado
                if normalizar_texto(keyword) in organismo_normalizado:
                    return categoria, keyword # Retornamos la categoría y la keyword que coincidió
        return None, None

    # Aplicar la función y dividir los resultados en dos nuevas columnas
    resultados = df_resultado['organismo'].apply(encontrar_categoria)
    df_resultado['categoria_organismo'] = [res[0] for res in resultados]
    df_resultado['subcategoria_organismo'] = [res[1] for res in resultados]
    
    return df_resultado