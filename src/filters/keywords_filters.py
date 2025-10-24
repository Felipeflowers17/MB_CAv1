import pandas as pd
import re
import unicodedata

def normalizar_texto(texto: str) -> str:
    """
    Convierte un texto a minúsculas y elimina tildes/acentos.

    Args:
        texto: El string a normalizar.

    Returns:
        El string normalizado.
    """
    if not isinstance(texto, str):
        return ""
    # NFD: Normalization Form Decomposed, para separar letras de tildes
    # .encode('ascii', 'ignore'): Elimina los caracteres no-ASCII (las tildes)
    # .decode('utf-8'): Vuelve a convertir el stream de bytes a un string
    s = ''.join(c for c in unicodedata.normalize('NFD', texto.lower()) if unicodedata.category(c) != 'Mn')
    return s

def contar_keywords(df: pd.DataFrame, keywords: list) -> pd.DataFrame:
    """
    Cuenta cuántas keywords se encuentran en el campo 'nombre' de cada compra.

    Añade dos columnas:
    - 'keywords_encontradas_conteo': Número de keywords encontradas.
    - 'keywords_encontradas_lista': Una lista con las keywords que coincidieron.

    Args:
        df: DataFrame de pandas con los datos de las compras.
        keywords: Lista de palabras clave a buscar.

    Returns:
        El DataFrame original con las dos nuevas columnas.
    """
    df_resultado = df.copy()

    if 'nombre' not in df_resultado.columns or not keywords:
        df_resultado['keywords_encontradas_conteo'] = 0
        df_resultado['keywords_encontradas_lista'] = [[] for _ in range(len(df_resultado))]
        return df_resultado

    # Normalizar la lista de keywords una sola vez
    keywords_normalizadas = [normalizar_texto(k) for k in keywords]

    def encontrar_keywords(nombre):
        if pd.isna(nombre):
            return 0, []
        
        nombre_normalizado = normalizar_texto(nombre)
        encontradas = []
        
        for keyword in keywords_normalizadas:
            # Usar word boundaries (\b) para buscar palabras completas y evitar sub-matches
            # ej: buscar 'herramienta' y no coincidir con 'herramientas' si no se desea.
            # Si se desea coincidencia parcial, se puede quitar \b
            if re.search(r'\b' + re.escape(keyword) + r'\b', nombre_normalizado):
                encontradas.append(keyword)
        
        return len(encontradas), encontradas

    # Aplicar la función a la columna 'nombre'
    resultados = df_resultado['nombre'].apply(encontrar_keywords)
    
    df_resultado['keywords_encontradas_conteo'] = [res[0] for res in resultados]
    df_resultado['keywords_encontradas_lista'] = [res[1] for res in resultados]

    return df_resultado