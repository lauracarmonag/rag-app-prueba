import time
import concurrent.futures
import pandas as pd
import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    handlers=[
        logging.FileHandler('load_test_results.txt'),
        logging.StreamHandler(sys.stdout)
    ]
)

def test_single_query(question, iteration):
    """Simula una consulta"""
    print(f"Iteración {iteration} - Probando pregunta: {question}")
    start_time = time.time()
    time.sleep(2)  # Simulamos el tiempo de procesamiento
    time_taken = time.time() - start_time
    return time_taken

def run_load_test(num_iterations=5):
    """Ejecuta pruebas de carga múltiples veces"""
    print("\nIniciando pruebas de carga...")
    
    test_questions = [
        "¿Cuál es la idea principal del artículo?",
        "¿Por qué es importante este tema?",
        "¿Cuáles son los puntos clave?"
    ]
    
    results = []
    for i in range(num_iterations):
        print(f"\n=== Simulación #{i+1} ===")
        for question in test_questions:
            time_taken = test_single_query(question, i+1)
            results.append(time_taken)
            print(f"Tiempo de respuesta: {time_taken:.2f} segundos")
    
    return results

if __name__ == "__main__":
    print("=== INICIANDO PRUEBAS DE CARGA ===")
    
    # Ejecutar 20 iteraciones
    results = run_load_test(20)
    
    # Analizar resultados
    if results:
        print("\n=== RESULTADOS FINALES ===")
        print(f"Total de simulaciones: 5")
        print(f"Total de consultas: {len(results)}")
        print(f"Tiempo promedio: {sum(results)/len(results):.2f} segundos")
        print(f"Tiempo máximo: {max(results):.2f} segundos")
        print(f"Tiempo mínimo: {min(results):.2f} segundos")
    else:
        print("No se obtuvieron resultados")
    
    print("\n=== PRUEBAS COMPLETADAS ===")