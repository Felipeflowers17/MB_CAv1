"""
Test mínimo de scraper real
Extrae SOLO 1 página para verificar funcionamiento
"""
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from src.scraper.list_scraper import ScraperListado
from config.config import FECHA_SCRAPING


def test_scraper_una_pagina():
    """Test rápido: extrae solo 1 página"""
    print("TEST: Scraper listado (1 página)")
    print("-" * 50)
    print(f"Fecha: {FECHA_SCRAPING}")
    print()
    
    # Crear scraper limitado a 1 página
    scraper = ScraperListado(max_paginas=1)
    
    # Ejecutar sin guardar
    compras, _ = scraper.ejecutar(guardar=False)
    
    # Validaciones
    assert compras is not None, "No se obtuvieron compras"
    assert isinstance(compras, list), "Compras no es lista"
    assert len(compras) > 0, "Lista de compras vacía"
    
    print(f"✓ Compras extraídas: {len(compras)}")
    
    # Validar estructura de primera compra
    primera = compras[0]
    assert 'codigo' in primera or 'id' in primera, "Sin código"
    assert 'nombre' in primera, "Sin nombre"
    assert 'organismo' in primera, "Sin organismo"
    
    print(f"✓ Estructura válida")
    
    # Mostrar ejemplo
    codigo = primera.get('codigo') or primera.get('id')
    nombre = primera['nombre'][:50]
    organismo = primera['organismo'][:30]
    
    print()
    print("Ejemplo de compra extraída:")
    print(f"  Código: {codigo}")
    print(f"  Nombre: {nombre}...")
    print(f"  Organismo: {organismo}...")
    
    return len(compras)


def main():
    """Ejecuta test de scraper"""
    print("=" * 50)
    print("TESTING: Scraper real (modo rápido)")
    print("=" * 50)
    print()
    print("ADVERTENCIA: Este test hace request real")
    print("Presiona Ctrl+C para cancelar")
    print()
    
    try:
        total = test_scraper_una_pagina()
        
        print()
        print("=" * 50)
        print("RESULTADO: Test exitoso")
        print(f"Total compras: {total}")
        print("=" * 50)
        return 0
        
    except KeyboardInterrupt:
        print("\nTest cancelado por usuario")
        return 1
    except AssertionError as e:
        print(f"\nERROR: Test falló - {e}")
        return 1
    except Exception as e:
        print(f"\nERROR: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())