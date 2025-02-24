import streamlit as st
import pandas as pd
from datetime import datetime
import json

def load_performance_logs():
    """Carga y procesa los logs de rendimiento"""
    try:
        with open('performance_logs.txt', 'r') as f:
            logs = f.readlines()
        
        # Procesar cada línea del log
        data = []
        for log in logs:
            try:
                # Separar fecha y métrica
                date_str, metric = log.split(' - ')
                date = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S,%f')
                
                # Extraer operación y tiempo
                operation = metric.split(':')[0]
                time = float(metric.split(':')[1].replace('segundos', '').strip())
                
                data.append({
                    'fecha': date,
                    'operacion': operation,
                    'tiempo': time
                })
            except Exception as e:
                continue
                
        return pd.DataFrame(data)
    except FileNotFoundError:
        st.error("No se encontró el archivo performance_logs.txt")
        return pd.DataFrame()

def main():
    st.title("📊 Métricas de Rendimiento RAG")
    
    # Cargar datos de rendimiento
    df_performance = load_performance_logs()
    
    if not df_performance.empty:
        # Calcular promedios por operación
        process_time = df_performance[df_performance['operacion'] == 'process_scientific_document']['tiempo'].mean()
        response_time = df_performance[df_performance['operacion'] == 'get_response']['tiempo'].mean()
        
        # Mostrar métricas
        st.header("Tiempos Promedio")
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric(
                "Carga de Archivo",
                f"{process_time:.2f}s" if not pd.isna(process_time) else "N/A"
            )
        
        with col2:
            st.metric(
                "Respuestas",
                f"{response_time:.2f}s" if not pd.isna(response_time) else "N/A"
            )
        
        # Mostrar datos en tabla
        st.header("Detalle de Operaciones")
        st.dataframe(
            df_performance.groupby('operacion')['tiempo'].agg(['mean', 'count']).round(2).rename(
                columns={'mean': 'Tiempo Promedio (s)', 'count': 'Número de Operaciones'}
            )
        )

if __name__ == "__main__":
    main()