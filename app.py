import streamlit as st
import os
import time
import logging
import json
from datetime import datetime
import chromadb
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.llms import Ollama
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import ConversationalRetrievalChain

# Función para guardar interacciones
def save_interaction(question, answer, is_helpful):
    """Guarda la interacción en un archivo JSON"""
    interaction = {
        'fecha': datetime.now().isoformat(),
        'pregunta': question,
        'respuesta': answer,
        'util': is_helpful
    }
    
    try:
        # Asegurarse de que el directorio existe
        os.makedirs('logs', exist_ok=True)
        file_path = os.path.join('logs', 'interacciones.json')
        
        # Cargar o crear el archivo de interacciones
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                try:
                    interactions = json.load(f)
                except json.JSONDecodeError:
                    interactions = []
        else:
            interactions = []
        
        # Agregar nueva interacción
        interactions.append(interaction)
        
        # Guardar todas las interacciones
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(interactions, f, ensure_ascii=False, indent=2)
            
        st.sidebar.info(f"Interacción guardada en: {file_path}")
            
    except Exception as e:
        st.error(f"Error guardando la interacción: {str(e)}")

# Configuración de estilos Davivienda
st.markdown("""
    <style>
        /* Colores Davivienda */
        :root {
            --davivienda-red: #FF0000;
            --davivienda-dark-red: #CC0000;
            --davivienda-white: #FFFFFF;
        }
        
        /* Título principal */
        .main-title {
            color: var(--davivienda-red);
            font-size: 2.5rem;
            font-weight: bold;
            padding: 1rem 0;
            text-align: center;
            background-color: var(--davivienda-white);
            border-radius: 10px;
            margin-bottom: 2rem;
        }
        
        /* Botones */
        .stButton > button {
            background-color: var(--davivienda-red) !important;
            color: white !important;
            border: none !important;
            border-radius: 5px !important;
            padding: 0.5rem 2rem !important;
        }
        
        /* Sidebar */
        .css-1d391kg {
            background-color: var(--davivienda-dark-red);
        }
        
        /* Métricas */
        .stMetric {
            background-color: var(--davivienda-white);
            padding: 1rem;
            border-radius: 5px;
            border: 2px solid var(--davivienda-red);
        }
        
        /* Cajas de texto */
        .stTextInput > div > div > input {
            border: 2px solid var(--davivienda-red) !important;
            border-radius: 5px;
        }
        
        /* Selectbox */
        .stSelectbox > div > div {
            border: 2px solid var(--davivienda-red) !important;
        }
    </style>
    """, unsafe_allow_html=True)

# Configurar logging
logging.basicConfig(
    filename='performance_logs.txt',
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)

def log_performance(operation, time_taken):
    logging.info(f"{operation}: {time_taken:.2f} segundos")
    
def measure_time(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        time_taken = end_time - start_time
        log_performance(func.__name__, time_taken)
        return result, time_taken
    return wrapper

def calculate_confidence_score(response, question, source_docs):
    """Calcula un puntaje de confianza más completo"""
    # Puntuación por longitud (30% del score)
    length_score = min(len(response.split()) / 100, 1.0) * 0.3
    
    # Puntuación por relevancia con la pregunta (40% del score)
    keywords = set(question.lower().split())
    response_words = set(response.lower().split())
    relevance_score = len(keywords.intersection(response_words)) / len(keywords) * 0.4
    
    # Puntuación por fuentes citadas (30% del score)
    source_score = min(len(source_docs) / 3, 1.0) * 0.3
    
    # Score final (0-100)
    total_score = (length_score + relevance_score + source_score) * 100
    
    return total_score

@st.cache_resource
def initialize_chroma():
    client = chromadb.PersistentClient(path="./chroma_db")
    return client

@st.cache_resource
def initialize_llm():
    return Ollama(
        model="mistral",
        system="Eres un asistente experto que siempre responde en español. Tus respuestas deben ser claras, profesionales y basadas en el documento proporcionado. Proporciona respuestas detalladas y bien estructuradas."
    )

@st.cache_resource
def initialize_embeddings():
    return OllamaEmbeddings(model="mistral")

@measure_time
def process_scientific_document(file_path):
    loader = PyPDFLoader(file_path)
    documents = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100
    )
    return text_splitter.split_documents(documents)

@measure_time
def get_response(query, vectorstore):
    llm = initialize_llm()
    chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(search_kwargs={'k': 3}),
        return_source_documents=True
    )
    return chain({"question": query, "chat_history": []})

