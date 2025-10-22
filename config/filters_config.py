"""
Configuración de filtros para compras ágiles
Sistema de puntuación y criterios de relevancia
"""

# ============================================
# FILTRO POR ORGANISMOS
# ============================================

# Lista de organismos prioritarios (coincidencia exacta)
# Se llenará después del análisis del primer día
ORGANISMOS_PRIORITARIOS = [
    # Ejemplos (comentados hasta tener datos reales):
    # "Municipalidad de Santiago",
    # "IV Brigada Aérea",
]

# Categorías de organismos (coincidencia parcial en nombre)
# Se busca si el nombre del organismo CONTIENE estas palabras
CATEGORIAS_ORGANISMOS = {
    'municipal': ['Municipalidad', 'Municipio', 'Comuna'],
    'fuerzas_armadas': ['Ejército', 'Armada', 'Fuerza Aérea', 'Brigada'],
    'salud': ['Hospital', 'Consultorio', 'CESFAM', 'Servicio de Salud'],
    'educacion': ['Escuela', 'Liceo', 'Colegio', 'Universidad', 'Instituto'],
    'servicios_publicos': ['Servicio Nacional', 'Ministerio', 'Subsecretaría'],
}

# ============================================
# DETECCIÓN DE SEGUNDO LLAMADO
# ============================================

# Palabras clave que indican segundo llamado en nombre/descripción
KEYWORDS_SEGUNDO_LLAMADO = [
    'segundo llamado',
    '2do llamado',
    '2° llamado',
    'segunda convocatoria',
    'nueva publicación',
    'republicación',
    'segundo proceso',
]

# ============================================
# SISTEMA DE PUNTUACIÓN DE RELEVANCIA
# ============================================

# Puntos por cada criterio cumplido
PUNTOS_ORGANISMO_PRIORITARIO = 5
PUNTOS_CATEGORIA_ORGANISMO = 2
PUNTOS_SEGUNDO_LLAMADO = 5

# Umbral mínimo para considerar CA como relevante
UMBRAL_RELEVANCIA = 7

