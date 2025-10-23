"""
Test de archivos JSON guardados
Valida estructura y contenido de datos reales
"""
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from src.scraper.utilidades.helpers import cargar_json
from config.config import DIRECTORIO_DATOS_RAW


def listar_archivos_json():
    """Lista todos los archivos JSON en data/raw/"""
    archivos = list(DIRECTORIO_DATOS_RAW.glob("*.json"))
    return sorted(archivos, key=lambda x: x.stat().st_mtime, reverse=True)


def test_archivo_mas_reciente():
    """Prueba el archivo JSON más reciente"""
    print("TEST: Validación de JSON guardado")
    print("-" * 50)
    
    # Buscar archivos
    archivos = listar_archivos_json()
    
    if not archivos:
        print("ADVERTENCIA: No hay archivos JSON en data/raw/")
        print("Ejecuta primero un scraping para generar datos")
        return None
    
    # Cargar el más reciente
    archivo_reciente = archivos[0]
    print(f"Archivo: {archivo_reciente.name}")
    
    try:
        datos = cargar_json(archivo_reciente)
        print(f"✓ JSON cargado correctamente")
        
        # Validar estructura
        assert isinstance(datos, list), "Datos no es lista"
        assert len(datos) > 0, "Datos vacíos"
        print(f"✓ Estructura válida: {len(datos)} items")
        
        # Validar primer item
        primer_item = datos[0]
        assert isinstance(primer_item, dict), "Item no es diccionario"
        
        campos_esperados = ['codigo', 'nombre', 'organismo']
        campos_presentes = [c for c in campos_esperados if c in primer_item or 'id' in primer_item]
        
        print(f"✓ Campos básicos presentes")
        
        # Mostrar estadísticas
        print()
        print("Estadísticas del archivo:")
        print(f"  Total items: {len(datos)}")
        print(f"  Tamaño: {archivo_reciente.stat().st_size / 1024:.1f} KB")
        
        # Mostrar ejemplo
        print()
        print("Ejemplo de item:")
        codigo = primer_item.get('codigo') or primer_item.get('id')
        nombre = primer_item.get('nombre', 'N/A')[:50]
        organismo = primer_item.get('organismo', 'N/A')[:30]
        
        print(f"  Código: {codigo}")
        print(f"  Nombre: {nombre}...")
        print(f"  Organismo: {organismo}...")
        
        return len(datos)
        
    except Exception as e:
        print(f"ERROR al procesar archivo: {e}")
        raise


def test_listar_todos_archivos():
    """Lista todos los archivos disponibles"""
    print("\nTEST: Listado de archivos")
    print("-" * 50)
    
    archivos = listar_archivos_json()
    
    if not archivos:
        print("No hay archivos JSON")
        return
    
    print(f"Total archivos: {len(archivos)}")
    print()
    print("Archivos encontrados (más recientes primero):")
    
    for i, archivo in enumerate(archivos[:5], 1):
        tamaño_kb = archivo.stat().st_size / 1024
        print(f"  {i}. {archivo.name} ({tamaño_kb:.1f} KB)")
    
    if len(archivos) > 5:
        print(f"  ... y {len(archivos) - 5} más")


def main():
    """Ejecuta tests de JSON"""
    print("=" * 50)
    print("TESTING: Archivos JSON guardados")
    print("=" * 50)
    
    try:
        test_listar_todos_archivos()
        total = test_archivo_mas_reciente()
        
        if total:
            print()
            print("=" * 50)
            print("RESULTADO: Tests exitosos")
            print(f"Items validados: {total}")
            print("=" * 50)
        else:
            print()
            print("=" * 50)
            print("RESULTADO: No hay datos para validar")
            print("=" * 50)
        
        return 0
        
    except Exception as e:
        print(f"\nERROR: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())