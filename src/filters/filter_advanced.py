import pandas as pd
from typing import Optional, List

# Importar todas las funciones de los filtros individuales
from .Segundo_llamado import filtrar_por_estado_convocatoria
from .monto import filtrar_por_monto
from .fecha import filtrar_por_fecha
from .ID import filtrar_por_codigo
from .urgencia_filter import aplicar_criterio_urgencia
from .keywords_filters import contar_keywords
from .organismo_filters import categorizar_organismos

# Importar la configuración de puntuación
from config.filters_config import (
    ORGANISMOS_PRIORITARIOS,
    CATEGORIAS_ORGANISMOS,
    PUNTOS_ORGANISMO_PRIORITARIO,
    PUNTOS_CATEGORIA_ORGANISMO,
    PUNTOS_SEGUNDO_LLAMADO,
    UMBRAL_RELEVANCIA
)

# Definimos aquí los puntos que faltaban en el archivo de configuración
PUNTOS_OPORTUNIDAD = 3 # Bonus por alerta de urgencia
PUNTOS_KEYWORD = 1     # Puntos por cada keyword encontrada

class FiltradorAvanzado:
    """
    Clase que orquesta el proceso completo de filtrado y puntuación de compras.
    """
    def __init__(self, df_compras: pd.DataFrame):
        if not isinstance(df_compras, pd.DataFrame):
            raise TypeError("Se esperaba un DataFrame de pandas.")
        self.df_original = df_compras.copy()
        self.df_procesado = df_compras.copy()

    def _aplicar_filtros_duros(self, min_monto: Optional[float], max_monto: Optional[float], fecha_inicio: Optional[str], fecha_fin: Optional[str]):
        """Aplica los filtros que descartan compras."""
        print("-> Aplicando filtros duros...")
        self.df_procesado = filtrar_por_estado_convocatoria(self.df_procesado)
        print(f"   {len(self.df_procesado)} compras restantes tras filtro de estado.")
        self.df_procesado = filtrar_por_monto(self.df_procesado, min_monto, max_monto)
        print(f"   {len(self.df_procesado)} compras restantes tras filtro de monto.")
        self.df_procesado = filtrar_por_fecha(self.df_procesado, fecha_inicio, fecha_fin)
        print(f"   {len(self.df_procesado)} compras restantes tras filtro de fecha.")

    def _enriquecer_datos(self, keywords: List[str]):
        """Aplica los filtros que añaden columnas para el scoring."""
        print("-> Enriqueciendo datos para puntuación...")
        if self.df_procesado.empty:
            return
        self.df_procesado = aplicar_criterio_urgencia(self.df_procesado)
        self.df_procesado = contar_keywords(self.df_procesado, keywords)
        self.df_procesado = categorizar_organismos(self.df_procesado, ORGANISMOS_PRIORITARIOS, CATEGORIAS_ORGANISMOS)
        print("   Datos enriquecidos con información de urgencia, keywords y organismos.")

    def _calcular_puntuacion(self):
        """Calcula el puntaje de relevancia para cada compra."""
        print("-> Calculando puntuación de relevancia...")
        if self.df_procesado.empty:
            self.df_procesado['puntuacion_relevancia'] = 0
            self.df_procesado['motivos_puntuacion'] = [[] for _ in range(len(self.df_procesado))]
            return

        motivos_series = [[] for _ in range(len(self.df_procesado))]
        # Inicializamos la columna de puntuación
        self.df_procesado['puntuacion_relevancia'] = 0

        for index, row in self.df_procesado.iterrows():
            score = 0
            motivos = []
            
            score += PUNTOS_SEGUNDO_LLAMADO
            motivos.append(f"Segundo Llamado (+{PUNTOS_SEGUNDO_LLAMADO})")

            if row.get('es_organismo_prioritario', False):
                score += PUNTOS_ORGANISMO_PRIORITARIO
                motivos.append(f"Organismo Prioritario (+{PUNTOS_ORGANISMO_PRIORITARIO})")
            elif pd.notna(row.get('categoria_organismo')):
                score += PUNTOS_CATEGORIA_ORGANISMO
                motivos.append(f"Categoría Organismo (+{PUNTOS_CATEGORIA_ORGANISMO})")
            
            if row.get('alerta_oportunidad', False):
                score += PUNTOS_OPORTUNIDAD
                motivos.append(f"Alerta Oportunidad (+{PUNTOS_OPORTUNIDAD})")

            keyword_count = row.get('keywords_encontradas_conteo', 0)
            if keyword_count > 0:
                puntos_kw = keyword_count * PUNTOS_KEYWORD
                score += puntos_kw
                motivos.append(f"{keyword_count} Keyword(s) (+{puntos_kw})")
            
            self.df_procesado.at[index, 'puntuacion_relevancia'] = score
            motivos_series[self.df_procesado.index.get_loc(index)] = motivos

        self.df_procesado['motivos_puntuacion'] = motivos_series
        print("   Puntuación calculada.")

    def ejecutar_filtrado(self, keywords: List[str], min_monto: Optional[float] = None, max_monto: Optional[float] = None, fecha_inicio: Optional[str] = None, fecha_fin: Optional[str] = None, codigo_exacto: Optional[str] = None) -> pd.DataFrame:
        print("\n===== INICIANDO FILTRADO AVANZADO =====")
        if codigo_exacto:
            print(f"-> Búsqueda directa por código: {codigo_exacto}")
            self.df_procesado = filtrar_por_codigo(self.df_original, codigo_exacto)
        else:
            self._aplicar_filtros_duros(min_monto, max_monto, fecha_inicio, fecha_fin)

        self._enriquecer_datos(keywords)
        self._calcular_puntuacion()

        print(f"-> Filtrando por umbral de relevancia (puntuación >= {UMBRAL_RELEVANCIA})")
        df_final = self.df_procesado[self.df_procesado['puntuacion_relevancia'] >= UMBRAL_RELEVANCIA]
        print(f"Resultado: {len(df_final)} compras consideradas relevantes.")
        print("===== FILTRADO AVANZADO COMPLETADO =====\n")
        
        return df_final.sort_values(by='puntuacion_relevancia', ascending=False)