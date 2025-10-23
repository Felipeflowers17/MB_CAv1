

# ============================================
# FILTRO POR ORGANISMOS
# ============================================

# Lista de organismos prioritarios (coincidencia exacta)
ORGANISMOS_PRIORITARIOS = [
    # Por ejemplo, Municipalidad de Santiago, Hospital de Curicó, etc.
]

CATEGORIAS_ORGANISMOS = {
    # 1. MUNICIPALIDADES Y ASOCIACIONES (Alto Volumen)
    'municipal': [
        'Municipalidad',
        'Municipio',
        'Comuna',
        'Asociación de Municipalidades',
        'Corp. Municipal',
    ],
    
    # 2. SALUD (Alto Gasto Específico)
    'salud': [
        'Hospital',
        'Consultorio',
        'CESFAM',
        'Servicio de Salud',
        'Central de Abastecimiento', # CENABAST
        'Salud',
    ],
    
    # 3. GOBIERNO CENTRAL Y AGENCIAS (Decisores Clave)
    'gobierno_central': [
        'Ministerio',
        'Subsecretaría',
        'Agencia',
        'Comisión',
        'Instituto',
        'Delegación Presidencial',
    ],
    
    # 4. EDUCACIÓN SUPERIOR / CFT (Sector Académico)
    'educacion_superior': [
        'Universidad',
        'Centro de Formación Técnica',
        'CFT',
    ],
    
    # 5. OBRAS PÚBLICAS Y VIVIENDA (Infraestructura / Proyectos grandes)
    'obras_publicas_serviu': [
        'MOP',
        'SERVIU',
        'Dirección de Obras',
        'Vivienda y Urbanización',
    ],
    
    # 6. FUERZAS ARMADAS / SEGURIDAD (Defensa y Orden)
    'fuerzas_armadas': [
        'Ejército', 
        'Armada', 
        'Fuerza Aérea', 
        'Carabineros',
        'Policia de Investigaciones', # PDI
        'GENDARMERIA',
        'Defensa Nacional',
    ],

    # 7. PODER JUDICIAL Y LEGISLATIVO (Legal y Control)
    'judicial_legislativo': [
        'Tribunal',
        'Judicial',
        'Contraloría',
        'Ministerio Público',
        'Cámara de Diputados',
        'Senado',
    ],
    
    # 8. CORPORACIONES Y FUNDACIONES (Otros fines)
    'corporaciones_varias': [
        'Corporación Cultural',
        'Corporación de Deportes',
        'Fundación',
    ],
}

# ============================================
# DETECCIÓN DE SEGUNDO LLAMADO
# ============================================




# ============================================
# SISTEMA DE PUNTUACIÓN DE RELEVANCIA
# ============================================

# Puntos por cada criterio cumplido
PUNTOS_ORGANISMO_PRIORITARIO = 5
PUNTOS_CATEGORIA_ORGANISMO = 2
PUNTOS_SEGUNDO_LLAMADO = 5 

# Umbral mínimo para considerar CA como relevante
UMBRAL_RELEVANCIA = 7