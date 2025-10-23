"""
Test de manejador de API
Valida: interceptación, parseo, extracción de datos
"""
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from src.scraper.api_handler import ManejadorAPI
from src.scraper.utilidades.logger import configurar_logger


class MockResponse:
    """Mock de respuesta de Playwright para testing"""
    
    def __init__(self, url, json_data=None):
        self.url = url
        self._json_data = json_data
    
    def json(self):
        if self._json_data is None:
            raise Exception("No JSON data")
        return self._json_data


def test_inicializacion():
    """Prueba inicialización del manejador"""
    print("TEST: Inicialización")
    print("-" * 50)
    
    logger = configurar_logger('test_api_handler')
    manejador = ManejadorAPI(logger)
    
    assert manejador.logger is not None
    assert manejador.datos_respuesta_actual is None
    print(f"✓ Manejador inicializado correctamente")


def test_interceptacion_valida():
    """Prueba interceptación de respuesta válida"""
    print("\nTEST: Interceptación válida")
    print("-" * 50)
    
    logger = configurar_logger('test_api_handler')
    manejador = ManejadorAPI(logger)
    
    # Crear respuesta mock válida
    datos_mock = {
        "success": "OK",
        "payload": {
            "resultados": [
                {"id": "1234-567-COT89", "nombre": "Test"},
                {"id": "1234-567-COT90", "nombre": "Test 2"}
            ],
            "resultCount": 2,
            "pageCount": 1,
            "page": 1,
            "pageSize": 15
        }
    }
    
    url_api = "https://api.buscador.mercadopublico.cl/compra-agil?page=1"
    response_mock = MockResponse(url_api, datos_mock)
    
    # Interceptar
    manejador.interceptar_respuesta(response_mock)
    
    assert manejador.hay_respuesta_disponible() == True
    assert manejador.datos_respuesta_actual is not None
    print(f"✓ Respuesta interceptada y guardada")


def test_extraccion_resultados():
    """Prueba extracción de resultados"""
    print("\nTEST: Extracción de resultados")
    print("-" * 50)
    
    logger = configurar_logger('test_api_handler')
    manejador = ManejadorAPI(logger)
    
    # Simular respuesta
    datos_mock = {
        "success": "OK",
        "payload": {
            "resultados": [
                {"id": "1234-567-COT89", "nombre": "Test 1"},
                {"id": "1234-567-COT90", "nombre": "Test 2"},
                {"id": "1234-567-COT91", "nombre": "Test 3"}
            ]
        }
    }
    
    url_api = "https://api.buscador.mercadopublico.cl/compra-agil"
    response_mock = MockResponse(url_api, datos_mock)
    manejador.interceptar_respuesta(response_mock)
    
    # Extraer resultados
    resultados = manejador.extraer_resultados()
    
    assert isinstance(resultados, list)
    assert len(resultados) == 3
    assert resultados[0]['id'] == "1234-567-COT89"
    
    print(f"✓ Resultados extraídos: {len(resultados)} items")


def test_extraccion_metadata():
    """Prueba extracción de metadata de paginación"""
    print("\nTEST: Extracción de metadata")
    print("-" * 50)
    
    logger = configurar_logger('test_api_handler')
    manejador = ManejadorAPI(logger)
    
    # Simular respuesta con metadata
    datos_mock = {
        "success": "OK",
        "payload": {
            "resultados": [],
            "resultCount": 450,
            "pageCount": 30,
            "page": 5,
            "pageSize": 15
        }
    }
    
    url_api = "https://api.buscador.mercadopublico.cl/compra-agil"
    response_mock = MockResponse(url_api, datos_mock)
    manejador.interceptar_respuesta(response_mock)
    
    # Extraer metadata
    metadata = manejador.extraer_metadata_paginacion()
    
    assert metadata['resultCount'] == 450
    assert metadata['pageCount'] == 30
    assert metadata['page'] == 5
    assert metadata['pageSize'] == 15
    
    print(f"✓ Metadata extraída correctamente")
    print(f"  Total resultados: {metadata['resultCount']}")
    print(f"  Total páginas: {metadata['pageCount']}")
    print(f"  Página actual: {metadata['page']}")
    print(f"  Tamaño página: {metadata['pageSize']}")


def test_verificacion_exito():
    """Prueba verificación de respuesta exitosa"""
    print("\nTEST: Verificación de éxito")
    print("-" * 50)
    
    logger = configurar_logger('test_api_handler')
    manejador = ManejadorAPI(logger)
    
    # Respuesta exitosa
    datos_exitosa = {
        "success": "OK",
        "payload": {"resultados": []}
    }
    
    url_api = "https://api.buscador.mercadopublico.cl/compra-agil"
    response_mock = MockResponse(url_api, datos_exitosa)
    manejador.interceptar_respuesta(response_mock)
    
    assert manejador.verificar_respuesta_exitosa() == True
    print(f"✓ Respuesta exitosa verificada")
    
    # Respuesta fallida
    datos_fallida = {
        "success": "ERROR",
        "payload": {}
    }
    
    response_mock_2 = MockResponse(url_api, datos_fallida)
    manejador.interceptar_respuesta(response_mock_2)
    
    assert manejador.verificar_respuesta_exitosa() == False
    print(f"✓ Respuesta fallida detectada")


def test_limpieza():
    """Prueba limpieza de respuesta"""
    print("\nTEST: Limpieza de datos")
    print("-" * 50)
    
    logger = configurar_logger('test_api_handler')
    manejador = ManejadorAPI(logger)
    
    # Agregar datos
    datos_mock = {
        "success": "OK",
        "payload": {"resultados": [{"test": "data"}]}
    }
    
    url_api = "https://api.buscador.mercadopublico.cl/compra-agil"
    response_mock = MockResponse(url_api, datos_mock)
    manejador.interceptar_respuesta(response_mock)
    
    assert manejador.hay_respuesta_disponible() == True
    
    # Limpiar
    manejador.limpiar_respuesta_actual()
    
    assert manejador.hay_respuesta_disponible() == False
    assert manejador.datos_respuesta_actual is None
    print(f"✓ Respuesta limpiada correctamente")


def main():
    """Ejecuta todos los tests"""
    print("=" * 50)
    print("TESTING: Manejador de API")
    print("=" * 50)
    
    try:
        test_inicializacion()
        test_interceptacion_valida()
        test_extraccion_resultados()
        test_extraccion_metadata()
        test_verificacion_exito()
        test_limpieza()
        
        print("\n" + "=" * 50)
        print("RESULTADO: Manejador de API válido")
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