def main():
    # Header con logo
    st.markdown("""
        <div style='text-align: center; padding: 1rem;'>
            <h1 class='main-title'>📄 Sistema de Análisis de Documentos</h1>
        </div>
    """, unsafe_allow_html=True)
    
    # Sidebar con estilo personalizado
    st.sidebar.markdown("""
        <div style='background-color: #CC0000; padding: 1rem; border-radius: 5px; color: white;'>
            <h2>Métricas de Rendimiento</h2>
        </div>
    """, unsafe_allow_html=True)
    
    if st.sidebar.checkbox("Mostrar tiempos de respuesta"):
        try:
            with open('performance_logs.txt', 'r') as f:
                logs = f.readlines()[-5:]
                for log in logs:
                    st.sidebar.text(log.strip())
        except FileNotFoundError:
            st.sidebar.write("No hay logs disponibles aún")
    
    # Preguntas sugeridas
    suggested_questions = [
        "¿Cuál es la idea principal del artículo?",
        "¿Por qué es importante este tema?",
        "¿Cuáles son los puntos clave o argumentos principales?",
        "¿Qué evidencias o ejemplos presenta el artículo?",
        "¿Cuáles son las implicaciones o consecuencias de lo que se plantea?",
        "¿Qué preguntas o dudas quedan abiertas después de leerlo?"
    ]
    
    try:
        initialize_chroma()
    except Exception as e:
        st.error(f"Error inicializando ChromaDB: {str(e)}")
        return
    
    if 'vectorstore' not in st.session_state:
        st.session_state.vectorstore = None
    
    # Contenedor principal con estilo
    st.markdown("""
        <div style='background-color: white; padding: 2rem; border-radius: 10px; box-shadow: 0 2px 6px rgba(0,0,0,0.1);'>
            <h3 style='color: #FF0000;'>Sistema de Análisis Inteligente</h3>
        </div>
    """, unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader("Sube tu artículo (PDF)", type=['pdf'])
    
    if uploaded_file:
        os.makedirs('docs', exist_ok=True)
        file_path = os.path.join('docs', uploaded_file.name)
        with open(file_path, 'wb') as f:
            f.write(uploaded_file.getbuffer())
        
        if st.session_state.vectorstore is None:
            with st.spinner('Analizando el artículo...'):
                splits, process_time = process_scientific_document(file_path)
                embeddings = initialize_embeddings()
                st.session_state.vectorstore = Chroma.from_documents(
                    splits, 
                    embeddings,
                    persist_directory="./chroma_db"
                )
            st.success(f'¡Artículo analizado correctamente en {process_time:.2f} segundos!')
        
        # Selector de preguntas con nuevo diseño
        st.write("### Preguntas de Análisis")
        st.write("Selecciona una pregunta o escribe la tuya:")
        
        col1, col2 = st.columns([2,3])
        with col1:
            selected_question = st.selectbox(
                "Preguntas sugeridas:",
                ["Selecciona una pregunta..."] + suggested_questions
            )
        
        with col2:
            question = st.text_input(
                "Tu pregunta sobre el artículo:",
                value=selected_question if selected_question != "Selecciona una pregunta..." else ""
            )
        
        if st.button("Analizar", key="analyze_btn"):
            if question and question != "Selecciona una pregunta...":
                with st.spinner('Analizando...'):
                    try:
                        start_time = time.time()
                        result, response_time = get_response(question, st.session_state.vectorstore)
                        
                        # Calcular métricas
                        confidence_score = calculate_confidence_score(
                            result["answer"], 
                            question, 
                            result.get("source_documents", [])
                        )
                        
                        # Contenedor de respuesta estilizado
                        st.markdown("""
                            <div style='background-color: white; padding: 2rem; border-radius: 10px; border: 2px solid #FF0000; margin: 1rem 0;'>
                                <h3 style='color: #FF0000;'>Respuesta:</h3>
                                <p style='font-size: 1.1rem;'>{}</p>
                            </div>
                        """.format(result["answer"]), unsafe_allow_html=True)
                        
                        # Métricas en columnas estilizadas
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown(f"""
                                <div style='background-color: white; padding: 1rem; border-radius: 5px; border: 2px solid #FF0000; text-align: center;'>
                                    <h4 style='color: #FF0000;'>Confianza</h4>
                                    <p style='font-size: 1.5rem;'>{confidence_score:.1f}%</p>
                                </div>
                            """, unsafe_allow_html=True)
                        with col2:
                            st.markdown(f"""
                                <div style='background-color: white; padding: 1rem; border-radius: 5px; border: 2px solid #FF0000; text-align: center;'>
                                    <h4 style='color: #FF0000;'>Tiempo de Respuesta</h4>
                                    <p style='font-size: 1.5rem;'>{response_time:.2f}s</p>
                                </div>
                            """, unsafe_allow_html=True)
                        
                        # Feedback del usuario estilizado
                        st.markdown("""
                            <div style='background-color: white; padding: 1rem; border-radius: 5px; border: 2px solid #FF0000; margin-top: 1rem;'>
                                <h4 style='color: #FF0000;'>¿Fue útil esta respuesta?</h4>
                            </div>
                        """, unsafe_allow_html=True)
                        
                        col1, col2, col3 = st.columns([1,1,4])
                        with col1:
                            if st.button("👍 Sí"):
                                save_interaction(question, result["answer"], True)
                                st.success("¡Gracias por tu feedback!")
                        with col2:
                            if st.button("👎 No"):
                                save_interaction(question, result["answer"], False)
                                st.error("Gracias, trabajaremos en mejorar.")
                        
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
            else:
                st.warning("Por favor, selecciona o escribe una pregunta.")

if __name__ == "__main__":
    main()