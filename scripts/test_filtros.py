"""
Test de sistema de filtrado
Valida: detección por campo estado_convocatoria
"""
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from src.scraper.filters import FiltradorCompras


def test_deteccion_por_estado():
    """Prueba detección de segundo llamado por estado_convocatoria"""
    print("TEST: Detección por estado_convocatoria")
    print("-" * 50)
    
    filtrador = FiltradorCompras()
    
    # Compra con segundo llamado (estado_convocatoria = 2)
    compra_segundo = {
        "codigo": "1234-567-COT89",
        "nombre": "ADQUISICIÓN DE HERRAMIENTAS",
        "organismo": "Municipalidad Test",
        "estado_convocatoria": 2
    }
    es_segundo = filtrador.es_segundo_llamado(compra_segundo)
    assert es_segundo == True
    print(f"✓ Detectado segundo llamado (estado_convocatoria = 2)")
    
    # Compra primer llamado (estado_convocatoria = 1)
    compra_primero = {
        "codigo": "1234-567-COT90",
        "nombre": "ADQUISICIÓN DE MATERIALES",
        "organismo": "Municipalidad Test",
        "estado_convocatoria": 1
    }
    es_segundo = filtrador.es_segundo_llamado(compra_primero)
    assert es_segundo == False
    print(f"✓ No detectado en primer llamado (estado_convocatoria = 1)")
    
    # Compra sin campo estado_convocatoria
    compra_sin_campo = {
        "codigo": "1234-567-COT91",
        "nombre": "COMPRA TEST",
        "organismo": "Test"
    }
    es_segundo = filtrador.es_segundo_llamado(compra_sin_campo)
    assert es_segundo == False
    print(f"✓ Sin campo estado_convocatoria procesado correctamente")


def test_filtrado_completo():
    """Prueba filtrado completo de lista de compras"""
    print("\nTEST: Filtrado completo")
    print("-" * 50)
    
    filtrador = FiltradorCompras()
    
    # Crear compras de prueba
    compras = [
        {
            "codigo": "1234-567-COT89",
            "nombre": "COMPRA 1",
            "organismo": "Test",
            "estado_convocatoria": 2
        },
        {
            "codigo": "1234-567-COT90",
            "nombre": "COMPRA 2",
            "organismo": "Test",
            "estado_convocatoria": 1
        },
        {
            "codigo": "1234-567-COT91",
            "nombre": "COMPRA 3",
            "organismo": "Test",
            "estado_convocatoria": 2
        },
        {
            "codigo": "1234-567-COT92",
            "nombre": "COMPRA 4",
            "organismo": "Test",
            "estado_convocatoria": 1
        }
    ]
    
    # Filtrar
    compras_filtradas = filtrador.filtrar_segundo_llamado(compras)
    
    assert len(compras_filtradas) == 2
    assert all(c['estado_convocatoria'] == 2 for c in compras_filtradas)
    
    print(f"✓ Total compras: {len(compras)}")
    print(f"✓ Segundo llamado: {len(compras_filtradas)}")
    print(f"✓ Primer llamado: {len(compras) - len(compras_filtradas)}")


def test_metadata():
    """Prueba agregado de metadata"""
    print("\nTEST: Metadata de filtrado")
    print("-" * 50)
    
    filtrador = FiltradorCompras()
    
    compras = [
        {
            "codigo": "1234-567-COT89",
            "nombre": "COMPRA SEGUNDO LLAMADO",
            "organismo": "Test",
            "estado_convocatoria": 2
        }
    ]
    
    compras_filtradas = filtrador.filtrar_segundo_llamado(compras)
    
    assert len(compras_filtradas) == 1
    assert 'metadata_filtrado' in compras_filtradas[0]
    assert compras_filtradas[0]['metadata_filtrado']['es_segundo_llamado'] == True
    assert compras_filtradas[0]['metadata_filtrado']['estado_convocatoria'] == 2
    assert 'fecha_filtrado' in compras_filtradas[0]['metadata_filtrado']
    
    print(f"✓ Metadata agregada correctamente")


def test_estadisticas():
    """Prueba generación de estadísticas"""
    print("\nTEST: Estadísticas")
    print("-" * 50)
    
    filtrador = FiltradorCompras()
    
    compras = [
        {"codigo": f"COT{i}", "estado_convocatoria": 2 if i % 3 == 0 else 1}
        for i in range(10)
    ]
    
    compras_filtradas = filtrador.filtrar_segundo_llamado(compras)
    estadisticas = filtrador.generar_estadisticas(compras, compras_filtradas)
    
    assert 'total_compras' in estadisticas
    assert 'segundo_llamado' in estadisticas
    assert 'primer_llamado' in estadisticas
    assert 'porcentaje_segundo_llamado' in estadisticas
    
    print(f"✓ Estadísticas generadas")
    print(f"  Total: {estadisticas['total_compras']}")
    print(f"  Segundo llamado: {estadisticas['segundo_llamado']}")
    print(f"  Porcentaje: {estadisticas['porcentaje_segundo_llamado']:.1f}%")


def main():
    """Ejecuta todos los tests"""
    print("=" * 50)
    print("TESTING: Sistema de filtrado")
    print("=" * 50)
    
    try:
        test_deteccion_por_estado()
        test_filtrado_completo()
        test_metadata()
        test_estadisticas()
        
        print("\n" + "=" * 50)
        print("RESULTADO: Todos los tests pasaron")
        print("=" * 50)
        return 0
        
    except AssertionError as e:
        print(f"\nERROR: Test falló - {e}")
        return 1
    except Exception as e:
        print(f"\nERROR: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())